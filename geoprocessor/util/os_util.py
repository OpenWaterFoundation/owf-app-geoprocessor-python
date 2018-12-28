# os_util - useful utility functions for the operating system
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
Functions related to the operating system.
"""

import os


def is_windows_os():
    """
    Indicate whether the operating system is Windows.

    Returns:  True if Windows, False if not.
    """
    if os.name.upper() == 'NT':
        return True
    else:
        return False


def is_linux_os():
    """
    Indicate whether the operating system is Linux.

    Returns:  True if Linux, False if not.
    """
    if os.name.upper() == 'POSIX':
        return True
    else:
        return False
