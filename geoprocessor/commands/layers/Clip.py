# Clip

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.command as command_util
import geoprocessor.util.validators as validators

import logging

from processing.tools import general


class Clip(AbstractCommand):

    """
    Clips a GeoLayer by another GeoLayer.

    This command clips an input GeoLayer by the boundary of a clipping GeoLayer (polygon). The features of the input
    GeoLayer are retained in the output clipped layer if they intersect with the boundary of the clipping GeoLayer.
    The output clipped layer will become a new GeoLayer. The attribute fields of the input GeoLayer are retained within
    the output clipped GeoLayer.
    """

    # Command Parameters
    # InputGeoLayerID (str, required): the ID of the input GeoLayer, the layer to be clipped
    # ClippingGeoLayerID (str, required): the ID of the clipping GeoLayer. This GeoLayer must have polygon geometry.
    # OutputGeoLayerID (str, optional): the ID for the new GeoLayer that will be created as the clipped output layer
    # IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the OutputGeoLayerID
    #   already exists within the GeoProcessor. Available options are: `Replace`, `Warn` and `Fail` (Refer to user
    #   documentation for detailed description.) Default value is `Replace`.
    __command_parameter_metadata = [
        CommandParameterMetadata("InputGeoLayerID", type("")),
        CommandParameterMetadata("ClippingGeoLayerID", type("")),
        CommandParameterMetadata("OutputGeoLayerID", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        super(Clip, self).__init__()
        self.command_name = "Clip"
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

        # Check that parameter InputGeoLayerID is a non-empty, non-None string.
        pv_InputGeoLayerID = self.get_parameter_value(parameter_name='InputGeoLayerID',
                                                      command_parameters=command_parameters)

        if not validators.validate_string(pv_InputGeoLayerID, False, False):
            message = "InputGeoLayerID parameter has no value."
            recommendation = "Specify the InputGeoLayerID parameter to indicate the input GeoLayer."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that parameter ClippingGeoLayerID is a non-empty, non-None string.
        pv_ClippingGeoLayerID = self.get_parameter_value(parameter_name='ClippingGeoLayerID',
                                                      command_parameters=command_parameters)

        if not validators.validate_string(pv_ClippingGeoLayerID, False, False):

            message = "ClippingGeoLayerID parameter has no value."
            recommendation = "Specify the ClippingGeoLayerID parameter to indicate the clipping GeoLayer."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that optional parameter IfGeoLayerIDExists is either `Replace`, `Warn`, `Fail` or None.
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        acceptable_values = ["Replace", "Warn", "Fail"]
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
            logger.warning(warning)
            raise ValueError(warning)
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def run_command(self):
        """
        Run the command. Clip the input GeoLayer by the clipping GeoLayer. Create a new GeoLayer with the clipped
        output layer.

        Args:
            None.

        Returns:
            Nothing.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Set up logger and warning count.
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Obtain the parameter values.
        pv_InputGeoLayerID = self.get_parameter_value("InputGeoLayerID")
        pv_ClippingGeoLayerID = self.get_parameter_value("ClippingGeoLayerID")
        pv_OutputGeoLayerID = self.get_parameter_value("OutputGeoLayerID", default_value="{}_clippedBy_{}".format(
            pv_InputGeoLayerID, pv_ClippingGeoLayerID))
        pv_IfGeoLayerIDExists = self.get_parameter_value("IfGeoLayerIDExists", default_value="Replace")

        # Check that the InputGeoLayerID is a valid GeoLayer ID.
        if self.command_processor.get_geolayer(pv_InputGeoLayerID):

            # Check that the ClippingGeoLayerID is a valid GeoLayer ID.
            if self.command_processor.get_geolayer(pv_ClippingGeoLayerID):

                # Mark as an error if the pv_OutputGeoLayerID is the same as a registered GeoLayerList ID
                if self.command_processor.get_geolayerlist(pv_OutputGeoLayerID):

                    warning_count += 1
                    message = 'The GeoLayer ID ({}) value is already in use as a GeoLayerList ID.'.format(
                        pv_OutputGeoLayerID)
                    recommendation = 'Specifiy a new GeoLayerID.'
                    logger.error(message)
                    self.command_status.add_to_log(command_phase_type.RUN,
                                                   CommandLogRecord(command_status_type.FAILURE,
                                                                    message, recommendation))

                else:

                    # Boolean to determine if the GeoLayer should be created. Only set to False if the input GeoLayerID
                    # is the same as a registered GeoLayerID and the IfGeoLayerIDExists is set to 'FAIL'
                    create_geolayer = True

                    # If the pv_OutputGeoLayerID is the same as an already-registered GeoLayerID, react according to the
                    # pv_IfGeoLayerIDExists value.
                    if self.command_processor.get_geolayer(pv_OutputGeoLayerID):

                        # Warnings/recommendations if the input GeoLayerID is the same as a registered GeoLayerID
                        message = 'The GeoLayer ID ({}) value is already in use as a GeoLayer ID.'.format(
                            pv_OutputGeoLayerID)
                        recommendation = 'Specify a new GeoLayerID.'

                        # The registered GeoLayer should be replaced with the new GeoLayer (with warnings).
                        if pv_IfGeoLayerIDExists.upper() == "WARN":
                            warning_count += 1
                            logger.warning(message)
                            self.command_status.add_to_log(command_phase_type.RUN,
                                                           CommandLogRecord(command_status_type.WARNING,
                                                                            message, recommendation))
                        # The matching IDs should cause a FAILURE.
                        elif pv_IfGeoLayerIDExists.upper() == "FAIL":
                            create_geolayer = False
                            warning_count += 1
                            logger.error(message)
                            self.command_status.add_to_log(command_phase_type.RUN,
                                                           CommandLogRecord(command_status_type.FAILURE,
                                                                            message, recommendation))

                    # If set to run, clip the input GeoLayer by the clipping GeoLayer and save the output as a new
                    # GeoLayer with the GeoLayer ID of pv_OutputGeoLayerID.
                    if create_geolayer:

                        # Get the Input GeoLayer and the Clipping GeoLayer.
                        input_geolayer = self.command_processor.get_geolayer(pv_InputGeoLayerID)
                        clipping_geolayer = self.command_processor.get_geolayer(pv_ClippingGeoLayerID)

                        # Check that the Clipping GeoLayer is of polygon type.
                        polygon_types = ["WKBPolygon", "WKBMultiPolygon", "WKBPolygon25D", "WKBMultiPolygon25D"]
                        if clipping_geolayer.geom_type in polygon_types:

                            # Log a warning if the CRS of the two GeoLayers are not the same.
                            if not input_geolayer.get_crs() == clipping_geolayer.get_crs():

                                warning_count += 1
                                message = "The Input GeoLayer ({}|{}) and the Clipping GeoLayer ({}|{}) do not have " \
                                          "the same Coordinate Reference Systems.".format(pv_InputGeoLayerID,
                                                                                          input_geolayer.get_crs(),
                                                                                          pv_ClippingGeoLayerID,
                                                                                          clipping_geolayer.get_crs())
                                recommendation = "Reproject one or both of the GeoLayers."
                                logger.warning(message)
                                self.command_status.add_to_log(command_phase_type.RUN,
                                                               CommandLogRecord(command_status_type.FAILURE, message,
                                                                                recommendation))

                            try:
                                # Perform the QGIS clip function
                                clipped_output = general.runalg("qgis:clip",
                                                                input_geolayer.qgs_vector_layer,
                                                                clipping_geolayer.qgs_vector_layer,
                                                                None)

                                # Create a new GeoLayer
                                new_geolayer = GeoLayer(pv_OutputGeoLayerID, clipped_output["OUTPUT"], "MEMORY")
                                self.command_processor.add_geolayer(new_geolayer)
                                logger.info("LOOK HERE")
                                logger.info(self.command_processor.geolayers)

                            # Raise an exception if an unexpected error occurs during the process
                            except Exception as e:
                                warning_count += 1
                                message = "Unexpected error clipping GeoLayer {} from GeoLayer {}.".format(
                                    pv_InputGeoLayerID, pv_ClippingGeoLayerID)
                                recommendation = "Check the log file for details."
                                logger.exception(message, e)
                                self.command_status.add_to_log(command_phase_type.RUN,
                                                               CommandLogRecord(command_status_type.FAILURE, message,
                                                                                recommendation))

                        # The Clipping GeoLayer is not a polygon.
                        else:
                            warning_count += 1
                            message = "The Clipping GeoLayer ({}) does not contain polygon features.".format(
                                pv_ClippingGeoLayerID)
                            recommendation = "Specify a GeoLayer with polygon geometry for the ClippingGeoLayerID " \
                                             "parameter."
                            logger.error(message)
                            self.command_status.add_to_log(command_phase_type.RUN,
                                                           CommandLogRecord(command_status_type.FAILURE, message,
                                                                            recommendation))

            # The ClippingGeoLayerID is not a valid GeoLayer ID.
            else:
                warning_count += 1
                message = 'The ClippingGeoLayerID ({}) value is not a valid GeoLayer ID.'.format(pv_ClippingGeoLayerID)
                recommendation = 'Specify a valid GeoLayerID.'
                logger.error(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message,
                                                                recommendation))


        # The InputGeoLayerID is not a valid GeoLayer ID.
        else:
            warning_count += 1
            message = 'The InputGeoLayerID ({}) is not a valid GeoLayer ID.'.format(pv_InputGeoLayerID)
            recommendation = 'Specify a valid GeoLayerID.'
            logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE, message,
                                                            recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
