# AddGeoLayerAttribute

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.validators as validators

import logging


class AddGeoLayerAttribute(AbstractCommand):

    """
    Add an attribute to a GeoLayer.

    * This command adds a single attribute to a single GeoLayer.
    * The attribute name is specified.
    * The attribute type is specified.
    * There are currently 4 available attribute types.
        1. string: A text field.
        2. date: A date field (not including time).
        3. int: A whole number field. Can hold negative values.
        4. double: A real (decimal) number field. Can hold negative values.

    """

    # Command Parameters
    # GeoLayerID (str, required): the ID of the input GeoLayer, the layer to add the attribute
    # AttributeName (str, required): the name of the attribute to add. Must be a unique attribute name to the
    #    GeoLayer. If working with Esri Shapefiles, it is highly recommended that the string is 10 characters or less.
    # AttributeType (str, required): the attribute's data type. Options include 'string', 'date', 'int' and 'double'.
    #   Read the user documentation or the docstring for a more detailed parameter description.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("AttributeName", type("")),
        CommandParameterMetadata("AttributeType", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """
        # AbstractCommand data
        super(AddGeoLayerAttribute, self).__init__()
        self.command_name = "AddGeoLayerAttribute"
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

        # Check that parameter AttributeType is either 'string', 'date', 'int' and 'double'.
        pv_AttributeType = self.get_parameter_value(parameter_name="AttributeType",
                                                    command_parameters=command_parameters)

        acceptable_values = ["string", "date", "int", "double"]
        if not validators.validate_string_in_list(pv_AttributeType, acceptable_values, ignore_case=True):
            message = "AttributeType parameter value ({}) is not recognized.".format(pv_AttributeType)
            recommendation = "Specify one of the acceptable values ({}) for the AttributeType parameter.".format(
                acceptable_values)
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

    def __should_attribute_be_added(self, geolayer_id, attribute_name):
        """
        Checks the following:
         * The ID of the input GeoLayer is an actual GeoLayer (if not, log an error message and do not continue.)
         * The attribute name is a unique name for the GeoLayer (if not, log an error message and do not continue.)
         * The attribute name is 10 or less characters (if not, log a warning but still create the attribute.)

        Args:
            geolayer_id: the ID of the GeoLayer to add the new attribute
            attribute_name: the name of the attribute to add to the GeoLayer

        Returns:
            add_attribute: Boolean. If TRUE, the attribute should be added to the GeoLayer. If FALSE, a check has
             failed and the attribute should not be added.
        """

        # Boolean to determine if the attribute should be added. Set to TRUE until one or many checks fail.
        add_attribute = True

        # If the input GeoLayer does not exist, raise a FAILURE.
        if not self.command_processor.get_geolayer(geolayer_id):

            add_attribute = False
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

            # If the input attribute name is not unique to the attribute table, raise a FAILURE.
            if attribute_name in list_of_existing_attributes:

                add_attribute = False
                self.warning_count += 1
                message = 'The attribute name ({}) is not unique.'.format(attribute_name)
                recommendation = 'Specify a unique attribute name.'
                self.logger.error(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE,
                                                                message, recommendation))

            # If the input attribute name is longer than 10 characters, raise a WARNING.
            if len(attribute_name) > 10:

                self.warning_count += 1
                message = 'The attribute name ({}) is longer than 10 characters. Esri Shapefiles require the' \
                          ' attribute names to be 10 or less characters.'.format(attribute_name)
                recommendation = 'If this GeoLayer will be written in shapefile format, change the attribute name to' \
                                 ' only include 10 or less characters.'
                self.logger.warning(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.WARNING,
                                                                message, recommendation))

        # Return the Boolean to determine if the attribute should be added. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return add_attribute

    def run_command(self):
        """
        Run the command. Add the attribute to the GeoLayer.

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
        pv_AttributeType = self.get_parameter_value("AttributeType")

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_attribute_be_added(pv_GeoLayerID, pv_AttributeName):

            # Run the process.
            try:

                # Get the input GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Add the attribute to the GeoLayer.
                input_geolayer.add_attribute(pv_AttributeName, pv_AttributeType)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error adding attribute ({}) to GeoLayer {}.".format(pv_AttributeName,
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
