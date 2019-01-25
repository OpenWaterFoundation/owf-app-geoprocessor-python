# UnzipFile - command to unzip a zip file
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2019 Open Water Foundation
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
import geoprocessor.util.validator_util as validators
import geoprocessor.util.zip_util as zip_util

import logging
import os


class UnzipFile(AbstractCommand):
    """
    Unzips a file.

    Command Parameters
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
    __command_parameter_metadata = [
        CommandParameterMetadata("File", type("")),
        CommandParameterMetadata("FileType", type("")),
        CommandParameterMetadata("OutputFolder", type("")),
        CommandParameterMetadata("DeleteFile", type(""))]

    def __init__(self):
        """
        Initialize the command
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "UnzipFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = "Unzip a compressed file."
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # File
        self.parameter_input_metadata['File.Description'] = "file to be unzipped"
        self.parameter_input_metadata['File.Label'] = "File"
        self.parameter_input_metadata['File.Required'] = True
        self.parameter_input_metadata['File.Tooltip'] = \
            "The file to be unzipped (relative or absolute path). ${Property} syntax is recognized."
        self.parameter_input_metadata['File.FileSelector.Type'] = "Read"
        self.parameter_input_metadata['File.FileSelector.Title'] = "Select the file to be unzipped"
        # FileType
        self.parameter_input_metadata['FileType.Description'] = "input file format"
        self.parameter_input_metadata['FileType.Label'] = "File type"
        self.parameter_input_metadata['FileType.Tooltip'] = (
            "The file format of the input File. The following file formats are currently accepted.\n\n"
            "TAR: a .tar file.\n"
            "ZIP: A .zip file.")
        self.parameter_input_metadata['FileType.Value.Default.Description'] = "from the File extension."
        # OutputFolder
        self.parameter_input_metadata['OutputFolder.Description'] = "name of the destination folder"
        self.parameter_input_metadata['OutputFolder.Label'] = "Output folder"
        self.parameter_input_metadata['OutputFolder.Tooltip'] = (
            "The name of the destination folder. The extracted files are saved here.\n"
            "${Property} syntax is recognized.")
        self.parameter_input_metadata['OutputFolder.FileSelector.Type'] = "Write"
        self.parameter_input_metadata['OutputFolder.FileSelector.Title'] = "Select the destination folder"
        self.parameter_input_metadata['OutputFolder.Value.Default.Description'] = "parent folder of the File"
        # DeleteFile
        self.parameter_input_metadata['DeleteFile.Description'] = 'whether to delete the file'
        self.parameter_input_metadata['DeleteFile.Label'] = "Delete file?"
        self.parameter_input_metadata['DeleteFile.Tooltip'] = (
            "Boolean.\n\n"
            "If True, the compressed file is deleted after the extraction.\n"
            "If False, the compressed file remains after the extraction.")
        self.parameter_input_metadata['DeleteFile.Value.Default'] = "False"
        self.parameter_input_metadata['DeleteFile.Values'] = ["", "True", "False"]

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

        # Check that either the parameter File is a non-empty, non-None string.
        pv_File = self.get_parameter_value(parameter_name='File', command_parameters=command_parameters)

        if not validators.validate_string(pv_File, False, False):

            message = "File parameter has no value."
            recommendation = "Specify the File parameter to indicate the compressed file to extract."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional parameter FileType is an acceptable value or is None.
        pv_FileType = self.get_parameter_value(parameter_name="FileType", command_parameters=command_parameters)

        acceptable_values = ["Zip", "Tar"]

        if not validators.validate_string_in_list(pv_FileType, acceptable_values, none_allowed=True,
                                                  empty_string_allowed=False, ignore_case=True):
            message = "FileType parameter value ({}) is not recognized.".format(pv_FileType)
            recommendation = "Specify one of the acceptable values ({}) for the" \
                             " FileType parameter.".format(acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional DeleteFile parameter value is a valid Boolean value or is None.
        pv_DeleteFile = self.get_parameter_value(parameter_name="DeleteFile", command_parameters=command_parameters)

        if not validators.validate_bool(pv_DeleteFile, none_allowed=True, empty_string_allowed=False):
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

    def __should_extract_file(self, file_abs, output_folder_abs, file_type):
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
        should_run_command = []

        # If the File parameter value is not a valid file, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsFilePathValid", "File", file_abs, "FAIL"))

        # If the OutputFolder parameter value is not a valid folder, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsFolderPathValid", "OutputFolder", output_folder_abs,
                                                       "FAIL"))

        # If the File Type is not recognized, raise a FAILURE.
        if file_type is None:
            message = "A valid FileType cannot be determined from the file ({}).".format(file_abs)
            recommendation = "Use the FileType parameter to assign the appropriate file type."
            should_run_command.append(False)
            self.logger.error(message)
            self.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.FAILURE,
                                                                                  message, recommendation))

        # If the File Type is not actually recognized by the input File, raise a FAILURE.
        if file_type.upper() == "ZIP":
            should_run_command.append(validators.run_check(self, "IsZipFile", "File", file_abs, "FAIL"))
        elif file_type.upper() == "TAR":
            should_run_command.append(validators.run_check(self, "IsTarFile", "File", file_abs, "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    @staticmethod
    def __get_default_file_type(file_path):
        """
        Helper function to get the default FileType parameter value.

        Arg:
            file_path: the absolute path to the input File parameter

        Returns: The default FileType parameter value. Returns None if the file extension does not correlate with
            a compatible FileType.
        """

        # A dictionary of compatible file extensions and their corresponding FileType.
        # key: Uppercase file extension.
        # value: Uppercase file type.
        dic = {".TAR": "TAR", ".ZIP": "ZIP"}

        # Iterate over the dictionary and return the FileType that corresponds to the the input file's extension.
        for ext, file_type in dic.items():
            if io_util.get_extension(file_path).upper() == ext:
                return file_type

        # If the file extension is not recognized, return None.
        return None

    def run_command(self):
        """
        Run the command. Extract the compressed file.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the File and the DeleteFile parameter values.
        pv_File = self.get_parameter_value("File")
        pv_DeleteFile = self.get_parameter_value("DeleteFile", default_value="False")

        # Convert the File parameter value relative path to an absolute path. Expand for ${Property} syntax.
        file_abs = io_util.verify_path_for_os(io_util.to_absolute_path(
            self.command_processor.get_property('WorkingDir'),
            self.command_processor.expand_parameter_value(pv_File, self)))

        # Get the FileType parameter value.
        default_file_ext = self.__get_default_file_type(file_abs)
        pv_FileType = self.get_parameter_value("FileType", default_value=default_file_ext)

        # Get the OutputFolder parameter value.
        parent_folder = io_util.get_path(file_abs)
        pv_OutputFolder = self.get_parameter_value("OutputFolder", default_value=parent_folder)

        # Convert the OutputFolder parameter value relative path to an absolute path. Expand for ${Property} syntax.
        output_folder_abs = io_util.verify_path_for_os(io_util.to_absolute_path(
            self.command_processor.get_property('WorkingDir'),
            self.command_processor.expand_parameter_value(pv_OutputFolder, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_extract_file(file_abs, output_folder_abs, pv_FileType):

            try:

                # If the file is a .zip file, extract the zip file.
                if pv_FileType.upper() == "ZIP":

                    zip_util.unzip_all_files(file_abs, output_folder_abs)

                # If the file is a .tar file, extract the tar file.
                elif pv_FileType.upper() == "TAR":

                    zip_util.untar_all_files(file_abs, output_folder_abs)

                # If configured, remove the input compressed file.
                if string_util.str_to_bool(pv_DeleteFile):
                    os.remove(file_abs)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error extracting the {} file ({}).".format(pv_FileType, pv_File)
                recommendation = "Check the log file for details."
                self.logger.error(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
