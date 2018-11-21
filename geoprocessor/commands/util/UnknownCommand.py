import geoprocessor.commands.abstract.AbstractCommand as AbstractCommand


class UnknownCommand(AbstractCommand.AbstractCommand):
    """
    General command class used when the GeoProcessorCommandFactory does not recognize the command.
    This allows the command to exist gracefully in a command file and command list.
    Running the command has no effect.
    """
    def __init__(self):
        """
        Initialize a new instance of the command.
        """
        # Don't set the command name because don't know that there is one.
        # The AbstractCommand.command_string will be used to output the full string:
        super().__init__()

    def initialize_command(self, command_string, processor, full_initialization):
        """
        Initialize the command.  This overrides the AbstractCommand.initialize_command function
        because an UnknownCommand may be ill-formed and no attempt is made to parse it.

        Args:
            command_string: Full command string, which may include indentation.
            processor: The GeoProcessor instance, which the command will use to interact with the processor.
            full_initialization: Ignored.  A value of False is passed to AbstractCommand.initialize_command().

        Returns:
            Nothing.
        """

        # Set data in the parent class, but do not attempt to parse the command since unknown syntax
        full_initialization = False
        super(UnknownCommand, self).initialize_command(command_string, processor, full_initialization)

    def run_command(self):
        """
        Run the command.  Does nothing since an unknown command.

        Returns:
            Nothing.
        """
        # print("In UnknownCommand.run_command")
        pass
