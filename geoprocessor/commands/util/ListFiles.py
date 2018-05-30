# ListFiles

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validators

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
    __command_parameter_metadata = [
        CommandParameterMetadata("Folder", type("")),
        CommandParameterMetadata("URL", type("")),
        CommandParameterMetadata("IncludePatterns", type("")),
        CommandParameterMetadata("ExcludePatterns", type("")),
        CommandParameterMetadata("ListFiles", type("")),
        CommandParameterMetadata("ListFolders", type("")),
        CommandParameterMetadata("ListProperty", type("")),
        CommandParameterMetadata("IfPropertyExists", type(""))]

    def __init__(self):
        """
        Initialize the command
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "ListFiles"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns: None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning = ""

        # Check that either the parameter Folder or the parameter URL is a non-empty, non-None string.
        pv_Folder = self.get_parameter_value(parameter_name='Folder', command_parameters=command_parameters)
        pv_URL = self.get_parameter_value(parameter_name='URL', command_parameters=command_parameters)

        folder_is_string = validators.validate_string(pv_Folder, False, False)
        url_is_string = validators.validate_string(pv_URL, False, False)

        if folder_is_string and url_is_string:
            message = "The Folder parameter and the URL parameter cannot both be enabled in the same command."
            recommendation = "Specify only the Folder parameter or only the URL parameter."
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        if not folder_is_string and not url_is_string:
            message = "Both the Folder parameter and the URL have no value."
            recommendation = "Specify EITHER the Folder parameter OR the URL parameter."
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that optional ListFiles parameter value is a valid Boolean value or is None.
        pv_ListFiles = self.get_parameter_value(parameter_name="ListFiles", command_parameters=command_parameters)

        if not validators.validate_bool(pv_ListFiles, none_allowed=True, empty_string_allowed=False):
            message = "ListFiles parameter value ({}) is not a recognized boolean value.".format(pv_ListFiles)
            recommendation = "Specify either 'True' or 'False for the ListFiles parameter."
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that optional ListFolders parameter value is a valid Boolean value or is None.
        pv_ListFolders = self.get_parameter_value(parameter_name="ListFolders", command_parameters=command_parameters)
        if not validators.validate_bool(pv_ListFolders, none_allowed=True, empty_string_allowed=False):
            message = "ListFolders parameter value ({}) is not a recognized boolean value.".format(pv_ListFolders)
            recommendation = "Specify either 'True' or 'False for the ListFolders parameter."
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that parameter ListProperty is a non-empty, non-None string.
        pv_ListProperty = self.get_parameter_value(parameter_name='ListProperty', command_parameters=command_parameters)

        if not validators.validate_string(pv_ListProperty, False, False):
            message = "ListProperty parameter has no value."
            recommendation = "Specify the ListProperty parameter."
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that optional parameter IfPropertyExists is either `Replace`, `ReplaceAndWarn`, `Warn`, `Fail`, None.
        pv_IfPropertyExists = self.get_parameter_value(parameter_name="IfPropertyExists",
                                                       command_parameters=command_parameters)

        acceptable_values = ["Replace", "ReplaceAndWarn", "Warn", "Fail"]

        if not validators.validate_string_in_list(pv_IfPropertyExists, acceptable_values, none_allowed=True,
                                                  empty_string_allowed=True, ignore_case=True):
            message = "IfPropertyExists parameter value ({}) is not recognized.".format(pv_IfPropertyExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfPropertyExists parameter.".format(
                acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)

        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def __should_list_files(self, folder_abs, url_abs, list_files_bool, list_dirs_bool, list_property):
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

        Returns:
            Boolean. If TRUE, the GeoLayer should be clipped. If FALSE, at least one check failed and the GeoLayer
            should not be clipped.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the Folder parameter is enabled, continue with the checks.
        if folder_abs:

            # If the Folder is not a valid folder, raise a FAILURE.
            should_run_command.append(validators.run_check(self, "IsFolderPathValid", "Folder", folder_abs, "FAIL"))

        # If the URL parameter is enabled, continue with the checks.
        if url_abs:

            # If the URL is not a valid url, raise a FAILURE.
            should_run_command.append(validators.run_check(self, "IsUrlValid", "URL", url_abs, "FAIL"))

        # If both the ListFiles and the ListFolders are set to FALSE, raise a WARNING.
        if not list_files_bool and not list_dirs_bool:

            message = "Both ListFiles and ListFolders are set to FALSE. There will be no output."
            recommendation = "Set at lease one of the parameters to TRUE."
            self.logger.warning(message)
            self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.WARNING,
                                                                                    message, recommendation))
            should_run_command.append(True)

        # If the ListProperty is the same as an already-existing Property, raise a WARNING or FAILURE (depends
        # on the value of the IfPropertyExists parameter.)
        should_run_command.append(validators.run_check(self, "IsPropertyUnique", "ListProperty", list_property, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    @staticmethod
    def scrape_html(url, read_files, read_dirs, include_list=None, exclude_list=None):
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
        link_list_filtered = string_util.filter_list_of_strings(link_list, include_list, exclude_list)

        # Return the list of filtered and available links within the input URL.
        return [url + link_name for link_name in link_list_filtered]

    def run_command(self):

        # Obtain the parameter values.
        pv_Folder = self.get_parameter_value("Folder")
        pv_URL = self.get_parameter_value("URL")
        pv_ListFiles = self.get_parameter_value("ListFiles", default_value="True")
        pv_ListFolders = self.get_parameter_value("ListFolders", default_value="True")
        pv_ListProperty = self.get_parameter_value("ListProperty")
        pv_IncludePatterns = self.get_parameter_value("IncludePatterns", default_value="*")
        pv_ExcludePatterns = self.get_parameter_value("ExcludePatterns", default_value="''")

        # Convert the IncludeAttributes and ExcludeAttributes to lists.
        to_include = string_util.delimited_string_to_list(pv_IncludePatterns)
        to_exclude = string_util.delimited_string_to_list(pv_ExcludePatterns)

        # Convert the pv_ListFiles and pv_ListFolders to Boolean values.
        list_files_bool = string_util.str_to_bool(pv_ListFiles)
        list_dirs_bool = string_util.str_to_bool(pv_ListFolders)

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
        if self.__should_list_files(folder_abs, url_abs, list_files_bool, list_dirs_bool, pv_ListProperty):

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
                        output_filtered = string_util.filter_list_of_strings(files + dirs, to_include, to_exclude)

                    # If configured to list files, continue.
                    elif list_files_bool:

                        # Filter the list of files with regards to the IIncludePatterns and ExcludePatterns.
                        output_filtered = string_util.filter_list_of_strings(files, to_include, to_exclude)

                    # If configured to list folders, continue.
                    elif list_dirs_bool:

                        # Filter the list of folders with regards to the IIncludePatterns and ExcludePatterns.
                        output_filtered = string_util.filter_list_of_strings(dirs, to_include, to_exclude)

                    else:
                        output_filtered = []

                    # Add the filtered list to the desired ListProperty. Sort the list alphabetically
                    self.command_processor.set_property(pv_ListProperty, sorted(output_filtered, key=str.lower))

                # If the input is a url.
                if pv_URL:

                    # If configured to list files and folders, continue.
                    if list_files_bool and list_dirs_bool:
                        output_filtered = self.scrape_html(url_abs, True, True, to_include, to_exclude)

                    # If configured to list files, continue.
                    elif list_files_bool:
                        output_filtered = self.scrape_html(url_abs, True, False, to_include, to_exclude)

                    # If configured to list folders, continue.
                    elif list_dirs_bool:
                        output_filtered = self.scrape_html(url_abs, False, True, to_include, to_exclude)

                    else:
                        output_filtered = None

                    # Add the filtered list to the desired ListProperty.
                    self.command_processor.set_property(pv_ListProperty, sorted(output_filtered, key=str.lower))

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error running ListFiles command."
                recommendation = "Check the log file for details."
                self.logger.error(message, exc_info=True)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
