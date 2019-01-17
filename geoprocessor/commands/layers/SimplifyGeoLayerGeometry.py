# SimplifyGeoLayerGeometry - command to simplify a GeoLayer's geometry
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
import geoprocessor.util.validator_util as validators
import geoprocessor.util.qgis_util as qgis_util

import logging
import os
from plugins.processing.tools import general


class SimplifyGeoLayerGeometry(AbstractCommand):

    """
    Simplifies the geometries in a line or polygon layer. The geometries are simplified by decreasing the number of
    vertices. A new GeoLayer is created with the simplified geometries.

    Command Parameters

    * GeoLayerID (str, required): the ID of the input GeoLayer, the layer to be clipped
    * Tolerance (float, required): a float representing to what extent the geometry should be simplified. The larger
        the number, the more simple the geometries and the smaller the output file size. According to this reference,
        https://gis.stackexchange.com/questions/148585/what-is-simplify-tolerance-in-qgiss-simplify-geometries-tool,
        "points are removed if the distance with the tentative simplified line is smaller than the tolerance". The
        units are the same at the CRS of the layer.
    * SimplifyMethod (str, optional): the method used to simplify the GeoLayer. Options are as follows:
        DouglasPeucker: use the Douglas-Peucker algorithm to simplify the GeoLayer
        Default: DouglasPeuker
    * SimplifiedGeoLaterID (str, optional): the ID of the simplified GeoLayer. By default, the simplified geolayer id
        is geolayerid_simple_tolerance where geolayerid is the GeoLayerID value and tolerance is the Tolerance value.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the SimplifiedGeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("Tolerance", type(2.5)),
        CommandParameterMetadata("SimplifyMethod", type(str)),
        CommandParameterMetadata("SimplifiedGeoLayerID", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "SimplifyGeoLayerGeometry"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = {}
        self.command_metadata['Description'] = ('This command decreases the number of vertices within the geometries '
                                                'for each feature of a GeoLayer.\nThis command is useful when the file '
                                                'size of a GeoLayer is too large.')
        self.command_metadata['EditorType'] = 'Generic'

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters):
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

        # Check that parameter GeoLayerID is a non-empty, non-None string.
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID', command_parameters=command_parameters)

        if not validators.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the a GeoLayer."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that parameter Tolerance is a non-empty, non-None string.
        pv_Tolerance = self.get_parameter_value(parameter_name='Tolerance', command_parameters=command_parameters)

        if not validators.validate_string(pv_Tolerance, False, False):
            message = "Tolerance parameter has no value."
            recommendation = "Specify the Tolerance parameter to indicate the simplification extent."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional parameter SimplifyMethod is either `DouglasPeucker` or None.
        pv_SimplifyMethod = self.get_parameter_value(parameter_name="SimplifyMethod",
                                                     command_parameters=command_parameters)
        acceptable_values = ["DouglasPeucker"]
        if not validators.validate_string_in_list(pv_SimplifyMethod, acceptable_values, none_allowed=True,
                                                  empty_string_allowed=True, ignore_case=True):
            message = "SimplifyMethod parameter value ({}) is not recognized.".format(pv_SimplifyMethod)
            recommendation = "Specify one of the acceptable values ({}) for the SimplifyMethod parameter.".format(
                acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional parameter IfGeoLayerIDExists is either `Replace`, `Warn`, `Fail` or None.
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

    def __should_simplify_geolayer(self, geolayer_id, simplified_geolayer_id):
        """
        Checks the following:
        * the ID of the GeoLayer is an existing GeoLayer ID
        * the geolayer is either a POLYGON or LINE type
        * the ID of the SimplifedGeoLayerID is unique (not an existing GeoLayer ID)

        Args:
            geolayer_id: the ID of the GeoLayer to be simplified

        Returns:
             Boolean. If TRUE, the GeoLayer should be simplified If FALSE, at least one check failed and the GeoLayer
                should not be simplified.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the GeoLayerID is not an existing GeoLayerID, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsGeoLayerIDExisting", "GeoLayerID", geolayer_id,
                                                       "FAIL"))

        # If the GeoLayer does not have POLYGON or LINE geometry, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "DoesGeoLayerIdHaveCorrectGeometry", "GeoLayerID",
                                                       geolayer_id, "FAIL", other_values=[["Polygon", "LineString"]]))

        # If the SimplifiedGeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE (depends
        # on the value of the IfGeoLayerIDExists parameter.)
        should_run_command.append(validators.run_check(self, "IsGeoLayerIdUnique", "SimplifiedGeoLayerID",
                                                       simplified_geolayer_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self):
        """
        Run the command. Simplify the GeoLayer by the tolerance.

        Returns:  None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_Tolerance = self.get_parameter_value("Tolerance")
        tolerance_float = float(pv_Tolerance)
        pv_SimplifyMethod = self.get_parameter_value("SimplifyMethod", default_value="DouglasPeucker").upper()
        default_simple_id = "{}_simple_{}".format(pv_GeoLayerID, pv_Tolerance)
        pv_SimplifiedGeoLayerID = self.get_parameter_value("SimplifiedGeoLayerID", default_value=default_simple_id)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_simplify_geolayer(pv_GeoLayerID, pv_SimplifiedGeoLayerID):

            try:

                # Get the GeoLayer.
                geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # If the GeoLayer is an in-memory GeoLayer, make it an on-disk GeoLayer.
                if geolayer.source_path is None or geolayer.source_path.upper() in ["", "MEMORY"]:

                    # Get the absolute path of the GeoLayer to write to disk.
                    geolayer_disk_abs_path = os.path.join(self.command_processor.get_property('TempDir'), geolayer.id)

                    # Write the GeoLayer to disk. Overwrite the (memory) GeoLayer in the geoprocessor with the
                    # on-disk GeoLayer.
                    geolayer = geolayer.write_to_disk(geolayer_disk_abs_path)
                    self.command_processor.add_geolayer(geolayer)

                # If the SimplifyMethod is DouglasPeucker, continue.
                if pv_SimplifyMethod == "DOUGLASPEUCKER":

                    # Perform the QGIS simplify geometries function. Refer to the REF below for parameter descriptions.
                    # REF: https://docs.qgis.org/2.8/en/docs/user_manual/processing_algs/qgis/
                    #       vector_geometry_tools/simplifygeometries.html
                    alg_parameters = {"INPUT": geolayer.qgs_vector_layer,
                                      "METHOD": 0,
                                      "TOLERANCE": tolerance_float,
                                      "OUTPUT": "memory:"}
                    simple_output = self.command_processor.qgis_processor.runAlgorithm("native:simplifygeometries",
                                                                                       alg_parameters)

                    # Create a new GeoLayer and add it to the GeoProcessor's geolayers list.
                    # in QGIS3, simple_output["OUTPUT"] returns the returns the QGS vector layer object
                    # see ClipGeoLayer.py for information about value in QGIS2 environment
                    new_geolayer = GeoLayer(pv_SimplifiedGeoLayerID, simple_output["OUTPUT"], "MEMORY")
                    self.command_processor.add_geolayer(new_geolayer)

            # Raise an exception if an unexpected error occurs during the process.
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error simplifying GeoLayer {}.".format(pv_GeoLayerID)
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
