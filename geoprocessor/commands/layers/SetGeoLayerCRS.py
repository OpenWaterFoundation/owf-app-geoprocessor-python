# SetGeoLayerCRS - command to set GeoLayer coordinate reference system (CRS)
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
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.validator_util as validators

import logging

from plugins.processing.tools import general


class SetGeoLayerCRS(AbstractCommand):

    """
    Sets a GeoLayer's coordinate reference system (CRS)

    * If the GeoLayer already has a CRS, this command will reset the GeoLayer's CRS to the new CRS.

    Command Parameters
    * GeoLayerID (str, required): the ID of the input GeoLayer, the layer to set the CRS.
    * CRS (str, EPSG/ESRI code, required): the CRS to set for the GeoLayer.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("CRS", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "SetGeoLayerCRS"
        self.command_description = "sets a GeoLayer's coordinate reference system"
        self.command_parameter_metadata = self.__command_parameter_metadata

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

        # Check that parameters GeoLayerID and is a non-empty, non-None string.
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID', command_parameters=command_parameters)

        if not validators.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the input GeoLayer."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that parameter CRS is a non-empty, non-None string.
        pv_CRS = self.get_parameter_value(parameter_name='CRS', command_parameters=command_parameters)

        if not validators.validate_string(pv_CRS, False, False):

            message = "CRS parameter has no value."
            recommendation = "Specify the CRS parameter to indicate the new coordinate reference system."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def __should_set_crs(self, geolayer_id, crs_code):
        """
        Checks the following:
         * The ID of the input GeoLayer is an actual GeoLayer (if not, log an error message & do not continue.)
         * The CRS is a valid coordinate reference system code.
         * The CRS is difference than the GeoLayer's CRS.

        Args:
            geolayer_id (str): the ID of the GeoLayer to add the new attribute
            crs_code (str): the CRS to set for the GeoLayer (EPSG or ESRI code)

        Returns:
            set_crs: Boolean. If TRUE, the CRS should be set. If FALSE, a check has failed & the CRS should not be set.
        """

        # Boolean to determine if the CRS should be set. Set to TRUE until one or many checks fail.
        set_crs = True

        # Boolean to determine if the input GeoLayer id is a valid GeoLayer ID. Set to TRUE until proved False.
        input_geolayer_exists = True

        # If the input GeoLayer does not exist, raise a FAILURE.
        if not self.command_processor.get_geolayer(geolayer_id):

            set_crs = False
            input_geolayer_exists = False
            self.warning_count += 1
            message = 'The input GeoLayer ID ({}) does not exist.'.format(geolayer_id)
            recommendation = 'Specify a valid GeoLayerID.'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # If the input CRS code is not a valid code, raise a FAILURE.
        if qgis_util.get_qgscoordinatereferencesystem_obj(crs_code) is None:

            set_crs = False
            self.warning_count += 1
            message = 'The input CRS ({}) is not a valid CRS code.'.format(geolayer_id)
            recommendation = 'Specify a valid CRS code (EPSG codes are an approved format).'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # If the input CRS code is that same as the GeoLayer's current CRS, raise a WARNING.
        if input_geolayer_exists and self.command_processor.get_geolayer(geolayer_id).get_crs():

            if crs_code.upper() == self.command_processor.get_geolayer(geolayer_id).get_crs().upper():

                set_crs = False
                self.warning_count += 1
                message = 'The input GeoLayer ({}) already is projected to the input' \
                          ' CRS ({}).'.format(geolayer_id, crs_code)
                recommendation = 'The SetGeoLayerCRS command will not run. Specify a different CRS code.'
                self.logger.warning(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.WARNING, message, recommendation))

        # Return the Boolean to determine if the crs should be set. If TRUE, all checks passed. If FALSE, one or many
        # checks failed.
        return set_crs

    def run_command(self):
        """
        Run the command. Set the GeoLayer coordinate reference system.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_CRS = self.get_parameter_value("CRS")

        # Convert the pv_GeoLayerID parameter to expand for ${Property} syntax.
        pv_GeoLayerID = self.command_processor.expand_parameter_value(pv_GeoLayerID, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_set_crs(pv_GeoLayerID, pv_CRS):

            # Run the process.
            try:

                # Get the input GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Check if the input GeoLayer already has an assigned CRS.
                if input_geolayer.get_crs():

                    # Reproject the GeoLayer.
                    alg_parameters = {"INPUT": input_geolayer.qgs_vector_layer,
                                      "TARGET_CRS": pv_CRS,
                                      "OUTPUT": "memory:"}
                    reprojected = self.command_processor.qgis_processor.runAlgorithm("native:reprojectlayer",
                                                                                     alg_parameters)

                    # Create a new GeoLayer and add it to the GeoProcessor's geolayers list.

                    # In QGIS 2 the reprojected["OUTPUT"] returned the full file pathname of the memory output layer
                    # (saved in a QGIS temporary folder)
                    # qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_file(reprojected["OUTPUT"])
                    # new_geolayer = GeoLayer(input_geolayer.id, qgs_vector_layer, "MEMORY")

                    # In QGIS 3 the reprojected["OUTPUT"] returns the QGS vector layer object
                    new_geolayer = GeoLayer(input_geolayer.id, reprojected["OUTPUT"], "MEMORY")
                    self.command_processor.add_geolayer(new_geolayer)

                else:
                    alg_parameters = {"INPUT": input_geolayer.qgs_vector_layer,
                                      "CRS": pv_CRS}
                    self.command_processor.qgis_processor.runAlgorithm("qgis:definecurrentprojection", alg_parameters)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error setting CRS ({}) of GeoLayer ({})".format(pv_CRS, pv_GeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.error(message, exc_info=True)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
