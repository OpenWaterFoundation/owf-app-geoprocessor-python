# WriteTableToDataStore

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.Table import Table

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.pandas_util as pandas_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validators

import logging


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

        # Convert the IncludeColumns and ExcludeColumns to lists.
        cols_to_include = string_util.delimited_string_to_list(pv_IncludeColumns)
        cols_to_exclude = string_util.delimited_string_to_list(pv_ExcludeColumns)

        # Convert the ColumnMap parameter from string to a list of mapping entries.
        # col_map_entry_list = string_util.delimited_string_to_list(pv_ColumnMap, delimiter=',')
        col_map_dic = string_util.delimited_string_to_dictionary_one_value(pv_ColumnMap, entry_delimiter=",",
                                                                           key_value_delimiter=":", trim=True)
        print("Col Map: {}".format(col_map_dic))

        print("ToInclude: {}, ToExclude: {}".format(cols_to_include, cols_to_exclude))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_write_table(pv_TableID, pv_DataStoreID, pv_DataStoreTable):

            try:

                # Get the Table object
                table_obj = self.command_processor.get_table(pv_TableID)

                # Get a list of columns from the Table
                table_cols = table_obj.get_column_names()
                print("All cols: {}".format(table_cols))
                table_cols_to_include = string_util.filter_list_of_strings(table_cols, cols_to_include, cols_to_exclude)
                print("Include cols: {}".format(table_cols_to_include))

                values_str_master = ""

                # Iterate over the rows in the Table.
                for index, row in table_obj.df.iterrows():

                    cols_str = ""
                    values_str_row = ""

                    # Iterate over the Table columns that should be included in the DataStore table.
                    for table_col_to_include in table_cols_to_include:

                        value = row[table_col_to_include]
                        values_str_row += "'{}', ".format(value)

                        # Get the corresponding Database column name
                        if table_col_to_include in col_map_dic.keys():
                            db_col_name = col_map_dic[table_col_to_include]
                        else:
                            db_col_name = table_col_to_include

                        cols_str += "{}, ".format(db_col_name)

                    cols_str = cols_str.rsplit(", ", 1)[0]
                    values_str_row = "({})".format(values_str_row.rsplit(", ", 1)[0])
                    values_str_master += "{}, ".format(values_str_row)

                values_str_master = values_str_master.rsplit(", ", 1)[0]
                sql_str = "INSERT INTO {} ({}) VALUES {};".format(pv_DataStoreTable, cols_str, values_str_master)
                print(sql_str)

                # Get DataStore object
                datastore_obj = self.command_processor.get_datastore(pv_DataStoreID)

                # Execute the Sql statement.
                datastore_obj.cursor.execute(sql_str)

                # Commit the changes
                datastore_obj.connection.commit()

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error writing Table {} to DataStore ({}).".format(pv_TableID,
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
