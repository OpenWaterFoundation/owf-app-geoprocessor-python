"""
Functions that provide validation for data values, in particular command parameters.
These functions are typically called from the check_command_parameters function
of commands to validate a parameter value.
Multiple functions may be called if necessary, although as many validator functions
as necessary can be defined.
"""

def validate_boolean ( boolean_value, none_allowed, empty_string_allowed ):
    """
    Validate that a boolean value is True or False.

    Args:
        boolean_value: Boolean value to check, can be string or boolean type.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.

    Returns:
        True if boolean value is valid, False if invalid.
    """
    # First check some specific cases
    if boolean_value == None:
        if none_allowed:
            return True
        else:
            return False
    if type(boolean_value) == 'str':
        if boolean_value == "":
            if ( empty_string_allowed ):
                return True
            else:
                return False
        # Reassign the value as a boolean to check
        try:
            boolean_value = bool(boolean_value)
        except:
            return False

    # By definition bool can only be None, True, or False so all cases are handled above.
    return True

def validate_int_in_range ( int_value, int_min, int_max, none_allowed, empty_string_allowed ):
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
    if int_value == None:
        if none_allowed:
            return True
        else:
            return False
    if type(int_value) == 'str':
        if int_value == "":
            if ( empty_string_allowed ):
                return True
            else:
                return False
        # Reassign the value as an integer to check
        try:
            int_value = int(int_value)
        except:
            return False

    # Now check the range
    if int_value >= int_min and int_value <= int_max:
        return True
    else:
        return False

def validate_string ( string_value, none_allowed, empty_string_allowed ):
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
    if string_value == None:
        if none_allowed:
            return True
        else:
            return False
    if string_value == "":
        if ( empty_string_allowed ):
            return True
        else:
            return False
    # If special cases pass then any string value is valid.
    return True

def validate_string_in_list ( string_value, string_list, none_allowed, empty_string_allowed, ignore_case=False ):
    """
    Validate that a string value is in a list.

    Args:
        string_value: String value to check, must be string type.
        string_list: List of allowed strings.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.
        ignore_case: If True, then string comparisons will ignore case.  If False, case is important.

    Returns:
        True if string value is valid, False if invalid.
    """
    # First check some specific cases
    if string_value == None:
        if none_allowed:
            return True
        else:
            return False
    if string_value == "":
        if ( empty_string_allowed ):
            return True
        else:
            return False

    # Now to see if the string is in the list
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
