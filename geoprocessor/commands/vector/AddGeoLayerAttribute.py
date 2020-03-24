# AddGeoLayerAttribute - command to add attributes to a GeoLayer
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

from geoprocessor.core.CommandError import CommandError
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validator_util

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
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("AttributeName", type("")),
        CommandParameterMetadata("AttributeType", type("")),
        CommandParameterMetadata("InitialValue", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata["Description"] = "Add a single attribute to a single GeoLayer."
    __command_metadata["EditorType"] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "the ID of the GeoLayer"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = \
        "The ID of the GeoLayer to have an attribute added. ${Property} syntax is recognized. "
    # AttributeName
    __parameter_input_metadata['AttributeName.Description'] = "the attribute name"
    __parameter_input_metadata['AttributeName.Label'] = "Attribute name"
    __parameter_input_metadata['AttributeName.Required'] = True
    __parameter_input_metadata['AttributeName.Tooltip'] = \
        "The attribute name. Highly recommended to be 10 or less characters. Case-specific."
    # AttributeType
    __parameter_input_metadata['AttributeType.Description'] = "the attribute data type"
    __parameter_input_metadata['AttributeType.Label'] = "Attribute type"
    __parameter_input_metadata['AttributeType.Required'] = True
    __parameter_input_metadata['AttributeType.Values'] = ['date', 'double', 'int', 'string']
    __parameter_input_metadata['AttributeType.Value.DefaultForDisplay'] = ''
    __parameter_input_metadata['AttributeType.Tooltip'] =\
        "The attribute data type. Must be one of the " \
        "following options: \nstring : The attribute values will be text. e.g. blue, Colorado, helicopter \n" \
        "int: The attribute values will be integers. e.g. 100, 0, -54 \n" \
        "double : The attribute values will be real numbers. e.g.100.01, 0.00089, -54.0 \n" \
        "date : The attribute values will be date values. e.g. YYYY-MM-DD format is recommended. "
    # InitialValue
    __parameter_input_metadata['InitialValue.Description'] = "attribute value"
    __parameter_input_metadata['InitialValue.Label'] = "Attribute value"
    __parameter_input_metadata['InitialValue.Tooltip'] =\
        "Attribute value. ${Property} syntax is recognized. \n" \
        "All features are populated with the same value. This parameter is designed to aid in command testing. "

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "AddGeoLayerAttribute"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata
        self.parameter_input_metadata = self.__parameter_input_metadata

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters: dict) -> None:
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
        warning_message = ""

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

        # Check that parameter AttributeType is either 'string', 'date', 'int' and 'double'.
        # noinspection PyPep8Naming
        pv_AttributeType = self.get_parameter_value(parameter_name="AttributeType",
                                                    command_parameters=command_parameters)

        acceptable_values = ["string", "date", "int", "double"]
        if not validator_util.validate_string_in_list(pv_AttributeType, acceptable_values, ignore_case=True):
            message = "AttributeType parameter value ({}) is not recognized.".format(pv_AttributeType)
            recommendation = "Specify one of the acceptable values ({}) for the AttributeType parameter.".format(
                acceptable_values)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            self.logger.warning(warning_message)
            raise CommandParameterError(warning_message)
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, geolayer_id: str, attribute_name: str) -> bool:
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
            self.logger.warning(message)
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
                self.logger.warning(message)
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

    def run_command(self) -> None:
        """
        Run the command. Add the attribute to the GeoLayer.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        # noinspection PyPep8Naming
        pv_AttributeName = self.get_parameter_value("AttributeName")
        # noinspection PyPep8Naming
        pv_AttributeType = self.get_parameter_value("AttributeType")
        # noinspection PyPep8Naming
        pv_InitialValue = self.get_parameter_value("InitialValue", default_value=None)

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.command_processor.expand_parameter_value(pv_GeoLayerID, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(pv_GeoLayerID, pv_AttributeName):
            # Run the process.
            # noinspection PyBroadException
            try:
                # Get the input GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Add the attribute to the GeoLayer.
                input_geolayer.add_attribute(pv_AttributeName, pv_AttributeType)

                # If the InitialValue parameter has been set, populate the added attribute with the given value.
                # Expand for ${Property} syntax.
                # noinspection PyPep8Naming
                pv_InitialValue = self.command_processor.expand_parameter_value(pv_InitialValue, self)
                if pv_InitialValue:
                    input_geolayer.populate_attribute(pv_AttributeName, pv_InitialValue)

            # Raise an exception if an unexpected error occurs during the process
            except Exception:
                self.warning_count += 1
                message = "Unexpected error adding attribute ({}) to GeoLayer {}.".format(pv_AttributeName,
                                                                                          pv_GeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
