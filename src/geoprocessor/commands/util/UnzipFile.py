# UnzipFile - command to unzip a zip file
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2023 Open Water Foundation
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
import geoprocessor.util.string_util as string_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validator_util
import geoprocessor.util.zip_util as zip_util

import logging
import os
from pathlib import Path


class UnzipFile(AbstractCommand):
    """
    Unzips a file.

    Command Parameters:
    * File (str, required): the path to the file to extract relative or absolute)
    * FileType (str, optional): the type of compressed file.  Must be one of the following:
        `zip`: ZIP file (.zip)
        `tar`: Tape archive (.tar)
        Default: determined by the files extension.
    * OutputFolder (str, optional): the folder that will hold the extracted contents of the compressed file.
        Default: The parent folder of the compressed file.
    * DeleteFile (boolean, optional): If TRUE, the compressed file will be deleted after the extraction takes place.
        If FALSE, the compressed file will remain. Default: FALSE
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("File", type("")),
        CommandParameterMetadata("FileType", type("")),
        CommandParameterMetadata("OutputFolder", type("")),
        CommandParameterMetadata("IfFolderDoesNotExist", type("")),
        CommandParameterMetadata("DeleteFile", type(""))]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = "Unzip a compressed file."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # File
    __parameter_input_metadata['File.Description'] = "file to be unzipped"
    __parameter_input_metadata['File.Label'] = "File"
    __parameter_input_metadata['File.Required'] = True
    __parameter_input_metadata['File.Tooltip'] = \
        "The file to be unzipped (relative or absolute path). ${Property} syntax is recognized."
    __parameter_input_metadata['File.FileSelector.Type'] = "Read"
    __parameter_input_metadata['File.FileSelector.Title'] = "Select the file to be unzipped"
    __parameter_input_metadata['File.FileSelector.Filters'] = ["Zip file (*.tar *.zip)", "All files (*)"]
    # FileType
    __parameter_input_metadata['FileType.Description'] = "input file format"
    __parameter_input_metadata['FileType.Label'] = "File type"
    __parameter_input_metadata['FileType.Tooltip'] = (
        "The file format of the input file. The following file formats are currently accepted:\n\n"
        "tar: a .tar file.\n"
        "zip: A .zip file.")
    __parameter_input_metadata['FileType.Values'] = ['tar', 'zip']
    __parameter_input_metadata['FileType.Value.Default'] = 'zip'
    __parameter_input_metadata['FileType.Value.Default.Description'] = "from the File extension."
    __parameter_input_metadata['FileType.Value.Default.ForEditor'] = ''
    # OutputFolder
    __parameter_input_metadata['OutputFolder.Description'] = "name of the destination folder"
    __parameter_input_metadata['OutputFolder.Label'] = "Output folder"
    __parameter_input_metadata['OutputFolder.Tooltip'] = (
        "The name of the destination folder. The extracted files are saved here.\n"
        "${Property} syntax is recognized.")
    __parameter_input_metadata['OutputFolder.FileSelector.Type'] = "Write"
    __parameter_input_metadata['OutputFolder.FileSelector.Title'] = "Select the destination folder"
    __parameter_input_metadata['OutputFolder.Value.Default.Description'] = "parent folder of the File"
    # IfFolderDoesNotExist
    __parameter_input_metadata['IfFolderDoesNotExist.Description'] = 'action if output folder does not exist'
    __parameter_input_metadata['IfFolderDoesNotExist.Label'] = "If folder does not exist?"
    __parameter_input_metadata['IfFolderDoesNotExist.Tooltip'] = (
        "If Create, create the output folder if it does not exist.\n"
        "If Warn, warn and do not complete the command.")
    __parameter_input_metadata['IfFolderDoesNotExist.Value.Default'] = "Warn"
    __parameter_input_metadata['IfFolderDoesNotExist.Values'] = ["", "Create", "Warn", "Fail"]
    # DeleteFile
    __parameter_input_metadata['DeleteFile.Description'] = 'whether to delete the zip file when done'
    __parameter_input_metadata['DeleteFile.Label'] = "Delete file?"
    __parameter_input_metadata['DeleteFile.Tooltip'] = (
        "Boolean.\n\n"
        "If True, the compressed file is deleted after the extraction.\n"
        "If False, the compressed file remains after the extraction.")
    __parameter_input_metadata['DeleteFile.Value.Default'] = "False"
    __parameter_input_metadata['DeleteFile.Values'] = ["", "True", "False"]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data.
        super().__init__()
        self.command_name = "UnzipFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display.
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata.
        self.parameter_input_metadata = self.__parameter_input_metadata

        # Class data.
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

        # Check that optional parameter FileType is an acceptable value or is None.
        # noinspection PyPep8Naming
        pv_FileType = self.get_parameter_value(parameter_name="FileType", command_parameters=command_parameters)

        acceptable_values = self.__parameter_input_metadata['FileType.Values']

        if not validator_util.validate_string_in_list(pv_FileType, acceptable_values, none_allowed=True,
                                                      empty_string_allowed=True, ignore_case=True):
            message = "FileType parameter value ({}) is not recognized.".format(pv_FileType)
            recommendation = "Specify one of the acceptable values ({}) for the" \
                             " FileType parameter.".format(acceptable_values)
            warning_message += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional IfFolderDoesNotExist parameter value is a valid value or is None.
        # noinspection PyPep8Naming
        pv_IfFolderDoesNotExist = self.get_parameter_value(parameter_name="IfFolderDoesNotExist",
                                                           command_parameters=command_parameters)

        if not validator_util.validate_string_in_list(pv_IfFolderDoesNotExist, self.
                                                      __parameter_input_metadata['IfFolderDoesNotExist.Values'],
                                                      True, True, False):
            message = "IfFolderDoesNotExist parameter value ({}) is not a recognized value.".format(
                pv_IfFolderDoesNotExist)
            recommendation = "Specify either 'Create', 'Warn', or 'Fail' for the IfFolderDoesNotExist parameter."
            warning_message += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional DeleteFile parameter value is a valid Boolean value or is None.
        # noinspection PyPep8Naming
        pv_DeleteFile = self.get_parameter_value(parameter_name="DeleteFile", command_parameters=command_parameters)

        if not validator_util.validate_bool(pv_DeleteFile, none_allowed=True, empty_string_allowed=False):
            message = "DeleteFile parameter value ({}) is not a recognized boolean value.".format(pv_DeleteFile)
            recommendation = "Specify either 'True' or 'False for the DeleteFile parameter."
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
            # Refresh the phase severity.
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, file_abs: str, file_type: str) -> bool:
        """
        Checks the following:
        * the File is a valid file
        * the FileType correctly identifies the File's type

        Args:
            file_abs (str): the full path to the input compressed File
            file_type(str): the FileType value depicting the file type of the input File

        Returns:
            Boolean. If TRUE, the file should be extracted. If FALSE, at least one check failed and the file should
            not be extracted.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests.
        # If TRUE, the test confirms that the command should be run.
        should_run_command = list()

        # If the File parameter value is not a valid file, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsFilePathValid", "File", file_abs, "FAIL"))

        # If the File Type is not recognized, raise a FAILURE.
        if file_type is None:
            message = "A valid FileType cannot be determined from the file ({}).".format(file_abs)
            recommendation = "Use the FileType parameter to assign the appropriate file type."
            should_run_command.append(False)
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.FAILURE,
                                                                                  message, recommendation))
        else:
            # If the File Type is not actually recognized by the input File, raise a FAILURE.
            if file_type.upper() == "ZIP":
                should_run_command.append(validator_util.run_check(self, "IsZipFile", "File", file_abs, "FAIL"))
            elif file_type.upper() == "TAR":
                should_run_command.append(validator_util.run_check(self, "IsTarFile", "File", file_abs, "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    @staticmethod
    def __get_default_file_type(file_path: str) -> str or None:
        """
        Helper function to get the default FileType parameter value.

        Arg:
            file_path: the absolute path to the input File parameter

        Returns: The default FileType parameter value.
            Returns None if the file extension does not correlate with a compatible FileType.
        """

        # A dictionary of compatible file extensions and their corresponding FileType.
        # key: Uppercase file extension.
        # value: Uppercase file type.
        dic = {"TAR": "TAR", "ZIP": "ZIP"}

        # Iterate over the dictionary and return the FileType that corresponds to the input file's extension.
        for ext, file_type in dic.items():
            if io_util.get_extension(file_path).upper() == ext:
                return file_type

        # If the file extension is not recognized, return None.
        return None

    def run_command(self) -> None:
        """
        Run the command. Extract the compressed file.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the File and the DeleteFile parameter values.
        # noinspection PyPep8Naming
        pv_File = self.get_parameter_value("File")
        # noinspection PyPep8Naming
        pv_IfFolderDoesNotExist = \
            self.get_parameter_value("IfFolderDoesNotExist",
                                     default_value=self.__parameter_input_metadata[
                                         'IfFolderDoesNotExist.Value.Default'])
        # noinspection PyPep8Naming
        pv_DeleteFile = self.get_parameter_value("DeleteFile", default_value="False")

        # Convert the File parameter value relative path to an absolute path. Expand for ${Property} syntax.
        file_abs = io_util.verify_path_for_os(io_util.to_absolute_path(
            self.command_processor.get_property('WorkingDir'),
            self.command_processor.expand_parameter_value(pv_File, self)))

        # Get the FileType parameter value.
        default_file_ext = self.__get_default_file_type(file_abs)
        # noinspection PyPep8Naming
        pv_FileType = self.get_parameter_value("FileType", default_value=default_file_ext)

        # Get the OutputFolder parameter value.
        parent_folder = io_util.get_path(file_abs)
        # noinspection PyPep8Naming
        pv_OutputFolder = self.get_parameter_value("OutputFolder", default_value=parent_folder)

        # Convert the OutputFolder parameter value relative path to an absolute path. Expand for ${Property} syntax.
        output_folder_abs = io_util.verify_path_for_os(io_util.to_absolute_path(
            self.command_processor.get_property('WorkingDir'),
            self.command_processor.expand_parameter_value(pv_OutputFolder, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(file_abs, pv_FileType):
            # ok_to_run indicates if it is OK to run the command's main logic.
            ok_to_run = True
            if not os.path.isdir(output_folder_abs):
                # Output folder does not exist.
                self.logger.info("Output folder does not exist.")
                # If requested, create the output folder.
                IfFolderDoesNotExist_upper = pv_IfFolderDoesNotExist.upper()
                if IfFolderDoesNotExist_upper == 'CREATE':
                    folder_path = Path(output_folder_abs)
                    folder_path.mkdir(parents=True)
                elif IfFolderDoesNotExist_upper == 'WARN':
                    self.warning_count += 1
                    message = "Output folder ({}) does not exist.)".format(pv_OutputFolder)
                    recommendation = "Make sure the folder exists before this command is run " \
                                     "or use 'IfFolderDoesNotExist=Create'"
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.WARNING, message, recommendation))
                    ok_to_run = False
                elif IfFolderDoesNotExist_upper == 'FAIL':
                    self.warning_count += 1
                    message = "Output folder ({}) does not exist.)".format(pv_OutputFolder)
                    recommendation = "Make sure the folder exists before this command is run " \
                                     "or use 'IfFolderDoesNotExist=Create'"
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
                    ok_to_run = False

            if ok_to_run:
                # noinspection PyBroadException
                try:
                    if pv_FileType.upper() == "ZIP":
                        # If the file is a .zip file, extract the zip file.
                        zip_util.unzip_all_files(file_abs, output_folder_abs)

                    elif pv_FileType.upper() == "TAR":
                        # If the file is a .tar file, extract the tar file.
                        zip_util.untar_all_files(file_abs, output_folder_abs)

                    if string_util.str_to_bool(pv_DeleteFile):
                        # If configured, remove the input compressed file.
                        os.remove(file_abs)

                # Raise an exception if an unexpected error occurs during the process.
                except Exception:
                    self.warning_count += 1
                    message = "Unexpected error extracting the {} file ({}).".format(pv_FileType, pv_File)
                    recommendation = "Check the log file for details."
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred.
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
