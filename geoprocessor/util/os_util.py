# os_util - useful utility functions for the operating system
# ________________________________________________________________NoticeStart_
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
# ________________________________________________________________NoticeEnd___

"""
Functions related to the operating system.
"""

import os
import platform


def get_os_distro():
    """
    Determine the operating system distribution, useful for showing system information
    but not advised for checks (use the is_*_os() functions to control program logic).

    Returns:
        (str) operating system distribution as "Cygwin", "MinGW", "Debian" (Linux), "Windows 10" for Windows 10,
        or None if unknown.
    """
    os_type_distro = None
    if is_cygwin_os():
        os_type_distro = "Cygwin"
    elif is_mingw_os():
        os_type_distro = "MinGW"
    elif is_windows_os():
        # Use the platform version
        os_type_distro = platform.uname()[2]
    return os_type_distro


def get_os_type():
    """
    Determine the major operating system type, useful for showing system information
    but not advised for checks (use the is_*_os() functions to control program logic).

    Returns:
        (str) operating system type as "Linux" or "Windows", or None if unknown.
    """
    os_type = None
    if is_linux_os():
        os_type = "Linux"
    elif is_windows_os():
        os_type = "Windows"
    return os_type


def is_cygwin_os():
    """
    Indicate whether the operating system is Cygwin.
    Cygwin is a Linux OS but someones Cygwin-specific logic must be implemented.

    Returns:  True if Cygwin operating system, False if not.
    """
    if platform.uname()[0].upper().find('CYGWIN') >= 0:
        return True
    else:
        return False


def is_linux_os():
    """
    Indicate whether the operating system is Linux.

    Returns:  True if Linux operating system, False if not.
    """
    if os.name.upper() == 'POSIX':
        return True
    else:
        return False


def is_mingw_os():
    """
    Indicate whether the operating system is MinGW, such as used with Git Bash.
    MinGW is a Linux OS but someones MinGW-specific logic must be implemented.

    Returns:  True if MinGW operating system, False if not.
    """
    if platform.uname()[0].upper().find('MINGW') >= 0:
        return True
    else:
        return False


def is_windows_os():
    """
    Indicate whether the operating system is Windows.

    Returns:  True if Windows operating system, False if not.
    """
    if os.name.upper() == 'NT':
        return True
    else:
        return False
