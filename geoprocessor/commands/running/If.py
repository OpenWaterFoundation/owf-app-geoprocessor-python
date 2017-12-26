# If command

import geoprocessor.commands.abstract.AbstractCommand as AbstractCommand
import geoprocessor.core.CommandParameterMetadata as CommandParameterMetadata

# Inherit from AbstractCommand
class If(AbstractCommand.AbstractCommand):
    def __init__(self):
        super(If, self).__init__()
        self.condition_eval = True
        self.command_name = "If"
        self.command_parameter_metadata = [
            CommandParameterMetadata.CommandParameterMetadata("Name",type(""),None),
            CommandParameterMetadata.CommandParameterMetadata("Condition",type(""),None),
            CommandParameterMetadata.CommandParameterMetadata("CompareAsStrings",type(True),None)
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