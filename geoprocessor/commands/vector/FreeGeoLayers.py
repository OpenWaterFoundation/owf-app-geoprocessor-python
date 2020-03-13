# FreeGeoLayers - command to free GeoLayer(s)
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
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import logging


class FreeGeoLayers(AbstractCommand):
    """
    Removes one or more GeoLayers from the GeoProcessor.

    Command Parameters
    * GeoLayerIDs (str, required): A comma-separated list of the IDs of the existing GeoLayers to free.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerIDs", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Remove one or more GeoLayers from the GeoProcessor."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # GeoLayersIDs
    __parameter_input_metadata['GeoLayerIDs.Description'] = \
        "comma-separated list of the ID's of the GeoLayers to free"
    __parameter_input_metadata['GeoLayerIDs.Label'] = "GeoLayersIDs"
    __parameter_input_metadata['GeoLayerIDs.Required'] = True
    __parameter_input_metadata['GeoLayerIDs.Tooltip'] = (
        "A comma-separated list of the IDs of the GeoLayers to free. \n"
        "Can also be *, which will remove all GeoLayers. ")

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "FreeGeoLayers"
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

        Returns: None

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning = ""

        # Check that parameter GeoLayerIDs is a non-empty, non-None string.
        # noinspection PyPep8Naming
        pv_GeoLayerIDs = self.get_parameter_value(parameter_name='GeoLayerIDs',
                                                  command_parameters=command_parameters)

        if not validator_util.validate_string(pv_GeoLayerIDs, False, False):
            message = "GeoLayerIDs parameter has no value."
            recommendation = "Specify the GeoLayerIDs parameter to indicate the GeoLayer to copy."
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

    def __should_geolayer_be_deleted(self, geolayer_id_list: [str]) -> bool:
        """
        Checks the following:
        * the IDs of the input GeoLayers are existing GeoLayer IDs

        Args:
            geolayer_id_list: an id list of the GeoLayers to be removed

        Returns:
            Boolean. If TRUE, the file should be extracted. If FALSE, at least one check failed and the file should
            not be extracted.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # Iterate over the GeoLayerIDs in the GeoLayerIDList.
        for geolayer_id in geolayer_id_list:

            # If the geolayer_id is not a valid GeoLayer ID, raise a FAILURE.
            should_run_command.append(validator_util.run_check(self, "IsGeoLayerIdExisting", "GeoLayerID", geolayer_id,
                                                               "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Remove the GeoLayer object from the GeoProcessor. Delete the GeoLayer instance.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_GeoLayerIDs = self.get_parameter_value("GeoLayerIDs")

        # Convert the GeoLayerIDs parameter from string to list format.
        # If configured, list all of the registered GeoLayer IDs.
        if pv_GeoLayerIDs == "*":
            list_of_geolayer_ids = []

            # Iterate over each GeoLayer registered within the GeoProcessor. Add each GeoLayer's ID to the list.
            for geolayer_obj in self.command_processor.geolayers:
                list_of_geolayer_ids.append(geolayer_obj.id)

        # If specific GeoLayer IDs are listed, convert the string into list format.
        else:
            list_of_geolayer_ids = string_util.delimited_string_to_list(pv_GeoLayerIDs)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_geolayer_be_deleted(list_of_geolayer_ids):

            # noinspection PyBroadException
            try:

                # Iterate over the GeoLayer IDS.
                for geolayer_id in list_of_geolayer_ids:

                    # Get GeoLayer to remove.
                    geolayer = self.command_processor.get_geolayer(geolayer_id)

                    # Remove the GeoLayer from the GeoProcessor's geolayers list.
                    index = self.command_processor.geolayers.index(geolayer)
                    del self.command_processor.geolayers[index]

                    # Delete the Qgs Vector Layer object.
                    del geolayer.qgs_layer

                    # Delete the GeoLayer.
                    del geolayer

            except Exception:
                # Raise an exception if an unexpected error occurs during the process.

                self.warning_count += 1
                message = "Unexpected error removing GeoLayer ({}).".format(pv_GeoLayerIDs)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
