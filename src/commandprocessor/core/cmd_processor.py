import os
from qgis.core import QgsApplication
from commandprocessor.core import abstractcommand
from commandprocessor.commands import qgis_commands, owf_commands
from processing.core.Processing import Processing

# A dictionary that relates a command's name (string) to its class. This dictionary is used to initialize a command
# class once the command's name have been read from the command file processor (process_command_file).
command_string_obj_dic = {"CreateLayerList": owf_commands.CreateLayerList,
                          "QgisClip": qgis_commands.QgisClip,
                          "ExportLayerList": owf_commands.ExportLayerList,
                          "QgisSimplifyGeometries": qgis_commands.QgisSimplifyGeometries,
                          "QgisExtractByAttributes": qgis_commands.QgisExtractByAttributes,
                          "EditLayerList": owf_commands.EditLayerList}

# Reads a command file (.txt) and returns a list with each line of the command file (command line) as an item
def read_command_file(path):
    """Converts a text file to a list with each line (each command) as a separate item in the content list.
    Returns the list of lines.

    :param path: A string, the full pathname to the input command file"""

    with open(path) as command_file:
        content = command_file.readlines()
        content = [x.strip() for x in content]

    return content

# Converts the string format of an input parameter value (when in key:value format) into input parameter value and index of that parameter
def parse_parameter_string_key_value(parameter_string, parameter_names):
    """The user has the option to input parameter values in a command line with either just the parameter value (in
    the correct order required by the command class) or they can use key=value format where the parameter name (key)
    is written out followed by an (=) sign and then the parameter value. This function will parse a parameter string
    if it is in the key=value format. It will return the parameter value and the index of that parameter in reference
    to the command class' list of parameters.

    :param parameter_string: A string, a parameter string in key=value format
    :param parameter_names: A list, the parameter names in order required by the command class"""

    # the parameter name is set on the left side of the = sign whereas the parameter value is set on the right side
    # of the = sign
    parameter_string_name = (parameter_string.split('=')[0]).strip()
    parameter_string_value = (parameter_string.split('=')[1]).strip()

    # get the index of the parameter in reference to the command class' ordered parameter list
    parameter_index = parameter_names.index(parameter_string_name)

    return parameter_string_value, parameter_index

# Converts the string format of the parameter values into a list (containing strings and lists, if required)
def parse_parameter_string(parameter_string, command_name):
    """The command file (txt) only contains lines of strings. The parse function will convert the string
    representation of the parameter list into an actual list (each item containing a parameter value). If a parameter
    value requires list format, this function will convert the parameter value string into a parameter value list.

    :param parameter_string: A string, the parameter values of a command line (the parameter value string
    is located within the parenthesis of a command line string.
    :param command_name: A string, the name of the command called upon in the command string"""

    # a list that will hold each parameter value as a separate item
    parameter_list = []
    parameter_dic = {}

    # parses the entire parameter string into separate strings (each representing a parameter value). these parsed
    # strings are included as items in the list, string_list. Note that parameter values that are required to be lists
    # will still be represented as strings in this format.
    string_list = break_parameter_string(parameter_string)

    # get the order of the command class' parameter names
    parameter_names = command_string_obj_dic[command_name].parameter_names
    parameter_values = command_string_obj_dic[command_name].parameter_values
    num_parameters = len(parameter_names)

    # a count that determines which input parameter value (string format) is being processed
    count = 0

    # iterate through each parameter value (string format) of the string_list
    for string in string_list:

        # if the string is just a parameter value without a parameter name (without a key = value format)
        if "=" not in string:

            parameter_value = string
            parameter_index = count

        # if the parameter string is in the format key = value
        else:

            # split the key, value pair and return the parameter value and the parameter index of the parameter name
            #  in the specified command class
            parameter_value, parameter_index = parse_parameter_string_key_value(string, parameter_names)

        # if the parameter value is supposed to be a list, convert the parameter value string into list format
        if parameter_value.startswith('['):
            parameter_value = parameter_string_to_list(parameter_value)

        # add the input parameter value in the correct order in reference to the expected command class parameter order
        parameter_dic[parameter_index] = parameter_value
        # parameter_list.insert(parameter_index, parameter_value)

        count += 1

    # iterate over each parameter required by the command class (in expected order)
    for parameter_index in range(0, num_parameters):

        # if there is an input parameter value for the current parameter, then append that input parameter to the
        # parameter list
        if parameter_index in list(parameter_dic.keys()):
            parameter_list.append(parameter_dic[parameter_index])

        # if there is not an input parameter value for the current parameter, then append the default parameter value
        #  to the parameter list (as defined in the command class)
        else:
            parameter_list.append(parameter_values[parameter_names[parameter_index]])

    # return a list with each parameter value as an item. the items will be in string AND list format, if required.
    return parameter_list

# Converts a parameter value in string format to a parameter value in list format
def parameter_string_to_list(parameter_string):
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

# Converts a parameter_string into a list of strings (each string represents one parameter value)
def break_parameter_string(string):
    """The parameter values are originally parsed so that ALL parameter values are included in ONE string. Each
    parameter value is enclosed in double quotes (") and is separated from the next parameter value by a comma (').
    This function will take a single parameter value string and will split the string into multiple strings where each
    string represents one parameter value. These output strings will be items in the split_list list. The split_list
    list is returned.

        :param string: A string, a single string representing ALL parameter values from a command line"""

    # a list that will hold each of the parameter values as items (in string format)
    split_list = []

    # Boolean to determine if the current character should be part of the output string
    in_string = False

    # Boolean to determine if there is another character available after the current character
    next_char_exists = True

    # iterate over the characters in the input string
    for char_index in range(len(string)):
        current_char = string[char_index]

        # determine if this is the last character in the input string
        if char_index + 1 == len(string):
            next_char_exists = False
        else:
            next_char = string[char_index + 1]

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
            split_list.append(entry_string)

        # if the character is not a (") and there is currently a string defined, then add this character to the
        # entry list. The entry list will collect all of the characters within each string.
        elif in_string:
            entry.append(current_char)

        # if the current character is not a (") and there is not currently a string defined, then
        # skip this character without adding it to the entry list or changing the status of the in_string variable
        else:
            pass

    # return the list of parameter values (in string format)
    return split_list

# Parses a single command line (string). Returns the command name and the parameter values (list of strings and lists)
def parse_command(command_string):
    """The command file is made up of lines of string. This function will read and parse a string line. It will output
    the command name and the parameter values (list of strings and lists) associated with the original command line.

    :param command_string: A string, a single line of a command .txt file"""

    # Remove whitespaces on either side of the command line
    command_trimmed = command_string.strip()

    # If the command line is a comment, return None values for the command name and the parameter_values list
    if command_trimmed.startswith('#'):
        command_name = None
        parameter_values = None

    # If the command line is an actual command line
    else:

        # Determine the index of the first and last parenthesis within the command line string. All command lines
        # should have an opening and closing parenthesis.
        paren_start = command_trimmed.find("(")
        paren_end = command_trimmed.find(")")

        # get command name
        command_name = command_trimmed[:paren_start]

        # throw error if there are missing open or closing parethesis
        if not (paren_start or paren_end):

            print "Syntax Error: (must include open and closed parenthesis) within command {}".format(command_string)

        # get the section of the string that represents the parameter values (within the parenthesis)
        parameter_string = command_trimmed[paren_start + 1: paren_end]

        # if there are parameters to parse, convert the string of parameters into the parameter_values list (made up of
        # strings and lists, if required). Otherwise assign the parameter_values list to None.
        if len(parameter_string) > 0:
            parameter_values = parse_parameter_string(parameter_string, command_name)
        else:
            parameter_values = None

    # Return the command name (string foramt) and the paramter_values list (list of strings and lists, if required)
    return command_name, parameter_values

# Initializes and runs a single command
def process_command(command_name, parameter_values):
    """Given a command name and a list of input parameter values, this function will initialize a command class and run
    the instance of the class with the input parameters.

    :param command_name: A string, the name of a command, must correspond to a key in the command_string_obj_dic
    :param parameter_values: A list, a list of command parameter values required to run the called command"""

    # notify user which command is currently running
    print "Running {} with parameters {}".format(command_name, parameter_values)

    # initialize the command class
    command_instance = command_string_obj_dic[command_name](parameter_values)

    # run the command with the provided parameter values
    command_instance.run_command()

# Reads a command file (.txt), parses the command lines and runs the commands (in sequence)
def process_command_file(path):
    """The command processor. This function will read the input command file and will process the commands entered
    within the command file (with the specified parameters). It will start and close the QGIS environment.

    :param path: A string, the full pathname to the input command file"""

    # Initialize QGIS resources to utilize QGIS functionality.
    QGISprefixPath = r"C:\OSGeo4W\apps\qgis"
    QgsApplication.setPrefixPath(QGISprefixPath, True)
    qgs = QgsApplication([], True)
    qgs.initQgis()
    Processing.initialize()

    # Read command file (.txt) and returns each line of the command file (command line) as an item
    command_lines = read_command_file(path)

    # Iterate over each line of the command file (string format)
    for line in command_lines:

        # parse the command line and return the command name (string) and the parameter values (list of strings and lists)
        command_name, parameter_values = parse_command(line)

        # only continue if there is a command_name and a list of parameter values
        if command_name and parameter_values:
            # initialize and run the command given the parameter values
            process_command(command_name, parameter_values)

    # Close QGIS resources
    qgs.exit()

    # Remove any intermediate files from temporary folder that were created during the session
    temp_folder = abstractcommand.AbstractCommand.temp_folder
    for file in os.listdir(temp_folder):
        os.remove(os.path.join(temp_folder, file))


####################### WORKING ENVIRONMENT ###############################


# parse_parameter_string_key_value("layer_list_id = 'fema'", "ExportLayerList")


curr_directory = os.path.dirname(os.path.realpath(__file__))
cmdFileDir = curr_directory.replace("commandprocessor\core", "command_files")
process_command_file(os.path.join(cmdFileDir, "exampleCmdFile.txt"))
