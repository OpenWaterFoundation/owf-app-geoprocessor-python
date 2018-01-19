# CopyGeoLayer

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.validators as validators

import logging


class CopyGeoLayer(AbstractCommand):

    """
    Creates a copy of a GeoLayer in the GeoProcessor's geolayers list. The copied GeoLayer is added to the
    GeoProcessor's geolayers list.
    """

    # Command Parameters
    # GeoLayerID (str, required): The ID of the existing GeoLayer to copy.
    # CopiedGeoLayerID (str, optional): The ID of the copied GeoLayer. Default "{}_copy".format(GeoLayerID)
    # IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the CopiedGeoLayerID
    #   already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
    #   (Refer to user documentation for detailed description.) Default value is `Replace`.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("CopiedGeoLayerID", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        super(CopyGeoLayer, self).__init__()
        self.command_name = "CopyGeoLayer"
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

        # Check that parameter GeoLayerID is a non-empty, non-None string.
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID',
                                                 command_parameters=command_parameters)

        if not validators.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the GeoLayer to copy."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that optional parameter IfGeoLayerIDExists is either `Replace`, `ReplaceAndWarn`, `Warn`, `Fail` or
        # None.
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
        Run the command. Make a copy of the GeoLayer and add the copied GeoLayer to the GeoProcessor's geolayers list.

        Args:
            None.

        Returns:
            Nothing.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")

        # Check that the GeoLayerID is a valid GeoLayer ID.
        if self.command_processor.get_geolayer(pv_GeoLayerID):

            # Get the CopiedGeoLayerID parameter value
            pv_CopiedGeoLayerID = self.get_parameter_value("CopiedGeoLayerID",
                                                           default_value="{}_copy".format(pv_GeoLayerID))

            # Check if the CopiedGeoLayer should be created. Continue if TRUE. Error handling dealt with inside
            # the `__should_geolayer_be_created` method.
            if self.__should_geolayer_be_created(pv_CopiedGeoLayerID):

                # Copy the GeoLayer and add the copied GeoLayer to the GeoProcessor's geolayers list.
                try:
                    self.command_processor.copy_geolayer(pv_GeoLayerID, pv_CopiedGeoLayerID)

                # Raise an exception if an unexpected error occurs during the process
                except Exception as e:
                    self.warning_count += 1
                    message = "Unexpected error copying GeoLayer {} ".format(pv_GeoLayerID)
                    recommendation = "Check the log file for details."
                    self.logger.exception(message, e)
                    self.command_status.add_to_log(command_phase_type.RUN,
                                                   CommandLogRecord(command_status_type.FAILURE, message,
                                                                    recommendation))

        # The GeoLayerID is not a valid GeoLayer ID.
        else:
            self.warning_count += 1
            message = 'The GeoLayerID ({}) value is not a valid GeoLayer ID.'.format(pv_GeoLayerID)
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
