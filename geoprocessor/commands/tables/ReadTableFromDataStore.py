# ReadTableFromDataStore

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.Table import Table
from geoprocessor.core.Table import TableField
from geoprocessor.core.Table import TableRecord

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validators

import logging
import sqlalchemy


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
    * IncludeColumns (str, optional): A list of glob-style patterns to determine the DataStore table columns
        to read. Default: * (All columns are read).
    * ExcludeColumns (str, optional): A list of glob-style patterns to determine the DataStore table columns
        to read. Default: '' (No columns are excluded - All columns are read).
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
        CommandParameterMetadata("Top", type("")),
        CommandParameterMetadata("IncludeColumns", type("")),
        CommandParameterMetadata("ExcludeColumns", type("")),
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
        self.command_name = "ReadTableFromDataStore"
        self.command_description = "Read a table from a DataStore"
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

    @staticmethod
    def __read_table_from_datastore(ds, table_name, table_id, top, sql, cols_to_include, cols_to_exclude):
        """
        Creates a GeoProcessor table object from a DataStore table.

        Args:
            ds (obj): the DataStore object that contains the DataStore table to read
            table_name (str): the name of the DataStore table to read
                Can be None if using the Sql method or SqlFile method.
            table_id (str): the id of the GeoProcessor Table that is to be created
            top (int): the number of rows from the DataStore Table to read
                Can be None if using the Sql method or SqlFile method.
            sql (str): the SQL statement to select out the desired data from the DataStore table.
                Can be None if using the DataStoreTable method.
            cols_to_include (list): a list of glob-style patterns representing the DataStore Table columns to read
                Can be None if using the Sql method or SqlFile method.
            cols_to_exclude (list): a list of glob-style patterns representing the DataStore Table columns to read
                Can be None if using the Sql method or SqlFile method.

        Return: A GeoProcessor Table object.
        """

        # Create a GeoProcessor Table object.
        table = Table(table_id)

        # If a SQL statement has been specified, then continue.
        if sql:

            # Run the SQL statement
            result_from_sql = ds.connection.execute(sql)

            # Get the columns from the sql statement.
            table_cols = ds.connection.execute(sql).keys()

            # Get the first row from the result set.
            row = result_from_sql.fetchone()

            # An empty list to hold the columns that were included in the result set in response to the user-specified
            # sql.
            included_cols = []

            # Iterate over all of the available columns in the DataStore table.
            for table_col in table_cols:

                # Try to read the value of the DataStore table column. If it does not throw an error, it is known that
                # the column was included in the result set of the user-specified SQL statement. Add the column name to
                # the included_cols list.
                try:
                    value = row[table_col]
                    included_cols.append(table_col)

                # If an error is thrown, it is known that the column was not included in the result set of the
                #  user-specified SQL statement. Do not add the column name to the included_cols list.
                except:
                    pass

            # Iterate over the DataStore table columns that do have results from the user-specified SQL statement.
            for included_col in included_cols:

                # Create a TableField object and assign the field "name" as the column name.
                table_field = TableField(included_col)

                # Run the SQL statement
                result_from_sql = ds.connection.execute(sql)

                # Iterate over the rows of the DataStore table data.
                for row in result_from_sql:
                    # Add the row data for the column to the item list of the TableField.
                    table_field.items.append(row[included_col])

                # Determine the data type of the column's data.
                # A list that holds the data type for each data value in the column.
                data_types = []

                # Iterate over each of the data values in the column.
                for item in table_field.items:

                    # Add the data type of the item to the data_types list. Ignore data values that are None.
                    if item is not None:
                        data_types.append(type(item))

                # If the data_types list is empty, assume that all values in the column are set to None.
                if not data_types:
                    table_field.data_type = None

                # Set the data_type attribute of the TableField object to that specified in the data_types list.
                elif all(x == data_types[0] for x in data_types):
                    table_field.data_type = data_types[0]

                # All of the data types in the list should be the same value because database columns require that
                # the data in each column is only one data type. If more than one data type exists in the data_types
                # list, print an error message.
                else:
                    print("There was an error. Not all the data types are the same.")

                # Add the TableField object to the Table attributes.
                table.add_table_field(table_field)

                # Get the number of row entries in the TableField. This will be the same number for each of the
                # TableField objects so only the count of the entries in the last TableField object is used in the
                # remaining code.
                table.entry_count = len(table_field.items)

        # If a SQL statement has not been specified, continue.
        else:

            # Read the DataStore table into a DataStore Table object.
            ds_table_obj = ds.metadata.tables[table_name]

            # Query the DataStore table. The allows access to table information.
            q = ds.session.query(ds_table_obj)

            # Select all fields and rows of the table.
            s = sqlalchemy.sql.select([ds_table_obj])

            # Get a list of all of the column names.
            table_cols = [col["name"] for col in q.column_descriptions]

            # Sort the list of column names to create create a second list that only includes the columns to read.
            table_cols_to_read = string_util.filter_list_of_strings(table_cols, cols_to_include, cols_to_exclude, True)

            # Sort the table_cols_to_read list to order in the same order as the table columns in the DataStore table.
            cols_names = ds.return_col_names(table_name)
            table_cols_to_read = [col_name for col_name in cols_names if col_name in table_cols_to_read]

            # Iterate over the column names to read.
            for col in table_cols_to_read:

                # Create a TableField object and assign the field "name" as the column name.
                table_field = TableField(col)

                # Run the SQL query to get the DataStore tables' data. Save as result variable.
                result = ds.connection.execute(s)

                # If configured to limit the table read to a specified number of top rows, continue.
                if top:

                    # Counter to track the number of rows read into the Table Field items.
                    count = 0

                    # Iterate over the rows of the DataStore table data.
                    for row in result:

                        # If the current row count is less than the desired row count, continue.
                        while count < top:
                            # Add the row data for the column to the item list of the TableField. Increase the counter.
                            table_field.items.append(row[col])
                            count += 1

                # If configured to read all rows of the DataStore table, continue.
                else:

                    # Iterate over the rows of the DataStore table data.
                    for row in result:
                        # Add the row data for the column to the item list of the TableField.
                        table_field.items.append(row[col])

                # Determine the data type of the column's data.
                # A list that holds the data type for each data value in the column.
                data_types = []

                # Iterate over each of the data values in the column.
                for item in table_field.items:

                    # Add the data type of the item to the data_types list. Ignore data values that are None.
                    if item is not None:
                        data_types.append(type(item))

                # If the data_types list is empty, assume that all values in the column are set to None.
                if not data_types:
                    table_field.data_type = None

                # Set the data_type attribute of the TableField object to that specified in the data_types list.
                elif all(x == data_types[0] for x in data_types):
                    table_field.data_type = data_types[0]

                # All of the data types in the list should be the same value because database columns require that the
                # data in each column is only one data type. If more than one data type exists in the data_types list,
                # print an error message.
                else:
                    print("There was an error. Not all the data types are the same.")

                # Add the TableField object to the Table attributes.
                table.add_table_field(table_field)

                # Get the number of rows in the TableField. This will be the same number for each of the TableField
                # objects so only the count of the entries in the last TableField object is used in the remaining code.
                table.entry_count = len(table_field.items)

        # Iterate over the number of row entries.
        for i_row in range(table.entry_count):

            # Create a TableRecord object.
            table_record = TableRecord()

            # Iterate over the table fields.
            for i_col in range(len(table.table_fields)):

                # Get the data value for the specified row and the specified field.
                new_item = table.table_fields[i_col].items[i_row]

                # Assign that data value to the items list of the TableRecord.
                table_record.add_item(new_item)

            # Add the TableRecord object to the Table attributes.
            table.table_records.append(table_record)

        # Return the GeoProcessor Table object.
        return table

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
        pv_IncludeColumns = self.get_parameter_value("IncludeColumns", default_value="*")
        pv_ExcludeColumns = self.get_parameter_value("ExcludeColumns", default_value="")

        # Expand for ${Property} syntax.
        pv_DataStoreID = self.command_processor.expand_parameter_value(pv_DataStoreID, self)
        pv_DataStoreTable = self.command_processor.expand_parameter_value(pv_DataStoreTable, self)
        pv_Sql = self.command_processor.expand_parameter_value(pv_Sql, self)
        pv_TableID = self.command_processor.expand_parameter_value(pv_TableID, self)

        # Convert the IncludeColumns and ExcludeColumns parameter values to lists.
        cols_to_include = string_util.delimited_string_to_list(pv_IncludeColumns)
        cols_to_exclude = string_util.delimited_string_to_list(pv_ExcludeColumns)

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

                # Set the SQL statement to None until proof that SQL statement exists.
                sql_statement = None

                # If using the Sql method, the sql_statement is the user-provided sql statement.
                if pv_Sql:

                    sql_statement = pv_Sql
                    if '%' in sql_statement:
                        sql_statement = sql_statement.replace('%', '%%')

                # If using the Sql method, the sql_statement is the user-provided sql statement within a file.
                if pv_SqlFile:

                    # Get the SQL statement from the file.
                    f = open(pv_SqlFile, 'r')
                    sql_statement = f.read().strip()
                    if '%' in sql_statement:
                        sql_statement = sql_statement.replace('%', '%%')

                # Create the Table from the DataStore.
                table = self.__read_table_from_datastore(datastore, pv_DataStoreTable, pv_TableID, pv_Top,
                                                         sql_statement, cols_to_include, cols_to_exclude)

                # Add the table to the GeoProcessor's Tables list.
                self.command_processor.add_table(table)

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