import geoprocessor.commands.abstract.AbstractCommand as AbstractCommand


class BlankCommand(AbstractCommand.AbstractCommand):
    """
    A BlankCommand is used when the command contains only whitespace.
    The command does nothing when run.
    """
    def __init__(self):
        """
        Initialize a new instance of the command.
        """
        # Don't set the command name because don't know that there is one.
        # The AbstractCommand.command_string will be used to output the full string:
        super(BlankCommand, self).__init__()

    def initialize_command(self, command_string, processor, full_initialization):
        """
        Initialize the command.  This overrides the AbstractCommand.initialize_command function
        because there are no command parameters to parse.

        Args:
            command_string: Full command string, which may include indentation.
            processor: The GeoProcessor instance, which the command will use to interact with the processor.
            full_initialization: Ignored.  A value of False is passed to AbstractCommand.initialize_command().

        Returns:
            Nothing.
        """

        # Set data in the parent class, but do not attempt to parse the command since unknown syntax
        full_initialization = False
        super(BlankCommand, self).initialize_command(command_string, processor, full_initialization)

    def run_command(self):
        """
        Run the command.  Does nothing since an unknown command.

        Returns:
            Nothing.
        """
        # print("In BlankCommand.run_command")
        pass
