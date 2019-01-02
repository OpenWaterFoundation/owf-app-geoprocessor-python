# OpenDataStore - command to open a datastore
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2019 Open Water Foundation
# 
# GeoProcessor is free software:  you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     GeoProcessor is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with GeoProcessor.  If not, see <https://www.gnu.org/licenses/>.
# ________________________________________________________________NoticeEnd___

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType
from geoprocessor.core.DataStore import DataStore

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validators

import logging


class OpenDataStore(AbstractCommand):
    """
    Create an open database connection.

    Command Parameters
    * DataStoreID (str, required): the DataStore identifier.
    * IfDataStoreIDExists (str, optional): This parameter determines the action that occurs if the DataStoreID already
        exists within the GeoProcessor. Available options are: `Replace`, `Open`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    * DatabaseDialect (str, required): The database type, used to format the database connection URL for the matching
            database driver software. Currently the following are supported: PostgreSQL.
    * DatabaseServer (str, required): The database server name or IP address. Can be specified using ${Property}.
    * DatabaseName (str, required): the name of the database. Can be specified using ${Property}.
    * DatabaseUser (str, required): The database user. A read-only "guest" (or similar) account should be used for
            read-only operations, if possible. Can be specified using ${Property}.
    * DatabasePassword (str, required): The database password. Can be specified using ${Property}.
    * DatabasePort (str, optional): The database port.
    * ConfigFile (str, required): The path (relative or full) to the configuration file.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("OpenMode", type("")),
        CommandParameterMetadata("DatabaseDialect", type("")),
        CommandParameterMetadata("DatabaseServer", type("")),
        CommandParameterMetadata("DatabaseName", type("")),
        CommandParameterMetadata("DatabaseUser", type("")),
        CommandParameterMetadata("DatabasePassword", type("")),
        CommandParameterMetadata("DatabasePort", type("")),
        CommandParameterMetadata("DataStoreID", type("")),
        CommandParameterMetadata("ConfigFile", type("")),
        CommandParameterMetadata("IfDataStoreIDExists", type(""))]

    # Choices for DatabaseDialect, used to validate parameter and display in editor
    __choices_DatabaseDialect = ["PostGreSQL"]

    # Choices for IfDataStoreIDExists, used to validate parameter and display in editor
    __choices_IfDataStoreIDExists = ["Replace", "Open", "Warn", "Fail", "ReplaceAndWarn"]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "OpenDataStore"
        self.command_description = "Create a DataStore connection."
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
        pv_DataStoreID = self.get_parameter_value(parameter_name="DataStoreID", command_parameters=command_parameters)

        if not validators.validate_string(pv_DataStoreID, False, False):
            message = "DataStoreID parameter has no value."
            recommendation = "Specify a valid DataStore ID."
            warning += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional IfDataStoreIDExists param is `Replace`, `Open`, `Warn`, `Fail`, `ReplaceAndWarn` or None.
        pv_IfDataStoreIDExists = self.get_parameter_value(parameter_name="IfDataStoreIDExists",
                                                          command_parameters=command_parameters)

        if not validators.validate_string_in_list(pv_IfDataStoreIDExists, self.__choices_IfDataStoreIDExists,
                                                  none_allowed=True, empty_string_allowed=False, ignore_case=True):
            message = "IfDataStoreIDExists parameter value ({}) is not recognized.".format(pv_IfDataStoreIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfDataStoreIDExists parameter.". \
                format(self.__choices_IfDataStoreIDExists)
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check if the ConfigFile parameter is a non-empty, non-None string.
        pv_ConfigFile = self.get_parameter_value(parameter_name="ConfigFile", command_parameters=command_parameters)

        # If there is a value for ConfigFile, assume "Configuration file configures datastore" method.
        if validators.validate_string(pv_ConfigFile, False, False):

            pass

        # If the IfDataStoreIDExists parameter is set to "Open", ignore all checks.
        elif validators.validate_string_in_list(pv_IfDataStoreIDExists, ["OPEN"], False, False, True):

            pass

        # If there is no value for ConfigFile, assume "Parameters configure datastore" method.
        else:

            # Check that the required parameters are non-empty, non-None string.
            required_parameters = ["DatabaseServer", "DatabaseName", "DatabaseUser", "DatabasePassword"]
            for parameter in required_parameters:

                parameter_value = self.get_parameter_value(parameter_name=parameter,
                                                           command_parameters=command_parameters)

                if not validators.validate_string(parameter_value, False, False):
                    message = "{} parameter has no value.".format(parameter)
                    recommendation = "Specify a valid {} parameter.".format(parameter)
                    warning += "\n" + message
                    self.command_status.add_to_log(
                        CommandPhaseType.INITIALIZATION,
                        CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

            # Check that parameter DatabaseDialect is one of the acceptable values.
            pv_DatabaseDialect = self.get_parameter_value(parameter_name="DatabaseDialect",
                                                          command_parameters=command_parameters)

            if not validators.validate_string_in_list(pv_DatabaseDialect, self.__choices_DatabaseDialect, False, False,
                                                      True):
                message = "DatabaseDialect parameter value ({}) is not recognized.".format(pv_DatabaseDialect)
                recommendation = "Specify one of the acceptable values ({}) for the DatabaseDialect parameter.".format(
                    self.__choices_DatabaseDialect)
                warning += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def __should_open_datastore(self, datastore_id, file_path_abs, if_datastore_id_exists):
        """
            Checks the following:
                * the DataStore ID is unique
                * the ConfigFile is a valid file, if applicable
                * the DataStore is closed, if configured to open an existing DataStore

            Args:
                datastore_id (str): the ID of the DataStore to open/create
                file_path_abs (str): the absolute path the configuration file. Will be None if the "Parameters
                    configure datastore" method is to be used.
                if_datastore_id_exists (str):  Determines the action that occurs if the DataStoreID already exists.

            Returns:
                 Boolean. If TRUE, the  process should be run. If FALSE, it should not be run.
           """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the DataStoreID is the same as an already-existing DataStoreID, raise a WARNING, FAILURE or IGNORE
        # (depends on the value of the IfDataStoreIDExists parameter.)
        should_run_command.append(validators.run_check(self, "IsDataStoreIdUnique", "DataStoreID", datastore_id,
                                                       None))

        # If the "Configuration file configures datastore" method is to be used, continue with check.
        if file_path_abs is not None:

            # If the configuration file does not exists, raise a FAILURE.
            should_run_command.append(validators.run_check(self, "IsFilePathValid", "File", file_path_abs, "FAIL"))

        # If the DataStoreID already exists and the IfDataStoreIDExists parameter is set to "Open", continue.
        if self.command_processor.get_datastore(datastore_id) and if_datastore_id_exists.upper() == "OPEN":

            # Get the DataStore object.
            obj = self.command_processor.get_datastore(datastore_id)

            # Check that the existing DataStore is closed.
            if obj.is_connected:

                self.warning_count += 1
                message = "The DataStore ({}) is already open.".format(datastore_id)
                recommendation = "Specify a DataStoreID of a closed DataStore."
                self.logger.error(message)
                self.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.FAILURE,
                                                                                      message, recommendation))
                should_run_command.append(False)

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self):
        """
        Run the command. Open the connection to a database and store as a DataStore.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values. The DatabasePort parameter value will be obtained later in the code.
        pv_DatabaseDialect = self.get_parameter_value("DatabaseDialect")
        pv_DatabaseServer = self.get_parameter_value("DatabaseServer")
        pv_DatabaseName = self.get_parameter_value("DatabaseName")
        pv_DatabaseUser = self.get_parameter_value("DatabaseUser")
        pv_DatabasePassword = self.get_parameter_value("DatabasePassword")
        pv_DatabasePort = self.get_parameter_value("DatabasePort")
        pv_DataStoreID = self.get_parameter_value("DataStoreID")
        pv_ConfigFile = self.get_parameter_value("ConfigFile")
        pv_IfDataStoreIDExists = self.get_parameter_value("IfDataStoreIDExists", default_value="Replace")

        # Expand for ${Property} syntax.
        pv_DatabaseServer = self.command_processor.expand_parameter_value(pv_DatabaseServer, self)
        pv_DatabaseName = self.command_processor.expand_parameter_value(pv_DatabaseName, self)
        pv_DatabaseUser = self.command_processor.expand_parameter_value(pv_DatabaseUser, self)
        pv_DatabasePassword = self.command_processor.expand_parameter_value(pv_DatabasePassword, self)

        # Convert the File parameter value relative path to an absolute path and expand for ${Property} syntax.
        if pv_ConfigFile:
            pv_ConfigFile = io_util.verify_path_for_os(io_util.to_absolute_path(
                self.command_processor.get_property('WorkingDir'), self.command_processor.expand_parameter_value(
                    pv_ConfigFile, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_open_datastore(pv_DataStoreID, pv_ConfigFile, pv_IfDataStoreIDExists):

            try:

                # If the DataStoreID already exists and the IfDataStoreIDExists parameter is set to "Open", continue.
                if self.command_processor.get_datastore(pv_DataStoreID) and pv_IfDataStoreIDExists.upper() == "OPEN":

                    # Get the DataStore obj from the ID and open the connection.
                    datastore_obj = self.command_processor.get_datastore(pv_DataStoreID)
                    datastore_obj.open_db_connection()

                # If the "Configuration file configures datastore" method is used.
                elif pv_ConfigFile is not None:

                    print("WARNING: The 'Configuration file configures datastore' method is not currently enabled.")

                # If the "Parameters configure datastore" method is used.
                else:

                    # Create a new DataStore object and assign the DataStore ID.
                    new_datastore = DataStore(pv_DataStoreID)

                    # Assign the DataBase URI for the appropriate DataBase dialect.
                    if pv_DatabaseDialect.upper() == "POSTGRESQL":

                        new_datastore.get_db_uri_postgres(pv_DatabaseServer, pv_DatabaseName, pv_DatabaseUser,
                                                          pv_DatabasePassword, pv_DatabasePort)

                    # Open a connection to the database and add the DataStore object to the GeoProcessor.
                    new_datastore.open_db_connection()
                    self.command_processor.add_datastore(new_datastore)

            # Raise an exception if an unexpected error occurs during the process.
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error opening DataStore {}.".format(pv_DataStoreID)
                recommendation = "Check the log file for details."
                self.logger.error(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
