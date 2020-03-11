# Exit - command to end an If block
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

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validator_util

import logging


class Exit(AbstractCommand):
    """
    The Exit command ends processing.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
    ]

    def __init__(self) -> None:
        """
        Initialize the command instance.
        """
        super().__init__()
        self.command_name: str = "Exit"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = (
            "This command stops command processing, which is useful when troubleshooting.  "
            "See also the /* */ commands, which can be used to comment a block of commands.")
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()

    def check_command_parameters(self, command_parameters: dict) -> None:
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            None

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning = ""
        logger = logging.getLogger(__name__)

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception
        if len(warning) > 0:
            logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def run_command(self) -> None:
        """
        Run the command.  Does not do anything since the command is just a place-holder that is handled in
        the processor.

        Returns:
            None
        """
        pass
