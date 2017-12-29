# If command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.validators as validators

# Inherit from AbstractCommand
class If(AbstractCommand):
    def __init__(self):
        super(If, self).__init__()
        self.condition_eval = True
        self.command_name = "If"
        self.command_parameter_metadata = [
            CommandParameterMetadata("Name",type(""),None),
            CommandParameterMetadata("Condition",type(""),None),
            CommandParameterMetadata("CompareAsStrings",type(True),None)
        ]

    def check_command_parameters(self, command_parameters):
        '''Check the command parameters for validity.'''
        print('In If.check_command_parameters - need to complete.' )

    def get_condition_eval(self):
        '''Return the result of evaluating the condition,
        which is set when run_command() is called'''
        return self.condition_eval

    def get_name(self):
        '''Return the name of the EndIf (will match name of corresponding If)'''
        return self.command_parameters.get("Name", None)

    def run_command(self):
        print("In If.run_command")
        # Test always is true
        self.condition_eval = True