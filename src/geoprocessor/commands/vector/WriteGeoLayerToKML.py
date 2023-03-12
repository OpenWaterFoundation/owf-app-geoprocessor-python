# WriteGeoLayerToKML - write a GeoLayer to a KML file
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


class WriteGeoLayerToKML(AbstractCommand):
    """
    Writes a GeoLayer to a spatial data file in KML format.

    This command writes a GeoLayer registered within the geoprocessor to a KML spatial data file.
    The KML spatial data file can then be viewed within Google Earth, moved within folders on the local computer,
    packaged for delivery, etc.

    Registered GeoLayers are stored as GeoLayer objects within the geoprocessor's GeoLayers list.
    Each GeoLayer has one feature type (point, line, polygon, etc.) and other data
    (an identifier, a coordinate reference system, etc).
    This function only writes one single GeoLayer to a single spatial data file in GeoJSON format.

    Command Parameters:

    * GeoLayerID (str, required): the identifier of the GeoLayer to be written to a spatial data file in GeoJSON format.
    * OutputFile (str, required): the relative pathname of the output spatial data file.
    * PlacemarkNameAttribute (str, optional): Allows you to specify the field to use for the KML <name> element.
        Default: Name
    * PlacemarkDescriptionAttribute (str, optional): Allows you to specify the field to use for the KML <description>
        element. Default: Description
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("PlacemarkNameAttribute", type("")),
        CommandParameterMetadata("PlacemarkDescriptionAttribute", type(""))]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = "Write a GeoLayer to a file in KML format."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "identifier of the GeoLayer to write"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = "The GeoLayer identifier, can use ${Property}."
    # OutputFile
    __parameter_input_metadata['OutputFile.Description'] = "property file to write"
    __parameter_input_metadata['OutputFile.Label'] = "Output file"
    __parameter_input_metadata['OutputFile.Required'] = True
    __parameter_input_metadata['OutputFile.Tooltip'] = \
        "The output KML file (relative or absolute path). ${Property} syntax is recognized."
    __parameter_input_metadata['OutputFile.FileSelector.Type'] = "Write"
    __parameter_input_metadata['OutputFile.FileSelector.Title'] = "Select file to write output"
    __parameter_input_metadata['OutputFile.FileSelector.Filters'] = \
        ["GeoJSON file (*.kmz)", "All files (*.*)"]
    # PlacemarkNameAttribute
    __parameter_input_metadata['PlacemarkNameAttribute.Description'] = \
        "geolayer attribute for the KML's placemark name"
    __parameter_input_metadata['PlacemarkNameAttribute.Label'] = "Placemark name attribute"
    __parameter_input_metadata['PlacemarkNameAttribute.Tooltip'] = (
        "The GeoLayer attribute to populate the output KML's placemark <name> elements.\n"
        "Each GeoLayer feature is coverted into a KML placemark. Each placemark can have a <name> element.\n"
        "The attribute values within the PlacemarkNameAttribute will populate each placemark's name.\n"
        "For further explanation, look at the example KML document under the Structure section of the Keyhole "
        "Markup Language Wikipedia page.")
    __parameter_input_metadata['PlacemarkNameAttribute.Value.Default.Description'] = \
        "The output KML placemarks will not have a <name> element."
    # PlacemarkDescriptionAttribute
    __parameter_input_metadata['PlacemarkDescriptionAttribute.Description'] = \
        "GeoLayer attribute for KML's placemark description"
    __parameter_input_metadata['PlacemarkDescriptionAttribute.Label'] = "Placemark description attribute"
    __parameter_input_metadata['PlacemarkDescriptionAttribute.Tooltip'] = (
        "The GeoLayer attribute to populate the output KML's placemark <description> elements.\n"
        "Each GeoLayer feature is coverted into a KML placemark. Each placemark can have a <description> element.\n"
        "The attribute values within the PlacemarkDescriptionAttribute will populate each"
        "placemark's description.\n"
        "For further explanation, look at the example KML document under the Structure section of the "
        "Keyhole Markup Language Wikipedia page.")
    __parameter_input_metadata['PlacemarkDescriptionAttribute.Value.Default'] = \
        "The output KML placemarks will not have a <description> element."

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data.
        super().__init__()
        self.command_name = "WriteGeoLayerToKML"
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

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Write the GeoLayer to a spatial data file in KML format.

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
        pv_OutputFile = self.get_parameter_value("OutputFile")
        # noinspection PyPep8Naming
        pv_PlacemarkNameAttribute = self.get_parameter_value("PlacemarkNameAttribute")
        # noinspection PyPep8Naming
        pv_PlacemarkDescriptionAttribute = self.get_parameter_value("PlacemarkDescriptionAttribute")

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

                # Write the GeoLayer to a spatial data file in KML format.
                # "Note that KML by specification uses only a single projection, EPSG:4326.
                # All OGR KML output will be presented in EPSG:4326.
                # As such OGR will create layers in the correct coordinate system and transform any geometries."
                # - www.gdal.org/drv_kml.html
                qgis_util.write_qgsvectorlayer_to_kml(geolayer.qgs_layer,
                                                      output_file_absolute,
                                                      "EPSG:4326",
                                                      pv_PlacemarkNameAttribute,
                                                      pv_PlacemarkDescriptionAttribute,
                                                      "clampToGround")

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
