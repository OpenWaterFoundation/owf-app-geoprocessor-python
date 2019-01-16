# Blank - command for blank lines
# ________________________________________________________________NoticeStart_
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
# ________________________________________________________________NoticeEnd___

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand


class Blank(AbstractCommand):
    """
    A Blank command is used when the command contains only whitespace.
    The command does nothing when run.
    """
    def __init__(self):
        """
        Initialize a new instance of the command.
        """
        # Don't set the command name because don't know that there is one.
        # The AbstractCommand.command_string will be used to output the full string:
        super().__init__()
        # Name of command for menu and window title
        self.command_name = "Blank"
        # Description for menu "Command()... <description>"
        self.command_description = "Used for blank lines"

        # Command metadata for command editor display
        self.command_metadata = {}
        self.command_metadata['Description'] = 'This command is a placeholder for blank lines, which contain only ' \
                                               'whitespace characters (spaces and tabs). '
        self.command_metadata['EditorType'] = 'Generic'

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

        # Set data in the parent class, but do not attempt to parse the command since nothing to parse.
        full_initialization = False
        super(Blank, self).initialize_command(command_string, processor, full_initialization)

    def run_command(self):
        """
        Run the command.  Does nothing.

        Returns:
            Nothing.
        """
        # print("In Blank.run_command")
        pass
