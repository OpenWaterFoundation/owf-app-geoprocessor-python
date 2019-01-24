# CreateGeoLayerFromGeometry - command to create a GeoLayer from geometry
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

from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validators

import logging


class CreateGeoLayerFromGeometry(AbstractCommand):

    """
    Creates a new GeoLayer. The feature geometry is provided by the parameters.

    Command Parameters
    * NewGeoLayerID (str, required): The ID of the new GeoLayer.
    * GeometryFormat (str, required): The format of the input geometry. Can be `BoundingBox`, `WKT` or `WKB`. Refer
        to user documentation for descriptions of each geometry format.
    * GeometryData (str, required): The geometry data in the format specified by the GeometryFormat parameter.
    * CRS (str, required): The coordinate reference system of the new GeoLayer. The units of the GeometryData must
        match the units of the CRS.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the NewGeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("NewGeoLayerID", type("")),
        CommandParameterMetadata("GeometryFormat", type(str)),
        CommandParameterMetadata("GeometryData", type(str)),
        CommandParameterMetadata("CRS", type(str)),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "CreateGeoLayerFromGeometry"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = "This command creates a new GeoLayer from input geometry data."
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # NewGeoLayerID
        self.parameter_input_metadata['NewGeoLayerID.Description'] = "the id of the new GeoLayer"
        self.parameter_input_metadata['NewGeoLayerID.Label'] = "New GeoLayerID"
        self.parameter_input_metadata['NewGeoLayerID.Required'] = True
        self.parameter_input_metadata['NewGeoLayerID.Tooltip'] = "The ID of the new GeoLayer."
        # GeometryFormat
        self.parameter_input_metadata['GeometryFormat.Description'] = "the format of the GeometryData"
        self.parameter_input_metadata['GeometryFormat.Label'] = "Geometry Format"
        self.parameter_input_metadata['GeometryFormat.Required'] = True
        self.parameter_input_metadata['GeometryFormat.Tooltip'] = "The format of the GeometryData. Choose from one of "\
            "the options below. \nWKT: Well-Known Text is text representing vector geometry. \nBoundingBox: " \
            "Bounding Box Coordinates are a list of 4 coordinates representing the minimum and maximum " \
            "latitude and longitude of a POLYGON vector. \nWKB: Well-Known Binary is hexadecimal text representing " \
            "vector geometry. \nOnly available with QGIS version 3.0 or later. "
        self.parameter_input_metadata['GeometryFormat.Values'] = ["", "WKT", "BoundingBox", "WKB"]
        # GeometryData
        self.parameter_input_metadata['GeometryData.Description'] = "the geometry data for the new GeoLayer"
        self.parameter_input_metadata['GeometryData.Label'] = "Geometry Data"
        self.parameter_input_metadata['GeometryData.Required'] = True
        self.parameter_input_metadata['GeometryData.Tooltip'] = "The geometry data for the new GeoLayer. \nThe units " \
            "are the same as the units of the coordinate reference system (CRS). \n" \
            "If GeometryFormat is WKT... \nuse the syntax provided in the reference. If " \
            "GeometryFormat is BoundingBox... \nspecify the coordinates as comma-separated values in the " \
            "following order. \n    the left bound (minimum longitude) the bottom bound (minimum latitude) \n    " \
            "the right bound \n    (maximum longitude) the top \n    (maximum latitude) bound \n" \
            "If GeometryFormat is WKB... \nuse the syntax provided in the reference. \n" \
            "Only available with QGIS version 3.0 or later. "
        # CRS
        self.parameter_input_metadata['CRS.Description'] = "the coordinate references system of the new GeoLayer"
        self.parameter_input_metadata['CRS.Label'] = "CRS"
        self.parameter_input_metadata['CRS.Required'] = True
        self.parameter_input_metadata['CRS.Tooltip'] = "The coordinate reference system of the new GeoLayer. EPSG or " \
            "ESRI code format required (e.g. EPSG:4326, EPSG:26913, ESRI:102003). "
        # IfGeoLayerIDExists
        self.parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID Exists"
        self.parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = "The action that occurs if the NewGeoLayerID " \
            "already exists within the GeoProcessor. \nReplace : The existing GeoLayer within the " \
            "GeoProcessor is overwritten with the new GeoLayer. No warning is logged. \n" \
            "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new " \
            "GeoLayer. A warning is logged. \nWarn : The new GeoLayer is not created. A warning is logged. \n"\
            "Fail : The new GeoLayer is not created. A fail message is logged. "
        self.parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
        self.parameter_input_metadata['IfGeoLayerIdExists.Value.Default'] = "Replace"

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

        parameters = ["NewGeoLayerID", "GeometryData", "CRS"]

        # Check that the parameters are non-empty, non-None strings.
        for parameter in parameters:

            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)

            if not validators.validate_string(parameter_value, False, False):
                message = "{} parameter has no value.".format(parameter)
                recommendation = "Specify the {} parameter.".format(parameter)
                warning += "\n" + message
                self.command_status.add_to_log(
                    CommandPhaseType.INITIALIZATION,
                    CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that GeometryFormat parameter is either `BoundingBox`, `WKT` or `WKB`.
        pv_GeometryFormat = self.get_parameter_value(parameter_name="GeometryFormat",
                                                     command_parameters=command_parameters)
        acceptable_values = ["BoundingBox", "WKT", "WKB"]
        if not validators.validate_string_in_list(pv_GeometryFormat, acceptable_values, none_allowed=False,
                                                  empty_string_allowed=False, ignore_case=True):
            message = "GeometryFormat parameter value ({}) is not recognized.".format(pv_GeometryFormat)
            recommendation = "Specify one of the acceptable values ({}) for the GeometryFormat parameter.".format(
                acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional IfGeoLayerIDExists param is either `Replace`, `Warn`, `Fail`, `ReplaceAndWarn` or None.
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        acceptable_values = ["Replace", "Warn", "Fail", "ReplaceAndWarn"]
        if not validators.validate_string_in_list(pv_IfGeoLayerIDExists, acceptable_values, none_allowed=True,
                                                  empty_string_allowed=True, ignore_case=True):
            message = "IfGeoLayerIDExists parameter value ({}) is not recognized.".format(pv_IfGeoLayerIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfGeoLayerIDExists parameter.".format(
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

    def __should_geolayer_be_created(self, geolayer_id, crs, geometry_format, geometry_data):
        """
        Checks the following:
        * the CRS is a valid CRS
        * the ID of the new GeoLayer is unique (not an existing GeoLayer ID)
        * if the GeometryFormat is BoundingBox, check that the string has 4 items

        Args:
            geolayer_id: the id of the GeoLayer to be created
            crs: the crs code of the GeoLayer to be created
            geometry_format: the format that the geometry data is delivered
            geometry_data: the geometry data (as a string)

        Returns:
             Boolean. If TRUE, the GeoLayer should be simplified If FALSE, at least one check failed and the GeoLayer
                should not be simplified.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the CRS is not a valid coordinate reference system code, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsCRSCodeValid", "CRS", crs, "FAIL"))

        # If the new GeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE
        # (depends on the value of the IfGeoLayerIDExists parameter.)
        should_run_command.append(validators.run_check(self, "IsGeoLayerIdUnique", "NewGeoLayerID", geolayer_id, None))

        # If the GeometryFormat is BoundingBox, continue with the checks.
        if geometry_format.upper() == "BOUNDINGBOX":

            # If the GeometryData string does not contain 4 items when converted to a list, raise a FAILURE.
            should_run_command.append(validators.run_check(self, "IsListLengthCorrect", "GeometryData",
                                                           geometry_data, "FAIL", other_values=[",", 4]))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self):
        """
        Run the command. Create the GeoLayer with the input geometries. Add GeoLayer to the GeoProcessor's geolayers
         list.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_NewGeoLayerID = self.get_parameter_value("NewGeoLayerID")
        pv_GeometryFormat = self.get_parameter_value("GeometryFormat").upper()
        pv_GeometryData = self.get_parameter_value("GeometryData")
        pv_CRS = self.get_parameter_value("CRS")

        if self.__should_geolayer_be_created(pv_NewGeoLayerID, pv_CRS, pv_GeometryFormat, pv_GeometryData):

            try:

                # If the geometry format is bounding box, continue.
                if pv_GeometryFormat == "BOUNDINGBOX":

                    # Convert the geometry input from a string to a list of strings.
                    # Items are in the following order:
                    #   1. Left (West) bound coordinate
                    #   2. Bottom (South) bound coordinate
                    #   3. Right (East) bound coordinate
                    #   4. Top (North) bound coordinate
                    NSWE_extents = string_util.delimited_string_to_list(pv_GeometryData)
                    NW = "{} {}".format(NSWE_extents[0], NSWE_extents[3])
                    NE = "{} {}".format(NSWE_extents[2], NSWE_extents[3])
                    SE = "{} {}".format(NSWE_extents[2], NSWE_extents[1])
                    SW = "{} {}".format(NSWE_extents[0], NSWE_extents[1])
                    wkt_conversion = "POLYGON(({}, {}, {}, {}))".format(NW, NE, SE, SW)

                    # Create the QgsVectorLayer. BoundingBox will always create a POLYGON layer.
                    layer = qgis_util.create_qgsvectorlayer("Polygon", pv_CRS, "layer")

                    # Create the QgsGeometry object for the bounding box geometry.
                    qgs_geometry = qgis_util.create_qgsgeometry("WKT", wkt_conversion)

                # If the geometry format is Well-Known Text, continue.
                elif pv_GeometryFormat == "WKT":

                    # Get the equivalent QGS geometry type to the input WKT geometry.
                    # Ex: MultiLineString is converted to LineString.
                    qgsvectorlayer_geom_type = qgis_util.get_geometrytype_qgis_from_wkt(pv_GeometryData)

                    # Create the QgsVectorLayer. The geometry type will be determined from the WKT specifications.
                    layer = qgis_util.create_qgsvectorlayer(qgsvectorlayer_geom_type, pv_CRS, "layer")

                    # Create the QgsGeometry object for the Well-Known Text geometry.
                    qgs_geometry = qgis_util.create_qgsgeometry("WKT", pv_GeometryData)

                # If the geometry format is Well-Known Binary, continue.
                elif pv_GeometryFormat == "WKB":

                    # Create the QgsGeometry object for the Well-Known Binary geometry.
                    qgs_geometry = qgis_util.create_qgsgeometry("WKB", pv_GeometryData)

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
                new_geolayer = GeoLayer(pv_NewGeoLayerID, layer, "MEMORY")
                self.command_processor.add_geolayer(new_geolayer)

            # Raise an exception if an unexpected error occurs during the process.
            except Exception as e:

                self.warning_count += 1
                message = "Unexpected error creating GeoLayer ({}).".format(pv_NewGeoLayerID)
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
