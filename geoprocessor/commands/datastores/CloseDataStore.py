# CloseDataStore

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.DataStore import DataStore

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validators

import logging
import psycopg2 as pg


class CloseDataStore(AbstractCommand):
    """
    Close an existing open database connection.

    Command Parameters
    * DataStoreID (str, required): the DataStore identifier of the DataStore to close. ${Property} syntax enabled.
    * StatusMessage (str, optional): A status message to display when the datastore information is viewed.
        The status may be reset if the connection is automatically restored, for example when a subsequent database
        interaction occurs. Default: DataStore [DataStoreID] has been closed. ${Property} syntax enabled.
        Note that this is a placeholder parameter ported over from the TSTool command (CloseDataStore). It currently
        has no effect of the GeoProcessor environment. In future development this message could be hooked into the
        log or the UI.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("DataStoreID", type("")),
        CommandParameterMetadata("StatusMessage", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "CloseDataStore"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns: None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """

        warning = ""

        # Check that the DataStoreID is a non-empty, non-None string.
        pv_DataStoreID = self.get_parameter_value(parameter_name="DataStoreID",
                                                  command_parameters=command_parameters)

        if not validators.validate_string(pv_DataStoreID, False, False):
            message = "DataStoreID parameter has no value."
            recommendation = "Specify a valid DataStore ID."
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def __should_close_datastore(self, datastore_id):
        """
        Checks the following:
            * the DataStore ID is an existing DataStore ID

        Args:
            datastore_id (str): the ID of the DataStore to close

        Returns:
             Boolean. If TRUE, the  process should be run. If FALSE, it should not be run.
       """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the DataStore ID is not an existing DataStore ID, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsDataStoreIdExisting", "DataStoreID", datastore_id,
                                                       "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self):
        """
        Run the command. Close an existing DataStore and remove it from the GeoProcessor.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the DataStoreID parameter value and expand for ${Property} syntax.
        pv_DataStoreID = self.get_parameter_value("DataStoreID")
        pv_DataStoreID = self.command_processor.expand_parameter_value(pv_DataStoreID, self)

        # Configure the default status message.
        default_status_message = "DataStore {} has been closed.".format(pv_DataStoreID)

        # Obtain the StatusMessage parameter value and expand for ${Property} syntax.
        pv_StatusMessage = self.get_parameter_value("StatusMessage", default_value=default_status_message)
        pv_StatusMessage = self.command_processor.expand_parameter_value(pv_StatusMessage, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_close_datastore(pv_DataStoreID):

            try:

                # Get the DataStore object
                datastore_obj = self.command_processor.get_datastore(pv_DataStoreID)

                # If the DataStore's database type is PostGreSQL, then continue.
                if datastore_obj.type.upper() == "POSTGRESQL":

                    # Close the DataStore connection.
                    datastore_obj.connection.close()

                    # Remove the DataStore object from the GeoProcessor.
                    self.command_processor.free_datastore(datastore_obj)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error closing DataStore {}.".format(pv_DataStoreID)
                recommendation = "Check the log file for details."
                self.logger.error(message, exc_info=True)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
