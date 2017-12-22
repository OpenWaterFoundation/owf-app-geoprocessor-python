# useful utility functions

def to_command_string_list(command_file):
    """convert a command file into a list of command strings (one item in the list for each line of the command file)

    :param: a string, the full pathname to a command file """

    # a list that will hold each command string as a item in the list
    command_string_list = []

    # iterate over each line in the command file and append the line as a string (remove white spaces on either side of
    # the line) to the command string list
    with open(command_file) as command_file:
        command_string_list_format = command_file.readlines()
        command_string = ("".join(command_string_list_format)).strip()
        command_string_list.append(command_string)

    # return the command string list
    return command_string_list

def get_command_name(command_line):
        """Parses the command_line and returns the CommandName"""

        # remove white spaces on either side of the command line
        command_line = command_line.strip()

        # determine the index of the first parenthesis within the command line.
        paren_start = command_line.find("(")

        # get the command name from the command line (in front of the '(' symbol )
        command_name = command_line[:paren_start]

        return command_name

def to_parameter_string(command_string):
    """Parses a command string into a parameter string"""

    # remove white spaces on either side of the command line
    command_string = command_string.strip()

    # determine the index of the first and last parenthesis within the command line string.
    paren_start = command_string.find("(")
    paren_end = command_string.find(")")

    # get the parameter line from the command string (in between the '(' symbol and the ')' symbol)
    parameter_string = command_string[paren_start + 1: paren_end]

    # check that there are available parameters. if so, return the parameter_line. else, return None
    if len(parameter_string) == 0:
        parameter_string = None
    return parameter_string

def to_parameter_items(parameter_string):
    """parameter strings are made up of individual parameter items -- one item (string format) for each parameter
    split parameter string into list of parameter items and return the list

    Example: [INPUT] parameterLine = '"firstParameter", "secondParameter", "thirdParameterName = thirdParameterValue"'
    [OUTPUT] parameter_strings = ['firstParameter', 'secondParameter', 'thirdParameterName = thirdParameterValue']

    :param parameter_string: A string, the sting inside the () of a command line that represents all of the input
    parameter values determined by the user"""

    # if the parameter line is not empty
    if parameter_string:

        # a list that will hold each of parameter strings
        parameter_items = []

        # Boolean to determine if the current character should be part of a parameter string
        in_string = False

        # Boolean to determine if there is another character available after the current character
        next_char_exists = True

        # iterate over the characters in the parameter_line
        for char_index in range(len(parameter_string)):

            # get the current character
            current_char = parameter_string[char_index]

            # determine if the current character is the last character in the parameter_line
            if char_index + 1 == len(parameter_string):
                next_char_exists = False

            # get the next character
            else:
                next_char = parameter_string[char_index + 1]

            # if current character is the quote symbol (") and there is not currently a string defined, then this is
            # the start of a parameter string
            if current_char == '"' and not in_string:

                in_string = True
                current_parameter_string_characters = []

            # if current character is the quote symbol (") and there is currently a string defined, AND this is the last
            # character or the next character is a ',' then this is the end of a parameter string
            # TODO add logic to include if the user put a space before the comma ex: '"string" ,' instead of '"string",'
            elif current_char == '"' and in_string and (next_char == "," or not next_char_exists):

                in_string = False
                current_parameter_string = "".join(current_parameter_string_characters)
                parameter_items.append(current_parameter_string)

            # if the character is not a (") and there is currently a string defined, then add this character to the
            # current_parameter_string_characters list. This list will collect all of the characters within each parameter
            # string.
            elif in_string:
                current_parameter_string_characters.append(current_char)

            # if the current character is not a (") and there is not currently a string defined, then
            # skip this character without adding it to the entry list or changing the status of the in_string variable
            else:
                pass

        # return the list of parameter strings
        return parameter_items
    else:
        return None

def to_parameter_dic(parameter_items):
    """Converts a list of parameter items (a string representing one parameter name/value in name=value format) into
    a dictionary where the key is the parameter name and the value is the parameter value. The parameter value is
    converted from a string to a list (if required)."""

    # a dictionary that holds each parameter as an entry (key: parameter name, value: parameter value)
    parameter_dic = {}

    # iterate over each item in the parameter items list
    for parameter_item in parameter_items:

        # the key, value format is determined by the inclusion of an equals sign
        if "=" in parameter_item:

            # the parameter name is on the left-side of the equals sign and the parameter value is on the right-side of the
            # equals sign
            parameter_name = (parameter_item.split('=')[0]).strip()
            parameter_value = (parameter_item.split('=')[1]).strip()


            # if the parameter value should be in list format, convert the string value to a list value
            if parameter_value.startswith('['):
                parameter_value = __to_correct_format(parameter_value)

            # append the parameter name and the parameter value (in string or list format) to the parameter dictionary
            parameter_dic[parameter_name] = parameter_value

        else:

            print "ERROR: the parameter ({}) is not in a proper 'parameter name = parameter value' format.".format(parameter_item)

    return parameter_dic

# converts a parameter value in string format to a parameter value in list format
def __to_correct_format(parameter_value):
    """The command file (txt) only contains lines of strings. The parameter values within each command line, are,
    initially all string format. However, it is required that some parameter values be list format. This function
    converts a sting parameter value to a list parameter value and returns the parameter value in list format.

    :param parameter_value: a parameter value in string format that is supposed to be in list format"""


    # Boolean to determine if the current character is a part of a string
    in_string = False

    # A list to hold the items (strings) of the parameter value list.
    parameter_value_list = []

    # iterate through the characters of the input parameter value string
    for char in parameter_value:

        # if current character is the apostrophe symbol (') and there is not currently a string defined, then this is
        # the start of a string that is meant to live as an item in the parameter value list
        if char == "'" and not in_string:
            entry = []
            in_string = True

        # if current character is the apostrophe symbol (') and there is currently a string defined, then this is the
        # end of a string that is meant to live as an item in the parameter value list. Add the string to the
        # parameter value list
        elif char == "'" and in_string:
            in_string = False
            entry_string = "".join(entry)
            parameter_value_list.append(entry_string)

        # if the current character is not the apostrophe symbol (') and there is currently a string defined, then add
        # this character to the entry list. The entry list will collect all of the characters within each string.
        elif char != "'" and in_string:
            entry.append(char)

        # if the current character is not the apostrophe symbol (') and there is not currently a string defined, then
        # skip this character without adding it to the entry list or changing the status of the in_string variable
        else:
            pass

    # return the parameter value list with the items as string values
    return parameter_value_list
