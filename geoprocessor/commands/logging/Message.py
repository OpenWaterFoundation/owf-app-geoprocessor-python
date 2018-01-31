# Message command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.commandUtil as command_util
import geoprocessor.util.validatorsUtil as validators

import logging


class Message(AbstractCommand):
    """
    The Message command prints a message to the log file and optionally sets
    the command status to alert about an issue.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("Message", type("")),
        CommandParameterMetadata("CommandStatus", type(""))
    ]

    def __init__(self):
        """
        Initialize the command instance.
        """
        super(Message, self).__init__()
        self.command_name = "Message"
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
        logger = logging.getLogger("gp")

        # Message is required
        pv_Message = self.get_parameter_value(parameter_name='Message', command_parameters=command_parameters)
        if not validators.validate_string(pv_Message, False, False):
            message = "Message parameter has no value."
            recommendation = "Specify text for the Message parameter."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))
        pv_CommandStatus = self.get_parameter_value(parameter_name='CommandStatus',
                                                    command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_CommandStatus,
                                                  command_status_type.get_command_status_types(), True, True):
            message = 'The requested command status "' + pv_CommandStatus + '"" is invalid.'
            recommendation = "Specify a valid command status."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception
        if len(warning) > 0:
            logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def run_command(self):
        """
        Run the command.  Print the message to the log file.

        Returns:
            Nothing.

        Raises:
            RuntimeError if any exception occurs.
        """
        logger = logging.getLogger(__name__)
        warning_count = 0

        # Message parameter won't be null.
        pv_Message = self.get_parameter_value('Message')
        message_expanded = self.command_processor.expand_parameter_value(pv_Message)
        logger.info(message_expanded)

        if warning_count > 0:
            message = "There were " + warning_count + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
