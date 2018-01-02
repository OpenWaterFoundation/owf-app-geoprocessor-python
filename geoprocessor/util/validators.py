"""
Functions that provide validation for data values, in particular command parameters.
These functions are typically called from the check_command_parameters function
of commands to validate a parameter value.
Multiple functions may be called if necessary, although as many validator functions
as necessary can be defined.
"""


def validate_bool(bool_value, none_allowed, empty_string_allowed):
    """
    Validate that a boolean value is True or False.

    Args:
        bool_value: Boolean value to check, can be string or bool type.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.

    Returns:
        True if bool value is valid, False if invalid.
    """
    # First check some specific cases
    if bool_value is None:
        if none_allowed:
            return True
        else:
            return False
    if isinstance(bool_value, str):
        if bool_value == "":
            if empty_string_allowed:
                return True
            else:
                return False
        # Reassign the value as a bool to check
        # Dangerous to use bool(bool_value) because True is returned for all sorts of things.
        # Therefore do a bit more work.
        bool_value_upper = bool_value.upper()
        if bool_value_upper == 'TRUE':
            return True
        else:
            return False

    # By definition bool can only be None, True, or False so all cases are handled above.
    return True


def validate_int_in_range(int_value, int_min, int_max, none_allowed, empty_string_allowed):
    """
    Validate that an integer value is in a range.

    Args:
        int_value: Integer value to check, can be string or int type.
        int_min: Minimum acceptable value.
        int_max: Maximum acceptable value.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.

    Returns:
        True if integer value is valid, False if invalid.
    """
    # First check some specific cases
    if int_value is None:
        if none_allowed:
            return True
        else:
            return False
    if isinstance(int_value, str):
        if int_value == "":
            if empty_string_allowed:
                return True
            else:
                return False
        # Reassign the value as an integer to check
        try:
            int_value = int(int_value)
        except ValueError:
            return False

    # Now check the range
    if int_min <= int_value <= int_max:
        return True
    else:
        return False


def validate_number(number_value, none_allowed, empty_string_allowed):
    """
    Validate that a number value is True or False.

    Args:
        number_value: Number value to check, can be string or number (int or float) type.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.

    Returns:
        True if number value is valid, False if invalid.
    """
    # First check some specific cases
    if number_value is None:
        if none_allowed:
            return True
        else:
            return False
    if isinstance(number_value, str):
        if number_value == "":
            if empty_string_allowed:
                return True
            else:
                return False
        # Reassign the value as a number to check - use float since it includes int values
        try:
            float(number_value)
        except ValueError:
            return False
    else:
        # May do more checks later but for now above should be sufficient
        pass
    return True


def validate_string(string_value, none_allowed, empty_string_allowed):
    """
    Validate that a string value is specified.
    This is a basic test just to make sure that a value has been provided.

    Args:
        string_value: String value to check, must be string type.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.

    Returns:
        True if string value is valid, False if invalid.
    """
    # First check some specific cases
    if string_value is None:
        if none_allowed:
            return True
        else:
            return False
    if string_value == "":
        if empty_string_allowed:
            return True
        else:
            return False
    # If special cases pass then any string value is valid.
    return True


def validate_string_in_list(string_value, string_list, none_allowed=False,
                            empty_string_allowed=False, ignore_case=False):
    """
    Validate that a string value is in a list of allowed string values.

    Args:
        string_value (str): String value to check, must be string type.
        string_list: List of allowed strings.
        none_allowed (bool): If the value is None, OK.
        empty_string_allowed (bool): If the value is an empty string, OK.
        ignore_case (bool): If True, then string comparisons will ignore case.  If False, case is important.

    Returns:
        True if string value is valid, False if invalid.
    """
    # First check some specific cases
    if string_value is None:
        if none_allowed:
            return True
        else:
            return False
    if string_value == "":
        if empty_string_allowed:
            return True
        else:
            return False

    # Now to see if the string is in the list
    string_value_upper = None
    if ignore_case:
        string_value_upper = string_value.upper()
    for s in string_list:
        if ignore_case:
            if s.upper() == string_value_upper:
                return True
        else:
            if s == string_value:
                return True
    # No string in the list was matched
    return False


def validate_list(list_value, none_allowed, empty_string_allowed, brackets_required=True):
    """
    Validate that a list value is a list.

    The list_value can either be a list type or a string that can be converted into a list (checks that the string
    contains both the '[' and the ']' symbols).

    Args:
        list_value: List value to check, can be string or list type.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.
        brackets_required: If the value requires open and close brackets ([]), validate that the brackets exist

    Returns:
        True if list value is valid, False if invalid.
    """
    # First check some specific cases
    if list_value is None:
        if none_allowed:
            return True
        else:
            return False

    if isinstance(list_value, str):
        if list_value == "":
            if empty_string_allowed:
                return True
            else:
                return False
        else:
            if brackets_required:
                if '[' in list_value and ']' in list_value:
                    return True
                else:
                    return False
            else:
                return True

    elif type(list_value) == 'list':
        return True

    else:
        return False
