# ReadGeoLayerFromGeoJSON

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.command as command_util
import geoprocessor.util.geo as geo_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.io as io_util
import geoprocessor.util.validators as validators

import os
import logging


class ReadGeoLayerFromGeoJSON(AbstractCommand):

    """
    Reads a GeoLayer from a GeoJSON spatial data file.

    This command reads a layer from a GeoJSON file and creates a GeoLayer object within the geoprocessor. The
    GeoLayer can then be accessed in the geoprocessor by its identifier and further processed.

    GeoLayers are stored on a computer or are available for download as a spatial data file (GeoJSON, shapefile,
    feature class in a file geodatabase, etc.). Each GeoLayer has one feature type (point, line, polygon, etc.) and
    other data (an identifier, a coordinate reference system, etc). This function reads a single GeoLayer from a single
    GeoJSON file in GeoJSON format (consistent with the fact that GeoJSON files store one layer).

    In order for the geoprocessor to use and manipulate spatial data files, GeoLayers are instantiated as
    `QgsVectorLayer <https://qgis.org/api/classQgsVectorLayer.html>`_ objects.
    """

    # Command Parameters
    # SpatialDataFile (str, required): the relative pathname to the spatial data file (GeoJSON format)
    # GeoLayerID (str, optional): the GeoLayer identifier. If None, the spatial data filename (without the
    #   .geojson extension) will be used as the GeoLayer identifier. For example: If GeoLayerID is None and the
    #   absolute pathname to the spatial data file is C:/Desktop/Example/example_file.geojson, then the GeoLayerID
    #   will be `example_file`.
    __command_parameter_metadata = [
        CommandParameterMetadata("SpatialDataFile", type("")),
        CommandParameterMetadata("GeoLayerID", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        super(ReadGeoLayerFromGeoJSON, self).__init__()
        self.command_name = "ReadGeoLayerFromGeoJSON"
        self.command_parameter_metadata = self.__command_parameter_metadata

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
        # - existence of the file will also be checked in run_command().
        pv_SpatialDataFile = self.get_parameter_value(parameter_name='SpatialDataFile',
                                                      command_parameters=command_parameters)

        if not validators.validate_string(pv_SpatialDataFile, False, False):

            message = "SpatialDataFile parameter has no value."
            recommendation = "Specify the SpatialDataFile parameter to indicate the spatial data layer file."
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
        """
        Run the command. Read the layer file from a GeoJSON file, create a GeoLayer object, and add to the
        GeoProcessor's geolayer list.

        Args:
            None.

        Returns:
            Nothing.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Set up logger and warning count
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Obtain the SpatialDataFile parameter value
        pv_SpatialDataFile = self.get_parameter_value("SpatialDataFile")

        # Convert the SpatialDataFile parameter value relative path to an absolute path and expand for ${Property}
        # syntax
        spatial_data_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_SpatialDataFile, self)))

        # Check that the SpatialDataFile is a valid file
        if os.path.isfile(spatial_data_file_absolute):

            # Throw a warning if the SpatialDataFile does not end in .geojson
            if not spatial_data_file_absolute.upper().endswith(".GEOJSON"):
                warning_count += 1
                message = 'The SpatialDataFile does not end with the .geojson extension.'
                logger.warning(message)

            # Obtain the GeoLayerID parameter value. By default, the GeoLayerID is the filename without the extension
            # (%f formatter).
            pv_GeoLayerID = self.get_parameter_value("GeoLayerID", default_value='%f')

            # If the pv_GeoLayerID is a valid %-formatter, assign the pv_GeoLayerID the corresponding value.
            if pv_GeoLayerID in ['%f', '%F', '%E']:

                pv_GeoLayerID = geo_util.expand_formatter(spatial_data_file_absolute, pv_GeoLayerID)

            # Mark as an error if the pv_GeoLayerID is the same as a registered GeoLayerList ID
            if geo_util.is_geolist_id(self, pv_GeoLayerID):

                warning_count += 1
                message = 'The GeoLayer ID ({}) value is already in use as a GeoLayerList ID.'.format(pv_GeoLayerID)
                recommendation = 'Specifiy a new GeoLayerID.'
                logger.error(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE,
                                                                message, recommendation))

            else:

                # Mark as a warning if the pv_GeoLayerID is the same as a registered GeoLayer ID. The registered
                # GeoLayer will be overwritten with this new GeoLayer.
                if geo_util.is_geolayer_id(self, pv_GeoLayerID):

                    warning_count += 1
                    message = 'The GeoList ID ({}) value is already in use as a GeoLayer ID. GeoLayer ID ({}) is ' \
                              'being overwritten.'.format(pv_GeoLayerID, pv_GeoLayerID)
                    recommendation = 'Specifiy a new GeoLayerID.'
                    logger.warning(message)
                    self.command_status.add_to_log(command_phase_type.RUN,
                                                   CommandLogRecord(command_status_type.WARNING,
                                                                    message, recommendation))

                # Create the QGSVectorLayer object and the GeoLayer object. Append the GeoLayer object to the
                # geoprocessor's geolayers list.
                try:

                    # Create a QGSVectorLayer object with the GeoJSON SpatialDataFile
                    qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_spatial_data_file(spatial_data_file_absolute)

                    # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
                    geolayer_obj = GeoLayer(geolayer_id=pv_GeoLayerID,
                                            geolayer_qgs_vector_layer=qgs_vector_layer,
                                            geolayer_source_path=spatial_data_file_absolute)

                    # TODO egiles 2018-01-09 Need to figure out how to use the add_geolayer function to add the
                    # TODO GeoLayer object to the GeoProcessor's geolayers list
                    self.command_processor.geolayers.append(geolayer_obj)

                # Raise an exception if an unexpected error occurs during the process
                except Exception as e:
                    warning_count += 1
                    message = "Unexpected error reading GeoLayer {} from GeoJSON file {}.".format(pv_GeoLayerID,
                                                                                                  pv_SpatialDataFile)
                    recommendation = "Check the log file for details."
                    logger.exception(message, e)
                    self.command_status.add_to_log(command_phase_type.RUN,
                                                   CommandLogRecord(command_status_type.FAILURE, message,
                                                                    recommendation))

        # If the SpatialDataFile is not a file, log an error message.
        else:
            warning_count += 1
            message = "The SpatialDataFile ({}) is not a valid file.".format(pv_SpatialDataFile)
            recommendation = "Specify a valid file."
            logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
