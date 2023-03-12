# ExtractGeoLayerSelectionConditionType - selection condition type enumeration for ExtractGeoLayer command
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

# The following is needed to allow type hinting -> GeoLayer, and requires Python 3.7+
# See:  https://stackoverflow.com/questions/33533148/
#         how-do-i-specify-that-the-return-type-of-a-method-is-the-same-as-the-class-itsel
from __future__ import annotations

from enum import Enum


class ExtractGeoLayerSelectionConditionType(Enum):
    """
    Possible values of command status.
    These don't exactly mach QGIS documentation but are phrased for use in user interfaces and commands.
    """
    Intersects = 0
    Contains = 1
    Disjoint = 2
    Equals = 3
    Touches = 4
    Overlaps = 5
    AreWithin = 6
    Crosses = 7

    # The enumeration automatically contains "name" that has the value of the left side above,
    # and "value" that has the value on the right side above.
    # Therefore, use mixed case for the name, which will be used in human-facing interfaces.

    def __str__(self):
        """
        Format the enumeration value as a string - just return the name.

        Returns:

        """
        return self.name

    @classmethod
    def names(cls, sort=False) -> [str]:
        """
        Returns:  A list of the enumeration names, unsorted.

        Args:
            sort (bool): Whether to sort the list of names (default=False).
        """
        names = [member.name for member in ExtractGeoLayerSelectionConditionType]
        if sort:
            # Sort the names alphabetically.
            names.sort()
        return names

    @classmethod
    def value_of(cls, str_value, ignore_case=False) -> ExtractGeoLayerSelectionConditionType or None:
        """
        Look up the value of an enumeration given the string value.
        This is useful for standardizing internal values to the specific enumeration value
        whereas some code may accept variants, such as 'AreWithin' and 'Within'.

        Args:
            str_value (str): String value of the enumeration.
            ignore_case (bool): Whether to ignore case (default = False).

        Returns:
            Value of the enumeration, or None if not matched.
        """

        for item in ExtractGeoLayerSelectionConditionType:
            if ignore_case:
                str_value = str_value.upper()
                item_name = item.name.upper()
            else:
                item_name = item.name
            if str_value == item_name:
                return item

        # Was not matched.
        return None
