import os
from commandprocessor.util import abstractcommand, processor_utilities
import command_dictionary
from processing.core.Processing import Processing
from qgis.core import QgsApplication


# command files are made up of one or many lines (comment lines and command lines)
# split command file to a list of comment lines and command lines
# return comment_lines, command_lines
def read_command_file(command_file_path):

    with open(command_file_path) as command_file:
        lines = command_file.readlines()
        command_file_lines = [line.strip() for line in lines]

    comment_lines = []
    command_lines = []
    for line in command_file_lines:
        if line.startswith('#'):
            comment_lines.append(line)
        elif line == "":
            pass
        else:
            command_lines.append(line)

    return comment_lines, command_lines

# command lines are made up of a command name and a parameter line
# split command line to the command name
# return command name. return None if the command name is not a registered command name
def command_line_to_command_name(command_line):

    command_line = command_line.strip()

    # Determine the index of the first parenthesis within the command line.
    paren_start = command_line.find("(")

    command_name = command_line[:paren_start]
    if processor_utilities.is_command_name_valid(command_name):
        return command_name

    else:
        print "Invalid command name for {}".format(command_line)
        return None

# command lines are made up of a command name and a parameter line
# split command line to the parameter line
# return parameter line
def command_line_to_parameter_line(command_line):

    command_line = command_line.strip()

    # Determine the index of the first and last parenthesis within the command line string.
    paren_start = command_line.find("(")
    paren_end = command_line.find(")")

    parameter_line = command_line[paren_start + 1: paren_end]

    if len(parameter_line) == 0:
        parameter_line = None

    return parameter_line

# parameter lines are made up of individual parameter strings (one string for each parameter)
# split parameter line into list of parameter strings
# return parameter strings
def parameter_line_to_parameter_strings(parameter_line):

    # a list that will hold each of the parameter values as items (in string format)
    parameter_strings = []

    # Boolean to determine if the current character should be part of the output string
    in_string = False

    # Boolean to determine if there is another character available after the current character
    next_char_exists = True

    # iterate over the characters in the input string
    for char_index in range(len(parameter_line)):
        current_char = parameter_line[char_index]

        # determine if this is the last character in the input string
        if char_index + 1 == len(parameter_line):
            next_char_exists = False
        else:
            next_char = parameter_line[char_index + 1]

        # if current character is the quote symbol (") and there is not currently a string defined, then this is
        # the start of a parameter value string
        # if current_char == '"' and not in_string and next_char != ",":
        if current_char == '"' and not in_string:

            in_string = True
            entry = []

        # if current character is the quote symbol (") and there is currently a string defined, AND this is the last
        # character or the next character is a ',' then this is the end of a parameter value string
        # TODO add logic to include if the user put a space before the comma ex: '"string" ,' instead of '"string",'
        elif current_char == '"' and in_string and (next_char == "," or not next_char_exists):

            in_string = False
            entry_string = "".join(entry)
            parameter_strings.append(entry_string)

        # if the character is not a (") and there is currently a string defined, then add this character to the
        # entry list. The entry list will collect all of the characters within each string.
        elif in_string:
            entry.append(current_char)

        # if the current character is not a (") and there is not currently a string defined, then
        # skip this character without adding it to the entry list or changing the status of the in_string variable
        else:
            pass

    # return the list of parameter values (in string format)
    return parameter_strings

# Converts a parameter value in string format to a parameter value in list format
def parameter_value_string_to_list_format(parameter_string):
    """The command file (txt) only contains lines of strings. The parameter values within each command line, are,
    initially all string format. However, it is required that some parameter values be list format. This function
    converts a sting parameter value to a list parameter value and returns the parameter value in list format.

    :param parameter_string: a parameter value in string format that is supposed to be in list format"""

    # Boolean to determine if the current character is a part of a string
    in_string = False

    # A list to hold the items (strings) of the parameter value list.
    parameter_value_list = []

    # iterate through the characters of the input parameter value string
    for char in parameter_string:

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

# each parameter string is made up of one parameter value (can either be string or list)
# the parameter value is associated with a specific parameter name (in the command class)
# convert parameter string into parameter value
# return parameter name and parameter value
def parameter_string_to_parameter_value(parameter_string, index_in_parameter_line, command_name):

    if "=" in parameter_string:

        parameter_name = (parameter_string.split('=')[0]).strip()
        parameter_value = (parameter_string.split('=')[1]).strip()

    else:

        command_parameter_names = processor_utilities.get_command_parameter_names(command_name)
        parameter_name = command_parameter_names[index_in_parameter_line]
        parameter_value = (parameter_string).strip()

    if parameter_value.startswith('['):

        parameter_value = parameter_value_string_to_list_format(parameter_value)

    return parameter_name, parameter_value

# each parameter line (made up of parameter strings) has unique parameter values provided by the user
# this function converts a parameter string into a dictionary of unique parameter values related to parameter names
def parameter_strings_to_input_parameter_value_dic(parameter_strings, command_name):

    input_parameter_value_dic = {}

    count  = 0

    for parameter_string in parameter_strings:

        parameter_name, input_parameter_value = parameter_string_to_parameter_value(parameter_string, count,
                                                                                    command_name)
        input_parameter_value_dic[parameter_name] = input_parameter_value
        count += 1

    return input_parameter_value_dic

# need to add comments to this function
def map_input_parameter_values_to_parameter_list(input_parameter_value_dic, command_name):

    ordered_parameter_list = []

    command_parameter_values_dic = processor_utilities.get_command_parameter_values_dic(command_name)
    command_parameter_names = processor_utilities.get_command_parameter_names(command_name)

    for command_parameter_name in command_parameter_names:

        if command_parameter_name in list(input_parameter_value_dic.keys()):

            ordered_parameter_list.append(input_parameter_value_dic[command_parameter_name])

        else:

            ordered_parameter_list.append(command_parameter_values_dic[command_parameter_name])

    return ordered_parameter_list

# given a command name and a complete and ordered list of parameter values, this function will initialize a command
# class object and run class' run_command function
def run_command(command_name, ordered_parameter_values):

    # notify user which command is currently running
    print "Running {} with parameters {}".format(command_name, ordered_parameter_values)

    # initialize the command class
    command_instance = command_dictionary.command_dictionary[command_name](ordered_parameter_values)

    # run the command with the provided parameter values
    command_instance.run_command()

# this function will read a command file, parse the features of each command, and run the commands in sequential order
def process_command_file(path):

    # Initialize QGIS resources to utilize QGIS functionality.
    QGISprefixPath = r"C:\OSGeo4W\apps\qgis"
    QgsApplication.setPrefixPath(QGISprefixPath, True)
    qgs = QgsApplication([], True)
    qgs.initQgis()
    Processing.initialize()

    comment_lines, command_lines = read_command_file(path)
    for command_line in command_lines:
        command_name = command_line_to_command_name(command_line)

        parameter_line = command_line_to_parameter_line(command_line)
        parameter_strings = parameter_line_to_parameter_strings(parameter_line)
        input_parameter_value_dic = parameter_strings_to_input_parameter_value_dic(parameter_strings, command_name)
        ordered_parameter_values = map_input_parameter_values_to_parameter_list(input_parameter_value_dic, command_name)
        run_command(command_name, ordered_parameter_values)

    # Close QGIS resources
    qgs.exit()

    # Remove any intermediate files from temporary folder that were created during the session
    temp_folder = abstractcommand.AbstractCommand.temp_folder
    for file in os.listdir(temp_folder):
        os.remove(os.path.join(temp_folder, file))


####################### WORKING ENVIRONMENT ###############################
curr_directory = os.path.dirname(os.path.realpath(__file__))
cmdFileDir = curr_directory.replace("commandprocessor\core", "command_files")
process_command_file(os.path.join(cmdFileDir, "exampleCmdFile.txt"))

