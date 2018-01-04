# ReadGeoLayersFromFolder

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
import geoprocessor.core.GeoLayerMetadata as GeoLayerMetadata

import geoprocessor.util.command as command_util
import geoprocessor.util.geo as geo_util
import geoprocessor.util.io as io_util
import geoprocessor.util.validators as validators

import os
import logging
import glob


# Inherit from Abstract Command
class ReadGeoLayersFromFolder(AbstractCommand):
    # TODO egiles 2018-01-03 Add Raises section in command documentation

    """
        Reads the GeoLayers within a folder.

        This command reads a the GeoLayers from a folder and creates GeoLayer objects within the
        geoprocessor. The GeoLayers can then be accessed in the geoprocessor by their identifier and further processed.

        GeoLayers are stored on a a computer or are available for download as a spatial data file (GeoJSON, shapefile,
        feature class in a file geodatabase, etc.). Each GeoLayer has one feature type (point, line, polygon, etc.) and
        other data (an identifier, a coordinate reference system, etc). Note that this function only reads GeoLayers
        from within a folder.

        In order for the geoprocessor to use and manipulate spatial data files, GeoLayers are instantiated as
        `QgsVectorLayer <https://qgis.org/api/classQgsVectorLayer.html>`_ objects. This command will read the GeoLayers
        from spatial data files within a folder and instantiate them as geoprocessor GeoLayer objects.

        Args:
            SpatialDataFolder (str, required): the relative pathname to the folder containing spatial data files
            GeoLayerID_prefix (str, optional): the GeoLayer identifier will, by default, use the filename of the
            spatial data file that is being read. However, if a value is set for this parameter, the GeoLayerID will
            take the following format: [GeoLayerID_prefix]_[filename]
            Subset_Pattern (str, optional): the glob-style pattern of the filename to determine which spatial data
            file within the folder are to be processed
        """

    def __init__(self):
        """Initialize the command"""

        super(ReadGeoLayersFromFolder, self).__init__()
        self.command_name = "ReadGeoLayersFromFolder"
        self.command_parameter_metadata = [
            CommandParameterMetadata("SpatialDataFolder", type("")),
            CommandParameterMetadata("GeoLayerID_prefix", type("")),
            CommandParameterMetadata("Subset_Pattern", type("")),
            CommandParameterMetadata("CommandStatus", type(""))
        ]

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            Nothing.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning = ""
        logger = logging.getLogger(__name__)

        # Check that parameter SpatialDataFolder is a non-empty, non-None string.
        pv_SpatialDataFolder = self.get_parameter_value(parameter_name='SpatialDataFolder',
                                                      command_parameters=command_parameters)

        if not validators.validate_string(pv_SpatialDataFolder, False, False):
            message = "SpatialDataFile parameter has no value."
            recommendation = "Specify text for the SpatialDataFile parameter."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def run_command(self):

        # Obtain the SpatialDataFolder parameter value and the Subset_Pattern parameter value
        pv_SpatialDataFolder = self.get_parameter_value("SpatialDataFolder")
        pv_Subset_Pattern = self.get_parameter_value("Subset_Pattern")

        # Convert the SpatialDataFolder parameter value relative path to an absolute path
        spatialDataFolder_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_SpatialDataFolder, self)))

        # Check that the SpatialDataFolder is a folder
        if os.path.isdir(spatialDataFolder_absolute):

            # Determine which files within the folder should be processed. All files will be processed if
            # pv_Subset_Pattern is set to None. Otherwise only files that match the given pattern will be processed.
            if pv_Subset_Pattern:
                spatial_data_files_abs = [os.path.join(spatialDataFolder_absolute, source_file)
                                    for source_file in glob.glob(os.path.join(spatialDataFolder_absolute, pv_Subset_Pattern))
                                    if os.path.isfile(os.path.join(spatialDataFolder_absolute, source_file))
                                    and (source_file.endswith(".shp") or source_file.endswith(".geojson"))]

            else:
                spatial_data_files_abs = [os.path.join(spatialDataFolder_absolute, source_file)
                                    for source_file in os.listdir(spatialDataFolder_absolute)
                                    if os.path.isfile(os.path.join(spatialDataFolder_absolute, source_file))
                                    and (source_file.endswith(".shp") or source_file.endswith(".geojson"))]

            # Iterate through the desired spatial data files
            for spatial_data_file in spatial_data_files_abs:

                # Get the filename without the extension
                filename_wo_ext = (os.path.basename(spatial_data_file)).rsplit('.')[0]

                # Get the GeoLayerID
                pv_GeoLayerID_prefix = self.get_parameter_value("GeoLayerID_prefix")
                if pv_GeoLayerID_prefix:
                    GeoLayerID = "{}_{}".format(pv_GeoLayerID_prefix, filename_wo_ext)
                else:
                    GeoLayerID = filename_wo_ext

                # Throw a warning if the pv_GeoLayerID is not unique
                if geo_util.is_geolist_id(self, GeoLayerID) or geo_util.is_geolayer_id(self, GeoLayerID):

                    # TODO throw a warning
                    pass

                else:
                    # Create a QGSVectorLayer object with the spatial data file
                    QgsVectorLayer = command_util.return_qgsvectorlayer_from_spatial_data_file(spatial_data_file)

                    # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
                    GeoLayer = GeoLayerMetadata.GeoLayerMetadata(geolayer_id=GeoLayerID,
                                                                 geolayer_qgs_object=QgsVectorLayer,
                                                                 geolayer_source_path=spatial_data_file)
                    self.command_processor.GeoLayers.append(GeoLayer)


        # If the SpatialDataFile is not a folder
        else:
            print "The SpatialDataFolder {} is not a valid folder.".format(spatialDataFolder_absolute)
