# StartLog command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.io as io_util
import geoprocessor.util.log as log_util
import geoprocessor.util.validators as validators

import logging


class StartLog(AbstractCommand):
    """
    The StartLog command (re)starts the log file.
    This is useful to ensure that a local log file is created with the command file.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("LogFile", type(""))
    ]

    def __init__(self):
        """
        Initialize the command instance.
        """
        super(StartLog, self).__init__()
        self.command_name = "StartLog"
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
        warning = ""
        pv_LogFile = self.get_parameter_value(parameter_name='LogFile', command_parameters=command_parameters)
        if not validators.validate_string(pv_LogFile, False, False):
            message = "LogFile parameter has no value."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify the log file."))
            print(message)

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception
        if len(warning) > 0:
            # Message.printWarning ( warning_level,
            #    MessageUtil.formatMessageTag(command_tag, warning_level), routine, warning );
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def run_command(self):
        """
        Run the command.  Print the message to the log file.

        Returns:
            Nothing.
        """
        logger = logging.getLogger(__name__)
        warning_count = 0

        pv_LogFile = self.get_parameter_value('LogFile')
        log_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(
                self.command_processor.get_property('WorkingDir'),
                self.command_processor.expand_parameter_value(pv_LogFile)))

        try:
            # Change the GeoProcesssor logger to use the specified file
            # - The initial application log file will be closed.
            log_util.reset_log_file_handler(log_file_absolute)
        except Exception as e:
            warning_count += 1
            message = 'Unexpected error (re)starting log file "' + log_file_absolute + '"'
            logger.exception(message, e)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE, message,
                                 "Check the old log file or command window for details."))

        if warning_count > 0:
            message = "There were " + warning_count + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
