# ReadRasterGeoLayerFromWebMapService - command to read a GeoLayer from a web map service (WMS)
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
import geoprocessor.util.validator_util as validator_util

import logging


# TODO smalers 2020-03-21 need to fully implement - add Name and Description parameters.
class ReadRasterGeoLayerFromWebMapService(AbstractCommand):
    """
    Read a raster GeoLayer from a web map service (WMS).

    This command reads a raster GeoLayer from a file and creates a GeoLayer object within the
    geoprocessor. The GeoLayer can then be accessed in the geoprocessor by its identifier and further processed.

    TODO smalers 2020-04-09 need to ealuate for processing, for now use to store the URL
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("InputUrl", type("")),
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("Name", type("")),
        CommandParameterMetadata("Description", type("")),
        CommandParameterMetadata("Properties", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Read a raster GeoLayer from a Web Map Service (WMS).\n" \
                                        "This layer is typically used for a background layer."
    __command_metadata['EditorType'] = "Simple"

    # Parameter Metadata
    __parameter_input_metadata = dict()
    # InputUrl
    __parameter_input_metadata['InputUrl.Description'] = "URL to WMS server"
    __parameter_input_metadata['InputUrl.Label'] = "WMS Url"
    __parameter_input_metadata['InputUrl.Tooltip'] = \
        "The Web Map Server (WMS) URL to read. ${Property} syntax is recognized."
    __parameter_input_metadata['InputUrl.Required'] = True
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "output GeoLayer identifier"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
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

    # Choices for IfGeoLayerIDExists, used to validate parameter and display in editor
    __choices_IfGeoLayerIDExists = ["Replace", "ReplaceAndWarn", "Warn", "Fail"]

    def __init__(self) -> None:
        """
        Initialize the command
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "ReadRasterGeoLayerFromWebMapService"
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

    def check_runtime_data(self, input_url: str, geolayer_id: str) -> bool:
        """
        Checks the following:
        * the input file (absolute) is a valid file
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)

        Args:
            input_url: the URL to the Web Map Service
            geolayer_id: the ID of the output GeoLayer

        Returns:
            run_read: Boolean. If TRUE, the read process should be run. If FALSE, the read process should not be run.
        """

        # Boolean to determine if the read process should be run. Set to true until an error occurs.
        run_read = True

        # If the input URL is not a valid URL, raise a FAILURE.
        # - TODO need to implement some type of check
        # if not os.path.isfile(input_file_abs):
        #     run_read = False
        #     self.warning_count += 1
        #     message = "The InputFile ({}) is not a valid file.".format(input_file_abs)
        #     recommendation = "Specify a valid file."
        #     self.logger.warning(message)
        #     self.command_status.add_to_log(CommandPhaseType.RUN,
        #                                    CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

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
        Run the command. Read the layer file from a Web Map Service (WMS), create a GeoLayer object, and add to the
        GeoProcessor's geolayer list.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_InputUrl = self.get_parameter_value("InputUrl")
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

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_InputUrl = self.command_processor.expand_parameter_value(pv_InputUrl, self)
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.command_processor.expand_parameter_value(pv_GeoLayerID, self)
        # noinspection PyPep8Naming
        pv_Name = self.get_parameter_value("Name", default_value=pv_GeoLayerID)
        # noinspection PyPep8Naming
        pv_Description = \
            self.get_parameter_value("Description",
                                     default_value=self.parameter_input_metadata['Description.Value.Default'])
        # noinspection PyPep8Naming
        pv_Properties = self.get_parameter_value("Properties")

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
        # input_file_absolute = io_util.verify_path_for_os(
        #     io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
        #                              self.command_processor.expand_parameter_value(pv_InputFile, self)))

        # If the pv_GeoLayerID is a valid %-formatter, assign the pv_GeoLayerID the corresponding value.
        # if pv_GeoLayerID in ['%f', '%F', '%E', '%P', '%p']:
        #     # noinspection PyPep8Naming
        #     pv_GeoLayerID = io_util.expand_formatter(input_file_absolute, pv_GeoLayerID)

        # Run the checks on the parameter values. Only continue if the checks passed.
        # if self.check_runtime_data(input_file_absolute, pv_GeoLayerID):
        #     # noinspection PyBroadException
        #     try:
        #         # Create a QGSRasterLayer object in raster format
        #         qgs_raster_layer = qgis_util.read_qgsrasterlayer_from_file(input_file_absolute)

        #         # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
        #         geolayer_obj = RasterGeoLayer(geolayer_id=pv_GeoLayerID,
        #                                       qgs_raster_layer=qgs_raster_layer,
        #                                       input_path_full=input_file_absolute,
        #                                       input_path=pv_InputFile)
        #         self.command_processor.add_geolayer(geolayer_obj)

        if self.check_runtime_data(pv_InputUrl, pv_GeoLayerID):
            try:
                qgs_raster_layer = None
                geolayer_obj = RasterGeoLayer(geolayer_id=pv_GeoLayerID,
                                              name=pv_Name,
                                              description=pv_Description,
                                              qgs_raster_layer=qgs_raster_layer,
                                              input_format=RasterFormatType.WMS,
                                              input_path_full=pv_InputUrl,
                                              input_path=pv_InputUrl)

                # Set the properties
                properties = command_util.parse_properties_from_parameter_string(pv_Properties)
                # Set the properties as additional properties (don't just reset the properties dictionary)
                geolayer_obj.set_properties(properties)

                self.command_processor.add_geolayer(geolayer_obj)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process
                self.warning_count += 1
                message = "Unexpected error reading RasterGeoLayer {} from Web Map Service {}.".format(
                    pv_GeoLayerID, pv_InputUrl)
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
