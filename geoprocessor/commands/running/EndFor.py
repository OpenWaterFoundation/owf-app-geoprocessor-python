# EndFor command

import geoprocessor.commands.abstract.AbstractCommand as AbstractCommand
import geoprocessor.core.CommandParameterMetadata as CommandParameterMetadata

# Inherit from AbstractCommand
class EndFor(AbstractCommand.AbstractCommand):
    def __init__(self):
        super(EndFor, self).__init__()
        self.command_name = "EndFor"
        self.command_parameter_metadata = [
            CommandParameterMetadata.CommandParameterMetadata("Name",type(""),None)
        ]

    def check_command_parameters(self, command_parameters):
        '''Check the command parameters for validity.'''
        print('In EndFor.check_command_parameters - need to complete.' )

    def get_name(self):
        '''Return the name of the EndIf (will match name of corresponding If)'''
        return self.command_parameters.get("Name", None)

    def run_command(self):
        print("In EndFor.run_command")
