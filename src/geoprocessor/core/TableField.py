# TableField - class to represent table field information
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

import enum


class TableField(object):
    """
    A TableField class is a building block object of a Table object. It represents a single column of a Table.
    The TableField holds data for a Table column. Its core structure is the "items" attribute, a list of data values in
    sequential order of the Table's row entries.
    """

    def __init__(self, data_type: type, column_name: str, description: str = "", width: int = None,
                 precision: int = None, units: str = ""):
        """
        Initialize the TableField object.

        Args:
            column_name: the name of the Table column that the TableField object is representing.
        """

        # "name" is a string that is the Table column's name.
        self.name: str = column_name

        # Description for field.
        self.description: str = description

        # Data units for field.
        self.units: str = units

        # Width of the field (maximum characters for strings or number width in characters, used when displaying data.
        # A value of None means unlimited.
        self.width: int = width

        # Precision applied to numbers (e.g., 3 1in 11.3 formatting).
        # A value of None means not used.
        self.precision: int = precision

        # "items" is a list that holds the TableField's data values  (must be the same data type, Nones allowed)
        # TODO smalers 2020-11-14 this design stored table data in columns - for now rely on record-based storage
        # self.items = []

        # "data_type" is the Python data type class that represents the items in the TableField's items attribute list
        # - bool
        # - float
        # - int
        # - str
        # - etc
        self.data_type: type = data_type

        # "null_values" is a list of values from the original table that represent NULL values
        # TODO smalers 2020-11-14 was this used with Pandas?  No need for this since Python supports None
        #  for generic case and NaN for floating point numbers
        # self.null_values = []

    def x__is_data_type(self, data_type_to_check):
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
                # noinspection PyBroadException
                try:
                    int(item)
                except Exception:
                    is_correct_type = False

            # If checking for FLOAT values and the item is not a float value, set the is_correct_type to FALSE.
            elif data_type_to_check.upper() == "FLOAT":
                # noinspection PyBroadException
                try:
                    float(item)
                except Exception:
                    is_correct_type = False

            # If checking for STR values and the item is not a string value, set the is_correct_type to FALSE.
            elif data_type_to_check.upper() == "STR":
                # noinspection PyBroadException
                try:
                    str(item)
                except Exception:
                    is_correct_type = False

            if not is_correct_type:
                break

        return is_correct_type

    def x__convert_data_type(self, output_data_type):
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

    def x_assign_data_type(self):
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
            # TODO smalers 2020-11-14 currently using internal Python types
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

    def x_assign_nulls(self):
        """
        Convert the value in a list that represent null values to a None value. This function requires that the
        data list items that match the specified null values are of the same data type.

        For example:

        1.0 (float) != 1 (int) != True (Boolean) != "1" (str)

            Args:

            Return: an updated data list with the substituted null values as None value.
            """

        # TODO smalers 2020-01-16 need to evaluate what this was...
        #        data_list (list): a list of items to check for null values
        #        null_values (list): a list of values that represent null values. This list can be mixed type.

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
