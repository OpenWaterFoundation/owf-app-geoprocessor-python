# UnknownCommand - command to use for unknown commands
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2023 Open Water Foundation
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

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = "Unknown command - running this command will result in a warning.\n" \
        "Edits to the command will not be checked."
    __command_metadata['EditorType'] = "Generic"
    __command_metadata['EditorTitle'] = 'Edit unknown command'  # Does not follow normal CommandName(...).

    def __init__(self) -> None:
        """
        Initialize a new instance of the command.
        """
        # Don't set the command name because don't know that there is one.
        # The AbstractCommand.command_string will be used to output the full string:
        super().__init__()

        self.command_name = "UnknownCommand"

        # Command metadata for command editor display.
        self.command_metadata = self.__command_metadata

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

        # Set data in the parent class, but do not attempt to parse the command since unknown syntax.
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

    def to_string(self, command_parameters: dict = None, format_all: bool = False) -> str:
        """
        Return the original command string.
        """
        return self.command_string
