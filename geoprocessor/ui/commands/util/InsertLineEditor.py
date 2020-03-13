# CommentBlockEndEditor - editor for */ command editor
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

from PyQt5 import QtCore, QtGui, QtWidgets

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand
from geoprocessor.ui.commands.abstract.AbstractCommandEditor import AbstractCommandEditor

import geoprocessor.util.app_util as app_util
import geoprocessor.ui.util.qt_util as qt_util


class InsertLineEditor(AbstractCommandEditor):
    """
    Command editor for single line commands such as /*, */, and empty line.
    The editor dialog shows the description and help button and the command string, but no parameters.
    """

    # def __init__(self, command_name, command_description, parameter_count, command_parameters, current_values):
    def __init__(self, command: AbstractCommand) -> None:
        """
        Initialize the InsertLineEditor Dialog instance.

        Args:
            command: the command to edit
        """

        # Call the parent class
        super().__init__(command)

        # "input_edit_objects" is a dictionary that relates each command parameter with its associated Qt Widget
        # input field
        # KEY (str): the command parameter name
        # VALUE (obj): the associated Qt Widget input field
        # self.input_edit_objects = {}

        # "command_parameter_current_values" is a dictionary that holds the command parameters and their current values
        # KEY (str): the name of the command parameter
        # VALUE (str): the entered value of the command parameter
        # self.command_parameter_current_values = current_values

        # Defined in AbstractCommandEditor
        # Initialize components that will be used
        # self.CommandDisplay_View_TextBrowser = None

        # Defined in AbstractCommandEditor
        # Layout used for the main editor
        # - other layouts may be added as needed to organize components
        #self.grid_layout = None

        # Defined in AbstractCommandEditor
        # Position in the layout for components as they are added, 0=row at top, 1 is next down, etc.
        # - each addition should increment before adding a component
        # self.grid_layout_row = -1

        # Create variable to know if we are updating an existing command
        # or inserting a new command into the command list
        # NOT defined in AbstractCommandEditor - local to this class
        # self.update = False
        # If command parameters have already been defined for command,  know that are updating an existing command.
        # if command.command_parameters is not None:
        #    self.update = True

        # NOT defined in AbstractCommandEditor - local to this class
        # Indicate if an error status is currently in effect, due to invalid parameters
        # - will be set in check_input() and is checked in ui_action_ok_clicked()
        self.error_wait = False

        # Set up the UI for the command editor window
        self.setup_ui_core()

        # Defined here and NOT in AbstractCommandEditor
        # Initially call refresh to the UI in case updating a command
        # - will transfer command parameter values into the UI components
        self.refresh_ui()

    def check_input(self) -> None:
        """
        Check the parameter values shown in the editor to make sure all values are valid.
        There is nothing to check since no parameters.

        Returns:
            None.
        """
        pass

    def refresh_ui(self) -> None:
        """
        This function is called to ensure that the UI and command are consistent in the UI:

        1. The first time called:
            - Make sure the UI is up to date with initial command parameters
        2. Every time called:
            - Update the command string from values in the UI components.
            - Only non-empty values are set in the string.
            - Because the comment start is just /*, always shows this string

        Returns:
            None
        """
        command_string = self.command.to_string()
        self.CommandDisplay_View_TextBrowser.setPlainText(command_string)

    def setup_ui(self) -> None:
        """
        This function is called by AbstractCommandEditor.setup_ui_core(), which sets up the editor dialog.
        Currently it does nothing because one-line commands without parameters just display in the command area.

        Returns:
            None
        """
        pass

    def ui_action_cancel_clicked(self) -> None:
        """
        Handle clicking on cancel button.

        Returns:
            None
        """
        # To cancel, call the standard reject() function, which will set the return value.
        # - this allows the return value to be checked in the calling code
        self.reject()

    def ui_action_ok_clicked(self) -> None:
        """
        Handle clicking on OK button:

        1. The parameters in the input components are validated - in this case no parameters need to be checked.
        2. If OK, exit by calling accept().
        3. If not OK, the editor stays open until the user corrects or presses Cancel.

        Returns:
            None
        """
        # Check the input
        self.check_input()
        if self.error_wait:
            # User was shown a warning dialog and had to acknowledge it, so here just ignore the "OK"
            # - errors in input parameters need to be fixed before OK works
            pass
        else:
            # No error so OK to exit
            # - call the standard accept() function to set the return value
            self.accept()
