# WriteGeoLayerPropertiesToFile command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.io as io_util
import geoprocessor.util.string as string_util
import geoprocessor.util.validators as validators

import logging
import os
import sys
import traceback


class WriteGeoLayerPropertiesToFile(AbstractCommand):
    """
    The WriteGeoLayerPropertiesToFile command writes GeoLayer properties to a file.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
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

    def __init__(self):
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data
        super(WriteGeoLayerPropertiesToFile, self).__init__()
        self.command_name = "WriteGeoLayerPropertiesToFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            Nothing.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning_message = ""
        logger = logging.getLogger(__name__)

        # GeoLayerID is required
        # - non-empty, non-None string.
        # - existence of the GeoLayer will also be checked in run_command().
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID',
                                                 command_parameters=command_parameters)
        if not validators.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the GeoLayer to process."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # OutputFile is required
        pv_OutputFile = self.get_parameter_value(parameter_name='OutputFile', command_parameters=command_parameters)
        if not validators.validate_string(pv_OutputFile, False, False):
            message = "The OutputFile must be specified."
            recommendation = "Specify the output file."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # IncludeProperties is optional, default to * at runtime

        # WriteMode is optional, will default to Overwrite at runtime
        pv_WriteMode = self.get_parameter_value(parameter_name='WriteMode', command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_WriteMode,
                                                  self.__choices_WriteMode, True, True):
            message = "WriteMode parameter is invalid."
            recommendation = "Specify the WriteMode parameter as blank or one of " + \
                             str(self.__choices_WriteMode)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # FileFormat is optional, will default to NameTypeValue at runtime
        pv_FileFormat = self.get_parameter_value(parameter_name='FileFormat', command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_FileFormat,
                                                  self.__choices_FileFormat, True, True):
            message = "FileFormat parameter is invalid."
            recommendation = "Specify the FileFormat parameter as blank or one of " + \
                             str(self.__choices_FileFormat)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # SortOrder is optional, will default to None (no sort) at runtime
        pv_SortOrder = self.get_parameter_value(parameter_name='SortOrder', command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_SortOrder,
                                                  self.__choices_SortOrder, True, True):
            message = "SortOrder parameter is invalid."
            recommendation = "Specify the SortOrder parameter as blank or one of " + \
                             str(self.__choices_SortOrder)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception
        if len(warning_message) > 0:
            logger.warning(warning_message)
            raise ValueError(warning_message)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def run_command(self):
        """
        Run the command.  Write the processor properties to a file.

        Returns:
            Nothing.

        Raises:
                RuntimeError: if a runtime input error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Get data for the command
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_OutputFile = self.get_parameter_value('OutputFile')
        pv_IncludeProperties = self.get_parameter_value('IncludeProperties')
        include_properties = []  # Default
        if pv_IncludeProperties is not None and len(pv_IncludeProperties) > 0:
            include_properties = string_util.delimited_string_to_list(pv_IncludeProperties)
        pv_WriteMode = self.get_parameter_value('WriteMode')
        write_mode = pv_WriteMode
        if pv_WriteMode is None or pv_WriteMode == "":
            write_mode = 'Overwrite'  # Default
        pv_FileFormat = self.get_parameter_value('FileFormat')
        file_format = pv_FileFormat
        if pv_FileFormat is None or pv_FileFormat == "":
            file_format = 'NameValueType'  # Default
        pv_SortOrder = self.get_parameter_value('SortOrder')
        sort_order = 0  # no sort
        if pv_SortOrder is not None:
            if pv_SortOrder == 'Ascending':
                sort_order = 1
            elif pv_SortOrder == 'Descending':
                sort_order = -1

        # Runtime checks on input

        pv_OutputFile_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        if warning_count > 0:
            message = "There were " + warning_count + " warnings about command parameters."
            logger.warning(message)
            raise ValueError(message)

        # Write the output file

        try:
            # Get the GeoLayer object
            geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)
            if geolayer is None:
                message = 'Unable to find GeoLayer for GeoLayerID="' + pv_GeoLayerID + '"'
                warning_count += 1
                logger.error(message)
                self.command_status.add_to_log(
                    command_phase_type.RUN,
                    CommandLogRecord(command_status_type.FAILURE, message, "Check the log file for details."))
            else:
                problems = []  # Empty list of properties
                io_util.write_property_file(pv_OutputFile_absolute, geolayer.properties,
                                            include_properties, write_mode, file_format, sort_order, problems)
                # Record any problems that were found
                for problem in problems:
                    warning_count += 1
                    logger.error(problem)
                    self.command_status.add_to_log(
                        command_phase_type.RUN,
                        CommandLogRecord(command_status_type.FAILURE, problem,
                                         "See the log file for details."))

        except Exception as e:
            warning_count += 1
            message = 'Unexpected error writing file "' + pv_OutputFile_absolute + '"'
            traceback.print_exc(file=sys.stdout)
            logger.exception(message, e)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE, message,
                                 "See the log file for details."))

        except:
            warning_count += 1
            message = 'Unexpected error writing file "' + pv_OutputFile_absolute + '"'
            traceback.print_exc(file=sys.stdout)
            logger.exception(message)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE, message,
                                 "See the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            logger.warning(message)
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
