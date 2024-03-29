# CreatePointsAlongLine - command to create point layer along a line
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

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
# import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.validator_util as validator_util

import logging


class CreatePointsAlongLine(AbstractCommand):
    """
    Creates a copy of a GeoLayer in the GeoProcessor's geolayers list.
    The copied GeoLayer is added to the GeoProcessor's geolayers list.

    Command Parameters:

    * GeoLayerID (str, required): The ID of the existing GeoLayer to copy.
    * CopiedGeoLayerID (str, optional): The ID of the copied GeoLayer. Default "{}_copy".format(GeoLayerID)
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the CopiedGeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("CopiedGeoLayerID", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data.
        super().__init__()
        self.command_name = "CreatePointsAlongLine"
        self.command_parameter_metadata = self.__command_parameter_metadata

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

        # Check that optional parameter IfGeoLayerIDExists is either `Replace`, `ReplaceAndWarn`, `Warn`, `Fail`, None.
        # noinspection PyPep8Naming
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        acceptable_values = ["Replace", "ReplaceAndWarn", "Warn", "Fail"]
        if not validator_util.validate_string_in_list(pv_IfGeoLayerIDExists, acceptable_values, none_allowed=True,
                                                      empty_string_allowed=True, ignore_case=True):
            message = "IfGeoLayerIDExists parameter value ({}) is not recognized.".format(pv_IfGeoLayerIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfGeoLayerIDExists parameter.".format(
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
            # Refresh the phase severity.
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, input_geolayer_id: str, output_geolayer_id: str) -> bool:
        """
        Checks the following:
        * the ID of the input GeoLayer is an existing GeoLayer ID
        * the geometry of the input GeoLayer is a LineString
        * check that distance is greater than 0

        Args:
            input_geolayer_id: the ID of the input GeoLayer
            output_geolayer_id: the ID of the output, copied GeoLayer

        Returns:
            run_copy: Boolean. If TRUE, the copy process should be run. If FALSE, the copy process should not be run.
        """

        # Boolean to determine if the copy process should be run. Set to true until an error occurs.
        run_copy = True

        # If the input GeoLayer ID is not an existing GeoLayer ID, raise a FAILURE.
        if not self.command_processor.get_geolayer(input_geolayer_id):

            run_copy = False
            self.warning_count += 1
            message = 'The GeoLayerID ({}) is not a valid GeoLayer ID.'.format(input_geolayer_id)
            recommendation = 'Specify a valid GeoLayerID.'
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message,
                                                            recommendation))

        # If the output GeoLayer ID is the same as an already-registered GeoLayerID,
        # react according to the pv_IfGeoLayerIDExists value.
        elif self.command_processor.get_geolayer(output_geolayer_id):
            # Get the IfGeoLayerIDExists parameter value.
            # noinspection PyPep8Naming
            pv_IfGeoLayerIDExists = self.get_parameter_value("IfGeoLayerIDExists", default_value="Replace")

            # Warnings/recommendations if the OutputGeolayerID is the same as a registered GeoLayerID.
            message = 'The CopiedGeoLayerID ({}) value is already in use as a GeoLayer ID.'.format(output_geolayer_id)
            recommendation = 'Specify a new GeoLayerID.'

            if pv_IfGeoLayerIDExists.upper() == "REPLACEANDWARN":
                # The registered GeoLayer should be replaced with the new GeoLayer (with warnings).

                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING,
                                                                message, recommendation))

            if pv_IfGeoLayerIDExists.upper() == "WARN":
                # The registered GeoLayer should not be replaced. A warning should be logged.

                run_copy = False
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING,
                                                                message, recommendation))

            elif pv_IfGeoLayerIDExists.upper() == "FAIL":
                # The matching IDs should cause a FAILURE.

                run_copy = False
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE,
                                                                message, recommendation))

        # Return the Boolean to determine if the copy process should be run. If TRUE, all checks passed.
        # If FALSE, one or many checks failed.
        return run_copy

    def run_command(self) -> None:
        """
        Run the command. Make a copy of the GeoLayer and add the copied GeoLayer to the GeoProcessor's geolayers list.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0
