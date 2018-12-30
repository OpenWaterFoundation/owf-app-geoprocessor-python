# AbstractCommand - class that is the abstract parent class for all commands
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2019 Open Water Foundation
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

from geoprocessor.core.CommandStatus import CommandStatus
import geoprocessor.util.command_util as command_util


class AbstractCommand(object):
    """
    Parent to all other command classes. Stores common data. Provides common functions,
    which can (and in some casts should) be overloaded in child classes.
    """

    def __init__(self):

        # Full command string (with indentation).
        self.command_string = ""

        # Command name as user would see. Will be set when command is parsed. Will NOT be set if an UnknownCommand.
        self.command_name = ""

        # Command description, used in editors.
        self.command_description = ""

        # Command processor, needed to interact with the geoprocessing environment.
        self.command_processor = None

        # Command parameters, a dictionary of input parameter names and parameter values.
        # The parameter values are all strings, matching the parsed values from the command string.
        # This ensures that no internal conversion, decimal round-off, etc. is exhibited.
        # The parameters are converted to needed non-string values in the command's run_command() function.
        self.command_parameters = {}

        # Command parameter metadata, a list of CommandParameterMetadata to
        # describe parameter names and types used by the command.
        self.command_parameter_metadata = []

        # Command status to track issues.
        self.command_status = CommandStatus()

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.
        This function should be defined in child classes in most cases.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            Nothing.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        pass

    def get_parameter_metadata(self, parameter_name):
        """
        Return the metadata for the requested parameter name.
        This can also be used to figure out if a parameter name is valid
        (return value of None indicates invalid).

        Args:
            parameter_name: Parameter name of interest.

        Returns:  Metadata for the requested parameter name, or None if not found.
        """
        # Loop through the list of command pareters and find a matching item.
        # Ignore case in the comparison.
        for parameter_metadata in self.command_parameter_metadata:
            if parameter_metadata.parameter_name.upper() == parameter_name.upper():
                return parameter_metadata
        # Matching parameter not found so return None
        return None

    def get_parameter_value(self, parameter_name, command_parameters=None, default_value=None):
        """
        Return the value for a parameter name.

        Args:
            parameter_name (str): The name of the parameter for which to return the parameter value.
            command_parameters:  A dictionary of command parameters to search for parameter_name.
                If None, the command's internal command parameter dictionary is used.
                Specifying this parameter is helpful, for example, when checking parameters in a
                temporary dictionary, such as created in a command editor.
            default_value: If the parameter is not found, the value to return (None by default).
                A value of None returned typically indicates that the parameter was not specified
                and the default value should be used.

        Returns:
            The parameter value as a string.
        """
        try:
            if command_parameters is None:
                # Get the parameter from the command's dictionary
                # parameter_value = self.command_parameters.get(parameter_name)
                parameter_value = self.command_parameters[parameter_name]
            else:
                # Get the parameter from the provided parameter dictionary
                # parameter_value = command_parameters.get(parameter_name)
                parameter_value = command_parameters[parameter_name]
            return parameter_value
        except KeyError:
            # Parameter was not found
            return default_value

    def initialize_command(self, command_string, processor, full_initialization):
        """
        Initialize the command by setting the processor and parsing parameters.

        Args:
            command_string:  The full command string.
            processor:  The GeoProcessor instance, which is set in the new command.
            full_initialization:  Indicates whether to
        """
        # Set the command string
        # - strip off the whitespace on the right such as newline (may be present if reading from a file)
        # - do not strip the left side since indent is used for formatting and want to retain
        self.command_string = command_string.rstrip()

        # Set the command processor.
        self.command_processor = processor

        # If full initialization, the input parameters will be parsed and the values will be added to the
        # command_parameters
        if full_initialization:

            # the following will call the AbstractCommand.parse_command by default
            self.parse_command(command_string)

    def parse_command(self, command_string):
        """
        Parse the command string and into self.command_parameters dictionary of
        command parameter names and values.
        The self.command_parameters dictionary is populated.

        Args:
            command_string The full command string as in Command(Param1="Value1",Param2="Value2")

        Returns:
            Nothing.
        """

        # Get the parameter string from the command string
        # (this is the string within the parenthesis of a command string).
        parameter_string = command_util.parse_parameter_string_from_command_string(command_string)

        debug = False
        if len(parameter_string) > 0:
            # Parameters are available to parse...
            # Parse the parameter string of form Parameter="Value",Parameter="Value" into a list of parameter items.
            # Parameter items are strings that represent key=value pairs for each parameter in the parameter string.
            # The parameter items are separated by commas in the parameter string.
            parameter_items = command_util.parse_parameter_string_into_key_value_pairs(parameter_string)

            # Parse each parameter key and value pair. If the parameter value is supposed to be in list format
            # (rather than string format) convert it to a list. Return a dictionary with each parameter as a separate
            # entry (key: parameter name as entered by the user, value: the parameter value (in either string or list
            # format) assign the parameter dictionary to self.command_parameters for use by the specific command.
            self.command_parameters = command_util.parse_key_value_pairs_into_dictionary(parameter_items)
            if debug:
                print("CMD_PARAM: {}".format(self.command_parameters))

        # Print out the parsed command parameters for debugging
        if debug:
            for parameter_name, parameter_value in self.command_parameters.items():
                print('After parsing, command parameter name="' + parameter_name + '" value="' + parameter_value + '"')
                pass

    def print_for_debug(self):
        print("Debug information for command")
        print("Command name=" + self.command_name)
        print("Command string=" + self.command_string)
        for parameter_name, parameter_value in self.command_parameters.items():
            print('Command parameter name ="' + parameter_name + '", value="' + parameter_value + '"')

    def run_command(self):
        """
        Run the command. This should always be overridden by the command class.

        Returns:
        """
        print('In AbstractCommand.run_command')

    def to_string(self, command_parameters=None, format_all=False):
        """
        Format the internal command data into the command string that users see.
        This version of the function should only be used by commands that follow CommandName(Param1="Value1",...)
        syntax and should otherwise be overloaded in the specific command class.
        Only parameters that have been specified (values are not None and not empty strings)
        will be output by default to minimize command length.
        The order of parameters is given by the get_parameter_metadata() function,
        which indicates a logical order (input first, group by feature, etc.).
        Any unknown parameters are output at the end - this should normally not occur but is
        enabled to help with troubleshooting.
        A parameter value that is a list will be output with surrounding [ ].
        If brackets are optional, they should be handled in parsing and command editor dialogs can display
        without brackets.

        Args:
            command_parameters (dict):
                If specified, a dictionary of parameter names and values to format.
                If specified as None, all non-empty command parameters will be formatted.
            format_all (bool):
                If True, format all command parameters even if not specified, useful for troubleshooting.
                If False, only format specified parameters, default for normal functionality.

        Returns:  Formatted command string such as CommandName(Param1="Value1",Param2="Value2",...)
        """
        # If the parameters passed in are None, use the command parameters
        if command_parameters is None:
            command_parameters = self.command_parameters
        # First part of command is the indent from the original command
        command_string_formatted = ""
        for i_command in range[0:len(self.command_string) - 1]:
            if self.command_string[i_command] == " ":
                command_string_formatted = command_string_formatted + " "
            else:
                # No more spaces at front of the command
                break
        # Append the command name and starting parenthesis
        command_string_formatted = command_string_formatted + self.command_name + "("
        # Loop through all the parameters that are valid for the command.
        param_output_count = 0
        for command_parameter_meta in self.command_parameter_metadata:
            parameter_value = self.get_parameter_value(command_parameter_meta.parameter_name,
                                                       command_parameters=command_parameters)
            # Determine whether to output
            do_output = False
            if format_all:
                do_output = True
            else:
                # Only output if the parameter is not None and not a blank string
                if (parameter_value is not None) and (str(parameter_value) != ""):
                    do_output = True
            if do_output:
                # If this is not the first parameter, add a comma separator
                if param_output_count > 0:
                    command_string_formatted = command_string_formatted + ","
                # Append the parameter using syntax ParameterName="ParameterValue"
                # - simple objects will output with no formatting
                # - lists will be output as ['a', 'b', 'c'] or [1, 2, 3], OK for now but will have to handle parsing
                command_string_formatted = command_string_formatted + command_parameter_meta.parameter_name + '="' + \
                    str(parameter_value) + '"'
        # Append the trailing parenthesis
        command_string_formatted = command_string_formatted + ")"
        return command_string_formatted
