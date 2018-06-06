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
    * DatabaseType (str, required): The database type, used to format the database connection URL for the matching
        database driver software. Currently the following are supported: PostgreSQL.
    * DatabaseServer (str, required): The database server name or IP address. Can be specified using ${Property}.
    * DatabaseName (str, required): the name of the database. Can be specified using ${Property}.
    * DatabaseUser (str, required): The database user. A read-only "guest" (or similar) account should be used for
        read-only operations, if possible. Can be specified using ${Property}.
    * DatabasePassword (str, required): The database password. Can be specified using ${Property}.
    * DatabasePort (str, optional): The database port.
    * DataStoreID (str, optional): the DataStore identifier. Default value: DatabaseName
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("DatabaseType", type("")),
        CommandParameterMetadata("DatabaseServer", type("")),
        CommandParameterMetadata("DatabaseName", type("")),
        CommandParameterMetadata("DatabaseUser", type("")),
        CommandParameterMetadata("DatabasePassword", type("")),
        CommandParameterMetadata("DatabasePort", type("")),
        CommandParameterMetadata("DataStoreID", type(""))]

    # Choices for DatabaseType, used to validate parameter and display in editor
    __choices_DatabaseType = ["POSTGRESQL"]

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
        required_parameters = ["DatabaseServer", "DatabaseName", "DatabaseUser", "DatabasePassword"]
        for parameter in required_parameters:

            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)

            if not validators.validate_string(parameter_value, False, False):
                message = "{} parameter has no value.".format(parameter)
                recommendation = "Specify a valid {} parameter.".format(parameter)
                warning += "\n" + message
                self.command_status.add_to_log(
                    command_phase_type.INITIALIZATION,
                    CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that parameter DatabaseType is one of the acceptable values.
        pv_DatabaseType = self.get_parameter_value(parameter_name="DatabaseType",
                                                   command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_DatabaseType, self.__choices_DatabaseType, False, False, True):
            message = "DatabaseType parameter value ({}) is not recognized.".format(pv_DatabaseType)
            recommendation = "Specify one of the acceptable values ({}) for the DatabaseType parameter.".format(
                self.__choices_DatabaseType)
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                           CommandLogRecord(command_status_type.FAILURE, message,
                                                            recommendation))

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

        # Obtain the parameter values. The DatabasePort parameter value will be obtained later in the code.
        pv_DatabaseType = self.get_parameter_value("DatabaseType")
        pv_DatabaseServer = self.get_parameter_value("DatabaseServer")
        pv_DatabaseName = self.get_parameter_value("DatabaseName")
        pv_DatabaseUser = self.get_parameter_value("DatabaseUser")
        pv_DatabasePassword = self.get_parameter_value("DatabasePassword")
        pv_DataStoreID = self.get_parameter_value("DataStoreID", default_value=pv_DatabaseName)

        # Expand for ${Property} syntax.
        pv_DatabaseServer = self.command_processor.expand_parameter_value(pv_DatabaseServer, self)
        pv_DatabaseName = self.command_processor.expand_parameter_value(pv_DatabaseName, self)
        pv_DatabaseUser = self.command_processor.expand_parameter_value(pv_DatabaseUser, self)
        pv_DatabasePassword = self.command_processor.expand_parameter_value(pv_DatabasePassword, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_open_datastore():

            try:

                if pv_DatabaseType.upper() == "POSTGRESQL":

                    # Get the port. If not set, use the default PostGreSQL port number.
                    pv_DatabasePort = self.get_parameter_value("DatabasePort", default_value="5432")

                    # Open a connection to the database
                    connection = pg.connect("host={} dbname={} user={} password={} port={}".format(pv_DatabaseServer,
                                                                                                   pv_DatabaseName,
                                                                                                   pv_DatabaseUser,
                                                                                                   pv_DatabasePassword,
                                                                                                   pv_DatabasePort))

                    # Create a DataStore and add it to the geoprocessor's datastore list.
                    datastore_obj = DataStore(pv_DataStoreID, connection,  pv_DatabaseName, pv_DatabaseServer,
                                              pv_DatabaseUser, pv_DatabaseUser, pv_DatabasePort)
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
