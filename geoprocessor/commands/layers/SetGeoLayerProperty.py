# SetGeoLayerProperty command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validators

import logging
import sys
import traceback


class SetGeoLayerProperty(AbstractCommand):
    """
    The SetGeoLayerProperty command sets a GeoLayer property.
    These properties are useful for controlling processing logic, for example selecting only layers
    that have a specific property value, tracking the state of processing, and using for quality control on the layer.
    The property values may not be able to be persisted because a layer format may
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("PropertyName", type("")),
        CommandParameterMetadata("PropertyType", type("")),
        CommandParameterMetadata("PropertyValue", type(""))
    ]

    def __init__(self):
        """
        Initialize a command instance.
        """
        # AbstractCommand data
        super(SetGeoLayerProperty, self).__init__()
        self.command_name = "SetProperty"
        self.command_parameter_metadata = self.__command_parameter_metadata

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

        # GeoLayerID is required
        # - non-empty, non-None string.
        # - existence of the GeoLayer will also be checked in run_command().
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID',
                                                 command_parameters=command_parameters)
        if not validators.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the GeoLayer to process."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # PropertyName is required
        pv_PropertyName = self.get_parameter_value(parameter_name='PropertyName', command_parameters=command_parameters)
        if not validators.validate_string(pv_PropertyName, False, False):
            message = "PropertyName parameter has no value."
            recommendation = "Specify a property name."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # PropertyType is required
        pv_PropertyType = self.get_parameter_value(parameter_name='PropertyType', command_parameters=command_parameters)
        property_types = ["bool", "float", "int", "long", "str"]
        if not validators.validate_string_in_list(pv_PropertyType, property_types, False, False):
            message = 'The requested property type "' + pv_PropertyType + '"" is invalid.'
            recommendation = "Specify a valid property type:  " + str(property_types)
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # PropertyValue is required
        pv_PropertyValue = self.get_parameter_value(
            parameter_name='PropertyValue', command_parameters=command_parameters)
        if not validators.validate_string(pv_PropertyValue, False, False):
            # TODO smalers 2017-12-28 add other parameters similar to TSTool to set special values
            message = "PropertyValue parameter is not specified."
            recommendation = "Specify a property value."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception
        if len(warning) > 0:
            logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def run_command(self):
        """
        Run the command.  Set a GeoLayer property value.

        Returns:
            Nothing.

        Raises:
            RuntimeError if any exception occurs running the command.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_PropertyName = self.get_parameter_value('PropertyName')
        pv_PropertyType = self.get_parameter_value('PropertyType')
        pv_PropertyValue = self.get_parameter_value('PropertyValue')
        # Expand the property value string before converting to the requested type
        pv_PropertyValue_expanded = self.command_processor.expand_parameter_value(pv_PropertyValue)

        try:
            # Convert the property value string to the requested type
            pv_PropertyValue2 = None
            if pv_PropertyType == 'bool':
                pv_PropertyValue2 = bool(pv_PropertyValue_expanded)
            elif pv_PropertyType == 'float':
                pv_PropertyValue2 = float(pv_PropertyValue_expanded)
            elif pv_PropertyType == 'int':
                pv_PropertyValue2 = int(pv_PropertyValue_expanded)
            elif pv_PropertyType == 'str':
                pv_PropertyValue2 = str(pv_PropertyValue_expanded)
            # Now set the object as a property, will be the requested type
            if pv_PropertyValue2 is not None:
                self.command_processor.set_property(pv_PropertyName, pv_PropertyValue2)

            # Get the GeoLayer object
            geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)
            if geolayer is None:
                message = 'Unable to find GeoLayer for GeoLayerID="' + pv_GeoLayerID + '"'
                warning_count += 1
                logger.error(message)
                self.command_status.add_to_log(
                    command_phase_type.RUN,
                    CommandLogRecord(command_status_type.FAILURE, message, "Check the log file for details."))
            else:
                geolayer.set_property(pv_PropertyName, pv_PropertyValue2)
        except Exception as e:
            warning_count += 1
            message = 'Unexpected error setting GeoLayer property "' + pv_PropertyName + '"'
            traceback.print_exc(file=sys.stdout)
            logger.exception(message, e)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE, message,
                                 "Check the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
