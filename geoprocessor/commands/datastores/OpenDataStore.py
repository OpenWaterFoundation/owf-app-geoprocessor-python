# OpenDataStore

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


class OpenDataStore(AbstractCommand):
    """
    Create an open database connection.

    Command Parameters
    * Host (str, required): the database host
    * DatabaseName (str, required): the name of the database
    * User (str, required): the database user
    * Password (str, required): the database user's password
    * Port (str, required): the database port
    * DataStoreID (str, optional): the DataStore identifier. Default value: DatabaseName
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("Host", type("")),
        CommandParameterMetadata("DatabaseName", type("")),
        CommandParameterMetadata("User", type("")),
        CommandParameterMetadata("Password", type("")),
        CommandParameterMetadata("Port", type("")),
        CommandParameterMetadata("DataStoreID", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "OpenDataStore"
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

        # Check that the required parameters are non-empty, non-None string.
        required_parameters = ["Host", "DatabaseName", "User", "Password", "Port"]
        for parameter in required_parameters:

            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)

            if not validators.validate_string(parameter_value, False, False):
                message = "{} parameter has no value.".format(parameter)
                recommendation = "Specify a valid {} parameter.".format(parameter)
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

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def __should_open_datastore(self):
        """
       Checks the following:

       Args:

       Returns:
           run_open: Boolean. If TRUE, the process should be run. If FALSE, it should not be run.
       """

        return True

        # TODO egiles 2018/06/05 Need to add checks --> not sure which checks to run

    def run_command(self):
        """
        Run the command.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_Host = self.get_parameter_value("Host")
        pv_DatabaseName = self.get_parameter_value("DatabaseName")
        pv_User = self.get_parameter_value("User")
        pv_Password = self.get_parameter_value("Password")
        pv_Port = self.get_parameter_value("Port")
        pv_DataStoreID = self.get_parameter_value("DataStoreID", default_value=pv_DatabaseName)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_open_datastore():

            try:

                # Open a connection to the database
                connection = pg.connect("host={} dbname={} user={} password={} port={}".format(pv_Host,
                                                                                               pv_DatabaseName,
                                                                                               pv_User,
                                                                                               pv_Password,
                                                                                               pv_Port))

                # Create a DataStore and add it to the geoprocessor's datastore list.
                datastore_obj = DataStore(pv_DataStoreID, connection,  pv_Host, pv_User, pv_Password, pv_Port)
                self.command_processor.add_datastore(datastore_obj)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error reading opening DataStore {} from database ({}).".format(pv_DataStoreID,
                                                                                                     pv_DatabaseName)
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
