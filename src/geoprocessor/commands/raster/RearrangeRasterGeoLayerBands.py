# RearrangeRasterGeoLayerBands - command to rearrange raster GeoLayer bands
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
from geoprocessor.core.GeoLayer import GeoLayer
from geoprocessor.core.QGISAlgorithmProcessingFeedbackHandler import QgisAlgorithmProcessingFeedbackHandler
from geoprocessor.core.RasterGeoLayer import RasterGeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import logging


class RearrangeRasterGeoLayerBands(AbstractCommand):
    """
    Rearrange a raster GeoLayer's bands, including option to omit bands.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", str),
        CommandParameterMetadata("Bands", str),
        CommandParameterMetadata("OutputGeoLayerID", str)]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = (
        "Rearrange the bands of a raster GeoLayer, including changing the order and the band to include.\n"
        "The layer can be updated or a new layer created."
    )
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "GeoLayer identifier"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = "The ID of the GeoLayer."
    # CRS
    __parameter_input_metadata['Bands.Description'] = "bands"
    __parameter_input_metadata['Bands.Label'] = "Bands"
    __parameter_input_metadata['Bands.Required'] = True
    __parameter_input_metadata['Bands.Tooltip'] = "List of band numbers, separated by commas "
    # OutputGeoLayerID
    __parameter_input_metadata['OutputGeoLayerID.Description'] = "the output GeoLayerID"
    __parameter_input_metadata['OutputGeoLayerID.Label'] = "Output GeoLayerID"
    __parameter_input_metadata['OutputGeoLayerID.Required'] = False
    __parameter_input_metadata['OutputGeoLayerID.Tooltip'] = "The output GeoLayerID."

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data.
        super().__init__()
        self.command_name = "RearrangeRasterGeoLayerBands"
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

    def check_runtime_data(self, geolayer_id: str, bands: [int]) -> bool:
        """
        Checks the following:
         * The ID of the input GeoLayer is an actual GeoLayer (if not, log an error message & do not continue.)
         * The input geolayer includes the requested band numbers

        Args:
            geolayer_id (str): the ID of the GeoLayer to add the new attribute
            bands ([int]): list of bands, each value 1+

        Returns:
            run_ok: Boolean. If TRUE, OK to run. If FALSE, command should not be run.
        """

        # Boolean to determine if the CRS should be set. Set to TRUE until one or many checks fail.
        run_ok = True

        input_geolayer = self.command_processor.get_geolayer(geolayer_id)
        if geolayer_id is None:
            # If the input GeoLayer does not exist, FAILURE.
            run_ok = False
            self.warning_count += 1
            message = 'The input GeoLayer ID ({}) does not exist.'.format(geolayer_id)
            recommendation = 'Specify a valid GeoLayerID.'
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        else:
            # Make sure that the bands are provided as a comma-separated list of integers.
            for band in bands:
                if (band < 1) or (band > input_geolayer.get_num_bands()):
                    run_ok = False
                    self.warning_count += 1
                    message = 'The input GeoLayer ({}) does not have band {}.  Cannot rearrange band.'.format(
                        geolayer_id, band)
                    recommendation = 'Specify a band 1 to {}.'.format(input_geolayer.get_num_bands())
                    self.logger.warning(message)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.WARNING, message, recommendation))

        # Return the Boolean to determine if the crs should be set. If TRUE, all checks passed.
        # If FALSE, one or many checks failed.
        return run_ok

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
        pv_Bands = self.get_parameter_value("Bands")
        # noinspection PyPep8Naming
        pv_OutputGeoLayerID = self.get_parameter_value("OutputGeoLayerID")

        # Convert the pv_GeoLayerID parameter to expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.command_processor.expand_parameter_value(pv_GeoLayerID, self)
        # noinspection PyPep8Naming
        pv_Bands = self.command_processor.expand_parameter_value(pv_Bands, self)
        # noinspection PyPep8Naming
        pv_OutputGeoLayerID = self.command_processor.expand_parameter_value(pv_OutputGeoLayerID, self)

        bands = []
        if (pv_Bands is not None) and (pv_Bands != ''):
            bands = string_util.delimited_string_to_int_list(pv_Bands, ",")

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(pv_GeoLayerID, bands):
            # Run the process.

            raster_output_file = None
            # noinspection PyBroadException
            try:
                # Get the input GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Rearrange the layer bands:
                # - output is to a temporary file so have to read it

                # Get the temporary folder based on TemporaryFolder parameter:
                # - for now use the system temporary folder
                output_ext = "tif"
                raster_output_file = io_util.create_tmp_filename('gp', 'rearrange_bands', output_ext)
                self.logger.info("Temporary file is: {}".format(raster_output_file))

                # See:
                #   https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/gdal/rasterconversion.html
                #      #rearrange-bands
                # GeoTIF OPTIONS:
                # https://gdal.org/drivers/raster/gtiff.html#raster-gtiff
                #
                # See cloud optimized GeoTIFF:  https://trac.osgeo.org/gdal/wiki/CloudOptimizedGeoTIFF

                # The following parameters are for GeoTIFF.
                alg_parameters = {
                    # Generic parameters regardless of output format.
                    "INPUT": input_geolayer.qgs_layer,
                    "BANDS": bands,
                    "OUTPUT": str(raster_output_file),
                    # The following are for GeoTIFF.
                    "OPTIONS": "TILED=YES|COPY_SRC_OVERVIEWS=YES|COMPRESS=LZW",
                }
                feedback_handler = QgisAlgorithmProcessingFeedbackHandler(self)
                alg_output = qgis_util.run_processing(processor=self.command_processor.qgis_processor,
                                                      algorithm="gdal:rearrange_bands",
                                                      algorithm_parameters=alg_parameters,
                                                      feedback_handler=feedback_handler)
                self.warning_count += feedback_handler.get_warning_count()
                # Output is a dictionary.
                self.logger.info("Algorithm output: {}".format(alg_output))

                # Create a new QgsRasterLayer from the temporary file:
                # - output file name should be the same as specified but get from results to confirm
                rearranged_layer = qgis_util.read_qgsrasterlayer_from_file(alg_output['OUTPUT'])
                self.logger.info("Layer metadata after rearranging bands:")
                qgis_util.log_raster_metadata(rearranged_layer, logger=self.logger)

                if (pv_OutputGeoLayerID is not None) and (pv_OutputGeoLayerID != ''):
                    # Use the new GeoLayerID.
                    new_geolayer_id = pv_OutputGeoLayerID
                else:
                    # Use the existing GeoLayerID.
                    new_geolayer_id = pv_GeoLayerID

                # Create a new GeoLayer from the temporary file and add it to the GeoProcessor's geolayers list.
                new_geolayer = RasterGeoLayer(geolayer_id=new_geolayer_id,
                                              qgs_raster_layer=rearranged_layer,
                                              name=input_geolayer.name,
                                              description=input_geolayer.description,
                                              input_path_full=GeoLayer.SOURCE_MEMORY,
                                              input_path=GeoLayer.SOURCE_MEMORY)

                self.command_processor.add_geolayer(new_geolayer)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process.
                self.warning_count += 1
                message = "Unexpected error rearranging GeoLayer {} bands to {}".format(pv_GeoLayerID, pv_Bands)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
            finally:
                # Remove the temporary file to optimize disk space use.
                if raster_output_file is not None:
                    io_util.remove_tmp_file(raster_output_file)

        # Determine success of command processing. Raise Runtime Error if any errors occurred.
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
