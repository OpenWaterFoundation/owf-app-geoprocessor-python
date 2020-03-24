# command_util - useful utility functions for the GeoProcessor
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

# Don't import class only because there are additional functions in CommandParameterMetaData
import geoprocessor.core.CommandParameterMetadata as CommandParameterMetaData

# TODO smalers 2020-01-14 can't import for type hint because it results in circular reference
# from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatus import CommandStatus
from geoprocessor.core.CommandStatusType import CommandStatusType
# from geoprocessor.core.GeoProcessor import GeoProcessor

import logging


def append_command_status_log_records(command_status: CommandStatus, commands: []) -> None:
    """
    Append log records from a list of commands to a status.  For example, this is used
    when running a list of commands with a "runner" command like RunCommands to get a full list of logs.
    The command associated with the individual logs is set to the original command so that
    the "runner" is not associated with the log.

    Args:
        command_status (CommandStatus):  CommandStatus object for a command.
        commands: List of Command from which to get commands status.

    Returns:
        None.
    """
    if command_status is None:
        return

    if commands is None:
        return

    # Loop through the commands
    for command in commands:
        # Transfer the command log records from each command to the given command_status.
        status2 = command.command_status
        # Append command log records for each run mode...
        # logs = status2.get_command_log(CommandPhaseType.INITIALIZATION)
        logs = status2.initialization_log_list
        for log_record in logs:
            # log_record.setCommandStatusProvider(csp)
            command_status.add_to_log(CommandPhaseType.INITIALIZATION, log_record)
        # logs = status2.get_command_log(CommandPhaseType.DISCOVERY)
        logs = status2.discovery_log_list
        for log_record in logs:
            # log_record.setCommandStatusProvider(csp);
            command_status.add_to_log(CommandPhaseType.DISCOVERY, log_record)
        # logs = status2.getCommandLog(CommandPhaseType.RUN)
        logs = status2.run_log_list
        for log_record in logs:
            # logRecord.setCommandStatusProvider(csp);
            command_status.add_to_log(CommandPhaseType.RUN, log_record)


# TODO smalers 2020-01-15 cannot type hint GeoProcessor becauese it results in circular dependence with import
def get_command_status_max_severity(processor) -> CommandStatusType:
    """
    Get the maximum command status severity for the processor.  This is used, for example, when
    determining an overall status for a RunCommands() command.

    Args:
        processor:  Command processor, needed to get all commands.

    Returns:
        Most severe command status from all commands in a processor.
    """
    most_severe_command_status = CommandStatusType.UNKNOWN
    for command in processor.commands:
        status_from_command = get_highest_command_status_severity(command.command_status)
        # Message.printStatus (2,"", "Highest severity \"" + command.toString() + "\"=" + from_command.toString());
        most_severe_command_status = CommandStatusType.max_severity(most_severe_command_status, status_from_command)
    return most_severe_command_status


def get_highest_command_status_severity(command_status: CommandStatusType) -> CommandStatusType:
    """
    Returns the highest status severity of all phases, to indicate the most severe problem with a command.

    Args:
        command_status (CommandStatus):  Command status object.

    Returns:
        the highest status severity of all phases, to indicate the most severe problem with a command.
    """
    status_severity = CommandStatusType.UNKNOWN
    if command_status is None:
        return status_severity  # Default is UNKNOWN

    # Python 2 does not have enumerations like Java code so do comparisons brute force
    phase_status = command_status.get_command_status_for_phase(CommandPhaseType.INITIALIZATION)
    if phase_status is None:
        phase_status = CommandStatusType.UNKNOWN
    if phase_status.value > status_severity.value:
        status_severity = phase_status

    phase_status = command_status.get_command_status_for_phase(CommandPhaseType.DISCOVERY)
    if phase_status is None:
        phase_status = CommandStatusType.UNKNOWN
    if phase_status.value > status_severity.value:
        status_severity = phase_status

    phase_status = command_status.get_command_status_for_phase(CommandPhaseType.RUN)
    if phase_status is None:
        phase_status = CommandStatusType.UNKNOWN
    # TODO sam 2017-04-13 This can be problematic if the discovery mode had a warning or failure
    # and run mode was success.  This may occur due to dynamic files being created, etc.
    # The overall status in this case should be success.
    # Need to evaluate how this method gets called and what intelligence is used.
    if phase_status.value > status_severity.value:
        status_severity = phase_status

    return status_severity


def get_required_parameter_names(command) -> list:
    """
    Examine the command.parameter_input_metadata list and return parameter names for *.Required = True instances.
    This is used, for example, when checking command parameters to make sure that required parameters have values.

    Args:
        command (AbstractCommand):  Command instance derived from AbstractCommand.

    Returns:
        list(str):  Name of parameters that are required for the command.
    """
    required_parameter_names = []
    if command is None:
        # Null input so return an empty list
        return required_parameter_names

    # Loop through all parameter names because input metadata may not be defined for all
    for command_parameter_metadata in command.command_parameter_metadata:
        parameter_name = command_parameter_metadata.parameter_name
        # Check that the ParameterName.Required input metadata is defined
        try:
            # Loop
            required_value = command.parameter_input_metadata[parameter_name + '.Required']
            if required_value:
                # Parameter is confirmed to be required so add to the return list
                required_parameter_names.append(parameter_name)
        except KeyError:
            # Input is not defined so use default of optional
            pass

    return required_parameter_names


def parse_command_name_from_command_string(command_string: str) -> str:
    """
    Parses the command name out of the command string.
    Strings are of format:

        CommandName()
        CommandName

    Args:
        command_string:  Full command string, may have leading whitespace.

    Returns:
        Command name.
    """

    # Remove white spaces on either side of the command string.
    command_string = command_string.strip()

    # Determine the index of the first parenthesis within the command string.
    paren_start_pos = command_string.find("(")

    if paren_start_pos > 0:
        # Get the command name from the command string (in front of the '(' symbol ).
        command_name = command_string[:paren_start_pos].strip()
    else:
        # Assume just the command name, used in factory
        command_name = command_string.strip()

    return command_name


def parse_key_value_pairs_into_dictionary(parameter_items: [str]) -> dict:
    """
    Converts a list of Parameter=Value strings into
    a dictionary where the key is the parameter name and the value is the parameter value, as a string.

    Args:
        parameter_items: A list of parameter strings, each with format Parameter="Value"
    Returns:
        A dictionary where the key is the parameter name and value is the parameter value as a string.
    """
    logger = logging.getLogger(__name__)

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
            if equal_pos > 0:
                parameter_name = parameter_item[:equal_pos].strip()
                parameter_value = parameter_item[equal_pos + 1:].strip()
                # Remove the enclosing " from the parameter value, but allow " to remain within the parameter value.
                # Whitespace directly adjoining the surrounding " are not stripped.
                if parameter_value[0] == '"':
                    parameter_value = parameter_value[1:]
                if parameter_value[len(parameter_value) - 1] == '"':
                    parameter_value = parameter_value[:len(parameter_value) - 1]

                # Append the parameter name and the parameter value (in string or list format) to the
                # parameter dictionary.
                parameter_dictionary[parameter_name] = parameter_value
            else:
                logger.warning("The parameter ({}) is not in a proper 'Parameter=\"Value\"' format.".format(
                    parameter_item))

        else:
            logger.warning("The parameter ({}) is not in a proper 'Parameter=\"Value\"' format.".format(parameter_item))

    return parameter_dictionary


def parse_parameter_string_from_command_string(command_string: str) -> str:
    """
    Parses a command string to extract the parameter string between parentheses.
    For example, for a full command string:

        CommandName(Parameter1="Value1",Parameter2="Value2") would

    return: Parameter1="Value1",Parameter2="Value2"

    Return an empty string if no parameters or just the command name.

    Args:
        command_string: The command string to parse.

    Return:
        Parameter1="Value1",Parameter2="Value2"
        An empty string is returned if the full command string has no parameters.

    Raises:
        ValueError if the command syntax is invalid.
    """

    # Remove white spaces on either side of the command line.
    command_string_stripped = command_string.strip()

    # Determine the index of the first and last parenthesis within the command line string.
    # - ( and ) are allowed in parameters if quoted, as determined in further parsing.
    paren_start_pos = command_string_stripped.find("(")
    if paren_start_pos < 0:
        # No parameters so return an empty string
        return ""
    # Find the right-most parenthesis in case one is included in the quoted part of the parameter value
    paren_end_pos = command_string_stripped.rfind(")")

    if (paren_start_pos <= 0) or (paren_end_pos != (len(command_string_stripped) - 1)):
        # Bounding parenthesis are not present.
        # - expecting somewhere on left and in last position on the right
        message = 'Invalid syntax for "' + command_string + '".  Expecting CommandName(Parameter="Value",...)'
        # Get logger her instead of top to increase performance, but can move it
        logger = logging.getLogger(__name__)
        logger.warning(message)
        raise ValueError(message)

    # Get the parameter line from the command string (in between the '(' and the ')' ).
    parameter_string = command_string_stripped[paren_start_pos + 1: paren_end_pos]
    # Strip enclosing whitespace
    parameter_string = parameter_string.strip()
    return parameter_string


def parse_parameter_string_into_key_value_pairs(parameter_string: str, delimiter: str = ",") -> [str]:
    """
    Parse the parameter string part of a command into a list of Property=Value pairs.

    Example:
    [INPUT] parameter_string = Parameter1="Value1",Parameter2="Value2",...
    [OUTPUT] parameter_strings = ['Parameter1="Value1"', 'Parameter2="Value2"', ... ]

    Args:
        parameter_string (str):
            The string inside the () of a command string that represents all of the input parameter values.
        delimiter (str):
            The delimiter character between pameter="value" strings.
    Returns:
        A list of 'parameter=value' strings.
    """
    logger = logging.getLogger(__name__)

    # The list of "Parameter=Value" strings, allowed to be an empty list.
    parameter_items = []

    # print("Splitting full parameter string into pairs:  " + parameter_string)

    # Parse if the parameter line is not empty.
    if len(parameter_string) > 0:

        # Boolean to determine if the current character is part of a quoted parameter value.
        in_quoted_string = False
        # Whether a comma is found after a parameter pair
        comma_found = False
        param_name_start_pos = -1
        # param_value_end_pos = -1

        # Iterate over the characters in the parameter_string.
        for char_index in range(0, len(parameter_string)):

            # Get the current character.
            current_char = parameter_string[char_index]
            # print("Processing character '" + current_char + "'" )

            if not in_quoted_string:
                # Not in a quoted parameter value string.
                if current_char == '"':
                    # Start of a parameter value string.
                    # - TODO smalers 2018-12-17 need to evaluate whether to allow escaping double quote
                    in_quoted_string = True
                elif current_char == ' ':
                    # Whitespace, skip
                    pass
                elif current_char == delimiter:
                    # Found a delimiter between parameters
                    comma_found = True
                else:
                    # Assume that the character is the start of a parameter name
                    if param_name_start_pos < 0:
                        param_name_start_pos = char_index
                    # Error if there was not a comma found separating parameters
                    # (actually can handle as nonfatal but prefer commas for clarity).
                    if (len(parameter_items) > 0) and not comma_found:
                        # 2nd or greater parameter so need to have found a comma to separate parameters
                        logger.warning("Missing comma between parameter definitions")
                        comma_found = False
            else:
                # In a quoted parameter value string.
                if current_char == '"':
                    # Found the ending quote
                    in_quoted_string = False
                    param_value_end_pos = char_index
                    # Add the parameter string to the list
                    current_parameter_string = parameter_string[param_name_start_pos:param_value_end_pos+1]
                    # print("Adding parameter item to list:  " + current_parameter_string)
                    parameter_items.append(current_parameter_string)
                    # Now reset for the next parameter
                    param_name_start_pos = -1

    # Return the list of parameter strings, may be empty.
    return parameter_items


def parse_properties_from_parameter_string(properties_string: str, delimiter1: str = ",",
                                           delimiter2: str = ":") -> dict:
    """
    Parses a command parameter string containing properties, where values are optionally surrounded by single quotes:

        Property1=Value1,Property2=Value2) would
        Property1='Value1',Property2='Value2')

    return: Property1="Value1",Property2="Value2"
    Return an dictionary of the parsed properties, may be an empty dictionary.

    Args:
        properties_string (str): The command string to parse.
        delimiter1 (str): Delimiter between properies, defaults to ",".
        delimiter2 (str): Delimiter between property and value, defaults to ":".

    Return:
        Dictionary of the parsed properties.

    Raises:
        ValueError if the command syntax is invalid.
    """
    debug = False   # Use to troubleshoot code but not production
    logger = None
    if debug:
        logger = logging.getLogger(__name__)

    # The list of "Parameter=Value" strings, allowed to be an empty list.
    properties_dict = dict()

    if properties_string is None:
        return properties_dict

    # Remove white spaces on either side of the command line.
    properties_string_stripped = properties_string.strip()

    # print("Splitting full properties string into pairs:  " + properties_string)

    # Parse if the properties string is not empty.
    if len(properties_string_stripped) > 0:
        # Boolean to determine if the current character is part of a quoted property value.
        in_quoted_string = False  # Used for property value
        in_property_name = True  # To start processing - first character should be a non-special character
        in_property_value = False
        property_name = ""
        property_value = ""

        # Iterate over the characters in the properties_string.
        # - the state is either in_property_name or in_property_value
        last_index = len(properties_string_stripped) - 1
        for char_index in range(0, len(properties_string_stripped)):
            # Get the current character.
            current_char = properties_string[char_index]
            if debug:
                logger.debug("Processing '" + current_char + "' property_name='" + property_name +
                             "' property_value='" + property_value + "' in_property_name=" + str(in_property_name) +
                             " in_property_value=" + str(in_property_value))

            if current_char == ' ':
                if in_property_name:
                    # Skip - auto compress property names
                    pass
                elif in_property_value:
                    # Spaces are allowed in the value if quoted, otherwise skip
                    if in_quoted_string:
                        property_value += current_char
                    else:
                        pass
            elif current_char == delimiter1:
                # Typically a comma, which separates properties
                if in_property_name:
                    raise ValueError("Unexpected delimiter ({}) found at character {}, "
                                     "maybe need to surround property value with ' '.".format(delimiter1,
                                                                                              (char_index + 1)))
                elif in_property_value:
                    # Delimiters are allowed in the value if quoted, otherwise, end of value
                    if in_quoted_string:
                        property_value += current_char
                    else:
                        # Add the property
                        if debug:
                            logger.debug('Found comma in value, adding property ' + property_name + "=" +
                                         property_value)
                        properties_dict[property_name] = property_value
                        # Reset for the next property
                        in_property_name = False
                        property_name = ""
                        in_property_value = False
                        property_value = ""
                else:
                    # Transitioning from previous property
                    in_property_name = True
            elif current_char == delimiter2:
                # Typically colon, which separates property name and value
                if in_property_name:
                    # Ignore the character and start processing the property value
                    in_property_name = False
                    in_property_value = True
                elif in_property_value:
                    # Delimiters are allowed in the value if quoted, otherwise bad format
                    if in_quoted_string:
                        property_value += current_char
                    else:
                        raise ValueError("Unexpected delimiter ({}) found at character {}, "
                                         "maybe need to surround property value with ' '".format(delimiter2,
                                                                                                 (char_index + 1)))
            elif current_char == "'":
                # Single quotes optionally surround the property value.
                if in_property_name:
                    raise ValueError("Unexpected character (') found at character {}, bad property definition.".
                                     format((char_index + 1)))
                elif in_property_value:
                    if in_quoted_string:
                        # In a quoted string so this indicates the end of the property value
                        properties_dict[property_name] = property_value
                        # Reset for next property
                        in_property_name = False
                        property_name = ""
                        in_property_value = False
                        property_value = ""
                        # Close the quoted string
                        in_quoted_string = False
                    else:
                        # Not yet in a quoted string so start
                        in_quoted_string = True
                else:
                    # Single quote should not start a new property name
                    raise ValueError("Unexpected character (') found at character {}, bad property definition.".
                                     format((char_index + 1)))
            else:
                # Non-special character to add to property name or value.
                if in_property_name:
                    # Add the character to the property name
                    property_name += current_char
                elif in_property_value:
                    # Add the character to the property value
                    property_value += current_char
                else:
                    # Not in property name or value.
                    # - between properties so start the property name
                    in_property_name = True
                    property_name += current_char

            if char_index == last_index:
                # Last character from input string.
                # - close out the last un-quoted property value
                # - loop will exit normally
                if current_char != "'":
                    properties_dict[property_name] = property_value

    # Return the list of parameter strings, may be empty.
    return properties_dict


def read_file_into_string_list(filename: str) -> [str]:
    """
    Convert a file into a list of strings (one string for each line of the file).

    Args:
        filename (str): the full pathname to a file to read.

    Returns:
        A list of strings where each string corresponds to a line in the file.
    """

    # A list that will hold each string as a item in the list.
    string_list = []

    # Iterate over each line in the file and append the line as a string.
    # Retain indentation to allow formatting of the input.
    with open(filename) as infile:
        content = infile.readlines()
        for string in content:
            string_list.append(string)

    # Return the string list.
    return string_list


def validate_command_parameter_names(command, warning_message: str, deprecated_parameter_names: [str] = None,
                                     deprecated_parameter_notes: [str] = None, remove_invalid: bool = True) -> str:
    """
    Validate that the parameter names parsed out of a command and saved in AbstractCommand.command_parameters
    are recognized by the command.
    Any invalid parameters are indicated by appending to the warning message that is returned.
    A command status log message is also added.
    This function is typically called by the command's check_command_parameters() function.
    This code is a port of the Java TSCommandProcessorUtil.validParameterNames and PropList.validatePropNames() methods.

    Args:
        command: The command to evaluate.
        warning_message: The multi-line warning message output by check_command_parameters() function.
            If not None, it will be appended to.
        deprecated_parameter_names: List of string for parameter names that are deprecated (obsolete)
            (default is not to use).
        deprecated_parameter_notes: Note for deprecated parameter names, for example to indicate new alternative
            (default is not to use).
        remove_invalid: Boolean indicating whether or not to remove invalid parameters from the command parameters
            (default is True, so as to not pollute the command with old parameter data).

    Returns:
        The updated warning string, or a new string with the warning.

    Raises:
        ValueError if 1) the deprecated parameter names list size is not the same as the deprecated notes list size.

    """
    if command is None:
        return warning_message

    # Validate the properties and discard any that are invalid (a message will be generated)
    # and will be displayed once.
    # First generate a simple list of warnings, as per the Java PropList.validateParameterNames() method.
    warning_list = []

    # Get the sizes of the lists that will be iterated through, handling null lists gracefully.

    valid_parameter_names = CommandParameterMetaData.get_parameter_names(command.command_parameter_metadata)
    valid_parameter_names_size = len(valid_parameter_names)

    deprecated_parameter_names_size = 0
    if deprecated_parameter_names is not None:
        deprecated_parameter_names_size = len(deprecated_parameter_names)

    # The size of the deprecated_notes list is computed in order to check that its size is the same as the
    # deprecated_parameters size.

    has_notes = False
    deprecated_parameter_notes_size = 0
    if deprecated_parameter_notes is not None:
        deprecated_parameter_notes_size = len(deprecated_parameter_notes)
        has_notes = True

    if has_notes and (deprecated_parameter_names_size != deprecated_parameter_notes_size):
        raise ValueError("The number of deprecated parameter names (" + str(deprecated_parameter_names_size) +
                         ") is not the same as the number of deprecated parameter notes (" +
                         str(deprecated_parameter_notes_size) + ")")

    # Iterate through all the parameter names for the command and check whether they are valid, invalid, or deprecated.

    # List of parameter names in each category.
    invalid_parameter_messages = []
    invalid_parameters = []
    deprecated_parameter_messages = []

    # String used for messages.
    remove_invalid_string = ""
    if remove_invalid:
        remove_invalid_string = "  Removing the invalid parameter."

    # Cannot iterate through a dictionary and remove items from dictionary.
    # Therefore convert the dictionary to a list and iterate on the list
    command_parameter_names = list(command.command_parameters.keys())

    # Check size dynamically in case props are removed below
    # Because the dictionary size may change during iteration, keep a list of invalid parameters and delete in 2nd loop.
    for i_parameter in range(len(command_parameter_names)):
        # First make sure that the parameter is in the valid parameter name list.
        # Parameters will only be checked for whether they are deprecated if they are not valid.
        valid = False
        # Do the following because dictionary does not allow deletion in iterator.
        parameter_name = command_parameter_names[i_parameter]

        for i_valid_parameter in range(0, valid_parameter_names_size):
            if valid_parameter_names[i_valid_parameter] == parameter_name:
                valid = True
                break

        if not valid:
            # Only check to see if the parameter name is in the deprecated list if it was not already found in
            # the valid parameter names list.

            for i_deprecated_parameter in range(deprecated_parameter_names_size):
                if deprecated_parameter_names[i_deprecated_parameter] == parameter_name:
                    msg = '"' + parameter_name + '" is no longer recognized as a valid parameter.' + \
                          remove_invalid_string
                    if has_notes:
                        msg = msg + "  " + deprecated_parameter_notes[i_deprecated_parameter]
                    deprecated_parameter_messages.append(msg)

                    # Flag valid as True because otherwise this Property will also be reported
                    # as an invalid property below, and that is not technically true.
                    # Nor is it technically true that the property is valid, strictly-speaking,
                    # but this avoids double error messages for the same parameter.

                    valid = True
                    break

            # Add the error message for invalid properties.
            if not valid:
                invalid_parameter_messages.append('"' + parameter_name + '" is not a valid parameter.' +
                                                  remove_invalid_string)

            if not valid and remove_invalid:
                # Keep a list of indices for invalid parameters so that the items can be removed from the dictionary.
                invalid_parameters.append(parameter_name)

    if remove_invalid:
        # Have a list of index positions to remove
        for invalid_parameter in invalid_parameters:
            try:
                del command.command_parameters[invalid_parameter]
            except KeyError:
                # Just absorb - should not happen since the parameter name was from the dictionary
                pass

    # Now add the warning messages to the list of strings
    # - these are full messages formatted above, not just lists of parameter names
    for i_invalid in range(len(invalid_parameter_messages)):
        warning_list.append(invalid_parameter_messages[i_invalid])

    for i_deprecated in range(len(deprecated_parameter_messages)):
        warning_list.append(deprecated_parameter_messages[i_deprecated])

    if len(warning_list) == 0:
        # No new warnings were generated
        if warning_message is not None:
            # Return the original warning string
            return warning_message
        else:
            # Return an empty string
            return ""
    else:
        # Some new warnings were generated.
        # Add a warning formatted for command status logging and UI.
        # Multiple lines are indicated by embedded newline (\n) characters
        size = len(warning_list)
        msg = ""
        for i in range(size):
            warning_message += "\n" + warning_list[i]
            msg += warning_list[i]
        # Add a command status log message for the warning messages that were generated
        command.command_status.add_to_log(
            CommandPhaseType.INITIALIZATION,
            CommandLogRecord(CommandStatusType.WARNING, msg, "Specify only valid parameters - see documentation."))
    return warning_message


# TODO smalers 2020-03-16 this code is experimental - need to figure out better way to implement validation.
def validate_geolayer_attributes_exist(command, command_phase_type: CommandPhaseType,
                                       command_status_type: CommandStatusType, geolayerid_parameter: str,
                                       geolayer_id: str, attributes: [str],
                                       logger: logging.Logger = None) -> ():
    """
    Check that the attributes exist in a GeoLayer's attribute table.

    Args:
        command:  Command being processed.
        command_phase_type:  The CommandPhaseType for command log record.
        command_status_type:  The CommandStatusType for command log record.
        geolayerid_parameter:  Parameter name that provides value for 'geolayer_id'.
        geolayer_id:  GeoLayerID for layer to check.
        attributes:  List of attribute names to check for.
        logger:  If not None, log a message.

    Returns:
        Tuple of (is_valid, warning_count, message), where
    """

    # Get the GeoLayer.
    geolayer = command.command_processor.get_geolayer(geolayer_id)

    # Get the existing attribute names of the input GeoLayer.
    list_of_existing_attributes = geolayer.get_attribute_field_names()

    # Create a list of invalid input attribute names.
    # An invalid attribute name is an input attribute name that does not match any of the existing attribute names of
    # the GeoLayer.
    invalid_attributes = []
    for attribute in attributes:
        if attribute not in list_of_existing_attributes:
            invalid_attributes.append(attribute)

    warning_count = 0
    is_valid = True
    message = ""
    recommendation = ""
    if len(invalid_attributes) > 0:
        # If there are invalid attributes, the check failed.
        is_valid = False
        # Log the issue
        message = "Parameter {}:  GeoLayerID {} does not contain attributes: {}".format(
                  geolayerid_parameter, geolayer_id, invalid_attributes)
        recommendation = "Specify valid attribute names."
        warning_count += 1

    return is_valid, warning_count, message, recommendation
