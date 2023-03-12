# WriteGeoLayerToGeoJSON - command to write a GeoLayer to a GeoJSON file
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
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validator_util

import logging


class WriteGeoLayerToGeoJSON(AbstractCommand):
    """
    This command writes a vector GeoLayer to a GeoJSON spatial data file.
    The GeoJSON file can then be viewed within a GIS, moved within folders on the local computer, published, etc.

    Each GeoLayer object within the geoprocessor's GeoLayers list has one feature type (point, line, polygon, etc.)
    and other data (an identifier, a coordinate reference system, etc). This
    function only writes as single GeoLayer to a single GeoJSON file.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("OutputCRS", type("")),
        CommandParameterMetadata("OutputPrecision", type(2))]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = "Write a GeoLayer to a file in GeoJSON format, using RFC 7946 standard."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "identifier of the GeoLayer"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = "The GeoLayer identifier, can use ${Property}."
    # OutputFile
    __parameter_input_metadata['OutputFile.Description'] = "GeoJSON file to write"
    __parameter_input_metadata['OutputFile.Label'] = "Output file"
    __parameter_input_metadata['OutputFile.Required'] = True
    __parameter_input_metadata['OutputFile.Tooltip'] = (
        "The output GeoJSON file (relative or absolute path)."
        "${Property} syntax is recognized.")
    __parameter_input_metadata['OutputFile.FileSelector.Type'] = "Write"
    __parameter_input_metadata['OutputFile.FileSelector.Title'] = "Select GeoJSON file to write"
    __parameter_input_metadata['OutputFile.FileSelector.Filters'] = \
        ["GeoJSON file (*.geojson *.json)", "All files (*.*)"]
    # OutputCRS
    __parameter_input_metadata['OutputCRS.Description'] = "coordinate reference system of output (always WGS84)"
    __parameter_input_metadata['OutputCRS.Enabled'] = False  # Because default value is always used
    __parameter_input_metadata['OutputCRS.Label'] = "Output CRS"
    __parameter_input_metadata['OutputCRS.Tooltip'] = (
        "The coordinate reference system of the output GeoJSON, always EPSG:4326 (WGS84)." )
    __parameter_input_metadata['OutputCRS.Value.Default'] = "EPSG:4326" # WGS84
    # OutputPrecision
    __parameter_input_metadata['OutputPrecision.Description'] = "number of decimal points in output"
    __parameter_input_metadata['OutputPrecision.Label'] = "Output precision"
    __parameter_input_metadata['OutputPrecision.Tooltip'] = (
        "The number of decimal points to include in the output GeoJSON file's coordinates. "
        "Must be a positive integer at or between 0 and 15.\n"
        "The precision of coordinate values can greatly impact the size of the file and precision of drawing "
        "the features.\n"
        "For example, a higher OutputPrecision value increases the output GeoJSON file size and "
        "increases the geometry's precision.")
    __parameter_input_metadata['OutputPrecision.Value.Default'] = "5"  # must be between 0 and 15

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data.
        super().__init__()
        self.command_name = "WriteGeoLayerToGeoJSON"
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

        Returns:
            None.

        Raises:
            ValueError:  If any parameters are invalid or do not have a valid value.
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

        # Refresh the phase severity.
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, geolayer_id, output_file_abs, output_precision):
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
            Boolean. If TRUE, the GeoLayer should be written.
                If FALSE, at least one check failed and the GeoLayer should not be written.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests.
        # If TRUE, the test confirms that the command should be run.
        should_run_command = list()

        # If the GeoLayer ID is not an existing GeoLayer ID, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIdExisting", "GeoLayerID", geolayer_id,
                                                           "FAIL"))

        # If the folder of the OutputFile file path is not a valid folder, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "DoesFilePathHaveAValidFolder", "OutputFile",
                                                           output_file_abs, "FAIL"))

        # If the output precision is not at or between 0 and 15, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsIntBetweenRange", "OutputPrecision",
                                                           output_precision, "FAIL", other_values=[0, 15]))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Write the GeoLayer to a spatial data file in GeoJSON format.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values except for the OutputCRS
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        # noinspection PyPep8Naming
        pv_OutputPrecision = int(
            self.get_parameter_value("OutputPrecision",
                                     default_value=self.parameter_input_metadata['OutputPrecision.Value.Default']))
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value("OutputFile")

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.command_processor.expand_parameter_value(pv_GeoLayerID, self)

        # Convert the OutputFile parameter value relative path to an absolute path and expand for ${Property} syntax.
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(pv_GeoLayerID, output_file_absolute, pv_OutputPrecision):

            # noinspection PyBroadException
            try:
                # Get the GeoLayer.
                geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Get the current coordinate reference system (in EPSG code) of the current GeoLayer.
                geolayer_crs_code = geolayer.get_crs_code()

                # OutputCRS is always EPSG:4326 (WGS84).
                # noinspection PyPep8Naming
                pv_OutputCRS = self.get_parameter_value("OutputCRS", default_value='EPSG:4326')
                if pv_OutputCRS != "EPSG:4326":
                    self.warning_count += 1
                    message = "OutputCRS must be EPSG:4326 (resetting automatically)"
                    recommendation = "Change the OutputCRS to ESPG:4326 (using text editor)."
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
                    pv_OutputCRS = "EPSG:4326"

                # Write the GeoLayer to a spatial data file in GeoJSON format.
                qgis_util.write_qgsvectorlayer_to_geojson(geolayer.qgs_layer,
                                                          output_file_absolute,
                                                          pv_OutputCRS,
                                                          pv_OutputPrecision)

                # Save the output file names in the layer, used when creating a GeoMapProject.
                self.logger.debug("Setting output_path_full='" + output_file_absolute + "' output_path='" +
                                  pv_OutputFile + "'")
                geolayer.output_path_full = output_file_absolute
                geolayer.output_path = pv_OutputFile

                # Save the output file in the processor, used by the UI to list output files.
                self.command_processor.add_output_file(output_file_absolute)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process.
                self.warning_count += 1
                message = "Unexpected error writing GeoLayer {} to GeoJSON format.".format(pv_GeoLayerID)
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
