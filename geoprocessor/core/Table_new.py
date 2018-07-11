import pandas as pd
import enum


class Table(object):
    """
    The Table class holds tabular data objects (columns and rows). All Table objects contain a list of TableRecords
    and a list of TableFields. The table data is stored twice - once in the TableRecords attribute list and again in
    the TableFields attribute list.

    The TableRecords attribute list holds a list of TableRecord objects. Each TableRecord object contains a list of
    table items (data values). A TableRecord holds one row of the Table's data. The TableRecords attribute list
    contains one TableRecord object for each row of the Table. Processing Table data by records is beneficial when
    deleting and inserting data rows.

    The TableFields attribute list holds a list of TableField objects. Each TableField object contains a list of table
    items (data values). A TableField holds one column of the Table's data. The TableFields attribute list contains one
    TableField object for each column of the Table. Processing Table data by fields is beneficial given faster
    processing speed over the table record method.

    The Table data can also be stored in a pandas DataFrame object in order to leverage the pandas library and
    functionality. Processing Table data by pandas DataFrame is beneficial when attempting complicated analysis
    processes. The pandas library is designed to accomplish intricate table analytics at a fast processing speed.

    A list of registered Table instances are maintained by the GeoProcessor's self.tables property (type: list). The
    GeoProcessor's commands retrieve in-memory Table instances from the GeoProcessor's self.tables property using the
    GeoProcessor.get_table() function. New Table instances are added to teh GeoProcessor list using the add_table()
    function.

    There are a number of properties associated with each Table. The initialized properties stored within each Table
    instance are the STATIC properties that will never change (identifier). The DYNAMIC properties (the TableFields
    attribute list, the TableRecords attribute list, the record count, etc.) are created when needed by accessing
    class functions.
    """

    def __init__(self, table_id):
        """
        Initialize the Table object.

        Args:
            table_id (str): String that is the Table's reference ID. This ID is used to access the Table from the
            GeoProcessor for manipulation.
        """

        # "id" is a string that is the Table's reference ID. This ID is used to access the Table from the GeoProcessor
        # for manipulation.
        self.id = table_id

        # "pandas_df" is a Pandas Data Frame object created by the pandas library. All manipulations are performed on
        # the Table's pandas data frame.
        self.pandas_df = None

        # "table_fields" is a list that holds the Table's TableField objects. A TableField object represents one
        # column of the Table.
        self.table_fields = []

        # "table_records" is a list that holds the Table's TableRecords objects. TableRecord object represents one
        # row of the Table.
        self.table_records = []

        # "record_count" is an integer representing the number of records (rows) in the Table (not including the
        # header row)
        self.record_count = None

    def add_table_field(self, table_field_obj):
        """
        Add a TableField object to the Table's "table_fields" attribute list.

        Args:
            The TableField object to add to the Table's "table_fields" attribute list.

        Return: None
        """

        # Add the TableField object to the Table's "table_fields" attribute list.

        self.table_fields.append(table_field_obj)

    def add_table_record(self, table_record_obj):
        """
        Add a TableRecord object to the Table's "table_records" attribute list.

        Args:
            The TableRecord object to add to the Table's "table_records" attribute list.

        Return: None
        """

        # Add the TableRecord object to the Table's "table_records" attribute list.
        self.table_fields.append(table_record_obj)

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

    def return_column_index(self, column_name):

        return self.return_fieldnames().index(column_name)

    def return_fieldnames(self):

        fieldnames = []
        for table_field in self.table_fields:
            fieldnames.append(table_field.name)

        return fieldnames


class TableRecord(object):
    """
    A TableRecord class is a building block object of a Table object. It represents a single row of a Table.
    The TableRecord holds data for a Table row. Its core structure is the "items" attribute, a list of data values in
    sequential order of the Table's column headers.
    """

    def __init__(self):
        """
        Initialize the TableRecord object.
        """

        # "items" is a list that holds the TableRecord's data values (can be different data types)
        self.items = []

        # "null_values" is a list of values from the original table that represent NULL values
        self.null_values = None

    def add_item(self, item):
        """
        Add a data value item to the TableRecord items attribute list.

        Args:
            item (any data type): a data value to add to the TableRecord's items attribute list

        Return: None
        """

        # Add the data value item to the TableRecord's items attribute list.
        self.items.append(item)


class TableField(object):
    """
    A TableField class is a building block object of a Table object. It represents a single column of a Table.
    The TableField holds data for a Table column. Its core structure is the "items" attribute, a list of data values in
    sequential order of the Table's row entries.
    """

    def __init__(self, column_name):
        """
        Initialize the TableField object.

        Args:
            column_name: the name of the Table column that the TableField object is representing.
        """

        # "name" is a string that is the Table column's name.
        self.name = column_name

        # "items" is a list that holds the TableField's data values  (must be the same data type, Nones allowed)
        self.items = []

        # "data_type" is the Python data type class that represents the items in the TableField's items attribute list
        self.data_type = None

        # "null_values" is a list of values from the original table that represent NULL values
        self.null_values = []

    def __is_data_type(self, data_type_to_check):
        """
        Check if the items in the column are of the desired data type. Pass over None values. Only assess the column
         based off of the non-None values.

         Args:
            data_type_to_check: The data type to check if the column items match.

        Return: Boolean that specifies if the items in the column are of the specified data type.
        """

        # Boolean to determine if the items are all of the expected data type or None.
        # Set to TRUE until proven FALSE.
        is_correct_type = True

        boolean_dic = {"TRUE": True, "FALSE": False, "1": True, "0": False}

        # Iterate over the TableField items.
        for item in self.items:

            # If the item is equal to None, pass and do not run any further checks.
            if item is None:
                pass

            # If checking for Boolean values and the item is not a Boolean value, set the is_correct_type to FALSE.
            elif data_type_to_check.upper() == "BOOLEAN" and item.upper() not in boolean_dic.keys():
                is_correct_type = False

            # If checking of INT values and the item is not an int value, set the is_correct_type to FALSE.
            elif data_type_to_check.upper() == "INT":
                try:
                    int(item)
                except:
                    is_correct_type = False

            # If checking for FLOAT values and the item is not a float value, set the is_correct_type to FALSE.
            elif data_type_to_check.upper() == "FLOAT":
                try:
                    float(item)
                except:
                    is_correct_type = False

            # If checking for STR values and the item is not a string value, set the is_correct_type to FALSE.
            elif data_type_to_check.upper() == "STR":
                try:
                    str(item)
                except:
                    is_correct_type = False

            if not is_correct_type:
                break

        return is_correct_type

    def __convert_data_type(self, output_data_type):
        """
        Comvert the items in the column (string) to the desired data type.

        Args:
            output_data_type (str): the desired data type of which to convert the column items

        Return:
            None
        """

        #  A list to hold the column items that have been converted to the desired data type.
        converted_list = []

        # Iterate over the items in the column.
        for item in self.items:

            # If the item is None, retain the None value as that item's value. Add None to the converted_list.
            if item is None:
                converted_list.append(None)

            # If the conversion data type is Boolean, convert the item to a Boolean value.
            # Add the converted item to the converted_list.
            elif output_data_type.upper() == "BOOLEAN":
                boolean_dic = {"TRUE": True, "FALSE": False, "1": True, "0": False}
                converted_list.append(boolean_dic[item.upper()])

            # If the conversion data type is an integer, convert the item to an Int value.
            # Add the converted item to the converted_list.
            elif output_data_type.upper() == "INT":
                converted_list.append(int(item))

            # If the conversion data type is a float, convert the item to a Float value.
            # Add the converted item to the converted_list.
            elif output_data_type.upper() == "FLOAT":
                converted_list.append(float(item))

            # If the conversion data type is a string, convert the item to a Str value.
            # Add the converted item to the converted_list.
            elif output_data_type.upper() == "STR":
                converted_list.append(str(item))

        # Overwrite the old column items with the converted column items.
        self.items = converted_list

    def assign_data_type(self):
        """
        Convert the column contents to the correct data type. By default, the logic attempts to determine the correct
        data type based upon the content items. Handles Boolean, integers, floats and strings. Need to figure out how
        to gracefully handle dictionaries, lists, and tuples.

        Return: None
        """

        # If the column is a column of only None values, assign the data_type to None.
        if all(x == self.items[0] for x in self.items) and self.items[0] is None:
            self.data_type = None

        # If there is at least one value other than None in the column, determine the column data type.
        else:

            # Enumerator of DataTypes
            # In specific order to make sure that the logic assumes the correct data type.
            class DataTypes(enum.Enum):
                Boolean, Int, Float, Str = bool, int, float, str

            # Iterate over the data types.
            for data_type in DataTypes:

                # If the items in the column are of the data type, continue.
                if self.__is_data_type(data_type.name):

                    # Convert the data values (all strings) in the column to the assumed data type.
                    self.__convert_data_type(str(data_type.name))

                    # Assign the data type of the column to the assumed data type.
                    self.data_type = data_type.value
                    break

    def assign_nulls(self):
        """
        Convert the value in a list that represent null values to a None value. This function requires that the
         data list items that match the specified null values are of the same data type.
        For example:
        1.0 (float) != 1 (int) != True (Boolean) != "1" (str)

            Args:
                data_list (list): a list of items to check for null values
                null_values (list): a list of values that represent null values. This list can be mixed type.

            Return: an updated data list with the substituted null values as None value.
            """

        # Iterate over the null values.
        for null_value in self.null_values:

            # Iterate over the data list items.
            for item in self.items:

                # If the null value is equal to the data list item. The data types must also match. Python doesn't
                # require that two objects have the same type for them to be considered equal.
                if null_value == item and isinstance(item, type(null_value)):

                    # Get the index of the null value in the data list.
                    index = self.items.index(item)

                    # Assign the null value in the data list to None.
                    self.items[index] = None

# ################################################## TEST ENVIRONMENT ###################################################
#
# from geoprocessor.core.DataStore import DataStore
# import geoprocessor.util.string_util as string_util
# import sqlalchemy
# import csv
#
#
# def __read_table_from_datastore(ds, table_name, table_id, top, sql, cols_to_include, cols_to_exclude):
#     """
#     Creates a GeoProcessor table object from a DataStore table.
#
#     Args:
#         ds (obj): the DataStore object that contains the DataStore table to read
#         table_name (str): the name of the DataStore table to read
#             Can be None if using the Sql method or SqlFile method.
#         table_id (str): the id of the GeoProcessor Table that is to be created
#         top (int): the number of rows from the DataStore Table to read
#             Can be None if using the Sql method or SqlFile method.
#         sql (str): the SQL statement to select out the desired data from the DataStore table.
#             Can be None if using the DataStoreTable method.
#         cols_to_include (list): a list of glob-style patterns representing the DataStore Table columns to read
#             Can be None if using the Sql method or SqlFile method.
#         cols_to_exclude (list): a list of glob-style patterns representing the DataStore Table columns to read
#             Can be None if using the Sql method or SqlFile method.
#
#     Return: A GeoProcessor Table object.
#     """
#
#     # Read the DataStore table into a DataStore Table object.
#     ds_table_obj = ds.metadata.tables[table_name]
#
#     # Create a GeoProcessor Table object.
#     table = Table(table_id)
#
#     # Query the DataStore table. The allows access to table information.
#     q = ds.session.query(ds_table_obj)
#
#     # Select all fields and rows of the table.
#     s = sqlalchemy.sql.select([ds_table_obj])
#
#     # Get a list of all of the column names.
#     table_cols = [col["name"] for col in q.column_descriptions]
#
#     # Sort the list of column names to create create a second list that only includes the columns to read.
#     table_cols_to_read = string_util.filter_list_of_strings(table_cols, cols_to_include, cols_to_exclude, True)
#
#     # Sort the table_cols_to_read list to order in the same order as the table columns in the DataStore table.
#     cols_names = ds.return_col_names(table_name)
#     table_cols_to_read = [col_name for col_name in cols_names if col_name in table_cols_to_read]
#
#     # If a SQL statement has been specified, then continue.
#     if sql:
#
#         # Run the SQL statement
#         result_from_sql = ds.connection.execute(sql)
#
#         # Get the first row from the result set.
#         row = result_from_sql.fetchone()
#
#         # An empty list to hold the columns that were included in the result set in response to the user-specified
#         # sql.
#         included_cols = []
#
#         # Iterate over all of the available columns in the DataStore table.
#         for table_col in table_cols:
#
#             # Try to read the value of the DataStore table column. If it does not throw an error, it is known that
#             # the column was included in the result set of the user-specified SQL statement. Add the column name to
#             # the included_cols list.
#             try:
#                 value = row[table_col]
#                 included_cols.append(table_col)
#
#             # If an error is thrown, it is known that the column was not included in the result set of the
#             #  user-specified SQL statement. Do not add the column name to the included_cols list.
#             except:
#                 pass
#
#         # Iterate over the DataStore table columns that do have results from the user-specified SQL statement.
#         for included_col in included_cols:
#
#             # Create a TableField object and assign the field "name" as the column name.
#             table_field = TableField(included_col)
#
#             # Run the SQL statement
#             result_from_sql = ds.connection.execute(sql)
#
#             # Iterate over the rows of the DataStore table data.
#             for row in result_from_sql:
#                 # Add the row data for the column to the item list of the TableField.
#                 table_field.items.append(row[included_col])
#
#             # Determine the data type of the column's data.
#             # A list that holds the data type for each data value in the column.
#             data_types = []
#
#             # Iterate over each of the data values in the column.
#             for item in table_field.items:
#
#                 # Add the data type of the item to the data_types list. Ignore data values that are None.
#                 if item is not None:
#                     data_types.append(type(item))
#
#             # If the data_types list is empty, assume that all values in the column are set to None.
#             if not data_types:
#                 table_field.data_type = None
#
#             # Set the data_type attribute of the TableField object to that specified in the data_types list.
#             elif all(x == data_types[0] for x in data_types):
#                 table_field.data_type = data_types[0]
#
#             # All of the data types in the list should be the same value because database columns require that
#             # the data in each column is only one data type. If more than one data type exists in the data_types
#             # list, print an error message.
#             else:
#                 print("There was an error. Not all the data types are the same.")
#
#             # Add the TableField object to the Table attributes.
#             table.add_table_field(table_field)
#
#             # Get the number of row entries in the TableField. This will be the same number for each of the
#             # TableField objects so only the count of the entries in the last TableField object is used in the
#             # remaining code.
#             table.entry_count = len(table_field.items)
#
#     # If a SQL statement has not been specified, continue.
#     else:
#
#         # Iterate over the column names to read.
#         for col in table_cols_to_read:
#
#             # Create a TableField object and assign the field "name" as the column name.
#             table_field = TableField(col)
#
#             # Run the SQL query to get the DataStore tables' data. Save as result variable.
#             result = ds.connection.execute(s)
#
#             # If configured to limit the table read to a specified number of top rows, continue.
#             if top:
#
#                 # Counter to track the number of rows read into the Table Field items.
#                 count = 0
#
#                 # Iterate over the rows of the DataStore table data.
#                 for row in result:
#
#                     # If the current row count is less than the desired row count, continue.
#                     while count < top:
#                         # Add the row data for the column to the item list of the TableField. Increase the counter.
#                         table_field.items.append(row[col])
#                         count += 1
#
#             # If configured to read all rows of the DataStore table, continue.
#             else:
#
#                 # Iterate over the rows of the DataStore table data.
#                 for row in result:
#                     # Add the row data for the column to the item list of the TableField.
#                     table_field.items.append(row[col])
#
#             # Determine the data type of the column's data.
#             # A list that holds the data type for each data value in the column.
#             data_types = []
#
#             # Iterate over each of the data values in the column.
#             for item in table_field.items:
#
#                 # Add the data type of the item to the data_types list. Ignore data values that are None.
#                 if item is not None:
#                     data_types.append(type(item))
#
#             # If the data_types list is empty, assume that all values in the column are set to None.
#             if not data_types:
#                 table_field.data_type = None
#
#             # Set the data_type attribute of the TableField object to that specified in the data_types list.
#             elif all(x == data_types[0] for x in data_types):
#                 table_field.data_type = data_types[0]
#
#             # All of the data types in the list should be the same value because database columns require that the
#             # data in each column is only one data type. If more than one data type exists in the data_types list,
#             # print an error message.
#             else:
#                 print("There was an error. Not all the data types are the same.")
#
#             # Add the TableField object to the Table attributes.
#             table.add_table_field(table_field)
#
#             # Get the number of rows in the TableField. This will be the same number for each of the TableField
#             # objects so only the count of the entries in the last TableField object is used in the remaining code.
#             table.entry_count = len(table_field.items)
#
#     # Iterate over the number of row entries.
#     for i_row in range(table.entry_count):
#
#         # Create a TableRecord object.
#         table_record = TableRecord()
#
#         # Iterate over the table fields.
#         for i_col in range(len(table.table_fields)):
#             # Get the data value for the specified row and the specified field.
#             new_item = table.table_fields[i_col].items[i_row]
#
#             # Assign that data value to the items list of the TableRecord.
#             table_record.add_item(new_item)
#
#         # Add the TableRecord object to the Table attributes.
#         table.table_records.append(table_record)
#
#     # Return the GeoProcessor Table object.
#     return table
#
#
# def __read_table_from_delimited_file(path, table_id, delimiter, header_count, null_values):
#     """
#     Creates a GeoProcessor table object from a delimited file.
#
#     Args:
#         path (str): the path to the delimited file on the local machine
#         table_id (str): the id of the GeoProcessor Table that is to be created
#         delimiter (str): the delimiter of the input file
#         header_count (int): the number of rows representing the header content (not data values)
#         null_values (list): list of strings that are values in the delimited file representing null values
#
#     Return: A GeoProcessor Table object.
#     """
#
#     # Create a table object
#     table = Table(table_id)
#
#     # Open the csv file to read.
#     with open(path, 'r') as csvfile:
#
#         # Pass the csv file to the csv.reader object. Specify the delimiter.
#         csvreader = csv.reader(csvfile, delimiter=delimiter)
#
#         # TODO egiles 2018-06-25 Need to determine what column headers will be if there are no column headers in
#         # TODO the original delimited file (where header_count = 0).
#
#         # By default, the column headers are retrieved as the last line of the header rows.
#         # Get the column headers.
#         for i in range(header_count):
#             col_headers = next(csvreader)
#
#         # Iterate over the number of columns specified by a column header name.
#         for i in range(len(col_headers)):
#
#             # Create a TableField object and assign the field "name" as the column header name.
#             table_field = TableField(col_headers[i])
#
#             # An empty list to hold the items within the TableField.
#             col_content = []
#
#             # Reset the csv reader to start the reading of the csv file at the first row.
#             csvfile.seek(0)
#
#             # Skip the header rows.
#             for i_head in range(header_count):
#                 next(csvreader)
#
#             # Iterate over the non-header rows and append the column items to the col_content list.
#             for row in csvreader:
#                 col_content.append(row[i])
#
#             # Add the column contents to the TableField object.
#             table_field.items = col_content
#
#             # Set the null values
#             table_field.null_values = null_values
#
#             # Convert the data value that represent null values into None value.\
#             table_field.assign_nulls()
#
#             # Convert the column contents to the correct data type.
#             table_field.assign_data_type()
#
#             # Add the updated table field object to the Table attribute.
#             table.add_table_field(table_field)
#
#         # Get the number of row entries.
#         table.entry_count = len(table_field.items)
#
#     # Iterate over the number of row entries.
#     for i_row in range(table.entry_count):
#
#         # Create a TableRecord object.
#         table_record = TableRecord()
#
#         # Iterate over the table fields.
#         for i_col in range(len(table.table_fields)):
#             new_item = table.table_fields[i_col].items[i_row]
#             table_record.add_item(new_item)
#
#         # Add the table record to the Table attributes.
#         table.table_records.append(table_record)
#
#         # Return the GeoProcessor Table object.
#     return table
#
#
# def get_datastore_col_name(column_map, column_name):
#
#     if column_name in column_map.keys():
#         return column_map[column_name]
#     else:
#         return column_name
#
#
# column_map = {"first":"first_name", "last":"last_name"}
#
# # Create a DataStore object
# ds = DataStore("ds")
#
# # Connect to a database
# ds.get_db_uri_postgres("localhost", "dvdrental", "postgres", "postgres")
# ds.open_db_connection()
#
# # Specify the name of the database table to read
# table_to_read = "actor"
#
# # Read a database table
# database_table = __read_table_from_datastore(ds, table_to_read, table_to_read, None, None, ["*"], [""])
#
# # Read a delimited file table
# path_to_delimited_file = r"C:\Users\egiles\Desktop\example.txt"
# delimited_table = __read_table_from_delimited_file(path_to_delimited_file, "delimited", ",", 2, ["NULL"])
#
# # Specify the list of columns in the delimited_table to write to the database_table.
# cols_to_write = ["actor_id", "first", "last"]
#
# row_data_to_insert = []
#
# # Get the SqlAlchemy version of the database_table
# database_table_sqlalchemy = ds.return_sql_alchemy_table_object(table_to_read)
#
# # Iterate over each record in the delimited table.
# for table_record in delimited_table.table_records:
#
#     record_dic = {}
#
#     # Iterate over the columns to write.
#     for col_to_write in cols_to_write:
#
#         # Get the column index.
#         index = delimited_table.return_column_index(col_to_write)
#
#         # Get the data value
#         value = table_record.items[index]
#
#         # Get the corresponding column name in the database table.
#         database_col_name = get_datastore_col_name(column_map, col_to_write)
#
#         # Add the value to the record_dic.
#         # KEY: the name of the database column to write to
#         # VALUE: the value to write to the database table
#         record_dic[database_col_name] = value
#
#     # Add this row data dictionary to the master row list.
#     row_data_to_insert.append(record_dic)
#
#
#
# method = "insert"
#
# if method.upper() == "INSERT":
#
#     ins = database_table_sqlalchemy.insert()
#     result = ds.connection.execute(ins, row_data_to_insert)
#     print(result)
#
# # if method.upper() == "DELETE":
# #
# #     # Iterate over the delimited table records.
# #     for table_record in database_table.table_records:
# #
# #         # Iterate over the delimited table column names to write.
# #         for col_to_write in cols_to_write:
# #
# #             # Get the column index of the delimited file.
# #             index = delimited_table.return_column_index(col_to_write)
# #
# #             # Get the corresponding column name in the database table.
# #             database_col_name = get_datastore_col_name(column_map, col_to_write)
# #
# #             # Get the Sql Alchemy version of the column object.
# #             database_col_sqlalchemy = ds.return_sql_alchemy_column_object(database_col_name, table_to_read)
# #
# #             database_col_sqlalchemy == table_record.items[index]
# #
# #
# #
# #
# #         for table_record in d_table.table_records:
# #             del_st = ds_table_obj.delete().where(
# #                 ds.return_sql_alchemy_column_object("first_name", table_name) == table_record.items[0] and
# #                 ds.return_sql_alchemy_column_object("last_name", table_name) == table_record.items[1])
# #             res = ds.connection.execute(del_st)
# #
# # # CREATE THE DATA STORE CONNECTION
# # ds = DataStore("ds")
# # ds.get_db_uri_postgres("localhost", "dvdrental", "postgres", "postgres")
# # ds.open_db_connection()
# #
# # # GET THE DATA STORE TABLE
# # table_name = "actor"
# # ds_table = __read_table_from_datastore(ds, table_name, table_name, None, None, ["*"], [""])
# #
# # # GET THE DELIMITED FILE TABLE
# # d_table = __read_table_from_delimited_file(r"C:\Users\egiles\Desktop\example.txt", "delimited", ",", 2, ["NULL"])
# #
# # # GET DICTIONARY KEY: FIELD NAME VALUE: CORRESPONDING RECORD VALUE
# # dic_list = []
# # for table_record in d_table.table_records:
# #     dic = {}
# #     for i in range(len(table_record.items)):
# #         dic[d_table.return_fieldnames()[i]] = table_record.items[i]
# #     dic_list.append(dic)
# #
# # # GET THE SQL ALCHEMY DATA STORE TABLE
# # # Read the DataStore table into a DataStore Table object.
# # ds_table_obj = ds.metadata.tables[table_name]
# #
# # # DETERMINE IF DELETE OR INSERT
# # delete = True
# #
# # # INSERT THE DELIMITED FILE RECORDS INTO THE DATABASE TABLE
# # if not delete:
# #     ins = ds_table_obj.insert()
# #     ds.connection.execute(ins, dic_list)
# #
# # # DELETE RECORDS FROM THE DATABASE TABLE
# # if delete:
# #
# #
# #     # # Query the DataStore table. The allows access to table information.
# #     # q = ds.session.query(ds_table_obj)
# #
# #     for table_record in d_table.table_records:
# #         del_st = ds_table_obj.delete().where(
# #             ds.return_sql_alchemy_column_object("first_name", table_name) == table_record.items[0] and
# #             ds.return_sql_alchemy_column_object("last_name", table_name) == table_record.items[1])
# #         res = ds.connection.execute(del_st)
