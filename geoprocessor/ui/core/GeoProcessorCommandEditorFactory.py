# GeoProcessorCommandEditorFactory - class to create command editor for a command string
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

import logging

import geoprocessor.util.command_util as command_util
from geoprocessor.ui.commands.abstract.GenericCommandEditor import GenericCommandEditor
from geoprocessor.ui.commands.editors.CommentBlockStartCommandEditor import CommentBlockStartCommandEditor
from geoprocessor.ui.commands.editors.CommentBlockEndCommandEditor import CommentBlockEndCommandEditor
from geoprocessor.ui.commands.editors.CommentCommandEditor import CommentCommandEditor
from geoprocessor.ui.commands.layers.ReadGeoLayerFromGeoJSON_Editor import ReadGeoLayerFromGeoJSON_Editor


class GeoProcessorCommandEditorFactory(object):
    """
    Factory to create command instances by examining command string.
    Only instantiates the command instance but does not parse the command string.
    The command string is parsed within the command class instance.
    """

    def __init__(self):
        """
        Initialize the command editor factory.
        """

        # Use the following for diagnostics and performance analysis - total count of commands processed
        self.command_created_count = 0

        # Use the following for error-handling - total number of unknown commands
        self.command_unknown_count = 0

    def new_command_editor(self, command, create_unknown_command_if_not_recognized=True):
        """
        Creates the editor for a command based on the command line of the command file.
        This can be called in the following cases:

        1. New command, such as from GeoProcessor UI menu, in which case the command string will be CommandName().
        2. Existing command, such as from GeoProcessor UI right-click/Edit Command menu,
           in which case the command string will be CommandName(ParameterName="ParameterValue",...)

        Args:
            command: command object
            create_unknown_command_if_not_recognized (bool) If TRUE, create an UnknownCommand when the input
            command is not recognized, if FALSE, throw an error.

        Returns:
            A command editor dialog instance that matches the command name.
            The command string is not parsed. TODO smalers 2018-07-28 need to evaluate this for existing commands.

        Raises:
            ValueError if the command is not recognized.
            See create_unknown_command_if_not_recognized=False in the constructor.
        """

        logger = logging.getLogger(__name__)

        # Get command name from the first part of the command.
        command_string = command.command_string
        command_string_trimmed = command_string.strip()
        paren_pos = command_string_trimmed.find('(')

        # Create booleans to know if the command is a variation of a comment command
        comment = False
        commentBlockStart = False
        commentBlockEnd = False

        # Special comment cases
        if command_string.startswith("#"):
            comment = True
        elif command_string.startswith("/*"):
            commentBlockStart = True
        elif command_string.startswith("*/"):
            commentBlockEnd = True

        # The symbol '(' was found.
        # Assume command of syntax CommandName(Param1="...",Param2="...").
        if paren_pos != -1:

            # Get command name from command string, command name is before the first open parenthesis.
            command_name = command_util.parse_command_name_from_command_string(command_string_trimmed)

            # Initialize the command editor class object if it is a valid command.
            # - only some commands have custom editors, depending on whether time has been spent building an editor
            # - alphabetize the commands
            # - use uppercase to reduce steps needed when comparing command names as case-insensitive.
            # TODO the following was commented out by @jurentie since GenericCommandEditor is always returned
            # command_name_upper = command_name.upper()
            # command_editor = None  # Editor for the given command
            # if command_name_upper == "READGEOLAYERFROMGEOJSON":
            #     # command_editor = ReadGeoLayerFromGeoJSON_Editor(command)
            #     print('GeoProcessorCommandEditorFactory.new_command_editor.READGEOLAYERFROMGEOJSON')
            #     # return command_editor

            # if command_editor is not None:
            #     # Successfully created an editor
            #     self.command_created_count = self.command_created_count + 1

            # If here the command name was not matched and additional steps are taken to throw an error.
            # Don't know the command so create an UnknownCommand or throw an exception.
            if create_unknown_command_if_not_recognized:
                logger.info("Command line is unknown command. Creating GenericCommandEditor for: " +
                            command_string_trimmed)
                # If the command is a basic comment return the appropriate
                # unique command editor
                if comment:
                    return CommentCommandEditor(command)
                # If the command is a comment block start return the
                # appropriate unique command editor
                elif commentBlockStart:
                    return CommentBlockStartCommandEditor(command)
                # If the command is a comment block end return the
                # appropriate unique command editor
                elif commentBlockEnd:
                    return CommentBlockEndCommandEditor(command)
                return GenericCommandEditor(command)
            else:
                logger.warning("Command line is unknown syntax.")
                raise ValueError('Unrecognized command "' + command_string + '"')

        # The syntax is not recognized so create a GenericCommandEditor or throw an exception.
        else:
            if create_unknown_command_if_not_recognized:
                logger.info("Command line is unknown syntax. Creating GenericCommandEditor for: " +
                            command_string_trimmed)
                # If the command is a basic comment return the appropriate
                # unique command editor
                if comment:
                    return CommentCommandEditor(command)
                # If the command is a comment block start return the
                # appropriate unique command editor
                elif commentBlockStart:
                    return CommentBlockStartCommandEditor(command)
                # If the command is a comment block end return the
                # appropriate unique command editor
                elif commentBlockEnd:
                    return CommentBlockEndCommandEditor(command)
                return GenericCommandEditor(command)
            else:
                logger.warning("Command line is unknown syntax.")
                raise ValueError('Unrecognized command "' + command_string + '"')
