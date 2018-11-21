# SetPropertyFromGeoLayer command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validators

import logging


# TODO smalers 2018-01-10 Need to have more control of what to do if the processor property is not found.
class SetPropertyFromGeoLayer(AbstractCommand):
    """
    The SetPropertyFromGeoLayer command sets a GeoProcessor property from a GeoLayer property.
    This is particularly useful when inside a For() loop and a GeoLayer property needs to be accessed.
    Converting a GeoLayer property to a GeoProcessor property simplifies other commands since they can
    use the general ${Property} syntax.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("GeoLayerPropertyName", type("")),
        CommandParameterMetadata("PropertyName", type(""))
    ]

    def __init__(self):
        """
        Initialize a command instance.
        """
        # AbstractCommand data
        super().__init__()
        self.command_name = "SetPropertyFromGeoLayer"
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

        # GeoLayerProperty is required
        pv_PropertyName = self.get_parameter_value(parameter_name='GeoLayerPropertyName',
                                                   command_parameters=command_parameters)
        if not validators.validate_string(pv_PropertyName, False, False):
            message = "GeoLayerPropertyName parameter has no value."
            recommendation = "Specify a property name."
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

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception
        if len(warning) > 0:
            logger.warn(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def run_command(self):
        """
        Run the command.  Set the GeoProcessor property to that of the specified GeoLayer property.

        Returns:
            Nothing.

        Raises:
            RuntimeError if an exception occurs, for example if the property name is not found.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_GeoLayerPropertyName = self.get_parameter_value('GeoLayerPropertyName')
        pv_PropertyName = self.get_parameter_value('PropertyName')

        try:
            # Get the GeoLayer object
            geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)
            if geolayer is None:
                message = 'Unable to find GeoLayer for GeoLayerID="' + pv_GeoLayerID + '"'
                warning_count += 1
                self.command_status.add_to_log(
                    command_phase_type.RUN,
                    CommandLogRecord(command_status_type.FAILURE, message, "Check the log file for details."))
            else:
                # First get the property from the GeoLayer
                property_value = geolayer.get_property(pv_GeoLayerPropertyName)
                if property_value is not None:
                    self.command_processor.set_property(pv_PropertyName, property_value)
        except Exception as e:
            warning_count += 1
            message = 'Unexpected error setting property "' + pv_PropertyName + '"'
            logger.exception(message, e)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE, message,
                                 "Check the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
