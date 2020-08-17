# RasterizeGeoLayer - command to create a raster GeoLayer from a vector GeoLayer
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
from geoprocessor.core import RasterFormatType
from geoprocessor.core.RasterGeoLayer import RasterGeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.validator_util as validator_util

from datetime import datetime
import logging
import os
from pathlib import Path
import tempfile

from qgis import processing


class RasterizeGeoLayer(AbstractCommand):
    """
    Creates a new raster GeoLayer from a vector GeoLayer.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("Attribute", type("")),
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("RasterFormat", type("")),
        CommandParameterMetadata("CellValueType", type("")),
        CommandParameterMetadata("RasterUnits", type("")),
        CommandParameterMetadata("RasterWidth", type("")),
        CommandParameterMetadata("RasterHeight", type("")),
        CommandParameterMetadata("CellWidth", type("")),
        CommandParameterMetadata("CellHeight", type("")),
        CommandParameterMetadata("ConstantValue", type("")),
        CommandParameterMetadata("MissingValue", type("")),
        CommandParameterMetadata("NewGeoLayerID", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Create a new raster GeoLayer from an existing vector GeoLayer.\n"\
        "The GDAL 'rasterize' tool is used.  A file is created and can be read as a GeoLayer.\n"\
        "Only raster formats that support georeferencing are supported."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "ID of the existing vector GeoLayer"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = "The ID of the existing vector GeoLayer."
    # Attribute
    __parameter_input_metadata['Attribute.Description'] = "GeoLayer attribute to transfer to raster"
    __parameter_input_metadata['Attribute.Label'] = "Attribute"
    __parameter_input_metadata['Attribute.Required'] = False
    __parameter_input_metadata['Attribute.Tooltip'] =\
        "The input GeoLayer attribute to transfer to the raster layer, or use ConstantValue."
    # OutputFile
    __parameter_input_metadata['OutputFile.Description'] = "Raster file to write"
    __parameter_input_metadata['OutputFile.Label'] = "Raster file to write"
    __parameter_input_metadata['OutputFile.Tooltip'] = \
        "The raster file to write (relative or absolute path, must have recognized extension). " + \
        "${Property} syntax is recognized.  If omitted, a temporary file will be created."
    __parameter_input_metadata['OutputFile.Required'] = False
    __parameter_input_metadata['OutputFile.FileSelector.Type'] = "Write"
    # RasterFormat
    __parameter_input_metadata['RasterFormat.Description'] = "raster format"
    __parameter_input_metadata['RasterFormat.Label'] = "Raster format"
    __parameter_input_metadata['RasterFormat.Required'] = False
    __parameter_input_metadata['RasterFormat.Tooltip'] =\
        "Raster format for temporary output file.  See:  https://gdal.org/drivers/raster/index.html"
    __parameter_input_metadata['RasterFormat.Values'] = ['GTiff']
    # __parameter_input_metadata['RasterFormat.Values'] = ['GeoTIFF', 'JPEG', 'JPEG2000']
    __parameter_input_metadata['RasterFormat.Value.Default'] = 'GTiff'
    __parameter_input_metadata['RasterFormat.Value.Default.ForEditor'] = ''
    # CellValueType
    __parameter_input_metadata['CellValueType.Description'] = "cell value type"
    __parameter_input_metadata['CellValueType.Label'] = "Cell value type"
    __parameter_input_metadata['CellValueType.Required'] = False
    __parameter_input_metadata['CellValueType.Tooltip'] = "Type of data value to store in each cell."
    __parameter_input_metadata['CellValueType.Values'] = ['Byte', 'Integer16', 'Integer32', 'Float32', 'Float64']
    __parameter_input_metadata['CellValueType.Value.Default'] = 'Byte'
    __parameter_input_metadata['CellValueType.Value.Default.ForEditor'] = ''
    # RasterUnits
    __parameter_input_metadata['RasterUnits.Description'] = "raster units (for cell dimension)"
    __parameter_input_metadata['RasterUnits.Label'] = "Raster units"
    __parameter_input_metadata['RasterUnits.Required'] = True
    __parameter_input_metadata['RasterUnits.Tooltip'] = "Units for the raster cells."
    __parameter_input_metadata['RasterUnits.Values'] = ['Pixels', 'GeoUnits']
    __parameter_input_metadata['RasterUnits.Value.Default'] = 'Pixels'
    # RasterWidth
    __parameter_input_metadata['RasterWidth.Description'] = "raster layer width in raster units"
    __parameter_input_metadata['RasterWidth.Label'] = "Raster width (if RasterUnits=Pixels)"
    __parameter_input_metadata['RasterWidth.Required'] = False
    __parameter_input_metadata['RasterWidth.Tooltip'] = "Raster width if RasterUnits=Pixels."
    # RasterHeight
    __parameter_input_metadata['RasterHeight.Description'] = "raster layer height in raster units"
    __parameter_input_metadata['RasterHeight.Label'] = "Raster height (if RasterUnits=Pixels)"
    __parameter_input_metadata['RasterHeight.Required'] = False
    __parameter_input_metadata['RasterHeight.Tooltip'] = "Raster height if RasterUnits=Pixels."
    # CellWidth
    __parameter_input_metadata['CellWidth.Description'] = "cell width in raster units"
    __parameter_input_metadata['CellWidth.Label'] = "Cell width (if RasterUnits=GeoUnits)"
    __parameter_input_metadata['CellWidth.Required'] = False
    __parameter_input_metadata['CellWidth.Tooltip'] = "Cell width if RasterUnits=GeoUnits."
    # CellHeight
    __parameter_input_metadata['CellHeight.Description'] = "cell height in raster units"
    __parameter_input_metadata['CellHeight.Label'] = "Cell height (if RasterUnits=GeoUnits)"
    __parameter_input_metadata['CellHeight.Required'] = False
    __parameter_input_metadata['CellHeight.Tooltip'] = "Cell height if RasterUnits=GeoUnits."
    # ConstantValue
    __parameter_input_metadata['ConstantValue.Description'] = "constant data value to assign"
    __parameter_input_metadata['ConstantValue.Label'] = "Constant value"
    __parameter_input_metadata['ConstantValue.Required'] = False
    __parameter_input_metadata['ConstantValue.Tooltip'] = "Constant value to assign if Attribute is not specified."
    # MissingValue
    __parameter_input_metadata['MissingValue.Description'] = "missing data value"
    __parameter_input_metadata['MissingValue.Label'] = "Missing value"
    __parameter_input_metadata['MissingValue.Required'] = False
    __parameter_input_metadata['MissingValue.Tooltip'] = "Value to use for missing values."
    # NewGeoLayerID
    __parameter_input_metadata['NewGeoLayerID.Description'] = "ID of the new GeoLayer"
    __parameter_input_metadata['NewGeoLayerID.Label'] = "New GeoLayerID"
    __parameter_input_metadata['NewGeoLayerID.Required'] = False
    __parameter_input_metadata['NewGeoLayerID.Tooltip'] =\
        "The ID of the new GeoLayer.  If omitted, use another command to read the output file."
    # IfGeoLayerIDExists
    __parameter_input_metadata['IfGeoLayerIDExists.Description'] = "action if output exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = (
        "The action that occurs if the NewGeoLayerID already exists within the GeoProcessor.\n"
        "Replace: The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer. "
        "No warning is logged.\n"
        "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer. "
        "A warning is logged. \n"
        "Warn: The new GeoLayer is not created. A warning is logged. \n"
        "Fail: The new GeoLayer is not created. A fail message is logged.")
    __parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
    __parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"
    # __parameter_input_metadata['IfGeoLayerIDExists.Value.Default.ForEditor'] = ""

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "RasterizeGeoLayer"
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

    def check_runtime_data(self, new_geolayer_id: str) -> bool:
        """
        Checks the following:
        * the ID of the new GeoLayer is unique (not an existing GeoLayer ID)

        Args:
            new_geolayer_id: the id of the GeoLayer to be created

        Returns:
             Boolean. If TRUE, the GeoLayer should be simplified If FALSE, at least one check failed and the GeoLayer
                should not be simplified.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the new GeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE
        # (depends on the value of the IfGeoLayerIDExists parameter.)
        # should_run_command.append(validator_util.run_check(self, "IsGeoLayerIdUnique", "NewGeoLayerID",
        #                                                   new_geolayer_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Create the raster GeoLayer from the vector GeoLayer.
        Add GeoLayer to the GeoProcessor's geolayers list.

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
        pv_Attribute = self.get_parameter_value("Attribute")
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value("OutputFile")
        # noinspection PyPep8Naming
        pv_RasterFormat = self.get_parameter_value(
            "RasterFormat", default_value=self.__parameter_input_metadata['RasterFormat.Value.Default'])
        # Use TIF for the raster format
        # - tif is handled well in GIS and is also supported by the OWF InfoMapper
        # - TODO smalers 2020-07-17 implement an enumeration to handle lookups
        raster_format_upper = pv_RasterFormat.upper()
        output_ext = 'tif'
        # noinspection PyPep8Naming
        pv_ConstantValue = self.get_parameter_value("ConstantValue")
        # noinspection PyPep8Naming
        pv_RasterUnits = self.get_parameter_value("RasterUnits")
        # noinspection PyPep8Naming
        pv_RasterWidth = self.get_parameter_value("RasterWidth")
        # noinspection PyPep8Naming
        pv_RasterHeight = self.get_parameter_value("RasterHeight")
        # noinspection PyPep8Naming
        pv_CellWidth = self.get_parameter_value("CellWidth")
        # noinspection PyPep8Naming
        pv_CellHeight = self.get_parameter_value("CellHeight")
        # noinspection PyPep8Naming
        pv_CellValueType = self.get_parameter_value("CellValueType")
        # noinspection PyPep8Naming
        pv_MissingValue = self.get_parameter_value("MissingValue")
        # noinspection PyPep8Naming
        pv_NewGeoLayerID = self.get_parameter_value("NewGeoLayerID")

        # Convert the OutputFile parameter value relative path to an absolute path and expand for ${Property} syntax
        output_is_tmp = False
        if pv_OutputFile is None or pv_OutputFile == "":
            # Create a temporary file name.
            output_is_tmp = True
            now = datetime.today()
            nowstring = '{:04d}-{:02d}-{:02d}-{:02d}-{:02d}-{:02d}.{}'.format(now.year, now.month, now.day,
                                                                              now.hour, now.minute,
                                                                              now.second, now.microsecond)
            # See:  https://svn.osgeo.org/gdal/tags/gdal_1_2_5/frmts/formats_list.html
            if raster_format_upper == 'GEOTIFF':
                output_ext = 'tif'
            # TODO smalers 2020-07-17 anything other than TIF seems to work
            elif raster_format_upper == 'JPEG':
                output_ext = 'jpg'
            elif raster_format_upper == 'JPEG2000':
                output_ext = 'j2k'
            raster_output_file = Path(tempfile.gettempdir()).joinpath('gp-{}-rasterize-{}.{}'.format(
                os.getpid(),
                nowstring,
                output_ext))
            # Second file is layer extent
            raster_aux_xml_output_file = Path(tempfile.gettempdir()).joinpath('gp-{}-rasterize-{}.{}.aux.xml'.
                                                                              format(os.getpid(), nowstring,
                                                                                     output_ext))
        else:
            # Use the specified output file
            output_file_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                         self.command_processor.expand_parameter_value(pv_OutputFile, self)))
            raster_output_file = Path(output_file_absolute)
            raster_aux_xml_output_file = Path(output_file_absolute + ".aux.xml")

        if self.check_runtime_data(pv_NewGeoLayerID):

            # noinspection PyBroadException
            try:
                # Get the GeoLayer which will be QgsVectorLayer
                # Passes a GeoLayerID to GeoProcessor to return the GeoLayer that matches the ID
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Assign parameter to pass into runAlgorithm
                # INPUT = input GeoLayer (QgsVectorLayer)
                # FIELD = Attribute name to split by
                # OUTPUT = path to write output GeoLayers to this creates a list of files following the naming
                #          convention attributeName_attributeValue.extension
                #          ex: GNIS_ID_00030007.shp
                #          The default format for QGIS 3.10 is GeoPackage with .gpkg extension.
                #          There is discussion that the format (via extension) should be able to be specified,
                #          but go with GeoPackage.
                alg_parameters = dict()
                alg_parameters['INPUT'] = input_geolayer.qgs_layer
                # Use the input layer ID to use it's extent
                extent = input_geolayer.qgs_layer.extent()
                # Despite documentation, it seems like extent requires the numbers
                # - see:  https://gis.stackexchange.com/questions/212645/
                #             how-to-make-qgis-processing-algorithms-use-default-parameter
                alg_parameters['EXTENT'] =\
                    '{},{},{},{}'.format(extent.xMinimum(), extent.xMaximum(), extent.yMinimum(), extent.yMaximum())
                if pv_Attribute is not None and pv_Attribute != "":
                    alg_parameters['FIELD'] = pv_Attribute
                units_are_int = True
                if pv_RasterUnits is not None and pv_RasterUnits != "":
                    if pv_RasterUnits.upper() == 'PIXELS':
                        units_are_int = True
                        alg_parameters['UNITS'] = 0
                    elif pv_RasterUnits.upper() == 'GEOUNITS':
                        units_are_int = False
                        alg_parameters['UNITS'] = 1
                if pv_ConstantValue is not None and pv_ConstantValue != "":
                    if units_are_int:
                        alg_parameters['BURN'] = int(pv_ConstantValue)
                    else:
                        alg_parameters['BURN'] = float(pv_ConstantValue)
                # The following is used with GeoUnits
                if pv_RasterWidth is not None and pv_RasterWidth != "":
                    if units_are_int:
                        alg_parameters['WIDTH'] = int(pv_RasterWidth)
                    else:
                        alg_parameters['WIDTH'] = float(pv_RasterWidth)
                if pv_RasterHeight is not None and pv_RasterHeight != "":
                    if units_are_int:
                        alg_parameters['HEIGHT'] = int(pv_RasterHeight)
                    else:
                        alg_parameters['HEIGHT'] = float(pv_RasterHeight)
                # The following is used with pixel units
                if pv_CellWidth is not None and pv_CellWidth != "":
                    if units_are_int:
                        alg_parameters['WIDTH'] = int(pv_CellWidth)
                    else:
                        alg_parameters['WIDTH'] = float(pv_CellWidth)
                if pv_CellHeight is not None and pv_CellHeight != "":
                    if units_are_int:
                        alg_parameters['HEIGHT'] = int(pv_CellHeight)
                    else:
                        alg_parameters['HEIGHT'] = float(pv_CellHeight)
                if pv_CellValueType is not None and pv_CellValueType != "":
                    raster_data_type_upper = pv_CellValueType.upper()
                    if raster_data_type_upper == 'BYTE':
                        alg_parameters['DATA_TYPE'] = 0
                    elif raster_data_type_upper == 'INTEGER16':
                        alg_parameters['DATA_TYPE'] = 1
                    elif raster_data_type_upper == 'INTEGER32':
                        alg_parameters['DATA_TYPE'] = 4
                    elif raster_data_type_upper == 'FLOAT32':
                        alg_parameters['DATA_TYPE'] = 5
                    elif raster_data_type_upper == 'FLOAT64':
                        alg_parameters['DATA_TYPE'] = 6
                if pv_MissingValue is not None and pv_MissingValue != "":
                    if units_are_int:
                        alg_parameters['NODATA'] = int(pv_MissingValue)
                    else:
                        alg_parameters['NODATA'] = float(pv_MissingValue)

                self.logger.info("Writing tmp output raster file: {}".format(raster_output_file))
                self.logger.info("Writing tmp output aux.xml file: {}".format(raster_aux_xml_output_file))
                alg_parameters['OUTPUT'] = str(raster_output_file)

                # Remove the file before running so that if an error the old output is not mistakenly used.
                if raster_output_file.exists():
                    # noinspection PyBroadException
                    try:
                        raster_output_file.unlink()
                    except Exception:
                        self.warning_count += 1
                        message = "Error removing temporary layer file before rasterize: {}).".format(
                            raster_output_file)
                        recommendation = \
                            "Confirm that no other application is using the file. Check the log file for details."
                        self.logger.warning(message, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.WARNING, message,
                                                                        recommendation))
                if raster_aux_xml_output_file.exists():
                    # noinspection PyBroadException
                    try:
                        raster_aux_xml_output_file.unlink()
                    except Exception:
                        self.warning_count += 1
                        message = "Error removing temporary layer file before rasterize: {}).".format(
                            raster_aux_xml_output_file)
                        recommendation = \
                            "Confirm that no other application is using the file. Check the log file for details."
                        self.logger.warning(message, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.WARNING, message,
                                                                        recommendation))

                # Call runAlgorithm with the parameter "gdal:rasterize" and pass in the parameters defined above.
                self.logger.info('Algorithm parameters: {}'.format(alg_parameters))
                # TODO smalers 2020-07-20 does not seem to be any difference between class or module.
                # - files ares still not unlinked
                # - aux.xml file seems to be delayed writing, even requiring GeoProcessor to exit?
                # - See:  https://gis.stackexchange.com/questions/136366/
                #           turn-off-the-setting-of-qgis-to-produce-xml-when-closing
                do_processing_class = True
                if do_processing_class:
                    # 'Processing' class
                    alg_output = self.command_processor.qgis_processor.runAlgorithm("gdal:rasterize",
                                                                                    alg_parameters
                                                                                    # feedback=self
                                                                                    )
                else:
                    # Lowercase 'processing'
                    alg_output = processing.run("gdal:rasterize",
                                                alg_parameters
                                                # feedback=self)
                                                )

                # Output is a dictionary
                self.logger.info("Algorithm output: {}".format(alg_output))

                # Read the raster layer file that was created.
                qgs_raster_layer = qgis_util.read_qgsrasterlayer_from_file(str(raster_output_file))

                if pv_NewGeoLayerID is not None and pv_NewGeoLayerID != "":
                    # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
                    # - for now hard-code the input format
                    input_format = RasterFormatType.GTiff
                    geolayer_obj = RasterGeoLayer(geolayer_id=pv_NewGeoLayerID,
                                                  name="test",
                                                  description="test",
                                                  qgs_raster_layer=qgs_raster_layer,
                                                  input_format=input_format,
                                                  input_path_full=str(raster_output_file),
                                                  input_path=str(raster_output_file))
                    self.command_processor.add_geolayer(geolayer_obj)

                if output_is_tmp:
                    # Remove the temporary files after running so that the file system does not fill up.
                    # - if not temporary file, leave the files
                    if raster_output_file.exists():
                        # noinspection PyBroadException
                        try:
                            raster_output_file.unlink()
                            self.logger.info("Removed temporary raster output file: {}".format(raster_output_file))
                        except Exception:
                            message = "Error removing temporary layer file after rasterize: {}).".format(
                                raster_output_file)
                            self.logger.warning(message, exc_info=True)
                            self.logger.warning("Will attempt to remove the next time GeoProcessor starts.")
                            # TODO smalers 2020-07-19
                            # self.warning_count += 1
                            # recommendation = \
                            #     "There is a known QGIS issue that is being evaluated. " \
                            #     "Check the log file for details. " \
                            #     "Will attempt to remove the next time GeoProcessor starts."
                            # self.command_status.add_to_log(CommandPhaseType.RUN,
                            #                                CommandLogRecord(CommandStatusType.WARNING, message,
                            #                                                 recommendation))
                            tmp_file_comments =\
                                ["Temporary file created by RasterizeGeoLayer command, process {}".format(os.getpid())]
                            io_util.add_tmp_file_to_remove(raster_output_file, tmp_file_comments)

                    if raster_aux_xml_output_file.exists():
                        # noinspection PyBroadException
                        try:
                            raster_aux_xml_output_file.unlink()
                            self.logger.info("Removed temporary raster output file: {}".format(
                                raster_aux_xml_output_file))
                        except Exception:
                            message = "Error removing temporary layer file after rasterize: {}).".format(
                                raster_aux_xml_output_file)
                            self.logger.warning(message, exc_info=True)
                            self.logger.warning("Will attempt to remove the next time GeoProcessor starts.")
                            # TODO smalers 2020-07-19
                            # self.warning_count += 1
                            # recommendation = \
                            #     "There is a known QGIS issue that is being evaluated. "\
                            #     "Check the log file for details. "\
                            #     "Will attempt to remove the next time GeoProcessor starts."
                            # self.command_status.add_to_log(CommandPhaseType.RUN,
                            #                                CommandLogRecord(CommandStatusType.WARNING, message,
                            #                                                 recommendation))
                            tmp_file_comments =\
                                ["Temporary file created by RasterizeGeoLayer command, process {}".format(os.getpid())]
                            io_util.add_tmp_file_to_remove(raster_aux_xml_output_file, tmp_file_comments)
                    else:
                        # There seems to be a delay writing this file so add to the remove list just in case
                        tmp_file_comments = ["Temporary file created by RasterizeGeoLayer command, process {}".format(
                            os.getpid())]
                        io_util.add_tmp_file_to_remove(raster_aux_xml_output_file, tmp_file_comments)

            except Exception:
                self.warning_count += 1
                message = "Unexpected error rasterizing GeoLayer ({}).".format(pv_NewGeoLayerID)
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
