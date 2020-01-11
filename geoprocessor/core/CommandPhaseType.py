# CommandPhaseType - command phase types
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

from enum import Enum


class CommandPhaseType(Enum):
    """
    Enumeration for command phase type.

    String representation is uppercase because it is mainly used internally:

    INITIALIZATION:  Creation and initialization of the command.
    DISCOVERY:  Run the command in discovery mode.
    RUN:  Run the command completely.

    Numerical values are ordered in logical order of command phases.
    """
    INITIALIZATION = 1
    DISCOVERY = 2
    RUN = 3

    @classmethod
    def get_command_phase_types(cls, sort=False):
        """
        Return the list of valid command phases.

        Args:
            sort:  If True, sort alphabetically.  If False, return in order of execution (default).

        Returns:
            The list of phase types, for example for use in command parameter choice.

        """
        if sort:
            # Sort alphabetically
            return [CommandPhaseType.DISCOVERY, CommandPhaseType.INITIALIZATION, CommandPhaseType.RUN]
        else:
            # Return in order of processing order.
            return [CommandPhaseType.INITIALIZATION, CommandPhaseType.DISCOVERY, CommandPhaseType.RUN]

    def __str__(self):
        """
        Format the enumeration value as a string - just return the name.

        Returns:

        """
        return self.name
