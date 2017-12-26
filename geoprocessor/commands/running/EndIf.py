# EndIf command

import geoprocessor.commands.abstract.AbstractCommand as AbstractCommand
import geoprocessor.core.CommandParameterMetadata as CommandParameterMetadata

# Inherit from AbstractCommand
class EndIf(AbstractCommand.AbstractCommand):
    def __init__(self):
        super(EndIf, self).__init__()
        self.command_name = "EndIf"
        self.command_parameter_metadata = [
            CommandParameterMetadata.CommandParameterMetadata("Message",type(""),None),
            CommandParameterMetadata.CommandParameterMetadata("CommandStatus",type(""),None)
        ]

    def check_command_parameters(self, command_parameters):
        '''Check the command parameters for validity.'''
        print('In EndIf.check_command_parameters - need to complete.' )

    def get_name(self):
        '''Return the name of the EndIf (will match name of corresponding If)'''
        return self.command_parameters.get("Name", None)

    def run_command(self):
        print("In EndIf.run_command")
