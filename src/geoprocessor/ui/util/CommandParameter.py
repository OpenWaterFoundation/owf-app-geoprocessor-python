# CommandParameter - class to hold information about a command's parameter, used with UI
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


class CommandParameter(object):
    """
    Hold information required for the user interface about a command parameter.
    This can be added to the core/CommandParameterMetadata in future development.
    For now, this class is separate to keep the core and the UI information separate.
    """

    def __init__(self, name: str, description: str, optional: bool, tooltip: str,
                 default_value_description: str = None) -> None:
        """
        Initialize the CommandParameter instance.

        Args:
            name (str): the name of the command parameter
            description(str): the BRIEF description of the command parameter
            optional (bool): boolean to determine if the command parameter is required or optional.
                If TRUE, the parameter is optional.
                If FALSE, the parameter is required.
            tooltip (str): a string that will appear in the UI when the user hovers over the command parameter's
                input field. Can be None and no tooltip will appear.
            default_value_description (str): the default value. Can be None and no default value will be displayed
                in the dialog window. Default: None
        """

        # Name of the command parameter.
        self.name = name

        # Full description of the command parameter.
        self.description = self.create_full_description(description, optional, default_value_description)

        # Whether the command parameter is required or optional.
        self.optional = optional

        # Hint associated with the command parameter.
        self.tooltip = tooltip

        # Default value of the command parameter, if applicable.
        self.default_value_desc = default_value_description

    @staticmethod
    def create_full_description(brief_description: str, optional: bool, default_value: str) -> str:
        """
        Converts pieces of the command parameter's description into a full and fully-formatted description that will
        display on the command parameter UI dialog window.

        Args:
            brief_description (str): a brief description of the command parameter
            optional (bool): boolean to determine if the command parameter is required or optional.
                If TRUE, the parameter is optional.
                If FALSE, the parameter is required.
            default_value (str): the default value. Can be None.

        Return: a command parameter's full description
        """

        # If the parameter is configured to be optional, include the word "Optional" in the full description.
        if optional:
            required = "Optional"

        # If the parameter is configured to be required, include the word "Required" in the full description.
        else:
            required = "Required"

        # If a default value is specified, add the default value in the full description.
        if default_value:
            full_description = "{} - {}\n(default: {})".format(required, brief_description, default_value)

        # If a default value is NOT specifeid, only inlcude the optional setting and the brief description in the
        # full description.
        else:
            full_description = "{} - {}".format(required, brief_description)

        # Return the full description as a string.
        return full_description
