# WebGet - command to retrieve a file from the web
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
import geoprocessor.util.validator_util as validator_util
import geoprocessor.util.zip_util as zip_util

import logging
import os
import requests

from requests.auth import HTTPBasicAuth


class WebGet(AbstractCommand):
    """
    Downloads a file from a web url.

    This command downloads a file on the web and saves it on the local computer.

    Command Parameters:
    * URL (str, required): the URL of the file to be downloaded.
    * OutputFile (str, optional): the relative pathname of the output file. Default: Filename is the same as the url
        filename. File is saved to the parent folder of the gp workflow file (the working directory).
    * Username (str, optional): an appropriate username if the URL to download is private
    * Password (str, optional): an appropriate password if the URL to download is private
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("URL", type("")),
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("Username", type("")),
        CommandParameterMetadata("Password", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Download a file from a URL."
    __command_metadata['EditorType'] = "Simple"

    __parameter_input_metadata = dict()
    # URL
    __parameter_input_metadata['URL.Description'] = "URL to read content"
    __parameter_input_metadata['URL.Label'] = "URL"
    __parameter_input_metadata['URL.Tooltip'] = \
        "Specify the URL from which to read content, can use ${Property}."
    __parameter_input_metadata['URL.Required'] = True
    __parameter_input_metadata['URL.FileSelector.Type'] = "Read"
    # Output File
    __parameter_input_metadata['OutputFile.Description'] = ""
    __parameter_input_metadata['OutputFile.Label'] = "Output File"
    __parameter_input_metadata['OutputFile.Tooltip'] = (
        "The output file path (relative or absolute). ${Property} syntax is recognized.\n"
        "Formatting specifiers such as %f are recognized.\n"
        "The output file will be overwritten if it already exists.\n"
        "The password is not encrypted here so read-only or public accounts are recommended.")
    __parameter_input_metadata['OutputFile.Required'] = False
    __parameter_input_metadata['OutputFile.FileSelector.Type'] = "Write"
    __parameter_input_metadata['OutputFile.FileSelector.Filters'] = ["All files (*)"]
    # Username
    __parameter_input_metadata['Username.Description'] = "case-sensitive"
    __parameter_input_metadata['Username.Label'] = "User name"
    __parameter_input_metadata['Username.Tooltip'] = "Specify a valid username to access a private URL file."
    __parameter_input_metadata['Username.Required'] = False
    # Password
    __parameter_input_metadata['Password.Description'] = "case-sensitive"
    __parameter_input_metadata['Password.Label'] = "Password"
    __parameter_input_metadata['Password.Tooltip'] = "Specify a valid password to access a private URL file."
    __parameter_input_metadata['Password.Required'] = False

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        # Name of command for menu and window title
        self.command_name = "WebGet"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

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

    def check_runtime_data(self, output_file_abs: str) -> bool:
        """
       Checks the following:
       * the output folder is a valid folder

       Args:
           output_file_abs: the full pathname to the output file

       Returns:
           run_webget: Boolean. If TRUE, the webget process should be run. If FALSE, it should not be run.
       """

        # Boolean to determine if the webget process should be run. Set to true until an error occurs.
        run_webget = True

        # If the OutputFolder is not a valid folder, raise a FAILURE.
        output_folder = os.path.dirname(output_file_abs)
        if not os.path.isdir(output_folder):

            run_webget = False
            self.warning_count += 1
            message = 'The output folder ({}) of the OutputFile is not a valid folder.'.format(output_folder)
            recommendation = 'Specify a valid relative pathname for the output file.'
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.FAILURE,
                                                                                  message, recommendation))

        # Return the Boolean to determine if the webget process should be run. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return run_webget

    @ staticmethod
    def __rename_files_in_a_folder(list_of_files: [str], folder_path: str, new_filename: str) -> None:
        """

        Renames files within a folder to a new name. The files retain their pathname (they stay in the same folder)
        and retain their file extension.

        Args:
            list_of_files (list of strings): a list of filenames (without the path but WITH the extension)
            folder_path (string): the full pathname to the folder that is storing the files in the list_of_files list
            new_filename (string): the new filename for the files in the list_of_files list. All files will be renamed
                to this same value.

        Returns:
             None.

        Raises:
            None.
        """

        # Iterate over the files to be renamed.
        for existing_file in list_of_files:

            # Get the full path of the existing file
            existing_path = os.path.join(folder_path, existing_file)

            # Get the file extension of the existing file
            existing_extension = io_util.get_extension(existing_path)

            # Create the full path of the renamed file. If an extension was included in the original filename, then that
            # same extension is included in the new filename.
            new_path = os.path.join(folder_path, "{}{}".format(new_filename, existing_extension))
            os.rename(existing_path, new_path)

    def run_command(self) -> None:
        """
        Run the command. Download the file from the web and save it on the local computer.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values
        # noinspection PyPep8Naming
        pv_URL = self.get_parameter_value("URL")
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value("OutputFile", default_value=None)
        # noinspection PyPep8Naming
        pv_Username = self.get_parameter_value("Username", default_value=None)
        # noinspection PyPep8Naming
        pv_Password = self.get_parameter_value("Password", default_value=None)

        # Convert the pv_URL parameter to expand for ${Property} syntax.
        url_abs = self.command_processor.expand_parameter_value(pv_URL, self)

        # Convert the OutputFile parameter value relative path to an absolute path. Expand for ${Property} syntax.
        # If the OutputFile parameter is specified, continue.
        if pv_OutputFile:
            output_file_absolute = io_util.verify_path_for_os(io_util.to_absolute_path(
                self.command_processor.get_property('WorkingDir'),
                self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        # If the OutputFile parameter is NOT specified, continue.
        else:
            # original_filename = io_util.get_filename(pv_URL) + io_util.get_extension(pv_URL)
            original_filename = io_util.get_filename(pv_URL)
            output_file_absolute = io_util.verify_path_for_os(io_util.to_absolute_path(
                self.command_processor.get_property('WorkingDir'),
                self.command_processor.expand_parameter_value(original_filename, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(output_file_absolute):
            # noinspection PyBroadException
            try:
                # Get the output folder.
                output_folder = os.path.dirname(output_file_absolute)

                # Get the URL file and convert it into a request Response object
                # Authentication Reference: http://docs.python-requests.org/en/master/user/authentication/
                r = requests.get(url_abs, auth=HTTPBasicAuth(pv_Username, pv_Password), verify=False, stream=True)

                # Get the filename of the URL and the output file
                url_filename = io_util.get_filename(url_abs)
                output_filename = io_util.get_filename(output_file_absolute)

                # Remove the output file if it already exists.
                if os.path.exists(output_file_absolute):
                    os.remove(output_file_absolute)

                if zip_util.is_zip_file_request(r):
                    # If the URL file is a zip file, process as a zip file.

                    # Create an empty list to hold the files that were downloaded/extracted to the output folder.
                    downloaded_files = []

                    with open(os.path.join(output_folder, "{}.zip".format(url_filename)), "wb") as downloaded_zip_file:
                        downloaded_zip_file.write(r.content)
                    downloaded_files.append("{}.zip".format(url_filename))

                    # Determine if the downloaded zip file(s) should be renamed. If the filename is %f then the
                    # filenames of the downloaded products should be the same as the url filenames
                    if not output_filename == '%f':
                        self.__rename_files_in_a_folder(list_of_files=downloaded_files, folder_path=output_folder,
                                                        new_filename=output_filename)

                else:
                    # Download the file to the output folder.
                    with open(os.path.join(output_folder, os.path.basename(url_abs)), "wb") as downloaded_file:
                        downloaded_file.write(r.content)

                    # Determine if the downloaded file should be renamed. If the filename is %f then the filename
                    # of the downloaded product should be the same as the url filename
                    if not output_filename == '%f':
                        self.__rename_files_in_a_folder(list_of_files=[os.path.basename(url_abs)],
                                                        folder_path=output_folder,
                                                        new_filename=output_filename)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process
                self.warning_count += 1
                message = "Unexpected error downloading file from URL {}.".format(url_abs)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.FAILURE,
                                                                                      message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
