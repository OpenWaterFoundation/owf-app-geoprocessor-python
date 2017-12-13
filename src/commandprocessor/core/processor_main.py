# system imports
import os

# third-party imports
from processing.core.Processing import Processing
from qgis.core import QgsApplication

# local imports
from commandprocessor.util import abstractcommand, processor_utilities
import command_dictionary

# ------------------------------------------------------------------------------------------------------------------ #

# command files are made up of one or many lines (comment lines and command lines)
# split command file to a list of comment lines and command lines
# return comment_lines and command_lines
def read_command_file(command_file_path):
    """Reads each line of a command file and writes each line to its respective lists. Two lists are returned, the
    comment_lines list and the command_lines list. The comment_lines list contains all of the comments (indicated by a
    # prefix) in the command file in sequence. The command_lines list contains all of the command lines in the command
    file in sequence.

    :param command_file_path: A string, the full pathname to the command file to be read"""

    # append each line in the command file to the command_file_lines list
    with open(command_file_path) as command_file:
        lines = command_file.readlines()
        command_file_lines = [line.strip() for line in lines]

    # comment_lines: A list, placeholder list that will hold all of the command file lines that start with a '#'
    # command_lines: A list, placeholder list htat will hold all of the command file lines representing command lines
    comment_lines = []
    command_lines = []

    # iterate over each line in the command file and determine if it is a comment line, a blank line or a command line
    for line in command_file_lines:

        # comment line
        if line.startswith('#'):
            comment_lines.append(line)

        # blank line
        elif line == "":
            pass

        # command line
        else:
            command_lines.append(line)

    # return the comment_lines list and the command_lines list
    return comment_lines, command_lines

# command lines are made up of a command name and a parameter line ex: CommandName(parameterLine)
# return CommandName from command line, return None if the CommandName is not a registered command name
def command_line_to_command_name(command_line):
    """Parses the command_line and returns the CommandName

    :param command_line: A string, a command line in the following format --> CommandName(parameterLine)"""


    # remove white spaces on either side of the command line
    command_line = command_line.strip()

    # determine the index of the first parenthesis within the command line.
    paren_start = command_line.find("(")

    # get the command name from the command line (in front of the '(' symbol )
    command_name = command_line[:paren_start]

    # check that command name is a registered and valid command name. if so, return the command name
    if processor_utilities.is_command_name_valid(command_name):
        return command_name

    # if the command name is not registered with the command_dictionary, return Non and print an error message
    else:
        print "Invalid command name for {}".format(command_line)
        return None

# command lines are made up of a command name and a parameter line ex: CommandName(parameterLine)
# return the parameter line from the command line, return None if there are no parameters within the '()'
def command_line_to_parameter_line(command_line):
    """Parses the command_line and returns the parameter line.

    :param command_line: A string, a command line in the following format --> CommandName(parameterLine)"""

    # remove white spaces on either side of the command line
    command_line = command_line.strip()

    # determine the index of the first and last parenthesis within the command line string.
    paren_start = command_line.find("(")
    paren_end = command_line.find(")")

    # get the parameter line from the commmand line (in between the '(' symbol and the ')' symbol)
    parameter_line = command_line[paren_start + 1: paren_end]

    # check that there are available parameters. if so, return the parameter_line. else, return None
    if len(parameter_line) == 0:
        parameter_line = None
    return parameter_line

# parameter lines are made up of individual parameter strings (one string for each parameter)
# split parameter line into list of parameter strings and return parameter strings as a list
def parameter_line_to_parameter_strings(parameter_line):
    """Each command requires one to many parameters. The parameter line has all of the required parameter values
    entered by the user. Each parameter string is encapsulated in double quotes and separated from the following
    parameter by a comma. This function will parse the single string (the parameter line) into a list of many strings
    (each representing a difference parameter value).

    Example: [INPUT] parameterLine = '"firstParameter", "secondParameter", "thirdParameterName = thirdParameterValue"'
    [OUTPUT] parameter_strings = ['firstParameter', 'secondParameter', 'thirdParameterName = thirdParameterValue']

    :param parameter_line: A string, the sting inside the () of a command line that represents all of the input
    parameter values determined by the user"""

    # a list that will hold each of parameter strings
    parameter_strings = []

    # Boolean to determine if the current character should be part of a parameter string
    in_string = False

    # Boolean to determine if there is another character available after the current character
    next_char_exists = True

    # iterate over the characters in the parameter_line
    for char_index in range(len(parameter_line)):

        # get the current character
        current_char = parameter_line[char_index]

        # determine if the current character is the last character in the parameter_line
        if char_index + 1 == len(parameter_line):
            next_char_exists = False

        # get the next character
        else:
            next_char = parameter_line[char_index + 1]

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
            parameter_strings.append(current_parameter_string)

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
    return parameter_strings

# converts a parameter value in string format to a parameter value in list format
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
# return parameter value and, associated parameter name
def parameter_string_to_parameter_value(parameter_string, index_in_parameter_line, command_name):
    """A parameter line contains all of the parameter input values required for a command to run. Each parameter input
    value, determined by the user, is split by a comma. The parameter_line_to_parameter_strings command splits the
    parameter line into a list of multiple parameter strings (one for each parameter required by the class). This tool
    allows users to either enter just the input parameter value (in which the parameters must be entered in a specific
    order so that the parameter value can be mapped to the parameter name) or enter the parameter name = parameter
    value (in which the parameters do not need to be entered in a specific order because the parameter name is included
    within the parameter string). This function will return the parameter value and the associated parameter name
    given an input parameter string.

    :param parameter_string: A string, the parameter string split by the parameter_line_to_parameter_strings command
    :param index_in_parameter_line: An int, the index of this parameter_string in reference to the other parameter
    strings in the parameter line, starts at 0 (where 0 represents the first parameter string in the parameter line)
    :param command_name: A string, the name of the command that is to be called"""

    # the key, value format is determined by the inclusion of an equals sign
    if "=" in parameter_string:

        # the parameter name is on the left-side of the equals sign and the parameter value is on the right-side of the
        # equals sign
        parameter_name = (parameter_string.split('=')[0]).strip()
        parameter_value = (parameter_string.split('=')[1]).strip()

    # if there is no equals sign, then the parameter name is not included in the parameter string
    else:

        # gets a list of the command parameter names required by the command class being called
        command_parameter_names = processor_utilities.get_command_parameter_names(command_name)

        # if the parameter name is not included in the parameter string, the user must enter the parameter value in
        # the SAME ORDER as required by the command class. Given this fact, the parameter name can be retrieved by
        # getting the parameter name from the command class' parameter list at the same index as the current parameter
        # string is called in the parameter line. the parameter value is, then, the same as the parameter string.
        parameter_name = command_parameter_names[index_in_parameter_line]
        parameter_value = (parameter_string).strip()

    # all parameter strings are in the format of strings. some parameters, however, are required to by of the list type.
    # if the parameter value is to be a list (as indicated by the '[' symbol, then convert the parameter value (in
    # string format) to list format
    if parameter_value.startswith('['):

        parameter_value = parameter_value_string_to_list_format(parameter_value)

    # return the parameter value (either string or list) and the associated parameter name
    return parameter_value, parameter_name

# each parameter line (made up of parameter strings) has unique parameter values provided by the user
# this function converts a parameter string into a dictionary of unique parameter values related to parameter names
def parameter_strings_to_input_parameter_value_dic(parameter_strings, command_name):
    """A user is required to enter the required command parameter values. There are, however, some optional command
    parameter values. This function will map the users input command parameter values (required and optional, if
    included) to the corresponding parameter name. A dictionary of user-defined parameters (values are the parameter
    values and the keys are the corresponding parameter names) is returned from a list of parameter strings.

    :param parameter_string: A string, the parameter string split by the parameter_line_to_parameter_strings command
    :param command_name: A string, the name of the command that is to be called"""

    # this dictionary will hold each parameter value (that the user wrote to the command line) and its associated
    # parameter name. this is different from the dictionary retrieved from the
    # processor_utilities.get_command_parameter_values_dic command because that dictionary holds ALL possible
    # parameter names and values. This dictionary MIGHT NOT include the optional parameter names and values that are
    # ALWAYS included in the get_command_parameter_values_dic dictionary
    input_parameter_value_dic = {}

    # track the index of the current parameter string in relation to the other parameter strings in the parameter list
    # (represented here in list format as teh parameter_strings list)
    count = 0

    # iterate over each parameter string
    for parameter_string in parameter_strings:

        # get the parameter value and the associated parameter name from the parameter string. Add both to the
        # dictionary with the parameter name as the dictionary key and the parameter value as the dictionary value
        input_parameter_value, parameter_name = parameter_string_to_parameter_value(parameter_string, count,
                                                                                    command_name)
        input_parameter_value_dic[parameter_name] = input_parameter_value
        count += 1

    # return the dictionary
    return input_parameter_value_dic

# create a list of parameter values (ordered by the parameter name required by the command class). if an optional
# parameter value is not included in the original command line, this function will populate that optional parameter
# value (within the list) with the default parameter value (defined in the command class)
def map_input_parameter_values_to_parameter_list(input_parameter_value_dic, command_name):
    """In order for a command object to become instantiated properly, it requires a list of parameters. The list must
    be in the order of the class' pre-defined parameter list. This function takes a dictionary of user input parameter
    values (and associated parameter names as keys) and returns a list of parameter values in the order required by the
    command class.

    :param input_parameter_value_dic: A dictionary, dictionary of user-defined parameter values (dictionary values) and
    the corresponding parameter names (dictionary keys)
    :param command_name: the name of the command class that is being processed"""

    # a list that will hold the parameter values (both user-defined and default) for the command being called in order
    # required by tbe command class
    ordered_parameter_list = []

    # get the dictionary of parameters required by the command class (dictionary values, parameter values, will be set
    # to None for the required parameters and will be set to a value for the default parameters; dictionary keys are
    # the parameter names)
    command_parameter_values_dic = processor_utilities.get_command_parameter_values_dic(command_name)

    # get the ordered list of required and optional parameter names for the command class
    command_parameter_names = processor_utilities.get_command_parameter_names(command_name)

    # iterate through the each parameter name in the order required by the class
    for command_parameter_name in command_parameter_names:

        # if the user has defined the value for the parameter name, append the parameter value to ordered_parameter_list
        if command_parameter_name in list(input_parameter_value_dic.keys()):

            ordered_parameter_list.append(input_parameter_value_dic[command_parameter_name])

        # if the user has not defined the value for the parameter name, append the default parameter value defined by
        # the command's class
        else:

            ordered_parameter_list.append(command_parameter_values_dic[command_parameter_name])

    # return the ordered list of parameter values for the given command class
    return ordered_parameter_list

# given a command name and a complete and ordered list of parameter values, this function will initialize a command
# class object and run class' run_command function
def run_command(command_name, ordered_parameter_values):
    """Each command class requires a list of parameter values (in the same order as the list in the class' parameter
    name class variable. This function will initialize the called command with the user-defined parameters. It will
    run the run_command method within the class. This will complete that task that the command class was designed to
    complete.

    :param command_name: A string, the name of the command that is to be called
    :param ordered_parameter_values: A list, a list of the user-defined and default parameter values for the command
    class in the required order defined by the command class"""

    # notify user which command is currently running and the input parameter values
    print "Running {} with parameters {}".format(command_name, ordered_parameter_values)

    # initialize the command class
    command_instance = command_dictionary.command_dictionary[command_name](ordered_parameter_values)

    # run the command with the provided parameter values
    command_instance.run_command()

# this function will read a command file, parse the features of each command, and run the commands in sequential order
def process_command_file(path):
    """This is the main funciton call of the processor_main module. This function will initialize the QGIS environment,
    read a command file, parse the command file, run each command line of the command file, close the QGIS environment
    (once all of the command lines of the command file have been processed) and delete any of the temporary files
    created during the session process.

    :param path: A string, the full pathname to the command file that is to be run"""

    # Initialize QGIS resources to utilize QGIS functionality.
    QGISprefixPath = r"C:\OSGeo4W\apps\qgis"
    QgsApplication.setPrefixPath(QGISprefixPath, True)
    qgs = QgsApplication([], True)
    qgs.initQgis()
    Processing.initialize()

    # parse the command file into command lines and comment lines
    comment_lines, command_lines = read_command_file(path)

    # iterate through each command line (in sequential order)
    for command_line in command_lines:

        # parse the command line
        # get the command name of the command being called by the command line (validate that the command exists)
        # get the string representing the user-defined parameter values for the command
        command_name = command_line_to_command_name(command_line)
        parameter_line = command_line_to_parameter_line(command_line)

        # parse the parameter sting into a list of strings (each representing a separate parameter value)
        parameter_strings = parameter_line_to_parameter_strings(parameter_line)

        # create a dictionary of the user-defined parameter values (value) with the corresponding parameter names (key)
        input_parameter_value_dic = parameter_strings_to_input_parameter_value_dic(parameter_strings, command_name)

        # create a list of parameter values (both user-defined and default) in the order required by the class
        ordered_parameter_values = map_input_parameter_values_to_parameter_list(input_parameter_value_dic, command_name)

        # run the command with the user-defined and default parameter values
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

