# If command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validators

class If(AbstractCommand):
    """
    The If command starts an If block.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("Name", type("")),
        CommandParameterMetadata("Condition", type("")),
        CommandParameterMetadata("CompareAsStrings", type(True))
    ]

    def __init__(self):
        """
        Initialize the command instance.
        """
        super(If, self).__init__()
        # AbstractCommand data
        self.command_name = "If"
        self.command_parameter_metadata = self.__command_parameter_metadata
        # Local data
        self.condition_eval = True

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
