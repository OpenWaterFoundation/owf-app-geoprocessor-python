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

    # TODO egiles 2018-01-16 Need to discuss the following with Steve and implement code design from the discussion:
    #   TODO Explained in detail in issue #22 of owf-app-geoprocessor-python GitHub repo
    #   TODO (1) Should there be another command function called check_command_parameters_during_run where the command
    #   TODO parameter values that cannot be checked in the current check_command_parameters are checked before running.
    #   TODO The benefit of this would be that the run_command function would ONLY be concerned with the running of the
    #   TODO process rather than checking the parameter values. The following TODO items are parameter checks that need
    #   TODO to be written for the ClipGeoLayer command (either in the run_command function or a
    #   TODO new check_command_parameters_during_run function)
    #   TODO (2) Check that the clipping GeoLayer contains features with polygon geometries. (not in current code)
    #   TODO (3) Check that the input GeoLayer and the clipping GeoLayer are in the same CRS (not in current code)
    #   TODO (4) Check that the input GeoLayer ID is a valid ID (in current code under run_command function)
    #   TODO (5) Check that the clipping GeoLayer ID is a valid ID (in current code under run_command function)
    #   TODO (6) Check that the OutputGeoLayer ID is not an already existing GeoLayer ID (in current code ...)
    #   TODO (7) Check that the OutputGeoLayer ID is not an already existing GeoLayerList ID (in current code ...)

    """
    Clips a GeoLayer by another GeoLayer.

    This command clips an input GeoLayer by the boundary of a clipping GeoLayer (polygon). The features of the input
    GeoLayer are retained in the output clipped layer if they intersect with the boundary of the clipping GeoLayer.
    The output clipped layer will become a new GeoLayer. The attribute fields and values of the input GeoLayer are
    retained within the output clipped GeoLayer.
    """

    # Command Parameters
    # InputGeoLayerID (str, required): the ID of the input GeoLayer, the layer to be clipped
    # ClippingGeoLayerID (str, required): the ID of the clipping GeoLayer. This GeoLayer must have polygon geometry.
    # OutputGeoLayerID (str, optional): the ID of the GeoLayer created as the output clipped layer. By default the
    #   GeoLayerID of the output layer will be {}_clippedBy_{} where the first variable is the InputGeoLayerID and the
    #   second variable is that ClippingGeoLayerID
    # IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the CopiedGeoLayerID
    #   already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
    #   (Refer to user documentation for detailed description.) Default value is `Replace`.
    __command_parameter_metadata = [
        CommandParameterMetadata("InputGeoLayerID", type("")),
        CommandParameterMetadata("ClippingGeoLayerID", type("")),
        CommandParameterMetadata("OutputGeoLayerID", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        super(ClipGeoLayer, self).__init__()
        self.command_name = "Clip"
        self.command_parameter_metadata = self.__command_parameter_metadata
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
            logger.warning(warning)
            raise ValueError(warning)
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def __should_geolayer_be_created(self, geolayer_id):
        """
        Checks that the ID of the GeoLayer to be created is not an existing GeoLayerList ID or an existing GeoLayer ID.
        The GeoLayer will NOT be created if ID is the same as an existing GeoLayerList ID. Depending on the
        IfGeoLayerIDExists parameter value, the GeoLayer to be created might be created even if it has the same ID as
        an existing GeoLayer ID. (See logic or user documentation for more detailed information.)

        Args:
            geolayer_id: the id of the GeoLayer to be created

        Returns:
            create_geolayer: Boolean. If TRUE, the GeoLayer should be created. If FALSE, the GeoLayer should not be
            created.

        Raises:
            None.
        """

        # Boolean to determine if the GeoLayer should be created. Set to true until an error occurs.
        create_geolayer = True

        # If the geolayer_id is the same as as already-existing GeoLayerListID, raise a FAILURE.
        if self.command_processor.get_geolayerlist(geolayer_id):

            create_geolayer = False
            self.warning_count += 1
            message = 'The GeoLayer ID ({}) value is already in use as a GeoLayerList ID.'.format(geolayer_id)
            recommendation = 'Specifiy a new GeoLayerID.'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE,
                                                            message, recommendation))

        # If the geolayer_id is the same as an already-registered GeoLayerID, react according to the
        # pv_IfGeoLayerIDExists value.
        elif self.command_processor.get_geolayer(geolayer_id):

            # Get the IfGeoLayerIDExists parameter value.
            pv_IfGeoLayerIDExists = self.get_parameter_value("IfGeoLayerIDExists", default_value="Replace")

            # Warnings/recommendations if the geolayer_id is the same as a registered GeoLayerID
            message = 'The GeoLayer ID ({}) value is already in use as a GeoLayer ID.'.format(geolayer_id)
            recommendation = 'Specify a new GeoLayerID.'

            # The registered GeoLayer should be replaced with the new GeoLayer (with warnings).
            if pv_IfGeoLayerIDExists.upper() == "REPLACEANDWARN":
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.WARNING,
                                                                message, recommendation))

            # The registered GeoLayer should not be replaces. A warning should be logged.
            if pv_IfGeoLayerIDExists.upper() == "WARN":
                create_geolayer = False
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.WARNING,
                                                                message, recommendation))

            # The matching IDs should cause a FAILURE.
            elif pv_IfGeoLayerIDExists.upper() == "FAIL":
                create_geolayer = False
                self.warning_count += 1
                self.logger.error(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE,
                                                                message, recommendation))

        return create_geolayer

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

        # Obtain the parameter values.
        pv_InputGeoLayerID = self.get_parameter_value("InputGeoLayerID")
        pv_ClippingGeoLayerID = self.get_parameter_value("ClippingGeoLayerID")
        pv_OutputGeoLayerID = self.get_parameter_value("OutputGeoLayerID", default_value="{}_clippedBy_{}".format(
            pv_InputGeoLayerID, pv_ClippingGeoLayerID))


        # Check that the InputGeoLayerID is a valid GeoLayer ID.
        if self.command_processor.get_geolayer(pv_InputGeoLayerID):

            # Check that the ClippingGeoLayerID is a valid GeoLayer ID.
            if self.command_processor.get_geolayer(pv_ClippingGeoLayerID):

                # Check if the OutputGeoLayer should be created. Continue if TRUE. Error handling dealt with inside
                # the `__should_geolayer_be_created` method.
                if self.__should_geolayer_be_created(pv_OutputGeoLayerID):

                    # Get the Input GeoLayer and the Clipping GeoLayer.
                    input_geolayer = self.command_processor.get_geolayer(pv_InputGeoLayerID)
                    clipping_geolayer = self.command_processor.get_geolayer(pv_ClippingGeoLayerID)

                    try:
                        # Perform the QGIS clip function
                        # Arg1: the qgis algorithm
                        # Arg2: the QgsVectorLayer containing the features to be clipped.
                        # Arg3: the QgsVectorLayer  containing the features that are used to clip the features in
                        #   the input layer.
                        # Arg4: the full file pathname of the output product. If None, output product is saved in
                        #   memory within the QGIS environment. That memory layer is then saved to the
                        #   clipped_output variable.
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

            # The ClippingGeoLayerID is not a valid GeoLayer ID.
            else:
                self.warning_count += 1
                message = 'The ClippingGeoLayerID ({}) value is not a valid GeoLayer ID.'.format(pv_ClippingGeoLayerID)
                recommendation = 'Specify a valid GeoLayerID.'
                self.logger.error(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message,
                                                                recommendation))

        # The InputGeoLayerID is not a valid GeoLayer ID.
        else:
            self.warning_count += 1
            message = 'The InputGeoLayerID ({}) is not a valid GeoLayer ID.'.format(pv_InputGeoLayerID)
            recommendation = 'Specify a valid GeoLayerID.'
            self.logger.error(message)
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
