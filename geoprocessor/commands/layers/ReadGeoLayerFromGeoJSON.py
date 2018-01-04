# ReadGeoLayerFromGeoJSON

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
class ReadGeoLayerFromGeoJSON(AbstractCommand):

    """
        Reads a GeoLayer from a GeoJSON spatial data file.

        This command reads a GeoLayer from a GeoJSON file and creates a GeoLayer object within the
        geoprocessor. The GeoLayer can then be accessed in the geoprocessor by its identifier and further processed.

        GeoLayers are stored on a computer or are available for download as a spatial data file (GeoJSON, shapefile,
        feature class in a file geodatabase, etc.). Each GeoLayer has one feature type (point, line, polygon, etc.) and
        other data (an identifier, a coordinate reference system, etc). Note that this function only reads a single
        GeoLayer from a single file in GeoJSON format.

        In order for the geoprocessor to use and manipulate spatial data files, GeoLayers are instantiated as
        `QgsVectorLayer <https://qgis.org/api/classQgsVectorLayer.html>`_ objects. This command will read the GeoLayer
        from a GeoJSON spatial data file and instantiate the data as a geoprocessor GeoLayer object.

        Args:
            SpatialDataFile (str, required): the relative pathname to the spatial data file (GeoJSON format)
            GeoLayerID (str, optional): the GeoLayer identifier. If None, the spatial data filename (without the
            .geojson extension) will be used as the GeoLayer identifier. For example: If GeoLayerID is None and the
            absolute pathname to the spatial data file is C:/Desktop/Example/example_file.geojson, then the GeoLayerID
            will be `example_file`.

        Returns:
            Nothing

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
            RuntimeError if any errors occurred during run_command method. Warnings within the run_command method do
            not throw a RuntimeError but instead print a warning to the log.
        """

    def __init__(self):
        """Initialize the command"""

        super(ReadGeoLayerFromGeoJSON, self).__init__()
        self.command_name = "ReadGeoLayerFromGeoJSON"
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

        # Set up logger and warning/error count
        warning_count = 0
        error_count = 0
        logger = logging.getLogger(__name__)

        # Obtain the SpatialDataFile parameter value
        pv_SpatialDataFile = self.get_parameter_value("SpatialDataFile")

        # Convert the SpatialDataFile parameter value relative path to an absolute path
        spatialDataFile_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_SpatialDataFile, self)))

        # Check that the SpatialDataFile is a valid file and is in GeoJSON format
        if os.path.isfile(spatialDataFile_absolute) and spatialDataFile_absolute.endswith(".geojson"):

            # Obtain the GeoLayerID parameter value
            pv_GeoLayerID = self.get_parameter_value("GeoLayerID")

            # If the pv_GeoLayerID is set to None, assign the filename (without the extension) as the GeoLayerID
            if not pv_GeoLayerID:
                pv_GeoLayerID = (os.path.basename(spatialDataFile_absolute)).replace(".geojson", "")

            # Mark as an error if the pv_GeoLayerID is the same as a registered GeoLayerList ID
            if geo_util.is_geolist_id(self, pv_GeoLayerID):

                error_count += 1
                message = 'The GeoLayer ID ({}) is already a registered GeoLayerList ID.'.format(pv_GeoLayerID)
                logger.error(message)

            else:

                # Mark as a warning if the pv_GeoLayerID is the same as a registered GeoLayer ID. The registered
                # GeoLayer will be overwritten with this new GeoLayer.
                if geo_util.is_geolayer_id(self, pv_GeoLayerID):

                    warning_count += 1
                    message = 'The GeoList ID ({}) is already registered. GeoLayer ID ({}) is being overwritten.'\
                        .format(pv_GeoLayerID, pv_GeoLayerID)
                    logger.warning(message)

                # Create the QGSVectorLayer object and the GeoLayer object. Append the
                # GeoLayer object to the geoprocessor's GeoLayers list.
                try:

                    # Create a QGSVectorLayer object with the GeoJSON SpatialDataFile
                    QgsVectorLayer = command_util.return_qgsvectorlayer_from_spatial_data_file(spatialDataFile_absolute)

                    # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
                    GeoLayer_obj = GeoLayer(geolayer_id=pv_GeoLayerID,
                                            geolayer_qgs_object=QgsVectorLayer,
                                            geolayer_source_path=spatialDataFile_absolute)
                    self.command_processor.GeoLayers.append(GeoLayer_obj)

                # Raise an exception if an unexpected error occurs during the process
                except Exception as e:
                    error_count += 1
                    message = "Unexpected error creating GeoLayer {}.".format(pv_GeoLayerID)
                    logger.exception(message, e)
                    self.command_status.add_to_log(command_phase_type.RUN,
                                                   CommandLogRecord(command_status_type.FAILURE, message,
                                                                    "Check the log file for details."))

        # If the SpatialDataFile is not a GeoJSON file, log an error message.
        else:
            error_count += 1
            message = 'The SpatialDataFile ({}) is not a valid GeoJSON file.'.format(pv_SpatialDataFile)
            logger.error(message)

        # Determine success of command processing
        # Raise Runtime Error if any errors occurred
        if error_count > 0:
            message = "There were {} errors and {} warnings proceeding this command.".format(error_count, warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors. Print warning message to log if any warnings
        # occurred.
        else:
            if warning_count > 0:
                message = "There were 0 errors and {} warnings proceeding this command.".format(warning_count)
                logger.warning(message)
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
