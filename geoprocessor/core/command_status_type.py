"""
Possible values of command status.
When the code migrates to Python 3 this can be replaced with an Enum named CommandStatusType.
"""

UNKNOWN = 'UNKNOWN'
INFO = 'INFO'
SUCCESS = 'SUCCESS'
WARNING = 'WARNING'
FAILURE = 'FAILURE'

__status_list = [ INFO, SUCCESS, WARNING, FAILURE ]

def get_command_status_types(sort=False):
    """
    Return the list of valid command status.

    Args:
        sort:  If True, sort alphabetically.  If False, return in order of severity (default).

    Returns:
        The list of status types, for example for use in command parameter choice.

    """
    if ( sort ):
        # Sort alphabetically
        return [ INFO, FAILURE, SUCCESS, WARNING ]
    else:
        # Return in order of severity (good to bad)
        return [ INFO, SUCCESS, WARNING, FAILURE ]

def max_severity ( command_status1, command_status2 ):
    """
    Return the maximum (most severe) status of the given two status.

    Args:
        command_status1: First status to check such as 'SUCCESS' (indicates severity).
        command_status2: Second status to check such as 'WARNING' (indicates severity).

    Returns:
        The maximum (most severe) status of the given two status.
    """
    # If a true enumeration were used, then the comparisons could be simple numeric.
    # However, since Python just defines the strings, find the position in the array and then compare.
    pos1 = -1
    pos2 = -1
    pos = 0
    for status in __status_list:
        pos = pos + 1
        if ( command_status1 == status ):
            pos1 = pos
            break
    pos = 0
    for status in __status_list:
        pos = pos + 1
        if ( command_status2 == status ):
            pos2 = pos
            break
    if ( pos1 >= pos2 ):
        return command_status1
    else:
        return command_status2
