# Table - class to represent a table using general design
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

# Import Pandas just to ensure that the development and deployed environments contain Pandas, but needs more work.
import pandas as pd

from geoprocessor.core import TableField as TableField
from geoprocessor.core import TableRecord as TableRecord


class DataTable(object):
    """
    The DataTable class holds tabular data objects (columns and rows).
    Instances are generically referred to as "Table" in the user interface.
    All DataTable objects contain a list of TableRecord and a list of TableField, similar to Java TSTool design.

    The table_records list contains a list of TableRecord objects. Each TableRecord object contains a list of
    table items (data objects or None). A TableRecord holds one row of the Table's data.
    Organizing Table data by records is beneficial when deleting and inserting data rows.
    Inserting or deleting columns requires processing all rows.

    The table_fields list holds a list of TableField objects. Each TableField object contains metadata for a table
    column. A TableField holds one column of the Table's data.

    The DataTable data can also be stored in a pandas DataFrame object in order to leverage the pandas library and
    functionality. Processing Table data by pandas DataFrame is beneficial when attempting complicated analysis
    processes. The pandas library is designed to accomplish intricate table analytics at a fast processing speed.
    THIS FUNCTIONALITY IS BEING EVALUATED.

    A list of DataTable instances are maintained by the GeoProcessor's self.tables property (type: list). The
    GeoProcessor's commands retrieve in-memory DataTable instances from the GeoProcessor's self.tables property
    using the GeoProcessor.get_table() function. New Table instances are added to teh GeoProcessor list using the
    add_table() function.

    There are a number of properties associated with each Table. The initialized properties stored within each Table
    instance.  The table identifier is only set at creation but row and column data can change dynamically.
    """

    def __init__(self, table_id: str) -> None:
        """
        Initialize the DataTable object.

        Args:
            table_id (str): String that is the Table's reference ID. This ID is used to access the Table from the
            GeoProcessor for manipulation.
        """

        # "id" is a string that is the Table's reference ID. This ID is used to access the Table from the GeoProcessor
        # for manipulation.
        self.id: str = table_id

        # TODO smalers 2020-11-13 attempted to use Pandas Data Frame for tables but had issues
        # - previous developer could not resolve how to handle missing data values
        # - for now use a design similar to TSTool Java
        # - if Pandas object added, refactor the methods that access the table but hopefully functionality is retained
        # "pandas_df" is a Pandas Data Frame object created by the pandas library. All manipulations are performed on
        # the Table's pandas data frame.
        # self.pandas_df = None

        # "table_fields" is a list that holds the Table's TableField objects. A TableField object represents one
        # column of the Table.
        self.table_fields: [TableField] = []

        # "table_records" is a list that holds the Table's TableRecords objects. TableRecord object represents one
        # row of the Table.
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

    def x_create_df(self):
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

    def x_print_df(self):
        """
        Print the Table's pandas DataFrame to the console.

        Return: None
        """

        # Print the table title, the pandas DataFrame and a spacer to the console.
        print("Pandas DataFrame for Table {}".format(self.id))
        print(self.pandas_df)
        print("\n---------------\n")

    def x_print_fields(self):
        """
        Print the Table's TableFields to the console.

        Return: None
        """

        # Print the table title, the table (by column) and a spacer to the console.
        print("Fields (Columns) for Table {}".format(self.id))
        for table_field in self.table_fields:
            print(table_field.items)
        print("\n---------------\n")

    def x_print_records(self):
        """
        Print the Table's TableRecords to the console.

        Return: None
        """

        # Print the table title, the table (by row) and a spacer to the console.
        print("Records (Rows) for Table {}".format(self.id))
        for table_record in self.table_records:
            print(table_record.items)
        print("\n---------------\n")

    def x_return_column_index(self, column_name):

        return self.return_fieldnames().index(column_name)

    def x_return_fieldnames(self):

        fieldnames = []
        for table_field in self.table_fields:
            fieldnames.append(table_field.name)

        return fieldnames


