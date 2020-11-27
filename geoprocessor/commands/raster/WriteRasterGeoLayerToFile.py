# WriteRasterGeoLayerToFile - command to write a rster GeoLayer to a file
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

from qgis.core import QgsRasterFileWriter, QgsRasterPipe, QgsCoordinateTransformContext

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandError import CommandError
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.validator_util as validator_util

import logging


class WriteRasterGeoLayerToFile(AbstractCommand):
    """
    Write a raster GeoLayer to a raster data file (any recognized file extension).
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", str),
        CommandParameterMetadata("OutputFile", str),
        CommandParameterMetadata("OutputCRS", str)]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Write a raster GeoLayer to a file."
    __command_metadata['EditorType'] = "Simple"

    # Parameter Metadata
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "GeoLayer identifier"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = (
        "GeoLayer identifier for the layer to write.  Formatting characters and ${Property} syntax is recognized.")
    # OutputFile
    __parameter_input_metadata['OutputFile.Description'] = "Raster file to write"
    __parameter_input_metadata['OutputFile.Label'] = "Raster file to write"
    __parameter_input_metadata['OutputFile.Tooltip'] = \
        "The raster file to write (relative or absolute path, must have recognized extension)." + \
        "${Property} syntax is recognized."
    __parameter_input_metadata['OutputFile.Required'] = True
    __parameter_input_metadata['OutputFile.FileSelector.Type'] = "Write"
    # OutputCRS
    __parameter_input_metadata['OutputCRS.Description'] = "coordinate reference system of the raster"
    __parameter_input_metadata['OutputCRS.Label'] = "Output CRS"
    __parameter_input_metadata['OutputCRS.Tooltip'] = (
        "The coordinate reference system of the output raster file. EPSG or ESRI code format required "
        "(e.g. EPSG:4326, EPSG:26913, ESRI:102003).\n"
        "If the output CRS is different than the CRS of the GeoLayer, the output GeoJSON is reprojected "
        "to the new CRS.")

    def __init__(self) -> None:
        """
        Initialize the command
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "WriteRasterGeoLayerToFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

        # Parameter Metadata
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

    def check_runtime_data(self, output_file_abs: str, geolayer_id: str) -> bool:
        """
        Checks the following:
        * the output file parent folder (absolute) is a valid folder
        * the ID of the GeoLayer exists

        Args:
            geolayer_id (str): the ID of the GeoLayer to write
            output_file_abs (str): the full pathname to the output file

        Returns:
            run_read: Boolean. If TRUE, the command should be run. If FALSE, the command should not be run.
        """

        # Boolean to determine if the process should be run. Set to true until an error occurs.
        should_run_command = list()

        # If the GeoLayer ID is not an existing GeoLayer ID, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIdExisting", "GeoLayerID", geolayer_id,
                                                           "FAIL"))

        # If the folder of the OutputFile file path is not a valid folder, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "DoesFilePathHaveAValidFolder", "OutputFile",
                                                           output_file_abs, "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Read the layer file from a raster format file, create a GeoLayer object, and add to the
        GeoProcessor's geolayer list.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID", default_value='%f')
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value("OutputFile")
        # noinspection PyPep8Naming
        pv_OutputCRS = self.get_parameter_value("OutputCRS")

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.command_processor.expand_parameter_value(pv_GeoLayerID, self)
        # noinspection PyPep8Naming
        pv_OutputCRS = self.command_processor.expand_parameter_value(pv_OutputCRS, self)

        # Convert the OutputFile parameter value relative path to an absolute path and expand for ${Property} syntax
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(output_file_absolute, pv_GeoLayerID):
            # noinspection PyBroadException
            try:
                # Get the GeoLayer
                geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Write the raster layer to a file
                # See:  https://python.hotexamples.com/examples/qgis.core/QgsRasterFileWriter/
                #             writeRaster/python-qgsrasterfilewriter-writeraster-method-examples.html
                file_writer = QgsRasterFileWriter(output_file_absolute)
                pipe = QgsRasterPipe()
                qgs_raster_layer = geolayer.qgs_layer
                provider = qgs_raster_layer.dataProvider()
                if not pipe.set(provider.clone()):
                    self.warning_count += 1
                    message = "Error setting pipe for raster output."
                    recommendation = "Check the log file for details."
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
                else:
                    # Handle output CRS.
                    # TODO smalers 2020-07-17 not sure how to handle the transfer
                    # - how does it differ from the CRS function parameter?
                    if pv_OutputCRS is not None and pv_OutputCRS != "":
                        crs = qgis_util.parse_qgs_crs(pv_OutputCRS)
                        if crs is None:
                            # Default the layer CRS and generate an error
                            crs = qgs_raster_layer.crs()
                            self.warning_count += 1
                            message = "Requested output CRS {} is invalid, keeping the original CRS {}.".format(
                                pv_OutputCRS, crs)
                            recommendation = "Confirm that the output CRS is valid."
                            self.logger.warning(message, exc_info=True)
                            self.command_status.add_to_log(CommandPhaseType.RUN,
                                                           CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                            recommendation))
                    else:
                        # Default to outputting the same CRS as the input layer
                        crs = qgs_raster_layer.crs()
                    # crs_string should not be needed
                    crs_string = ""
                    #crs_transform = QgsCoordinateTransformContext(qgs_raster_layer.crs(), crs, crs_string)
                    crs_transform = QgsCoordinateTransformContext()
                    # pipe = None
                    output_file_ext = io_util.get_extension(output_file_absolute)
                    # Get specific output options.
                    options = []
                    if output_file_ext.upper() == 'TIF':
                        self.logger.info("Using TIF compression and tiles for output file.")
                        # Set the create options so output is compressed and optimized for the web.
                        # See cloud optimized GeoTIFF:  https://trac.osgeo.org/gdal/wiki/CloudOptimizedGeoTIFF
                        options = [
                            #"EXTRA": '-co TILED=YES -co COPY_SRC_OVERVIEWS=YES -co COMPRESS=LZW'
                            #"OPTIONS": 'TILED=YES,COPY_SRC_OVERVIEWS=YES,COMPRESS=LZW'
                            "TILED=YES",
                            "COPY_SRC_OVERVIEWS=YES",
                            "COMPRESS=LZW"
                        ]
                    file_writer.setCreateOptions(options)
                    file_writer.writeRaster(
                        pipe,
                        provider.xSize(),
                        provider.ySize(),
                        provider.extent(),
                        crs,
                        # qgs_raster_layer.crs(),
                        crs_transform  # seems to be redundant with crs - is QGIS migrating design?
                    )

            except Exception:
                self.warning_count += 1
                message = "Unexpected error writing RasterGeoLayer {} to raster file {}.".format(
                    pv_GeoLayerID, output_file_absolute)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise RuntimeError if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
