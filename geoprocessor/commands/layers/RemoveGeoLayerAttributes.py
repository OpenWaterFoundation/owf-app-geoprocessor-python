# RemoveGeoLayerAttributes

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validators

import logging


class RemoveGeoLayerAttributes(AbstractCommand):

    """
    Removes one or more attributes from a GeoLayer.

    * The names of the attributes to remove are specified.

    Command Parameters
    * GeoLayerID (str, required): the ID of the input GeoLayer, the layer to remove the attribute from
    * AttributeNames (str, required): the names of the attributes to remove. Strings separated by commas. Attribute
        names must be valid attribute fields to the GeoLayer. This parameter is case specific.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("AttributeNames", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "RemoveGeoLayerAttributes"
        self.command_description = "Remove one or more attributes from a GeoLayer"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns: None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning = ""

        # Check that parameters GeoLayerID and is a non-empty, non-None string.
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID', command_parameters=command_parameters)

        if not validators.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the input GeoLayer."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that parameter AttributeNames is a non-empty, non-None string.
        pv_AttributeNames = self.get_parameter_value(parameter_name='AttributeNames',
                                                    command_parameters=command_parameters)

        if not validators.validate_string(pv_AttributeNames, False, False):

            message = "AttributeNames parameter has no value."
            recommendation = "Specify the AttributeNames parameter to indicate the name of attribute to add."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def __should_attribute_be_removed(self, geolayer_id, attribute_names):
        """
        Checks the following:
         * The ID of the input GeoLayer is an actual GeoLayer (if not, log an error message and do not continue.)
         * The attribute names are valid names for the GeoLayer (if not, log an error message and do not continue.)

        Args:
            geolayer_id: the ID of the GeoLayer with the attribute to remove
            attribute_names (list of strings): the names of the attributes to remove from the GeoLayer

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
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # If the input GeoLayer does exist, continue with the checks.
        else:

            # Get the input GeoLayer object.
            input_geolayer = self.command_processor.get_geolayer(geolayer_id)

            # Get the existing attribute names of the input GeoLayer.
            list_of_existing_attributes = input_geolayer.get_attribute_field_names()

            # Create a list of invalid input attribute names. An invalid attribute name is an input attribute name
            # that is not matching any of the existing attribute names of the GeoLayer.
            invalid_attrs = (attr_name for attr_name in attribute_names if attr_name not in list_of_existing_attributes)

            # Iterate over the invalid input attribute names and raise a FAILURE for each.
            for invalid_attr in invalid_attrs:

                remove_attribute = False
                self.warning_count += 1
                message = 'The attribute name ({}) is not valid.'.format(invalid_attr)
                recommendation = 'Specify a valid attribute name. Valid attributes for this layer are' \
                                 ' as follows: {}'.format(list_of_existing_attributes)
                self.logger.error(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Return the Boolean to determine if the attribute should be removed. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return remove_attribute

    def run_command(self):
        """
        Run the command. Remove the attribute from the GeoLayer.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_AttributeNames = self.get_parameter_value("AttributeNames")

        # Convert the AttributeNames parameter from a string to a list.
        attribute_names_list = string_util.delimited_string_to_list(pv_AttributeNames)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_attribute_be_removed(pv_GeoLayerID, attribute_names_list):

            # Run the process.
            try:

                # Get the input GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Iterate over the input attributes to remove.
                for attribute_name in attribute_names_list:

                    # Remove the attribute from the GeoLayer.
                    input_geolayer.remove_attribute(attribute_name)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:

                self.warning_count += 1
                message = "Unexpected error removing attribute(s) ({}) from GeoLayer {}.".format(pv_AttributeNames,
                                                                                                 pv_GeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.error(message, exc_info=True)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
