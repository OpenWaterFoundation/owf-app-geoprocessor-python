# Table - class to store table data using Pandas table
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

import typing


class Table(object):
    """
    The Table class holds tabular data objects (columns and rows).
    The core data is stored in a pandas data frame object in order to leverage the pandas library and functionality.
    Additional data members are used to store data that are not part of the pandas data frame object and are
    required from the GeoProcessor.
    These include attributes like a table identifier and a source filename.

    A list of registered Table instances are maintained by the GeoProcessor's 'self.tables' property (type: list).
    The GeoProcessor's commands retrieve in-memory Table instances from the GeoProcessor's 'self.tables'
    property using the GeoProcessor.get_table() function.
    New Table instances are added to teh GeoProcessor list using the add_table() function.

    There are a number of properties associated with each Table.
    The initialized properties stored within each Table instance are the STATIC properties that will never change
    (identifier, df object, and source path).
    The DYNAMIC properties (column names, number of table entries, etc.)
    are created when needed by accessing class functions.

    Tables can be made in memory from within the GeoProcessor.
    This occurs when a command is called that, by design, creates a new Table.
    When this occurs, the in-memory Table is assigned a table_id from within the command,
    the df is created from within the command and the source_path is set to 'MEMORY' or 'NONE'.
    """
    def __init__(self, table_id: str, pandas_df, table_source_path: str, properties:dict = None) -> None:
        """
        Initialize a new Table instance.

        Args:
            table_id (str):
                String that is the Table's reference ID. This ID is used to access the Table from the GeoProcessor for
                manipulation.
            pandas_df (pandas Data Frame object):
                Object created by the pandas library. All Table manipulations are performed on the Tables's pandas data
                 frame object.
            table_source_path (str):
                The full pathname to the original file on the user's local computer. If the tables was made in memory
                from the GeoProcessor, this value is set to `MEMORY`.
            properties ({}):
                A dictionary of user (non-built-in) properties that can be assigned to the tables.
                These properties facilitate processing.
        """

        # "id" is a string that is the Table's reference ID.
        # This ID is used to access the Table from the GeoProcessor for manipulation.
        self.id: str = table_id

        # "pandas_df" is a Pandas Data Frame object created by the 'pandas' library.
        # All manipulations are performed on the Table's pandas data frame.
        self.df = pandas_df

        # "source_path" (str) is the full pathname to the original data file on the user's local computer.
        self.source_path: str = table_source_path

        # "int_null_value" is the value used to replace the null value within the integer columns, if applicable.
        # See ReadTableFromDataStore parameters IntNullHandleMethod  and IntNullValue for more information.
        self.int_null_value = None

        # "properties" (dict) is a dictionary of user (non-built-in) properties that are assigned to the layer.
        # These properties facilitate processing and may or may not be output to to a persistent format,
        # depending on whether the format allows general properties on the layer.
        # If None an empty dictionary is created.
        # TODO smalers 2018-01-10 does the QGIS layer have such an object already that could be used without confusion?
        # - don't want a bunch of internal properties visible to the user.
        if properties is None:
            self.properties = {}
        else:
            self.properties = properties

    def deep_copy(self):
        """
        Creates and returns a deep copy of the Table's pandas Data Frame object.

        Return:
            A pandas Data Frame object.
        """

        return self.df.copy(deep=True)

    def get_column_names(self) -> [str]:
        """
        Return a list of column names.

        Returns: A list of column names.
        """

        # Return a list of the column names.
        return list(self.df)

    def get_column_values_as_list(self, column_name) -> [typing.Any]:
        """
        Return all the column values for a given column.

        Args:
            column_name (str): the name of the column of interest

        Returns: A list of the column values.
        """

        # Return a list of the column values for the given input column.
        return self.df[column_name].tolist()

    def count_columns(self) -> int:
        """
        Return either the number of columns for the table.

        Returns:
            The column count (int).
        """
        row, col = self.df.shape
        return col

    def count_rows(self, return_col=True) -> int:
        """
        Return the number of rows for the table.

        Returns:
            The row count (int).
        """
        row, col = self.df.shape
        return row
