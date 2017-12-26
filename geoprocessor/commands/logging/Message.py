# Message command

import geoprocessor.commands.abstract.AbstractCommand as AbstractCommand
import geoprocessor.commands.abstract.command_phase_type as command_phase_type
import geoprocessor.commands.abstract.command_status_type as command_status_type
import geoprocessor.commands.abstract.CommandLogRecord as CommandLogRecord
import geoprocessor.core.CommandParameterMetadata as CommandParameterMetadata
import geoprocessor.util.command as util_command
import geoprocessor.util.validators as validators

# Inherit from AbstractCommand
class Message(AbstractCommand.AbstractCommand):
    def __init__(self):
        super(Message, self).__init__()
        self.command_name = "Message"
        self.command_parameter_metadata = [
            CommandParameterMetadata.CommandParameterMetadata("Message",type(""),None),
            CommandParameterMetadata.CommandParameterMetadata("CommandStatus",type(""),None)
        ]

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
        # TODO smalers 2017-12-25 need to log the warnings
        if not validators.validate_string(self.get_parameter_value('Message'),False,False):
            message = "Message parameter has no value.  Specify a non-empty string."
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                CommandLogRecord.CommandLogRecord(command_status_type.FAILURE, message, "Specify text for the Message parameter."))
            print(message)
        pv_CommandStatus = self.get_parameter_value('CommandStatus')
        if not validators.validate_string_in_list(pv_CommandStatus,command_status_type.get_command_status_types(),True,True):
            message = 'The requested command status "' + pv_CommandStatus + '"" is invalid.'
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                CommandLogRecord.CommandLogRecord(command_status_type.FAILURE, message, "Specify a valid command status."))
            print(message)

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = util_command.validate_command_parameter_names ( self, warning )

        # If any warnings were generated, throw an exception
        if len(warning) > 0:
            #Message.printWarning ( warning_level,
            #    MessageUtil.formatMessageTag(command_tag, warning_level), routine, warning );
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION,command_status_type.SUCCESS)

    def run_command(self):
        """
        Run the command.  Print the message to the log file.

        Returns:
            Nothing.

        """
        print("In Message.run_command")
        # Message won't be null.
        pv_Message = self.get_parameter_value('Message')
        message_expanded = self.command_processor.expand_parameter_value(pv_Message)
        print(pv_Message)