# CommandParameterMetadtaa - class to hold command parameter metadata
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

class CommandParameterMetadata(object):
    """
    Metadata for the command parameters, a list of which is maintained as
    AbstractCommand.command_parameter_metadata.
    This information is used to output parameters in the proper order in AbstractCommand.to_string()
    and also provide basic validation data (valid parameter names, type).
    Validation requires more effort when the allowed value is an enumeration, etc.
    """

    def __init__(self, parameter_name, parameter_type, parameter_description=None, default_value=None,
                 editor_tooltip=None, validator_function=None):
        # Parameter name should be in format WordWord
        self.parameter_name = parameter_name

        # Parameter description should be short, for editor right size
        self.parameter_description = parameter_description

        # Parameter default value, as string
        self.default_value = default_value

        # Parameter tooltip
        self.editor_tooltip = editor_tooltip

        # Parameter type should match the output of the type(), for example type(""), type(1), type(1.0).
        # Use string for complex types that will require parsing in the command.
        self.parameter_type = parameter_type

        # TODO smalers 2018-07-27 need to indicate whether required, optional, or depends on input

        # Validator function to be called to validate the command parameter
        # TODO smalers 2017-12-30 This may be removed since validation is often more complicated
        # and is implemented by design in each command's check_command_parameters function
        self.validator_function = validator_function

# Functions that can be used as static functions outside of the class,
# for example to process the full list of CommandParameterMetadata objects.


def get_parameter_names(parameter_metadata_list):
    """
    Return the list of parameter names in a list, extracted from the metadata list.

    Args:
        parameter_metadata_list:  List of CommandParameterMetadata.
    Returns:
        List of string containing parameter names from metadata.
    """
    parameter_names = []
    if parameter_metadata_list is not None:
        for meta in parameter_metadata_list:
            parameter_names.append(meta.parameter_name)

    return parameter_names
