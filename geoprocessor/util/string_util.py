"""
This module provides utilities for manipulating strings.
"""

import re


# TODO smalers 2018-01-20 need to evaluate how many complexities to handle, similar to TSTool Java code
# - quoted strings
# - whitespace that is literal (need \ escape?)
# - adjoining delimiters
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


def glob2re(pat):
    """
    Translates a shell PATTERN to a regular expression.

    The input parameters of the ReadGeoLayersFromFolder command are the exact same as the input parameters
    of this command, ReadGeoLayersFromFGDB. This design is for user convenience so that the user only needs
    to learn the input parameters of one command and will, in turn, know the input parameters for all
    ReadGeoLayersFrom... commands.

    In the ReadGeoLayersFromFolder command, there is an optional input parameter called Subset_Pattern. Like in
    the ReadGeoLayersFromFGDB command, this parameter allows the user to select only a subset of the spatial
    data files within the source (folder, file geodatabase, etc.) to read as GeoLayers into the geoprocessor.
    This is accomplished by entering a glob-style pattern into the Subset_Pattern parameter value. In the
    ReadGeoLayerFromFolder command, the glob-style pattern is effective because the run_command code iterates
    over files on the local machine (glob is designed to find patterns in pathnames). However, in the
    ReadGeoLayersFromFGDB command, the feature classes in the file geodatabase are first written to a list. The
    list is then iterated over and only the strings that match the Subset_Pattern are processed. Feature class
    names are not file pathnames and, for that reason, the glob-style does not work.

    This function converts a glob-style pattern into a regular expression that can be used to iterate over a
    list of strings. This function was not written by Open Water Foundation but was instead copied from the
    following source: https://stackoverflow.com/questions/27726545/
    python-glob-but-against-a-list-of-strings-rather-than-the-filesystem.

    Args:
        pat (str, required): a pattern in glob-style (shell)

    Returns:
        A pattern in regular expression.

    Raises:
        Nothing.
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


def string_to_boolean(string):
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
