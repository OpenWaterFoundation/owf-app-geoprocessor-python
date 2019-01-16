# WriteGeoLayerToShapefile - write a GeoLayer to a shapefile
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

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validators
import geoprocessor.util.zip_util as zip_util

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
    * ZipOutput (boolean, optional): If TRUE, the shapefile files will be zipped. If FALSE, they will not be zipped.
        Default: False.
    """

    # Define the command parameters/
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("OutputCRS", type("")),
        CommandParameterMetadata("ZipOutput", type(True))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        # Name of command for menu and window title
        self.command_name = "WriteGeoLayerToShapefile"
        # Description for menu "Command()... <description>"
        self.command_description = "Write GeoLayer to a file in Shapefile format"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = {}
        self.command_metadata['Description'] = 'This command writes a GeoLayer to a file in Esri Shapefile format.'
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
        # - existence of the GeoLayer will also be checked in run_command().
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID', command_parameters=command_parameters)

        if not validators.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the GeoLayer to write."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that parameter OutputFile is a non-empty, non-None string.
        # - existence of the folder will also be checked in run_command().
        pv_OutputFile = self.get_parameter_value(parameter_name='OutputFile', command_parameters=command_parameters)

        if not validators.validate_string(pv_OutputFile, False, False):
            message = "OutputFile parameter has no value."
            recommendation = "Specify the OutputFile parameter (relative or absolute pathname) to indicate the " \
                             "location and name of the output spatial data file in GeoJSON format."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional ZipOutput parameter value is a valid Boolean value or is None.
        pv_ZipOutput = self.get_parameter_value(parameter_name="ZipOutput", command_parameters=command_parameters)
        if not validators.validate_bool(pv_ZipOutput, none_allowed=True, empty_string_allowed=False):
            message = "ZipOutput parameter value ({}) is not a recognized boolean value.".format(pv_ZipOutput)
            recommendation = "Specify either 'True' or 'False for the ZipOutput parameter."
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

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def __should_write_geolayer(self, geolayer_id, output_file_abs):
        """
       Checks the following:
       * the ID of the GeoLayer is an existing GeoLayer ID
       * the output folder is a valid folder

       Args:
           geolayer_id: the ID of the GeoLayer to be written
           output_file_abs: the full pathname to the output file

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
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # If the OutputFolder is not a valid folder, raise a FAILURE.
        output_folder = os.path.dirname(output_file_abs)
        if not os.path.isdir(output_folder):
            run_write = False
            self.warning_count += 1
            message = 'The output folder ({}) of the OutputFile is not a valid folder.'.format(output_folder)
            recommendation = 'Specify a valid relative pathname for the output file.'
            self.logger.error(message)
            self.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.FAILURE,
                                                                                    message, recommendation))

        # Return the Boolean to determine if the write process should be run. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return run_write


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
        pv_ZipOutput = self.get_parameter_value("ZipOutput", default_value='False')

        # Convert the ZipOutput value to a Boolean value.
        zip_output_bool = string_util.string_to_boolean(pv_ZipOutput)

        # Convert the OutputFile parameter value relative path to an absolute path and expand for ${Property} syntax
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_write_geolayer(pv_GeoLayerID, output_file_absolute):

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
                if zip_output_bool:
                    zip_util.zip_shapefile(output_file_absolute)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error writing GeoLayer {} to spatial data file in Shapefile format.".format(
                    pv_GeoLayerID)
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
