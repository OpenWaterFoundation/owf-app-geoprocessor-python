# ClipGeoLayer

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validators
import geoprocessor.util.qgis_util as qgis_util

import logging

import os

from plugins.processing.tools import general


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
        second variable is the ClippingGeoLayerID.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the OutputGeoLayerID
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
        super().__init__()
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
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)

        Args:
            input_geolayer_id: the ID of the input GeoLayer
            clipping_geolayer_id: the ID of the clipping GeoLayer
            output_geolayer_id: the ID of the output, clipped GeoLayer

        Returns:
             Boolean. If TRUE, the GeoLayer should be clipped. If FALSE, at least one check failed and the GeoLayer
                should not be clipped.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the input GeoLayerID is not an existing GeoLayerID, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsGeoLayerIDExisting", "InputGeoLayerID",
                                                       input_geolayer_id, "FAIL"))

        # If the clipping GeoLayer ID is not an existing GeoLayer ID, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsGeoLayerIDExisting", "ClippingGeoLayerID",
                                                       clipping_geolayer_id, "FAIL"))

        # If the input GeoLayer and the clipping GeoLayer both exist, continue with the checks.
        if False not in should_run_command:

            # If the clipping GeoLayerID does not contain features of polygon type, raise a FAILURE.
            should_run_command.append(validators.run_check(self, "DoesGeoLayerIDHaveCorrectGeometry",
                                                           "ClippingGeoLayerID", clipping_geolayer_id,
                                                           "FAIL", other_values=[["Polygon"]]))

            # If the input GeoLayer and the clipping GeoLayer do not have the same CRS, raise a WARNING.
            should_run_command.append(validators.run_check(self, "DoGeoLayerIDsHaveMatchingCRS", "InputGeoLayerID",
                                                           input_geolayer_id, "WARN",
                                                           other_values=["ClippingGeoLayerID", clipping_geolayer_id]))

        # If the OutputGeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE (depends
        # on the value of the IfGeoLayerIDExists parameter.)
        should_run_command.append(validators.run_check(self, "IsGeoLayerIdUnique", "OutputGeoLayerID",
                                                       output_geolayer_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

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

                # If the input GeoLayer is an in-memory GeoLayer, make it an on-disk GeoLayer.
                if input_geolayer.source_path is None or input_geolayer.source_path.upper() in ["", "MEMORY"]:

                    # Get the absolute path of the GeoLayer to write to disk.
                    geolayer_disk_abs_path = os.path.join(self.command_processor.get_property('TempDir'), input_geolayer.id)

                    # Write the GeoLayer to disk. Overwrite the (memory) GeoLayer in the geoprocessor with the
                    # on-disk GeoLayer.
                    input_geolayer = input_geolayer.write_to_disk(geolayer_disk_abs_path)
                    self.command_processor.add_geolayer(input_geolayer)

                # If the clipping GeoLayer is an in-memory GeoLayer, make it an on-disk GeoLayer.
                if clipping_geolayer.source_path is None or clipping_geolayer.source_path.upper() in ["", "MEMORY"]:

                    #  Get the absolute path of the GeoLayer to write to disk.
                    geolayer_disk_abs_path = os.path.join(self.command_processor.get_property('TempDir'),
                                                          clipping_geolayer.id)

                    # Write the GeoLayer to disk. Overwrite the (memory) GeoLayer in the geoprocessor with the
                    # on-disk GeoLayer.
                    clipping_geolayer = clipping_geolayer.write_to_disk(geolayer_disk_abs_path)
                    self.command_processor.add_geolayer(clipping_geolayer)

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
