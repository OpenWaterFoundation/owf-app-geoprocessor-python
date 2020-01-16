# ExtractFile - command to extract a file from a zip file
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

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util
import geoprocessor.util.zip_util as zip_util

import logging
import os


class ExtractFile(AbstractCommand):
    """
    Extracts a file.

    Command Parameters
    * File (str, required): the path to the file to extract relative or absolute)
    * FileType (str, optional): the type of compressed file. Defaulted to 'zip'. Must be one of the following:
        `zip`: ZIP file (.zip)
        `tar`: Tape archive (.tar)
    * OutputFolder (str, optional): the folder that will hold the extracted contents of the compressed file.
        Default: The parent folder of the compressed file.
    * DeleteFile (boolean, optional): If TRUE, the compressed file will be deleted after the extraction takes place.
        If FALSE, the compressed file will remain. Default: TRUE
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("File", type("")),
        CommandParameterMetadata("FileType", type("")),
        CommandParameterMetadata("OutputFolder", type("")),
        CommandParameterMetadata("DeleteFile", type(""))]

    def __init__(self) -> None:
        """
        Initialize the command
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "ExtractFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

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
        warning = ""

        # Check that either the parameter File is a non-empty, non-None string.
        # noinspection PyPep8Naming
        pv_File = self.get_parameter_value(parameter_name='File', command_parameters=command_parameters)

        if not validator_util.validate_string(pv_File, False, False):

            message = "File parameter has no value."
            recommendation = "Specify the File parameter to indicate the compressed file to extract."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional parameter FileType is an acceptable value or is None.
        # noinspection PyPep8Naming
        pv_FileType = self.get_parameter_value(parameter_name="FileType", command_parameters=command_parameters)

        acceptable_values = ["Zip", "Tar"]

        if not validator_util.validate_string_in_list(pv_FileType, acceptable_values, none_allowed=True,
                                                      empty_string_allowed=False, ignore_case=True):
            message = "FileType parameter value ({}) is not recognized.".format(pv_FileType)
            recommendation = "Specify one of the acceptable values ({}) for the" \
                             " FileType parameter.".format(acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional DeleteFile parameter value is a valid Boolean value or is None.
        # noinspection PyPep8Naming
        pv_DeleteFile = self.get_parameter_value(parameter_name="DeleteFile", command_parameters=command_parameters)

        if not validator_util.validate_bool(pv_DeleteFile, none_allowed=True, empty_string_allowed=False):
            message = "DeleteFile parameter value ({}) is not a recognized boolean value.".format(pv_DeleteFile)
            recommendation = "Specify either 'True' or 'False for the DeleteFile parameter."
            warning += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)

        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def __should_extract_file(self, file_abs: str, output_folder_abs: str, file_type: str) -> bool:
        """
        Checks the following:
        * the File is a valid file
        * the OutputFolder is a valid folder
        * the FileType correctly identifies the File's type

        Args:
            file_abs (str): the full path to the input compressed File
            output_folder_abs(str): the full path to the OutputFolder
            file_type(str): the FileType value depicting the file type of the input File

        Returns:
            Boolean. If TRUE, the file should be extracted. If FALSE, at least one check failed and the file should
            not be extracted.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the File parameter value is not a valid file, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsFilePathValid", "File", file_abs, "FAIL"))

        # If the OutputFolder parameter value is not a valid folder, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsFolderPathValid", "OutputFolder", output_folder_abs,
                                                           "FAIL"))

        # If the File Type is not actually recognized by the input File, raise a FAILURE.
        if file_type == "ZIP":
            should_run_command.append(validator_util.run_check(self, "IsZipFile", "File", file_abs, "FAIL"))
        elif file_type == "TAR":
            should_run_command.append(validator_util.run_check(self, "IsTarFile", "File", file_abs, "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Extract the compressed file.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_File = self.get_parameter_value("File")
        # noinspection PyPep8Naming
        pv_FileType = self.get_parameter_value("FileType", default_value="zip").upper()
        # noinspection PyPep8Naming
        pv_DeleteFile = self.get_parameter_value("DeleteFile", default_value="True")

        # Convert the File parameter value relative path to an absolute path. Expand for ${Property} syntax.
        file_abs = io_util.verify_path_for_os(io_util.to_absolute_path(
            self.command_processor.get_property('WorkingDir'),
            self.command_processor.expand_parameter_value(pv_File, self)))

        # Get the OutputFolder parameter value.
        parent_folder = io_util.get_path(file_abs)
        # noinspection PyPep8Naming
        pv_OutputFolder = self.get_parameter_value("OutputFolder", default_value=parent_folder)

        # Convert the OutputFolder parameter value relative path to an absolute path. Expand for ${Property} syntax.
        output_folder_abs = io_util.verify_path_for_os(io_util.to_absolute_path(
            self.command_processor.get_property('WorkingDir'),
            self.command_processor.expand_parameter_value(pv_OutputFolder, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_extract_file(file_abs, output_folder_abs, pv_FileType):

            # noinspection PyBroadException
            try:

                # If the file is a .zip file, extract the zip file.
                if pv_FileType == "ZIP":

                    zip_util.unzip_all_files(file_abs, output_folder_abs)

                # If the file is a .tar file, extract the tar file.
                elif pv_FileType == "TAR":

                    zip_util.untar_all_files(file_abs, output_folder_abs)

                # If configured, remove the input compressed file.
                if string_util.str_to_bool(pv_DeleteFile):
                    os.remove(file_abs)

            # Raise an exception if an unexpected error occurs during the process
            except Exception:
                self.warning_count += 1
                message = "Unexpected error extracting the {} file ({}).".format(pv_FileType, pv_File)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
