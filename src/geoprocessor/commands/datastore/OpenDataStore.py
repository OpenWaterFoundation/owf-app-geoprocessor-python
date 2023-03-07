# OpenDataStore - command to open a datastore
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2020 Open Water Foundation
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

from geoprocessor.core.CommandError import CommandError
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType
from geoprocessor.core.DataStore import DataStore

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validator_util

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
    __command_parameter_metadata: [CommandParameterMetadata] = [
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

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = ("This command creates a generic DataStore to provide data access "
                                         "from: \n"
                                         "- a database")
    #                                    "- a web service")
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # DataStoreID
    __parameter_input_metadata['DataStoreID.Description'] = "identifier to assign to the DataStore"
    __parameter_input_metadata['DataStoreID.Label'] = "DataStoreID"
    __parameter_input_metadata['DataStoreID.Required'] = True
    __parameter_input_metadata['DataStoreID.Tooltip'] = \
        "Identifier to assign to the DataStore. This allows the DataStore to be used with other commands.\n" \
        "Can be specified using ${Property}."
    # IfDataStoreIDExists
    __parameter_input_metadata['IfDataStoreIDExists.Description'] =\
        "the action that occurs if the DataStoreID already exists"
    __parameter_input_metadata['IfDataStoreIDExists.Label'] = "If DataStoreID Exists"
    __parameter_input_metadata['IfDataStoreIDExists.Tooltip'] = \
        "The action that occurs if the DataStoreID already exists within the GeoProcessor.\n" \
        "Replace: The existing DataStore within the GeoProcessor is overwritten with the new DataStore. " \
        "No warning is logged.\n" \
        "Open: The existing DataStore is opened if closed. No warning is logged.\n" \
        "ReplaceAndWarn: The existing DataStore within the GeoProcessor is overwritten with the new " \
        "DataStore. A warning is logged.\n" \
        "Warn : The new DataStore is not created. A warning is logged.\n" \
        "Fail : The new DataStore is not created. A fail message is logged."
    __parameter_input_metadata['IfDataStoreIDExists.Value.Default'] = "Replace"
    __parameter_input_metadata['IfDataStoreIDExists.Values'] = \
        ["", "Replace", "Open", "ReplaceAndWarn", "Warn", "Fail"]
    # DatabaseServer
    __parameter_input_metadata['DatabaseServer.Description'] = "the database server name or IP address"
    __parameter_input_metadata['DatabaseServer.Label'] = "Database Server"
    __parameter_input_metadata['DatabaseServer.Required'] = True
    __parameter_input_metadata['DatabaseServer.Tooltip'] = \
        "The database server name or IP address.\nCan be specified using ${Property}."
    # DatabaseDialect
    __parameter_input_metadata['DatabaseDialect.Description'] = "the database dialect"
    __parameter_input_metadata['DatabaseDialect.Label'] = "Database Dialect"
    __parameter_input_metadata['DatabaseDialect.Required'] = True
    __parameter_input_metadata['DatabaseDialect.Tooltip'] = \
        "The database dialect, used to format the database connection URL for the matching database driver " \
        "software. "
    # DatabaseName
    __parameter_input_metadata['DatabaseName.Description'] = "the name of the database"
    __parameter_input_metadata['DatabaseName.Label'] = "Database Name"
    __parameter_input_metadata['DatabaseName.Required'] = True
    __parameter_input_metadata['DatabaseName.Tooltip'] = \
        "The name of the database. Can be specified using ${Property}."
    # DatabaseUser
    __parameter_input_metadata['DatabaseUser.Description'] = "the database user"
    __parameter_input_metadata['DatabaseUser.Label'] = "Database User"
    __parameter_input_metadata['DatabaseUser.Required'] = True
    __parameter_input_metadata['DatabaseUser.Tooltip'] = \
        "The database user. A read-only 'guest' (or similar) account should be used for read-only operations, " \
        "if possible.\nCan be specified using ${Property}."
    # DatabasePassword
    __parameter_input_metadata['DatabasePassword.Description'] = "the database password"
    __parameter_input_metadata['DatabasePassword.Label'] = "Database Password"
    __parameter_input_metadata['DatabasePassword.Required'] = True
    __parameter_input_metadata['DatabasePassword.Tooltip'] = \
        "The database password. Can be specified using ${Property}."
    # DatabasePort
    __parameter_input_metadata['DatabasePort.Description'] = "the database port"
    __parameter_input_metadata['DatabasePort.Label'] = "Database Port"
    __parameter_input_metadata['DatabasePort.Tooltip'] = "The database port."
    __parameter_input_metadata['DatabasePort.Value.Default'] = "The default port for the DatabaseDialect"
    # ConfigFile
    __parameter_input_metadata['ConfigFile.Description'] = "the path to the file"
    __parameter_input_metadata['ConfigFile.Label'] = "Config File"
    __parameter_input_metadata['ConfigFile.Required'] = True
    __parameter_input_metadata['ConfigFile.Tooltip'] = \
        "The path (relative or absolute) to the file containing the database configurations."

    # Choices for DatabaseDialect, used to validate parameter and display in editor
    __choices_DatabaseDialect: [str] = ["PostGreSQL"]

    # Choices for IfDataStoreIDExists, used to validate parameter and display in editor
    __choices_IfDataStoreIDExists: [str] = ["Replace", "Open", "Warn", "Fail", "ReplaceAndWarn"]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "OpenDataStore"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata
        self.parameter_input_metadata = self.__parameter_input_metadata

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters: dict) -> None:
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns: None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """

        warning_message = ""

        # Check that required parameters are non-empty, non-None strings.
        required_parameters = command_util.get_required_parameter_names(self)
        for parameter in required_parameters:
            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)
            if not validator_util.validate_string(parameter_value, False, False):
                message = "Required {} parameter has no value.".format(parameter)
                recommendation = "Specify the {} parameter.".format(parameter)
                warning_message += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional IfDataStoreIDExists param is `Replace`, `Open`, `Warn`, `Fail`, `ReplaceAndWarn` or None.
        # noinspection PyPep8Naming
        pv_IfDataStoreIDExists = self.get_parameter_value(parameter_name="IfDataStoreIDExists",
                                                          command_parameters=command_parameters)

        if not validator_util.validate_string_in_list(pv_IfDataStoreIDExists, self.__choices_IfDataStoreIDExists,
                                                      none_allowed=True, empty_string_allowed=False, ignore_case=True):
            message = "IfDataStoreIDExists parameter value ({}) is not recognized.".format(pv_IfDataStoreIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfDataStoreIDExists parameter.". \
                format(self.__choices_IfDataStoreIDExists)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # noinspection PyPep8Naming
        pv_ConfigFile = self.get_parameter_value(parameter_name="ConfigFile", command_parameters=command_parameters)

        if validator_util.validate_string(pv_ConfigFile, False, False):
            # If there is a value for ConfigFile, assume "Configuration file configures datastore" method.
            pass
        elif validator_util.validate_string_in_list(pv_IfDataStoreIDExists, ["OPEN"], False, False, True):
            # If the IfDataStoreIDExists parameter is set to "Open", ignore all checks.
            pass
        else:
            # If there is no value for ConfigFile, assume "Parameters configure datastore" method.

            # Check that the required parameters are non-empty, non-None string.
            required_parameters = ["DatabaseServer", "DatabaseName", "DatabaseUser", "DatabasePassword"]
            for parameter in required_parameters:

                parameter_value = self.get_parameter_value(parameter_name=parameter,
                                                           command_parameters=command_parameters)

                if not validator_util.validate_string(parameter_value, False, False):
                    message = "{} parameter has no value.".format(parameter)
                    recommendation = "Specify a valid {} parameter.".format(parameter)
                    warning_message += "\n" + message
                    self.command_status.add_to_log(
                        CommandPhaseType.INITIALIZATION,
                        CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

            # Check that parameter DatabaseDialect is one of the acceptable values.
            # noinspection PyPep8Naming
            pv_DatabaseDialect = self.get_parameter_value(parameter_name="DatabaseDialect",
                                                          command_parameters=command_parameters)

            if not validator_util.validate_string_in_list(pv_DatabaseDialect, self.__choices_DatabaseDialect,
                                                          False, False, True):
                message = "DatabaseDialect parameter value ({}) is not recognized.".format(pv_DatabaseDialect)
                recommendation = "Specify one of the acceptable values ({}) for the DatabaseDialect parameter.".format(
                    self.__choices_DatabaseDialect)
                warning_message += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            self.logger.warning(warning_message)
            raise CommandParameterError(warning_message)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, datastore_id: str, file_path_abs: str, if_datastore_id_exists: str) -> bool:
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
        should_run_command = list()

        # If the DataStoreID is the same as an already-existing DataStoreID, raise a WARNING, FAILURE or IGNORE
        # (depends on the value of the IfDataStoreIDExists parameter.)
        should_run_command.append(validator_util.run_check(self, "IsDataStoreIdUnique", "DataStoreID", datastore_id,
                                                           None))

        # If the "Configuration file configures datastore" method is to be used, continue with check.
        if file_path_abs is not None:

            # If the configuration file does not exists, raise a FAILURE.
            should_run_command.append(validator_util.run_check(self, "IsFilePathValid", "File", file_path_abs, "FAIL"))

        # If the DataStoreID already exists and the IfDataStoreIDExists parameter is set to "Open", continue.
        if self.command_processor.get_datastore(datastore_id) and if_datastore_id_exists.upper() == "OPEN":

            # Get the DataStore object.
            obj = self.command_processor.get_datastore(datastore_id)

            # Check that the existing DataStore is closed.
            if obj.is_connected:

                self.warning_count += 1
                message = "The DataStore ({}) is already open.".format(datastore_id)
                recommendation = "Specify a DataStoreID of a closed DataStore."
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.FAILURE,
                                                                                      message, recommendation))
                should_run_command.append(False)

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Open the connection to a database and store as a DataStore.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values. The DatabasePort parameter value will be obtained later in the code.
        # noinspection PyPep8Naming
        pv_DatabaseDialect = self.get_parameter_value("DatabaseDialect")
        # noinspection PyPep8Naming
        pv_DatabaseServer = self.get_parameter_value("DatabaseServer")
        # noinspection PyPep8Naming
        pv_DatabaseName = self.get_parameter_value("DatabaseName")
        # noinspection PyPep8Naming
        pv_DatabaseUser = self.get_parameter_value("DatabaseUser")
        # noinspection PyPep8Naming
        pv_DatabasePassword = self.get_parameter_value("DatabasePassword")
        # noinspection PyPep8Naming
        pv_DatabasePort = self.get_parameter_value("DatabasePort")
        # noinspection PyPep8Naming
        pv_DataStoreID = self.get_parameter_value("DataStoreID")
        # noinspection PyPep8Naming
        pv_ConfigFile = self.get_parameter_value("ConfigFile")
        # noinspection PyPep8Naming
        pv_IfDataStoreIDExists = self.get_parameter_value("IfDataStoreIDExists", default_value="Replace")

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_DatabaseServer = self.command_processor.expand_parameter_value(pv_DatabaseServer, self)
        # noinspection PyPep8Naming
        pv_DatabaseName = self.command_processor.expand_parameter_value(pv_DatabaseName, self)
        # noinspection PyPep8Naming
        pv_DatabaseUser = self.command_processor.expand_parameter_value(pv_DatabaseUser, self)
        # noinspection PyPep8Naming
        pv_DatabasePassword = self.command_processor.expand_parameter_value(pv_DatabasePassword, self)

        # Convert the File parameter value relative path to an absolute path and expand for ${Property} syntax.
        if pv_ConfigFile:
            # noinspection PyPep8Naming
            pv_ConfigFile = io_util.verify_path_for_os(io_util.to_absolute_path(
                self.command_processor.get_property('WorkingDir'), self.command_processor.expand_parameter_value(
                    pv_ConfigFile, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(pv_DataStoreID, pv_ConfigFile, pv_IfDataStoreIDExists):
            # noinspection PyBroadException
            try:
                if self.command_processor.get_datastore(pv_DataStoreID) and pv_IfDataStoreIDExists.upper() == "OPEN":
                    # Get the DataStore obj from the ID and open the connection.
                    datastore_obj = self.command_processor.get_datastore(pv_DataStoreID)
                    datastore_obj.open_db_connection()

                elif pv_ConfigFile is not None:
                    # If the "Configuration file configures datastore" method is used.

                    print("WARNING: The 'Configuration file configures datastore' method is not currently enabled.")

                else:
                    # If the "Parameters configure datastore" method is used.

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
            except Exception:
                self.warning_count += 1
                message = "Unexpected error opening DataStore {}.".format(pv_DataStoreID)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
