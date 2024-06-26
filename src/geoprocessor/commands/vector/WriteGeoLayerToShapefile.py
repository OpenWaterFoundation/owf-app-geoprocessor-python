# WriteGeoLayerToShapefile - write a GeoLayer to a shapefile
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

import geoprocessor.util.command_util as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validator_util
import geoprocessor.util.zip_util as zip_util

import os
import logging


class WriteGeoLayerToShapefile(AbstractCommand):
    """
    Write a GeoLayer to a spatial data file in shapefile format.

    This command writes a GeoLayer registered within the geoprocessor to a spatial date file in Shapefile format
    (a group of multiple files).
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", str),
        CommandParameterMetadata("OutputFile", str),
        CommandParameterMetadata("OutputCRS", str),
        CommandParameterMetadata("ZipOutput", bool)]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = "Write a GeoLayer to a file in Esri Shapefile format."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "identifier of the GeoLayer to write"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = "The identifier of the GeoLayer to write."
    # OutputFile
    __parameter_input_metadata['OutputFile.Description'] = "the shapefile to write"
    __parameter_input_metadata['OutputFile.Label'] = "Output file"
    __parameter_input_metadata['OutputFile.Required'] = True
    __parameter_input_metadata['OutputFile.Tooltip'] = \
        "The output Esri Shapefile (relative or absolute path). ${Property} syntax is recognized."
    __parameter_input_metadata['OutputFile.FileSelector.Type'] = "Write"
    __parameter_input_metadata['OutputFile.FileSelector.Title'] = "Select shapefile to write"
    __parameter_input_metadata['OuputFile.FileSelector.Filters'] = \
        ["Shapefile (*.shp)", "All files (*.*)"]
    # OutputCRS
    __parameter_input_metadata['OutputCRS.Description'] = "coordinate reference system of the shapefile"
    __parameter_input_metadata['OutputCRS.Label'] = "Output CRS"
    __parameter_input_metadata['OutputCRS.Tooltip'] = (
        "The coordinate reference system of the output GeoJSON. EPSG or ESRI code format required "
        "(e.g. EPSG:4326, EPSG:26913, ESRI:102003).\n"
        "If the output CRS is different than the CRS of the GeoLayer, the output GeoJSON is reprojected "
        "to the new CRS.")
    __parameter_input_metadata['OutputCRS.Value.Default'] = "The GeoLayer's CRS"
    # zipOutput
    __parameter_input_metadata['ZipOutput.Description'] = "whether to zip the shapefile"
    __parameter_input_metadata['ZipOutput.Label'] = "Zip output?"
    __parameter_input_metadata['ZipOutput.Tooltip'] = (
        "If TRUE, the GeoLayer is written as a zipped shapefile.\n"
        "If FALSE the GeoLayer is witten as an unzipped shapefile.")
    __parameter_input_metadata['ZipOutput.Value.Default'] = "FALSE"
    __parameter_input_metadata['ZipOutput.Values'] = ["", "TRUE", "FALSE"]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data.
        super().__init__()
        self.command_name = "WriteGeoLayerToShapefile"
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

        # Check that optional ZipOutput parameter value is a valid Boolean value or is None.
        # noinspection PyPep8Naming
        pv_ZipOutput = self.get_parameter_value(parameter_name="ZipOutput", command_parameters=command_parameters)
        if not validator_util.validate_bool(pv_ZipOutput, none_allowed=True, empty_string_allowed=False):
            message = "ZipOutput parameter value ({}) is not a recognized boolean value.".format(pv_ZipOutput)
            recommendation = "Specify either 'True' or 'False for the ZipOutput parameter."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            self.logger.warning(warning_message)
            raise CommandParameterError(warning_message)

        # Refresh the phase severity.
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, geolayer_id: str, output_file_abs: str) -> bool:
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
        # valid_output_bool = True

        # If the GeoLayer ID is not an existing GeoLayer ID, raise a FAILURE.
        if not self.command_processor.get_geolayer(geolayer_id):
            run_write = False
            self.warning_count += 1
            message = 'The GeoLayerID ({}) is not a valid GeoLayer ID.'.format(geolayer_id)
            recommendation = 'Specify a valid GeoLayerID.'
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # If the OutputFolder is not a valid folder, raise a FAILURE.
        output_folder = os.path.dirname(output_file_abs)
        if not os.path.isdir(output_folder):
            run_write = False
            self.warning_count += 1
            message = 'The output folder ({}) of the OutputFile is not a valid folder.'.format(output_folder)
            recommendation = 'Specify a valid relative pathname for the output file.'
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.FAILURE,
                                                                                  message, recommendation))

        # Return the Boolean to determine if the write process should be run. If TRUE, all checks passed.
        # If FALSE, one or many checks failed.
        return run_write

    def run_command(self) -> None:
        """
        Run the command. Write the GeoLayer to a spatial data file in Shapefile format to the folder OutputFolder.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values except for the OutputCRS.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value("OutputFile")
        # noinspection PyPep8Naming
        pv_ZipOutput = self.get_parameter_value("ZipOutput", default_value='False')

        # Convert the ZipOutput value to a Boolean value.
        zip_output_bool = string_util.str_to_bool(pv_ZipOutput)

        # Convert the OutputFile parameter value relative path to an absolute path and expand for ${Property} syntax.
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(pv_GeoLayerID, output_file_absolute):

            # noinspection PyBroadException
            try:

                # Get the GeoLayer.
                geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Get the current coordinate reference system (in EPSG code) of the current GeoLayer.
                geolayer_crs = geolayer.get_crs()

                # Obtain the parameter value of the OutputCRS.
                # noinspection PyPep8Naming
                pv_OutputCRS = self.get_parameter_value("OutputCRS", default_value=geolayer_crs)

                # Write the GeoLayer to a spatial data file in Shapefile format.
                qgis_util.write_qgsvectorlayer_to_shapefile(geolayer.qgs_layer,
                                                            output_file_absolute,
                                                            pv_OutputCRS)

                # Zip the shapefiles, if configured to do so.
                if zip_output_bool:
                    zip_path = zip_util.zip_shapefile(output_file_absolute)
                    # Save the output file in the processor, used by the UI to list output files.
                    self.command_processor.add_output_file(zip_path)
                else:
                    # Save the output file in the processor, used by the UI to list output files.
                    self.command_processor.add_output_file(output_file_absolute)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process.
                self.warning_count += 1
                message = "Unexpected error writing GeoLayer {} to spatial data file in Shapefile format.".format(
                    pv_GeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred.
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
