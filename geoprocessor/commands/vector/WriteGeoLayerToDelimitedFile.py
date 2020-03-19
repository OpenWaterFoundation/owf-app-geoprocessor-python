# WriteGeoLayerToDelimitedFile - command to write a GeoLayer to a delimited file
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

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.validator_util as validator_util

import logging

import os


class WriteGeoLayerToDelimitedFile(AbstractCommand):
    """
    Writes a GeoLayer to a delimited spatial data file.

    This command writes a layer to a delimited file. The delimited file can then be viewed within a GIS, moved within
    folders on the local computer, packaged for delivery, etc. The geometry is either held in one column in
    WKT (Well Known Text) format or in multiple columns in XY(Z) format. Each attribute field of the GeoLayer is
    written to the delimited file as a column. (The column name is the attribute name). Each row of the delimited
    file represents a single feature in the GeoLayer.

    Registered GeoLayers are stored as GeoLayer objects within the geoprocessor's GeoLayers list. Each GeoLayer has one
    feature type (point, line, polygon, etc.) and other data (an identifier, a coordinate reference system, etc). This
    function only writes one single GeoLayer to a single spatial data file in delimited file format. If the GeoLayer
    is anything other than 'POINT' data, the delimited file must hold the geometry data in WKT format
    (OutputGeometryFormat = `WKT`, see below).

    Command Parameters
    * GeoLayerID (str, required): the identifier of the GeoLayer to be written to a spatial data file in CSV format.
    * OutputFile (str, required): the pathname (relative or absolute) of the output spatial data file (do not include
        the .csv extension)
    * OutputCRS (str, EPSG code, optional): the coordinate reference system that the output spatial data file will be
        projected. By default, the output spatial data file will be projected to the GeoLayer's current CRS.
    * OutputGeometryFormat (str, optional): how the geometry will be displayed in the output CSV file. Default is
        `XY`. Available options are as follows:
        (1) `WKT`: the geometry will be held in one column in its Well Known Text (WKT) representation. This format
            can represent `POINT`, `LINE` or `POLYGON` data.
        (2) `XYZ`: the geometry will be held in the X, Y and Z representation (in multiple columns). This format can
            only represent `POINT` data.
        (3) `XY`: the geometry will be held in the X, and Y representation (in multiple columns). This format can
            only represent `POINT` data. The X column is first and then the Y column.
        (4) `YX`: the geometry will be held in the X, and Y representation (in multiple columns). This format can
        only represent `POINT` data. The Y column is first and then the X column.
    * OutputDelimiter (str, optional): the delimiter of the output CSV file. Default is `COMMA`.
        Available options are as follows:
        (1) `COMMA` (2) `SEMICOLON` (3) `TAB` (4) `SPACE`
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("OutputCRS", type("")),
        CommandParameterMetadata("OutputGeometryFormat", type("")),
        CommandParameterMetadata("OutputDelimiter", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Write a GeoLayer to a delimited file."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "identifier of the GeoLayer to write"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = "The identifier of the GeoLayer to write."
    # OutputFile
    __parameter_input_metadata['OutputFile.Description'] = "property file to write"
    __parameter_input_metadata['OutputFile.Label'] = "Output file"
    __parameter_input_metadata['OutputFile.Required'] = True
    __parameter_input_metadata['OutputFile.Tooltip'] = (
        "The output delimited file (relative or absolute path). The file extension is not required. "
        "${Property} syntax is recognized.")
    __parameter_input_metadata['OutputFile.FileSelector.Type'] = "Write"
    __parameter_input_metadata['OutputFile.FileSelector.Title'] = "Select file to write"
    __parameter_input_metadata['OutputFile.FileSelector.Filters'] = \
        ["Delimited file (*.csv *.txt)", "All files (*.*)"]
    # OutputCRS
    __parameter_input_metadata['OutputCRS.Description'] = "coordinate reference system of output"
    __parameter_input_metadata['OutputCRS.Label'] = "Output CRS"
    __parameter_input_metadata['OutputCRS.Tooltip'] = (
        "The output delimited file (relative or absolute path). "
        "The file extension is not required.\n${Property} syntax is recognized.")
    __parameter_input_metadata['OutputCRS.Value.Default'] = "The GeoLayer's CRS"
    # OutputGeometryFormat
    __parameter_input_metadata['OutputGeometryFormat.Description'] = "geometry representation"
    __parameter_input_metadata['OutputGeometryFormat.Label'] = "Output geometry format"
    __parameter_input_metadata['OutputGeometryFormat.Tooltip'] = (
        "The geometry representation. Must be one of the following options:\n"
        "WKT: The geometry is stored in one column in its Well Known Text (WKT) representation. "
        "This type of geometry can represent 2D and 3D POINTS, LINES or POLYGONS. \n"
        "XY: The geometry is stored in two columns as X and Y coordinates. "
        "This type of geometry can only represent 2D POINTS. The X column is before the Y column.\n"
        "YX: The geometry is stored in two columns as X and Y coordinates. "
        "This type of geometry can only represent 2D POINTS. The Y column is before the X column.\n"
        "XYZ: The geometry is stored in three columns as X, Y, and Z coordinates. "
        "This type of geometry can only represent 3D POINTS.")
    __parameter_input_metadata['OutputGeometryFormat.Values'] = ["", "WKT", "XY", "YX", "XYZ"]
    __parameter_input_metadata['OutputGeometryFormat.Value.Default'] = "XY"
    # OutputDelimiter
    __parameter_input_metadata['OutputDelimiter.Description'] = "delimiter of the output file"
    __parameter_input_metadata['OutputDelimter.Label'] = "Output delimiter"
    __parameter_input_metadata['OutputDelimiter.Tooltip'] = (
        "The delimiter of the output delimited file. Must be one of the following options:\n"
        "COMMA: the comma (,)\n"
        "SEMICOLON: the semicolon (;)\n"
        "TAB: a tab character\n"
        "SPACE: a space character")
    __parameter_input_metadata['OutputDelimiter.Values'] = ["", "COMMA", "SEMICOLON", "TAB", "SPACE"]
    __parameter_input_metadata['OutputDelimiter.Value.Default'] = "COMMA"

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "WriteGeoLayerToDelimitedFile"
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

        warning = ""

        # Check that the appropriate parameters have a string value.
        for parameter in ['GeoLayerID', 'OutputFile']:

            # Get the parameter value.
            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)

            # Check that the parameter value is a non-empty, non-None string. If not, raise a FAILURE.
            if not validator_util.validate_string(parameter_value, False, False):
                message = "{} parameter has no value.".format(parameter)
                recommendation = "Specify the {} parameter.".format(parameter)
                warning += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional parameter OutputGeometryFormat is either `WKT`, `XYZ`, `XY`, `YX` or None.
        # noinspection PyPep8Naming
        pv_OutputGeometryFormat = self.get_parameter_value(parameter_name="OutputGeometryFormat",
                                                           command_parameters=command_parameters)
        acceptable_values = ["WKT", "XYZ", "XY", "YZ"]
        if not validator_util.validate_string_in_list(pv_OutputGeometryFormat, acceptable_values, none_allowed=True,
                                                      empty_string_allowed=False, ignore_case=True):
            message = "OutputGeometryFormat parameter value ({}) is not recognized.".format(pv_OutputGeometryFormat)
            recommendation = "Specify one of the acceptable values ({}) for the OutputGeometryFormat parameter.".format(
                acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional parameter OutputDelimiter is either `COMMA`, `SPACE`, `TAB`, `SEMICOLON` or None.
        # noinspection PyPep8Naming
        pv_OutputDelimiter = self.get_parameter_value(parameter_name="OutputDelimiter",
                                                      command_parameters=command_parameters)
        acceptable_values = ["COMMA", "SEMICOLON", "TAB", "SPACE"]
        if not validator_util.validate_string_in_list(pv_OutputDelimiter, acceptable_values, none_allowed=True,
                                                      empty_string_allowed=False, ignore_case=True):
            message = "OutputDelimiter parameter value ({}) is not recognized.".format(pv_OutputDelimiter)
            recommendation = "Specify one of the acceptable values ({}) for the OutputDelimiter parameter.".format(
                acceptable_values)
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

    def __should_write_geolayer(self, geolayer_id: str, output_file_abs: str, crs: str,
                                output_geom_format: str) -> bool:
        """
        Checks the following:
        * the ID of the GeoLayer is an existing GeoLayer ID
        * the output folder is a valid folder
        * the feature geometry is "POINT" if the geometry format parameter format is not "WKT"
        * the CRS is a valid CRS code

        Args:
            geolayer_id (str): the ID of the GeoLayer to be written
            output_file_abs (str): the full pathname (absolute) to the output CSV file (without the extension)
            crs (str): the desired coordinate reference system of the output spatial data
            output_geom_format (str): the geometry format to display the spatial data into CSV format

        Returns:
             Boolean. If TRUE, the GeoLayer should be written. If FALSE, at least one check failed and the GeoLayer
                should not be written.
       """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the GeoLayer ID is not an existing GeoLayer ID, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIdExisting", "GeoLayerID", geolayer_id,
                                                           "FAIL"))

        # If the GeoLayerID exists, continue with the checks.
        if False not in should_run_command:

            # If the output_geometry_format is not 'WKT', continue with the checks.
            if not output_geom_format.upper() == "WKT":

                # If the GeoLayer does not have POINT geometry, raise a FAILURE.
                should_run_command.append(validator_util.run_check(self, "DoesGeoLayerIdHaveCorrectGeometry",
                                                                   "GeoLayerID", geolayer_id,
                                                                   "FAIL", other_values=[["Point"]]))

            # Get the CRS of the input GeoLayer, if the parameter value for OutputCRS is None.
            if crs is None:
                crs = self.command_processor.get_geolayer(geolayer_id).get_crs()

            # If the CRS is not a valid CRS code, raise a FAILURE.
            should_run_command.append(validator_util.run_check(self, "IsCRSCodeValid", "OutputCRS", crs, "FAIL"))

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
        Run the command. Write the GeoLayer to a delimited file.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the command parameter values.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value("OutputFile")
        # noinspection PyPep8Naming
        pv_OutputCRS = self.get_parameter_value("OutputCRS")
        # noinspection PyPep8Naming
        pv_OutputGeometryFormat = self.get_parameter_value("OutputGeometryFormat", default_value="XY").upper()
        # noinspection PyPep8Naming
        pv_OutputDelimiter = self.get_parameter_value("OutputDelimiter", default_value="COMMA").upper()

        # Convert the OutputFile parameter value relative path to an absolute path and expand for ${Property} syntax
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        # Get the filename of the OutputFile with the path but without the extension.
        path, filename = os.path.split(output_file_absolute)
        path = os.path.split(output_file_absolute)[0]
        filename_wo_ext_path = os.path.join(path, os.path.splitext(filename)[0])

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_write_geolayer(pv_GeoLayerID, filename_wo_ext_path, pv_OutputCRS, pv_OutputGeometryFormat):

            # noinspection PyBroadException
            try:
                # Get the GeoLayer
                geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Get the current coordinate reference system (in EPSG code) of the current GeoLayer
                if pv_OutputCRS is None:
                    # noinspection PyPep8Naming
                    pv_OutputCRS = geolayer.get_crs()

                # Write the GeoLayer to a delimited spatial data file.
                qgis_util.write_qgsvectorlayer_to_delimited_file(geolayer.qgs_layer,
                                                                 filename_wo_ext_path,
                                                                 pv_OutputCRS,
                                                                 pv_OutputGeometryFormat,
                                                                 pv_OutputDelimiter)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process
                self.warning_count += 1
                message = "Unexpected error writing GeoLayer {} to delimited file format.".format(pv_GeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
