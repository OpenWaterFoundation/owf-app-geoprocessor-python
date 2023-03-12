# IfExistsActionType - actions to take if a data object exists
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


class IfExistsActionType(Enum):
    """
    Enumeration for If*Exists actions, for example IfGeoLayerIDExists.
    These are typically used in commands to allow users to indicate how to handle re-creating data objects.

    String representation is mixed case because it is used in configuration files.

    Numerical values indicate increasing severity.
    """
    Replace = 1
    ReplaceAndWarn = 2
    Warn = 3
    Fail = 4

    @classmethod
    def get_ifexistsaction_types(cls) -> [IfExistsActionType]:
        """
        Return the list of valid IfExistAction types.

        Args:
            None.

        Returns:
            The list of IfExistAction types.
        """
        # Return the enumeration types
        return [IfExistsActionType.Replace,
                IfExistsActionType.ReplaceAndWarn,
                IfExistsActionType.Warn,
                IfExistsActionType.Fail
                ]

    @classmethod
    def get_ifexistsaction_types_as_str(cls, include_blank: bool = False) -> [str]:
        """
        Return the list of valid IfExistsAction types as a list of str.

        Args:
            include_blank (bool): if True, include a blank string at the front, useful for UI choices.

        Returns:
            The list of IfExistsAction types as str, for example for use in a command parameter choice.
        """
        ifexistsaction_types = [str(IfExistsActionType.Replace),
                                str(IfExistsActionType.ReplaceAndWarn),
                                str(IfExistsActionType.Warn),
                                str(IfExistsActionType.Fail)
                               ]
        if include_blank:
            ifexistsaction_types.insert(0, '')
        return ifexistsaction_types

    @staticmethod
    def value_of_ignore_case(ifexistsaction_type: str) -> IfExistsActionType or None:
        """
        Get an instance of the enumeration based on string key, ignoring case of the strings.

        Args:
            ifexistsaction_type: The "if exists" action type to look up.

        Returns:
            IfExistsActionType instance matching the ifexistsaction_type, or None if no match.
        """
        if ifexistsaction_type is None:
            return None
        ifexistsaction_type_upper = ifexistsaction_type.upper()
        for name, member in IfExistsActionType.__members__.items():
            name_upper = name.upper()
            if name_upper == ifexistsaction_type_upper:
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
