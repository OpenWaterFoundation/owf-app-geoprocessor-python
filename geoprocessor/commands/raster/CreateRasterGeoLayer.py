# CreateRasterGeoLayer - command to create a raster GeoLayer
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

from geoprocessor.core.CommandError import CommandError
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType
from geoprocessor.core.GeoLayer import GeoLayer
from geoprocessor.core.RasterGeoLayer import RasterGeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.validator_util as validator_util

import gdal

import logging


class CreateRasterGeoLayer(AbstractCommand):
    """
    Creates a new raster GeoLayer.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("NewGeoLayerID", str),
        CommandParameterMetadata("DataType", str),
        CommandParameterMetadata("CRS", str),
        CommandParameterMetadata("NumRows", str),
        CommandParameterMetadata("NumColumns", str),
        CommandParameterMetadata("NumBands", str),
        CommandParameterMetadata("OriginX", float),
        CommandParameterMetadata("OriginY", float),
        CommandParameterMetadata("PixelWidth", float),
        CommandParameterMetadata("PixelHeight", float),
        CommandParameterMetadata("InitialValue", str),
        # TODO smalers 2020-11-26 How to set?
        # CommandParameterMetadata("NoDataValue", str),
        CommandParameterMetadata("IfGeoLayerIDExists", str)]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = (
        "Create a new raster GeoLayer, using TIF driver.\n"
        "A temporary file will be created and will be read into memory.\n"
        "Once created, the layer can be processed with other commands."
    )
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # NewGeoLayerID
    __parameter_input_metadata['NewGeoLayerID.Description'] = "id of the new GeoLayer"
    __parameter_input_metadata['NewGeoLayerID.Label'] = "New GeoLayerID"
    __parameter_input_metadata['NewGeoLayerID.Required'] = True
    __parameter_input_metadata['NewGeoLayerID.Tooltip'] = "The ID of the new GeoLayer."
    # NumBands
    __parameter_input_metadata['NumBands.Description'] = "number of bands"
    __parameter_input_metadata['NumBands.Label'] = "Number of bands"
    __parameter_input_metadata['NumBands.Required'] = True
    __parameter_input_metadata['NumBands.Tooltip'] = "Number of bands in the raster layer."
    # NumColumns
    __parameter_input_metadata['NumColumns.Description'] = "number of columns"
    __parameter_input_metadata['NumColumns.Label'] = "Number of columns"
    __parameter_input_metadata['NumColumns.Required'] = True
    __parameter_input_metadata['NumColumns.Tooltip'] = "Number of columns in the raster layer."
    # NumRows
    __parameter_input_metadata['NumRows.Description'] = "number of rows"
    __parameter_input_metadata['NumRows.Label'] = "Number of rows"
    __parameter_input_metadata['NumRows.Required'] = True
    __parameter_input_metadata['NumRows.Tooltip'] = "Number of rows in the raster layer."
    # DataType
    __parameter_input_metadata['DataType.Description'] = "cell data type for each band (see tooltip)"
    __parameter_input_metadata['DataType.Label'] = "Data type for bands"
    __parameter_input_metadata['DataType.Required'] = True
    __parameter_input_metadata['DataType.Tooltip'] = "The data type for each band, separated by commas " \
                                                     "(Byte, Int16, Int32, Float32, Float64, UInt16, UInt32)."
    # CRS
    __parameter_input_metadata['CRS.Description'] = "coordinate references system of the new GeoLayer"
    __parameter_input_metadata['CRS.Label'] = "CRS"
    __parameter_input_metadata['CRS.Required'] = True
    __parameter_input_metadata['CRS.Tooltip'] = (
        "The coordinate reference system of the new GeoLayer. EPSG or "
        "ESRI code format required (e.g. EPSG:4326, EPSG:26913, ESRI:102003).")
    # OriginX
    __parameter_input_metadata['OriginX.Description'] = "origin x-coordinate"
    __parameter_input_metadata['OriginX.Label'] = "Origin X"
    __parameter_input_metadata['OriginX.Required'] = True
    __parameter_input_metadata['OriginX.Tooltip'] = "Origin x-coordinate, in units of the coordinate reference system."
    # OriginY
    __parameter_input_metadata['OriginY.Description'] = "origin y-coordinate"
    __parameter_input_metadata['OriginY.Label'] = "Origin Y"
    __parameter_input_metadata['OriginY.Required'] = True
    __parameter_input_metadata['OriginY.Tooltip'] = "Origin y-coordinate, in units of the coordinate reference system."
    # PixelWidth
    __parameter_input_metadata['PixelWidth.Description'] = "pixel width"
    __parameter_input_metadata['PixelWidth.Label'] = "Pixel width"
    __parameter_input_metadata['PixelWidth.Required'] = True
    __parameter_input_metadata['PixelWidth.Tooltip'] = "Pixel width, in units of the coordinate reference system."
    # PixelHeight
    __parameter_input_metadata['PixelHeight.Description'] = "pixel height"
    __parameter_input_metadata['PixelHeight.Label'] = "Pixel height"
    __parameter_input_metadata['PixelHeight.Required'] = True
    __parameter_input_metadata['PixelHeight.Tooltip'] = "Pixel height, in units of the coordinate reference system."
    # IfGeoLayerIDExists
    __parameter_input_metadata['IfGeoLayerIDExists.Description'] = "action if output exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = (
        "The action that occurs if the NewGeoLayerID already exists within the GeoProcessor.\n"
        "Replace: The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer. "
        "No warning is logged.\n"
        "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer. "
        "A warning is logged.\n"
        "Warn: The new GeoLayer is not created. A warning is logged.\n"
        "Fail: The new GeoLayer is not created. A fail message is logged.")
    __parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
    __parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "CreateRasterGeoLayer"
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

        Returns:
            None.

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
                self.command_status.add_to_log(
                    CommandPhaseType.INITIALIZATION,
                    CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that OriginX parameter is a float
        # noinspection PyPep8Naming
        pv_OriginX = self.get_parameter_value(parameter_name="OriginX",
                                              command_parameters=command_parameters)
        if not validator_util.validate_float(pv_OriginX, none_allowed=False, empty_string_allowed=False,
                                             zero_allowed=False):
            message = "OriginX parameter value ({}) is invalid.".format(pv_OriginX)
            recommendation = "Specify a number."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that OriginY parameter is a float and not 0 (zero causes CRS issue?)
        # noinspection PyPep8Naming
        pv_OriginY = self.get_parameter_value(parameter_name="OriginY",
                                              command_parameters=command_parameters)
        if not validator_util.validate_float(pv_OriginY, none_allowed=False, empty_string_allowed=False,
                                             zero_allowed=False):
            message = "OriginX parameter value ({}) is invalid.".format(pv_OriginY)
            recommendation = "Specify a number."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that PixelWidth parameter is a float (zero causes CRS issue?)
        # noinspection PyPep8Naming
        pv_PixelWidth = self.get_parameter_value(parameter_name="PixelWidth",
                                                 command_parameters=command_parameters)
        if not validator_util.validate_float(pv_PixelWidth, none_allowed=False, empty_string_allowed=False):
            message = "PixelWidth parameter value ({}) is invalid.".format(pv_PixelWidth)
            recommendation = "Specify a number."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that PixelHeight parameter is a float
        # noinspection PyPep8Naming
        pv_PixelHeight = self.get_parameter_value(parameter_name="PixelHeight",
                                                  command_parameters=command_parameters)
        if not validator_util.validate_float(pv_PixelHeight, none_allowed=False, empty_string_allowed=False):
            message = "PixelHeight parameter value ({}) is invalid.".format(pv_PixelHeight)
            recommendation = "Specify a number."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional IfGeoLayerIDExists param is either `Replace`, `Warn`, `Fail`, `ReplaceAndWarn` or None.
        # noinspection PyPep8Naming
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        acceptable_values = ["Replace", "Warn", "Fail", "ReplaceAndWarn"]
        if not validator_util.validate_string_in_list(pv_IfGeoLayerIDExists, acceptable_values, none_allowed=True,
                                                      empty_string_allowed=True, ignore_case=True):
            message = "IfGeoLayerIDExists parameter value ({}) is not recognized.".format(pv_IfGeoLayerIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfGeoLayerIDExists parameter.".format(
                acceptable_values)
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
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, geolayer_id: str, crs: str) -> bool:
        """
        Checks the following:
        * the CRS is a valid CRS
        * the ID of the new GeoLayer is unique (not an existing GeoLayer ID)
        * if the GeometryFormat is BoundingBox, check that the string has 4 items

        Args:
            geolayer_id: the id of the GeoLayer to be created
            crs: the crs code of the GeoLayer to be created

        Returns:
             Boolean. If TRUE, the GeoLayer should be simplified If FALSE, at least one check failed and the GeoLayer
                should not be simplified.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the CRS is not a valid coordinate reference system code, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsCRSCodeValid", "CRS", crs, "FAIL"))

        # If the new GeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE
        # (depends on the value of the IfGeoLayerIDExists parameter.)
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIdUnique", "NewGeoLayerID",
                                                           geolayer_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Create the GeoLayer with the input geometries.
        Add GeoLayer to the GeoProcessor's geolayers list.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_NewGeoLayerID = self.get_parameter_value("NewGeoLayerID")
        # noinspection PyPep8Naming
        pv_DataType = self.get_parameter_value("DataType")
        # noinspection PyPep8Naming
        pv_CRS = self.get_parameter_value("CRS")
        # noinspection PyPep8Naming
        pv_NumRows = self.get_parameter_value("NumRows")
        num_rows = int(pv_NumRows)
        # noinspection PyPep8Naming
        pv_NumColumns = self.get_parameter_value("NumColumns")
        num_columns = int(pv_NumColumns)
        # noinspection PyPep8Naming
        pv_NumBands = self.get_parameter_value("NumBands")
        num_bands = int(pv_NumBands)
        # noinspection PyPep8Naming
        pv_OriginX = self.get_parameter_value("OriginX")
        origin_x = float(pv_OriginX)
        # noinspection PyPep8Naming
        pv_OriginY = self.get_parameter_value("OriginY")
        origin_y = float(pv_OriginY)
        # noinspection PyPep8Naming
        pv_PixelWidth = self.get_parameter_value("PixelWidth")
        pixel_width = float(pv_PixelWidth)
        # noinspection PyPep8Naming
        pv_PixelHeight = self.get_parameter_value("PixelHeight")
        pixel_height = float(pv_PixelHeight)
        # noinspection PyPep8Naming
        pv_InitialValue = self.get_parameter_value("InitialValue")
        initial_value = None
        if pv_InitialValue is not None and pv_InitialValue != '':
            if pv_DataType.upper().find('Int') or pv_DataType.upper() == 'BYTE':
                initial_value = int(pv_InitialValue)
            else:
                initial_value = float(pv_InitialValue)

        if self.check_runtime_data(pv_NewGeoLayerID, pv_CRS):
            # noinspection PyBroadException
            try:
                # Create the QgsVectorLayer.
                layer = qgis_util.create_qgsrasterlayer(
                    crs=pv_CRS,
                    num_rows=num_rows,
                    num_columns=num_columns,
                    num_bands=num_bands,
                    origin_x=origin_x,
                    origin_y=origin_y,
                    pixel_width=pixel_width,
                    pixel_height=pixel_height,
                    data_type=pv_DataType,
                    initial_value=initial_value)

                # Create a new GeoLayer with the QgsVectorLayer and add it to the GeoProcesor's geolayers list.
                # - treat as if memory since a temporary file is used but not expected to be used later
                new_geolayer = RasterGeoLayer(geolayer_id=pv_NewGeoLayerID,
                                              name=pv_NewGeoLayerID,
                                              qgs_raster_layer=layer,
                                              input_path_full=GeoLayer.SOURCE_MEMORY,
                                              input_path=GeoLayer.SOURCE_MEMORY)
                self.command_processor.add_geolayer(new_geolayer)

            except Exception:
                self.warning_count += 1
                message = "Unexpected error creating GeoLayer ({}).".format(pv_NewGeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
