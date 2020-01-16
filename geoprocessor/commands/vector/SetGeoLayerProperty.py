# SetGeoLayerProperty - command to set GeoLayer properties
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
import geoprocessor.util.validator_util as validator_util

import logging


class SetGeoLayerProperty(AbstractCommand):
    """
    The SetGeoLayerProperty command sets a GeoLayer property.
    These properties are useful for controlling processing logic, for example selecting only layers
    that have a specific property value, tracking the state of processing, and using for quality control on the layer.
    The property values may not be able to be persisted because a layer format may
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("PropertyName", type("")),
        CommandParameterMetadata("PropertyType", type("")),
        CommandParameterMetadata("PropertyValue", type(""))
    ]

    def __init__(self) -> None:
        """
        Initialize a command instance.
        """
        # AbstractCommand data
        super().__init__()
        self.command_name = "SetGeoLayerProperty"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = "Set the value of a GeoLayer property."
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # GeoLayerID
        self.parameter_input_metadata['GeoLayerID.Description'] = "GoeLayer identifier"
        self.parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
        self.parameter_input_metadata['GeoLayerID.Required'] = True
        self.parameter_input_metadata['GeoLayerID.Tooltip'] = "The GeoLayer identifier, can use ${Property}."
        # PropertyName
        self.parameter_input_metadata['PropertyName.Description'] = "property name"
        self.parameter_input_metadata['PropertyName.Label'] = "Property name"
        self.parameter_input_metadata['PropertyName.Required'] = True
        self.parameter_input_metadata['PropertyName.Tooltip'] = "The property name."
        # PropertyType
        self.parameter_input_metadata['PropertyType.Description'] = "property type"
        self.parameter_input_metadata['PropertyType.Label'] = "Property type"
        self.parameter_input_metadata['PropertyType.Required'] = True
        self.parameter_input_metadata['PropertyType.Tooltip'] = "The property type as bool, float, int, or str."
        self.parameter_input_metadata['PropertyType.Values'] = ['bool', 'float', 'int', 'str']
        # PropertyValue
        self.parameter_input_metadata['PropertyValue.Description'] = "property value"
        self.parameter_input_metadata['PropertyValue.Label'] = "Property value"
        self.parameter_input_metadata['PropertyValue.Required'] = True
        self.parameter_input_metadata['PropertyValue.Tooltip'] =\
            "The property value, as a string that can convert to the given type."

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
        warning = ""
        logger = logging.getLogger(__name__)

        # GeoLayerID is required
        # - non-empty, non-None string.
        # - existence of the GeoLayer will also be checked in run_command().
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID',
                                                 command_parameters=command_parameters)
        if not validator_util.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the GeoLayer to process."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # PropertyName is required
        # noinspection PyPep8Naming
        pv_PropertyName = self.get_parameter_value(parameter_name='PropertyName', command_parameters=command_parameters)
        if not validator_util.validate_string(pv_PropertyName, False, False):
            message = "PropertyName parameter has no value."
            recommendation = "Specify a property name."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # PropertyType is required
        # noinspection PyPep8Naming
        pv_PropertyType = self.get_parameter_value(parameter_name='PropertyType', command_parameters=command_parameters)
        property_types = ["bool", "float", "int", "long", "str"]
        if not validator_util.validate_string_in_list(pv_PropertyType, property_types, False, False):
            message = 'The requested property type "' + pv_PropertyType + '"" is invalid.'
            recommendation = "Specify a valid property type:  " + str(property_types)
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # PropertyValue is required
        # noinspection PyPep8Naming
        pv_PropertyValue = self.get_parameter_value(
            parameter_name='PropertyValue', command_parameters=command_parameters)
        if not validator_util.validate_string(pv_PropertyValue, False, False):
            # TODO smalers 2017-12-28 add other parameters similar to TSTool to set special values
            message = "PropertyValue parameter is not specified."
            recommendation = "Specify a property value."
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
            logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def run_command(self) -> None:
        """
        Run the command.  Set a GeoLayer property value.

        Returns:
            None

        Raises:
            RuntimeError if any exception occurs running the command.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        # noinspection PyPep8Naming
        pv_PropertyName = self.get_parameter_value('PropertyName')
        # noinspection PyPep8Naming
        pv_PropertyType = self.get_parameter_value('PropertyType')
        # noinspection PyPep8Naming
        pv_PropertyValue = self.get_parameter_value('PropertyValue')
        # Expand the property value string before converting to the requested type
        # noinspection PyPep8Naming
        pv_PropertyValue_expanded = self.command_processor.expand_parameter_value(pv_PropertyValue)

        # noinspection PyBroadException
        try:
            # Convert the property value string to the requested type
            # noinspection PyPep8Naming
            pv_PropertyValue2 = None
            if pv_PropertyType == 'bool':
                # noinspection PyPep8Naming
                pv_PropertyValue2 = bool(pv_PropertyValue_expanded)
            elif pv_PropertyType == 'float':
                # noinspection PyPep8Naming
                pv_PropertyValue2 = float(pv_PropertyValue_expanded)
            elif pv_PropertyType == 'int':
                # noinspection PyPep8Naming
                pv_PropertyValue2 = int(pv_PropertyValue_expanded)
            elif pv_PropertyType == 'str':
                # noinspection PyPep8Naming
                pv_PropertyValue2 = str(pv_PropertyValue_expanded)
            # Now set the object as a property, will be the requested type
            if pv_PropertyValue2 is not None:
                self.command_processor.set_property(pv_PropertyName, pv_PropertyValue2)

            # Get the GeoLayer object
            geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)
            if geolayer is None:
                message = 'Unable to find GeoLayer for GeoLayerID="' + pv_GeoLayerID + '"'
                warning_count += 1
                logger.warning(message)
                self.command_status.add_to_log(
                    CommandPhaseType.RUN,
                    CommandLogRecord(CommandStatusType.FAILURE, message, "Check the log file for details."))
            else:
                geolayer.set_property(pv_PropertyName, pv_PropertyValue2)
        except Exception:
            warning_count += 1
            message = 'Unexpected error setting GeoLayer property "' + pv_PropertyName + '"'
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "Check the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
