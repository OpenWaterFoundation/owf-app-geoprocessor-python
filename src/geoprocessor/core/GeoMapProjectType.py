# GeoMapProjectType - map project types
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

# The following is needed to allow type hinting -> GeoLayer, and requires Python 3.7+
# See:  https://stackoverflow.com/questions/33533148/
#         how-do-i-specify-that-the-return-type-of-a-method-is-the-same-as-the-class-itsel
from __future__ import annotations

from enum import Enum


class GeoMapProjectType(Enum):
    """
    Enumeration for GeoMapProject type.

    String representation is mixed case because it is used in configuration files.

    Numerical values have no significance.
    """
    Dashboard = 1
    Grid = 2
    SingleMap = 3
    Story = 4

    @classmethod
    def get_geomapproject_types(cls) -> [GeoMapProjectType]:
        """
        Return the list of valid GeoMapProject types.

        Args:
            None.

        Returns:
            The list of GeoMapProject types.
        """
        # Return the enumeration types
        return [GeoMapProjectType.Dashboard,
                GeoMapProjectType.Grid,
                GeoMapProjectType.SingleMap,
                GeoMapProjectType.Story
                ]

    @classmethod
    def get_geomapproject_types_as_str(cls, include_blank: bool = False) -> [str]:
        """
        Return the list of valid GeoMapProject types as a list of str.

        Args:
            include_blank (bool): if True, include a blank string at the front, useful for UI choices.

        Returns:
            The list of GeoMapProject types as str, for example for use in a command parameter choice.
        """
        project_types = [str(GeoMapProjectType.Dashboard),
                         str(GeoMapProjectType.Grid),
                         str(GeoMapProjectType.SingleMap),
                         str(GeoMapProjectType.Story)
                        ]
        if include_blank:
            project_types.insert(0, '')
        return project_types

    @staticmethod
    def value_of_ignore_case(project_type: str) -> GeoMapProjectType or None:
        """
        Get an instance of the enumeration based on string key, ignoring case of the strings.

        Args:
            project_type: The project type to look up.

        Returns:
            GeoMapProjectType instance matching the project_type, or None if no match.
        """
        if project_type is None:
            return None
        project_type_upper = project_type.upper()
        for name, member in GeoMapProjectType.__members__.items():
            name_upper = name.upper()
            if name_upper == project_type_upper:
                return member
        # Nothing found
        return None

    def __str__(self) -> str:
        """
        Format the enumeration value as a string - just return the name.

        Returns:
            str:  Name for the enumeration value.
        """
        return self.name
