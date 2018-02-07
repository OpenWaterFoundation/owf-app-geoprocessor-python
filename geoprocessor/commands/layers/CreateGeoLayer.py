# CreateGeoLayer

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validators

import logging


class CreateGeoLayer(AbstractCommand):

    """
    Removes a GeoLayer from the GeoProcessor.

    Command Parameters
    * GeoLayerID (str, required): The ID of the existing GeoLayer to copy.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("GeometryType", type(str),
        CommandParameterMetadata("XYPoints", type([])))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super(CreateGeoLayer, self).__init__()
        self.command_name = "CreateGeoLayer"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """

        pass

    def __should_geolayer_be_created(self, geolayer_id):
        """
        Checks the following:
        * the ID of the input GeoLayer is an existing GeoLayer ID

        Args:
            geolayer_id: the id of the GeoLayer to be removed

        Returns:
            remove_geolayer: Boolean. If TRUE, the GeoLayer should be removed. If FALSE, one or more checks have failed
             and the GeoLayer should not be removed.
        """

        pass

    def run_command(self):
        """
        Run the command. Remove the GeoLayer object from the GeoProcessor. Delete the GeoLayer instance.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_GeometryType = self.get_parameter_value("GeometryType")
        pv_XYPoints = self.get_parameter_value("XYPoints")

        points = []

        xy_point_list = string_util.delimited_string_to_list(pv_XYPoints, delimiter=';')
        for point in xy_point_list:
            coordinate_list = string_util.delimited_string_to_list(point, delimiter=',')
            point_x_coord = float(coordinate_list[0])
            point_y_coord = float(coordinate_list[1])

            points.append(qgis_util.get_qgspoint_obj(point_x_coord, point_y_coord))

        layer = qgis_util.create_qgsvectorlayer("Polygon", "EPSG:4326", "new_layer")
        qgis_util.add_polygon_feature_to_qgsvectorlayer_from_points(layer, points)
        new_geolayer = GeoLayer(pv_GeoLayerID, layer, "MEMORY")
        self.command_processor.add_geolayer(new_geolayer)

        # # Run the checks on the parameter values. Only continue if the checks passed.
        # if self.__should_geolayer_be_deleted(pv_GeoLayerID):
        #
        #     try:
        #
        #         points = []
        #
        #         xy_point_list = string_util.delimited_string_to_list(pv_XYPoints, delimiter=';')
        #         for point in xy_point_list:
        #
        #             coordinate_list = string_util.delimited_string_to_list(point, delimiter=',')
        #             point_x_coord = float(coordinate_list[0])
        #             point_y_coord = float(coordinate_list[1])
        #
        #             points.append(qgis_util.get_qgspoint_obj(point_x_coord, point_y_coord))
        #
        #         layer = qgis_util.create_qgsvectorlayer("Polygon", "EPSG:4326", "new_layer")
        #         qgis_util.add_polygon_feature_to_qgsvectorlayer_from_points(layer, points)
        #         new_geolayer = GeoLayer(pv_GeoLayerID, layer, "MEMORY")
        #         self.command_processor.add_geolayer(new_geolayer)
        #
        #     # Raise an exception if an unexpected error occurs during the process.
        #     except Exception as e:
        #
        #         self.warning_count += 1
        #         message = "Unexpected error removing GeoLayer ({}).".format(pv_GeoLayerID)
        #         recommendation = "Check the log file for details."
        #         self.logger.error(message, exc_info=True)
        #         self.command_status.add_to_log(command_phase_type.RUN,
        #                                        CommandLogRecord(command_status_type.FAILURE, message,
        #                                                         recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
