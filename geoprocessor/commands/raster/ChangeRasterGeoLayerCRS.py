# ChangeRasterGeoLayerCRS - command to change raster GeoLayer coordinate reference system (CRS)
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
from geoprocessor.core.RasterGeoLayer import RasterGeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.validator_util as validator_util

from datetime import datetime
import logging
import os
from pathlib import Path
import tempfile


class ChangeRasterGeoLayerCRS(AbstractCommand):
    """
    Change a raster GeoLayer's coordinate reference system (CRS)
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", str),
        CommandParameterMetadata("CRS", str),
        CommandParameterMetadata("OutputGeoLayerID", str)]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = (
        "Change the coordinate reference system (CRS) of a raster GeoLayer.\n"
        "The layer can be updated or a new layer created."
    )
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "GeoLayer identifier"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = "The ID of the GeoLayer."
    # CRS
    __parameter_input_metadata['CRS.Description'] = "coordinate references system"
    __parameter_input_metadata['CRS.Label'] = "CRS"
    __parameter_input_metadata['CRS.Required'] = True
    __parameter_input_metadata['CRS.Tooltip'] = (
        "The coordinate reference system of the GeoLayer. "
        "EPSG or ESRI code format required (e.g. EPSG:4326, EPSG:26913, ESRI:102003).")
    # OutputGeoLayerID
    __parameter_input_metadata['OutputGeoLayerID.Description'] = "the output GeoLayerID"
    __parameter_input_metadata['OutputGeoLayerID.Label'] = "Output GeoLayerID"
    __parameter_input_metadata['OutputGeoLayerID.Required'] = False
    __parameter_input_metadata['OutputGeoLayerID.Tooltip'] = "The output GeoLayerID."

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "ChangeRasterGeoLayerCRS"
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
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, geolayer_id: str, crs_code: str) -> bool:
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

        if self.command_processor.get_geolayer(geolayer_id) is None:
            # If the input GeoLayer does not exist, FAILURE.
            set_crs = False
            input_geolayer_exists = False
            self.warning_count += 1
            message = 'The input GeoLayer ID ({}) does not exist.'.format(geolayer_id)
            recommendation = 'Specify a valid GeoLayerID.'
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        if qgis_util.parse_qgs_crs(crs_code) is None:
            # If the input CRS code is not a valid code, FAILURE.
            set_crs = False
            self.warning_count += 1
            message = 'The input CRS ({}) is not a valid CRS code.'.format(crs_code)
            recommendation = 'Specify a valid CRS code (EPSG codes are an approved format).'
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # If the input CRS code is that same as the GeoLayer's current CRS, raise a WARNING.
        if input_geolayer_exists and self.command_processor.get_geolayer(geolayer_id).get_crs_code():
            if crs_code.upper() == self.command_processor.get_geolayer(geolayer_id).get_crs_code().upper():
                set_crs = False
                self.warning_count += 1
                message = 'The input GeoLayer ({}) already is projected to the input' \
                          ' CRS ({}).'.format(geolayer_id, crs_code)
                recommendation = 'The SetGeoLayerCRS command will not run. Specify a different CRS code.'
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING, message, recommendation))

        # Return the Boolean to determine if the crs should be set. If TRUE, all checks passed. If FALSE, one or many
        # checks failed.
        return set_crs

    def run_command(self) -> None:
        """
        Run the command.

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
        pv_CRS = self.get_parameter_value("CRS")
        # noinspection PyPep8Naming
        pv_OutputGeoLayerID = self.get_parameter_value("OutputGeoLayerID")

        # Convert the pv_GeoLayerID parameter to expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.command_processor.expand_parameter_value(pv_GeoLayerID, self)
        # noinspection PyPep8Naming
        pv_OutputGeoLayerID = self.command_processor.expand_parameter_value(pv_OutputGeoLayerID, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(pv_GeoLayerID, pv_CRS):
            # Run the process.
            # noinspection PyBroadException
            try:
                # Get the input GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Check if the input GeoLayer has an existing CRS.
                if input_geolayer.get_crs_code():
                    # Reproject the GeoLayer.
                    # - output is to a temporary file so have to read it

                    # Get the temporary folder based on TemporaryFolder parameter
                    # - for now use the system temporary folder
                    now = datetime.today()
                    nowstring = '{:04d}-{:02d}-{:02d}-{:02d}-{:02d}-{:02d}.{}'.format(now.year, now.month, now.day,
                                                                                      now.hour, now.minute,
                                                                                      now.second, now.microsecond)
                    output_ext = "tif"
                    raster_output_file = Path(tempfile.gettempdir()).joinpath('gp-{}-warpreproject-{}.{}'.format(
                        os.getpid(),
                        nowstring,
                        output_ext))
                    self.logger.info("Temporary file is: {}".format(raster_output_file))

                    # See:
                    # https://docs.qgis.org/latest/en/docs/user_manual/processing_algs/gdal/rasterprojections.html
                    #    #warp-reproject
                    # GeoTIF OPTIONS:
                    # https://gdal.org/drivers/raster/gtiff.html#raster-gtiff
                    #
                    # See cloud optimized GeoTIFF:  https://trac.osgeo.org/gdal/wiki/CloudOptimizedGeoTIFF
                    # TODO smlers 2020-11-25 don't know how to pass the options
                    options = [
                        "TILED=YES",
                        "COPY_SRC_OVERVIEWS=YES",
                        "COMPRESS=LZW"
                    ]
                    alg_parameters = {
                        "INPUT": input_geolayer.qgs_layer,
                        "TARGET_CRS": pv_CRS,
                        # "OPTIONS": 'TILED=YES,COPY_SRC_OVERVIEWS=YES,COMPRESS=LZW',
                        # "OPTIONS": options,
                        # "EXTRA": '-co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW',
                        "TILED": "YES",
                        "COPY_SRC_OVERVIEWS": "YES",
                        "COMPRESS": "LZW",
                        #"EXTRA": '-co COMPRESS=LZW',
                        "OUTPUT": str(raster_output_file)
                    }
                    alg_output = self.command_processor.qgis_processor.runAlgorithm("gdal:warpreproject",
                                                                                    alg_parameters)
                    # Output is a dictionary
                    self.logger.info("Algorithm output: {}".format(alg_output))

                    # Create a new QgsRasterLayer from the temporary file.
                    # - output file name should be the same as specified but get from results to confirm
                    reprojected_layer = qgis_util.read_qgsrasterlayer_from_file(alg_output['OUTPUT'])
                    self.logger.info("Layer metadata after changing CRS:")
                    qgis_util.log_raster_metadata(reprojected_layer, logger=self.logger)

                    if (pv_OutputGeoLayerID is not None) and (pv_OutputGeoLayerID != ''):
                        # Use the new GeoLayerID
                        new_geolayer_id = pv_OutputGeoLayerID
                    else:
                        # Use the existing GeoLayerID
                        new_geolayer_id = pv_GeoLayerID

                    # Create a new GeoLayer from the temporary file and add it to the GeoProcessor's geolayers list.
                    new_geolayer = RasterGeoLayer(geolayer_id=new_geolayer_id,
                                                  qgs_raster_layer=reprojected_layer,
                                                  name=input_geolayer.name,
                                                  description=input_geolayer.description,
                                                  input_path_full=GeoLayer.SOURCE_MEMORY,
                                                  input_path=GeoLayer.SOURCE_MEMORY)

                    self.command_processor.add_geolayer(new_geolayer)

                    # TODO smalers 2020-11-24 remove temporary file to optimize disk space use.

                else:
                    # Input layer must have CRS defined in order to change the CRS
                    self.warning_count += 1
                    message = "Input layer {} does not have CRS - cannot change".format(pv_GeoLayerID)
                    recommendation = "Set the layer CRS when reading or creating."
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

            except Exception:
                # Raise an exception if an unexpected error occurs during the process
                self.warning_count += 1
                message = "Unexpected error changing GeoLayer {} CRS to {}".format(pv_GeoLayerID, pv_CRS)
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
