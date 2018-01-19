# Input/output functions
# - some are ported from Java IOUtil.java class

import os
import sys


def to_absolute_path(parent_dir, path):
    """
    Convert an absolute "parent_dir" and path to an absolute path.
    If the path is already an absolute path it is returned as is.
    If the path is a relative path, it is joined to the absolute path "parent_dir" and returned.
    This is a port of the Java IOUtil.toAbsolutePath() method.

    Args:
        parent_dir (str): Directory to prepend to path, for example the current working directory.
        path (str): Path to append to parent_dir to create an absolute path.
                   If absolute, it will be returned.
                   If relative, it will be appended to parent_dir.
                   If the path includes "..", the directory will be truncated before appending the non-".."
                   part of the path.

    Returns:
        The absolute path given the provided input path parts.
    """
    if os.path.isabs(path):
        # No need to do anything else so return the path without modification
        return path

    # Loop through the "path".  For each occurrence of "..", knock a directory off the end of the "parent_dir"...

    # Always trim any trailing directory separators off the directory paths.
    while len(parent_dir) > 1 and parent_dir.endswith(os.sep):
        parent_dir = parent_dir[0:len(parent_dir) - 1]

    while len(path) > 1 and path.endswith(os.sep):
        path = path[0:len(path) - 1]

    path_length = len(path)
    sep = os.sep
    for i in range(0, path_length):
        if path.startswith("./") or path.startswith(".\\"):
            # No need for this in the result.
            # Adjust the path and evaluate again.
            path = path[2:]
            i = -1
            path_length = path_length - 2
        if path.startswith("../") or path.startswith("..\\"):
            # Remove a directory from each path.
            pos = parent_dir.rfind(sep)
            if pos >= 0:
                # This will remove the separator.
                parent_dir = parent_dir[0:pos]
            # Adjust the path and evaluate again.
            path = path[3:]
            i = -1
            path_length -= 3
        elif path == "..":
            # Remove a directory from each path.
            pos = parent_dir.rfind(sep)
            if pos >= 0:
                parent_dir = parent_dir[0:pos]
            # Adjust the path and evaluate again.
            path = path[2:]
            i = -1
            path_length -= 2

    return os.path.join(parent_dir, path)


def verify_path_for_os(path):
    """
    Verify that a path is appropriate for the operating system.
    This is a simple method that does the following:
    - If on UNIX/LINUX, replace all \ characters with /.
      WARNING - as implemented, this will convert UNC paths to forward slashes.
      Windows drive letters are not changed, so this works best with relative paths.
    - If on Windows, replace all / characters with \

    Args:
        path (str): Path to adjust.

    Returns:
        Path adjusted to be compatible with the operating system.
    """
    if path is None:
        return path

    platform = sys.platform
    if platform == 'linux' or platform == 'linux2' or platform == 'cygwin' or platform == 'darwin':
        # Convert Windows paths to Linux
        return path.replace('\\', '/')
    else:
        # Assume Windows, convert paths from Linux to Windows
        return path.replace('/', '\\')


def expand_formatter(absolute_path, formatter):

    """
    Returns the appropriate value of a parsed absolute path given the user-defined formatter code. Many of times
    the user will want the filename without the extension or just the extension from an absolute path. This function
    will return the desired parsed path given the user's input.

    Args:
        absolute_path (string): a full pathname to a file
        formatter (string): a code that references the type of return value. See available formatter codes below:
            example absolute path | C:/Users/User/Desktop/example.geojson.txt
            %F | the filename with the extension ex: example.geojson.txt
            %f | the filename without the extension ex: example.geojson
            %P | the full path (including the leading path, the filename and the extension)
               |    ex: C:/Users/User/Desktop/example.geojson.txt
            %p | the leading path without the filename or extension ex: C:/Users/User/Desktop
            %E | the extension with the '.' character ex: .txt

    Returns:
        The appropriate value of the parsed absolute path given the input formatter code.
    """

    # Get the full path without the extension and the extension
    path_without_ext, extension = os.path.splitext(absolute_path)

    # Get the filename without the extension
    filename = os.path.basename(path_without_ext)

    # The %F formatter code returns the filename with the extension and without the leading path. Print warning
    # messages if the filename or extension are non-existent. (The returned value, in those cases, will not be None
    # but will instead be an empty string).
    if formatter == '%F':

        if extension == '':
            print "Warning: There is no file extension for the input file ({})".format(absolute_path)
        if filename == '':
            print "Warning: There is no filename for the input file ({})".format(absolute_path)
        return "{}{}".format(filename, extension)

    # The %f formatter code returns the filename without the leading path and without the extension. Print warning
    # messages if the filename is non-existent. (The returned value, in that case, will not be None but will instead be
    # an empty string).
    elif formatter == '%f':

        if filename == '':
            print "Warning: There is no filename for the input file ({})".format(absolute_path)
        return filename

    # The %P formatter code returns the filename with the leading path and with the file extension.
    elif formatter == '%P':

        return absolute_path

    # The %p formatter code returns the leading path without the filename or the file extension.
    elif formatter == '%p':

        return os.path.dirname(absolute_path)

    # The %E formatter code returns the extension with the '.' character. Print warning messages if the extension is
    # non-existent. (The returned value, in that case, will not be None but will instead be an empty string).
    elif formatter == '%E':

        if extension == '':
            print "Warning: There is no file extension for the input file ({})".format(absolute_path)
        return extension

    # Print a warning message and return None if the input formatter code is not a valid code.
    else:
        print "The formatter ({}) is not an option."
        return None


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

                            in_proper_list_format = __string_to_dictonary_properlistforamt(entry_value)
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


def __string_to_dictonary_properlistforamt(string):
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
