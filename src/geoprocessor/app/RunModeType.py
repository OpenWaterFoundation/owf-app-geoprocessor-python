# RunMode - run modes for the GeoProcessor application
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

# The following is needed to allow type hinting -> GeoProcessorAppSession, and requires Python 3.7+.
# See:  https://stackoverflow.com/questions/33533148/
#         how-do-i-specify-that-the-return-type-of-a-method-is-the-same-as-the-class-itsel
from __future__ import annotations

from enum import Enum


class RunModeType(Enum):
    """
    Enumeration for GeoProcessor application run type.

    String representation is uppercase because it is mainly used internally:

    BATCH:  Run in batch mode.
    HTTP:   Run the command in discovery mode.
    SHELL:  Run the GeoProcessor command prompt shell.
    UI:     Run the interactive user interface.

    Numerical values are ordered in alphabetical order.
    """
    BATCH = 1
    HTTP = 2
    SHELL = 3
    UI = 4

    @classmethod
    def get_run_modes(cls) -> [RunModeType]:
        """
        Return the list of valid run modes.

        Returns:
            The list of run modes;
        """
        # Return in order of processing order.
        return [RunModeType.BATCH, RunModeType.HTTP, RunModeType.SHELL, RunModeType.UI]

    def __str__(self) -> str:
        """
        Format the enumeration value as a string - just return the name.

        Returns:

        """
        return self.name
