# GeoProcessorCommandEditorFactory - class to create command editor for a command
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

import logging

from geoprocessor.app.GeoProcessorAppSession import GeoProcessorAppSession

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.ui.commands.abstract.AbstractCommandEditor import AbstractCommandEditor
from geoprocessor.ui.commands.abstract.SimpleCommandEditor import SimpleCommandEditor
from geoprocessor.ui.commands.abstract.GenericCommandEditor import GenericCommandEditor
from geoprocessor.ui.commands.util.InsertLineEditor import InsertLineEditor
from geoprocessor.ui.commands.util.InsertLineRulerEditor import InsertLineRulerEditor


class GeoProcessorCommandEditorFactory(object):
    """
    Factory to create command editor instance for a command object.
    """

    def __init__(self) -> None:
        """
        Initialize the command editor factory.
        """

        # TODO smalers 2019-01-18 the following data members are misplaced - need to move
        # Use the following for diagnostics and performance analysis - total count of commands processed
        self.command_created_count: int = 0

        # Use the following for error-handling - total number of unknown commands
        self.command_unknown_count: int = 0

    @classmethod
    def new_command_editor(cls, command: AbstractCommand, app_session: GeoProcessorAppSession) -> AbstractCommandEditor:
        """
        Creates the editor for a command object.
        A valid command object of some type will be provided, but may be UnknownCommand.
        This function can be called in the following cases:

        1. New command, such as from GeoProcessor UI menu, in which case no command parameters are provided.
        2. Existing command, such as from GeoProcessor UI right-click/Edit Command menu,
           in which case the command will have zero or more parameters defined.

        Some commands such as # comments require special handling, since multiple command lines are edited.
        This should be be handled before calling this function.

        Args:
            command (derived from AbstractCommand): command object
            app_session (GeoProcessorAppSession): application session instance

        Returns:
            A command editor suitable for the command.

        Raises:
            None, a suitable editor is always returned, with GenericCommandEditor as the default.
        """

        logger = logging.getLogger(__name__)

        # Initialize the command editor for the command object.
        # - only some commands have custom editors, depending on whether time has been spent building an editor

        # Check to see if command has editor type specified.
        # If so return the specified editor type, and otherwise return a generic command editor.
        try:
            editor_type = command.command_metadata['EditorType']
        except AttributeError:
            # May occur during code migration.
            # TODO smalers 2019-01-18 AbstractCommand.command_metadata needs to have class scope, not
            #                         be duplicated for every command instance.
            logger.warning('command_metadata not defined for command ' + str(command.command_name))
            logger.warning('Using Generic editor.  Code needs to be updated.')
            editor_type = 'Generic'
        except KeyError:
            # The editor type is not specified so default to 'Generic'
            editor_type = 'Generic'

        # Create the appropriate editor type
        if editor_type == "Generic":
            # Generic editor is simple parameter: value text fields
            return GenericCommandEditor(command)
        elif editor_type == "InsertLineEditor":
            # Single line commands like /* and */
            return InsertLineEditor(command)
        elif editor_type == "InsertLineRulerEditor":
            # Multi-line commands that use a ruler, such as one or more # commands
            return InsertLineRulerEditor(command)
        elif editor_type == "Simple":
            # Simple editor uses command class parameter_input_metadata dictionary to provide editor configuration
            return SimpleCommandEditor(command, app_session)
        elif editor_type == "Tabbed":
            # Tabbed editor is similar to Simple editor but parameters are grouped into tabs
            logger.warning('Tabbed editor is not implemented for command ' + str(command.command_name))
            logger.warning('Using generic command editor.')
            return GenericCommandEditor(command)
        else:
            # Editor type that is specified is not recognized, either a typo or code is out of date
            logger.warning('Editor type "' + editor_type + '" unrecognized for command ' + str(command.command_name))
            logger.warning('Using generic command editor.')
            return GenericCommandEditor(command)
