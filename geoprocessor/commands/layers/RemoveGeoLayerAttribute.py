# RemoveGeoLayerAttribute

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.validators as validators

import logging


class RemoveGeoLayerAttribute(AbstractCommand):

    """
    Removes an attribute from a GeoLayer.

    * This command removes a single attribute from a single GeoLayer.
    * The name of the attribute to remove is specified.
    """

    # Command Parameters
    # GeoLayerID (str, required): the ID of the input GeoLayer, the layer to remove the attribute from
    # AttributeName (str, required): the name of the attribute to remove. Must be a valid attribute field to the
    #    GeoLayer. This parameter is case specific.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("AttributeName", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """
        # AbstractCommand data
        super(RemoveGeoLayerAttribute, self).__init__()
        self.command_name = "RemoveGeoLayerAttribute"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning = ""
        logger = logging.getLogger(__name__)

        # Check that parameters GeoLayerID and is a non-empty, non-None string.
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID', command_parameters=command_parameters)

        if not validators.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the input GeoLayer."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that parameter AttributeName is a non-empty, non-None string.
        pv_AttributeName = self.get_parameter_value(parameter_name='AttributeName',
                                                    command_parameters=command_parameters)

        if not validators.validate_string(pv_AttributeName, False, False):

            message = "AttributeName parameter has no value."
            recommendation = "Specify the AttributeName parameter to indicate the name of attribute to add."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            logger.warning(warning)
            raise ValueError(warning)
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def __should_attribute_be_removed(self, geolayer_id, attribute_name):
        """
        Checks the following:
         * The ID of the input GeoLayer is an actual GeoLayer (if not, log an error message and do not continue.)
         * The attribute name is a valid name for the GeoLayer (if not, log an error message and do not continue.)

        Args:
            geolayer_id: the ID of the GeoLayer with the attribute to remove
            attribute_name: the name of the attribute to remove from the GeoLayer

        Returns:
            remove_attribute: Boolean. If TRUE, the attribute should be removed from the GeoLayer. If FALSE, a check
             has failed and the attribute should not be removed.
        """

        # Boolean to determine if the attribute should be removed. Set to TRUE until one or many checks fail.
        remove_attribute = True

        # If the input GeoLayer does not exist, raise a FAILURE.
        if not self.command_processor.get_geolayer(geolayer_id):

            # Boolean to determine if the attribute should be removed.
            remove_attribute = False
            self.warning_count += 1
            message = 'The input GeoLayer ID ({}) does not exist.'.format(geolayer_id)
            recommendation = 'Specify a valid GeoLayerID.'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE,
                                                            message, recommendation))

        # If the input GeoLayer does exist, continue with the checks.
        else:

            # Get the input GeoLayer object.
            input_geolayer = self.command_processor.get_geolayer(geolayer_id)

            # Get the existing attribute names of the input GeoLayer.
            list_of_existing_attributes = input_geolayer.get_attribute_field_names()

            # If the input attribute name is not valid, raise a FAILURE.
            if attribute_name not in list_of_existing_attributes:
                remove_attribute = False
                self.warning_count += 1
                message = 'The attribute name ({}) is not valid.'.format(attribute_name)
                recommendation = 'Specify a valid attribute name. Valid attributes for this layer are as follows: ' \
                                 '{}'.format(list_of_existing_attributes)
                self.logger.error(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE,
                                                                message, recommendation))

        # Return the Boolean to determine if the attribute should be removed. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return remove_attribute

    def run_command(self):
        """
        Run the command. Remove the attribute from the GeoLayer.

        Args:
            None.

        Returns:
            Nothing.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_AttributeName = self.get_parameter_value("AttributeName")

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_attribute_be_removed(pv_GeoLayerID, pv_AttributeName):

            # Run the process.
            try:

                # Get the input GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Remove the attribute from the GeoLayer.
                input_geolayer.remove_attribute(pv_AttributeName)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error removing attribute ({}) from GeoLayer {}.".format(pv_AttributeName,
                                                                                              pv_GeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.exception(message, e)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message,
                                                                recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
