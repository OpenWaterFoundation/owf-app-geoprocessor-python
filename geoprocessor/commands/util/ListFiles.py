# ListFiles - command to list files in a folder or URL location
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2020 Open Water Foundation
# 
# GeoProcessor is free software:  you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     GeoProcessor is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with GeoProcessor.  If not, see <https://www.gnu.org/licenses/>.
# ________________________________________________________________NoticeEnd___

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandError import CommandError
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import logging
import os
import urllib


class ListFiles(AbstractCommand):
    """
    Lists file and/or folders from a input folder. The input folder can be a folder on a local machine or a url 
    directory.
    
    Command Parameters
    * Folder (str, optional): the path to a folder on the local machine (relative or absolute)
    * URL (str, optional): a valid URL/web address (can end in / but is not required)
    * IncludePatterns (str, optional): a comma-separated list of glob-style patterns to determine which files/folders
        to list from the input folder/url Default: * (All files/folders are listed.).
    * ExcludePatterns (str, optional): a comma-separated list of glob-style patterns to determine which files/folders
        to not list from the input folder/url Default: '' ( No files/folders are excluded from being listed).
    * ListFiles (str converted to Boolean within command): If True, files within the input folder/URL will be
        listed. If False, files within the folder/URL will not be listed. Default: True
    * ListFolders (str converted to Boolean within command): If True, folders within the input folder/URL will be
        listed. If False, folders within the input folder/URL or URL will not be listed. Default: True
    * ListProperty (str, required): The name of the GeoProcessor property to store the output list of files/folders.
    * IfPropertyExists (str, optional): This parameter determines the action that occurs if the ListProperty
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("Folder", str),
        CommandParameterMetadata("URL", str),
        CommandParameterMetadata("IncludePatterns", str),
        CommandParameterMetadata("ExcludePatterns", str),
        CommandParameterMetadata("ListFiles", bool),
        CommandParameterMetadata("ListFolders", bool),
        CommandParameterMetadata("ListCount", int),
        CommandParameterMetadata("ListProperty", str),
        CommandParameterMetadata("ListProperty1", str),
        CommandParameterMetadata("IfPropertyExists", str)]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = (
        "Lists the files and/or folders within a folder or a URL.\n"
        "This is useful for iterating over files and folders.\n"
        "The files and folders are sorted in alphabetical order using lowercase strings.")
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # Folder
    __parameter_input_metadata['Folder.Description'] = "path of the folder"
    __parameter_input_metadata['Folder.Label'] = "Folder"
    __parameter_input_metadata['Folder.Tooltip'] = "The path of the folder of interest (relative or absolute)."
    __parameter_input_metadata['Folder.Value.Default'] = \
        "Required if 'URL' parameter is not specified."
    __parameter_input_metadata['Folder.FileSelector.Title'] = "select a path to a folder"
    __parameter_input_metadata['Folder.FileSelector.Type'] = "Read"
    __parameter_input_metadata['Folder.FileSelector.SelectFolder'] = True
    # URL
    __parameter_input_metadata['URL.Description'] = "the URL of interest"
    __parameter_input_metadata['URL.Label'] = "URL"
    __parameter_input_metadata['URL.Tooltip'] = "The URL of interest."
    __parameter_input_metadata['URL.Value.Default'] = "Required if Folder parameter is not specified."
    # TODO @jurentie 01/24/2019 FileSelector?
    # ListProperty
    __parameter_input_metadata['ListProperty.Description'] = "a property name to hold the output list"
    __parameter_input_metadata['ListProperty.Label'] = "List property"
    __parameter_input_metadata['ListProperty.Required'] = False
    __parameter_input_metadata['ListProperty.Tooltip'] = "Property name to hold the output list."
    # ListProperty1
    __parameter_input_metadata['ListProperty1.Description'] = "a property name to hold the output when a single value"
    __parameter_input_metadata['ListProperty1.Label'] = "List property (1 value)"
    __parameter_input_metadata['ListProperty1.Required'] = False
    __parameter_input_metadata['ListProperty1.Tooltip'] =\
        "Property name to hold the output when a single value. Use ListCount to restrict list to 1 value."
    # ListCount
    __parameter_input_metadata['ListCount.Description'] = "count of files to output"
    __parameter_input_metadata['ListCount.Label'] = "List count"
    __parameter_input_metadata['ListCount.Required'] = False
    __parameter_input_metadata['ListCount.Tooltip'] = "Indicate number of files to output, positive for start of list,"\
                                                      " negative for end of list."
    # IncludePatterns
    __parameter_input_metadata['IncludePatterns.Description'] = "a list that filters which items to include"
    __parameter_input_metadata['IncludePatterns.Label'] = "Include patterns"
    __parameter_input_metadata['IncludePatterns.Tooltip'] = \
        "A list of comma-separated glob-style patterns that filter which items to include in the output list."
    __parameter_input_metadata['IncludePatterns.Value.Default.Description'] = \
        "* - all files/folders are included."
    # ExcludePatterns
    __parameter_input_metadata['ExcludePatterns.Description'] = "a list that filters which items to exclude"
    __parameter_input_metadata['ExcludePatterns.Label'] = "Exclude patterns"
    __parameter_input_metadata['ExcludePatterns.Tooltip'] = \
        "A list of comma-separated glob-style patterns that filter which items to exclude in the output list."
    __parameter_input_metadata['ExcludePatterns.Value.Default.Description'] = "No files/folders are excluded."
    # ListFiles
    __parameter_input_metadata['ListFiles.Description'] = "whether to list files"
    __parameter_input_metadata['ListFiles.Label'] = "List files"
    __parameter_input_metadata['ListFiles.Tooltip'] = (
        "Boolean\n\n"
        "If True, files will be listed.\n"
        "If False, files will not be listed.")
    __parameter_input_metadata['ListFiles.Value.Default'] = "True"
    __parameter_input_metadata['ListFiles.Values'] = ["", "True", "False"]
    # ListFolders
    __parameter_input_metadata['ListFolders.Description'] = "whether to list folders"
    __parameter_input_metadata['ListFolders.Label'] = "List folders"
    __parameter_input_metadata['ListFolders.Tooltip'] = (
        "Boolean\n\n"
        "If True, folders will be listed.\n"
        "If False, folders will not be listed.")
    __parameter_input_metadata['ListFolders.Value.Default'] = "True"
    __parameter_input_metadata['ListFolders.Values'] = ["", "True", "False"]
    # IfPropertyExists
    __parameter_input_metadata['IfPropertyExists.Description'] = "action if ListProperty exists"
    __parameter_input_metadata['IfPropertyExists.Label'] = "If property exists"
    __parameter_input_metadata['IfPropertyExists.Tooltip'] = (
        "The action that occurs if 'List Property' is already an existing property.\n\n"
        "Replace: The existing property value is overwritten with the output list. No warning is logged\n"
        "ReplaceAndWarn: The existing property value is overwritten with the output list. A warning is logged.\n"
        "Warn: The existing property keeps its original value. A warning is logged.\n"
        "Fail: The existing property keeps its original value. A fail message is logged.")
    __parameter_input_metadata['IfPropertyExists.Value.Default'] = "Replace"
    __parameter_input_metadata['IfPropertyExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]

    def __init__(self) -> None:
        """
        Initialize the command
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "ListFiles"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata
        self.parameter_input_metadata = self.__parameter_input_metadata

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters: dict) -> None:
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns: None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning_message = ""

        # Check that required parameters are non-empty, non-None strings.
        required_parameters = command_util.get_required_parameter_names(self)
        for parameter in required_parameters:
            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)
            if not validator_util.validate_string(parameter_value, False, False):
                message = "Required {} parameter has no value.".format(parameter)
                recommendation = "Specify the {} parameter.".format(parameter)
                warning_message += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that either the parameter Folder or the parameter URL is a non-empty, non-None string.
        # noinspection PyPep8Naming
        pv_Folder = self.get_parameter_value(parameter_name='Folder', command_parameters=command_parameters)
        # noinspection PyPep8Naming
        pv_URL = self.get_parameter_value(parameter_name='URL', command_parameters=command_parameters)

        folder_is_string = validator_util.validate_string(pv_Folder, False, False)
        url_is_string = validator_util.validate_string(pv_URL, False, False)

        if folder_is_string and url_is_string:
            message = "The Folder parameter and the URL parameter cannot both be enabled in the same command."
            recommendation = "Specify only the Folder parameter or only the URL parameter."
            warning_message += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        if not folder_is_string and not url_is_string:
            message = "Both the Folder parameter and the URL have no value."
            recommendation = "Specify EITHER the Folder parameter OR the URL parameter."
            warning_message += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional ListFiles parameter value is a valid Boolean value or is None.
        # noinspection PyPep8Naming
        pv_ListFiles = self.get_parameter_value(parameter_name="ListFiles", command_parameters=command_parameters)

        if not validator_util.validate_bool(pv_ListFiles, none_allowed=True, empty_string_allowed=False):
            message = "ListFiles parameter value ({}) is not a recognized boolean value.".format(pv_ListFiles)
            recommendation = "Specify either 'True' or 'False for the ListFiles parameter."
            warning_message += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional ListFolders parameter value is a valid Boolean value or is None.
        # noinspection PyPep8Naming
        pv_ListFolders = self.get_parameter_value(parameter_name="ListFolders", command_parameters=command_parameters)
        if not validator_util.validate_bool(pv_ListFolders, none_allowed=True, empty_string_allowed=False):
            message = "ListFolders parameter value ({}) is not a recognized boolean value.".format(pv_ListFolders)
            recommendation = "Specify either 'True' or 'False for the ListFolders parameter."
            warning_message += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that parameter ListCount is an integer if specified
        # - allow blank and None
        # noinspection PyPep8Naming
        pv_ListCount = self.get_parameter_value(parameter_name='ListCount', command_parameters=command_parameters)

        if not validator_util.validate_int(pv_ListCount, True, True):
            message = "ListCount parameter is not an integer."
            recommendation = "Specify the ListCount as an integer."
            warning_message += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that parameter ListProperty or ListProperty1 is a non-empty, non-None string.
        # noinspection PyPep8Naming
        pv_ListProperty = self.get_parameter_value(parameter_name='ListProperty', command_parameters=command_parameters)
        # noinspection PyPep8Naming
        pv_ListProperty1 = self.get_parameter_value(parameter_name='ListProperty1',
                                                    command_parameters=command_parameters)

        validate1 = validator_util.validate_string(pv_ListProperty, False, False)
        validate2 = validator_util.validate_string(pv_ListProperty1, False, False)
        if not validate1 and not validate2:
            # Neither were specified.
            message = "ListProperty and ListProperty1 parameters have no value."
            recommendation = "Specify the ListProperty and/or ListProperty1 parameter."
            warning_message += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional parameter IfPropertyExists is either `Replace`, `ReplaceAndWarn`, `Warn`, `Fail`, None.
        # noinspection PyPep8Naming
        pv_IfPropertyExists = self.get_parameter_value(parameter_name="IfPropertyExists",
                                                       command_parameters=command_parameters)

        acceptable_values = ["Replace", "ReplaceAndWarn", "Warn", "Fail"]

        if not validator_util.validate_string_in_list(pv_IfPropertyExists, acceptable_values, none_allowed=True,
                                                      empty_string_allowed=True, ignore_case=True):
            message = "IfPropertyExists parameter value ({}) is not recognized.".format(pv_IfPropertyExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfPropertyExists parameter.".format(
                acceptable_values)
            warning_message += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            self.logger.warning(warning_message)
            raise CommandParameterError(warning_message)

        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, folder_abs: str, url_abs: str, list_files_bool: bool, list_dirs_bool: bool,
                           list_property: str, list_property1: str, if_property_exists: bool) -> bool:
        """
        Checks the following:
        * the URL/Folder is valid.
        * either the ListFiles or ListFolders (or both) are set to TRUE. Raise a WARNING, does not cause a FAILURE.
        * the list property is unique.

        Args:
            folder_abs (str or None): the full path to the input Folder
            url_abs (str of None): the full path to the input URL
            list_files_bool (Boolean): set to True if the files within the folder/url are to be listed.
            list_dirs_bool (Boolean): set to True if the folders within the folder/url are to be listed.
            list_property (str): the name of the property to hold the output list of strings
            list_property1 (str): the name of the property for one value
            if_property_exists (bool): indicate how to handle if requested property exists

        Returns:
            Boolean. If TRUE, the GeoLayer should be clipped. If FALSE, at least one check failed and the GeoLayer
            should not be clipped.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        if folder_abs:
            # If the Folder is not a valid folder, raise a FAILURE.
            should_run_command.append(validator_util.run_check(self, "IsFolderPathValid", "Folder", folder_abs, "FAIL"))

        if url_abs:
            # If the URL is not a valid url, raise a FAILURE.
            should_run_command.append(validator_util.run_check(self, "IsUrlValid", "URL", url_abs, "FAIL"))

        if not list_files_bool and not list_dirs_bool:
            # If both the ListFiles and the ListFolders are set to FALSE, raise a WARNING.
            message = "Both ListFiles and ListFolders are set to FALSE. There will be no output."
            recommendation = "Set at lease one of the parameters to TRUE."
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.WARNING,
                                                                                  message, recommendation))
            should_run_command.append(True)

        # If the ListProperty or ListProperty1 is the same as an already-existing Property,
        # raise a WARNING or FAILURE (depends on the value of the IfPropertyExists parameter.)
        if if_property_exists is not None and if_property_exists:
            should_run_command.append(validator_util.run_check(self, "IsPropertyUnique", "ListProperty", list_property,
                                                               None))
            should_run_command.append(validator_util.run_check(self, "IsPropertyUnique", "ListProperty1",
                                                               list_property1, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    @staticmethod
    def scrape_html(url: str, read_files: bool, read_dirs: bool,
                    include_list: [str] = None, exclude_list: [str] = None, include_count: int = None) -> [str]:
        """
        Reads a URL and outputs a list of links within the URL's source. The list of links can be filtered be the
        following options:
            * include file links, directory/folder links or both types of links
            * include/exclude links with names match a/multiple glob-style pattern(s)

        Args:
            url (str): a web address (URL) to scrape. Can, but is not required to, include an ending forward slash.
            read_files (bool): If True, the links associated with FILES will be included in the returned list. If False,
                the links associated with FILES will not be included in the returned list.
            read_dirs (bool): If True, the links associated with DIRECTORIES will be included in the returned list. If
                False, the links associated with DIRECTORIES will not be included in the returned list.
            include_list (list of str): A list of glob-style patterns. Links with names that match any of the glob-style
                patterns listed in this list will be included in the returned list. Default: None (All links are
                included.) The include_list is assigned ['*'] inside of the string_util.filter_list_of_strings function
                if set to None.
            exclude_list (list of str): A list of glob-style patterns. Links with names that match any of the glob-style
                patterns listed in this list will be excluded in the returned list. Default: None (No links excluded.)
                The exclude_list is assigned [''] inside of the string_util.filter_list_of_strings function if set to
                None.
            include_count (int): Maximum number of list values to return.  If positive, the number is for the start
                of the list.  If negative, the number is for the end of the list.

        Return:
            A list of links within the URL source page that match the configured settings.
        """

        # If the URL does not end in a forward slash, add an ending forward slash.
        if not url.endswith('/'):
            url += '/'

        # Read the source content of the URL.
        urlpath = urllib.urlopen(url)
        string = urlpath.read().decode('utf-8')

        # Get the URL of the parent directory.
        parent_dir_url = url.rsplit('/', 2)[0]

        # in_link determines if a URL character in within an HTML link. Set to FALSE until proven TRUE (when a link is
        # found within the source content of the URL).
        in_link = False

        # A list to hold the URL's source links that are directories/folders.
        dir_list = []

        # A list to hold the URL's source links that are files.
        file_list = []

        # Iterate through each character of the URL's source content.
        for i in range(len(string)):

            # If the string contains <A HREF= and the program is not currently reading a source content link, continue.
            if (string[i:i + 8]).upper() == "<A HREF=" and not in_link:
                # Set the in_link Boolean variable to True. Marks the start of reading a source link.
                in_link = True

                # Get the index of the character that starts the link's name.
                link_start_char_index = i + 9

            # If the string contains "> and the program is currently reading a source content link, continue.
            if (string[i:i + 2]).upper() == '">' and in_link:

                # Set the in_link Boolean variable to False. Marks the end of reading a source link.
                in_link = False

                # Get the index of the character that ends the link's name.
                link_end_char_index = i

                # Get the link's name.
                link_name = string[link_start_char_index: link_end_char_index]

                # If the link name ends in a forward slash, the link is a folder/directory. Add the link name (without
                # the leading path or the ending forward slash) to the dir_list.
                if link_name.endswith('/'):
                    dir_list.append(link_name.split('/')[-2])

                # If the link name does not end in a forward slash, the link is a file. Add the link name (without
                # the leading path) to the file_list.
                else:
                    file_list.append(link_name.split('/')[-1])

        # If the files and directories are of interest, create a list with both the files and the directories.
        link_list = None
        if read_files and read_dirs:
            link_list = dir_list + file_list

        # If the files are of interest, create a list with just the files.
        elif read_files:
            link_list = file_list

        # If the directories/folders are of interest, create a list with just the directories/folders.
        elif read_dirs:
            link_list = dir_list

        # Iterate over the each link name.
        for link in link_list:

            # Remove the link if it corresponds to a parent directory.
            if link in parent_dir_url:
                link_list.remove(link)

        # Filter the list of links with regards to the include_list and exclude_list parameters.
        link_list_filtered = string_util.filter_list_of_strings(link_list, include_list, exclude_list,
                                                                include_count=include_count)

        # Return the list of filtered and available links within the input URL.
        return [url + link_name for link_name in link_list_filtered]

    def run_command(self) -> None:

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_Folder = self.get_parameter_value("Folder")
        # noinspection PyPep8Naming
        pv_URL = self.get_parameter_value("URL")
        # noinspection PyPep8Naming
        pv_ListFiles = self.get_parameter_value("ListFiles", default_value="True")
        # noinspection PyPep8Naming
        pv_ListFolders = self.get_parameter_value("ListFolders", default_value="True")
        # noinspection PyPep8Naming
        pv_ListCount = self.get_parameter_value("ListCount")
        # noinspection PyPep8Naming
        pv_ListProperty = self.get_parameter_value("ListProperty")
        # noinspection PyPep8Naming
        pv_ListProperty1 = self.get_parameter_value("ListProperty1")
        # noinspection PyPep8Naming
        pv_IncludePatterns = self.get_parameter_value("IncludePatterns", default_value="*")
        # noinspection PyPep8Naming
        pv_ExcludePatterns = self.get_parameter_value("ExcludePatterns", default_value="''")
        # noinspection PyPep8Naming
        pv_IfPropertyExists = self.get_parameter_value("IfPropertyExists", default_value="Replace")
        if_property_exists_upper = 'REPLACE'  # Default.
        if pv_IfPropertyExists is not None and (len(pv_IfPropertyExists) > 0):
            if_property_exists_upper = pv_IfPropertyExists.upper()

        # Convert the IncludeAttributes and ExcludeAttributes to lists.
        to_include = string_util.delimited_string_to_list(pv_IncludePatterns)
        to_exclude = string_util.delimited_string_to_list(pv_ExcludePatterns)

        # Convert the pv_ListFiles and pv_ListFolders to Boolean values.
        list_files_bool = string_util.str_to_bool(pv_ListFiles)
        list_dirs_bool = string_util.str_to_bool(pv_ListFolders)

        # Convert pv_ListCount to an int
        list_count = None
        if pv_ListCount is not None and (len(pv_ListCount) > 0):
            list_count = int(pv_ListCount)

        # Set the absolute paths for the Folder and the URL to None until proven to exist within the command process.
        folder_abs = None
        url_abs = None

        # If the input is a local folder.
        if pv_Folder:

            # Convert the Folder parameter value relative path to an absolute path and expand for ${Property} syntax.
            folder_abs = io_util.verify_path_for_os(io_util.to_absolute_path(
                self.command_processor.get_property('WorkingDir'),
                self.command_processor.expand_parameter_value(pv_Folder, self)))

        # If the input is a url.
        if pv_URL:

            # Convert the URL parameter to expand for ${Property} syntax.
            url_abs = self.command_processor.expand_parameter_value(pv_URL, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(folder_abs, url_abs, list_files_bool, list_dirs_bool, pv_ListProperty,
                                   pv_ListProperty1, pv_IfPropertyExists):

            # noinspection PyBroadException
            try:
                # If the input is a local folder.
                if pv_Folder:

                    # Get a list of the files in the folder.
                    files = [f for f in os.listdir(folder_abs) if os.path.isfile(os.path.join(folder_abs, f))]

                    # Get a list of directories in the folder.
                    dirs = [d for d in os.listdir(folder_abs) if os.path.isdir(os.path.join(folder_abs, d))]

                    # If configured to list files and folders, continue.
                    if list_files_bool and list_dirs_bool:

                        # Filter the list of files and folders with regards to the IncludePatterns and ExcludePatterns.
                        output_filtered = string_util.filter_list_of_strings(files + dirs, to_include, to_exclude,
                                                                             include_count=list_count)

                    # If configured to list files, continue.
                    elif list_files_bool:

                        # Filter the list of files with regards to the IIncludePatterns and ExcludePatterns.
                        output_filtered = string_util.filter_list_of_strings(files, to_include, to_exclude,
                                                                             include_count=list_count)

                    # If configured to list folders, continue.
                    elif list_dirs_bool:

                        # Filter the list of folders with regards to the IIncludePatterns and ExcludePatterns.
                        output_filtered = string_util.filter_list_of_strings(dirs, to_include, to_exclude,
                                                                             include_count=list_count)

                    else:
                        output_filtered = []

                # If the input is a url.
                elif pv_URL:

                    # If configured to list files and folders, continue.
                    if list_files_bool and list_dirs_bool:
                        output_filtered = self.scrape_html(url_abs, True, True, to_include, to_exclude,
                                                           include_count=list_count)

                    # If configured to list files, continue.
                    elif list_files_bool:
                        output_filtered = self.scrape_html(url_abs, True, False, to_include, to_exclude,
                                                           include_count=list_count)

                    # If configured to list folders, continue.
                    elif list_dirs_bool:
                        output_filtered = self.scrape_html(url_abs, False, True, to_include, to_exclude,
                                                           include_count=list_count)

                    else:
                        output_filtered = None

                # Add the filtered list to the desired ListProperty.
                if pv_ListProperty is not None and (len(pv_ListProperty) > 0):
                    existing_property = self.command_processor.get_property(pv_ListProperty)
                    if (if_property_exists_upper == 'REPLACE') or (if_property_exists_upper == 'REPLACEANDWARN'):
                        # Set the property value.
                        # self.logger.info("Setting property {} to {}".format,pv_ListProperty, output_filtered)
                        self.command_processor.set_property(pv_ListProperty, sorted(output_filtered, key=str.lower))
                        if existing_property is not None and (if_property_exists_upper == 'REPLACEANDWARN'):
                            self.warning_count += 1
                            message = "Set property '{}' and warning.".format(pv_ListProperty)
                            recommendation = "Confirm that property should be set."
                            self.logger.warning(message)
                            self.command_status.add_to_log(CommandPhaseType.RUN,
                                                           CommandLogRecord(CommandStatusType.WARN, message,
                                                                            recommendation))
                    elif (if_property_exists_upper == 'WARN') or (if_property_exists_upper == 'FAIL'):
                        self.warning_count += 1
                        message = "Not resetting existing property '{}'.".format(pv_ListProperty)
                        recommendation = "Confirm that property should be set."
                        self.logger.warning(message)
                        if if_property_exists_upper == 'WARN':
                            self.command_status.add_to_log(CommandPhaseType.RUN,
                                                           CommandLogRecord(CommandStatusType.WARNING, message,
                                                                            recommendation))
                        elif if_property_exists_upper == 'FAIL':
                            self.command_status.add_to_log(CommandPhaseType.RUN,
                                                           CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                            recommendation))

                if pv_ListProperty1 is not None and (len(pv_ListProperty1) > 0):
                    existing_property = self.command_processor.get_property(pv_ListProperty1)
                    if (if_property_exists_upper == 'REPLACE') or (if_property_exists_upper == 'REPLACEANDWARN'):
                        # Set the property value.
                        # self.logger.info("Setting property {} to {}".format,pv_ListProperty, output_filtered[0])
                        self.command_processor.set_property(pv_ListProperty1, output_filtered[0])
                        if existing_property is not None and (if_property_exists_upper == 'REPLACEANDWARN'):
                            self.warning_count += 1
                            message = "Set property '{}' and warning.".format(pv_ListProperty1)
                            recommendation = "Confirm that property should be set."
                            self.logger.warning(message)
                            self.command_status.add_to_log(CommandPhaseType.RUN,
                                                           CommandLogRecord(CommandStatusType.WARN, message,
                                                                            recommendation))
                    elif (if_property_exists_upper == 'WARN') or (if_property_exists_upper == 'FAIL'):
                        self.warning_count += 1
                        message = "Not resetting existing property '{}'.".format(pv_ListProperty)
                        recommendation = "Confirm that property should be set."
                        self.logger.warning(message)
                        if if_property_exists_upper == 'WARN':
                            self.command_status.add_to_log(CommandPhaseType.RUN,
                                                           CommandLogRecord(CommandStatusType.WARNING, message,
                                                                            recommendation))
                        elif if_property_exists_upper == 'FAIL':
                            self.command_status.add_to_log(CommandPhaseType.RUN,
                                                           CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                            recommendation))

            except Exception:
                # Raise an exception if an unexpected error occurs during the process
                self.warning_count += 1
                message = "Unexpected error running ListFiles command."
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
