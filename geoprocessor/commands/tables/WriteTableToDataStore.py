# WriteTableToDataStore

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type


import geoprocessor.util.command_util as command_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validators

import logging
import psycopg2.extras


class WriteTableToDataStore(AbstractCommand):
    """
    Writes a Table to a DataStore object.

    Command Parameters
    * TableID (str, required): Identifier for table to write. Can be specified with ${Property}.
    * IncludeColumns (str, optional) A comma-separated list of the glob-style patterns filtering which table columns to
        write.
    * ExcludeColumns (str, optional) A comma-separated list of the glob-style patterns filtering which table columns to
        NOT write. This will override IncludeColumns.
    * DataStoreID (str, required): The id of a DataStore to receive data. ${Property} syntax is recognized.
    * DataStoreTable (str, required): The name of the DataStore table to receive data. ${Property} syntax is recognized.
    * ColumnMap (str, optional): A dictionary indicating which columns in TableID have different names in DataStore
        Table, using the syntax: ColumnName:DatastoreTableName, ColumnName:DatastoreTableName,...
        Default: DataStore TableName columns are assumed to match the column names in TableID.
    * DataStoreRelatedColumnsMap (str, optional):
    * WriteMode (str, optional): The method used to write data, recognizing the databases use insert and update SQL
        statements, one of: DeleteInsert, Insert, InsertUpdate, Update, or UpdateInsert
        Default: InsertUpdate
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("TableID", type("")),
        CommandParameterMetadata("IncludeColumns", type("")),
        CommandParameterMetadata("ExcludeColumns", type("")),
        CommandParameterMetadata("DataStoreID", type("")),
        CommandParameterMetadata("DataStoreTable", type("")),
        CommandParameterMetadata("ColumnMap", type("")),
        CommandParameterMetadata("DataStoreRelatedColumnsMap", type("")),
        CommandParameterMetadata("WriteMode", type(""))]

    # Choices for WriteMode, used to validate parameter and display in editor
    __choices_WriteMode = ["DeleteInsert", "Insert", "InsertUpdate", "Update", "UpdateInsert"]

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

        # Check that the required parameters are non-empty, non-None strings.
        required_parameters = ["TableID", "DataStoreID", "DataStoreTable"]

        for parameter in required_parameters:

            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)
            if not validators.validate_string(parameter_value, False, False):
                message = "{} parameter has no value.".format(parameter)
                recommendation = "Specify a valid value for the {} parameter.".format(parameter)
                warning += "\n" + message
                self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that optional parameter WriteMode is one of the acceptable values or is None.
        pv_WriteMode = self.get_parameter_value(parameter_name="WriteMode",
                                                command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_WriteMode, self.__choices_WriteMode, none_allowed=True,
                                                  empty_string_allowed=False, ignore_case=True):
            message = "WriteMode parameter value ({}) is not recognized.".format(pv_WriteMode)
            recommendation = "Specify one of the acceptable values ({}) for the WriteMode parameter.".format(
                self.__choices_WriteMode)
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

    @staticmethod
    def __get_table_cols_to_write(include_col_patterns, exclude_col_patterns, table):
        """
        The command allows for users to select a subset of the Table columns to write to the DataStore database. This
        function returns a list of Table columns configured to write data by the user inputs.

        Args:
            include_col_patterns (str): A comma-separated list of the glob-style patterns filtering which table columns
                to write.
            exclude_col_patterns (str): A comma-separated list of the glob-style patterns filtering which table columns
                to NOT write. This will override IncludeColumns.
            table (obj): the Table that is being written to the DataStore

        Return:
            A list of Table column names configured to write data.
        """

        # Convert the IncludeColumns and the ExcludeColumns parameters from strings to lists
        table_cols_to_include_patterns = string_util.delimited_string_to_list(include_col_patterns)
        table_cols_to_exclude_patterns = string_util.delimited_string_to_list(exclude_col_patterns)

        # Get a list of all of the columns in the Table
        all_table_cols = table.get_column_names()

        # Get a list of the columns in the Table that are configured to be pushed to the DataStore
        table_cols_to_include = string_util.filter_list_of_strings(all_table_cols, table_cols_to_include_patterns,
                                                                   table_cols_to_exclude_patterns)

        # Return a list of Table column names configured to write data.
        return table_cols_to_include

    @staticmethod
    def __get_mapped_datastore_col_from_table_col(table_col_name, col_map_dic):
        """
        Get the corresponding DataStore table column name given the Table column name. This is achieved by looking up
        the corresponding values in the user-configured ColumnMap.

        Args:
            table_col_name (str): the name of the Table column
            col_map_dic (dic): a dictionary mapping the Table columns to the DataStore table columns
                Key: Table column ---> Value: DataStore table column

        Return: The corresponding DataStore table column name.
        """

        # If the Table column name is registered in the ColumnMap, return the corresponding DataStore table column name.
        if table_col_name in col_map_dic.keys():
            return col_map_dic[table_col_name]

        # If the Table column name is not registered in the ColumnMap, assume the Table column name directly maps to a
        # DataStore table column name. Return the Table column name.
        else:
            return table_col_name

    @staticmethod
    def __get_datatype_of_database_col(datastore, datastore_table_name, col_name):
        """
        Get the DataType of the PostGreSql DataStore table column.

        datastore (obj): the DataStore that is receiving the data
        datastore_table_name (str): the name of the DataStore table that is receiving the data
        col_name (str): the name of the column to determine data type

        Return: The PostGreSql DataType for the input column.
        """

        # For comments, see the following reference.
        # REF: https://stackoverflow.com/questions/27832289/postgresql-how-do-you-get-the-column-formats
        cur = datastore.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql_statement = """select * from information_schema.columns where table_schema NOT IN ('information_schema',
         'pg_catalog') AND table_name IN ('{}') AND column_name IN ('{}')""".format(datastore_table_name, col_name)
        cur.execute(sql_statement)
        for cur_row in cur:
            db_datatype = cur_row['data_type']
            return db_datatype

    def __get_datastore_cols_to_receive(self, table_cols_to_write, col_map_dic):
        """
        Get a list of the columns in the DataStore that are configured to receive data.

        Args:
            table_cols_to_write: a list of Table column names that are configured to write data
            col_map_dic (dic): a dictionary mapping the Table columns to the DataStore table columns
                Key: Table column ---> Value: DataStore table column

        Return: A list of DataBase table columns that are expected to receive data.
        """

        # Get a list of the columns in the DataStore that are configured to receive data.
        datastore_table_cols_to_receive = []

        # Iterate over the Table Columns to Write
        for table_col_to_include in table_cols_to_write:

            # Get the corresponding DataStore table column name, as configured with user input in the ColumnMap.
            corresponding_datastore_table_col_name = self.__get_mapped_datastore_col_from_table_col(
                table_col_to_include, col_map_dic)

            # Add corresponding DataStore table column name to the master list.
            datastore_table_cols_to_receive.append(corresponding_datastore_table_col_name)

        # Return the list of the columns in the DataStore that are configured to receive data.
        return datastore_table_cols_to_receive

    def __should_write_table(self, table_id, datastore_id, datastore_table_name):
        """
        Checks the following:
            * the Table ID exists
            * the DataStore ID exists
            * the DataStore table exists

        Args:
            table_id (str): the ID of the Table to write
            datastore_id (str): the ID of the DataStore to receive data
            datastore_table_name (str): the name of the DataStore table to receive data

        Returns:
             Boolean. If TRUE, the process should be run. If FALSE, it should not be run.
       """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the DataStore ID is not an existing DataStore ID, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsDataStoreIdExisting", "DataStoreID", datastore_id,
                                                       "FAIL"))

        # Only run the following check if the previous check passed.
        if False not in should_run_command:

            # If the DataStoreTable is not a table within the DataStore, raise a FAILURE.
            should_run_command.append(validators.run_check(self, "IsTableInDataStore", "DataStoreTable",
                                                           datastore_table_name, "FAIL", other_values=[datastore_id]))

        # If the Table ID is not an existing Table ID, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsTableIdExisting", "TableID", table_id, "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def __should_write_table2(self, datastore, datastore_table_name, datastore_table_cols_to_receive):
        """
            Checks the following:
                * the datastore columns configured to receive data are existing columns within the DataStore table

            Args:
                datastore (obj): the DataStore that is receiving the data
                datastore_table_name (str): the name of the DataStore table that is receiving the data
                datastore_table_cols_to_receive (list of strings):  A list of DataBase table columns that are expected
                    to receive data.

            Returns:
                 Boolean. If TRUE, the process should be run. If FALSE, it should not be run.
           """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        invalid_columns = []

        # Get the DataStore Table columns
        datastore_table_cols = datastore.get_list_of_columns(datastore_table_name)

        for datastore_table_col_to_receive in datastore_table_cols_to_receive:
            if datastore_table_col_to_receive not in datastore_table_cols:
                invalid_columns.append(datastore_table_col_to_receive)

        if invalid_columns:
            message = "One or more of the DataStore columns configured to be edited do(es) not exist in the DataStore" \
                      " table ({}). The invalid columns are: \n({}).".format(datastore_table_name, invalid_columns)
            recommendation = "Specify valid DataStore columns to edit."

            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                    message, recommendation))
            should_run_command.append(False)

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            self.warning_count += 1
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
        pv_TableID = self.get_parameter_value("TableID")
        pv_IncludeColumns = self.get_parameter_value("IncludeColumns", default_value="*")
        pv_ExcludeColumns = self.get_parameter_value("ExcludeColumns", default_value="''")
        pv_DataStoreID = self.get_parameter_value("DataStoreID")
        pv_DataStoreTable = self.get_parameter_value("DataStoreTable")
        pv_ColumnMap = self.get_parameter_value("ColumnMap", default_value="")
        pv_DataStoreRelatedColumnsMap = self.get_parameter_value("DataStoreRelatedColumnsMap")
        pv_WriteMode = self.get_parameter_value("WriteMode", default_value="InsertUpdate")

        # Expand for ${Property} syntax.
        pv_TableID = self.command_processor.expand_parameter_value(pv_TableID, self)
        pv_DataStoreID = self.command_processor.expand_parameter_value(pv_DataStoreID, self)
        pv_DataStoreTable = self.command_processor.expand_parameter_value(pv_DataStoreTable, self)

        # Convert the ColumnMap from string to a dictionary. Key: Table Column Name; Value: DataStore Column Name
        col_map_dic = string_util.delimited_string_to_dictionary_one_value(pv_ColumnMap, ",", ":", True)

        # Run the checks on the parameter values. Only continue if the checks pass.
        if self.__should_write_table(pv_TableID, pv_DataStoreID, pv_DataStoreTable):

            # Get the Table object
            table_obj = self.command_processor.get_table(pv_TableID)

            # Get DataStore object
            datastore_obj = self.command_processor.get_datastore(pv_DataStoreID)

            # Get the list of the columns in the Table that are configured to write.
            table_cols_to_write = self.__get_table_cols_to_write(pv_IncludeColumns, pv_ExcludeColumns, table_obj)

            # Get the list of the columns in the DataStore that are configured to receive data.
            datastore_table_cols_to_receive = self.__get_datastore_cols_to_receive(table_cols_to_write, col_map_dic)

            # Run a second level of checks. Only continue if the check passes.
            if self.__should_write_table2(datastore_obj, pv_DataStoreTable, datastore_table_cols_to_receive):

                try:

                    # A Sql statement is used to insert data into a DataBase table. One portion of the Sql statement
                    # includes the data values that are to be entered. The values_str_master holds that portion the Sql
                    # statement as a string value. String values from each Table row are appended to this master string.
                    values_str_master = ""

                    # Iterate over the rows in the Table.
                    for index, row in table_obj.df.iterrows():

                        # A Sql statement is used to insert data into a DataBase table. One portion of the Sql statement
                        # includes the database table columns that will receive the data. The cols_str holds that
                        # portion of the Sql statement as a string. Refreshes for each table row.
                        cols_str = ""

                        # A Sql statement is used to insert data into a DataBase table. One portion of the Sql statement
                        # includes the data values that are to be entered. The values_str_row holds that portion the
                        # Sql statement as a string value FOR the current row. The values_str_row is then appended to
                        # the values_str_master for each row. Refreshes for each table row.
                        values_str_row = ""

                        # Iterate over the Table columns that should be included in the DataStore table.
                        for table_col_to_write in table_cols_to_write:

                            # Get the corresponding Database table column name.
                            db_col_name = self.__get_mapped_datastore_col_from_table_col(table_col_to_write,
                                                                                         col_map_dic)

                            # Add the Database table column name to the cols_str Sql portion.
                            cols_str += "{}, ".format(db_col_name)

                            # Get the data type of the Table column. (pandas)
                            col_data_type = table_obj.df[table_col_to_write].dtype

                            # Gracefully handles object (str), int64 (int), float64 (float) and bool (bool) data types.
                            # Still needs to address datetime64, timedelta[ns], and category data types.
                            # See REF: http://pbpython.com/pandas_dtypes.html
                            value = row[table_col_to_write]
                            if col_data_type == "object":
                                values_str_row += "'{}', ".format(value)
                            elif col_data_type == "int64" or col_data_type == "float64":
                                values_str_row += "{}, ".format(value)
                            elif col_data_type == "bool":
                                values_str_row += "{}, ".format(str(value).upper())

                            # Get the DataBase table column datatype. Currently this data is not used but could be
                            # used in the future to help with Data Type errors.
                            database_col_datatype = self.__get_datatype_of_database_col(datastore_obj,
                                                                                        pv_DataStoreTable,
                                                                                        db_col_name)

                        # End of Table columns. Remove the last comma and space characters in the cols_str and the
                        # values_str_row strings.
                        cols_str = cols_str.rsplit(", ", 1)[0]
                        values_str_row = "({})".format(values_str_row.rsplit(", ", 1)[0])

                        # Append the Table values for this Table row to the master values SQL statement.
                        values_str_master += "{}, ".format(values_str_row)

                    # End of Table rows. Remove the last comma and space characters in the values_str_master string.
                    values_str_master = values_str_master.rsplit(", ", 1)[0]

                    # Build the INSERT Sql statement to push the Table data to the DataStore table.
                    # REF: http://www.postgresqltutorial.com/postgresql-insert/
                    sql_str = "INSERT INTO {} ({}) VALUES {};".format(pv_DataStoreTable, cols_str, values_str_master)

                    # Execute the Sql statement and commit the changes.
                    datastore_obj.cursor.execute(sql_str)
                    datastore_obj.connection.commit()

                # Raise an exception if an unexpected error occurs during the process
                except Exception as e:
                    self.warning_count += 1
                    message = "Unexpected error writing Table {} to DataStore ({}).".format(pv_TableID,
                                                                                            pv_DataStoreID)
                    recommendation = "Check the log file for details."
                    self.logger.error(message, exc_info=True)
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
