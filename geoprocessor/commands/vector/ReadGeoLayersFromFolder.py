# ReadGeoLayersFromFolder - command to read GeoLayers from a folder
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
from geoprocessor.core.VectorGeoLayer import VectorGeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validator_util
import geoprocessor.util.qgis_util as qgis_util

import os
import logging
import glob


class ReadGeoLayersFromFolder(AbstractCommand):
    """
    Reads the GeoLayers within a folder.

    This command reads a the GeoLayers from a folder and creates GeoLayer objects within the
    geoprocessor. The GeoLayers can then be accessed in the geoprocessor by their identifier and further processed.

    GeoLayers are stored on a a computer or are available for download as a spatial data file (GeoJSON, shapefile,
    feature class in a file geodatabase, etc.). Each GeoLayer has one feature type (point, line, polygon, etc.) and
    other data (an identifier, a coordinate reference system, etc). Note that this function only reads one or
    many GeoLayers from within a single folder.

    In order for the geoprocessor to use and manipulate spatial data files, GeoLayers are instantiated as
    `QgsVectorLayer <https://qgis.org/api/classQgsVectorLayer.html>`_ objects. This command will read the GeoLayers
    from spatial data files within a folder and instantiate them as geoprocessor GeoLayer objects.

    Command Parameters
    * SpatialDataFolder (str, required): the relative pathname to the folder containing spatial data files
    * GeoLayerID_prefix (str, optional): the GeoLayer identifier will, by default, use the filename of the spatial data
        file that is being read. However, if a value is set for this parameter, the GeoLayerID will take the following
        format: [GeoLayerID_prefix]_[filename]
    * Subset_Pattern (str, optional): the glob-style pattern of the file name to determine which files within the
        folder are to be processed. More information on creating a glob pattern can be found at:
         REF: <https://docs.python.org/2/library/glob.html>.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the CopiedGeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("SpatialDataFolder", type("")),
        CommandParameterMetadata("GeoLayerID_prefix", type("")),
        CommandParameterMetadata("Subset_Pattern", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Read one or more GeoLayer(s) from a folder."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # SpatialDataFolder
    __parameter_input_metadata['SpatialDataFolder.Description'] = "folder to read"
    __parameter_input_metadata['SpatialDataFolder.Label'] = "Spatial data folder"
    __parameter_input_metadata['SpatialDataFolder.Required'] = True
    __parameter_input_metadata['SpatialDataFolder.Tooltip'] = "The folder to read."
    __parameter_input_metadata['SpatialDataFolder.FileSelector.Type'] = "Read"
    __parameter_input_metadata['SpatialDataFolder.FileSelector.Title'] = "Select the spatial data folder to read"
    # GeoLayerID_prefix
    __parameter_input_metadata['GeoLayerID_prefix.Description'] = "output GeoLayer identifier prefix"
    __parameter_input_metadata['GeoLayerID_prefix.Label'] = "GeoLayerID prefix"
    __parameter_input_metadata['GeoLayerID_prefix.Tooltip'] = \
        "GeoLayers read from a folder have an identifier in the GeoLayerID_prefix_Filename format."
    __parameter_input_metadata['GeoLayerID_prefix.Value.Default'] = (
        "No prefix is used. The GeoLayerID is the spatial data filename without the leading path and without the "
        "file extension (Formatting character %f).")
    # Subset_Pattern
    __parameter_input_metadata['Subset_Pattern.Description'] = "globstyle pattern of feature classes to read"
    __parameter_input_metadata['Subset_Pattern.Label'] = "Subset pattern"
    __parameter_input_metadata['Subset_Pattern.Tooltip'] = \
        "The glob-style pattern (e.g., CO_* or *_[MC]O) of spatial data files to read from the folder."
    __parameter_input_metadata['Subset_Pattern.Value.Default'] = \
        "No pattern is used. All spatial data files (.shp and .geojson) within the folder are read."
    # IfGeoLayerIDExists
    __parameter_input_metadata['IfGeoLayerIDExists.Description'] = "action if exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = (
        "The action that occurs if the GeoLayerID already exists within the GeoProcessor.\n"
        "Replace : The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer.  "
        "No warning is logged.\n"
        "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new "
        "GeoLayer. A warning is logged. \n"
        "Warn : The new GeoLayer is not created. A warning is logged. \n"
        "Fail : The new GeoLayer is not created. A fail message is logged.")
    __parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
    __parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "ReadGeoLayersFromFolder"
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

        # Check that parameter SpatialDataFolder is a non-empty, non-None string.
        # noinspection PyPep8Naming
        pv_SpatialDataFolder = self.get_parameter_value(parameter_name='SpatialDataFolder',
                                                        command_parameters=command_parameters)

        if not validator_util.validate_string(pv_SpatialDataFolder, False, False):
            message = "SpatialDataFolder parameter has no value."
            recommendation = "Specify text for the SpatialDataFolder parameter."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional parameter IfGeoLayerIDExists is either `Replace`, `ReplaceAndWarn`, `Warn`, `Fail`, None.
        # noinspection PyPep8Naming
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        acceptable_values = ["Replace", "ReplaceAndWarn", "Warn", "Fail"]
        if not validator_util.validate_string_in_list(pv_IfGeoLayerIDExists, acceptable_values, none_allowed=True,
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

    def __should_read_folder(self, spatial_data_folder_abs: str) -> bool:

        """
        Checks the following:
        * the SpatialDataFolder (absolute) is a valid folder

        Args:
            spatial_data_folder_abs: the full pathname to the input spatial data folder

        Returns:
            run_read: Boolean. If TRUE, the folder read process should be run. If FALSE, it should not be run.
        """

        # Boolean to determine if the read process should be run. Set to true until an error occurs.
        run_read = True

        # If the input spatial data folder is not a valid file path, raise a FAILURE.
        if not os.path.isdir(spatial_data_folder_abs):

            run_read = False
            self.warning_count += 1
            message = "The SpatialDataFolder ({}) is not a valid folder.".format(spatial_data_folder_abs)
            recommendation = "Specify a valid folder."
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Return the Boolean to determine if the read process should be run. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return run_read

    def __should_read_geolayer(self, geolayer_id: str) -> bool:
        """
        Checks the following:
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)

        Args:
            geolayer_id: the ID of the output GeoLayer

        Returns:
            run_read: Boolean. If TRUE, the GeoLayer read process should be run. If FALSE, the read process should
             not be run.
        """

        # Boolean to determine if the read process should be run. Set to true until an error occurs.
        run_read = True

        # If the GeoLayerID is the same as an already-registered GeoLayerID, react according to the
        # pv_IfGeoLayerIDExists value.
        if self.command_processor.get_geolayer(geolayer_id):

            # Get the IfGeoLayerIDExists parameter value.
            # noinspection PyPep8Naming
            pv_IfGeoLayerIDExists = self.get_parameter_value("IfGeoLayerIDExists", default_value="Replace")

            # Warnings/recommendations if the GeolayerID is the same as a registered GeoLayerID.
            message = 'The GeoLayerID ({}) value is already in use as a GeoLayer ID.'.format(geolayer_id)
            recommendation = 'Specify a new GeoLayerID.'

            # The registered GeoLayer should be replaced with the new GeoLayer (with warnings).
            if pv_IfGeoLayerIDExists.upper() == "REPLACEANDWARN":
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING,
                                                                message, recommendation))

            # The registered GeoLayer should not be replaced. A warning should be logged.
            if pv_IfGeoLayerIDExists.upper() == "WARN":

                run_read = False
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING,
                                                                message, recommendation))

            # The matching IDs should cause a FAILURE.
            elif pv_IfGeoLayerIDExists.upper() == "FAIL":

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
        Run the command. Read all spatial data files within the folder. For each desired spatial data file (can be
        specified by the Subset_Pattern parameter), create a GeoLayer object, and add to the GeoProcessor's geolayer
        list.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_SpatialDataFolder = self.get_parameter_value("SpatialDataFolder")
        # noinspection PyPep8Naming
        pv_Subset_Pattern = self.get_parameter_value("Subset_Pattern")
        # noinspection PyPep8Naming
        pv_GeoLayerID_prefix = self.get_parameter_value("GeoLayerID_prefix")

        # Convert the SpatialDataFolder parameter value relative path to an absolute path
        sd_folder_abs = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_SpatialDataFolder, self)))

        # Run the initial checks on the parameter values. Only continue if the checks passed.
        if self.__should_read_folder(sd_folder_abs):

            # Determine which files within the folder should be processed. All files will be processed if
            # pv_Subset_Pattern is set to None. Otherwise only files that match the given pattern will be processed.
            # Check that each file in the folder is:
            #   1. a file
            #   2. a spatial data file (ends in .shp or .geojson)
            #   3. follows the given pattern (if Subset_Pattern parameter value does not equal None)
            if pv_Subset_Pattern:
                spatial_data_files_abs = [os.path.join(sd_folder_abs, source_file)
                                          for source_file in glob.glob(os.path.join(sd_folder_abs, pv_Subset_Pattern))
                                          if os.path.isfile(os.path.join(sd_folder_abs, source_file))
                                          and (source_file.endswith(".shp") or source_file.endswith(".geojson"))]

            else:
                spatial_data_files_abs = [os.path.join(sd_folder_abs, source_file)
                                          for source_file in os.listdir(sd_folder_abs)
                                          if os.path.isfile(os.path.join(sd_folder_abs, source_file))
                                          and (source_file.endswith(".shp") or source_file.endswith(".geojson"))]

            # Iterate through the desired spatial data files
            for spatial_data_file_absolute in spatial_data_files_abs:

                # Determine the GeoLayerID.
                if pv_GeoLayerID_prefix:
                    geolayer_id = "{}_{}".format(pv_GeoLayerID_prefix,
                                                 io_util.expand_formatter(spatial_data_file_absolute, '%f'))
                else:
                    geolayer_id = io_util.expand_formatter(spatial_data_file_absolute, '%f')

                # Run the secondary checks on the parameter values. Only continue if the checks passed.
                if self.__should_read_geolayer(geolayer_id):

                    # noinspection PyBroadException
                    try:
                        # Create a QGSVectorLayer object with the GeoJSON SpatialDataFile
                        qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_file(spatial_data_file_absolute)

                        # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
                        geolayer_obj = VectorGeoLayer(geolayer_id=geolayer_id,
                                                      geolayer_qgs_vector_layer=qgs_vector_layer,
                                                      geolayer_source_path=spatial_data_file_absolute)
                        self.command_processor.add_geolayer(geolayer_obj)

                    # Raise an exception if an unexpected error occurs during the process
                    except Exception:
                        self.warning_count += 1
                        message = "Unexpected error reading GeoLayer {} from" \
                                  " file {}.".format(geolayer_id, spatial_data_file_absolute)
                        recommendation = "Check the log file for details."
                        self.logger.warning(message, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                        recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
