# ReadRasterGeoLayerFromFile - command to read a GeoLayer from a shapefile
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
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validator_util

import os
import logging


# TODO smalers 2020-03-21 need to fully implement - add Name and Description parameters.
class ReadRasterGeoLayerFromFile(AbstractCommand):
    """
    Read a raster GeoLayer from a raster data file (any recognized file extension).

    This command reads a raster GeoLayer from a file and creates a GeoLayer object within the
    geoprocessor. The GeoLayer can then be accessed in the geoprocessor by its identifier and further processed.

    In order for the geoprocessor to use and manipulate spatial data files, GeoLayers are instantiated as
    `QgsRasterLayer <https://qgis.org/api/classQgsRasterLayer.html>` objects.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("InputFile", str,
                                 parameter_description="Path to file",
                                 editor_tooltip="Path to raster file to read, can use ${Property}."),
        CommandParameterMetadata("GeoLayerID", str,
                                 parameter_description="GeoLayer identifier",
                                 editor_tooltip="GeoLayer identifier."),
        CommandParameterMetadata("Name", str),
        CommandParameterMetadata("Description", str),
        CommandParameterMetadata("Properties", str),
        CommandParameterMetadata("IfGeoLayerIDExists", str,
                                 parameter_description="Action if GeoLayer exists",
                                 default_value="Warn",
                                 editor_tooltip="Action if GeoLayer exists.")  # ,
        # TODO smalers 2020-11-29 it would be good to be able to turn on debugging for drivers
        # CommandParameterMetadata("Debug", str)
    ]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Read a raster GeoLayer from a file."
    __command_metadata['EditorType'] = "Simple"

    # Parameter Metadata
    __parameter_input_metadata = dict()
    # InputFile
    __parameter_input_metadata['InputFile.Description'] = "Raster file to read"
    __parameter_input_metadata['InputFile.Label'] = "Raster file to read"
    __parameter_input_metadata['InputFile.Tooltip'] = \
        "The raster file to read (relative or absolute path, must have recognized extension)." + \
        "${Property} syntax is recognized."
    __parameter_input_metadata['InputFile.Required'] = True
    __parameter_input_metadata['InputFile.FileSelector.Type'] = "Read"
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "output GeoLayer identifier"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Tooltip'] = (
        "A GeoLayer identifier. Formatting characters and ${Property} syntax is recognized.")
    __parameter_input_metadata['GeoLayerID.Value.Default'] = (
        "The GeoJSON filename without the leading path and without the file extension.")
    # Name
    __parameter_input_metadata['Name.Description'] = "GeoLayer name"
    __parameter_input_metadata['Name.Label'] = "Name"
    __parameter_input_metadata['Name.Required'] = False
    __parameter_input_metadata['Name.Tooltip'] = "The GeoLayer name, can use ${Property}."
    __parameter_input_metadata['Name.Value.Default.Description'] = "GeoLayerID"
    # Description
    __parameter_input_metadata['Description.Description'] = "GeoLayer description"
    __parameter_input_metadata['Description.Label'] = "Description"
    __parameter_input_metadata['Description.Required'] = False
    __parameter_input_metadata['Description.Tooltip'] = "The GeoLayer description, can use ${Property}."
    __parameter_input_metadata['Description.Value.Default'] = ''
    # Properties
    __parameter_input_metadata['Properties.Description'] = "properties for the new GeoLayer"
    __parameter_input_metadata['Properties.Label'] = "Properties"
    __parameter_input_metadata['Properties.Required'] = False
    __parameter_input_metadata['Properties.Tooltip'] = \
        "Properties for the new GeoLayer using syntax:  property:value,property:'value'"
    # IfGeoLayerIDExists
    __parameter_input_metadata['IfGeoLayerIDExists.Description'] = "action if exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = (
        "The action that occurs if the GeoLayerID already exists within the GeoProcessor.\n"
        "Replace : The existing GeoLayer within the GeoProcessor is overwritten with the new"
        "GeoLayer. No warning is logged.\n"
        "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new "
        "GeoLayer. A warning is logged. \n"
        "Warn : The new GeoLayer is not created. A warning is logged. \n"
        "Fail : The new GeoLayer is not created. A fail message is logged.")
    __parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
    __parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"
    # Debug
    __parameter_input_metadata['Debug.Description'] = "whether to turn on debug messages"
    __parameter_input_metadata['Debug.Label'] = "Debug?"
    __parameter_input_metadata['Debug.Tooltip'] = "Whether to turn on debug messages."
    __parameter_input_metadata['Debug.Values'] = ["", "False", "True"]
    __parameter_input_metadata['Debug.Value.Default'] = "False"

    # Choices for IfGeoLayerIDExists, used to validate parameter and display in editor
    __choices_IfGeoLayerIDExists = ["Replace", "ReplaceAndWarn", "Warn", "Fail"]

    def __init__(self) -> None:
        """
        Initialize the command
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "ReadRasterGeoLayerFromFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

        # Parameter Metadata
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

        # Check that optional parameter IfGeoLayerIDExists is one of the acceptable values or is None.
        # noinspection PyPep8Naming
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_IfGeoLayerIDExists, self.__choices_IfGeoLayerIDExists,
                                                      none_allowed=True, empty_string_allowed=True, ignore_case=True):
            message = "IfGeoLayerIDExists parameter value ({}) is not recognized.".format(pv_IfGeoLayerIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfGeoLayerIDExists parameter.".format(
                self.__choices_IfGeoLayerIDExists)
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

    def check_runtime_data(self, input_file_abs: str, input_is_url: bool, geolayer_id: str) -> bool:
        """
        Checks the following:
        * the input file (absolute) is a valid file
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)

        Args:
            input_file_abs: the full pathname to the input spatial data file
            input_is_url: whether the input file is a URL
            geolayer_id: the ID of the output GeoLayer

        Returns:
            run_read: Boolean. If TRUE, the read process should be run. If FALSE, the read process should not be run.
        """

        # Boolean to determine if the read process should be run. Set to true until an error occurs.
        run_read = True

        if input_is_url:
            # No checks because would be a performance hit to download a large file
            pass
        else:
            # If the input spatial data file is not a valid file path, raise a FAILURE.
            if not os.path.isfile(input_file_abs):

                run_read = False
                self.warning_count += 1
                message = "The InputFile ({}) is not a valid file.".format(input_file_abs)
                recommendation = "Specify a valid file."
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # If the GeoLayerID is the same as an already-registered GeoLayerID, react according to the
        # pv_IfGeoLayerIDExists value.
        if self.command_processor.get_geolayer(geolayer_id):
            # Get the IfGeoLayerIDExists parameter value.
            # noinspection PyPep8Naming
            pv_IfGeoLayerIDExists = self.get_parameter_value("IfGeoLayerIDExists", default_value="Replace")

            # Warnings/recommendations if the GeolayerID is the same as a registered GeoLayerID.
            message = 'The GeoLayerID ({}) value is already in use as a GeoLayer ID.'.format(geolayer_id)
            recommendation = 'Specify a new GeoLayerID.'

            if pv_IfGeoLayerIDExists.upper() == "REPLACEANDWARN":
                # The registered GeoLayer should be replaced with the new GeoLayer (with warnings).
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING,
                                                                message, recommendation))

            if pv_IfGeoLayerIDExists.upper() == "WARN":
                # The registered GeoLayer should not be replaced. A warning should be logged.
                run_read = False
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING,
                                                                message, recommendation))

            elif pv_IfGeoLayerIDExists.upper() == "FAIL":
                # The matching IDs should cause a FAILURE.
                run_read = False
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE,
                                                                message, recommendation))

        # Return the Boolean to determine if the read process should be run. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return run_read

    def run_command(self) -> None:
        """
        Run the command. Read the layer file from a raster format file, create a GeoLayer object, and add to the
        GeoProcessor's geolayer list.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_InputFile = self.get_parameter_value("InputFile")
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID", default_value='%f')
        # noinspection PyPep8Naming
        pv_Name = self.get_parameter_value("Name", default_value=pv_GeoLayerID)
        # noinspection PyPep8Naming
        pv_Description = \
            self.get_parameter_value("Description",
                                     default_value=self.parameter_input_metadata['Description.Value.Default'])
        # noinspection PyPep8Naming
        pv_Properties = self.get_parameter_value("Properties")
        # noinspection PyPep8Naming
        # pv_Debug = self.get_parameter_value("Debug", default_value='False')
        # debug = False
        # if pv_Debug is not None and (pv_Debug.upper() == 'True'):
        #    debug = True

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.command_processor.expand_parameter_value(pv_GeoLayerID, self)
        # noinspection PyPep8Naming
        pv_Name = self.command_processor.expand_parameter_value(pv_Name, self)
        # noinspection PyPep8Naming
        pv_Description = self.command_processor.expand_parameter_value(pv_Description, self)
        # noinspection PyPep8Naming
        pv_Properties = self.command_processor.expand_parameter_value(pv_Properties, self)

        # Convert the InputFile parameter value relative path to an absolute path and expand for ${Property}
        # syntax
        input_is_url = False
        if io_util.is_url(pv_InputFile):
            # Input is a URL
            input_file_absolute = pv_InputFile
            input_is_url = True
        else:
            input_file_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                         self.command_processor.expand_parameter_value(pv_InputFile, self)))

        # If the pv_GeoLayerID is a valid %-formatter, assign the pv_GeoLayerID the corresponding value.
        if pv_GeoLayerID in ['%f', '%F', '%E', '%P', '%p']:
            # noinspection PyPep8Naming
            pv_GeoLayerID = io_util.expand_formatter(input_file_absolute, pv_GeoLayerID)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(input_file_absolute, input_is_url, pv_GeoLayerID):
            # noinspection PyBroadException
            try:
                # Create a QGSRasterLayer object in raster format
                # qgs_raster_layer = qgis_util.read_qgsrasterlayer_from_file(input_file_absolute, debug = debug)
                qgs_raster_layer = qgis_util.read_qgsrasterlayer_from_file(input_file_absolute)

                file_extension = io_util.get_extension(pv_InputFile)
                input_format = RasterFormatType.get_format_from_extension(file_extension)
                # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
                geolayer_obj = RasterGeoLayer(geolayer_id=pv_GeoLayerID,
                                              name=pv_Name,
                                              description=pv_Description,
                                              qgs_raster_layer=qgs_raster_layer,
                                              input_format=input_format,
                                              input_path_full=input_file_absolute,
                                              input_path=pv_InputFile)
                # Set the properties
                properties = command_util.parse_properties_from_parameter_string(pv_Properties)
                # Set the properties as additional properties (don't just reset the properties dictionary)
                geolayer_obj.set_properties(properties)

                self.command_processor.add_geolayer(geolayer_obj)

            # Raise an exception if an unexpected error occurs during the process
            except Exception:

                self.warning_count += 1
                message = "Unexpected error reading RasterGeoLayer {} from raster file {}.".format(
                    pv_GeoLayerID, input_file_absolute)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise RuntimeError if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
