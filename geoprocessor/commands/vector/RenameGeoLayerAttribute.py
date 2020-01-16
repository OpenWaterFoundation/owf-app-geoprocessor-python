# RenameGeoLayerAttribute - command to rename GeoLayer attributes
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


class RenameGeoLayerAttribute(AbstractCommand):

    """
    Renames a GeoLayer's attribute.

    * This command renames a single GeoLayer attribute.
    * The existing attribute name is specified.
    * The new attribute name is specified.

    Command Parameters
    * GeoLayerID (str, required): the ID of the input GeoLayer, the layer with the attribute to rename.
    * ExistingAttributeName (str, required): the name of the attribute to rename. Must be a valid attribute name.
    * NewAttributeName (str, required): the new attribute name. Must be a unique attribute name to the GeoLayer. If
        working with Esri Shapefiles, it is highly recommended that the string is 10 characters or less.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("ExistingAttributeName", type("")),
        CommandParameterMetadata("NewAttributeName", type(""))]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "RenameGeoLayerAttribute"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = "Rename a single attribute in a GeoLayer."
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # GeoLayerID
        self.parameter_input_metadata['GeoLayerID.Description'] = "GeoLayer identifier"
        self.parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
        self.parameter_input_metadata['GeoLayerID.Required'] = True
        self.parameter_input_metadata['GeoLayerID.Tooltip'] = \
            "The ID of the GeoLayer with the attribute to be renamed."
        # ExistingAttributeName
        self.parameter_input_metadata['ExistingAttributeName.Description'] = "existing attribute name"
        self.parameter_input_metadata['ExistingAttributeName.Label'] = "Existing attribute name"
        self.parameter_input_metadata['ExistingAttributeName.Required'] = True
        self.parameter_input_metadata['ExistingAttributeName.Tooltip'] =\
            "The name of the existing attribute to be renamed. Case-specific."
        # NewAttributeName
        self.parameter_input_metadata['NewAttributeName.Description'] = "new attribute name"
        self.parameter_input_metadata['NewAttributeName.Label'] = "New attribute name"
        self.parameter_input_metadata['NewAttributeName.Required'] = True
        self.parameter_input_metadata['NewAttributeName.Tooltip'] = (
            "The new attribute name, recommended to be 10 or less characters if later output as a shapefile, "
            "case-specific.")

        # Class data
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
        warning = ""

        # Check that parameters GeoLayerID and is a non-empty, non-None string.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID', command_parameters=command_parameters)

        if not validator_util.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the input GeoLayer."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that parameter ExistingAttributeName is a non-empty, non-None string.
        # noinspection PyPep8Naming
        pv_ExistingAttributeName = self.get_parameter_value(parameter_name='ExistingAttributeName',
                                                            command_parameters=command_parameters)

        if not validator_util.validate_string(pv_ExistingAttributeName, False, False):

            message = "ExistingAttributeName parameter has no value."
            recommendation = "Specify the ExistingAttributeName parameter to indicate the name of the attribute to" \
                             " rename."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that parameter NewAttributeName is a non-empty, non-None string.
        # noinspection PyPep8Naming
        pv_NewAttributeName = self.get_parameter_value(parameter_name='NewAttributeName',
                                                       command_parameters=command_parameters)

        if not validator_util.validate_string(pv_NewAttributeName, False, False):
            message = "NewAttributeName parameter has no value."
            recommendation = "Specify the NewAttributeName parameter to indicate the new name of the renamed attribute."
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

    def __should_attribute_be_renamed(self, geolayer_id: str, existing_attribute_name: str,
                                      new_attribute_name: str) -> bool:
        """
        Checks the following:
         * The ID of the input GeoLayer is an actual GeoLayer (if not, log an error message & do not continue.)
         * The exiting attribute name is a valid name for the GeoLayer (if not, log an error message & do not continue.)
         * The new attribute name is a unique name for the GeoLayer (if not, log an error message & do not continue.)
         * The new attribute name is 10 or less characters (if not, log a warning but still rename the attribute.)

        Args:
            geolayer_id (str): the ID of the GeoLayer to add the new attribute
            existing_attribute_name (str): the name of the existing attribute to rename.
            new_attribute_name (str): the name of the new attribute name. The attribute will be renamed to this value.

        Returns:
            rename_attribute: Boolean. If TRUE, the attribute should be renamed. If FALSE, a check has failed and the
            attribute should not be renamed.
        """

        # Boolean to determine if the attribute should be renamed. Set to TRUE until one or many checks fail.
        rename_attribute = True

        # If the input GeoLayer does not exist, raise a FAILURE.
        if not self.command_processor.get_geolayer(geolayer_id):

            rename_attribute = False
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

            # If the existing attribute name is not valid, raise a FAILURE.
            if existing_attribute_name not in list_of_existing_attributes:

                rename_attribute = False
                self.warning_count += 1
                message = 'The existing attribute name ({}) is not valid.'.format(existing_attribute_name)
                recommendation = 'Specify a valid attribute name. Valid attributes for this layer are as follows: ' \
                                 '{}'.format(list_of_existing_attributes)
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

            # If the new attribute name is not unique to the attribute table, raise a FAILURE.
            if new_attribute_name in list_of_existing_attributes:

                rename_attribute = False
                self.warning_count += 1
                message = 'The new attribute name ({}) is not unique.'.format(new_attribute_name)
                recommendation = 'Specify a unique attribute name.'
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

            # If the new attribute name is longer than 10 characters, raise a WARNING.
            if len(new_attribute_name) > 10:

                self.warning_count += 1
                message = 'The new attribute name ({}) is longer than 10 characters. Esri Shapefiles require the' \
                          ' attribute names to be 10 or less characters.'.format(new_attribute_name)
                recommendation = 'If this GeoLayer will be written in shapefile format, change the attribute name to' \
                                 ' only include 10 or less characters.'
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING, message, recommendation))

        # Return the Boolean to determine if the attribute should be renamed. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return rename_attribute

    def run_command(self) -> None:
        """
        Run the command. Add the attribute to the GeoLayer.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        # noinspection PyPep8Naming
        pv_ExistingAttributeName = self.get_parameter_value("ExistingAttributeName")
        # noinspection PyPep8Naming
        pv_NewAttributeName = self.get_parameter_value("NewAttributeName")

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_attribute_be_renamed(pv_GeoLayerID, pv_ExistingAttributeName, pv_NewAttributeName):

            # Run the process.
            # noinspection PyBroadException
            try:

                # Get the input GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Rename the GeoLayer's attribute.
                input_geolayer.rename_attribute(pv_ExistingAttributeName, pv_NewAttributeName)

            # Raise an exception if an unexpected error occurs during the process
            except Exception:
                self.warning_count += 1
                message = "Unexpected error renaming attribute ({}) of GeoLayer ({})" \
                          " to new name of '{}'.".format(pv_ExistingAttributeName, pv_GeoLayerID, pv_NewAttributeName)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
