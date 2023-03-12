# GeoLayerSymbolClassificationType - classification type enumeration for GeoLayerSymbol
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

# The following is needed to allow type hinting -> GeoLayer, and requires Python 3.7+.
# See:  https://stackoverflow.com/questions/33533148/
#         how-do-i-specify-that-the-return-type-of-a-method-is-the-same-as-the-class-itsel
from __future__ import annotations

from enum import Enum


class GeoLayerSymbolClassificationType(Enum):
    """
    Possible values of command status.
    """
    SINGLESYMBOL = 1
    GRADUATED = 2
    CATEGORIZED = 3

    def __str__(self):
        """
        Format the enumeration value as a string - just return the name.

        Returns:

        """
        return self.name

    def to_json(self) -> dict:
        """
        Return dictionary of class data to support JSON serialization using json package.
        Don't serialize all the data because daa are in the typical spatial data format.
        Instead, serialize what is needed to support web mapping and other visualization.
        """
        return {
            "classificationType": self.name
        }

    def to_json_string(self) -> str:
        """
        Return the classification type to use with JSON serialization.
        This version results in a simple string.
        """
        if self == self.CATEGORIZED:
            return "Categorized"
        elif self == self.GRADUATED:
            return "Graduated"
        elif self == self.SINGLESYMBOL:
            return "SingleSymbol"

    @classmethod
    def value_of(cls, str_value, ignore_case=False):
        """
        Look up the value of an enumeration given the string value.
        This is useful for standardizing internal values to the specific enumeration value
        whereas some code may accept variants, such as 'WARN' and 'FAIL'.

        Args:
            str_value (str): String value of the enumeration.
            ignore_case (bool): Whether or not to ignore case (default = False).

        Returns:
            Value of the enumeration, or None if not matched.
        """

        if str_value == GeoLayerSymbolClassificationType.SINGLESYMBOL.name:
            return GeoLayerSymbolClassificationType.SINGLESYMBOL
        elif str_value == GeoLayerSymbolClassificationType.GRADUATED.name:
            return GeoLayerSymbolClassificationType.GRADUATED
        elif str_value == GeoLayerSymbolClassificationType.CATEGORIZED.name:
            return GeoLayerSymbolClassificationType.CATEGORIZED
        else:
            return None
