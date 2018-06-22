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

from numpy import nan


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
    * Top (str, optional): Indicate how many rows to return. Default: return all rows. Must be a string representing
        a positive integer. Only enabled if DataStoreTable is enabled.
    * TableID (str, required): Identifier to assign to the output table in the GeoProcessor, which allows the table
        data to be used with other commands. A new table will be created. Can be specified with ${Property}.
    * IfTableIDExists (str, optional): This parameter determines the action that occurs if the TableID already exists
        within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    * IntNullHandleMethod (str, optional): pandas can't have nulls in an int column. Choose 1 of the following:
        - ToFloat: convert the column to a float data type
        - UseIntNullValue: use -9999 as the missing int value
        Default: ToFloat
    * IntNullValue (str, optional): Value used to represent null values when IntNullHandleMethod is set to
        UseIntNullValue Default: -9999999999
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("DataStoreID", type("")),
        CommandParameterMetadata("DataStoreTable", type("")),
        CommandParameterMetadata("Sql", type("")),
        CommandParameterMetadata("SqlFile", type("")),
        CommandParameterMetadata("Top", type("")),
        CommandParameterMetadata("TableID", type("")),
        CommandParameterMetadata("IfTableIDExists", type("")),
        CommandParameterMetadata("IntNullHandleMethod", type("")),
        CommandParameterMetadata("IntNullValue", type(""))]

    # Choices for IfTableIDExists, used to validate parameter and display in editor
    __choices_IfTableIDExists = ["Replace", "ReplaceAndWarn", "Warn", "Fail"]

    # Choices for IntNullHandleMethod, used to validate parameter and display in editor
    __choices_IntNullHandleMethod = ["ToFloat", "UseIntNullValue"]

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

        # Run the checks for the Top parameter.
        pv_Top = self.get_parameter_value(parameter_name='Top', command_parameters=command_parameters)
        pv_DataStoreTable = self.get_parameter_value(parameter_name="DataStoreTable",
                                                     command_parameters=command_parameters)
        if pv_Top:

            # Check that the Top parameter is only used with the DataStoreTable selection.
            if is_string_list.count(True) == 1 and not pv_DataStoreTable:

                message = "The Top parameter is only valid when the DataStoreTable is enabled. The Top parameter" \
                          " value ({}) will be ignored.".format(pv_Top)
                recommendation = "To use the Top parameter, specify a value for the DataStoreTable parameter."
                self.command_status.add_to_log(
                    command_phase_type.INITIALIZATION,
                    CommandLogRecord(command_status_type.WARNING, message, recommendation))

            # If the DataStoreTable parameter is enabled, check that the Top parameter is an integer or None.
            if pv_DataStoreTable and not validators.validate_int(pv_Top, True, False):

                message = "Top parameter value ({}) is not a valid integer value.".format(pv_Top)
                recommendation = "Specify a positive integer for the Top parameter to specify how many rows to return."
                warning += "\n" + message
                self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

            # If the DataStoreTable parameter is enabled, check that the Top parameter is positive.
            elif pv_DataStoreTable and not int(pv_Top) > 0:

                message = "Top parameter value ({}) is not a positive, non-zero integer value.".format(pv_Top)
                recommendation = "Specify a positive integer for the Top parameter to specify how many rows to return."
                warning += "\n" + message
                self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Run the checks for the IntNullValue parameter.
        pv_IntNullValue = self.get_parameter_value(parameter_name='IntNullValue', command_parameters=command_parameters)

        if pv_IntNullValue:

            # Check that the IntNullValue parameter is only used with the DataStoreTable selection.
            if is_string_list.count(True) == 1 and not pv_DataStoreTable:
                message = "The IntNullValue parameter is only valid when the DataStoreTable is enabled. The" \
                          " IntNullValue parameter value ({}) will be ignored.".format(pv_IntNullValue)
                recommendation = "To use the IntNullValue parameter, specify a value for the DataStoreTable parameter."
                self.command_status.add_to_log(
                    command_phase_type.INITIALIZATION,
                    CommandLogRecord(command_status_type.WARNING, message, recommendation))

            # If the DataStoreTable parameter is enabled, check that the IntNullValue parameter is an integer or None.
            if pv_DataStoreTable and not validators.validate_int(pv_IntNullValue, True, False):
                message = "IntNullValue parameter value ({}) is not a valid integer value.".format(pv_IntNullValue)
                recommendation = "Specify an integer for the IntNullValue parameter."
                warning += "\n" + message
                self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                               CommandLogRecord(command_status_type.FAILURE, message,
                                                                recommendation))

        # Check that optional parameter IfTableIDExists is one of the acceptable values or is None.
        pv_IfTableIDExists = self.get_parameter_value(parameter_name="IfTableIDExists",
                                                      command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_IfTableIDExists, self.__choices_IfTableIDExists, none_allowed=True,
                                                  empty_string_allowed=False, ignore_case=True):
            message = "IfTableIDExists parameter value ({}) is not recognized.".format(pv_IfTableIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfTableIDExists parameter.".format(
                self.__choices_IfTableIDExists)
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that optional parameter IntNullHandleMethod is one of the acceptable values or is None.
        pv_IntNullHandleMethod = self.get_parameter_value(parameter_name="IntNullHandleMethod",
                                                          command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_IntNullHandleMethod, self.__choices_IntNullHandleMethod,
                                                  none_allowed=True, empty_string_allowed=False, ignore_case=True):
            message = "IntNullHandleMethod parameter value ({}) is not recognized.".format(pv_IntNullHandleMethod)
            recommendation = "Specify one of the acceptable values ({}) for the IntNullHandleMethod parameter.".format(
                self.__choices_IntNullHandleMethod)
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

    def __should_read_table(self, sql_file_abs, table_id, datastore_id):
        """
        Checks the following:
            * the SqlFile (absolute) is a valid file, if not None
            * the ID of the Table is unique (not an existing Table ID)
            * the DataStore exists

        Args:
            sql_file_abs (str): the full pathname to the sql file
            table_id (str): the ID of the output Table
            datastore_id (str): the ID of the DataStore to read

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

        # If the DataStore ID is not an existing DataStore ID, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsDataStoreIdExisting", "DataStoreID", datastore_id,
                                                       "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def __create_sql_statement(self, datastore_obj, datastore_table):

        # Get the IntNullHandleMethod and the IntNullValue parameter values.
        pv_IntNullHandleMethod = self.get_parameter_value("IntNullHandleMethod", default_value="ToFloat").upper()
        pv_IntNullValue = self.get_parameter_value("IntNullValue", default_value="-9999999999")

        # If the IntNullHandleMethod is set to ToFloat, use the simple form of the Sql statement. The Pandas library
        # will automatically convert int columns with null values to float columns.
        if pv_IntNullHandleMethod == "TOFLOAT":
            sql_statement = "SELECT * from {}".format(datastore_table)

        # If the IntNullHandleMethod is set to UseIntNullValue, create the appropriate Sql statement.
        else:

            # Get a list of all columns in the DataStore table.
            all_cols = datastore_obj.return_col_names(datastore_table)

            # Get a list of the integer-type columns in the DataStore table.
            int_cols = datastore_obj.return_int_col_names(datastore_table)

            # Get a list of the non integer-type columns in the DataStore table.
            non_int_cols = [col for col in all_cols if col not in int_cols]

            # If there are columns that hold integer data, create the COALESCE portion of the SQL statement.
            if int_cols:

                # Iterate over each of the integer columns.
                for i in range(len(int_cols)):

                    # Add the initial statement if this is the first time through the for loop.
                    if i == 0:
                        coalesce_statement = "COALESCE("

                    # Add the details of the integer column to the coalesce statement.
                    coalesce_statement += "{}, {}) as {}".format(int_cols[i], pv_IntNullValue, int_cols[i])

                    # Add the initial statement for the next coalesce statement, if this is not the last time through
                    # the loop.
                    if not i == len(int_cols) - 1:
                        coalesce_statement += ", COALESCE("

                # If there are non-integer columns, continue.
                if non_int_cols:

                    # Create the non-integer portion of the SQL statement.
                    non_int_cols_statement = ", ".join(non_int_cols)

            # Combine the SQL statement portions to create a final and complete SQL statement.

            # If there are columns representing integers and columns representing non-integers.
            if int_cols and non_int_cols:
                sql_statement = "SELECT {}, {} from {}".format(non_int_cols_statement, coalesce_statement,
                                                               datastore_table)

            # If there are only columns representing integers.
            elif int_cols:
                sql_statement = "SELECT {} from {}".format(coalesce_statement, datastore_table)

            # If there are no columns representing integers.
            else:
                sql_statement = "SELECT * from {}".format(datastore_table)

        # Return the SQL statement.
        return sql_statement

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
        pv_Top = self.get_parameter_value("Top")
        pv_TableID = self.get_parameter_value("TableID")
        pv_IntNullHandleMethod = self.get_parameter_value("IntNullHandleMethod", default_value="ToFloat").upper()
        pv_IntNullValue = self.get_parameter_value("IntNullValue", default_value="-9999999999")

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
        if self.__should_read_table(pv_SqlFile, pv_TableID, pv_DataStoreID):

            try:

                # Get the DataStore object
                datastore = self.command_processor.get_datastore(pv_DataStoreID)

                # If using the Sql method, the sql_statement is the user-provided sql statement.
                if pv_Sql:

                    sql_statement = pv_Sql
                    if '%' in sql_statement:
                        sql_statement = sql_statement.replace('%', '%%')

                # If using the DataStoreTable method, the sql_statement selects * from the specified table.=
                elif pv_DataStoreTable:

                    sql_statement = self.__create_sql_statement(datastore, pv_DataStoreTable)

                    # If specified, only query the top n rows.
                    if pv_Top:
                        sql_statement += " limit {}".format(pv_Top)

                # If using the SqlFile method, the sql_statement in read from the provided file.
                else:

                    # Get the SQL statement from the file.
                    f = open(pv_SqlFile, 'r')
                    sql_statement = f.read().strip()

                # Create a Pandas data frame from the selected DataStore data.
                df = pandas_util.create_data_frame_from_datastore_with_sql(sql_statement, datastore)

                df.fillna(value=nan, inplace=True)
                import pandas
                print(pandas.isna(df.receive_lines))

                # Create a Table object from the pandas data frame.
                table_obj = Table(pv_TableID, df, "DataStore ({})".format(pv_DataStoreID))

                # If an IntNullValue was used, assign the value to the Table property.
                if pv_IntNullHandleMethod == "USEINTNULLVALUE":
                    table_obj.int_null_value = pv_IntNullValue

                # Add the table to the geoprocessor's Tables list.
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