# WebGet

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validators
import geoprocessor.util.zip_util as zip_util

import logging
import os
import requests


class WebGet(AbstractCommand):

    """
    Downloads a file from a web url.

    This command downloads a file on the web and saves it on the local computer.

    Command Parameters:
    * URL (str, required): the URL of the file to be downloaded.
    * OutputFile (str, optional): the relative pathname of the output file. Default: Filename is the same as the url
        filename. File is saved to the parent folder of the gp workflow file (the working directory).
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("URL", type("")),
        CommandParameterMetadata("OutputFile", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super(WebGet, self).__init__()
        self.command_name = "WebGet"
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

        # Check that parameter URL is a non-empty, non-None string.
        # - existence of the url will also be checked in run_command().
        pv_URL = self.get_parameter_value(parameter_name='URL', command_parameters=command_parameters)

        if not validators.validate_string(pv_URL, False, False):

            message = "URL parameter has no value."
            recommendation = "Specify the URL parameter to indicate the URL of the file to download."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that parameter OutputFile is a non-empty string (can be None).
        # - existence of the folder will also be checked in run_command().
        pv_OutputFile = self.get_parameter_value(parameter_name='OutputFile', command_parameters=command_parameters)

        if not validators.validate_string(pv_OutputFile, True, False):

            message = "OutputFile parameter has no value."
            recommendation = "Specify the OutputFile parameter to indicate the output file."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
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

    def __should_run_webget(self, output_file_abs):
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
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                    message, recommendation))

        # Return the Boolean to determine if the webget process should be run. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return run_webget

    @ staticmethod
    def __rename_files_in_a_folder(list_of_files, folder_path, new_filename):
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

    def run_command(self):
        """
        Run the command. Download the file from the web and save it on the local computer.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values
        pv_URL = self.get_parameter_value("URL")
        pv_OutputFile = self.get_parameter_value("OutputFile", default_value=None)

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
            original_filename = io_util.get_filename(pv_URL) + io_util.get_extension(pv_URL)
            output_file_absolute = io_util.verify_path_for_os(io_util.to_absolute_path(
                self.command_processor.get_property('WorkingDir'),
                self.command_processor.expand_parameter_value(original_filename, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_run_webget(output_file_absolute):

            try:

                # Get the output folder.
                output_folder = os.path.dirname(output_file_absolute)

                # Get the URL file and convert it into a request Response object
                r = requests.get(url_abs, verify=False, stream=True)

                # Get the filename of the URL and the output file
                url_filename = io_util.get_filename(url_abs)
                output_filename = io_util.get_filename(output_file_absolute)

                # Remove the output file if it already exists.
                if os.path.exists(output_file_absolute):
                    os.remove(output_file_absolute)

                # If the URL file is a zip file, process as a zip file.
                if zip_util.is_zip_file_request(r):

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

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:

                self.warning_count += 1
                message = "Unexpected error downloading file from URL {}.".format(url_abs)
                recommendation = "Check the log file for details."
                self.logger.error(message, exc_info=True)
                self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                        message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
