# SetProperty command

import geoprocessor.commands.abstract.AbstractCommand as AbstractCommand
import geoprocessor.core.CommandParameterMetadata as CommandParameterMetadata

# Inherit from AbstractCommand
class SetProperty(AbstractCommand.AbstractCommand):
    def __init__(self):
        super(SetProperty, self).__init__()
        self.command_name = "SetProperty"
        self.command_parameter_metadata = [
            CommandParameterMetadata.CommandParameterMetadata("Message",type(""),None),
            CommandParameterMetadata.CommandParameterMetadata("CommandStatus",type(""),None)
        ]

    def check_command_parameters(self, command_parameters):
        '''Check the command parameters for validity.'''
        print('In SetProperty.check_command_parameters - need to complete.' )

    def run_command(self):
        print("In SetProperty.run_command")
        # Hardcode functionality to illustrate
        self.command_processor.set_property("Property1","Test property")