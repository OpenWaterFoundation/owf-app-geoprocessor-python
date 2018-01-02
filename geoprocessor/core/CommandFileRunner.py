from geoprocessor.core.GeoProcessor import GeoProcessor


class CommandFileRunner(object):
    """
    Utility class to run a command file by specifying the command file name.
    This class is useful to run the geoprocessor in batch mode.

    This is a port of the Java TSCommandFileRunner class.
    """

    def __init__(self):
        """
        Constructor for CommandFileRunner instance.
        This class is typically used for single-pass runs such as running a command file in batch mode.
        Once a runner is created, a command file can be run by calling the following functions,
        each of which provide parameters to control processing.
        The GeoProcessor instance is only created once and is reused.

        read_command_file()
        run_commands()

        """
        self.command_processor = GeoProcessor()

    def get_processor(self):
        return self.command_processor

    def is_command_file_enabled(self):
        """
        Determine whether the command file is enabled.
        This is used in the RunCommands() command to determine if a command file is enabled.

        Returns:
            True if the command file is enabled, and False if not (comments with #@enabled False).
        """
        commands = self.command_processor.commands
        for command in commands:
            command_string = command.to_string().upper_case()
            pos = command_string.find("@ENABLED")
            if pos >= 0:
                # Message.printStatus(2, "", "Detected tag: " + C)
                # Check the token following @ enabled
                if command_string.length() > (pos + 8):
                    # Have trailing characters
                    parts = command_string[pos:].split(" ")
                    if len(parts) > 1:
                        if parts[1].trim().equals("FALSE"):
                            # Message.printStatus(2, "", "Detected false")
                            return False
        # No #@enabled False found so command file is enabled
        return True

    def read_command_file(self, command_file_path, run_discovery_on_load=True):
        """
        Read the commands from a file.

        Args:
            command_file_path (str):  name of the command file to run, should be absolute path.
            run_discovery_on_load (bool):  indicates whether to run discovery mode on commands when loading
                (this can be a noticable performance hit for large command files and therefore for
                large batch runs setting to False can result in faster processing and in some cases
                avoid out of memory issues)

        Returns:
            Nothing.

        Raises:
            FileNotFoundError:  If the command file is not found.
        """
        self.command_processor.read_command_file(
            command_file_path,  # InitialWorkingDir processor property will be set to command file location
            True,  # Create UnknownCommand instances for unknown commands
            False,  # Do not append the commands to the commands already in the processor.
            run_discovery_on_load)

    def run_commands(self, run_properties=None):
        """
        Run the commands that have been previously read from the command file.

        Args:
            run_properties:  properties to pass to the processor.

        Returns:
            Nothing.

        Raises:
            RuntimeError:  If there is an error running the commands.
        """
        self.command_processor.run_commands(
            None,  # Subset of Command instances to run - just run all commands
            run_properties)  # Properties to control run