# CommandFileRunner - class to run a command file
#_________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2019 Open Water Foundation
# 
# GeoProcessor is free software:  you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     GeoProcessor is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with GeoProcessor.  If not, see <https://www.gnu.org/licenses/>.
#_________________________________________________________________NoticeEnd___

from geoprocessor.core.GeoProcessor import GeoProcessor

import logging


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
        Loop through the commands and look for @enabled False (ignore case)

        Returns:
            True if the command file is enabled, and False if not (comments with #@enabled False).
        """
        commands = self.command_processor.commands
        for command in commands:
            command_string = command.command_string.upper()
            pos = command_string.find("@ENABLED")
            if pos >= 0:
                # Message.printStatus(2, "", "Detected tag: " + C)
                # Check the token following @ enabled
                if len(command_string) > (pos + 8):
                    # Have trailing characters
                    value = command_string[pos + len("@ENABLED"):].strip()
                    if value.upper() == "FALSE":
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
            None.

        Raises:
            FileNotFoundError:  If the command file is not found.
        """
        self.command_processor.read_command_file(
            command_file_path,  # InitialWorkingDir processor property will be set to command file location
            True,  # Create UnknownCommand instances for unknown commands
            False,  # Do not append the commands to the commands already in the processor.
            run_discovery_on_load)

    def run_commands(self, run_properties=None, env_properties=None):
        """
        Run the commands that have been previously read from the command file.

        Args:
            run_properties (dict):  properties to pass to the processor, to control running.
            env_properties (dict):  properties to pass to the processor, from the environment.

        Returns:
            None.

        Raises:
            RuntimeError:  If there is an error running the commands.
        """
        logger = logging.getLogger(__name__)
        logger.info("Before calling run_commands")
        self.command_processor.run_commands(
            None,  # Subset of Command instances to run - just run all commands
            run_properties=run_properties,  # Properties to control run
            env_properties=env_properties)  # Properties from the environment
        logger.info("Back from calling run_commands")
