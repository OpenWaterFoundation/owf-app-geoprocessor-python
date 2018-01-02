# EndFor command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.validators as validators


# Inherit from AbstractCommand
class EndFor(AbstractCommand):
    def __init__(self):
        super(EndFor, self).__init__()
        self.command_name = "EndFor"
        self.command_parameter_metadata = [
            CommandParameterMetadata("Name", type(""))
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
        # TODO smalers 2017-12-25 need to log
        pv_Name = self.get_parameter_value(parameter_name='Name', command_parameters=command_parameters)
        if not validators.validate_string(pv_Name, False, False):
            message = "A name for the EndFor block must be specified"
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify the Name."))

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

    def get_name(self):
        """
        Return the name of the EndIf (will match name of corresponding If).

        Returns:
            The name of the EndIf (will match name of corresponding If).
        """
        return self.get_parameter_value("Name")

    def run_command(self):
        print("In EndFor.run_command")
