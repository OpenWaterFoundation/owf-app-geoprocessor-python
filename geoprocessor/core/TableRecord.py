# TableRecord - class to hold a row of table data
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

from typing import Any


class TableRecord(object):
    """
    A TableRecord class is a building block object of a Table object.
    The TableRecord holds data for a Table row. Its core structure is the "items" attribute, a list of data values in
    sequential order of the Table's fields (columns).
    """

    def __init__(self):
        """
        Initialize the TableRecord object.
        """

        # "values" is a list that holds the TableRecord's data values (can be different data types)
        self.values: [Any] = []

        # "null_values" is a list of values from the original table that represent NULL values
        # TODO smalers 2020-11-14 this is left over from earlier implementation.  Commnent out for now.
        # self.null_values = None

    def add_field_value(self, value):
        """
        Add a data value to the TableRecord value list.

        Args:
            value (Any): a data value to add to the TableRecord's items attribute list

        Return: None
        """

        # Add the data value item to the TableRecord's items attribute list.
        self.values.append(value)
