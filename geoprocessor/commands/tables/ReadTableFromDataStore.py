# ReadTableFromDataStore

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.Table import Table

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.pandas_util as pandas_util
import geoprocessor.util.validator_util as validators

import logging


class ReadTableFromDataStore(AbstractCommand):
    """
    Reads a Table from a DataStore object.

    Command Parameters
    * DataStoreID (str, required): The id of a database datastore to read. ${Property} syntax is recognized.
    * DataStoreTable (str, optional): The name of the database table to read when querying a single table or view. Can
        use ${Property} notation to insert processor property values. If specified, do not specify Sql or SqlFile.
    * Sql(str, optional): The SQL string that will be used to query the database, optionally using ${Property} notation
        to insert processor property values. If specified, do not specify DataStoreTable or SqlFile.
    * SqlFile(str, optional): The name of the file containing an SQL string to execute, optionally using ${Property}
        notation in the SQL file contents to insert processor property values. If specified, do not specify
        DataStoreTable or Sql.
    * TableID (str, required): Identifier to assign to the output table in the GeoProcessor, which allows the table
        data to be used with other commands. A new table will be created. Can be specified with ${Property}.
    * IfTableIDExists (str, optional): This parameter determines the action that occurs if the TableID already exists
        within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("DataStoreID", type("")),
        CommandParameterMetadata("DataStoreTable", type("")),
        CommandParameterMetadata("Sql", type("")),
        CommandParameterMetadata("SqlFile", type("")),
        CommandParameterMetadata("TableID", type("")),
        CommandParameterMetadata("IfTableIDExists", type(""))]

    # Choices for IfTableIDExists, used to validate parameter and display in editor
    __choices_IfTableIDExists = ["Replace", "ReplaceAndWarn", "Warn", "Fail"]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "ReadTableFromDelimitedFile"
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

        # Check that parameter TableID is a non-empty, non-None string.
        pv_TableID = self.get_parameter_value(parameter_name='TableID', command_parameters=command_parameters)

        if not validators.validate_string(pv_TableID, False, False):
            message = "TableID parameter has no value."
            recommendation = "Specify the TableID parameter to indicate the Table to write."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that parameter DataStoreID is a non-empty, non-None string.
        pv_DataStoreID = self.get_parameter_value(parameter_name='DataStoreID', command_parameters=command_parameters)

        if not validators.validate_string(pv_DataStoreID, False, False):
            message = "DataStoreID parameter has no value."
            recommendation = "Specify the DataStoreID parameter (relative or absolute pathname) to indicate the " \
                             "location and name of the output delimited file."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that one (and only one) selection method is a non-empty and non-None string.
        is_string_list = []
        selection_method_parameter_list = ["Sql", "SqlFile", "DataStoreTable"]

        for parameter in selection_method_parameter_list:

            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)
            is_string_list.append(validators.validate_string(parameter_value, False, False))

        if not is_string_list.count(True) == 1:
            message = "Must enable one (and ONLY one) of the following parameters: {}".format(
                selection_method_parameter_list)
            recommendation = "Specify the value for one (and ONLY one) of the following parameters: {}".format(
                selection_method_parameter_list)
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that optional parameter IfTableIDExists is one of the acceptable values or is None.
        pv_IfTableIDExists = self.get_parameter_value(parameter_name="IfTableIDExists",
                                                      command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_IfTableIDExists, self.__choices_IfTableIDExists, none_allowed=True,
                                                  empty_string_allowed=True, ignore_case=True):
            message = "IfTableIDExists parameter value ({}) is not recognized.".format(pv_IfTableIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfTableIDExists parameter.".format(
                self.__choices_IfTableIDExists)
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

    def __should_read_table(self, sql_file_abs, table_id):
        """
        Checks the following:
            * the SqlFile (absolute) is a valid file, if not None
            * the ID of the Table is unique (not an existing Table ID)

        Args:
            sql_file_abs (str): the full pathname to the sql file
            table_id (str): the ID of the output Table

        Returns:
             Boolean. If TRUE, the reading process should be run. If FALSE, it should not be run.
       """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # Only run following check if SqlFile method is being used.
        if sql_file_abs:

            # If the SqlFile is not a valid file path, raise a FAILURE.
            should_run_command.append(validators.run_check(self, "IsFilePathValid", "SqlFile", sql_file_abs, "FAIL"))

        # If the TableID is the same as an already-existing TableID, raise a WARNING or FAILURE (depends on the
        # value of the IfTableIDExists parameter.)
        should_run_command.append(validators.run_check(self, "IsTableIdUnique", "TableID", table_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self):
        """
        Run the command. Read the Table from the DataStore

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_DataStoreID = self.get_parameter_value("DataStoreID")
        pv_DataStoreTable = self.get_parameter_value("DataStoreTable")
        pv_Sql = self.get_parameter_value("Sql")
        pv_SqlFile = self.get_parameter_value("SqlFile")
        pv_TableID = self.get_parameter_value("TableID")

        # Expand for ${Property} syntax.
        pv_DataStoreID = self.command_processor.expand_parameter_value(pv_DataStoreID, self)
        pv_DataStoreTable = self.command_processor.expand_parameter_value(pv_DataStoreTable, self)
        pv_Sql = self.command_processor.expand_parameter_value(pv_Sql, self)
        pv_TableID = self.command_processor.expand_parameter_value(pv_TableID, self)

        # If available, convert the SqlFile parameter value relative path to an absolute path and expand for
        # ${Property} syntax.
        if pv_SqlFile:
            pv_SqlFile = io_util.verify_path_for_os(io_util.to_absolute_path(
                self.command_processor.get_property('WorkingDir'),
                self.command_processor.expand_parameter_value(pv_SqlFile, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_read_table(pv_SqlFile, pv_TableID):

            try:

                # Get the DataStore object
                datastore = self.command_processor.get_datastore(pv_DataStoreID)

                # If using the Sql method, the sql_statement is the user-provided sql statement.
                if pv_Sql:
                    sql_statement = pv_Sql

                # If using the DataStoreTable method, the sql_statement selects * from the specified table.
                elif pv_DataStoreTable:
                    sql_statement = "select * from {}".format(pv_DataStoreTable)

                # If using the SqlFile method, the sql_statement in read from the provided file.
                else:

                    # Get the SQL statement from the file.
                    f = open(pv_SqlFile, 'r')
                    sql_statement = f.read().strip()

                # Create a Pandas data frame from the selected DataStore data.
                df = pandas_util.create_data_frame_from_datastore_with_sql(datastore, sql_statement)

                # Create a Table object from the pandas data frame and add it to the geoprocessor's Tables list.
                table_obj = Table(pv_TableID, df, "DataStore ({})".format(pv_DataStoreID))
                self.command_processor.add_table(table_obj)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error reading Table {} from DataStore ({}).".format(pv_TableID,
                                                                                          pv_DataStoreID)
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