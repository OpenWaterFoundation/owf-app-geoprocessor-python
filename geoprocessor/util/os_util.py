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
