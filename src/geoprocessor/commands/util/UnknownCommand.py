import geoprocessor.commands.abstract.AbstractCommand as AbstractCommand

# Inherit from AbstractCommand
class UnknownCommand(AbstractCommand.AbstractCommand):
    def __init__(self):
        # Don't set the command name because don't know that there is one.
        # The AbstractCommand.command_string will be used to output the full string
        pass

    def initialize_command(self, command_string, processor, full_initialization):
        '''Intialize an UnknownCommand.'''

        # Handle here instead of the abstract class because it does not have a command name
        # - parse_command is not called
        self.command_string = command_string

    def run_command(self):
        print("In UnknownCommand.run_command")
