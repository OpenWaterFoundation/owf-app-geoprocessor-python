"""
This module provides utilities for manipulating strings.
"""

import re


# TODO smalers 2018-01-20 need to evaluate how many complexities to handle, similar to TSTool Java code
# - quoted strings
# - whitespace that is literal (need \ escape?)
# - adjoining delimiters
# - bounding [ ] as per Python list
# - strings surrounded with single quotes, which could work within a parameter value surrounded by double quotes
def delimited_string_to_list(delimited_string, delimiter=",", trim=True):
    """
    Split a string in delimited format into a list of strings.
    This function can be used, for example, to split comma-separated parameters for a command,
    assuming that the outside surrounding quotes have already been removed.
    For example, the following input (quotes shown for emphasis but would not be part of delimited_string):

         "a,b,c,  d,"

    would result in a list ["a","b","c","d",""].

    Args:
        delimited_string (str):  Delimited string to process.
        delimiter (str):  Delimiter characters (can be more than one), used to make the initial split.
        trim (bool):  If True (the default), trim whitespace from the resulting parts.

    Returns:
        A list of strings parsed from the delimited string, None if the original string is None, and
        guaranteed to be at least an empty list otherwise.
    """
    if delimited_string is None:
        return None
    else:
        parts = delimited_string.split(delimiter)
    if trim:
        for i in range(0, len(parts)):
            parts[i] = parts[i].strip()
    return parts


def delimited_string_to_dictionary_one_value(delimited_string, entry_delimiter=";", key_value_delimiter="=", trim=True):
    """
    Split a string in delimited format into a dictionary of strings.
    This function can be used, for example, to split comma-separated parameters for a command,
    assuming that the outside surrounding quotes have already been removed.
    For example, the following input (quotes shown for emphasis but would not be part of delimited_string):

         "key1=value1;key2=value2"

    would result in a list {'key1': 'value1', 'key2': 'value2'}.

    Args:
        delimited_string (str):  Delimited string to process.
        entry_delimiter (str):  Delimiter characters (can be more than one), used to make the initial split
            between dictionary entries.
        key_value_delimiter (str):  Delimiter characters (can be more than one), used to make the split
            between key value pairs.
        trim (bool):  If True (the default), trim whitespace from the resulting parts.

    Returns:
        A dictionary of strings parsed from the delimited string, None if the original string is None, and
        guaranteed to be at least an empty dictionary otherwise.
    """

    dictionary = {}

    if delimited_string is None:
        return None
    elif len(delimited_string) == 0:
        return dictionary
    else:
        entries = delimited_string.split(entry_delimiter)

        if trim:
            for i in range(0, len(entries)):
                entries[i] = entries[i].strip()

        for entry in entries:

            if entry.count(key_value_delimiter) == 1:

                key = entry.split(key_value_delimiter)[0]
                value = entry.split(key_value_delimiter)[1]

                if trim:
                    key = key.strip()
                    value = value.strip()

                dictionary[key] = value

            else:
                raise ValueError("{} is not in proper key{}value format.".format(entry, key_value_delimiter))

        return dictionary


def delimited_string_to_dictionary_list_value(delimited_string, entry_delimiter=";",
                                              key_value_delimiter="=", list_delimiter=",", trim=True):
    """
    Split a string in delimited format into a dictionary. The key is a string and the value is a list of strings.
    This function can be used, for example, to split comma-separated parameters for a command,
    assuming that the outside surrounding quotes have already been removed.
    For example, the following input (quotes shown for emphasis but would not be part of delimited_string):

         "key1=value1,value1b,value1c;key2=value2"

    would result in a list {'key1': ['value1', 'value1b', 'value1c'], 'key2': ['value2']}.

    Args:
        delimited_string (str):  Delimited string to process.
        entry_delimiter (str):  Delimiter characters (can be more than one), used to make the initial split
            between dictionary entries.
        key_value_delimiter (str):  Delimiter characters (can be more than one), used to make the split
            between key value pairs.
        list_delimiter (str): Delimiter characters (can be more than one), used to split the dictionary values
         between items.
        trim (bool):  If True (the default), trim whitespace from the resulting parts.

    Returns:
        A dictionary of strings parsed from the delimited string, None if the original string is None, and
        guaranteed to be at least an empty dictionary otherwise.
    """

    dictionary = {}

    if delimited_string is None:
        return None
    elif len(delimited_string) == 0:
        return dictionary
    else:
        entries = delimited_string.split(entry_delimiter)

        if trim:
            for i in range(0, len(entries)):
                entries[i] = entries[i].strip()

        for entry in entries:

            if entry.count(key_value_delimiter) == 1:

                key = entry.split(key_value_delimiter)[0]
                value = entry.split(key_value_delimiter)[1]

                if trim:
                    key = key.strip()
                    value = value.strip()

                value = delimited_string_to_list(value, list_delimiter, trim)

                if trim:
                    for i in range(0, len(value)):
                        value[i] = value[i].strip()

                dictionary[key] = value

            else:
                raise ValueError("{} is not in proper key{}value format.".format(entry, key_value_delimiter))

        return dictionary


def filter_list_of_strings(input_list, include_glob_patterns=None, exclude_glob_patterns=None):
    """
    Filters a list of strings by glob patterns.

    Args:
        input_list (list): a list of strings to filter
        include_glob_patterns (list): a list of glob-style patterns corresponding to the items in the input_list that
            are to be included. Default is ['*']. All items from the input_list are included.
        exclude_glob_patterns (list): a list of glob-style patterns corresponding to the items in the input_list that
            are to be excluded. Default is ['']. No items from the input_list are excluded.

    Return:
        A filtered list of strings.
    """

    # Assign the default values to the include_glob_patterns and the exclude_glob_patterns.
    if include_glob_patterns is None:
        include_glob_patterns = ['*']
    if exclude_glob_patterns is None:
        exclude_glob_patterns = ['']

    # A list to hold all of the item to include.
    master_items_to_include = []

    # A list to hold all of the item to exclude.
    master_items_to_exclude = []

    # Iterate over the include glob patterns.
    for pattern in include_glob_patterns:
        # Get the items from the input_list that match the pattern. Add the items to the master_items_to_include list.
        items_to_include = list(i for i in input_list if re.match(glob2re(pattern), i))
        master_items_to_include.extend(items_to_include)

    # Remove any duplicates from the master_items_to_include list.
    master_items_to_include = list(set(master_items_to_include))

    # Iterate over the exclude glob patterns.
    for pattern in exclude_glob_patterns:
        # Get the items from the input_list that match the pattern. Add the items to the master_items_to_exclude list.
        items_to_exclude = list(i for i in input_list if re.match(glob2re(pattern), i))
        master_items_to_exclude.extend(items_to_exclude)

    # Remove any duplicates from the master_items_to_exclude list.
    master_items_to_exclude = list(set(master_items_to_exclude))

    # Remove any items in the master_items_to_include if the same items is in the master_items_to_exclude. Return
    # the final list.
    return [i for i in master_items_to_include if i not in master_items_to_exclude]


def glob2re(pat):
    """
    Translates a shell PATTERN to a regular expression.

    This function converts a glob-style pattern into a regular expression that can be used to iterate over a
    list of strings. This function was not written by Open Water Foundation but was instead copied from the
    following source: https://stackoverflow.com/questions/27726545/
    python-glob-but-against-a-list-of-strings-rather-than-the-filesystem.

    Args:
        pat (str, required): a pattern in glob-style (shell)

    Returns:
        A pattern in regular expression.
    """

    i, n = 0, len(pat)
    res = ''
    while i < n:
        c = pat[i]
        i += 1
        if c == '*':
            # res = res + '.*'
            res += '[^/]*'
        elif c == '?':
            # res = res + '.'
            res += '[^/]'
        elif c == '[':
            j = i
            if j < n and pat[j] == '!':
                j += 1
            if j < n and pat[j] == ']':
                j += 1
            while j < n and pat[j] != ']':
                j += 1
            if j >= n:
                res += '\\['
            else:
                stuff = pat[i:j].replace('\\', '\\\\')
                i = j + 1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        else:
            res = res + re.escape(c)
    return res + '\Z(?ms)'


def is_bool(s):
    """
    Determine whether a string can evaluate to a bool, must be "true" or "false"

    Args:
        s: A string that is checked.

    Returns:
        True if the string is "true" or "false" in any case, False if not.

    """
    # Boolean is tricky since bool(s) returns False if "" and True if anything else
    # - could use bool(distutils.util.strtobool(s)) but does not reject integers
    s_up = s.upper()
    if s_up == "TRUE" or s_up == "FALSE":
        return True
    else:
        return False


def is_float(s):
    """
    Determine whether a string can evaluate to a float.

    Args:
        s: A string that is checked.

    Returns:
        True if the string evaluates to a float, False if not.

    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_int(s):
    """
    Determine whether a string can evaluate to an int.

    Args:
        s: A string that is checked.

    Returns:
        True if the string evaluates to an int, False if not.

    """
    try:
        int(s)
        return True
    except ValueError:
        return False


def key_value_pair_list_to_dictionary(key_value_list):
    """
    Convert a list of key=value strings to dictionary with corresponding keys and values.

    Args:
        key_value_list ([str]:  List of key=value strings.

    Returns:
        Dictionary of key=value, where values are strings.
    """
    dictionary = {}
    for key_value in key_value_list:
        # Split by equal sign
        pos = key_value.find("=")
        if pos > 1:
            # Get the key and value
            key = key_value[0:pos].strip()
            value = key_value[pos + 1:].strip()
        # Add to the dictionary
        if key != "":
            dictionary[key] = value
    return dictionary


def pattern_count(s, pattern):
    """
    Count the number of unique (non-overlapping) instances of a pattern in a string.

    Args:
        s (str): String to search.
        pattern (str): Pattern to search for.  Currently this can only be a one-character string.

    Returns:
        The count of the unique instances.
    """
    count = 0
    if s is None or pattern is None or len(pattern) < 1:
        return count
    size = len(s)
    c = pattern[0]
    for i in range(0, size):
        if s[i] == c:
            count += 1
    return count


# TODO smalers 2018-02-18 need to phase this version out
def string_to_boolean(string):
    """
    Convert a string into a Boolean value.
    This version is deprecated - use str_to_bool().
    """
    return str_to_bool(string)


def str_to_bool(string):
    """
    Convert a string into a Boolean value.

    Args:
        string (str): String to convert.

    Returns:
        The associated Boolean value. If the input string does not correspond with a Boolean value, None is returned.
    """

    # If the string is 'True', return TRUE.
    if string.upper() == "TRUE":
        return True

    # If the string is 'False', return FALSE.
    elif string.upper() == "FALSE":
        return False

    # If the input string does not correspond with a Boolean value, return None.
    else:
        return None
