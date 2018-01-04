# ReadGeoLayerFromShapefile

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.command as command_util
import geoprocessor.util.geo as geo_util
import geoprocessor.util.io as io_util
import geoprocessor.util.validators as validators

import os
import logging


# Inherit from Abstract Command
class ReadGeoLayerFromShapefile(AbstractCommand):
    # TODO egiles 2018-01-03 Add Raises section in command documentation

    """
        Reads a GeoLayer from a Shapefile spatial data file.

        This command reads a GeoLayer from a Shapefile file and creates a GeoLayer object within the
        geoprocessor. The GeoLayer can then be accessed in the geoprocessor by its identifier and further processed.

        GeoLayers are stored on a computer or are available for download as a spatial data file (GeoJSON, shapefile,
        feature class in a file geodatabase, etc.). Each GeoLayer has one feature type (point, line, polygon, etc.) and
        other data (an identifier, a coordinate reference system, etc). Note that this function only reads a single
        GeoLayer from a single file in Shapefile format.

        In order for the geoprocessor to use and manipulate spatial data files, GeoLayers are instantiated as
        `QgsVectorLayer <https://qgis.org/api/classQgsVectorLayer.html>`_ objects. This command will read the GeoLayer
        from a Shapefile spatial data file and instantiate the data as a geoprocessor GeoLayer object.

        Args:
            SpatialDataFile (str, required): the relative pathname to the spatial data file (Shapefile format)
            GeoLayerID (str, optional): the GeoLayer identifier. If None, the spatial data filename (without the
            .shp extension) will be used as the GeoLayer identifier. For example: If GeoLayerID is None and the
            absolute pathname to the spatial data file is C:/Desktop/Example/example_file.shp, then the GeoLayerID
            will be `example_file`.
        """

    def __init__(self):
        """Initialize the command"""

        super(ReadGeoLayerFromShapefile, self).__init__()
        self.command_name = "ReadGeoLayerFromShapefile"
        self.command_parameter_metadata = [
            CommandParameterMetadata("SpatialDataFile", type("")),
            CommandParameterMetadata("GeoLayerID", type("")),
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

        # Check that parameter SpatialDataFile is a non-empty, non-None string.
        pv_SpatialDataFile = self.get_parameter_value(parameter_name='SpatialDataFile',
                                                      command_parameters=command_parameters)

        if not validators.validate_string(pv_SpatialDataFile, False, False):
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

        # Obtain the SpatialDataFile parameter value
        pv_SpatialDataFile = self.get_parameter_value("SpatialDataFile")

        # Convert the SpatialDataFile parameter value relative path to an absolute path
        spatialDataFile_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_SpatialDataFile, self)))

        # Check that the SpatialDataFile is a valid file and is in Shapefile format
        if os.path.isfile(spatialDataFile_absolute) and spatialDataFile_absolute.endswith(".shp"):

            # Obtain the GeoLayerID parameter value
            pv_GeoLayerID = self.get_parameter_value("GeoLayerID")

            # If the pv_GeoLayerID is set to None, assign the filename (without the extension) as the GeoLayerID
            if not pv_GeoLayerID:
                pv_GeoLayerID = (os.path.basename(spatialDataFile_absolute)).replace(".shp", "")

            # Throw a warning if the pv_GeoLayerID is not unique
            if geo_util.is_geolist_id(self, pv_GeoLayerID) or geo_util.is_geolayer_id(self, pv_GeoLayerID):

                # TODO egiles 2018-01-04 Need to throw a warning
                pass

            # If the GeoLayerID is unique, create the QGSVectorLayer object and the GeoLayer object. Append the
            # GeoLayer object to the geoprocessor's GeoLayers list.
            else:

                # Create a QGSVectorLayer object with the Shapefile SpatialDataFile
                QgsVectorLayer = command_util.return_qgsvectorlayer_from_spatial_data_file(spatialDataFile_absolute)

                # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
                GeoLayer_obj = GeoLayer(geolayer_id=pv_GeoLayerID,
                                        geolayer_qgs_object=QgsVectorLayer,
                                        geolayer_source_path=spatialDataFile_absolute)
                self.command_processor.GeoLayers.append(GeoLayer_obj)


        # If the SpatialDataFile is not a Shapefile file, print an error message.
        else:
            # TODO egiles 2018-01-04 Need to throw a warning
            print "The SpatialDataFile {} is not a valid Shapefile.".format(spatialDataFile_absolute)
