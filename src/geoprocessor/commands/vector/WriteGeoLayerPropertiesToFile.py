# WriteGeoLayerPropertiesToFile - command to write GeoLayer properties to a file
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

import logging


class WriteGeoLayerPropertiesToFile(AbstractCommand):
    """
    The WriteGeoLayerPropertiesToFile command writes GeoLayer properties to a file.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("IncludeProperties", type("")),
        CommandParameterMetadata("WriteMode", type("")),
        CommandParameterMetadata("FileFormat", type("")),
        CommandParameterMetadata("SortOrder", type(""))
    ]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = "Write GeoLayer properties to a file."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "identifier of the GeoLayer to write"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = "The GeoLayer identifier, can use ${Property}."
    # OutputFile
    __parameter_input_metadata['OutputFile.Description'] = "property file to write"
    __parameter_input_metadata['OutputFile.Label'] = "Output file"
    __parameter_input_metadata['OutputFile.Required'] = True
    __parameter_input_metadata['OutputFile.Tooltip'] = \
        "The property file to write, as an absolute path or relative to the command file, can use ${Property"
    __parameter_input_metadata['OutputFile.FileSelector.Type'] = "Write"
    __parameter_input_metadata['OutputFile.FileSelector.Title'] = "Select file to write"
    __parameter_input_metadata['OutputFile.FileSelector.Filters'] = \
        ["Properties file (*.txt)", "All files (*)"]
    # IncludeProperties
    __parameter_input_metadata['IncludeProperties.Description'] = "properties to write"
    __parameter_input_metadata['IncludeProperties.Label'] = "Include properties"
    __parameter_input_metadata['IncludeProperties.Tooltip'] = (
        "The names of properties to write, separated by commas. "
        "The '*' wildcard can be used to indicate multiple properties.")
    __parameter_input_metadata['IncludeProperties.Value.Default.Description'] = "write all properties"
    # WriteMode
    __parameter_input_metadata['WriteMode.Description'] = "how to write"
    __parameter_input_metadata['WriteMode.Label'] = "Write mode"
    __parameter_input_metadata['WriteMode.Tooltip'] = (
        "Indicates how the file should be written:\n"
        "Append – append the properties to the file without checking for matches (create the file if "
        "it does not exist).\n"
        "Overwrite – overwrite the properties file.")
    __parameter_input_metadata['WriteMode.Values'] = ["", "Append", "Overwrite"]
    __parameter_input_metadata['WriteMode.Value.Default'] = "Overwrite"
    # FileFormat
    __parameter_input_metadata['FileFormat.Description'] = "file format"
    __parameter_input_metadata['FileFormat.Label'] = "File format"
    __parameter_input_metadata['FileFormat.Tooltip'] = "The file format."
    __parameter_input_metadata['FileFormat.Values'] = ["", "NameTypeValue", "NameTypeValuePython", "NameValue"]
    __parameter_input_metadata['FileFormat.Value.Default'] = 'NameValueType'
    # SortOrder
    __parameter_input_metadata['SortOrder.Description'] = "sort order"
    __parameter_input_metadata['SortOrder.Label'] = "Sort order"
    __parameter_input_metadata['SortOrder.Tooltip'] = "The sort order."
    __parameter_input_metadata['SortOrder.Values'] = ["", "Ascending", "Descending"]
    __parameter_input_metadata['SortOrder.Value.Default'] = 'Ascending'

    # Choices for WriteMode, used to validate parameter and display in editor.
    __choices_WriteMode = ["Append", "Overwrite"]

    # Choices for FileFormat, used to validate parameter and display in editor.
    __choices_FileFormat = ["NameTypeValue", "NameTypeValuePython", "NameValue"]

    # Choices for SortOrder, used to validate parameter and display in editor.
    __choices_SortOrder = ["Ascending", "Descending"]

    def __init__(self) -> None:
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data
        super().__init__()
        self.command_name = "WriteGeoLayerPropertiesToFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display.
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata.
        self.parameter_input_metadata = self.__parameter_input_metadata

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

        # WriteMode is optional, will default to Overwrite at runtime.
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

        # FileFormat is optional, will default to NameTypeValue at runtime.
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

        # SortOrder is optional, will default to None (no sort) at runtime.
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
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            logger.warning(warning_message)
            raise CommandParameterError(warning_message)

        # Refresh the phase severity.
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

        # Get data for the command.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value('OutputFile')
        # noinspection PyPep8Naming
        pv_IncludeProperties = self.get_parameter_value('IncludeProperties')
        # noinspection PyPep8Naming
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
            file_format = 'NameValueType'  # Default
        # noinspection PyPep8Naming
        pv_SortOrder = self.get_parameter_value('SortOrder')
        sort_order = 0  # no sort
        if pv_SortOrder is not None:
            if pv_SortOrder == 'Ascending':
                sort_order = 1
            elif pv_SortOrder == 'Descending':
                sort_order = -1

        # Runtime checks on input.

        # noinspection PyPep8Naming
        pv_OutputFile_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings about command parameters."
            logger.warning(message)
            raise CommandError(message)

        # Write the output file.

        # noinspection PyBroadException
        try:
            # Get the GeoLayer object.
            geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)
            if geolayer is None:
                message = 'Unable to find GeoLayer for GeoLayerID="' + pv_GeoLayerID + '"'
                warning_count += 1
                logger.warning(message)
                self.command_status.add_to_log(
                    CommandPhaseType.RUN,
                    CommandLogRecord(CommandStatusType.FAILURE, message, "Check the log file for details."))
            else:
                problems = []  # Empty list of properties.
                io_util.write_property_file(pv_OutputFile_absolute, geolayer.properties,
                                            include_properties, write_mode, file_format, sort_order, problems)
                # Record any problems that were found.
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
            raise CommandError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
