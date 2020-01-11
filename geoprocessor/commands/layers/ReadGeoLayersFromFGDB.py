# ReadGeoLayersFromFGDB - command to read GeoLayers from a file geodatabase
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
from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validators
import geoprocessor.util.qgis_util as qgis_util

import os
import logging
import re
import ogr


class ReadGeoLayersFromFGDB(AbstractCommand):

    """
    Reads the GeoLayers (feature classes) within a file geodatabase (FGDB).

    This command reads the GeoLayers from a file geodatabase and creates GeoLayer objects within the
    geoprocessor. The GeoLayers can then be accessed in the geoprocessor by their identifier and further processed.

    GeoLayers are stored on a computer or are available for download as a spatial data file (GeoJSON, shapefile,
    feature class in a file geodatabase, etc.). Each GeoLayer has one feature type (point, line, polygon, etc.) and
    other data (an identifier, a coordinate reference system, etc). Note that this function only reads one or many
    GeoLayers (feature classes) from within a single file geodatabase.

    In order for the geoprocessor to use and manipulate spatial data files, GeoLayers are instantiated as
    `QgsVectorLayer <https://qgis.org/api/classQgsVectorLayer.html>`_ objects. This command will read the GeoLayers
    from the feature classes within a file geodatabase and instantiate them as geoprocessor GeoLayer objects.

    Command Parameters
    * SpatialDataFolder (str, required): the relative pathname to the file geodatabase containing spatial data files
        (feature classes)
    * ReadOnlyOneFeatureClass (str, required): a string that can be converted to a valid boolean value. If TRUE, only
         one specific feature class is read in as a GeoLayer. If FALSE, multiple feature classes are read in as
         different GeoLayers.
    * FeatureClass (str, required if ReadOnlyOneFeatureClass is TRUE): the name of the feature class within the
        geodatabase to read.
    * GeoLayerID (str, required if ReadOnlyOneFeatureClass is TRUE): the GeoLayer identifier.
    * GeoLayerID_prefix (str, optional, only used if ReadOnlyOneFeatureClass is FALSE): the GeoLayer identifier will,
        by default, use the name of the feature class that is being read. However, if a value is set for this parameter,
         the GeoLayerID will follow this format: [GeoLayerID_prefix]_[name_of_feature_class].
    * Subset_Pattern (str, optional, only used if ReadOnlyOneFeatureClass is FALSE): the glob-style pattern of the
        feature class name to determine which feature classes within the file geodatabase are to be processed. More
        information on creating a glob pattern can be found at https://docs.python.org/2/library/glob.html.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the GeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`. Used if
        ReadOnlyOneFeatureClass is TRUE or FALSE.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("SpatialDataFolder", type("")),
        CommandParameterMetadata("ReadOnlyOneFeatureClass", type("")),
        CommandParameterMetadata("FeatureClass", type("")),
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("GeoLayerID_prefix", type("")),
        CommandParameterMetadata("Subset_Pattern", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "ReadGeoLayersFromFGDB"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = "Read one or more GeoLayerss from an Esri File Geodatabase."
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # SpatialDataFolder
        self.parameter_input_metadata['SpatialDataFolder.Description'] = "file geodatabase to read"
        self.parameter_input_metadata['SpatialDataFolder.Label'] = "Spatial data folder"
        self.parameter_input_metadata['SpatialDataFolder.Required'] = True
        self.parameter_input_metadata['SpatialDataFolder.Tooltip'] = "The file geodatbase to read (must end in .gdb)."
        self.parameter_input_metadata['SpatialDataFolder.FileSelector.Type'] = "Read"
        self.parameter_input_metadata['SpatialDataFolder.FileSelector.Title'] = "Select the file geodatabase to read."
        # ReadOnlyOneFeatureClass
        self.parameter_input_metadata['ReadOnlyOneFeatureClass.Description'] = "whether to read one feature class"
        self.parameter_input_metadata['ReadOnlyOneFeatureClass.Label'] = "Read only one feature class?"
        self.parameter_input_metadata['ReadOnlyOneFeatureClass.Required'] = True
        self.parameter_input_metadata['ReadOnlyOneFeatureClass.Tooltip'] = (
            "If TRUE, only one feature class will be read as a GeoLayer. Must specify a valid feature class name. \n"
            "If FALSE, one or more feature classes will be read as GeoLayers. "
            "Can specify the Subset_Pattern to select which feature classes to read.")
        self.parameter_input_metadata['ReadOnlyOneFeatureClass.Values'] = ["", "TRUE", "FALSE"]
        # IfGeoLayerIDExists
        self.parameter_input_metadata['IfGeoLayerIDExists.Description'] = "action if output exists"
        self.parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID exists"
        self.parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = (
            "The action that occurs if the GeoLayerID already exists within the GeoProcessor.\n"
            "Replace : The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer.  "
            "No warning is logged.\n"
            "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new "
            "GeoLayer. A warning is logged.\n"
            "Warn : The new GeoLayer is not created. A warning is logged.\n"
            "Fail : The new GeoLayer is not created. A fail message is logged.")
        self.parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
        self.parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"
        # FeatureClass
        self.parameter_input_metadata['FeatureClass.Description'] = "name of feature class to read"
        self.parameter_input_metadata['FeatureClass.Label'] = "Feature class"
        self.parameter_input_metadata['FeatureClass.Required'] = True
        self.parameter_input_metadata['FeatureClass.Tooltip'] =\
            "The name of the feature class within the file geodatabase to read. ${Property} syntax is recognized."
        # GeoLayerID
        self.parameter_input_metadata['GeoLayerID.Description'] = "output GeoLayer identifier"
        self.parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
        self.parameter_input_metadata['GeoLayerID.Required'] = True
        self.parameter_input_metadata['GeoLayerID.Tooltip'] = \
            "A GeoLayer identifier. Formatting characters and ${Property} syntax are recognized."
        # GeoLayerID_prefix
        self.parameter_input_metadata['GeoLayerID_prefix.Description'] = "a GeoLayer identifier prefix"
        self.parameter_input_metadata['GeoLayerID_prefix.Label'] = "GeoLayerID prefix"
        self.parameter_input_metadata['GeoLayerID_prefix.Tooltip'] =\
            "GeoLayers read from a file geodatabase have an identifier in the GeoLayerID_prefix_FeatureClass format."
        self.parameter_input_metadata['GeoLayerID_prefix.Value.Default'] =\
            "No prefix is used. The GeoLayerID is the name of the feature class."
        # Subset_Pattern
        self.parameter_input_metadata['Subset_Pattern.Description'] = "globstyle pattern of feature classes to read"
        self.parameter_input_metadata['Subset_Pattern.Label'] = "Subset pattern"
        self.parameter_input_metadata['Subset_Pattern.Tooltip'] =\
            "The glob-style pattern (e.g., CO_* or *_[MC]O) of feature classes to read from the file geodatabase."
        self.parameter_input_metadata['Subset_Pattern.Value.Default'] =\
            "No pattern is used. All feature classes within the file geodatabase are read."

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

        # Check that parameter SpatialDataFolder is a non-empty, non-None string.
        # - existence of the folder will also be checked in run_command().
        pv_SpatialDataFolder = self.get_parameter_value(parameter_name='SpatialDataFolder',
                                                        command_parameters=command_parameters)

        if not validators.validate_string(pv_SpatialDataFolder, False, False):
            message = "SpatialDataFolder parameter has no value."
            recommendation = "Specify text for the SpatialDataFolder parameter to indicate the file geodatabase."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

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

        # Check that the optional parameter ReadOnlyOneFeatureClass is a valid Boolean.
        pv_ReadOnlyOneFeatureClass = self.get_parameter_value(parameter_name="ReadOnlyOneFeatureClass",
                                                              command_parameters=command_parameters)
        if not validators.validate_bool(pv_ReadOnlyOneFeatureClass, True, False):
            message = "ReadOnlyOneFeatureClass is not a valid boolean value."
            recommendation = "Specify a valid boolean value for the ReadOnlyOneFeatureClass parameter."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Continue with checks if the ReadOnlyOneFeatureClass is a valid TRUE Boolean.
        elif string_util.str_to_bool(pv_ReadOnlyOneFeatureClass):

            # Check that parameter GeoLayerID is a non-empty, non-None string.
            pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID', command_parameters=command_parameters)

            if not validators.validate_string(pv_GeoLayerID, False, False):
                message = "GeoLayerID parameter has no value."
                recommendation = "Specify the GeoLayerID parameter."
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

    def __return_a_list_of_fc(self, fgdb_full_path):

        # The file geodatabase will be read and each feature class will be added to the feature_class_list.
        feature_class_list = []

        # Append each feature class in the Esri File Geodatabase to the feature_class_list.
        # REF: https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html|
        # "Get all layers in an Esri File GeoDataBase"
        ogr.UseExceptions()
        driver = ogr.GetDriverByName("OpenFileGDB")
        gdb = driver.Open(fgdb_full_path)
        for feature_class_idx in range(gdb.GetLayerCount()):
            feature_class = gdb.GetLayerByIndex(feature_class_idx)
            feature_class_list.append(feature_class.GetName())

        return feature_class_list

    def __should_read_gdb(self, spatial_data_folder_abs):

        """
        Checks the following:
        * the SpatialDataFolder (absolute) is a valid folder
        * the SpatialDataFolder (absolute) is a valid File GeoDatabase

        Args:
            spatial_data_folder_abs (str): the full pathname to the input spatial data folder

        Returns:
             Boolean. If TRUE, the GeoDatabase should be read. If FALSE, at least one check failed and the GeoDatabase
             should not be read.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the input spatial data folder is not a valid file path, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsFolderPathValid", "SpatialDataFolder",
                                                       spatial_data_folder_abs, "FAIL"))

        # If the input spatial data folder is valid, continue with the checks.
        if False not in should_run_command:

            # If the input spatial data folder is not a file geodatabase, raise a FAILURE.
            should_run_command.append(validators.run_check(self, "IsFolderAfGDB", "SpatialDataFolder",
                                                           spatial_data_folder_abs, "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def __should_read_geolayer(self, geolayer_id, one_geolayer_bool, fc_name=None, spatial_data_folder_abs=None):
        """
        Checks the following:
        * if only one geolayer is being read, the FeatureClass is an existing feature class within the File GeoDatabase
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)

        Args:
            geolayer_id (str): the ID of the output GeoLayer
            one_geolayer_bool (bool): if True, the command is only reading one FC from the FGDB
            fc_name (str): the name of the FC being read.  Only used if one_geolayer_bool is True. Default = None
            spatial_data_folder_abs (str): the full pathname to the input spatial data folder.
                Only used if one_geolayer_bool is True. Default = None

        Returns:
            Boolean. If TRUE, the GeoLayer should be read. If FALSE, at least one check failed and the GeoLayer
                should not be read.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the GeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE (depends
        # on the value of the IfGeoLayerIDExists parameter.)
        should_run_command.append(validators.run_check(self, "IsGeoLayerIdUnique", "GeoLayerID", geolayer_id, None))

        # If only one geolayer is being read from the file geodatabase, continue.
        if one_geolayer_bool:

            # If the provided feature class is not in the FGDB raise a FAILURE.
            should_run_command.append(validators.run_check(self, "IsFeatureClassInFGDB", "FeatureClass", fc_name,
                                                           "FAIL", other_values=[spatial_data_folder_abs]))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self):
        """
        Run the command. Read the feature classes within a file geodatabase. For each desired feature class (can be
        specified by the Subset_Pattern parameter), create a GeoLayer object, and add to the GeoProcessor's geolayer
        list.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the required and optional parameter values
        pv_SpatialDataFolder = self.get_parameter_value("SpatialDataFolder")
        pv_ReadOnlyOneFeatureClass = self.get_parameter_value("ReadOnlyOneFeatureClass")
        pv_Subset_Pattern = self.get_parameter_value("Subset_Pattern")
        pv_GeoLayerID_prefix = self.get_parameter_value("GeoLayerID_prefix")
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_FeatureClass = self.get_parameter_value("FeatureClass")

        # Convert the ReadOnlyOneFeatureClass from a string value to a Boolean value.
        pv_ReadOnlyOneFeatureClass = string_util.str_to_bool(pv_ReadOnlyOneFeatureClass)

        # Convert the SpatialDataFolder parameter value relative path to an absolute path
        sd_folder_abs = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_SpatialDataFolder, self)))

        # Run the initial checks on the parameter values. Only continue if the checks passed.
        if self.__should_read_gdb(sd_folder_abs):

            # If configured to only read one Feature Class into one GeoLayer.
            if pv_ReadOnlyOneFeatureClass:

                # Run the check to see if the GeoLayer should be read.
                if self.__should_read_geolayer(pv_GeoLayerID, True, pv_FeatureClass, sd_folder_abs):

                    try:

                        # Get the full pathname to the feature class
                        # TODO egiles 2018-01-04 Need to research how to properly document feature class source path
                        spatial_data_file_absolute = os.path.join(sd_folder_abs, str(pv_FeatureClass))

                        # Create a QgsVectorLayer object from the feature class.
                        qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_feature_class(sd_folder_abs,
                                                                                            pv_FeatureClass)

                        # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
                        geolayer_obj = GeoLayer(pv_GeoLayerID, qgs_vector_layer, spatial_data_file_absolute)
                        self.command_processor.add_geolayer(geolayer_obj)

                    # Raise an exception if an unexpected error occurs during the process
                    except Exception as e:

                        self.warning_count += 1
                        message = "Unexpected error reading feature class ({}) from file geodatabase ({}).".format(
                            pv_FeatureClass, sd_folder_abs)
                        recommendation = "Check the log file for details."
                        self.logger.warning(message, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                        recommendation))

            # If configured to read multiple Feature Classes into multiple GeoLayers.
            else:

                # Get a list of all of the feature classes in the file geodatabase.
                fc_list = self.__return_a_list_of_fc(sd_folder_abs)

                # Filter the fc_list to only include feature classes that meet the Subset Pattern configuration. If
                # the Subset Pattern configuration is None, all feature classes will remain in the fc_list.
                fc_list = string_util.filter_list_of_strings(fc_list, [pv_Subset_Pattern])

                # Iterate over the feature classes in the fc_list.
                for feature_class in fc_list:

                    # Determine the GeoLayerID.
                    if pv_GeoLayerID_prefix:
                        geolayer_id = "{}_{}".format(pv_GeoLayerID_prefix, feature_class)
                    else:
                        geolayer_id = feature_class

                    # Run the secondary checks on the parameter values. Only continue if the checks passed.
                    if self.__should_read_geolayer(geolayer_id, False):

                        try:

                            # Get the full pathname to the feature class
                            # TODO egiles 2018-01-04 Need to research how to properly document feature class source path
                            spatial_data_file_absolute = os.path.join(sd_folder_abs, str(feature_class))

                            # Create a QgsVectorLayer object from the feature class.
                            qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_feature_class(sd_folder_abs,
                                                                                                feature_class)

                            # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
                            geolayer_obj = GeoLayer(geolayer_id, qgs_vector_layer, spatial_data_file_absolute)
                            self.command_processor.add_geolayer(geolayer_obj)

                        # Raise an exception if an unexpected error occurs during the process
                        except Exception as e:

                            self.warning_count += 1
                            message = "Unexpected error reading feature class ({}) from file geodatabase ({}).".format(
                                feature_class, sd_folder_abs)
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
