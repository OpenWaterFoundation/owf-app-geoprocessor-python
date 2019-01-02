# command_status_type - command status types
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2019 Open Water Foundation
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

from enum import Enum


class CommandStatusType(Enum):
    """
    Possible values of command status.
    """
    UNKNOWN = -1
    INFO = 0
    SUCCESS = 1
    WARNING = 2
    FAILURE = 3

    __status_list = [INFO, SUCCESS, WARNING, FAILURE]

    @classmethod
    def get_command_status_types(cls, sort=False):
        """
        Return the list of valid command status.

        Args:
            sort:  If True, sort alphabetically.  If False, return in order of severity (default).

        Returns:
            The list of status types, for example for use in command parameter choice.

        """
        if sort:
            # Sort alphabetically
            return [CommandStatusType.FAILURE,
                    CommandStatusType.INFO,
                    CommandStatusType.SUCCESS,
                    CommandStatusType.WARNING]
        else:
            # Return in order of severity (good to bad)
            return [CommandStatusType.INFO,
                    CommandStatusType.SUCCESS,
                    CommandStatusType.WARNING,
                    CommandStatusType.FAILURE]

    @classmethod
    def get_command_status_types_as_str(cls, sort=False):
        """
        Return the list of valid command status as list of str.

        Args:
            sort:  If True, sort alphabetically.  If False, return in order of severity (default).

        Returns:
            The list of status types as str, for example for use in command parameter choice.

        """
        # First get the list of types
        command_status_types = cls.get_command_status_types(sort=sort)

        # Convert to strings
        command_status_types_as_str = []
        for command_status_type in command_status_types:
            command_status_types_as_str.append(command_status_type.name)

        return command_status_types_as_str

    @classmethod
    def max_severity(cls, command_status1, command_status2):
        """
        Return the maximum (most severe) status of the given two status.

        Args:
            command_status1: First status to check such as 'SUCCESS' (indicates severity).
            command_status2: Second status to check such as 'WARNING' (indicates severity).

        Returns:
            The maximum (most severe) status of the given two status.
            For example, FAILURE is more severe than WARNING.
        """
        # If a true enumeration were used, then the comparisons could be simple numeric.
        # However, since Python just defines the strings, use the number_value function to help.
        if command_status1.value > command_status2.value:
            return command_status1
        elif command_status2.value > command_status1.value:
            return command_status2
        else:
            # They are the same
            return command_status1

    def __str__(self):
        """
        Format the enumeration value as a string - just return the name.

        Returns:

        """
        return self.name

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

        warning_short = "Warn"
        failure_short = "Fail"
        if ignore_case:
            # Input string can be anything so convert to uppercase for comparison
            str_value = str_value.upper()
            warning_short = warning_short.upper()
            failure_short = failure_short.upper()

        if str_value == CommandStatusType.UNKNOWN.name:
            return CommandStatusType.UNKNOWN
        elif str_value == CommandStatusType.INFO.name:
            return CommandStatusType.INFO
        elif str_value == CommandStatusType.SUCCESS.name:
            return CommandStatusType.SUCCESS
        elif str_value == CommandStatusType.WARNING.name or str_value == warning_short:
            return CommandStatusType.WARNING
        elif str_value == CommandStatusType.FAILURE.name or str_value == failure_short:
            return CommandStatusType.FAILURE
        else:
            return None
