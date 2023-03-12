# SetProperty - command to set a processor property
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2023 Open Water Foundation
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

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandError import CommandError
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import logging


class SetProperty(AbstractCommand):
    """
    The SetProperty command sets a processor property.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("PropertyName", type("")),
        CommandParameterMetadata("PropertyType", type("")),
        CommandParameterMetadata("PropertyValue", type("")),
        CommandParameterMetadata("PropertyValues", type(""))
    ]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = "Set the value of a property used by the processor."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # PropertyName
    __parameter_input_metadata['PropertyName.Description'] = "property name"
    __parameter_input_metadata['PropertyName.Label'] = "Property name"
    __parameter_input_metadata['PropertyName.Required'] = True
    __parameter_input_metadata['PropertyName.Tooltip'] = "The property name."
    # PropertyType
    __parameter_input_metadata['PropertyType.Description'] = "property type"
    __parameter_input_metadata['PropertyType.Label'] = "Property type"
    __parameter_input_metadata['PropertyType.Required'] = True
    __parameter_input_metadata['PropertyType.Values'] = ['bool', 'float', 'int', 'str']
    # TODO smalers 2020-07-14 remove when tested.
    # __parameter_input_metadata['PropertyType.Value.DefaultForDisplay'] = 'str'
    __parameter_input_metadata['PropertyType.Value.Default.ForEditor'] = 'str'
    __parameter_input_metadata['PropertyType.Tooltip'] = \
        "The property type as bool, float, int, or str, will also be used for the type of values if multiple values."
    # PropertyValue
    __parameter_input_metadata['PropertyValue.Description'] = "property value"
    __parameter_input_metadata['PropertyValue.Label'] = "Property value"
    __parameter_input_metadata['PropertyValue.Tooltip'] = \
        "The property value, as a string that can be converted to the given type."
    __parameter_input_metadata['PropertyValue.Value.Default.Description'] = \
        "'PropertyValue' or 'PropertyValues' must be specified."
    # PropertyValues
    __parameter_input_metadata['PropertyValues.Description'] = "property value as a list"
    __parameter_input_metadata['PropertyValues.Label'] = "Property values"
    __parameter_input_metadata['PropertyValues.Tooltip'] = (
        "The property values, as a list. Currently, comma-separated values are supported with optional"
        "surrounding [ ].\nIn the future single-quoted strings will be supported to allow commas in the strings.\n"
        "Strings are stripped of surrounding whitespace.")
    __parameter_input_metadata['PropertyValues.Value.Default.Description'] = \
        "'PropertyValue' or 'PropertyValues' must be specified."

    # Choices for PropertyType valid values.
    __choices_PropertyType: [str] = ["bool", "float", "int", "long", "str"]

    def __init__(self) -> None:
        """
        Initialize a command instance.
        """
        # AbstractCommand data.
        super().__init__()
        self.command_name = "SetProperty"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display.
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata.
        self.parameter_input_metadata = self.__parameter_input_metadata

    def check_command_parameters(self, command_parameters: dict) -> None:
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            None

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning_message = ""
        logger = logging.getLogger(__name__)

        # Check that required parameters are non-empty, non-None strings.
        required_parameters = command_util.get_required_parameter_names(self)
        for parameter in required_parameters:
            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)
            if not validator_util.validate_string(parameter_value, False, False):
                message = "Required {} parameter has no value.".format(parameter)
                recommendation = "Specify the {} parameter.".format(parameter)
                warning_message += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # TODO smalers 2017-12-28 add other parameters similar to TSTool to set special values
        # TODO smalers 2020-03-21 make sure type can be parsed into the indiated type, also for the list

        # Only one of PropertyValue and PropertyValues can be specified.
        property_value_parameter_count = 0
        # noinspection PyPep8Naming
        pv_PropertyValue = self.get_parameter_value(
            parameter_name='PropertyValue', command_parameters=command_parameters)
        if pv_PropertyValue is not None and pv_PropertyValue != "":
            property_value_parameter_count += 1
        # noinspection PyPep8Naming
        pv_PropertyValues = self.get_parameter_value(
            parameter_name='PropertyValues', command_parameters=command_parameters)
        if pv_PropertyValues is not None and pv_PropertyValues != "":
            property_value_parameter_count += 1
            if not validator_util.validate_list(pv_PropertyValues, True, True, brackets_required=False):
                message = "PropertyValues parameter is not valid."
                recommendation = "Specify a list of values separated by commas and optional spaces."
                warning_message += "\n" + message
                self.command_status.add_to_log(
                    CommandPhaseType.INITIALIZATION,
                    CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        if property_value_parameter_count != 1:
            message = "PropertyValue (single value) or PropertyValues (for list) parameter must be specified."
            recommendation = "Specify a single value with PropertyValue or list of values with PropertyValues."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, and if non-empty triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            # Message.printWarning ( warning_level,
            #    MessageUtil.formatMessageTag(command_tag, warning_level), routine, warning );
            logger.warning(warning_message)
            raise CommandParameterError(warning_message)

        # Refresh the phase severity.
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def run_command(self) -> None:
        """
        Run the command.  Set a property on the GeoProcessor.

        Returns:
            None

        Raises:
            RuntimeError if there is any exception running the command.

        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # noinspection PyPep8Naming
        pv_PropertyName = self.get_parameter_value('PropertyName')
        # noinspection PyPep8Naming
        pv_PropertyType = self.get_parameter_value('PropertyType')
        # noinspection PyPep8Naming
        pv_PropertyValue = self.get_parameter_value('PropertyValue')
        # noinspection PyPep8Naming
        pv_PropertyValues = self.get_parameter_value('PropertyValues')
        # Expand the property value string before converting to the requested type.
        # noinspection PyPep8Naming
        pv_PropertyValue_expanded = self.command_processor.expand_parameter_value(pv_PropertyValue)
        # noinspection PyPep8Naming
        pv_PropertyValues_expanded = self.command_processor.expand_parameter_value(pv_PropertyValues)
        do_list = False  # Single property is the default.
        if pv_PropertyValues is not None and pv_PropertyValues != "":
            # Doing a list.
            do_list = True

        # noinspection PyBroadException
        try:
            parameter_value_as_list = []
            parameter_value_to_parse = ""
            if do_list:
                parameter_value_to_parse = pv_PropertyValues_expanded
            else:
                # Single property - add to a list as if a single-value list.
                parameter_value_to_parse = pv_PropertyValue_expanded
            # logger.info('Parsing parameter "' + str(parameter_value_to_parse) + "'")
            # Parse the list into a string list:
            # - Remove leading [ and trailing ] so only have simple string list
            parameter_value_to_parse = parameter_value_to_parse.strip()  # First strip whitespace
            if parameter_value_to_parse.startswith("["):
                parameter_value_to_parse = parameter_value_to_parse[1:]
            if parameter_value_to_parse.endswith("]"):
                parameter_value_to_parse = parameter_value_to_parse[0:len(parameter_value_to_parse) - 1]
            parameter_value_as_string_list = string_util.delimited_string_to_list(parameter_value_to_parse, trim=True)
            # logger.info('Parsed parameter "' + str(parameter_value_as_string_list) + "'")
            # Loop through the list.
            parameter_value2 = None
            for parameter_value in parameter_value_as_string_list:
                # Convert the property value string to the requested type.
                parameter_value2 = None
                if pv_PropertyType == 'bool':
                    # Use the following because conversion of strings to booleans is tricky, too many unexpected True.
                    parameter_value2 = string_util.str_to_bool(parameter_value)
                elif pv_PropertyType == 'float':
                    parameter_value2 = float(parameter_value)
                elif pv_PropertyType == 'int':
                    parameter_value2 = int(parameter_value)
                elif pv_PropertyType == 'str':
                    parameter_value2 = str(parameter_value)
                # Now set the object as a property, will be the requested type.
                if do_list:
                    # The property is a list:
                    # - for now avoid adding None - later For command should process only valid values
                    if parameter_value2 is not None:
                        parameter_value_as_list.append(parameter_value2)
            if do_list:
                # Doing a list so set the property value to the list:
                # - list could be empty - is this an issue?
                self.command_processor.set_property(pv_PropertyName, parameter_value_as_list)
                # logger.info('Setting parameter "' + str(pv_PropertyName) + '"="' + str(parameter_value_as_list) + '"')
            else:
                # The property value is a single object and will have been processed in the loop's only iteration.
                if parameter_value2 is not None:
                    self.command_processor.set_property(pv_PropertyName, parameter_value2)
                    # logger.info('Setting parameter "' + str(pv_PropertyName) + '"="' + str(parameter_value2) + '"')
        except Exception:
            warning_count += 1
            message = 'Unexpected error setting property "' + str(pv_PropertyName) + '"'
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "Check the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise CommandError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
