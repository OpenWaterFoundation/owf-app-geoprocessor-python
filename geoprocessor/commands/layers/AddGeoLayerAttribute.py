# AddGeoLayerAttribute - command to add attributes to a GeoLayer
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

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validators

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

    Command Parameters
    * GeoLayerID (str, required): the ID of the input GeoLayer, the layer to add the attribute
    * AttributeName (str, required): the name of the attribute to add. Must be a unique attribute name to the GeoLayer.
        If working with Esri Shapefiles, it is highly recommended that the string is 10 characters or less.
    * AttributeType (str, required): the attribute's data type. Options include 'string', 'date', 'int' and 'double'.
        Read the user documentation or the docstring for a more detailed parameter description.
    * InitialValue (str, optional): a string value used to populate the added attribute for each feature. All
        features will have the same attribute value. This parameter is used mainly for testing. If not specified,
        the attribute values are set to NULL.
    """

    # Define command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("AttributeName", type("")),
        CommandParameterMetadata("AttributeType", type("")),
        CommandParameterMetadata("InitialValue", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "AddGeoLayerAttribute"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata["Description"] = "Add a single attribute to a single GeoLayer."
        self.command_metadata["EditorType"] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # GeoLayerID
        self.parameter_input_metadata['GeoLayerID.Description'] = "the ID of the GeoLayer"
        self.parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
        self.parameter_input_metadata['GeoLayerID.Required'] = True
        self.parameter_input_metadata['GeoLayerID.Tooltip'] =\
            "The ID of the GeoLayer to have an attribute added. ${Property} syntax is recognized. "
        # AttributeName
        self.parameter_input_metadata['AttributeName.Description'] = "the attribute name"
        self.parameter_input_metadata['AttributeName.Label'] = "Attribute name"
        self.parameter_input_metadata['AttributeName.Required'] = True
        self.parameter_input_metadata['AttributeName.Tooltip'] =\
            "The attribute name. Highly recommended to be 10 or less characters. Case-specific."
        # AttributeType
        self.parameter_input_metadata['AttributeType.Description'] = "the attribute data type"
        self.parameter_input_metadata['AttributeType.Label'] = "Attribute type"
        self.parameter_input_metadata['AttributeType.Required'] = True
        self.parameter_input_metadata['AttributeType.Values'] = ['date', 'double', 'int', 'string']
        self.parameter_input_metadata['AttributeType.Tooltip'] = "The attribute data type. Must be one of the " \
            "following options: \nstring : The attribute values will be text. e.g. blue, Colorado, helicopter \n" \
            "int: The attribute values will be integers. e.g. 100, 0, -54 \n" \
            "double : The attribute values will be real numbers. e.g.100.01, 0.00089, -54.0 \n"\
            "date : The attribute values will be date values. e.g. YYYY-MM-DD format is recommended. "
        # InitialValue
        self.parameter_input_metadata['InitialValue.Description'] = "attribute value"
        self.parameter_input_metadata['InitialValue.Label'] = "Attribute value"
        self.parameter_input_metadata['InitialValue.Tooltip'] = "Attribute value. ${Property} syntax is recognized. \n"\
            "All features are populated with the same value. This parameter is designed to aid in command testing. "

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

        # Check that parameters GeoLayerID and is a non-empty, non-None string.
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID', command_parameters=command_parameters)

        if not validators.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the input GeoLayer."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that parameter AttributeName is a non-empty, non-None string.
        pv_AttributeName = self.get_parameter_value(parameter_name='AttributeName',
                                                    command_parameters=command_parameters)

        if not validators.validate_string(pv_AttributeName, False, False):

            message = "AttributeName parameter has no value."
            recommendation = "Specify the AttributeName parameter to indicate the name of attribute to add."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

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
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

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
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

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
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

            # If the input attribute name is longer than 10 characters, raise a WARNING.
            if len(attribute_name) > 10:

                self.warning_count += 1
                message = 'The attribute name ({}) is longer than 10 characters. Esri Shapefiles require the' \
                          ' attribute names to be 10 or less characters.'.format(attribute_name)
                recommendation = 'If this GeoLayer will be written in shapefile format, change the attribute name to' \
                                 ' only include 10 or less characters.'
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING, message, recommendation))

        # Return the Boolean to determine if the attribute should be added. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return add_attribute

    def run_command(self):
        """
        Run the command. Add the attribute to the GeoLayer.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_AttributeName = self.get_parameter_value("AttributeName")
        pv_AttributeType = self.get_parameter_value("AttributeType")
        pv_InitialValue = self.get_parameter_value("InitialValue", default_value=None)

        # Expand for ${Property} syntax.
        pv_GeoLayerID = self.command_processor.expand_parameter_value(pv_GeoLayerID, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_attribute_be_added(pv_GeoLayerID, pv_AttributeName):

            # Run the process.
            try:

                # Get the input GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Add the attribute to the GeoLayer.
                input_geolayer.add_attribute(pv_AttributeName, pv_AttributeType)

                # If the InitialValue parameter has been set, populate the added attribute with the given value.
                # Expand for ${Property} syntax.
                pv_InitialValue = self.command_processor.expand_parameter_value(pv_InitialValue, self)
                if pv_InitialValue:
                    input_geolayer.populate_attribute(pv_AttributeName, pv_InitialValue)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error adding attribute ({}) to GeoLayer {}.".format(pv_AttributeName,
                                                                                          pv_GeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.error(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
