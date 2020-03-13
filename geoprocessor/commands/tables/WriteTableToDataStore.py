# WriteTableToDataStore - command to write a table to a datastore
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

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType
from geoprocessor.core.DataStore import DataStore
from geoprocessor.core.Table import Table

import geoprocessor.util.command_util as command_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import logging


class WriteTableToDataStore(AbstractCommand):
    """
    Writes a Table to a DataStore object.

    Command Parameters
    * TableID (str, required): Identifier for Table to write. Can be specified with ${Property}.
    * IncludeColumns (str, optional) A comma-separated list of the glob-style patterns filtering which table columns to
        write.
    * ExcludeColumns (str, optional) A comma-separated list of the glob-style patterns filtering which table columns to
        NOT write. This will override IncludeColumns.
    * DataStoreID (str, required): The ID of a DataStore to receive data. ${Property} syntax is recognized.
    * DataStoreTable (str, required): The name of the DataStore table to receive data. ${Property} syntax is recognized.
    * ColumnMap (str, optional): A dictionary indicating which columns in TableID have different names in DataStore
        Table, using the syntax: ColumnName:DatastoreTableName, ColumnName:DatastoreTableName,...
        Default: DataStore TableName columns are assumed to match the column names in TableID.
    * DataStoreRelatedColumnsMap (str, optional): Not currently enabled.
    * WriteMode (str, required): The method used to write data. Muse choose one of the following:
        1. NewTableInsert: a new table is added to the database and all rows of TableID are added to the database table.
        2. ExistingTableOverwrite: the existing database table is dropped and another database table is added
            (with the same name). All rows of TableID are added to the database table.
        3. ExistingTableInsert: Rows of the TableID that do NOT conflict with any of the rows in the existing database
            table are appended to the database table.
        4. ExistingTableUpdate: Rows of the TableID that do conflict with any of the rows in the existing database
            table are used to update the existing database rows. The rows that do NOT conflict with any of the rows
                in the existing database table are NOT appended to the database table.
        5. ExistingTableInsertUpdate: Rows of the TableID that do NOT conflict with any of the rows in the existing
            database table are appended to the database table. Rows of the TableID that do conflict with any of the
            rows in the existing database table are used to update the existing database rows.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("TableID", type("")),
        CommandParameterMetadata("IncludeColumns", type("")),
        CommandParameterMetadata("ExcludeColumns", type("")),
        CommandParameterMetadata("DataStoreID", type("")),
        CommandParameterMetadata("DataStoreTable", type("")),
        CommandParameterMetadata("ColumnMap", type("")),
        CommandParameterMetadata("DataStoreRelatedColumnsMap", type("")),
        CommandParameterMetadata("WriteMode", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = (
        "This command processes each row in a Table and executes and "
        "SQL statement to insert the row into a database DataStore.")
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # TableID
    __parameter_input_metadata['TableID.Description'] = "table identifier"
    __parameter_input_metadata['TableID.Label'] = "TableID"
    __parameter_input_metadata['TableID.Required'] = True
    __parameter_input_metadata['TableID.Tooltip'] = "A Table identifier"
    # IncludeColumns
    __parameter_input_metadata['IncludeColumns.Description'] = "table columns to include"
    __parameter_input_metadata['IncludeColumns.Label'] = "Include columns"
    __parameter_input_metadata['IncludeColumns.Tooltip'] = \
        "A comma-separated list of the glob-style patterns filtering which columns to write."
    __parameter_input_metadata['IncludeColumns.Value.Default'] = "'* - all columns are processed"
    # ExcludeColumns
    __parameter_input_metadata['ExcludeColumns.Description'] = "table columns to exclude"
    __parameter_input_metadata['ExcludeColumns.Label'] = "Exclude columns"
    __parameter_input_metadata['ExcludeColumns.Tooltip'] = \
        "A comma-separated list of the glob-style patterns filtering which columns to write."
    __parameter_input_metadata['ExcludeColumns.Value.Default.Description'] = "all columns"
    # DataStoreID
    __parameter_input_metadata['DataStoreID.Description'] = "database DataStore"
    __parameter_input_metadata['DataStoreID.Label'] = "DataStoreID"
    __parameter_input_metadata['DataStoreID.Required'] = True
    __parameter_input_metadata['DataStoreID.Tooltip'] = \
        "The ID of a database DataStore to recieve the data. ${Property} syntax is recognized."
    # DataStoreTable
    __parameter_input_metadata['DataStoreTable.Description'] = "database table to receive data"
    __parameter_input_metadata['DataStoreTable.Label'] = "DataStore table"
    __parameter_input_metadata['DataStoreTable.Tooltip'] = (
        "The name of the database table to receive data. ${Property} syntax is recognized.\n"
        "If specified, do not specify Sql or SqlFile.")
    # TODO @jurentie 01/22/19 do these need to be read file selector type?
    # ColumnMap
    __parameter_input_metadata['ColumnMap.Description'] = "map table to datastore columns"
    __parameter_input_metadata['ColumnMap.Label'] = "Column map"
    __parameter_input_metadata['ColumnMap.Tooltip'] = (
        "Specify which columns in the Table have different names in the DataStore table.\n"
        "Use the syntax: ColumnName:DatastoreTableName, ColumnName:DatastoreTableName,...")
    __parameter_input_metadata['ColumnMap.Value.Default.Description'] = \
        "DataStore table columns names are assumed to match the Table column names."
    # DataStoreRelatedColumnsMap
    __parameter_input_metadata['DataStoreRelatedColumnsMap.Description'] = "datastore relate table columns"
    __parameter_input_metadata['DataStoreRelatedColumnsMap.Label'] = "DataStore related column map"
    __parameter_input_metadata['DataStoreRelatedColumnsMap.Tooltip'] = (
        "Indicate datastore columns that need to match values in a related table in the datastore. '"
        "This parameter is currently disabled.")
    __parameter_input_metadata['DataStoreRelatedColumnsMap.Value.Default'] = (
        "DataStore table columns are assumed to match the column names in TableID, "
        "with no need to perform reference table value matching.")
    # WriteMode
    __parameter_input_metadata['WriteMode.Description'] = "method used to write data"
    __parameter_input_metadata['WriteMode.Label'] = "Write mode"
    __parameter_input_metadata['WriteMode.Tooltip'] = (
        "The method used to write data.\n"
        "NewTableInsert: a new table is added to the database and all rows of TableID are added to "
        "the database table \n"
        "ExistingTableOverwrite: the existing database table is dropped and another database table is "
        "added (with the same name).\n"
        "All rows of TableID are added to the database table\n"
        "ExistingTableInsert: rows of the TableID that do NOT conflict with any of the rows in the existing \n"
        "database table are appended to the database table.\n"
        "ExistingTableUpdate: rows of the TableID that do conflict with any of the rows in the existing "
        "database table are used to update the existing database rows.\n"
        "The rows that do NOT conflict with any "
        "of the rows in the existing database table are NOT appended to the database table.\n"
        "ExistingTableInsertUpdate: rows of the TableID that do NOT conflict with any of the rows in the "
        "existing database table are appended to the database table.\n"
        "Rows of the TableID that do conflict with any of the rows in the existing database table are "
        "used to update the existing database rows.")

    # Choices for WriteMode, used to validate parameter and display in editor
    __choices_WriteMode = ["NewTableInsert", "ExistingTableOverwrite", "ExistingTableInsert", "ExistingTableUpdate",
                           "ExistingTableInsertUpdate"]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "WriteTableToDataStore"
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

        warning = ""

        # Check that the required parameters are non-empty, non-None strings.
        required_parameters = ["TableID", "DataStoreID", "DataStoreTable"]

        for parameter in required_parameters:

            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)
            if not validator_util.validate_string(parameter_value, False, False):
                message = "{} parameter has no value.".format(parameter)
                recommendation = "Specify a valid value for the {} parameter.".format(parameter)
                warning += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional parameter WriteMode is one of the acceptable values or is None.
        # noinspection PyPep8Naming
        pv_WriteMode = self.get_parameter_value(parameter_name="WriteMode",
                                                command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_WriteMode, self.__choices_WriteMode, none_allowed=False,
                                                      empty_string_allowed=False, ignore_case=True):
            message = "WriteMode parameter value ({}) is not recognized.".format(pv_WriteMode)
            recommendation = "Specify one of the acceptable values ({}) for the WriteMode parameter.".format(
                self.__choices_WriteMode)
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

    @staticmethod
    def __get_table_cols_to_write(include_col_patterns: str, exclude_col_patterns: str, table: Table) -> [str]:
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
                                                                   table_cols_to_exclude_patterns,
                                                                   return_inclusions=True)

        # Return a list of Table column names configured to write data.
        return table_cols_to_include

    @staticmethod
    def __get_table_cols_to_exclude(include_col_patterns: str, exclude_col_patterns: str, table: Table) -> [str]:
        """
        The command allows for users to select a subset of the Table columns to write to the DataStore database. This
        function returns a list of Table columns NOT configured to write data by the user inputs.

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

        # Get a list of the columns in the Table that are NOT configured to be pushed to the DataStore
        table_cols_to_exclude = string_util.filter_list_of_strings(all_table_cols, table_cols_to_include_patterns,
                                                                   table_cols_to_exclude_patterns,
                                                                   return_inclusions=False)

        # Return a list of Table column names NOT configured to write data.
        return table_cols_to_exclude

    @staticmethod
    def __get_mapped_datastore_col_from_table_col(table_col_name: str, col_map_dic: dict) -> str:
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

    def __get_datastore_cols_to_receive(self, table_cols_to_write: [str], col_map_dic: dict) -> [str]:
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

    def __should_write_table(self, table_id: str, datastore_id: str, datastore_table_name: str, writemode: str) -> bool:
        """
        Checks the following:
            * the Table ID exists
            * the DataStore ID exists
            * the DataStore table exists if the writemode is ExistingTableInsert, ExistingTableUpdate, or
                ExistingTableInsertUpdate
            * the DataStore table does not exist if the writemode starts with NewTable

        Args:
            table_id (str): the ID of the Table to write
            datastore_id (str): the ID of the DataStore to receive data
            datastore_table_name (str): the name of the DataStore table to receive data
            writemode (str): the method used to write data

        Returns:
             Boolean. If TRUE, the process should be run. If FALSE, it should not be run.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the DataStore ID is not an existing DataStore ID, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsDataStoreIdExisting", "DataStoreID", datastore_id,
                                                           "FAIL"))

        # Only run the following check if the previous check passed.
        if False not in should_run_command:

            if writemode.upper().startswith("EXISTING") and not writemode.upper().endswith("OVERWRITE"):

                # If the DataStoreTable is not a table within the DataStore, raise a FAILURE.
                should_run_command.append(validator_util.run_check(self, "IsTableInDataStore", "DataStoreTable",
                                                                   datastore_table_name, "FAIL",
                                                                   other_values=[datastore_id]))

            if writemode.upper().startswith("NEW"):

                # If the DataStoreTable is a table within the DataStore, raise a FAILURE.
                should_run_command.append(validator_util.run_check(self, "IsDataStoreTableUnique", "DataStoreTable",
                                                                   datastore_table_name, "FAIL",
                                                                   other_values=[datastore_id]))

        # If the Table ID is not an existing Table ID, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsTableIdExisting", "TableID", table_id, "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def __should_write_table2(self, datastore: DataStore, datastore_table_name: str,
                              datastore_table_cols_to_receive: [str], writemode: str) -> bool:
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

        # A list of Table columns that do not map to the DataStore Table columns.
        invalid_columns = []

        # Do not run this check if the WriteMode is NewTableInsert or ExistingTableOverwrite
        exception_modes = ["NEWTABLEINSERT", "EXISTINGTABLEOVERWRITE"]
        if writemode.upper() not in exception_modes:

            # Get the DataStore Table columns.
            datastore_table_cols = datastore.return_col_names(datastore_table_name)

            # Iterate over the DataStore columns that are configured to read data.
            for datastore_table_col_to_receive in datastore_table_cols_to_receive:

                # If the configured DataStore column does not exist in the DataStore table, add the configured
                # DataStore column to the list of invalid columns.
                if datastore_table_col_to_receive not in datastore_table_cols:
                    invalid_columns.append(datastore_table_col_to_receive)

        # If there are any invalid configured DataStore columns, raise a FAILURE.
        if invalid_columns:
            message = "One or more of the DataStore columns configured to be edited do(es) not exist in the DataStore" \
                " table ({}). The invalid columns are: \n({}).".format(datastore_table_name, invalid_columns)
            recommendation = "Specify valid DataStore columns to edit."

            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
            should_run_command.append(False)

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            self.warning_count += 1
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Read the Table from the DataStore

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_TableID = self.get_parameter_value("TableID")
        # noinspection PyPep8Naming
        pv_IncludeColumns = self.get_parameter_value("IncludeColumns", default_value="*")
        # noinspection PyPep8Naming
        pv_ExcludeColumns = self.get_parameter_value("ExcludeColumns", default_value="''")
        # noinspection PyPep8Naming
        pv_DataStoreID = self.get_parameter_value("DataStoreID")
        # noinspection PyPep8Naming
        pv_DataStoreTable = self.get_parameter_value("DataStoreTable")
        # noinspection PyPep8Naming
        pv_ColumnMap = self.get_parameter_value("ColumnMap", default_value="")
        # noinspection PyPep8Naming
        # pv_DataStoreRelatedColumnsMap = self.get_parameter_value("DataStoreRelatedColumnsMap")
        # noinspection PyPep8Naming
        pv_WriteMode = self.get_parameter_value("WriteMode").upper()

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_TableID = self.command_processor.expand_parameter_value(pv_TableID, self)
        # noinspection PyPep8Naming
        pv_DataStoreID = self.command_processor.expand_parameter_value(pv_DataStoreID, self)
        # noinspection PyPep8Naming
        pv_DataStoreTable = self.command_processor.expand_parameter_value(pv_DataStoreTable, self)

        # Run the checks on the parameter values. Only continue if the checks pass.
        if self.__should_write_table(pv_TableID, pv_DataStoreID, pv_DataStoreTable, pv_WriteMode):

            # Get the Table object.
            table_obj = self.command_processor.get_table(pv_TableID)

            # Get DataStore object
            datastore_obj = self.command_processor.get_datastore(pv_DataStoreID)

            # Convert the ColumnMap from string to a dictionary. Key: Table Column Name; Value: DataStore Column Name
            col_map_dic = string_util.delimited_string_to_dictionary_one_value(pv_ColumnMap, ",", ":", True)

            # Get the list of the columns in the Table that are configured to write.
            table_cols_to_write = self.__get_table_cols_to_write(pv_IncludeColumns, pv_ExcludeColumns, table_obj)

            # Get the list of the columns in the DataStore that are configured to receive data.
            datastore_table_cols_to_receive = self.__get_datastore_cols_to_receive(table_cols_to_write, col_map_dic)

            # Run a second level of checks. Only continue if the check passes.
            if self.__should_write_table2(datastore_obj, pv_DataStoreTable, datastore_table_cols_to_receive,
                                          pv_WriteMode):

                # noinspection PyBroadException
                try:

                    # Get the list of the columns in the Table that are NOT configured to write.
                    table_cols_to_exclude = self.__get_table_cols_to_exclude(pv_IncludeColumns, pv_ExcludeColumns,
                                                                             table_obj)

                    # Make a deep copy of the Table object.
                    table_obj_copy = table_obj.deep_copy()

                    # Remove the copied pandas Data Frame columns that are not to be written to the DataStore.
                    table_obj_copy = table_obj_copy.drop(columns=table_cols_to_exclude)

                    # Rename the copied pandas Data Frame columns to match the columns in the database table.
                    table_obj_copy = table_obj_copy.rename(columns=col_map_dic)

                    # Write the copied pandas Data Frame to the DataStore's database table.
                    # If the WriteMode is NewTableInsert, continue.
                    if pv_WriteMode.upper() == "NEWTABLEINSERT":

                        table_obj_copy.to_sql(name=pv_DataStoreTable, con=datastore_obj.engine, index=False)

                    # If the WriteMode is ExistingTableOverwrite, continue.
                    elif pv_WriteMode.upper() == "EXISTINGTABLEOVERWRITE":

                        table_obj_copy.to_sql(name=pv_DataStoreTable, con=datastore_obj.engine, if_exists="replace",
                                              index=False)

                    # If the WriteMode is ExistingTableInsert, continue.
                    elif pv_WriteMode.upper() == "EXISTINGTABLEINSERT":

                        table_obj_copy.to_sql(name=pv_DataStoreTable, con=datastore_obj.engine, if_exists="append",
                                              index=False)

                    # If the WriteMode is ExistingTableUpdate, continue.
                    elif pv_WriteMode.upper() == "EXISTINGTABLEUPDATE":

                        print("The ExistingTableUpdate WriteMode is currently disabled.")

                    # If the WriteMode is ExistingTableInsertUpdate, continue.
                    elif pv_WriteMode.upper() == "EXISTINGTABLEINSERTUPDATE":

                        print("The ExistingTableInsertUpdate WriteMode is currently disabled.")

                # Raise an exception if an unexpected error occurs during the process
                except Exception:
                    self.warning_count += 1
                    message = "Unexpected error writing Table {} to DataStore ({}).".format(pv_TableID,
                                                                                            pv_DataStoreID)
                    recommendation = "Check the log file for details."
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                    recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
