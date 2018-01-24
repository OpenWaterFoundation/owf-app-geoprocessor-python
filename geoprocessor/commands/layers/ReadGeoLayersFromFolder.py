# ReadGeoLayersFromFolder

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.command as command_util
import geoprocessor.util.io as io_util
import geoprocessor.util.validators as validators
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
    __command_parameter_metadata = [
        CommandParameterMetadata("SpatialDataFolder", type("")),
        CommandParameterMetadata("GeoLayerID_prefix", type("")),
        CommandParameterMetadata("Subset_Pattern", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super(ReadGeoLayersFromFolder, self).__init__()
        self.command_name = "ReadGeoLayersFromFolder"
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
        pv_SpatialDataFolder = self.get_parameter_value(parameter_name='SpatialDataFolder',
                                                        command_parameters=command_parameters)

        if not validators.validate_string(pv_SpatialDataFolder, False, False):
            message = "SpatialDataFolder parameter has no value."
            recommendation = "Specify text for the SpatialDataFolder parameter."
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

    def __should_read_folder(self, spatial_data_folder_abs):

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
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Return the Boolean to determine if the read process should be run. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return run_read

    def __should_read_geolayer(self, geolayer_id):
        """
        Checks the following:
        * the ID of the output GeoLayer is unique (not an existing GeoLayerList ID)
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)

        Args:
            geolayer_id: the ID of the output GeoLayer

        Returns:
            run_read: Boolean. If TRUE, the GeoLayer read process should be run. If FALSE, the read process should
             not be run.
        """

        # Boolean to determine if the read process should be run. Set to true until an error occurs.
        run_read = True

        # If the GeoLayer ID is the same as as already-existing GeoLayerListID, raise a FAILURE.
        if self.command_processor.get_geolayerlist(geolayer_id):

            run_read = False
            self.warning_count += 1
            message = 'The GeoLayerID ({}) value is already in use as a GeoLayerList ID.'.format(geolayer_id)
            recommendation = 'Specify a new GeoLayerID.'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE,
                                                            message, recommendation))

        # If the GeoLayerID is the same as an already-registered GeoLayerID, react according to the
        # pv_IfGeoLayerIDExists value.
        elif self.command_processor.get_geolayer(geolayer_id):

            # Get the IfGeoLayerIDExists parameter value.
            pv_IfGeoLayerIDExists = self.get_parameter_value("IfGeoLayerIDExists", default_value="Replace")

            # Warnings/recommendations if the GeolayerID is the same as a registered GeoLayerID.
            message = 'The GeoLayerID ({}) value is already in use as a GeoLayer ID.'.format(geolayer_id)
            recommendation = 'Specify a new GeoLayerID.'

            # The registered GeoLayer should be replaced with the new GeoLayer (with warnings).
            if pv_IfGeoLayerIDExists.upper() == "REPLACEANDWARN":
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.WARNING,
                                                                message, recommendation))

            # The registered GeoLayer should not be replaced. A warning should be logged.
            if pv_IfGeoLayerIDExists.upper() == "WARN":

                run_read = False
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.WARNING,
                                                                message, recommendation))

            # The matching IDs should cause a FAILURE.
            elif pv_IfGeoLayerIDExists.upper() == "FAIL":

                run_read = False
                self.warning_count += 1
                self.logger.error(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE,
                                                                message, recommendation))

        # Return the Boolean to determine if the read process should be run. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return run_read

    def run_command(self):
        """
        Run the command. Read all spatial data files within the folder. For each desired spatial data file (can be
        specified by the Subset_Pattern parameter), create a GeoLayer object, and add to the GeoProcessor's geolayer
        list.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_SpatialDataFolder = self.get_parameter_value("SpatialDataFolder")
        pv_Subset_Pattern = self.get_parameter_value("Subset_Pattern")
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

                    try:
                        # Create a QGSVectorLayer object with the GeoJSON SpatialDataFile
                        qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_file(spatial_data_file_absolute)

                        # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
                        geolayer_obj = GeoLayer(geolayer_id, qgs_vector_layer, spatial_data_file_absolute)
                        self.command_processor.add_geolayer(geolayer_obj)

                    # Raise an exception if an unexpected error occurs during the process
                    except Exception as e:
                        self.warning_count += 1
                        message = "Unexpected error reading GeoLayer {} from" \
                                  " file {}.".format(geolayer_id, spatial_data_file_absolute)
                        recommendation = "Check the log file for details."
                        self.logger.exception(message, e)
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
