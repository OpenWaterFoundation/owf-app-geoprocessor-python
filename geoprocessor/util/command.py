# Useful utility functions for the GeoProcessor.

# Don't import class only because there are additional functions in CommandParameterMetaData
import geoprocessor.core.CommandParameterMetadata as CommandParameterMetaData
from geoprocessor.core.CommandLogRecord import CommandLogRecord
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

def parse_command_name_from_command_string(command_string):
    """
    Parses the command name out of the command string.

    Args:
        command_string:  Full command string, may have leading whitespace.
    Returns:
        Command name.
    """

    # Remove white spaces on either side of the command string.
    command_string = command_string.strip()

    # Determine the index of the first parenthesis within the command string.
    paren_start_pos = command_string.find("(")

    # Get the command name from the command string (in front of the '(' symbol ).
    command_name = command_string[:paren_start_pos].strip()

    return command_name

def parse_key_value_pairs_into_dictionary(parameter_items):
    """
    Converts a list of Parameter=Value strings into
    a dictionary where the key is the parameter name and the value is the parameter value, as a string.

    Args:
        parameter_items: A list of parameter strings, each with format Parameter="Value"
    Returns:
        A dictionary where the key is the parameter name and value is the parameter value as a string.
    """

    # A dictionary that holds each parameter as an entry (key: parameter name, value: parameter value).
    parameter_dictionary = {}

    # Iterate over each item in the parameter items list.
    for parameter_item in parameter_items:

        # The key=value format is determined by the inclusion of an equals sign.
        # -Parameter values are expected to ALWAYS be surrounded by double quotes.
        #  TODO smalers 2017-12-23 need to revisit this because some parameters may need to escape.
        if "=" in parameter_item:
            # The parameter name is on the left-side of the equal sign and
            # the parameter value is on the right-side of the equal sign.
            # The parameter value is expected to be enclosed in double quotes.
            # The parameter value may include special characters such as '='.
            equal_pos = parameter_item.find('=')
            if ( equal_pos > 0 ):
                parameter_name = parameter_item[:equal_pos].strip()
                parameter_value = parameter_item[equal_pos + 1:].strip()
                # Remove the enclosing " from the parameter value, but allow " to remain within the parameter value.
                # Whitespace directly adjoining the surrounding " are not stripped.
                if ( parameter_value[0] == '"'):
                    parameter_value = parameter_value[1:]
                if ( parameter_value[len(parameter_value) - 1] == '"'):
                    parameter_value = parameter_value[:len(parameter_value) - 1]

                # Append the parameter name and the parameter value (in string or list format) to the parameter dictionary.
                parameter_dictionary[parameter_name] = parameter_value
            else:
                print "ERROR: the parameter ({}) is not in a proper 'Parameter=\"Value\"' format.".format(parameter_item)

        else:
            print "ERROR: the parameter ({}) is not in a proper 'Parameter=\"Value\"' format.".format(parameter_item)

    return parameter_dictionary

def parse_parameter_string_from_command_string(command_string):
    """
    Parses a command string to extract the parameter string between parentheses.
    For example, a command CommandName(Property1="Value1",Property2="Value2") would
    return: Property1="Value1",Property2="Value2"

    Args:
        command_string: The command string to parse.
    Return:
        Property1="Value1",Property2="Value2"
        An empty string may result if the command has no parameters.
    """

    # Remove white spaces on either side of the command line.
    command_string = command_string.strip()

    # Determine the index of the first and last parenthesis within the command line string.
    # - ( and ) are allowed in parameters if quoted, as determined in further parsing.
    paren_start_pos = command_string.find("(")
    # Find the right-most parenthesis in case one is included in the quoted part of the parameter value
    paren_end_pos = command_string.rfind(")")

    if ( (paren_start_pos <= 0) or (paren_end_pos != (len(command_string) - 1))):
        # Bounding parenthesis are not present.
        message = 'Invalid syntax for "' + command_string + '".  Expecting CommandName(Parameter="Value",...)'
        print(message)
        #Message.printWarning ( 2, routine, message);
        #throw new InvalidCommandSyntaxException ( message );

    # Get the parameter line from the command string (in between the '(' and the ')' ).
    parameter_string = command_string[paren_start_pos + 1: paren_end_pos]
    print("After parsing, parameter_string=" + parameter_string)
    return parameter_string

def parse_parameter_string_into_key_value_pairs(parameter_string):
    """
    Parse the parameter string part of a command into a list of Property=Value pairs.

    Example:
    [INPUT] parameter_string = Parameter1="Value1",Parameter2="Value2",...
    [OUTPUT] parameter_strings = ['Parameter1="Value1"', 'Parameter2="Value2"', ... ]

    Args:
        param parameter_string: The string inside the () of a command string that represents all of the input
        parameter values
    Returns:
        A list of parameter strings.
    """

    # The list of "Parameter=Value" strings, allowed to be an empty list.
    parameter_items = []

    print("Splitting full parameter string into pairs:  " + parameter_string)

    # Parse if the parameter line is not empty.
    if (len(parameter_string) > 0):

        # Boolean to determine if the current character is part of a quoted parameter value.
        in_quoted_string = False
        # Whether a comma is found after a parameter pair
        comma_found = False
        param_name_start_pos = -1
        param_value_end_pos = -1

        # Iterate over the characters in the parameter_string.
        for char_index in range(0,len(parameter_string)):

            # Get the current character.
            current_char = parameter_string[char_index]
            #print("Processing character '" + current_char + "'" )

            if not in_quoted_string:
                # Not in a quoted parameter value string.
                if current_char == '"':
                    # Start of a parameter value string.
                    in_quoted_string = True
                elif current_char == ' ':
                    # Whitespace, skip
                    pass
                elif current_char == ',':
                    # Found a comma between parameters
                    comma_found = True
                else:
                    # Assume that the character is the start of a parameter name
                    if ( param_name_start_pos < 0 ):
                        param_name_start_pos = char_index
                    # Error if there was not a comma found separating parameters
                    # (actually can handle as nonfatal but prefer commas for clarity).
                    if (len(parameter_items) > 0) and not comma_found:
                        # 2nd or greater parameter so need to have found a comma to separate parameters
                        print("ERROR:  Missing comma between parameter definitions")
                        comma_found = False
            else:
                # In a quoted parameter value string.
                if current_char == '"':
                    # Found the ending quote
                    in_quoted_string = False
                    param_value_end_pos = char_index
                    # Add the parameter string to the list
                    current_parameter_string = parameter_string[param_name_start_pos:param_value_end_pos+1]
                    print("Adding parameter item to list:  " + current_parameter_string)
                    parameter_items.append(current_parameter_string)
                    # Now reset for the next parameter
                    param_name_start_pos = -1

    # Return the list of parameter strings, may be empty.
    return parameter_items

def read_file_into_string_list(filename):
    """
    Convert a file into a list of strings (one string for each line of the file).

    Args:
        param: a string, the full pathname to a file
    Returns:
        A list of strings where each string corresponds to a line in the file.
    """

    # A list that will hold each string as a item in the list.
    string_list = []

    # Iterate over each line in the file and append the line as a string.
    # Retain indentation to allow formatting of the input.
    with open(filename) as file:
        content = file.readlines()
        for string in content:
            string_list.append(string)

    # Return the string list.
    return string_list

# converts a parameter value in string format to a parameter value in list format
def to_correct_format(parameter_value):
    """
    The command file (txt) only contains lines of strings. The parameter values within each command line, are,
    initially all string format. However, it is required that some parameter values be list format. This function
    converts a string parameter value to a list parameter value and returns the parameter value in list format.

    :param parameter_value: a parameter value in string format that is supposed to be in list format
    """

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

def validate_command_parameter_names ( command, warning, deprecated_parameter_names = None,
    deprecated_parameter_notes = None, remove_invalid = True ):
    """
    Validate that the parameter names parsed out of a command and saved in AbstractCommand.command_parmeters
    are recognized by the command.
    Any invalid parameters are indicated by appending to the warning message.
    This function is typically called by the command's check_command_parameters() function.
    This code is a port of the Java TSCommandProcessorUtil.validParameterNames and PropList.validatePropNames() methods.

    Args:
        command: The command to evaluate.
        warning: The multi-line warning message output by check_command_parameters() function.
            If not None, it will be appended to.
        deprecated_parameter_names List of string for parameter names that are deprecated (obsolete)
            (default is not to use).
        deprecated_parameter_notes Note for deprecated parameter names, for example to indicate new alternative
            (default is not to use).
        remove_invalid: Boolean indicating whether or not to remove invalid parameters from the command parameters
            (default is True, so as to not pollute the command with old parameter data).

    Returns:
        The updated warning argument, or a new string with the warning.

    Raises:
        ValueError if 1) the deprecated parameter names list size is not the same as the deprecated notes list size.

    """
    if command == None:
		return warning

	# Validate the properties and discard any that are invalid (a message will be generated)
	# and will be displayed once.
    # First generate a simple list of warnings, as per the Java PropList.validateParameterNames() method.
    warning_list = []

    # Get the sizes of the lists that will be iterated through, handling null lists gracefully.

    valid_parameter_names = CommandParameterMetaData.get_parameter_names(command.command_parameter_metadata)
    valid_parameter_names_size = len(valid_parameter_names)

    deprecated_parameter_names_size = 0
    if deprecated_parameter_names != None:
        deprecated_parameter_names_size = len(deprecated_parameter_names)

    # The size of the deprecated_notes list is computed in order to check that its size is the same as the
    # deprecated_parameters size.

    has_notes = False
    deprecated_notes_size = 0
    if deprecated_parameter_notes != None:
        deprecated_parameter_notes_size = len(deprecated_parameter_notes)
        has_notes = True

    if has_notes and deprecated_parameter_names_size != deprecated_parameter_notes_size:
        raise ValueError("The number of deprecated parameter names (" + deprecated_parameter_names_size +
            ") is not the same as the number of deprecated parameter notes (" + deprecated_parameter_notes_size + ")")

    # Iterate through all the parameter names for the command and check whether they are valid, invalid, or deprecated.

    # List of parameter names in each category.
    invalid_parameters = []
    deprecated_parameters = []

    # String used for messages.
    remove_invalid_string = ""
    if remove_invalid:
        remove_invalid_string = "  Removing the invalid parameter."

    # Cannot iterate through a dictionary and remove items from dictionary.
    # Therefore convert the dictionary to a list and iterate on the list
    command_parameter_names = list(command.command_parameters.keys())

    # Check size dynamically in case props are removed below
    # Because the dictionary size may change during iteration, can't do the following
    #for parameter_name, parameter_value in command.command_parameters.iteritems():
    # TODO smalers 2017-12-25 need to iterate with for to allow delete from the dictionary
    for i_parameter in range(0,len(command_parameter_names)):
        # First make sure that the parameter is in the valid parameter name list.
        # Parameters will only be checked for whether they are deprecated if they are not valid.
        valid = False
        # TODO smalers 2017-12-25 do the following because dictionary does not allow deletion in iterator
        parameter_name = command_parameter_names[i_parameter]

        for i_valid_parameter in range(0,valid_parameter_names_size):
            if valid_parameter_names[i_valid_parameter] == parameter_name:
                valid = True
                break

        if not valid:
            # Only check to see if the parameter name is in the deprecated list if it was not already found in
            # the valid parameter names list.

            for i_deprecated_parameter in range(0,deprecated_parameter_names_size):
                if deprecated_parameter_names[i_deprecated_parameter] == parameter_name:
                    msg = '"' + parameter_name + '" is no longer recognized as a valid parameter.' + remove_invalid_string
                    if has_notes:
                        msg = msg + "  " + deprecated_parameter_notes[i_deprecated_parameter]
                    deprecated_parameters.append(msg);

                    # Flag valid as True because otherwise this Property will also be reported
                    # as an invalid property below, and that is not technically true.
                    # Nor is it technically true that the property is valid, strictly-speaking,
                    # but this avoids double error messages for the same parameter.

                    valid = True
                    break

            # Add the error message for invalid properties.
            if not valid:
                invalid_parameters.append( '"' + parameter_name + '" is not a valid parameter.' + remove_invalid_string)

            if not valid and remove_invalid:
                # Remove the parameter from the dictionary and iterator list.  Also decrement the list.
                try:
                    del command.command_parameters[parameter_name]
                    del command_parameter_names[i_parameter]
                    --i_parameter
                    # Size of the dictionary will be checked in for statement,
                    # which will reflect the new list size
                except KeyError:
                    # Just absorb - should not happen
                    pass

    # Now add the warning messages to the list of strings
    for i_invalid in range(0,len(invalid_parameters)):
        warning_list.append(invalid_parameters[i_invalid])

    for i_deprecated in range(0,len(deprecated_parameters)):
        warning_list.append(deprecated_parameters[i_deprecated])

    if len(warning_list) == 0:
        # No new warnings were generated
        if warning != None:
            # Return the original warning string
            return warning
        else:
            # Return an empty string
            return ""
    else:
        # Some new warnings were generated.
        # Add a warning formatted for command logging and UI.
        # Multiple lines are indicated by embedded newline (\n) characters
		size = len(warning_list)
		msg = ""
		for i in range(0,size):
			warning += "\n" + warning_list[i]
			msg += warning_list[i]
        # TODO smalers 2017-12-25 All Python commands should use status, right?
		#    if ( command instanceof CommandStatusProvider ) {
		status = command.command_status
		status.add_to_log(command_phase_type.INITIALIZATION,
			CommandLogRecord.CommandLogRecord(command_status_type.WARNING, msg,
				"Specify only valid parameters - see documentation."))
    return warning
