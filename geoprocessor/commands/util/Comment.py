import geoprocessor.commands.abstract.AbstractCommand as AbstractCommand

import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type


class Comment(AbstractCommand.AbstractCommand):
    """
    # comment.
    """
    def __init__(self):
        """
        Initialize a new instance of the command.
        """
        # Don't set the command name because there is not one.
        # The AbstractCommand.command_string will be used to output the full string:
        super(Comment, self).__init__()
        # Set the command status to success so that testing reports look better
        self.command_status.initialization_status = command_status_type.SUCCESS
        self.command_status.discovery_status = command_status_type.SUCCESS
        self.command_status.run_status = command_status_type.SUCCESS

    def initialize_command(self, command_string, processor, full_initialization):
        """
        Initialize the command.  This overrides the AbstractCommand.initialize_command function
        because a comment is treated as simple text.

        Args:
            command_string: Full command string, which may include indentation.
            processor: The GeoProcessor instance, which the command will use to interact with the processor.
            full_initialization: Ignored.  A value of False is passed to AbstractCommand.initialize_command().

        Returns:
            None.
        """

        # Set data in the parent class, but do not attempt to parse the command since unknown syntax
        full_initialization = False
        super(Comment, self).initialize_command(command_string, processor, full_initialization)

    def run_command(self):
        """
        Run the command.  Does nothing since comments cause no action.

        Returns:
            None.
        """
        self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
