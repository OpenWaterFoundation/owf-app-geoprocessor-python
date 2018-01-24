# WriteGeoLayerToGeoJSON

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.io as io_util
import geoprocessor.util.validators as validators

from qgis.core import QgsVectorFileWriter, QgsCoordinateReferenceSystem

import os
import logging


class WriteGeoLayerToGeoJSON(AbstractCommand):
    """
    Writes a GeoLayer to a spatial data file in GeoJSON format.

    This command writes a GeoLayer registered within the geoprocessor to a GeoJSON spatial data file. The GeoJSON
    spatial data file can then be viewed within a GIS, moved within folders on the local computer, packaged for
    delivery, etc.

    Registered GeoLayers are stored as GeoLayer objects within the geoprocessor's GeoLayers list. Each GeoLayer has one
    feature type (point, line, polygon, etc.) and other data (an identifier, a coordinate reference system, etc). This
    function only writes one single GeoLayer to a single spatial data file in GeoJSON format.

    Command Parameters
    * GeoLayerID (str, required): the identifier of the GeoLayer to be written to a spatial data file in GeoJSON format.
    * OutputFile (str, required): the relative pathname of the output spatial data file.
    * OutputCRS (str, EPSG code, optional): the coordinate reference system that the output spatial data file will be
        projected. By default, the output spatial data file will be projected to the GeoLayer's current CRS.
    * OutputPrecision (int, 0-15, optional): the precision (number of integers behind the GeoJSON geometry's decimal
        point) of the output spatial data file in GeoJSON format. Must be at or between 0 and 15. By default, the
        precision parameter is set to 5.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("OutputCRS", type("")),
        CommandParameterMetadata("OutputPrecision", type(2))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super(WriteGeoLayerToGeoJSON, self).__init__()
        self.command_name = "WriteGeoLayerToGeoJSON"
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

        # Check that parameter GeoLayerID is a non-empty, non-None string.
        # - existence of the GeoLayer will also be checked in run_command().
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID', command_parameters=command_parameters)

        if not validators.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the GeoLayer to write."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that parameter OutputFile is a non-empty, non-None string.
        # - existence of the folder will also be checked in run_command().
        pv_OutputFile = self.get_parameter_value(parameter_name='OutputFile', command_parameters=command_parameters)

        if not validators.validate_string(pv_OutputFile, False, False):
            message = "OutputFile parameter has no value."
            recommendation = "Specify the OutputFilen parameter (relative or absolute pathname) to indicate the " \
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
            self.logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def __should_write_geolayer(self, geolayer_id, output_file_abs, output_precision):
        """
       Checks the following:
       * the ID of the GeoLayer is an existing GeoLayer ID
       * the output folder is a valid folder
       * the output precision is at or between 0 and 15


       Args:
           geolayer_id: the ID of the GeoLayer to be written
           output_file_abs: the full pathname to the output file
           output_precision (int): the precision of the output GeoJSON file

       Returns:
           run_write: Boolean. If TRUE, the writing process should be run. If FALSE, it should not be run.
       """

        # Boolean to determine if the writing process should be run. Set to true until an error occurs.
        run_write = True

        # If the GeoLayer ID is not an existing GeoLayer ID, raise a FAILURE.
        if not self.command_processor.get_geolayer(geolayer_id):

            run_write = False
            self.warning_count += 1
            message = 'The GeoLayerID ({}) is not a valid GeoLayer ID.'.format(geolayer_id)
            recommendation = 'Specify a valid GeoLayerID.'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # If the OutputFolder is not a valid folder, raise a FAILURE.
        output_folder = os.path.dirname(output_file_abs)
        if not os.path.isdir(output_folder):

            run_write = False
            self.warning_count += 1
            message = 'The output folder ({}) of the OutputFile is not a valid folder.'.format(output_folder)
            recommendation = 'Specify a valid relative pathname for the output file.'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                    message, recommendation))

        # If the output precision is not at or between 0 and 15, raise a FAILURE.
        if output_precision < 0 or output_precision > 15:

            run_write = False
            self.warning_count += 1
            message = 'The OutputPrecision ({}) must be at or between 0 and 15'.format(output_precision)
            recommendation = 'Specify a valid OutputPrecision value.'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                    message, recommendation))

        # Return the Boolean to determine if the write process should be run. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return run_write

    def run_command(self):
        """
        Run the command. Write the GeoLayer to a spatial data file in GeoJSON format to the folder OutputFolder.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values except for the OutputCRS
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_OutputPrecision = int(self.get_parameter_value("OutputPrecision", default_value=5))
        pv_OutputFile = self.get_parameter_value("OutputFile")

        # Convert the OutputFile parameter value relative path to an absolute path and expand for ${Property} syntax
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_write_geolayer(pv_GeoLayerID, output_file_absolute, pv_OutputPrecision):

            try:
                # Get the GeoLayer
                geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Get the current coordinate reference system (in EPSG code) of the current GeoLayer
                geolayer_crs = geolayer.get_crs()

                # Obtain the parameter value of the OutputCRS
                pv_OutputCRS = self.get_parameter_value("OutputCRS", default_value=geolayer_crs)

                # Get the QGSVectorLayer object for the GeoLayer
                qgs_vector_layer = geolayer.qgs_vector_layer

                # Write the GeoLayer to a spatial data file in GeoJSON format
                # Reference: `QGIS API Documentation <https://qgis.org/api/classQgsVectorFileWriter.html>_`
                # To use the QgsVectorFileWriter.writeAsVectorFormat tool, the following sequential arguments are
                # defined:
                #   1. vectorFileName: the QGSVectorLayer object that is to be written to a spatial data format
                #   2. path to new file: the full pathname (including filename) of the output file
                #   3. output text encoding: always set to "utf-8"
                #   4. destination coordinate reference system
                #   5. driver name for the output file
                #   6. optional layerOptions (specific to driver name) : for GeoJSON, coordinate precision is defined
                # Note to developers: IGNORE `Unexpected Argument` error for layerOptions. This value is appropriate
                #   and functions properly.
                QgsVectorFileWriter.writeAsVectorFormat(qgs_vector_layer,
                                                        output_file_absolute,
                                                        "utf-8",
                                                        QgsCoordinateReferenceSystem(pv_OutputCRS),
                                                        "GeoJSON",
                                                        layerOptions=[
                                                            'COORDINATE_PRECISION={}'.format(pv_OutputPrecision)])

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error writing GeoLayer {} to GeoJSON format.".format(pv_GeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.exception(message, e)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
