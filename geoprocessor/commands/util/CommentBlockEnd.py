# */ - command for comment block end
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

from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType


class CommentBlockEnd(AbstractCommand):
    """
    */ comment block end.
    """
    def __init__(self):
        """
        Initialize a new instance of the command.
        """
        # The AbstractCommand.command_string will be used to output the full string:
        super().__init__()
        # Set the command status to success so that testing reports look better
        self.command_status.initialization_status = CommandStatusType.SUCCESS
        self.command_status.discovery_status = CommandStatusType.SUCCESS
        self.command_status.run_status = CommandStatusType.SUCCESS

        self.command_name = "*/"

        # Command metadata for command editor display
        self.command_metadata = {}
        self.command_metadata['Description'] = ('Multiple-line comments end with */. Spaces and tabs at the start '
                                                'of the comment line are OK. Additional text before the comment '
                                                'indicator is allowed.')
        self.command_metadata['EditorType'] = 'InsertLineEditor'

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
        super(CommentBlockEnd, self).initialize_command(command_string, processor, full_initialization)

    def run_command(self):
        """
        Run the command.  Does nothing since comments cause no action.
        The command type is examined in the processor to know when a comment block is ending.

        Returns:
            None.
        """
        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
