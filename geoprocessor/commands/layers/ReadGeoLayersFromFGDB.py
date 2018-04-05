# ReadGeoLayersFromFGDB

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
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
    * GeoLayerID_prefix (str, optional): the GeoLayer identifier will, by default, use the name of the feature class
        that is being read. However, if a value is set for this parameter, the GeoLayerID will follow this format:
        [GeoLayerID_prefix]_[name_of_feature_class]
    * Subset_Pattern (str, optional): the glob-style pattern of the feature class name to determine which feature
        classes within the file geodatabase are to be processed. More information on creating a glob pattern can be
        found at `this site <https://docs.python.org/2/library/glob.html>`_.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the CopiedGeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("SpatialDataFolder", type("")),
        CommandParameterMetadata("GeoLayerID_prefix", type("")),
        CommandParameterMetadata("Subset_Pattern", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command
        """

        # AbstractCommand data
        super(ReadGeoLayersFromFGDB, self).__init__()
        self.command_name = "ReadGeoLayersFromFGDB"
        self.command_parameter_metadata = self.__command_parameter_metadata

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
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

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
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)

        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def __should_read_gdb(self, spatial_data_folder_abs):

        """
        Checks the following:
        * the SpatialDataFolder (absolute) is a valid folder
        * the SpatialDataFolder (absolute) is a valid File GeoDatabase

        Args:
            spatial_data_folder_abs: the full pathname to the input spatial data folder
            geolayer_id: the ID of the output GeoLayer
            fc_name: the name of the feature class to read

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

    def __should_read_geolayer(self, geolayer_id):
        """
        Checks the following:
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)

        Args:
            geolayer_id: the ID of the output GeoLayer

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

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self):
        """
        Run the command. Read the feature classes within a file geodatabse. For each desired feature class (can be
        specified by the Subset_Pattern parameter), create a GeoLayer object, and add to the GeoProcessor's geolayer
        list.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the required and optional parameter values
        pv_SpatialDataFolder = self.get_parameter_value("SpatialDataFolder")
        pv_Subset_Pattern = self.get_parameter_value("Subset_Pattern")
        pv_GeoLayerID_prefix = self.get_parameter_value("GeoLayerID_prefix")

        # Convert the SpatialDataFolder parameter value relative path to an absolute path
        sd_folder_abs = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_SpatialDataFolder, self)))

        # Run the initial checks on the parameter values. Only continue if the checks passed.
        if self.__should_read_gdb(sd_folder_abs):

            # The file geodatabase will be read and each feature class will be added to the feature_class_list.
            feature_class_list = []

            # Append each feature class in the Esri File Geodatabase to the feature_class_list.
            # REF: https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html|
            # "Get all layers in an Esri File GeoDataBase"
            ogr.UseExceptions()
            driver = ogr.GetDriverByName("OpenFileGDB")
            gdb = driver.Open(sd_folder_abs)
            for feature_class_idx in range(gdb.GetLayerCount()):
                feature_class = gdb.GetLayerByIndex(feature_class_idx)
                feature_class_list.append(feature_class.GetName())

            # If a file_pattern has been included, update the feature_class_list to only include the desired files. If
            # no file pattern has been included, all feature classes within the file geodatabase will read as GeoLayers
            if pv_Subset_Pattern:
                glob_filter = (fc for fc in feature_class_list if
                               re.match(string_util.glob2re(pv_Subset_Pattern), fc))
                updated_feature_class_list = list(glob_filter)
                feature_class_list = updated_feature_class_list

            # Iterate through each desired feature class inside the file geodatabase.
            for feature_class in feature_class_list:

                # Determine the GeoLayerID.
                if pv_GeoLayerID_prefix:
                    geolayer_id = "{}_{}".format(pv_GeoLayerID_prefix, feature_class)
                else:
                    geolayer_id = feature_class

                # Run the secondary checks on the parameter values. Only continue if the checks passed.
                if self.__should_read_geolayer(geolayer_id):

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
                        self.logger.error(message, exc_info=True)
                        self.command_status.add_to_log(command_phase_type.RUN,
                                                       CommandLogRecord(command_status_type.FAILURE, message,
                                                                        recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
