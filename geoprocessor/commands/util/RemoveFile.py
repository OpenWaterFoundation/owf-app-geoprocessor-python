# RemoveFile command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.io as io_util
import geoprocessor.util.validators as validators

import logging
import os
import sys
import traceback


class RemoveFile(AbstractCommand):
    """
    The RemoveFile command removes a file from the computer.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("SourceFile", type("")),
        CommandParameterMetadata("IfSourceFileNotFound", type(""))
    ]

    # Choices for IfNotFound, used to validate parameter and display in editor
    __choices_IfSourceFileNotFound = ["Ignore", "Warn", "Fail"]

    def __init__(self):
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data
        super(RemoveFile, self).__init__()
        self.command_name = "RemoveFile"
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

        # SourceFile is required
        pv_SourceFile = self.get_parameter_value(parameter_name='SourceFile', command_parameters=command_parameters)
        if not validators.validate_string(pv_SourceFile, False, False):
            message = "The SourceFile must be specified."
            recommendation = "Specify the source file."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # IfSourceFileNotFound is optional, will default to Warn at runtime
        pv_IfSourceFileNotFound = self.get_parameter_value(parameter_name='IfSourceFileNotFound',
                                                           command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_IfSourceFileNotFound,
                                                  self.__choices_IfSourceFileNotFound, True, True):
            message = "IfSourceFileNotFound parameter is invalid."
            recommendation = "Specify the IfSourceFileNotFound parameter as blank or one of " + \
                             str(self.__choices_IfSourceFileNotFound)
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
        Run the command.
        Remove the specified file from the operating system.

        Returns:
            Nothing.

        Raises:
                RuntimeError: if a runtime input error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Get data for the command
        pv_SourceFile = self.get_parameter_value('SourceFile')

        # Runtime checks on input

        pv_SourceFile_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_SourceFile, self)))

        if warning_count > 0:
            message = "There were " + warning_count + " warnings about command parameters."
            logger.warning(message)
            raise ValueError(message)

        # Remove the file

        try:
            input_count = 1
            if not os.path.exists(pv_SourceFile_absolute):
                warning_count += 1
                message = 'The source file does not exist: "' + pv_SourceFile_absolute + '"'
                self.command_status.add_to_log(
                    command_phase_type.RUN,
                    CommandLogRecord(command_status_type.FAILURE, message,
                                     "Verify that the source exists at the time the command is run."))
                logger.warning(message)
                input_count -= 1

            if input_count == 1:
                logger.info('Removing file "' + pv_SourceFile_absolute + '"')
                os.remove(pv_SourceFile_absolute)

        except Exception as e:
            warning_count += 1
            message = 'Unexpected error removing file "' + pv_SourceFile_absolute + '"'
            traceback.print_exc(file=sys.stdout)
            logger.exception(message, e)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE, message,
                                 "See the log file for details."))

        if warning_count > 0:
            message = "There were " + warning_count + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
