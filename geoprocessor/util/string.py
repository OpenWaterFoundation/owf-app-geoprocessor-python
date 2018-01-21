"""
This module provides utilities for manipulating strings.
"""


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
        for i in range(0,len(parts)):
            parts[i] = parts[i].strip()
    return parts


def string_to_dictionary(string):
    """
        Parses a string in proper dictionary format to a dictionary.

        Proper dictionary format:
            (1) String starts and ends in open and closed curly brackets.
            (2) The entries of the dictionary are required to be enclosed in apostrophes.
            (3) The entry key is on the left side of an equals sign.
            (4) The entry value is on the right side of an equals sign.

        Args:
            string (string): a string to be parsed into a dictionary

        Returns:
            A dictionary, the parsed input string.

        Raises:
            Value Error. Raised if input string is not in proper dictionary format.
        """

    # Continue if the string is in proper dictionary format (starts with an open curly bracket and ends with a closed
    #  curly bracket).
    if string.startswith("{") and string.endswith("}"):

        # Return an empty dictionary if the string represents an empty dictionary.
        if len(string) == 2:
            return {}

        # Continue if the string is not empty and both the second and the second-to-last characters are apostrophes.
        elif string[1] == "'" and string[-2] == "'":

            # Continue if there are an even number of apostrophes in the string.
            if string.count("'") % 2 == 0:

                # A dictionary to hold the parsed entries.
                output_parsed_dic = {}

                # Boolean to determine if the current character is an item within the list.
                in_entry = False

                # A list to hold the parsed entries.
                entry_list = []

                # Iterate through the characters of the input string.
                for char in string:

                    # If the current character is the apostrophe symbol (') and there is not currently an item defined,
                    # then this is the start of an item that is meant to be a dictionary entry.
                    if char == "'" and not in_entry:
                        entry = []
                        in_entry = True

                    # If the current character is the apostrophe symbol (') and there is currently an item defined,
                    # then this is the end of an item that is meant to be a dictionary entry. Add the item to the
                    # entry_list.
                    elif char == "'" and in_entry:
                        in_entry = False
                        entry_string = "".join(entry)
                        entry_list.append(entry_string)

                    # If the current character is not the apostrophe symbol (') and there is currently an item defined,
                    # then add this character to the entry list. The entry list will collect all of the characters
                    # within each item.
                    elif char != "'" and in_entry:
                        entry.append(char)

                    # If the current character is not the apostrophe symbol (') and there is not currently an item
                    # defined, then skip this character without adding it to the entry list or changing the status of
                    # the in_entry variable.
                    else:
                        pass

                # Iterate through the entries of the entry_list.
                for entry in entry_list:

                    # Continue if the string is in proper dictionary form.
                    if entry.count("=") == 1:

                        entry_key = entry.split("=")[0]
                        entry_value = entry.split("=")[1]

                        # If the entry value is in list format, convert the entry value string into a list.
                        if entry_value.startswith('[') and entry_value.endswith(']'):

                            in_proper_list_format = __string_to_dictionary_properlistformat(entry_value)
                            entry_value = string_to_list(in_proper_list_format)

                        # Add the entry to the output_parsed_dic dictionary.
                        output_parsed_dic[entry_key] = entry_value

                    # The string is in improper list format. There should one equals sign in each entry.
                    else:
                        raise ValueError(
                            "The string ({}) is in improper dictionary format. There should be 1 equals sign in each "
                            "dictionary parameter. Entry ({}) does not only have 1 equals sign.".format(string, entry))

                # Return the output_parsed_dic
                return output_parsed_dic

            # The string is in improper dictionary format. There should be an even number of apostrophes.
            else:
                raise ValueError("The string ({}) is in improper dictionary format. There is not an EVEN number of"
                                 " apostrophes.".format(string))

        # The string is in improper dictionary format. Second or second-to-last character is not an apostrophe.
        else:
            raise ValueError(
                "The string ({}) is in improper dictionary format. The second and second to last characters must "
                "be apostrophes.".format(string))

    # The string is in improper dictionary format. First of last character is not a closed/open curly bracket.
    else:
        raise ValueError("The string ({}) is in improper dictionary format. The first character must be an open curly "
                         "bracket ({{) and the last character must be a closed curly bracket (}})".format(string))


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


def __string_to_dictionary_properlistformat(string):
    """
    A private function to be used in the string_to_dictionary. A dictionary in string format can have a list as an
    entry value. The entry value list does not have apostrophes around each entry (not in the proper string format for
    the string_to_list function). This function will convert the dictionary entry value string to proper string format
    so that the dictionary value can be converted to list format using the string_to_list function.

    Args:
        string: the string of the dictionary entry value that is meant to be a list

    Returns:
        output_string: the converted string of the dictionary entry value (input) in proper string format for the
        string_to_list function

    Raises:
        None
    """

    # Create an empty string. Characters will be added to this string as the function processes the input.
    output_string = ""

    # Iterate over each character in the input string.
    for char in string:

        # If the character is an open bracket, append an open bracket and an apostrophe to the output_string.
        if char == "[":
            output_string += "['"

        # If the character is a comma, append a comma surrounded by two apostrophes to the output_string.
        elif char == ',':
            output_string += "','"

        # If the character is a space, do not append anything to the output_string.
        elif char == ' ':
            pass

        # If the character is a closed bracket, append an apostrophe and a closed bracket to the output_string.
        elif char == ']':
            output_string += "']"

        # If the character is anything other than the above listed, append that character to the output_string.
        else:
            output_string += char

    # Return the processed output string.
    return output_string


# TODO smalers 2018-01-20 The behavior of this function may be too restrictive.
# - often a parameter will have a list of strings in CSV format for example Parameter="value1,value2,value3"
#   and it does not make sense to force users to add an additional level of quotes
def string_to_list(string):
    """
    Parses a string in proper list format to a list of strings.

    Proper list format:
        (1) String starts and ends in open and closed brackets.
        (2) The items of the list are required to be enclosed in apostrophes.

    Args:
        string (string): a string to be parsed into a list

    Returns:
        A list, the parsed input string.

    Raises:
        Value Error. Raised if input string is not in proper list format.
    """

    # Continue if the string is in proper list format (starts with an open bracket and ends with a closed bracket).
    if string.startswith("[") and string.endswith("]"):

        # Return an empty list if the string represents an empty list.
        if len(string) == 2:
            return []

        # Continue if the string is not empty and both the second and the second-to-last characters are apostrophes.
        elif string[1] == "'" and string[-2] == "'":

            # Continue if there are an even number of apostrophes in the string.
            if string.count("'") % 2 == 0:

                # Boolean to determine if the current character is an item within the list.
                in_item = False

                # A list to hold the parsed items (strings).
                output_parsed_list = []

                # Iterate through the characters of the input string.
                for char in string:

                    # If the current character is the apostrophe symbol (') and there is not currently a string defined,
                    # then this is the start of a string that is meant to be a list item.
                    if char == "'" and not in_item:
                        entry = []
                        in_item = True

                    # If the current character is the apostrophe symbol (') and there is currently a string defined,
                    # then this is the end of a string that is meant to be a list item. Add the string to the
                    # output_parsed_list.
                    elif char == "'" and in_item:
                        in_item = False
                        entry_string = "".join(entry)
                        output_parsed_list.append(entry_string)

                    # If the current character is not the apostrophe symbol (') and there is currently a string defined,
                    # then add this character to the entry list. The entry list will collect all of the characters
                    # within each item.
                    elif char != "'" and in_item:
                        entry.append(char)

                    # If the current character is not the apostrophe symbol (') and there is not currently a string
                    # defined, then skip this character without adding it to the entry list or changing the status of
                    # the in_string variable.
                    else:
                        pass

                # Return the output_parsed_list with the items as string values
                return output_parsed_list

            # The string is in improper list format. Uneven number of apostrophes.
            else:
                raise ValueError(
                    "The string ({}) is in improper list format. There is not an EVEN number of apostrophes.".format(
                        string))

        # The string is in improper list format. Second or second-to-last character is not an apostrophe.
        else:
            raise ValueError("The string ({}) is in improper list format. The second and second to last characters"
                             " must be apostrophes.".format(string))

    # The string is in improper list format. First of last character is not a closed/open bracket.
    else:
        raise ValueError("The string ({}) is in improper list format. The first character must be an open bracket ([)"
                         "and the last character must be a closed bracket (])".format(string))
