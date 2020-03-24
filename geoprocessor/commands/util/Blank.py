# Blank - command for blank lines
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


class Blank(AbstractCommand):
    """
    A Blank command is used when the command contains only whitespace.
    The command does nothing when run.
    """

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = 'This command is a placeholder for an empty line in a command file.\n' \
                                        'The command does not serve a purpose other than to store the empty line.\n' \
                                        'See also # comment command.'
    __command_metadata['EditorType'] = 'InsertLineEditor'
    __command_metadata['EditorTitle'] = 'Edit empty line'  # Title does not follow normal CommandName(...)

    def __init__(self) -> None:
        """
        Initialize a new instance of the command.
        """
        # Don't set the command name because don't know that there is one.
        # The AbstractCommand.command_string will be used to output the full string:
        super().__init__()
        self.command_name = "Blank"

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

    def initialize_command(self, command_string: str, processor, full_initialization: bool) -> None:
        """
        Initialize the command.  This overrides the AbstractCommand.initialize_command function
        because there are no command parameters to parse.

        Args:
            command_string: Full command string, which may include indentation.
            processor: The GeoProcessor instance, which the command will use to interact with the processor.
            full_initialization: Ignored.  A value of False is passed to AbstractCommand.initialize_command().

        Returns:
            None
        """

        # Set data in the parent class, but do not attempt to parse the command since nothing to parse.
        full_initialization = False
        super(Blank, self).initialize_command(command_string, processor, full_initialization)

    def run_command(self) -> None:
        """
        Run the command.  Does nothing.

        Returns:
            None
        """
        # print("In Blank.run_command")
        pass

    def to_string(self, command_parameters: dict = None, format_all: bool = False) -> str:
        """
        Return the string representation of the command, always an empty string.

        Returns:
            The string representation of the command, always an empty string.
        """
        return ''
