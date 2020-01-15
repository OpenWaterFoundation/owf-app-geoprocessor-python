# UnknownCommand - command to use for unknown commands
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2020 Open Water Foundation
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


class UnknownCommand(AbstractCommand):
    """
    General command class used when the GeoProcessorCommandFactory does not recognize the command.
    This allows the command to exist gracefully in a command file and command list.
    Running the command has no effect.
    """
    def __init__(self) -> None:
        """
        Initialize a new instance of the command.
        """
        self.command_name = "UnknownCommand"
        self.command_description = "Used when the command is not recognized"
        # Don't set the command name because don't know that there is one.
        # The AbstractCommand.command_string will be used to output the full string:
        super().__init__()

    def initialize_command(self, command_string: str, processor, full_initialization: bool) -> None:
        """
        Initialize the command.  This overrides the AbstractCommand.initialize_command function
        because an UnknownCommand may be ill-formed and no attempt is made to parse it.

        Args:
            command_string: Full command string, which may include indentation.
            processor: The GeoProcessor instance, which the command will use to interact with the processor.
            full_initialization: Ignored.  A value of False is passed to AbstractCommand.initialize_command().

        Returns:
            None
        """

        # Set data in the parent class, but do not attempt to parse the command since unknown syntax
        full_initialization = False
        super(UnknownCommand, self).initialize_command(command_string, processor, full_initialization)

    def run_command(self) -> None:
        """
        Run the command.  Does nothing since an unknown command.

        Returns:
            None
        """
        # print("In UnknownCommand.run_command")
        pass
