# string_util - utility functions for string manipulation
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2020 Open Water Foundation
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
This module provides utilities for manipulating strings.
"""

import logging
import re
from typing import Optional, List


def delimited_string_to_int_list(delimited_string: str, delimiter: str = ",") -> [str]:
    """
    Parse a delimited string into a list of numbers.

    Args:
        delimited_string (str): Delimited string.
        delimiter (str): Delimiter for the items in the string.

    Returns:
        List of integers, guaranteed to be non-None but may be empty
    """
    # Parse into string list
    string_list = delimited_string_to_list(delimited_string, delimiter)
    # Convert each string into an integer
    int_list = []
    if string_list is not None:
        for s in string_list:
            int_list.append(int(s))
        return int_list


# TODO smalers 2018-01-20 need to evaluate how many complexities to handle, similar to TSTool Java code
# - quoted strings
# - whitespace that is literal (need \ escape?)
# - adjoining delimiters
# - bounding [ ] as per Python list
# - strings surrounded with single quotes, which could work within a parameter value surrounded by double quotes
def delimited_string_to_list(delimited_string: str, delimiter: str = ",", trim: bool = True) -> [str]:
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
    # if delimited_string is None or delimited_string == "":
    if delimited_string is None:
        return None
    else:
        # The following works if even only a single item in the list
        parts = delimited_string.split(delimiter)
    if trim:
        for i in range(0, len(parts)):
            parts[i] = parts[i].strip()
    return parts


def delimited_string_to_dictionary_one_value(delimited_string: str, entry_delimiter: str = ";",
                                             key_value_delimiter: str = "=", trim: bool = True) -> dict or None:
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


def delimited_string_to_dictionary_list_value(delimited_string: str, entry_delimiter: str = ";",
                                              key_value_delimiter: str = "=", list_delimiter: str = ",",
                                              trim: bool = True) -> dict or None:
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


# TODO smalers 2021-04-25 this logic is confusing, expeecially the returned list.  Need to review.
def filter_list_of_strings(input_list: [str], include_glob_patterns: [str] = None,
                           exclude_glob_patterns: [str] = None, return_inclusions: bool = True,
                           include_count: int = None):
    """
    Filters a list of strings by glob patterns.

    Args:
        input_list (list): a list of strings to filter
        include_glob_patterns (list): a list of glob-style patterns corresponding to the items in the input_list that
            are to be included. Default is ['*']. All items from the input_list are included.
        exclude_glob_patterns (list): a list of glob-style patterns corresponding to the items in the input_list that
            are to be excluded. Default is ['']. No items from the input_list are excluded.
        return_inclusions (bool): Default is TRUE. If TRUE, a list of the items that should be included are returned.
            If FALSE, a list of the items that should be excluded are returned.
        include_count (int): Maximum number of list values to return.  If positive, the number is for the start
            of the list.  If negative, the number is for the end of the list.

    Return:
        A filtered list of strings. Results are based off of return_inclusions boolean.
    """

    # Assign the default values to the include_glob_patterns if there is no include_glob_patterns list.
    if include_glob_patterns is None:
        include_glob_patterns = ['*']
    # Assign the default values to the include_glob_patterns if all items in the include_glob_patterns list are None
    elif len([x for x in include_glob_patterns if x is None]) == len(include_glob_patterns):
        include_glob_patterns = ['*']
    # Assign the default values to the exclude_glob_patterns if there is no exclude_glob_patterns list.
    if exclude_glob_patterns is None:
        exclude_glob_patterns = ['']
    # Assign the default values to the exclude_glob_patterns if all items in the exclude_glob_patterns list are None
    elif len([x for x in exclude_glob_patterns if x is None]) == len(exclude_glob_patterns):
        exclude_glob_patterns = ['*']

    # A list to hold all of the item to include.
    master_items_to_include = []

    # A list to hold all of the item to exclude.
    master_items_to_exclude = []

    # Iterate over the include glob patterns.
    for pattern in include_glob_patterns:
        # Make sure that a None value is not passed.
        if pattern is not None:
            # Get the input list items that match the pattern. Add the items to the master_items_to_include list.
            items_to_include = list(i for i in input_list if re.match(glob2re(pattern), i))
            master_items_to_include.extend(items_to_include)

    # Remove any duplicates from the master_items_to_include list.
    master_items_to_include = list(set(master_items_to_include))

    # Iterate over the exclude glob patterns.
    for pattern in exclude_glob_patterns:
        # Make sure that a None value is not passed.
        if pattern is not None:
            # Get the input list items that match the pattern. Add the items to the master_items_to_exclude list.
            items_to_exclude = list(i for i in input_list if re.match(glob2re(pattern), i))
            master_items_to_exclude.extend(items_to_exclude)

    # Remove any duplicates from the master_items_to_exclude list.
    master_items_to_exclude = list(set(master_items_to_exclude))

    # The final inclusion list - holds all items that should be included after processing the patterns.
    include_list_final = [i for i in master_items_to_include if i not in master_items_to_exclude]

    # The final exclusion list - holds all items that should not be included after processing the patterns.
    exclude_list_final = [i for i in input_list if i not in include_list_final]

    # Sort the lists to return.
    include_list_final = sorted(include_list_final, key=str.lower)
    exclude_list_final = sorted(exclude_list_final, key=str.lower)

    # Return the appropriate list based off of the return_inclusions boolean.
    if return_inclusions:
        if include_count is not None:
            # Truncate the list to the requested number at front or back.
            if include_count > 0:
                # Truncate the returned list.
                if len(include_list_final) > include_count:
                    include_list_final = include_list_final[0:include_count]
            elif include_count < 0:
                # Return items at the end
                include_count = abs(include_count)
                if len(include_list_final) > include_count:
                    include_list_final = include_list_final[(len(include_list_final) - include_count):]
        return include_list_final
    else:
        if include_count is not None:
            # Truncate the list to the requested number at front or back.
            if include_count > 0:
                # Truncate the returned list.
                if len(exclude_list_final) > include_count:
                    exclude_list_final = exclude_list_final[0:include_count]
            elif include_count < 0:
                # Return items at the end
                include_count = abs(include_count)
                if len(exclude_list_final) > include_count:
                    exclude_list_final = exclude_list_final[(len(exclude_list_final) - include_count):]
        return exclude_list_final


def format_dict(dict_to_format: dict, value_quote: str = '"') -> str:
    """
    Format a dictionary for output in a string, such as for print statement.

    Args:
        dict_to_format: dictionary to format.
        value_quote: character to quote all values

    Returns:  a string containing formatted dictionary, string=key="value",key="value"
    """
    if dict is None:
        return ""
    formatted_string = ""
    count = 0
    delim = ","
    for key, value in dict_to_format.items():
        count = count + 1
        if count > 1:
            formatted_string = formatted_string + delim + key + "=" + value_quote + value + value_quote
        else:
            formatted_string = key + "=" + value_quote + value + value_quote
    return formatted_string


def get_leading_whitespace(s: str):
    """
    Get the leading whitespace for a string, used to get whitespace for indented commands.

    Args:
        s (str): string to process
    """
    white = ""
    for i in range(len(s)):
        if s[i] == " " or s[i] == "\t":
            # Add to the whitespace
            white += s[i]
        else:
            # Done processing
            break
    return white


def glob2re(pat: str) -> str:
    """
    Translates a glob-style shell pattern using '*' for wildcards to a regular expression.

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
    # noinspection
    return res + '\Z(?ms)'


def is_bool(s: str) -> bool:
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


def is_float(s: str) -> bool:
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


def is_int(s: str) -> bool:
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


def list_to_string(str_list: [str], add_nl: bool = False, nl: str = None) -> str:
    """
    Convert a list of strings to a single string.
    The separate strings should include trailing newline(s) ('\n') or specify add_nl parameter.

    Args:
        str_list ([str]): list of str to process into a single string.
        add_nl (bool):  whether to add newline character at the end of each string in the list.
        nl (str): newline character(s) to use at the end of strings if add_nl=True.

    Returns:
        String that contains the strings from the list.
    """
    logger = logging.getLogger(__name__)
    output_str = ""
    if nl is None:
        nl = '\n'
    for s in str_list:
        if add_nl:
            output_str = output_str + s + nl
        else:
            output_str = output_str + s
    return output_str


def key_value_pair_list_to_dictionary(key_value_list: [str]) -> dict:
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
        key = ""
        value = None
        if pos > 1:
            # Get the key and value
            key = key_value[0:pos].strip()
            value = key_value[pos + 1:].strip()
        # Add to the dictionary
        if key != "":
            dictionary[key] = value
    return dictionary


def parse_integer_list(s: str or None) -> [int]:
    """
    Parse a list of integers from string containing comma-separated list of individual integers and ranges, for
    example '1, 3-6, 17'.  The list will by default not be sorted.
    This is useful for parsing command parameter values into an internal data representation.

    Args:
        s (str): string to parse

    Returns:
        List containing integer values, guaranteed to be non-None but may be empty.
    """
    integer_list = []
    if s is None or len(s.strip()) == 0:
        return integer_list

    # First split the parts
    parts = []
    if s.find(",") < 0:
        parts.append(s.strip())
    else:
        parts = s.split(",")
        i = -1
        for part in parts:
            i += 1
            parts[i] = part.strip()

    # Loop through the parts:
    # - if a single integer set it
    # - if a range expand the range and set each value in the range to the parts
    for part in parts:
        if part.find("-") >= 0:
            range_parts = part.split("-")
            if len(range_parts) == 2:
                # Further process the range
                range_start = range_parts[0].trim()
                range_end = range_parts[1].trim()
                if is_int(range_start) and is_int(range_end):
                    i_range_start = int(range_start)
                    i_range_end = int(range_end)
                    for i in range(i_range_start,(i_range_end + 1)):
                        integer_list.append(i)
        else:
            if is_int(part):
                integer_list.append(int(part))

    # Return the integer list
    return integer_list


def pattern_count(s: str or None, pattern: Optional[str], patterns: Optional[List[str]] = None) -> int:
    """
    Count the number of unique (non-overlapping) instances of a pattern in a string.

    Args:
        s (str): String to search.
        pattern (str): String pattern to search for.  Currently this can only be a one-character string.
        patterns (str[]): Single character string patterns to search for.

    Returns:
        The count of the unique instances.
    """
    count = 0
    if s is None:
        return count
    size = len(s)
    for i in range(0, size):
        if pattern is not None and len(pattern) > 0:
            if s[i] == pattern[0]:
                count += 1
        if patterns is not None:
            # Loop through the patterns
            for p in patterns:
                if p is not None and len(p) > 0:
                    if s[i] == p[0]:
                        count += 1

    return count


def str_to_bool(string: str) -> bool or None:
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
