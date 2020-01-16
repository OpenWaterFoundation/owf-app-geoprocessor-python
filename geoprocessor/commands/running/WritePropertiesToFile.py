# WritePropertiesToFile - command to write processor properties to a file
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

import logging


class WritePropertiesToFile(AbstractCommand):
    """
    The WritePropertiesToFile command writes processor properties to a file.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("IncludeProperties", type("")),
        CommandParameterMetadata("WriteMode", type("")),
        CommandParameterMetadata("FileFormat", type("")),
        CommandParameterMetadata("SortOrder", type(""))
    ]

    # Choices for WriteMode, used to validate parameter and display in editor
    __choices_WriteMode = ["Append", "Overwrite"]

    # Choices for FileFormat, used to validate parameter and display in editor
    __choices_FileFormat = ["NameTypeValue", "NameTypeValuePython", "NameValue"]

    # Choices for SortOrder, used to validate parameter and display in editor
    __choices_SortOrder = ["Ascending", "Descending"]

    def __init__(self) -> None:
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data
        super().__init__()
        self.command_name = "WritePropertiesToFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = "Write command processor properties to a file."
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # OutputFile
        self.parameter_input_metadata['OutputFile.Description'] = "output file to write"
        self.parameter_input_metadata['OutputFile.Label'] = "Output file"
        self.parameter_input_metadata['OutputFile.Required'] = True
        self.parameter_input_metadata['OutputFile.Tooltip'] = (
            "The output file to write, as an absolute path or relative to the command file.\n"
            "Can use ${Property}.")
        self.parameter_input_metadata['OutputFile.FileSelector.Type'] = "Write"
        self.parameter_input_metadata['OutputFile.FileSelector.Title'] = "Select the output file"
        # IncludeProperties
        self.parameter_input_metadata['IncludeProperties.Description'] = "names of properties to write"
        self.parameter_input_metadata['IncludeProperties.Label'] = "Include properties"
        self.parameter_input_metadata['IncludeProperties.Tooltip'] = (
            "The names of properties to write, separated by commas.\n"
            "The '*' wildcard can be used to indicate multiple properties.")
        self.parameter_input_metadata['IncludeProperties.Value.Default'] = "write all properties."
        # WriteMode
        self.parameter_input_metadata['WriteMode.Description'] = "file write mode"
        self.parameter_input_metadata['WriteMode.Label'] = "Write mode"
        self.parameter_input_metadata['WriteMode.Tooltip'] = (
            "Indicates how the file should be written:\n"
            "Append – append the properties to the file without checking for matches (create the file if "
            "it does not exist).\n"
            "Overwrite – overwrite the properties file.")
        self.parameter_input_metadata['WriteMode.Values'] = ["", "Append", "Overwrite"]
        self.parameter_input_metadata['WriteMode.Value.Default'] = "Overwrite"
        # FileFormat
        self.parameter_input_metadata['FileFormat.Description'] = "file format"
        self.parameter_input_metadata['FileFormat.Label'] = "File format"
        self.parameter_input_metadata['FileFormat.Tooltip'] = "The file format."
        self.parameter_input_metadata['FileFormat.Values'] = ["", "NameTypeValue", "NameTypeValuePython", "NameValue"]
        self.parameter_input_metadata['FileFormat.Value.Default'] = 'NameValueType'
        # SortOrder
        self.parameter_input_metadata['SortOrder.Description'] = "sort order"
        self.parameter_input_metadata['SortOrder.Label'] = "Sort order"
        self.parameter_input_metadata['SortOrder.Tooltip'] = "The sort order."
        self.parameter_input_metadata['SortOrder.Values'] = ["", "Ascending", "Descending"]
        self.parameter_input_metadata['SortOrder.Value.Default'] = 'Ascending'

    def check_command_parameters(self, command_parameters: dict) -> None:
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            None

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning_message = ""
        logger = logging.getLogger(__name__)

        # OutputFile is required
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value(parameter_name='OutputFile', command_parameters=command_parameters)
        if not validator_util.validate_string(pv_OutputFile, False, False):
            message = "The OutputFile must be specified."
            recommendation = "Specify the output file."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # IncludeProperties is optional, default to * at runtime

        # WriteMode is optional, will default to Overwrite at runtime
        # noinspection PyPep8Naming
        pv_WriteMode = self.get_parameter_value(parameter_name='WriteMode', command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_WriteMode,
                                                      self.__choices_WriteMode, True, True):
            message = "WriteMode parameter is invalid."
            recommendation = "Specify the WriteMode parameter as blank or one of " + \
                             str(self.__choices_WriteMode)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # FileFormat is optional, will default to NameTypeValue at runtime
        # noinspection PyPep8Naming
        pv_FileFormat = self.get_parameter_value(parameter_name='FileFormat', command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_FileFormat,
                                                      self.__choices_FileFormat, True, True):
            message = "FileFormat parameter is invalid."
            recommendation = "Specify the FileFormat parameter as blank or one of " + \
                             str(self.__choices_FileFormat)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # SortOrder is optional, will default to None (no sort) at runtime
        # noinspection PyPep8Naming
        pv_SortOrder = self.get_parameter_value(parameter_name='SortOrder', command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_SortOrder,
                                                      self.__choices_SortOrder, True, True):
            message = "SortOrder parameter is invalid."
            recommendation = "Specify the SortOrder parameter as blank or one of " + \
                             str(self.__choices_SortOrder)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception
        if len(warning_message) > 0:
            logger.warning(warning_message)
            raise ValueError(warning_message)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def run_command(self) -> None:
        """
        Run the command.  Write the processor properties to a file.

        Returns:
            None

        Raises:
                RuntimeError: if a runtime input error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Get data for the command
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value('OutputFile')
        # noinspection PyPep8Naming
        pv_IncludeProperties = self.get_parameter_value('IncludeProperties')
        include_properties = []  # Default
        if pv_IncludeProperties is not None and len(pv_IncludeProperties) > 0:
            include_properties = string_util.delimited_string_to_list(pv_IncludeProperties)
        # noinspection PyPep8Naming
        pv_WriteMode = self.get_parameter_value('WriteMode')
        write_mode = pv_WriteMode
        if pv_WriteMode is None or pv_WriteMode == "":
            write_mode = 'Overwrite'  # Default
        # noinspection PyPep8Naming
        pv_FileFormat = self.get_parameter_value('FileFormat')
        file_format = pv_FileFormat
        if pv_FileFormat is None or pv_FileFormat == "":
            file_format = 'NameTypeValue'  # Default
        # noinspection PyPep8Naming
        pv_SortOrder = self.get_parameter_value('SortOrder')
        sort_order = 0  # no sort
        if pv_SortOrder is not None:
            if pv_SortOrder == 'Ascending':
                sort_order = 1
            elif pv_SortOrder == 'Descending':
                sort_order = -1

        # Runtime checks on input

        # noinspection PyPep8Naming
        pv_OutputFile_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings about command parameters."
            logger.warning(message)
            raise ValueError(message)

        # Write the output file

        # noinspection PyBroadException
        try:
            problems = []  # Empty list of properties
            io_util.write_property_file(pv_OutputFile_absolute, self.command_processor.properties,
                                        include_properties, write_mode, file_format, sort_order, problems)
            # Record any problems that were found
            for problem in problems:
                warning_count += 1
                logger.warning(problem)
                self.command_status.add_to_log(
                    CommandPhaseType.RUN,
                    CommandLogRecord(CommandStatusType.FAILURE, problem,
                                     "See the log file for details."))

        except Exception:
            warning_count += 1
            message = 'Unexpected error writing file "' + pv_OutputFile_absolute + '"'
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "See the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            logger.warning(message)
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
