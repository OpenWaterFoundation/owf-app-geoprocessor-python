# Message - command to output a message
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
import geoprocessor.util.validator_util as validators

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
        super().__init__()
        self.command_name = "Message"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = (
            "Print a message to the log file and optionally set the command status for notification.\n"
            "For example, use with an If command to notify when a condition is met.")
        self.command_metadata['EditorType'] = "Simple"

        # Parameter Metadata
        self.parameter_input_metadata = dict()
        # Message
        self.parameter_input_metadata['Message.Description'] = "message to print"
        self.parameter_input_metadata['Message.Label'] = "Message"
        self.parameter_input_metadata['Message.Tooltip'] = "The message to print. Can be specified using ${Property}."
        self.parameter_input_metadata['Message.Required'] = True
        # CommandStatus
        self.parameter_input_metadata['CommandStatus.Description'] = "status that should result from command"
        self.parameter_input_metadata['CommandStatus.Label'] = "Command status"
        self.parameter_input_metadata['CommandStatus.Tooltip'] = \
            "Indicate the status that should result from running the command: SUCCESS, WARNING, FAILURE."
        self.parameter_input_metadata['CommandStatus.Values'] = [ "", "SUCCESS", "WARNING", "FAILURE" ]
        self.parameter_input_metadata['CommandStatus.Value.Default'] = "SUCCESS"

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
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
        pv_CommandStatus = self.get_parameter_value(parameter_name='CommandStatus',
                                                    command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_CommandStatus,
                                                  CommandStatusType.get_command_status_types_as_str(), True, True):
            message = 'The requested command status "' + pv_CommandStatus + '"" is invalid.'
            recommendation = "Specify a valid command status."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception
        if len(warning) > 0:
            logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

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
        pv_CommandStatus = self.get_parameter_value('CommandStatus')
        if pv_CommandStatus is None or pv_CommandStatus == "":
            # Default status as a string
            pv_commandStatus = str(CommandStatusType.SUCCESS)
        # Convert the string to the enum
        command_status_type = CommandStatusType.value_of(pv_CommandStatus, ignore_case=True)
        message_expanded = self.command_processor.expand_parameter_value(pv_Message)
        logger.info(message_expanded)

        # Add a log message for the requested status type
        # - don't add to the warning count
        self.command_status.add_to_log(
            CommandPhaseType.RUN,
            CommandLogRecord(command_status_type, message_expanded, ""))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
