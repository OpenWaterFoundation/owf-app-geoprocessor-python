# SetProperty - command to set a processor property
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

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validators

import logging


class SetProperty(AbstractCommand):
    """
    The SetProperty command sets a processor property.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("PropertyName", type("")),
        CommandParameterMetadata("PropertyType", type("")),
        CommandParameterMetadata("PropertyValue", type("")),
        CommandParameterMetadata("PropertyValues", type(""))
    ]

    # Choices for PropertType valid values
    __choices_PropertyType = ["bool", "float", "int", "long", "str"]

    def __init__(self):
        """
        Initialize a command instance.
        """
        # AbstractCommand data
        super().__init__()
        self.command_name = "SetProperty"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = "Set the value of a property used by the processor."
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # PropertyName
        self.parameter_input_metadata['PropertyName.Description'] = "property name"
        self.parameter_input_metadata['PropertyName.Label'] = "Property name"
        self.parameter_input_metadata['PropertyName.Required'] = True
        self.parameter_input_metadata['PropertyName.Tooltip'] = "The property name."
        # PropertyType
        self.parameter_input_metadata['PropertyType.Description'] = "property type"
        self.parameter_input_metadata['PropertyType.Label'] = "Property type"
        self.parameter_input_metadata['PropertyType.Required'] = True
        self.parameter_input_metadata['PropertyType.Tooltip'] = \
            "The property type as bool, float, int, or str."
        # PropertyValue
        self.parameter_input_metadata['PropertyValue.Description'] = "property value"
        self.parameter_input_metadata['PropertyValue.Label'] = "Property value"
        self.parameter_input_metadata['PropertyValue.Tooltip'] = \
            "The property value, as a string that can be converted to the given type."
        self.parameter_input_metadata['PropertyValue.Value.Default.Description'] = \
            "'PropertyValue' or 'PropertyValues' must be specified."
        # PropertyValues
        self.parameter_input_metadata['PropertyValues.Description'] = "property value as a list of strings"
        self.parameter_input_metadata['PropertyValues.Label'] = "Property values"
        self.parameter_input_metadata['PropertyValues.Tooltip'] = (
            "The property values, as a list of string. Currently, comma-separated values are supported with optional\n"
            "surrounding [ ]. In the future single-quoted strings will be supported to allow commas in the strings.\n"
            "Strings are stripped of surrounding whitespace.")
        self.parameter_input_metadata['PropertyValues.Value.Default.Description'] = \
            "'PropertyValue' or 'PropertyValues' must be specified."

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            Nothing.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning = ""
        logger = logging.getLogger(__name__)

        # PropertyName is required
        pv_PropertyName = self.get_parameter_value(parameter_name='PropertyName', command_parameters=command_parameters)
        if not validators.validate_string(pv_PropertyName, False, False):
            message = "PropertyName parameter has no value."
            recommendation = "Specify a property name."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # PropertyType is required
        pv_PropertyType = self.get_parameter_value(parameter_name='PropertyType', command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_PropertyType, self.__choices_PropertyType, False, False):
            message = 'The requested property type "' + pv_PropertyType + '"" is invalid.'
            recommendation = "Specify a valid property type:  " + str(property_types)
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # TODO smalers 2017-12-28 add other parameters similar to TSTool to set special values

        property_value_parameter_count = 0  # increment for PropertyValue or PropertyValues, only one is allowed
        # PropertyValue or PropertyValues are required
        pv_PropertyValue = self.get_parameter_value(
            parameter_name='PropertyValue', command_parameters=command_parameters)
        if pv_PropertyValue is not None and pv_PropertyValue != "":
            property_value_parameter_count += 1
            if not validators.validate_string(pv_PropertyValue, True, True):
                message = "PropertyValue parameter is not specified."
                recommendation = "Specify a property value."
                warning += "\n" + message
                self.command_status.add_to_log(
                    CommandPhaseType.INITIALIZATION,
                    CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        pv_PropertyValues = self.get_parameter_value(
            parameter_name='PropertyValues', command_parameters=command_parameters)
        if pv_PropertyValues is not None and pv_PropertyValues != "":
            property_value_parameter_count += 1
            if not validators.validate_list(pv_PropertyValues, True, True, brackets_required=False):
                message = "PropertyValues parameter is not valid."
                recommendation = "Specify a list of values separated by commas and optional spaces."
                warning += "\n" + message
                self.command_status.add_to_log(
                    CommandPhaseType.INITIALIZATION,
                    CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        if property_value_parameter_count != 1:
            message = "PropertyValue (single value) or PropertyValues (for list) parameter must be specified."
            recommendation = "Specify a single value with PropertyValue or list of values with PropertyValues."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception
        if len(warning) > 0:
            # Message.printWarning ( warning_level,
            #    MessageUtil.formatMessageTag(command_tag, warning_level), routine, warning );
            logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def run_command(self):
        """
        Run the command.  Set a property on the GeoProcessor.

        Returns:
            Nothing.

        Raises:
            RuntimeError if there is any exception running the command.

        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        pv_PropertyName = self.get_parameter_value('PropertyName')
        pv_PropertyType = self.get_parameter_value('PropertyType')
        pv_PropertyValue = self.get_parameter_value('PropertyValue')
        pv_PropertyValues = self.get_parameter_value('PropertyValues')
        # Expand the property value string before converting to the requested type
        pv_PropertyValue_expanded = self.command_processor.expand_parameter_value(pv_PropertyValue)
        pv_PropertyValues_expanded = self.command_processor.expand_parameter_value(pv_PropertyValues)
        do_list = False  # Single property is the default
        if pv_PropertyValues is not None and pv_PropertyValues != "":
            # Doing a list
            do_list = True

        try:
            parameter_value_as_list = []
            parameter_value_to_parse = ""
            if do_list:
                parameter_value_to_parse = pv_PropertyValues_expanded
            else:
                # Single property - add to a list as if a single-value list
                parameter_value_to_parse = pv_PropertyValue_expanded
            # logger.info('Parsing parameter "' + str(parameter_value_to_parse) + "'")
            # Parse the list into a string list
            # - Remove leading [ and trailing ] so only have simple string list
            parameter_value_to_parse = parameter_value_to_parse.strip()  # First strip whitespace
            if parameter_value_to_parse.startswith("["):
                parameter_value_to_parse = parameter_value_to_parse[1:]
            if parameter_value_to_parse.endswith("]"):
                parameter_value_to_parse = parameter_value_to_parse[0:len(parameter_value_to_parse) - 1]
            parameter_value_as_string_list = string_util.delimited_string_to_list(parameter_value_to_parse, trim=True)
            # logger.info('Parsed parameter "' + str(parameter_value_as_string_list) + "'")
            # Loop through the list
            parameter_value2 = None
            for parameter_value in parameter_value_as_string_list:
                # Convert the property value string to the requested type
                parameter_value2 = None
                if pv_PropertyType == 'bool':
                    # Use the following because conversion of strings to booleans is tricky, too many unexpected True
                    parameter_value2 = string_util.str_to_bool(parameter_value)
                elif pv_PropertyType == 'float':
                    parameter_value2 = float(parameter_value)
                elif pv_PropertyType == 'int':
                    parameter_value2 = int(parameter_value)
                elif pv_PropertyType == 'str':
                    parameter_value2 = str(parameter_value)
                # Now set the object as a property, will be the requested type
                if do_list:
                    # The property is a list
                    # - for now avoid adding None - later For command should process only valid values
                    if parameter_value2 is not None:
                        parameter_value_as_list.append(parameter_value2)
            if do_list:
                # Doing a list so set the property value to the list
                # - list could be empty - is this an issue?
                self.command_processor.set_property(pv_PropertyName, parameter_value_as_list)
                # logger.info('Setting parameter "' + str(pv_PropertyName) + '"="' + str(parameter_value_as_list) + '"')
            else:
                # The property value is a single object and will have been processed in the loop's only iteration
                if parameter_value2 is not None:
                    self.command_processor.set_property(pv_PropertyName, parameter_value2)
                    # logger.info('Setting parameter "' + str(pv_PropertyName) + '"="' + str(parameter_value2) + '"')
        except Exception as e:
            warning_count += 1
            message = 'Unexpected error setting property "' + str(pv_PropertyName) + '"'
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "Check the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
