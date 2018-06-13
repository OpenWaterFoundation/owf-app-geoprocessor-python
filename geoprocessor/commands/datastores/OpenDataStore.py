# OpenDataStore

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.DataStore import DataStore

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validators

import logging


class OpenDataStore(AbstractCommand):
    """
    Create an open database connection.

    Command Parameters
    * OpenMode (str, required): The method used to open the DataStore. Must choose one of the three options.
        * NewByParameters: Open a new DataStore by entering parameters in the required fields.
        * NewByFile: Open a new DataStore by supplying a file that has the required configurations.
        * ExistingByID: Open an existing but closed DataStore by entering the DataStore ID.
    * If OpenMode is NewByParameters:
        * DatabaseDialect (str, required): The database type, used to format the database connection URL for the matching
            database driver software. Currently the following are supported: PostgreSQL.
        * DatabaseServer (str, required): The database server name or IP address. Can be specified using ${Property}.
        * DatabaseName (str, required): the name of the database. Can be specified using ${Property}.
        * DatabaseUser (str, required): The database user. A read-only "guest" (or similar) account should be used for
            read-only operations, if possible. Can be specified using ${Property}.
        * DatabasePassword (str, required): The database password. Can be specified using ${Property}.
        * DatabasePort (str, optional): The database port.
        * DataStoreID (str, optional): the DataStore identifier. Default value: DatabaseName
        * IfDataStoreIDExists (str, optional): This parameter determines the action that occurs if the DataStoreID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    * If OpenMode is NewByFile:
        * File (str, required): The path (relative or full) to the configuration file.
        Can be specified using ${Property}.
        * DataStoreID (str, optional): the DataStore identifier. Default value: DatabaseName
        * IfDataStoreIDExists (str, optional): This parameter determines the action that occurs if the DataStoreID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    * If ExistingByID:
        * DataStoreID (str, required): the ID of the DataStore to establish connection
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
        CommandParameterMetadata("File", type("")),
        CommandParameterMetadata("IfDataStoreIDExists", type(""))]

    # Choices for OpenMode, used to validate parameter and display in editor
    __choices_OpenMode = ["NEWBYPARAMETERS", "NEWBYFILE", "EXISTINGBYID"]

    # Choices for DatabaseDialect, used to validate parameter and display in editor
    __choices_DatabaseDialect = ["POSTGRESQL"]

    # Choices for IfDataStoreIDExists, used to validate parameter and display in editor
    __choices_IfDataStoreIDExists = ["REPLACE", "WARN", "FAIL", "REPLACEANDWARN"]

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

        # Check that the required parameter OpenMode is one of the acceptable value.
        pv_OpenMode = self.get_parameter_value(parameter_name="OpenMode", command_parameters=command_parameters)

        if not validators.validate_string_in_list(pv_OpenMode, self.__choices_OpenMode, True,
                                                  False, True):
            message = "OpenMode parameter value ({}) is not recognized.".format(pv_OpenMode)
            recommendation = "Specify one of the acceptable values ({}) for the OpenMode parameter.".format(
                self.__choices_OpenMode)
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Only continue if the first check was passed and the NewByParameters choice was selected.
        elif validators.validate_string_in_list(pv_OpenMode, ["NEWBYPARAMETERS"], True, False, True):

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
                        command_phase_type.INITIALIZATION,
                        CommandLogRecord(command_status_type.FAILURE, message, recommendation))

            # Check that optional IfDataStoreIDExists param is `Replace`, `Warn`, `Fail`, `ReplaceAndWarn` or None.
            pv_IfDataStoreIDExists = self.get_parameter_value(parameter_name="IfDataStoreIDExists",
                                                             command_parameters=command_parameters)

            if not validators.validate_string_in_list(pv_IfDataStoreIDExists, self.__choices_IfDataStoreIDExists,
                                                      none_allowed=True, empty_string_allowed=False, ignore_case=True):
                message = "IfDataStoreIDExists parameter value ({}) is not recognized.".format(pv_IfDataStoreIDExists)
                recommendation = "Specify one of the acceptable values ({}) for the IfDataStoreIDExists parameter.".\
                    format(self.__choices_IfDataStoreIDExists)
                warning += "\n" + message
                self.command_status.add_to_log(
                    command_phase_type.INITIALIZATION,
                    CommandLogRecord(command_status_type.FAILURE, message, recommendation))

            # Check that parameter DatabaseDialect is one of the acceptable values.
            pv_DatabaseDialect = self.get_parameter_value(parameter_name="DatabaseDialect",
                                                          command_parameters=command_parameters)

            if not validators.validate_string_in_list(pv_DatabaseDialect, self.__choices_DatabaseDialect, False, False,
                                                      True):
                message = "DatabaseDialect parameter value ({}) is not recognized.".format(pv_DatabaseDialect)
                recommendation = "Specify one of the acceptable values ({}) for the DatabaseDialect parameter.".format(
                    self.__choices_DatabaseDialect)
                warning += "\n" + message
                self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Only continue if the first check was passed and the NewByFile choice was selected.
        elif validators.validate_string_in_list(pv_OpenMode, ["NEWBYFILE"], False, False, True):

            # Check that the required parameter, File, is a non-empty, non-None string.
            pv_File = self.get_parameter_value(parameter_name="File", command_parameters=command_parameters)

            if not validators.validate_string(pv_File, False, False):
                message = "File has no value."
                recommendation = "Specify a valid value for the File parameter."
                warning += "\n" + message
                self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

            # Check that optional IfDataStoreIDExists param is `Replace`, `Warn`, `Fail`, `ReplaceAndWarn` or None.
            pv_IfDataStoreIDExists = self.get_parameter_value(parameter_name="IfDataStoreIDExists",
                                                              command_parameters=command_parameters)

            if not validators.validate_string_in_list(pv_IfDataStoreIDExists, self.__choices_IfDataStoreIDExists,
                                                      none_allowed=True, empty_string_allowed=False,
                                                      ignore_case=True):
                message = "IfDataStoreIDExists parameter value ({}) is not recognized.".format(
                    pv_IfDataStoreIDExists)
                recommendation = "Specify one of the acceptable values ({}) for the IfDataStoreIDExists parameter.". \
                    format(self.__choices_IfDataStoreIDExists)
                warning += "\n" + message
                self.command_status.add_to_log(
                    command_phase_type.INITIALIZATION,
                    CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Only continue if the first check was passed and the ExistingByID choice was selected.
        elif validators.validate_string_in_list(pv_OpenMode, ["EXISTINGBYID"], False, False, True):

            # Check that the required parameter, DataStoreID, is a non-empty, non-None string.
            pv_DataStoreID = self.get_parameter_value(parameter_name="DataStoreID",
                                                      command_parameters=command_parameters)

            if not validators.validate_string(pv_DataStoreID, False, False):
                message = "DataStoreID has no value."
                recommendation = "Specify a valid value for the DataStoreID parameter."
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

    def __should_open_datastore(self, open_mode, datastore_id, file_path_abs):
        """
            Checks the following:
                * the DataStore ID is unique if the NewByParameters mode is selected
                * the DataStore ID is unique if the NewByFile mode is selected
                * the File is a valid file if the NewByFile mode is selected
                * the DataStore ID is existing if the ExistingByID mode is selected

            Args:
                open_mode (str): The method used to open the DataStore.
                datastore_id (str): the ID of the DataStore to open/create
                file_path_abs (str): the absolute path the configuration file if the NewByFile mode is selected

            Returns:
                 Boolean. If TRUE, the  process should be run. If FALSE, it should not be run.
           """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the OpenMode is NewByParameters or NewByFile, continue with check.
        if open_mode.upper() == "NEWBYPARAMETERS" or open_mode.upper() == "NEWBYFILE":

            # If the DataStoreID is the same as an already-existing DataStoreID, raise a WARNING or FAILURE
            # (depends on the value of the IfDataStoreIDExists parameter.)
            should_run_command.append(validators.run_check(self, "IsDataStoreIdUnique", "DataStoreID", datastore_id,
                                                           None))

        # If the OpenMode is NewByFile, continue with check.
        if open_mode.upper() == "NEWBYFILE":

            # If the configuration file does not exists, raise a FAILURE.
            should_run_command.append(validators.run_check(self, "IsFilePathValid", "File", file_path_abs, "FAIL"))

        # If the OpenMode is ExistingByID, continue with check.
        if open_mode.upper() == "EXISTINGBYID":

            # If the DataStore ID is not an existing DataStore ID, raise a FAILURE.
            result = validators.run_check(self, "IsDataStoreIdExisting", "DataStoreID", datastore_id, "FAIL")
            should_run_command.append(result)

            # If the previous check passed, check If the DataStore is already connected. If it is, raise a FAILURE.
            if result is True:
                datastore_obj = self.command_processor.get_datastore(datastore_id)
                if datastore_obj.is_connected:

                    message = "The DataStoreID ({}) is already connected.".format(datastore_id)
                    recommendation = "Specify a DataStoreID that is not connected."

                    self.warning_count += 1
                    self.logger.error(message)
                    self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
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
        pv_OpenMode = self.get_parameter_value("OpenMode")
        pv_DatabaseDialect = self.get_parameter_value("DatabaseDialect")
        pv_DatabaseServer = self.get_parameter_value("DatabaseServer")
        pv_DatabaseName = self.get_parameter_value("DatabaseName")
        pv_DatabaseUser = self.get_parameter_value("DatabaseUser")
        pv_DatabasePassword = self.get_parameter_value("DatabasePassword")
        pv_DatabasePort = self.get_parameter_value("DatabasePort")
        pv_DataStoreID = self.get_parameter_value("DataStoreID", default_value=pv_DatabaseName)
        pv_File = self.get_parameter_value("File")

        # Expand for ${Property} syntax.
        pv_DatabaseServer = self.command_processor.expand_parameter_value(pv_DatabaseServer, self)
        pv_DatabaseName = self.command_processor.expand_parameter_value(pv_DatabaseName, self)
        pv_DatabaseUser = self.command_processor.expand_parameter_value(pv_DatabaseUser, self)
        pv_DatabasePassword = self.command_processor.expand_parameter_value(pv_DatabasePassword, self)

        # Convert the File parameter value relative path to an absolute path and expand for ${Property} syntax.
        if pv_File:
            pv_File = io_util.verify_path_for_os(io_util.to_absolute_path(
                self.command_processor.get_property('WorkingDir'), self.command_processor.expand_parameter_value(
                    pv_File, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_open_datastore(pv_OpenMode, pv_DataStoreID, pv_File):

            try:

                # If the OpenMode is set to NewByParameters, continue.
                if pv_OpenMode.upper() == "NEWBYPARAMETERS":

                    # Create a new DataStore object and assign the DataStore ID.
                    new_datastore = DataStore(pv_DataStoreID)

                    # Assign the DataBase URI for the appropriate DataBase dialect.
                    if pv_DatabaseDialect.upper() == "POSTGRESQL":

                        new_datastore.get_db_uri_postgres(pv_DatabaseServer, pv_DatabaseName, pv_DatabaseUser,
                                                          pv_DatabasePassword, pv_DatabasePort)

                    # Open a connection to the database and add the DataStore object to the GeoProcessor.
                    new_datastore.open_db_connection()
                    self.command_processor.add_datastore(new_datastore)

                # If the OpenMode is set to NewByFile, continue.
                elif pv_OpenMode.upper() == "NEWBYFILE":

                    print("WARNING: The NewByFile OpenMode is not currently enabled. Choose either the NewByParameters"
                          " or ExistingByID OpenMode.")

                # If the OpenMode is set to ExistingByID, continue.
                else:

                    # Get the DataStore obj from the ID and open the connection.
                    datastore_obj = self.command_processor.get_datastore(pv_DataStoreID)
                    datastore_obj.open_db_connection()

            # Raise an exception if an unexpected error occurs during the process.
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error opening DataStore {}.".format(pv_DataStoreID)
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
