# ClipGeoLayer

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.command as command_util
import geoprocessor.util.validators as validators
import geoprocessor.util.qgis_util as qgis_util

import logging

from processing.tools import general


class ClipGeoLayer(AbstractCommand):

    """
    Clips a GeoLayer by another GeoLayer.

    This command clips an input GeoLayer by the boundary of a clipping GeoLayer (polygon). The features of the input
    GeoLayer are retained in the output clipped layer if they intersect with the boundary of the clipping GeoLayer.
    The output clipped layer will become a new GeoLayer. The attribute fields and values of the input GeoLayer are
    retained within the output clipped GeoLayer.

    Command Parameters

    * InputGeoLayerID (str, required): the ID of the input GeoLayer, the layer to be clipped
    * ClippingGeoLayerID (str, required): the ID of the clipping GeoLayer. This GeoLayer must have polygon geometry.
    * OutputGeoLayerID (str, optional): the ID of the GeoLayer created as the output clipped layer. By default the
        GeoLayerID of the output layer will be {}_clippedBy_{} where the first variable is the InputGeoLayerID and the
        second variable is that ClippingGeoLayerID.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the CopiedGeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("InputGeoLayerID", type("")),
        CommandParameterMetadata("ClippingGeoLayerID", type("")),
        CommandParameterMetadata("OutputGeoLayerID", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super(ClipGeoLayer, self).__init__()
        self.command_name = "ClipGeoLayer"
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
            Nothing.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning = ""

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
        acceptable_values = ["Replace", "Warn", "Fail", "ReplaceAndWarn"]
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

    def __should_clip_geolayer(self, input_geolayer_id, clipping_geolayer_id, output_geolayer_id):
        """
        Checks the following:
        * the ID of the input GeoLayer is an existing GeoLayer ID
        * the ID of the clipping GeoLayer is an existing GeoLayer ID
        * the clipping GeoLayer contains features with POLYGON geometry
        * the input GeoLayer and the clipping GeoLayer are in the same coordinate reference system (warning, not error)
        * the ID of the output GeoLayer is unique (not an existing GeoLayerList ID)
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)

        Args:
            input_geolayer_id: the ID of the input GeoLayer
            clipping_geolayer_id: the ID of the clipping GeoLayer
            output_geolayer_id: the ID of the output, clipped GeoLayer

        Returns:
            run_clip: Boolean. If TRUE, the clipping process should be run. If FALSE, the clipping process should not
            be run.
        """

        # Boolean to determine if the clipping process should be run. Set to true until an error occurs.
        run_clip = True

        # Boolean to determine if the input GeoLayers (input and clipping) exist. Set to TRUE until proven FALSE.
        input_geolayers_exist = True

        # If the input GeoLayer ID is not an existing GeoLayer ID, raise a FAILURE.
        if not self.command_processor.get_geolayer(input_geolayer_id):

            run_clip = False
            input_geolayers_exist = False
            self.warning_count += 1
            message = 'The InputGeoLayerID ({}) is not a valid GeoLayer ID.'.format(input_geolayer_id)
            recommendation = 'Specify a valid GeoLayerID.'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # If the clipping GeoLayer ID is not an existing GeoLayer ID, raise a FAILURE.
        if not self.command_processor.get_geolayer(clipping_geolayer_id):

            run_clip = False
            input_geolayers_exist = False
            self.warning_count += 1
            message = 'The ClippingGeoLayerID ({}) value is not a valid GeoLayer ID.'.format(clipping_geolayer_id)
            recommendation = 'Specify a valid GeoLayerID.'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # If the clipping GeoLayerID does not contain features of polygon type, raise a FAILURE
        elif not self.command_processor.get_geolayer(clipping_geolayer_id).get_geometry() == "Polygon":

            run_clip = False
            self.warning_count += 1
            message = 'The ClippingGeoLayerID ({}) does not have POLYGON geometry.'.format(clipping_geolayer_id)
            recommendation = 'Specify a GeoLayerID of a GeoLayer with POLYGON geometry.'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # If the input GeoLayer and the clipping GeoLayer do not have the same CRS, raise a WARNING.
        if input_geolayers_exist:

            # Get the CRS of the input GeoLayer and the clipping GeoLayer
            crs_input = self.command_processor.get_geolayer(input_geolayer_id).get_crs()
            crs_clipping = self.command_processor.get_geolayer(clipping_geolayer_id).get_crs()

            if not crs_input == crs_clipping:

                self.warning_count += 1
                message = 'The InputGeoLayerID ({}) and the ClippingGeoLayerID ({}) do not have the same coordinate' \
                          '\ reference system.'.format(crs_input, crs_clipping)
                recommendation = 'Specify a GeoLayers that have the same coordinate reference system.'
                self.logger.warning(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.WARNING, message, recommendation))

        # If the output GeoLayer ID is the same as as already-existing GeoLayerListID, raise a FAILURE.
        if self.command_processor.get_geolayerlist(output_geolayer_id):

            run_clip = False
            self.warning_count += 1
            message = 'The OutputGeoLayerID ({}) value is already in use as a GeoLayerList ID.'.format(
                output_geolayer_id)
            recommendation = 'Specify a new GeoLayerID.'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # If the output GeoLayerID is the same as an already-registered GeoLayerID, react according to the
        # pv_IfGeoLayerIDExists value.
        elif self.command_processor.get_geolayer(output_geolayer_id):

            # Get the IfGeoLayerIDExists parameter value.
            pv_IfGeoLayerIDExists = self.get_parameter_value("IfGeoLayerIDExists", default_value="Replace")

            # Warnings/recommendations if the OutputGeolayerID is the same as a registered GeoLayerID.
            message = 'The OutputGeoLayerID ({}) value is already in use as a GeoLayer ID.'.format(output_geolayer_id)
            recommendation = 'Specify a new GeoLayerID.'

            # The registered GeoLayer should be replaced with the new GeoLayer (with warnings).
            if pv_IfGeoLayerIDExists.upper() == "REPLACEANDWARN":

                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.WARNING, message, recommendation))

            # The registered GeoLayer should not be replaced. A warning should be logged.
            if pv_IfGeoLayerIDExists.upper() == "WARN":

                run_clip = False
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.WARNING, message, recommendation))

            # The matching IDs should cause a FAILURE.
            elif pv_IfGeoLayerIDExists.upper() == "FAIL":

                run_clip = False
                self.warning_count += 1
                self.logger.error(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Return the Boolean to determine if the clip process should be run. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return run_clip

    def run_command(self):
        """
        Run the command. Clip the input GeoLayer by the clipping GeoLayer. Create a new GeoLayer with the clipped
        output layer.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_InputGeoLayerID = self.get_parameter_value("InputGeoLayerID")
        pv_ClippingGeoLayerID = self.get_parameter_value("ClippingGeoLayerID")
        pv_OutputGeoLayerID = self.get_parameter_value("OutputGeoLayerID", default_value="{}_clippedBy_{}".format(
            pv_InputGeoLayerID, pv_ClippingGeoLayerID))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_clip_geolayer(pv_InputGeoLayerID, pv_ClippingGeoLayerID, pv_OutputGeoLayerID):

            try:

                # Get the Input GeoLayer and the Clipping GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_InputGeoLayerID)
                clipping_geolayer = self.command_processor.get_geolayer(pv_ClippingGeoLayerID)

                # Perform the QGIS clip function. Refer to the reference below for parameter descriptions.
                # REF: https://docs.qgis.org/2.8/en/docs/user_manual/processing_algs/qgis/vector_overlay_tools/clip.html
                clipped_output = general.runalg("qgis:clip",
                                                input_geolayer.qgs_vector_layer,
                                                clipping_geolayer.qgs_vector_layer,
                                                None)

                # Create a new GeoLayer and add it to the GeoProcessor's geolayers list.
                # clipped_output["OUTPUT"] returns the full file pathname of the memory output layer (saved
                # in a QGIS temporary folder)
                qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_file(clipped_output["OUTPUT"])
                new_geolayer = GeoLayer(pv_OutputGeoLayerID, qgs_vector_layer, "MEMORY")
                self.command_processor.add_geolayer(new_geolayer)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error clipping GeoLayer {} from GeoLayer {}.".format(
                    pv_InputGeoLayerID,
                    pv_ClippingGeoLayerID)
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
