# command_phase_types - command phase types
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

"""
Possible values of command phase.
When the code migrates to Python 3 this can be replaced with an Enum named CommandPhaseType.

INITIALIZATION:  Creation and initialization of the command.
DISCOVERY:  Run the command in discovery mode.
RUN:  Run the command completely.
"""

INITIALIZATION = 'INITIALIZATION'
DISCOVERY = 'DISCOVERY'
RUN = 'RUN'


def get_command_status_types(sort=False):
    """
    Return the list of valid command phases.

    Args:
        sort:  If True, sort alphabetically.  If False, return in order of execution (default).

    Returns:
        The list of phase types, for example for use in command parameter choice.

    """
    if sort:
        # Sort alphabetically
        return [DISCOVERY, INITIALIZATION, RUN]
    else:
        # Return in order of processing order.
        return [INITIALIZATION, DISCOVERY, RUN]
