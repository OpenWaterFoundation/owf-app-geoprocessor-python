# ReadGeoLayerFromDelimitedFile - command to read a GeoLayer from a delimited file
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
from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validators

import logging


class ReadGeoLayerFromDelimitedFile(AbstractCommand):

    """
    Reads a GeoLayer from a delimited spatial data file.

    This command reads a layer from a delimited file and creates a GeoLayer object within the
    geoprocessor. The GeoLayer can then be accessed in the geoprocessor by its identifier and further processed.

    GeoLayers read from a delimited file hold point features. It is required that the delimited file has a column
     representing each feature's x coordinates and a column representing each feature's y coordinates. The other
     columns within the delimited file, if any, are included in the GeoLayer's attribute tables as individual attributes.

    In order for the geoprocessor to use and manipulate spatial data files, GeoLayers are instantiated as
    `QgsVectorLayer <https://qgis.org/api/classQgsVectorLayer.html>`_ objects.

    Command Parameters
    * DelimitedFile (str, required): The path (relative or absolute) to the delimited file to be read.
    * GeometryFormat (str, required): The geometry representation used within the delimited file. Must either be `XY`
        or `WKT`.
    * XColumn (str, required if GeometryFormat is `XY`): The name of the delimited file column that holds the x
        coordinate data.
    * YColumn (str, required if GeometryFormat is `XY`): The name of the delimited file column that holds the y
        coordinate data.
    * WKTColumn (str, required if GeometryFormat is `WKT`): The name of the delimited file column that holds teh WKT
        formatted geometries.
    * CRS (str, required): The coordinate reference system associated with the X and Y coordinates (in EPSG code).
    * Delimiter (str, optional): The delimiter symbol used in the delimited file. Defaulted to comma.
    * GeoLayerID (str, optional): the GeoLayer identifier. If None, the spatial data filename (without the .geojson
        extension) will be used as the GeoLayer identifier. For example: If GeoLayerID is None and the absolute
        pathname to the spatial data file is C:/Desktop/Example/example_file.geojson, then the GeoLayerID will be
        `example_file`.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the CopiedGeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("DelimitedFile", type("")),        
        CommandParameterMetadata("GeometryFormat", type("")),
        CommandParameterMetadata("XColumn", type("")),
        CommandParameterMetadata("YColumn", type("")),
        CommandParameterMetadata("WKTColumn", type("")),
        CommandParameterMetadata("CRS", type("")),
        CommandParameterMetadata("Delimiter", type("")),
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "ReadGeoLayerFromDelimitedFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = "This command reads a GeoLayer from a delimited file."
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # DelimitedFile
        self.parameter_input_metadata['DelimitedFile.Description'] = "the delimited file to read"
        self.parameter_input_metadata['DelimitedFile.Label'] = "Delimited File"
        self.parameter_input_metadata['DelimitedFile.Required'] = True
        self.parameter_input_metadata['DelimitedFile.Tooltip'] = "The delimited file to read (relative or absolute " \
            "path). ${Property} syntax is recognized."
        # CRS
        self.parameter_input_metadata['CRS.Description'] = "the coordiante reference system"
        self.parameter_input_metadata['CRS.Label'] = "CRS"
        self.parameter_input_metadata['CRS.Required'] = True
        self.parameter_input_metadata['CRS.Tooltip'] = "The coordinate reference system of the geometry in the " \
            "delimited file. \nEPSG or ESRI code format required (e.g. EPSG:4326, EPSG:26913, ESRI:102003)."
        # GeometryFormat
        self.parameter_input_metadata['GeometryFormat.Label'] = "Geometry Format"
        self.parameter_input_metadata['GeometryFormat.Required'] = True
        self.parameter_input_metadata['GeometryFormat.Tooltip'] = "	The geometry representation used within the " \
            "delimited file. Must be one of the following options: \nXY: The geometry is stored in two columns of " \
            "the delimited file. One column holds the X coordinates and the other column holds the Y coordinates. \n" \
            "WKT: The geometry is stored in one column of the delimited file. The geometry is in Well Known Text " \
            "representation."
        self.parameter_input_metadata['GeometryFormat.Values'] = ["", "XY", "WKT"]
        # XColumn
        self.parameter_input_metadata['XColumn.Label'] = "X Column"
        self.parameter_input_metadata['XColumn.Tooltip'] = "The name of the column in the delimited file " \
            "that holds the X coordinate data."
        self.parameter_input_metadata['XColumn.Value.Default'] = "If GeometryFormat is XY, this parameter is required."\
                "Otherwise this parameter is ignored."
        # YColumn
        self.parameter_input_metadata['YColumn.Label'] = "Y Column"
        self.parameter_input_metadata['YColumn.Tooltip'] = "The name of the column in the delimited file " \
            "that holds the Y coordinate data."
        self.parameter_input_metadata['YColumn.Value.Default'] = "If GeometryFormat is XY, this parameter is required."\
            "Otherwise, this parameter is ignored."
        # WKTColumn
        self.parameter_input_metadata['WKTColumn.Label'] = "WKT Column"
        self.parameter_input_metadata['WKTColumn.Tooltip'] = "The name of the column in the delimited file that " \
            "holds the WKT geometry data. \nIf GeometryFormat is WKT, this parameter is required. Otherwise, " \
            "this parameter is ignored."
        # Delimiter
        self.parameter_input_metadata['Delimiter.Label'] = "Delimiter"
        self.parameter_input_metadata['Delimiter.Tooltip'] = "The delimiter used to separate the columns of the " \
            "delimited file.\nMust enter the actual character instead of spelling the character. For example, ',' " \
            "is correct but COMMA is not correct."
        self.parameter_input_metadata['Delimiter.Value.Default'] = "','"
        # GeoLayerID
        self.parameter_input_metadata['GeoLayerID.Description'] = "a GeoLayerID"
        self.parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
        self.parameter_input_metadata['GeoLayerID.Tooltip'] = "A GeoLayer identifier. Formatting characters are " \
            "recognized."
        self.parameter_input_metadata['GeoLayerID.Value.Default'] = "The delimited filename without the leading path " \
            "and without the file extension (equivalent to formatting character %f)."
        # IfGeoLayerIDExists
        self.parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID Exists"
        self.parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = "The action that occurs if the OutputGeoLayerID " \
            "already exists within the GeoProcessor. \nReplace : The existing GeoLayer within the " \
            "GeoProcessor is overwritten with the new GeoLayer. No warning is logged. \n" \
            "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new " \
            "GeoLayer. A warning is logged. \nWarn : The new GeoLayer is not created. A warning is logged. \n" \
            "Fail : The new GeoLayer is not created. A fail message is logged. "
        self.parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
        self.parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"

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

        # Check that the appropriate parameters have a string value.
        for parameter in ['DelimitedFile', 'Delimiter', 'CRS', 'GeoLayerID']:

            # Get the parameter value.
            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)

            # Check that the parameter value is a non-empty, non-None string. If not, raise a FAILURE.
            if not validators.validate_string(parameter_value, False, False):

                message = "{} parameter has no value.".format(parameter)
                recommendation = "Specify the {} parameter.".format(parameter)
                warning += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that the GeometryFormat is either `XY` or `WKT`.
        pv_GeometryFormat = self.get_parameter_value(parameter_name="GeometryFormat", command_parameters=command_parameters)
        acceptable_values = ["WKT", "XY"]

        if not validators.validate_string_in_list(pv_GeometryFormat, acceptable_values, none_allowed=False,
                                                  empty_string_allowed=False, ignore_case=True):

            message = "GeometryFormat parameter value ({}) is not recognized.".format(pv_GeometryFormat)
            recommendation = "Specify one of the acceptable values ({}) for the GeometryFormat parameter.".format(
                acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that the correct ColumnName variables are correct.
        else:

            # If the pv_GeometryFormat is "WKT" then check that the WKTColumn has a string value.
            if pv_GeometryFormat is not None and pv_GeometryFormat.upper() == "WKT":

                # Check that the parameter value is a non-None string. If not, raise a FAILURE.
                if not validators.validate_string("WKTColumn", False, True):
                    message = "WKTColumn parameter has no value."
                    recommendation = "Specify the WKTColumn parameter."
                    warning += "\n" + message
                    self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                    recommendation))

            else:

                # Check that the appropriate parameters have a string value.
                for parameter in ['XColumn', 'YColumn']:

                    # Get the parameter value.
                    parameter_value = self.get_parameter_value(parameter_name=parameter,
                                                               command_parameters=command_parameters)

                    # Check that the parameter value is a non-None string. If not, raise a FAILURE.
                    if not validators.validate_string(parameter_value, False, True):
                        message = "{} parameter has no value.".format(parameter)
                        recommendation = "Specify the {} parameter.".format(parameter)
                        warning += "\n" + message
                        self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                                       CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                        recommendation))

        # Check that optional parameter IfGeoLayerIDExists is either `Replace`, `ReplaceAndWarn`, `Warn`, `Fail`, None.
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        acceptable_values = ["Replace", "ReplaceAndWarn", "Warn", "Fail"]
        if not validators.validate_string_in_list(pv_IfGeoLayerIDExists, acceptable_values, none_allowed=True,
                                                  empty_string_allowed=True, ignore_case=True):

            message = "IfGeoLayerIDExists parameter value ({}) is not recognized.".format(pv_IfGeoLayerIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfGeoLayerIDExists parameter.".format(
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
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def __should_read_geolayer(self, delimited_file, delimiter, geom_format, x_col, y_col, wkt_col, crs, geolayer_id):

        """
        Checks the following:
        * the DelimitedFile (absolute) is a valid file
        * if the CSV is using XY coordinates
        * -- > the XColumn is an actual field name
        * -- > the YColumn is an actual field name
        * if the CSV if using WKT geometries
        * -- > the WKTColumn is an actual field name
        * the CRS code is a valid code
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)

        Args:
            * delimited_file (str, required): The absolute path to the delimited file to be read.
            * delimiter (str, required): The delimiter symbol used in the delimited file. Often times a comma.
            * geom_format (str): The format of the geometry representation in the delimited file. Either `WKT` or `XY`.
            * x_col (str): The name of the delimited file column that holds the x coordinate data.
            * y_col (str): The name of the delimited file column that holds the y coordinate data.
            * crs (str, EPSG format): The coordinate reference system code associated with the X and Y coordinates.
            * geolayer_id (str): the GeoLayer identifier.

        Returns:
            Boolean. If TRUE, the geolayer should be read. If FALSE, the geolayer should not be read.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the 
        # test confirms that the command should be run. 
        should_run_command = []

        # If the input DelimitedFile is not a valid file path, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsFilePathValid", "DelimitedFile", delimited_file,
                                                       "FAIL"))

        # If the Delimited File exists, continue with the following checks.
        if should_run_command[0] is True:

            # If the geometry format is "XY", continue.
            if geom_format.upper() == "XY":

                # If the XColumn is not an existing column name in the delimited file, raise a FAILURE.
                should_run_command.append(validators.run_check(self, "IsDelimitedFileColumnNameValid", "XColumn", x_col,
                                                               "FAIL", other_values=[delimited_file, delimiter]))

                # If the YColumn is not an existing column name in the delimited file, raise a FAILURE.
                should_run_command.append(validators.run_check(self, "IsDelimitedFileColumnNameValid", "YColumn", y_col,
                                                               "FAIL", other_values=[delimited_file, delimiter]))

            # If the geometry format is "WKT", continue.
            else:

                # If the WKTColumn is not an existing column name in the delimited file, raise a FAILURE.
                should_run_command.append(validators.run_check(self, "IsDelimitedFileColumnNameValid", "WKTColumn",
                                                               wkt_col, "FAIL",
                                                               other_values=[delimited_file, delimiter]))

        # If the input CRS code is not a valid coordinate reference code, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsCrsCodeValid", "CRS", crs, "FAIL"))

        # If the GeoLayer ID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE (depends on the
        # value of the IfGeoLayerIDExists parameter.) The required, the IfGeoLayerIDExists parameter value is retrieved
        # inside run_check function.
        should_run_command.append(validators.run_check(self, "IsGeoLayerIdUnique", "GeoLayerID", geolayer_id, None))

        # Return the Boolean to determine if the process should be run. 
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self):
        """
        Run the command. Read the layer file from a delimited file, create a GeoLayer object, and add to the
        GeoProcessor's geolayer list.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_DelimitedFile = self.get_parameter_value("DelimitedFile")
        pv_Delimiter = self.get_parameter_value("Delimiter", default_value=',')
        pv_GeometryFormat = self.get_parameter_value("GeometryFormat")
        pv_XColumn = self.get_parameter_value("XColumn", default_value=None)
        pv_YColumn = self.get_parameter_value("YColumn", default_value=None)
        pv_WKTColumn = self.get_parameter_value("WKTColumn", default_value=None)
        pv_CRS = self.get_parameter_value("CRS")
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID", default_value='%f')

        # Convert the DelimitedFile parameter value relative path to an absolute path and expand for ${Property}
        # syntax
        delimited_file_abs = io_util.verify_path_for_os(io_util.to_absolute_path(
            self.command_processor.get_property('WorkingDir'),
            self.command_processor.expand_parameter_value(pv_DelimitedFile, self)))

        # If the pv_GeoLayerID is a valid %-formatter, assign the pv_GeoLayerID the corresponding value.
        if pv_GeoLayerID in ['%f', '%F', '%E', '%P', '%p']:
            pv_GeoLayerID = io_util.expand_formatter(delimited_file_abs, pv_GeoLayerID)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_read_geolayer(delimited_file_abs, pv_Delimiter, pv_GeometryFormat, pv_XColumn,
                                       pv_YColumn, pv_WKTColumn, pv_CRS, pv_GeoLayerID):

            try:

                if pv_GeometryFormat.upper() == "XY":

                    # Create a QGSVectorLayer object with the delimited file.
                    qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_delimited_file_xy(delimited_file_abs,
                                                                                            pv_Delimiter, pv_CRS,
                                                                                            pv_XColumn,
                                                                                            pv_YColumn)

                else:
                    # Create a QGSVectorLayer object with the delimited file.
                    qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_delimited_file_wkt(delimited_file_abs,
                                                                                             pv_Delimiter, pv_CRS,
                                                                                             pv_WKTColumn)

                # Create a GeoLayer and add it to the geoprocessor's GeoLayers list.
                geolayer_obj = GeoLayer(pv_GeoLayerID, qgs_vector_layer, delimited_file_abs)
                self.command_processor.add_geolayer(geolayer_obj)

            # Raise an exception if an unexpected error occurs during the process.
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error reading GeoLayer {} from delimited file {}.".format(pv_GeoLayerID,
                                                                                                pv_DelimitedFile)
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
