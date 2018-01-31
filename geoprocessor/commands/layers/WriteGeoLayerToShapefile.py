# WriteGeoLayerToShapefile

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.commandUtil as command_util
import geoprocessor.util.fileUtil as file_util
import geoprocessor.util.ioUtil as io_util
import geoprocessor.util.qgisUtil as qgis_util
import geoprocessor.util.stringUtil as string_util
import geoprocessor.util.validatorsUtil as validators

import os
import logging


class WriteGeoLayerToShapefile(AbstractCommand):
    """
    Writes a GeoLayer to a spatial data file in Shapefile format.

    This command writes a GeoLayer registered within the geoprocessor to a spatial date file in Shapefile format (a
    suite of multiple files). The Shapefile spatial data files can then be viewed within a GIS, moved within folders on
    the local computer, packaged for delivery, etc.

    Registered GeoLayers are stored as GeoLayer objects within the geoprocessor's GeoLayers list. Each GeoLayer has one
    feature type (point, line, polygon, etc.) and other data (an identifier, a coordinate reference system, etc). This
    function only writes one single GeoLayer to a single spatial data file in Shapefile format.

    Command Parameters
    * GeoLayerID (str, required): the identifier of the GeoLayer to be written to a spatial data file in Shapefile
        format
    * OutputFile (str, required): the relative pathname of the output spatial data file.
    * OutputCRS (str, EPSG code, optional): the coordinate reference system that the output spatial data file will be
        projected. By default, the output spatial data file will be projected to the GeoLayer's current CRS.
    * ExtendedOutput(boolean, optional): If TRUE, the individual shapefile component files will be written. If FALSE,
        the individual shapefile component files will not be written. Default: TRUE.
    * CompressedOutput(boolean, optional): If TRUE, a zip file with the shapefile component files will be written.
        If FALSE, a zip file with the shapefile component files will not be written. Default: FALSE.
    """

    # Define the command parameters/
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("OutputCRS", type("")),
        CommandParameterMetadata("ExtendedOutput", type(True)),
        CommandParameterMetadata("CompressedOutput", type(True))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super(WriteGeoLayerToShapefile, self).__init__()
        self.command_name = "WriteGeoLayerToShapefile"
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
            recommendation = "Specify the OutputFile parameter (relative or absolute pathname) to indicate the " \
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

    def __should_write_geolayer(self, geolayer_id, output_file_abs, extended_output_bool, compressed_output_bool):
        """
       Checks the following:
       * the ID of the GeoLayer is an existing GeoLayer ID
       * the output folder is a valid folder
       * the provided ExtendedOutput command parameter value is a valid Boolean value
       * the provided CompressedOutput command parameter value is a valid Boolean value.
       * one of the desired output formats is set to TRUE

       Args:
           geolayer_id: the ID of the GeoLayer to be written
           output_file_abs: the full pathname to the output file
           extended_output_bool: Boolean value (or None) to determine if the shapefile (extended format) should be
            written
           compressed_output_bool:  Boolean value (or None) to determine if the shapefile (compressed format) should be
            written

       Returns:
           run_write: Boolean. If TRUE, the writing process should be run. If FALSE, it should not be run.
       """

        # Boolean to determine if the writing process should be run. Set to true until an error occurs.
        run_write = True

        # Boolean to determine if the output format parameters have valid bool values. Set to true until proven false.
        valid_output_bool = True

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

        # If the input ExtendedOutput parameter value is not a valid Boolean value, raise a FAILURE.
        if extended_output_bool is None:
            run_write = False
            valid_output_bool = False
            self.warning_count += 1
            message = 'The ExtendedOutput parameter value ({}) is not valid.'.format(extended_output_bool)
            recommendation = 'Specify a valid Boolean value (True or False).'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                    message, recommendation))

        # If the input CompressedOutput parameter value is not a valid Boolean value, raise a FAILURE.
        if compressed_output_bool is None:
            run_write = False
            valid_output_bool = False
            self.warning_count += 1
            message = 'The CompressedOutput parameter value ({}) is not valid.'.format(extended_output_bool)
            recommendation = 'Specify a valid Boolean value (True or False).'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                    message, recommendation))

        # If both of the output foramt parameters have a valid Boolean parameter value, check that at least one of
        # them is set to TRUE. If not, raise a warning.
        if valid_output_bool and not (extended_output_bool or compressed_output_bool):
            run_write = False
            self.warning_count += 1
            message = 'Both output format (ExtendedOutput and CompressedOutput) have been set to FALSE. The ' \
                      'shapefile will not be wrtten.'
            recommendation = 'Set one or both of the output format parameters (ExtendedOutput and CompressedOutput)' \
                             ' to TRUE.'
            self.logger.warning(message)
            self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.WARNING,
                                                                                    message, recommendation))

        # Return the Boolean to determine if the write process should be run. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return run_write

    @staticmethod
    def __zip_shapefile(output_file_abs, keep_archive_files):

        # Get the output folder
        output_folder = os.path.dirname(output_file_abs)
        output_filename = os.path.basename(output_file_abs)

        # Files to archive
        files_to_archive = []

        for extension in ['.shx', '.shp', '.qpj', '.prj', '.dbf', '.cpg']:

            output_file_full_path = os.path.join(output_folder, output_filename + extension)

            if os.path.exists(output_file_full_path):
                files_to_archive.append(output_file_full_path)

        file_util.zip_files(files_to_archive, output_file_abs, keep_archive_files)

    def run_command(self):
        """
        Run the command. Write the GeoLayer to a spatial data file in Shapefile format to the folder OutputFolder.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values except for the OutputCRS
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_OutputFile = self.get_parameter_value("OutputFile")
        pv_ExtendedOutput = self.get_parameter_value("ExtendedOutput", default_value='True')
        pv_CompressedOutput = self.get_parameter_value("CompressedOutput", default_value='False')

        # Convert the ExtendedOutput and the CompressedOutput parameters from strings to Booleans
        extended_output_bool = string_util.string_to_boolean(pv_ExtendedOutput)
        compressed_output_bool = string_util.string_to_boolean(pv_CompressedOutput)

        # Convert the OutputFile parameter value relative path to an absolute path and expand for ${Property} syntax
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_write_geolayer(pv_GeoLayerID, output_file_absolute, extended_output_bool,
                                        compressed_output_bool):

            try:

                # Get the GeoLayer
                geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Get the current coordinate reference system (in EPSG code) of the current GeoLayer
                geolayer_crs = geolayer.get_crs()

                # Obtain the parameter value of the OutputCRS
                pv_OutputCRS = self.get_parameter_value("OutputCRS", default_value=geolayer_crs)

                # Write the GeoLayer to a spatial data file in Shapefile format
                qgis_util.write_qgsvectorlayer_to_shapefile(geolayer.qgs_vector_layer,
                                                            output_file_absolute,
                                                            pv_OutputCRS)

                # Zip the shapefiles, if configured to do so.
                if compressed_output_bool:
                    self.__zip_shapefile(output_file_absolute, extended_output_bool)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error writing GeoLayer {} to spatial data file in Shapefile format.".format(
                    pv_GeoLayerID)
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
