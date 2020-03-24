# CreateGeoLayer - command to create a GeoLayer
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
from geoprocessor.core.GeoLayer import GeoLayer
from geoprocessor.core.VectorGeoLayer import VectorGeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import logging


class CreateGeoLayer(AbstractCommand):
    """
    Creates a new GeoLayer. The feature geometry is provided by the parameters.

    Command Parameters
    * GeoLayerID (str, required): The ID of the new GeoLayer.
    * GeometryFormat (str, required): The format of the input geometry. Can be `BoundingBox`, `WKT` or `WKB`. Refer
        to user documentation for descriptions of each geometry format.
    * GeometryInput (str, required): The geometry data in the format specified by the GeometryFormat parameter.
    * CRS (str, required): The coordinate reference system of the new GeoLayer. The units of the GeometryInput must
        match the units of the CRS.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the GeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("GeometryFormat", type(str)),
        CommandParameterMetadata("GeometryInput", type(str)),
        CommandParameterMetadata("CRS", type(str)),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "CreateGeoLayer"
        self.command_parameter_metadata = self.__command_parameter_metadata

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

        # Check that GeometryFormat parameter is either `BoundingBox`, `WKT` or `WKB`.
        # noinspection PyPep8Naming
        pv_GeometryFormat = self.get_parameter_value(parameter_name="GeometryFormat",
                                                     command_parameters=command_parameters)
        acceptable_values = ["BoundingBox", "WKT", "WKB"]
        if not validator_util.validate_string_in_list(pv_GeometryFormat, acceptable_values, none_allowed=False,
                                                      empty_string_allowed=False, ignore_case=True):
            message = "GeometryFormat parameter value ({}) is not recognized.".format(pv_GeometryFormat)
            recommendation = "Specify one of the acceptable values ({}) for the GeometryFormat parameter.".format(
                acceptable_values)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional IfGeoLayerIDExists param is either `Replace`, `Warn`, `Fail`, `ReplaceAndWarn` or None.
        # noinspection PyPep8Naming
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        acceptable_values = ["Replace", "Warn", "Fail", "ReplaceAndWarn"]
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
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, geolayer_id: str, crs: str, geometry_format: str, geometry_input: str) -> bool:
        """
        Checks the following:
        * the CRS is a valid CRS
        * the ID of the new GeoLayer is unique (not an existing GeoLayer ID)
        * if the GeometryFormat is BoundingBox, check that the string has 4 items

        Args:
            geolayer_id: the id of the GeoLayer to be created
            crs: the crs code of the GeoLayer to be created
            geometry_format: the format that the geometry data is delivered
            geometry_input: the geometry data (as a string)

        Returns:
             Boolean. If TRUE, the GeoLayer should be created.
             If FALSE, at least one check failed and the GeoLayer should not be created.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the CRS is not a valid coordinate reference system code, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsCRSCodeValid", "CRS", crs, "FAIL"))

        # If the GeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE
        # (depends on the value of the IfGeoLayerIDExists parameter.)
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIdUnique", "GeoLayerID", geolayer_id, None))

        # If the GeometryFormat is BoundingBox, continue with the checks.
        if geometry_format.upper() == "BOUNDINGBOX":

            # If the GeometryInput string does not contain 4 items when converted to a list, raise a FAILURE.
            should_run_command.append(validator_util.run_check(self, "IsListLengthCorrect", "GeometryInput",
                                                               geometry_input, "FAIL", other_values=[",", 4]))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Create the GeoLayer with the input geometries. Add GeoLayer to the GeoProcessor's geolayers
         list.

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
        pv_GeometryFormat = self.get_parameter_value("GeometryFormat").upper()
        # noinspection PyPep8Naming
        pv_GeometryInput = self.get_parameter_value("GeometryInput")
        # noinspection PyPep8Naming
        pv_CRS = self.get_parameter_value("CRS")

        if self.check_runtime_data(pv_GeoLayerID, pv_CRS, pv_GeometryFormat, pv_GeometryInput):
            # noinspection PyBroadException
            try:
                layer = None
                qgs_geometry = None
                # If the geometry format is bounding box, continue.
                # noinspection PyPep8Naming
                if pv_GeometryFormat == "BOUNDINGBOX":
                    # Convert the geometry input from a string to a list of strings.
                    # Items are in the following order:
                    #   1. Left (West) bound coordinate
                    #   2. Bottom (South) bound coordinate
                    #   3. Right (East) bound coordinate
                    #   4. Top (North) bound coordinate
                    nswe_extents = string_util.delimited_string_to_list(pv_GeometryInput)
                    nw = "{} {}".format(nswe_extents[0], nswe_extents[3])
                    ne = "{} {}".format(nswe_extents[2], nswe_extents[3])
                    se = "{} {}".format(nswe_extents[2], nswe_extents[1])
                    sw = "{} {}".format(nswe_extents[0], nswe_extents[1])
                    wkt_conversion = "POLYGON(({}, {}, {}, {}))".format(nw, ne, se, sw)

                    # Create the QgsVectorLayer. BoundingBox will always create a POLYGON layer.
                    layer = qgis_util.create_qgsvectorlayer("Polygon", pv_CRS, "layer")

                    # Create the QgsGeometry object for the bounding box geometry.
                    qgs_geometry = qgis_util.create_qgsgeometry("WKT", wkt_conversion)

                elif pv_GeometryFormat == "WKT":
                    # If the geometry format is Well-Known Text, continue.

                    # Get the equivalent QGS geometry type to the input WKT geometry.
                    # Ex: MultiLineString is converted to LineString.
                    qgsvectorlayer_geom_type = qgis_util.get_geometrytype_qgis_from_wkt(pv_GeometryInput)

                    # Create the QgsVectorLayer. The geometry type will be determined from the WKT specifications.
                    layer = qgis_util.create_qgsvectorlayer(qgsvectorlayer_geom_type, pv_CRS, "layer")

                    # Create the QgsGeometry object for the Well-Known Text geometry.
                    qgs_geometry = qgis_util.create_qgsgeometry("WKT", pv_GeometryInput)

                elif pv_GeometryFormat == "WKB":
                    # If the geometry format is Well-Known Binary, continue.

                    # Create the QgsGeometry object for the Well-Known Binary geometry.
                    qgs_geometry = qgis_util.create_qgsgeometry("WKB", pv_GeometryInput)

                    # Get the equivalent Well-Known Text for the geometry.
                    qgs_geometry_as_wkt = qgs_geometry.exportToWkt()

                    # Get the equivalent QGS geometry type to the input WKT geometry.
                    # Ex: MultiLineString is converted to LineString.
                    qgsvectorlayer_geom_type = qgis_util.get_geometrytype_qgis_from_wkt(qgs_geometry_as_wkt)

                    # Create the QgsVectorLayer. The geometry type will be determined from the WKB specifications.
                    layer = qgis_util.create_qgsvectorlayer(qgsvectorlayer_geom_type, pv_CRS, "layer")

                # Add the feature (with the appropriate geometry) to the Qgs Vector Layer.
                qgis_util.add_feature_to_qgsvectorlayer(layer, qgs_geometry)

                # Create a new GeoLayer with the QgsVectorLayer and add it to the GeoProcesor's geolayers list.
                new_geolayer = VectorGeoLayer(geolayer_id=pv_GeoLayerID,
                                              qgs_vector_layer=layer,
                                              input_path_full=GeoLayer.SOURCE_MEMORY,
                                              input_path=GeoLayer.SOURCE_MEMORY)
                self.command_processor.add_geolayer(new_geolayer)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process.

                self.warning_count += 1
                message = "Unexpected error creating GeoLayer ({}).".format(pv_GeoLayerID)
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
