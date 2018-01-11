# WriteGeoLayerToShapefile

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.geo as geo_util
import geoprocessor.util.io as io_util
import geoprocessor.util.validators as validators

from qgis.core import QgsVectorFileWriter, QgsCoordinateReferenceSystem

import os
import logging


class WriteGeoLayerToShapefile(AbstractCommand):
    # TODO egiles 2018-01-04 Need to add information about Shapefile spatial data files in the docstring.

    """
    Writes a GeoLayer to a spatial data file in Shapefile format.

    This command writes a GeoLayer registered within the geoprocessor to a spatial date file in Shapefile format (a
    suite of multiple files). The Shapefile spatial data files can then be viewed within a GIS, moved within folders on
    the local computer, packaged for delivery, etc.

    Registered GeoLayers are stored as GeoLayer objects within the geoprocessor's GeoLayers list. Each GeoLayer has one
    feature type (point, line, polygon, etc.) and other data (an identifier, a coordinate reference system, etc). This
    function only writes one single GeoLayer to a single spatial data file in Shapefile format.
    """

    # Command Parameters
    # GeoLayerID (str, required): the identifier of the GeoLayer to be written to a spatial data file in Shapefile
    #   format
    # OutputFilename (str, required): the relative pathname of the output spatial data file.
    # OutputCRS (str, EPSG code, optional): the coordinate reference system that the output spatial data file will be
    #   projected. By default, the output spatial data file will be projected to the GeoLayer's current CRS.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("OutputFilename", type("")),
        CommandParameterMetadata("OutputCRS", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        super(WriteGeoLayerToShapefile, self).__init__()
        self.command_name = "WriteGeoLayerToShapefile"
        self.command_parameter_metadata = self.__command_parameter_metadata

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            Nothing.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """

        warning = ""
        logger = logging.getLogger(__name__)

        # Check that parameter GeoLayerID is a non-empty, non-None string.
        # - existence of the GeoLayer will also be checked in run_command().
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID',
                                                 command_parameters=command_parameters)

        if not validators.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the GeoLayer to write."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that parameter OutputFilename is a non-empty, non-None string.
        # - existence of the folder will also be checked in run_command().
        pv_OutputFilename = self.get_parameter_value(parameter_name='OutputFilename',
                                                     command_parameters=command_parameters)

        if not validators.validate_string(pv_OutputFilename, False, False):
            message = "OutputFilename parameter has no value."
            recommendation = "Specify the OutputFilename parameter (relative or absolute pathname) to indicate the " \
                             "location and name of the output spatial data file in GeoJSON format."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def run_command(self):
        """
        Run the command. Write the GeoLayer to a spatial data file in Shapefile format to the folder OutputFolder.

        Args:
            None.

        Returns:
            Nothing.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Set up logger and warning count
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Obtain the parameter values except for the OutputCRS
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_OutputFilename = self.get_parameter_value("OutputFilename")

        # Convert the OutputFilename parameter value relative path to an absolute path and expand for ${Property} syntax
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFilename, self)))

        # Check that the output folder is a valid folder
        output_folder = os.path.dirname(output_file_absolute)
        if os.path.isdir(output_folder):

            # Check that the GeoLayerID is a valid registered GeoLayer ID in the GeoProcessor
            if self.command_processor.get_geolayer(pv_GeoLayerID):

                try:

                    # Get the GeoLayer
                    geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                    # Get the current coordinate reference system (in EPSG code) of the current GeoLayer
                    geolayer_crs = geolayer.get_crs()

                    # Obtain the parameter value of the OutputCRS
                    pv_OutputCRS = self.get_parameter_value("OutputCRS", default_value=geolayer_crs)

                    # Get the QGSVectorLayer object for the GeoLayer
                    qgs_vector_layer = geolayer.qgs_vector_layer

                    # Write the GeoLayer to a spatial data file in Shapefile format
                    # Reference: `QGIS API Documentation <https://qgis.org/api/classQgsVectorFileWriter.html>_`
                    # To use the QgsVectorFileWriter.writeAsVectorFormat tool, the following sequential arguments are
                    # defined:
                    #   1. vectorFileName: the QGSVectorLayer object that is to be written to a spatial data format
                    #   2. path to new file: the full pathname (including filename) of the output file
                    #   3. output text encoding: always set to "utf-8"
                    #   4. destination coordinate reference system
                    #   5. driver name for the output file
                    # Note to developers: IGNORE `Unexpected Argument` error for layerOptions. This value is
                    # appropriate and functions properly.
                    QgsVectorFileWriter.writeAsVectorFormat(qgs_vector_layer,
                                                            output_file_absolute,
                                                            "utf-8",
                                                            QgsCoordinateReferenceSystem(pv_OutputCRS),
                                                            "ESRI Shapefile",
                                                            )

                # Raise an exception if an unexpected error occurs during the process
                except Exception as e:
                    print "FAILURE ---------------------------"
                    warning_count += 1
                    message = "Unexpected error writing GeoLayer {} to spatial data file in Shapefile format.".format(
                        pv_GeoLayerID)
                    recommendation = "Check the log file for details."
                    logger.exception(message, e)
                    self.command_status.add_to_log(command_phase_type.RUN,
                                                   CommandLogRecord(command_status_type.FAILURE, message,
                                                                    recommendation))

            # If the GeoLayerID is not a valid registered GeoLayer ID in the GeoProcessor, then throw an error.
            else:
                warning_count += 1
                message = 'The GeoLayer ID ({}) value is not a valid GeoLayerID.'.format(pv_GeoLayerID)
                recommendation = 'Specifiy a valid GeoLayerID.'
                logger.error(message)
                self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                        message, recommendation))

        # If the output folder does not exist
        else:
            warning_count += 1
            message = 'The output folder ({}) of the OutputFilename is not a valid folder.'.format(output_folder)
            recommendation = 'Specifiy a valid relative pathname for the output filename.'
            logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                    message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
