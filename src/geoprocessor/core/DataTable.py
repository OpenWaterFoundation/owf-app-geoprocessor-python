# DataTable - class to represent a table using general design
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2023 Open Water Foundation
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

# Import Pandas just to ensure that the development and deployed environments contain Pandas, but needs more work.
import pandas as pd

from geoprocessor.core import TableField as TableField
from geoprocessor.core import TableRecord as TableRecord

import typing


class DataTable(object):
    """
    The DataTable class holds tabular data objects (columns and rows).
    Instances are generically referred to as "Table" in the user interface.
    All DataTable objects contain a list of TableRecord and a list of TableField, similar to Java TSTool design.

    The table_records list contains a list of TableRecord objects.
    Each TableRecord object contains a list of table items (data objects or None).
    A TableRecord holds one row of the Table's data.
    Organizing Table data by records is beneficial when deleting and inserting data rows.
    Inserting or deleting columns requires processing all rows.

    The table_fields list holds a list of TableField objects.
    Each TableField object contains metadata for a table column.
    A TableField holds one column of the Table's data.

    The DataTable data can also be stored in a pandas DataFrame object in order to leverage the pandas library and
    functionality.
    Processing Table data by pandas DataFrame is beneficial when attempting complicated analysis processes.
    The pandas library is designed to accomplish intricate table analytics at a fast processing speed.
    THIS FUNCTIONALITY IS BEING EVALUATED.

    A list of DataTable instances are maintained by the GeoProcessor's self.tables property (type: list).
    The GeoProcessor's commands retrieve in-memory DataTable instances from the GeoProcessor's 'self.tables'
    property using the GeoProcessor.get_table() function.
    New Table instances are added to teh GeoProcessor list using the add_table() function.

    There are a number of properties associated with each Table.
    The initialized properties stored within each Table instance.
    The table identifier is only set at creation but row and column data can change dynamically.
    """

    def __init__(self, table_id: str) -> None:
        """
        Initialize the DataTable object.

        Args:
            table_id (str):
                String that is the Table's reference ID.
                This ID is used to access the Table from the GeoProcessor for manipulation.
        """

        # "id" is a string that is the Table's reference ID.
        # This ID is used to access the Table from the GeoProcessor for manipulation.
        self.id: str = table_id

        # TODO smalers 2020-11-13 attempted to use Pandas Data Frame for tables but had issues:
        # - previous developer could not resolve how to handle missing data values
        # - for now use a design similar to TSTool Java
        # - if Pandas object added, refactor the methods that access the table but hopefully functionality is retained
        # "pandas_df" is a Pandas Data Frame object created by the pandas library.
        # All manipulations are performed on the Table's pandas data frame.
        # self.pandas_df = None

        # "table_fields" is a list that holds the Table's TableField objects.
        # A TableField object represents one column of the Table.
        self.table_fields: [TableField] = []

        # "table_records" is a list that holds the Table's TableRecords objects.
        # TableRecord object represents one row of the Table.
        self.table_records: [TableRecord] = []

    def add_field(self, table_field: TableField) -> None:
        """
        Add a TableField object to the Table's "table_fields" list.

        Args:
            The TableField object to add to the Table's "table_fields" list.

        Return: None
        """

        # Add the TableField object to the Table's "table_fields" attribute list.

        self.table_fields.append(table_field)

    def add_record(self, table_record: TableRecord) -> None:
        """
        Add a TableRecord object to the Table's "table_records" list.

        Args:
            The TableRecord object to add to the Table's "table_records" list.

        Return: None
        """

        # Add the TableRecord object to the Table's "table_records" list.
        self.table_records.append(table_record)

    def get_column_index(self, column_name: str) -> int:
        """
        Return the column index (0+) for a column name.

        Args:
            column_name (str): name of the column of interest

        Returns:
            index (0+) of the column in the table
        """
        return self.get_field_names().index(column_name)

    def get_column_values_as_list(self, column_name: str) -> typing.List[typing.Any]:
        """
        Return the values in the requested column.

        Args:
            column_name (str): name of the column of interest

        Returns:
            list of values from the column
        """

        # First get the column index:
        # - this will throw an error if not found
        column_index = self.get_column_index(column_name)

        # Loop through the table and extract the values.
        values = []

        for record in self.table_records:
            values.append(record.get_field_value(column_index))

        return values

    def get_field_data_type(self, index: int) -> int:
        """
        Return the field data type given an index.

        Args:
            index: Column index.

        Returns:
            The field data type given an index.
        """
        if len(self.table_fields) <= index:
            raise IndexError("Table field index {} is not valid.".format(index))
        else:
            return self.table_fields[index].data_type

    def get_field_index(self, field_name: str) -> int:
        """
        Return the field index (0+) corresponding to the field name.

        Args:
            field_name:

        Returns:
            Field index (0+) corresponding to the field name, or -1 if not found.
        """
        for i, table_field in enumerate(self.table_fields):
            if table_field.name == field_name:
                return i

        return -1

    def get_field_names(self) -> typing.List[str]:
        """
        Return the table column (field) names.

        Returns:
            A list of the table column(field) names in the order of the table.
        """
        field_names = []
        for table_field in self.table_fields:
            field_names.append(table_field.name)

        return field_names

    def get_field_value(self, record_index: int, field_index: int) -> typing.Any:
        """
        Return the value for a record and column.

        Args:
            record_index (int): record index
            field_index (int): fienld index within the record

        Returns:
            Value for the record and column indices.
        """
        if len(self.table_records) <= record_index:
            raise IndexError("Table record index {} is not valid.".format(record_index))
        if len(self.table_fields) <= field_index:
            raise IndexError("Table field index {} is not valid.".format(field_index))

        table_record = self.table_records[record_index]
        return table_record.get_field_value(field_index)

    def get_number_of_columns(self) -> int:
        """
        Return the number of columns.

        Returns:
            Number of rows.
        """
        return len(self.table_fields)

    def get_number_of_rows(self) -> int:
        """
        Return the number of rows.

        Returns:
            Number of rows.
        """
        return len(self.table_records)

    def get_record(self, record_index: int = -1 ) -> TableRecord or None:
        """
        Return the TableRecord for the requested index.

        Args:
            record_index(int) table row index (0+_

        Returns:
            The TableRecord for the requested index or None if out of range.
        """
        if record_index >= 0:
            return self.table_records[record_index]
        else:
            return None

    def get_records(self, columns: [str] or [int], column_values: [typing.Any]) -> [TableRecord]:
        """
        Return records that match the values in specified columns.

        Args:
            columns ([str]): Column names to check.
            column_values ([Any]): Values for columns to check.

        Returns:
            List of matching records, guaranteed to be non-None but may be empty.
        """
        records = []
        if len(columns) == 0:
            return records
        elif isinstance(columns[0], str):
            # Convert column names to column numbers and then call recursively.
            column_numbers = []
            column_names = columns
            for column_name in column_names:
                column_numbers.append(self.get_field_index(column_name))
            return self.get_records(column_numbers, column_values)
        elif isinstance(columns[0], int):
            # Don't need to convert column names to column numbers.
            # Make sure that all the column numbers are >= 0.
            column_numbers = columns
            for icol in range(len(column_numbers)):
                if column_numbers[icol] < 0:
                    return records
            # Loop through table records.
            for record in self.table_records:
                match_count = 0
                # Loop through columns of interest and try to match values in those columns:
                # - column_contents - is what is in the table in that column
                # - column_value - is the value being requested
                for icol, column_value in enumerate(column_values):
                    # In some cases below, create a string version of the column value for comparisons:
                    # - TODO smalers 2020-11-15 does this do bad things for large floating point numbers
                    #   such as use scientific notation?
                    column_contents = record.get_field_value(column_numbers[icol])
                    if column_contents is None:
                        # Only match if both are None.
                        if column_value is None:
                            match_count += 1
                    elif self.get_field_data_type(column_numbers[icol]) == str:
                        # Do case-sensitive comparison:
                        # - TODO smalers 2020-11-14 evaluate whether to do case-insensitive comparison
                        if isinstance(column_value,str):
                            if column_value == column_contents:
                                match_count += 1
                        else:
                            # Convert the value to string.
                            column_value_str = "{}".format(column_value)
                            if column_value_str == column_contents:
                                match_count += 1
                    else:
                        # Not a string so use == to compare:
                        # - works well for int and bool but floating point may have roundoff
                        if column_value == column_contents:
                            match_count += 1
                if match_count == len(column_values):
                    # Have matched the requested number of column values so add record to the match list.
                    records.append(record)

            return records
        else:
            raise RuntimeError("column_names type is not str or int.")

    def create_df(self):
        """
        Create/recreate a pandas DataFrame from the Table's fields.

        Return: None
        """

        # Create an empty dictionary that will hold the Table columns and their corresponding values.
        # KEY: name of the Table column
        # VALUE: a list of the column values (one item for each Table record)
        col_entries_dic = {}

        # Iterate over the fields (columns) in the Table.
        for table_field in self.table_fields:

            # Assign the field name to the key and the field values to the value of the col_entries_dic dictionary.
            col_entries_dic[table_field.name] = table_field.items

            # Convert the dictionary of Table fields into a pandas DataFrame. Add the DataFrame to the Table attribute.
            self.pandas_df = pd.DataFrame(data=col_entries_dic)

    def print_df(self):
        """
        Print the Table's pandas DataFrame to the console.

        Return: None
        """

        # Print the table title, the pandas DataFrame and a spacer to the console.
        print("Pandas DataFrame for Table {}".format(self.id))
        print(self.pandas_df)
        print("\n---------------\n")

    def print_fields(self):
        """
        Print the Table's TableFields to the console.

        Return: None
        """

        # Print the table title, the table (by column) and a spacer to the console.
        print("Fields (Columns) for Table {}".format(self.id))
        for table_field in self.table_fields:
            print(table_field.items)
        print("\n---------------\n")

    def print_records(self):
        """
        Print the Table's TableRecords to the console.

        Return: None
        """

        # Print the table title, the table (by row) and a spacer to the console.
        print("Records (Rows) for Table {}".format(self.id))
        for table_record in self.table_records:
            print(table_record.items)
        print("\n---------------\n")
