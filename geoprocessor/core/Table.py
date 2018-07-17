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