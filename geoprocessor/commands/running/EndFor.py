# EndFor - command to end a For block
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


class EndFor(AbstractCommand):
    """
    The EndFor command indicates the end of a For block.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("Name", type(""))
    ]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = (
        "This command ends a block of commands that start with a For command.\n"
        "The For and EndFor commands must have the same value for the Name "
        "parameter to allow the processor to determine the start and end of the block.")
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # Name
    __parameter_input_metadata['Name.Description'] = "the name that will be matched with name of a For command"
    __parameter_input_metadata['Name.Label'] = "Name"
    __parameter_input_metadata['Name.Required'] = True
    __parameter_input_metadata['Name.Tooltip'] = \
        "The name that will be matched with the name of a For command to indicate the block of commands in the loop."

    def __init__(self) -> None:
        """
        Initialize the command instance.
        """
        super().__init__()
        self.command_name: str = "EndFor"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata
        self.parameter_input_metadata = self.__parameter_input_metadata

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

        # Name is required
        # noinspection PyPep8Naming
        pv_Name = self.get_parameter_value(parameter_name='Name', command_parameters=command_parameters)
        if not validator_util.validate_string(pv_Name, False, False):
            message = "A name for the EndFor block must be specified"
            recommendation = "Specify the Name."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

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

    def get_name(self) -> str:
        """
        Return the name of the EndIf (will match name of corresponding If).

        Returns:
            The name of the EndIf (will match name of corresponding If).
        """
        return self.get_parameter_value("Name")

    def run_command(self) -> None:
        """
        Run the command.  Does not do anything since the command is just a place-holder to match For().

        Returns:
            None
        """
        pass
