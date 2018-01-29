"""
Possible values of command status.
When the code migrates to Python 3 this can be replaced with an Enum named CommandStatusType.
"""

UNKNOWN = 'UNKNOWN'
INFO = 'INFO'
SUCCESS = 'SUCCESS'
WARNING = 'WARNING'
FAILURE = 'FAILURE'

__status_list = [INFO, SUCCESS, WARNING, FAILURE]


def get_command_status_types(sort=False):
    """
    Return the list of valid command status.

    Args:
        sort:  If True, sort alphabetically.  If False, return in order of severity (default).

    Returns:
        The list of status types, for example for use in command parameter choice.

    """
    if sort:
        # Sort alphabetically
        return [INFO, FAILURE, SUCCESS, WARNING]
    else:
        # Return in order of severity (good to bad)
        return [INFO, SUCCESS, WARNING, FAILURE]


def max_severity(command_status1, command_status2):
    """
    Return the maximum (most severe) status of the given two status.

    Args:
        command_status1: First status to check such as 'SUCCESS' (indicates severity).
        command_status2: Second status to check such as 'WARNING' (indicates severity).

    Returns:
        The maximum (most severe) status of the given two status.
        For example, FAILURE is more severe than WARNING.
    """
    # If a true enumeration were used, then the comparisons could be simple numeric.
    # However, since Python just defines the strings, use the number_value function to help.
    value1 = number_value(command_status1)
    value2 = number_value(command_status2)
    if value1 > value2:
        return command_status1
    elif value2 > value1:
        return command_status2
    else:
        # They are the same
        return command_status1


def number_value(command_status):
    """
    Lookup a numeric value for the status, to allow comparison.

    Args:
        command_status:  Command status string (e.g., 'FAILURE').

    Returns:
        Integer value corresponding to the status
    """
    if command_status == UNKNOWN:
        return -1
    elif command_status == INFO:
        return 0
    elif command_status == SUCCESS:
        return 1
    elif command_status == WARNING:
        return 2
    elif command_status == FAILURE:
        return 3


def value_of(str_value, ignore_case=False):
    """
    Look up the value of an enumeration given the string value.
    This is useful for standardizing internal values to the specific enumeration value
    whereas some code may accept variants, such as 'WARN' and 'FAIL'.

    Args:
        str_value (str): String value of the enumeration.
        ignore_case (bool): Whether or not to ignore case (default = False).

    Returns:
        Value of the enumeration, or None if not matched.
    """
    if ignore_case:
        # Input string can be anything so convert to uppercase for comparison
        str_value = str_value.upper()

    if str_value == 'UNKNOWN':
        return UNKNOWN
    elif str_value == 'INFO':
        return INFO
    elif str_value == 'WARNING' or str_value == 'WARN':
        return WARNING
    elif str_value == 'FAILURE' or str_value == 'FAIL':
        return FAILURE
    else:
        return None
