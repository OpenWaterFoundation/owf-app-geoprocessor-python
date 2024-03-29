# RemoveGeoLayerAttributes - command to remove GeoLayer attributes
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


class RemoveGeoLayerAttributes(AbstractCommand):

    """
    Removes one or more attributes from a GeoLayer.

    * The names of the attributes to remove are specified.

    Command Parameters:

    * GeoLayerID (str, required): the ID of the input GeoLayer, the layer to remove the attribute from
    * AttributeNames (str, required): the names of the attributes to remove. Strings separated by commas. Attribute
        names must be valid attribute fields to the GeoLayer. This parameter is case specific.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("AttributeNames", type(""))]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = "Removes one or more attributes from a GeoLayer."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "GeoLayer identifier"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = "The ID of the GeoLayer with the attribute to be removed."
    # AttributeNames
    __parameter_input_metadata['AttributeNames.Description'] = "names of the attributes to remove"
    __parameter_input_metadata['AttributeNames.Label'] = "Attribute Names"
    __parameter_input_metadata['AttributeNames.Required'] = True
    __parameter_input_metadata['AttributeNames.Tooltip'] = \
        "The names of the attributes to be removed, separated by commas, case-specific."

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data.
        super().__init__()
        self.command_name = "RemoveGeoLayerAttributes"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display.
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata.
        self.parameter_input_metadata = self.__parameter_input_metadata

        # Class data.
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters: dict) -> None:
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns: None.

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

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            self.logger.warning(warning_message)
            raise CommandParameterError(warning_message)
        else:
            # Refresh the phase severity.
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, geolayer_id: str, attribute_names: [str]) -> bool:
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
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # If the input GeoLayer does exist, continue with the checks.
        else:

            # Get the input GeoLayer object.
            input_geolayer = self.command_processor.get_geolayer(geolayer_id)

            # Get the existing attribute names of the input GeoLayer.
            list_of_existing_attributes = input_geolayer.get_attribute_field_names()

            # Create a list of invalid input attribute names.
            # An invalid attribute name is an input attribute name
            # that is not matching any of the existing attribute names of the GeoLayer.
            invalid_attrs = (attr_name for attr_name in attribute_names if attr_name not in list_of_existing_attributes)

            # Iterate over the invalid input attribute names and raise a FAILURE for each.
            for invalid_attr in invalid_attrs:

                remove_attribute = False
                self.warning_count += 1
                message = 'The attribute name ({}) is not valid.'.format(invalid_attr)
                recommendation = 'Specify a valid attribute name. Valid attributes for this layer are' \
                                 ' as follows: {}'.format(list_of_existing_attributes)
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Return the Boolean to determine if the attribute should be removed. If TRUE, all checks passed.
        # If FALSE, one or many checks failed.
        return remove_attribute

    def run_command(self) -> None:
        """
        Run the command. Remove the attribute from the GeoLayer.

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
        pv_AttributeNames = self.get_parameter_value("AttributeNames")

        # Convert the AttributeNames parameter from a string to a list.
        attribute_names_list = string_util.delimited_string_to_list(pv_AttributeNames)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(pv_GeoLayerID, attribute_names_list):
            # Run the process.
            # noinspection PyBroadException
            try:
                # Get the input GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Iterate over the input attributes to remove.
                for attribute_name in attribute_names_list:
                    # Remove the attribute from the GeoLayer.
                    input_geolayer.remove_attribute(attribute_name)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process.

                self.warning_count += 1
                message = "Unexpected error removing attribute(s) ({}) from GeoLayer {}.".format(pv_AttributeNames,
                                                                                                 pv_GeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred.
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
