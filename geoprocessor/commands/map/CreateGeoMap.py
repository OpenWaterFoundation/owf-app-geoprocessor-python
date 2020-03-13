# CreateGeoMap - command to create a new GeoMap
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

from geoprocessor.core.GeoMap import GeoMap

import geoprocessor.util.command_util as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import logging


class CreateGeoMap(AbstractCommand):
    """
    Creates a new GeoMap.

    Command Parameters
    * NewGeoMapId (str, required): The identifier for the new GeoMap.
    * GeoMapName (str, required): The name of the new GeoMap, used for displays.
    * Description (str, optional): The description of the new GeoMap, used for displays.
    * CRS (str, required): The coordinate reference system for the new GeoMap.
    * IfGeoMapIdExists (str, optional): This parameter determines the action that occurs if the GeoMapId
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("NewGeoMapId", type("")),
        CommandParameterMetadata("GeoMapName", type("")),
        CommandParameterMetadata("CRS", type("")),
        CommandParameterMetadata("IfGeoMapIdExists", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Create a new GeoMap, for display and to save the map configuration."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # NewGeoMapId
    __parameter_input_metadata['NewGeoMapId.Description'] = "identifier for the new GeoMap"
    __parameter_input_metadata['NewGeoMapId.Label'] = "New GeoMapId"
    __parameter_input_metadata['NewGeoMapId.Required'] = True
    __parameter_input_metadata['NewGeoMapId.Tooltip'] = "The identifier for the new GeoMap."
    # GeoMapName
    __parameter_input_metadata['GeoMapName.Description'] = "name for the new GeoMap"
    __parameter_input_metadata['GeoMapName.Label'] = "Name"
    __parameter_input_metadata['GeoMapName.Required'] = True
    __parameter_input_metadata['GeoMapName.Tooltip'] = "The name for the new GeoMap."
    # Description
    __parameter_input_metadata['Description.Description'] = "description for the new GeoMap"
    __parameter_input_metadata['Description.Label'] = "Description"
    __parameter_input_metadata['Description.Required'] = True
    __parameter_input_metadata['Description.Tooltip'] = "The description for the new GeoMap."
    # CRS
    __parameter_input_metadata['CRS.Description'] = "coordinate references system for the new GeoMap"
    __parameter_input_metadata['CRS.Label'] = "CRS"
    __parameter_input_metadata['CRS.Required'] = True
    __parameter_input_metadata['CRS.Tooltip'] = (
        "The coordinate reference system of the new GeoMap. EPSG or "
        "ESRI code format required (e.g. EPSG:4326, EPSG:26913, ESRI:102003).")
    # IfGeoMapIdExists
    __parameter_input_metadata['IfGeoMapIdExists.Description'] = "action if map exists"
    __parameter_input_metadata['IfGeoMapIdExists.Label'] = "If GeoMapId exists"
    __parameter_input_metadata['IfGeoMapIdExists.Tooltip'] = (
        "The action that occurs if the NewGeoMapId already exists within the GeoProcessor.\n"
        "Replace: The existing GeoMap within the GeoProcessor is replaced with the new GeoMap. "
        "No warning is logged.\n"
        "ReplaceAndWarn: The existing GeoMap within the GeoProcessor is replaced with the new GeoMap. "
        "A warning is logged.\n"
        "Warn: The new GeoMap is not created. A warning is logged.\n"
        "Fail: The new GeoMap is not created. A fail message is logged.")
    __parameter_input_metadata['IfGeoMapIdExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
    __parameter_input_metadata['IfGeoMapIdExists.Value.Default'] = "Replace"

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "CreateGeoMap"
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

        warning = ""

        parameters = ["NewGeoMapId", "GeoMapName", "CRS"]

        # Check that the parameters are non-empty, non-None strings.
        for parameter in parameters:

            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)

            if not validator_util.validate_string(parameter_value, False, False):
                message = "{} parameter has no value.".format(parameter)
                recommendation = "Specify the {} parameter.".format(parameter)
                warning += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional IfGeoMapIdExists param is either `Replace`, `Warn`, `Fail`, `ReplaceAndWarn` or None.
        # noinspection PyPep8Naming
        pv_IfGeoMapIdExists = self.get_parameter_value(parameter_name="IfGeoMapIdExists",
                                                       command_parameters=command_parameters)
        acceptable_values = ["Replace", "Warn", "Fail", "ReplaceAndWarn"]
        if not validator_util.validate_string_in_list(pv_IfGeoMapIdExists, acceptable_values, none_allowed=True,
                                                      empty_string_allowed=True, ignore_case=True):
            message = "IfGeoMapIdExists parameter value ({}) is not recognized.".format(pv_IfGeoMapIdExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfGeoMapIdExists parameter.".format(
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

    def __should_geomap_be_created(self, geomap_id: str, crs: str):
        """
        Checks the following:
        * the CRS is a valid CRS
        * the identifier of the new GeoMap is unique (not an existing GeoMapId)

        Args:
            geomap_id: the id of the GeoMap to be created
            crs: the crs code of the GeoMap to be created

        Returns:
             Boolean. If TRUE, the GeoMap should be created.
             If FALSE, at least one check failed and the GeoMap should not be created.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the CRS is not a valid coordinate reference system code, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsCRSCodeValid", "CRS", crs, "FAIL"))

        # If the GeoMapId is the same as an already-existing GeoMapId, raise a WARNING or FAILURE
        # (depends on the value of the IfGeoMapIdExists parameter.)
        should_run_command.append(validator_util.run_check(self, "IsGeoMapIdUnique", "GeoMapId", geomap_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Create the GeoMap.  Add the GeoMap to the GeoProcessor's geomaps list.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_GeoMapId = self.get_parameter_value("GeoMapId")
        # noinspection PyPep8Naming
        pv_GeoMapName = self.get_parameter_value("GeoMapName")
        # noinspection PyPep8Naming
        pv_CRS = self.get_parameter_value("CRS")

        if self.__should_geomap_be_created(pv_GeoMapId, pv_CRS):

            # noinspection PyBroadException
            try:
                layer = None
                # Add the map (with the appropriate geometry) to the Qgs map list.
                # TODO smalers 2020-03-09 need to decide if manage a list of QGIS maps or just GeoProcessor form
                # qgis_util.add_map_to_qgsmaplayer(layer, xxx)

                # Create a new GeoMap and add it to the GeoProcesor's geomaps list.
                new_geomap = GeoMap(geomap_id=pv_GeoMapId, geomap_name=pv_GeoMapName, crs=pv_CRS)
                self.command_processor.add_geolayer(new_geomap)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process.

                self.warning_count += 1
                message = "Unexpected error creating GeoMap ({}).".format(pv_GeoMapId)
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
