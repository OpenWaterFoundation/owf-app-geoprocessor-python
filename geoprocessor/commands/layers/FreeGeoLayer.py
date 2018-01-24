# FreeGeoLayer

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.validators as validators

import logging


class FreeGeoLayer(AbstractCommand):

    """
    Removes a GeoLayer from the GeoProcessor.

    Command Parameters
    * GeoLayerID (str, required): The ID of the existing GeoLayer to copy.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super(FreeGeoLayer, self).__init__()
        self.command_name = "FreeGeoLayer"
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
        warning = ""

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

    def __should_geolayer_be_deleted(self, geolayer_id):
        """
        Checks the following:
        * the ID of the input GeoLayer is an existing GeoLayer ID

        Args:
            geolayer_id: the id of the GeoLayer to be removed

        Returns:
            remove_geolayer: Boolean. If TRUE, the GeoLayer should be removed. If FALSE, one or more checks have failed
             and the GeoLayer should not be removed.
        """

        # Boolean to determine if the GeoLayer should be removed. Set to TRUE until one or many checks fail.
        remove_geolayer = True

        # If the geolayer_id is not a valid GeoLayer ID, raise a FAILURE.
        if not self.command_processor.get_geolayer(geolayer_id):

            remove_geolayer = False
            self.warning_count += 1
            message = 'The GeoLayer ID ({}) is not a valid GeoLayer ID.'.format(geolayer_id)
            recommendation = 'Specify a new GeoLayerID.'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE,
                                                            message, recommendation))

        # Return the Boolean to determine if the GeoLayer should be removed. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return remove_geolayer

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

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_geolayer_be_deleted(pv_GeoLayerID):

            try:

                # Get GeoLayer to remove.
                geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Remove the GeoLayer from the GeoProcessor's geolayers list.
                index = self.command_processor.geolayers.index(geolayer)
                del self.command_processor.geolayers[index]

                # Delete the GeoLayer.
                del geolayer

            # Raise an exception if an unexpected error occurs during the process.
            except Exception as e:

                self.warning_count += 1
                message = "Unexpected error removing GeoLayer ({}).".format(pv_GeoLayerID)
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
