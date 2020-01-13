# GenericCommandEditor - default generic command editor
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

from geoprocessor.core import CommandParameterMetadata
from geoprocessor.ui.commands.abstract.AbstractCommandEditor import AbstractCommandEditor
from geoprocessor.ui.util.CommandParameter import CommandParameter

import geoprocessor.ui.util.qt_util as qt_util

import logging


class GenericCommandEditor(AbstractCommandEditor):
    """
    Command editor with general interface, which will provide text fields for each property.
    """

    def __init__(self, command):
        """
        Create the generic command editor dialog box, used to edit commands that don't have a specific editor.

        Args:
            command (command obj): this is a command object passed from GeoProcessorCommandEditorFactory
        """
        # Initialize the parent abstract editor
        # - this will do basic setup of the dialog
        super().__init__(command)

        # Keep track of command object
        self.command = command

        # Turn localized debug on/off, useful for development
        # - should be False for production release
        # - this causes logger.info messages to be printed
        # - later can convert to logger.debug if still needed
        self.debug = True

        # Indicate if an error status is currently in effect, due to invalid parameters
        # - will be set in check_input() and is checked in ui_action_ok_clicked()
        self.error_wait = False

        # Indicate whether first time refresh_ui is called
        # - the first time the UI components may be initialized from data
        self.first_refresh_ui = True

        # "input_ui_components" is a dictionary that relates each command parameter with its associated Qt Widget
        # input field
        # KEY (str): the command parameter name
        # VALUE (obj): the associated Qt Widget input component
        self.input_ui_components = {}

        # Array of text fields (Qt LineEdit) containing parameter values, with object name matching parameter name
        # self.parameter_LineEdit = [None]*len(self.command.command_parameter_metadata)
        self.parameter_LineEdit = dict()

        # Create variable to know if we are updating an existing command
        # or inserting a new command into the command list
        self.update = False
        # if command parameters have already been defined for command
        # we know that we are updating an existing command
        if command.command_parameters:
            self.update = True

        # The row position in the self.parameter_QGridLayout, used in setup_ui() and its helper functions.
        self.y_parameter = -1

        # Setup the UI in the abstract class, which will call back to set_ui() in this class.
        self.setup_ui_core()

        # Initially call refresh in case updating a command
        self.refresh_ui()

    def check_input(self):
        """
        Check the parameter values shown in the editor to make sure all values are valid.
        If any invalid parameters are detected, set self.error_wait = True so ui_action_ok_clicked() can
        keep the editor open to fix the issue(s).

        Returns:
            None.
        """
        logger = logging.getLogger(__name__)
        # Get the command string from the command display text box
        command_string = self.CommandDisplay_View_TextBrowser.toPlainText()
        logger.info('Checking command parameter input using command string:' + str(command_string))
        # Initialize the parameters of the command object.
        # - TODO smalers 2019-01-18 this will modify the contents of the command, needs to be a new instance from
        #        what is in an existing command or else could corrupt the original data if invalid or cancel is
        #        then pressed
        self.command.initialize_command(command_string, self, True)

        self.error_wait = False
        try:
            # Check command parameters
            self.command.check_command_parameters(self.command.command_parameters)
        except Exception as e:
            message = str(e)
            # Indicate that an error occurred
            self.error_wait = True
            logger.info(message)
            qt_util.warning_message_box(message)

    def refresh_ui(self):
        """
        This function is called to ensure that the UI and command are consistent in the UI:

        1. The first time called:
            - Make sure the UI is up to date with initial command parameters
        2. Every time called:
            - Update the command string from values in the UI components.
            - Only non-empty values are set in the string.

        Returns:
            None
        """

        logger = logging.getLogger(__name__)
        if self.first_refresh_ui:
            # The setup_ui() function will have constructed all necessary UI components.
            # However, they may not be populated with values so do that here:
            # - in particular set combobox selections
            # - TODO smalers 2019-01-19 figure out how strict to be on case-specific
            for command_parameter_metadata in self.command.command_parameter_metadata:
                # Parameters listed in logical order such as input / analysis / output
                parameter_name = command_parameter_metadata.parameter_name
                # The parameter value comes from the command
                # - if a new command most values will not be set
                # - if an existing command then need to make sure all previous data is handled
                parameter_value = self.command.get_parameter_value(parameter_name)
                try:
                    # Get the UI input component for the parameter
                    parameter_ui = self.input_ui_components[parameter_name]
                    # Based on the UI component type, retrieve the parameter value
                    # - check the object type with isinstance
                    # - use the class name for logging, should agree with object type
                    ui_type = parameter_ui.__class__.__name__
                    # But try the isinstance
                    if isinstance(parameter_ui, QtWidgets.QLineEdit):
                        parameter_ui.setText(parameter_value)
                    else:
                        # Should not happen
                        logger.warning("Unknown input component type '" + ui_type + "' for parameter '" +
                                       parameter_name + "' - code problem.")
                        continue
                except KeyError as e:
                    # Should not happen because all parameters should have at least a text field.
                    message = "No input component for parameter '" + parameter_name + "' - code problem."
                    logger.warning(message, exc_info=True)
                    continue
            # Set the following so won't do this initialization again
            self.first_refresh_ui = False

        # Always do the following to transfer UI component values to the full command string at the bottom of editor.
        # UI components should be fully initialized and contain values that match the command parameters
        # - loop through all UI components, extract the values from the components (by component type)
        #   and use to update the command string

        # Loop through the command parameter metadata and retrieve the values from editor components
        try:
            # Add all parameters to a temporary dictionary
            parameters_from_ui = dict()
            for command_parameter_metadata in self.command.command_parameter_metadata:
                # Parameters listed in logical order such as input / analysis / output
                parameter_name = command_parameter_metadata.parameter_name
                parameter_value = None
                try:
                    # Get the UI input component for the parameter
                    parameter_ui = self.input_ui_components[parameter_name]
                    # Based on the UI component type, retrieve the parameter value
                    # - check the object type with isinstance
                    # - use the class name for logging, should agree with object type
                    ui_type = parameter_ui.__class__.__name__
                    # But try the isinstance
                    if isinstance(parameter_ui, QtWidgets.QLineEdit):
                        parameter_value = parameter_ui.text()
                    else:
                        # Should not happen
                        logger.warning("Unknown input component type '" + ui_type + "' for parameter '" +
                                        parameter_name + "' - code problem.")
                        continue
                    # If here a parameter value was determined
                    # - TODO smalers 2019-01-19 need to be a bit careful with empty string values
                    #        such as checking the parameter's default value
                    if parameter_value is not None and parameter_value != "":
                        parameters_from_ui[parameter_name] = parameter_value
                except KeyError as e:
                    # Should not happen because all parameters should have at least a text field.
                    message = "No input component for parameter '" + parameter_name + "' - code problem."
                    logger.warning(message, exc_info=True)
                    continue
            # Have a dictionary of parameters extracted from UI components
            # - format the command string using the command instance
            # - this does not change the command string in the command instance
            command_string = self.command.to_string(parameters_from_ui)
            self.CommandDisplay_View_TextBrowser.setPlainText(command_string)
        except Exception as e:
            message = "Error refreshing command from parameters"
            logger = logging.getLogger(__name__)
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

        # try:
        #     y_parameter = -1
        #     # Initial part of command string
        #     command_string = self.command.command_name + "("
        #     # Add all parameters to the command string
        #     for command_parameter_metadata in self.command.command_parameter_metadata:
        #         # Parameters listed in logical order
        #         y_parameter = y_parameter + 1
        #         if y_parameter == 0:
        #             sep = ""
        #         else:
        #             sep = ","
        #         parameter_name = command_parameter_metadata.parameter_name
        #         parameter_value = self.parameter_LineEdit[parameter_name].text()
        #         if parameter_value is not None and parameter_value != "":
        #             command_string = command_string + sep + parameter_name + '="' + parameter_value + '"'
        #     command_string = command_string + ")"
        #     self.CommandDisplay_View_TextBrowser.setPlainText(command_string)
        # except Exception as e:
        #     message="Error refreshing command from parameters"
        #     logger = logging.getLogger(__name__)
        #     logger.warning(message, exc_info=True)
        #     qt_util.warning_message_box(message)

    def setup_ui(self):
        """
        Set up the dialog UI elements.  This generic editor provides text fields for each property.

        Returns:
            None
        """

        logger = logging.getLogger(__name__)

        # The AbstractCommandEditor sets up the editor by:
        # 1. Initializes the dialog.
        # 2. Setting up standard editor top.
        # 3. Calls this method to set up command editor specifics.
        #    Set up a simple list of command parameter text fields
        # 4. Setting up the standard editor bottom.

        # Set up an area for a list of parameters
        self.parameter_QFrame = QtWidgets.QFrame(self)
        self.parameter_QFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.parameter_QFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.parameter_QFrame.setObjectName("Command_Parameters")
        self.grid_layout_row = self.grid_layout_row + 1
        self.grid_layout.addWidget(self.parameter_QFrame, self.grid_layout_row, 0, 1, -1)

        # Create a grid layout object. Apply to the Command_Parameters frame object.
        # Set the name of the grid layout object.
        self.parameter_QGridLayout = QtWidgets.QGridLayout(self.parameter_QFrame)
        self.parameter_QGridLayout.setObjectName("Command_Parameters_Layout")

        # Add entry fields for each parameter
        self.y_parameter = -1
        for command_parameter_metadata in self.command.command_parameter_metadata:
            # Get the parameter name for retrieving all other parameter variables
            # - the command parameter_input_metadata dictionary contains UI configuration properties
            # - each dictionary key starts with `ParameterName.', for example 'LogFile.Label'
            parameter_name = command_parameter_metadata.parameter_name

            # Parameters listed in logical order, from left to right
            # ---------------
            # Leftmost UI component, which is the label
            # ---------------
            # Label component, consistent for all input component types
            # ---------------
            parameter_Label = parameter_name
            self.setup_ui_parameter_label(parameter_name, parameter_Label)

            # --------------------
            # Text entry component
            # --------------------
            # --------------------
            # LineEdit (text field)
            # - default if properties don't indicate any other component
            # --------------------
            parameter_Tooltip = None
            try:
                parameter_Tooltip = command_parameter_metadata.editor_tooltip
            except KeyError:
                # Default is an empty string
                # - components should check for None or empty string and not set tooltip in this case
                parameter_Tooltip = ""
            self.setup_ui_parameter_text_field(parameter_name, parameter_Tooltip)

            # # ----------------------------------------------------
            # # Description component, optionally with default value
            # # ----------------------------------------------------
            parameter_Description = None
            try:
                parameter_description = command_parameter_metadata.parameter_description
            except KeyError:
                parameter_Description = ""
            self.setup_ui_parameter_description(parameter_name, parameter_description)

    def setup_ui_parameter_description(self, parameter_name, parameter_desc):
        """
        Override function in AbstractCommand class to add a description if it is specified
        in the command_parameter_metadata. This description will not be as specific as is
        in TabbedCommandEditor or SimpleCommandEditor, therefore there is a need for an overriden
        function.

        Args:
            parameter_name (str) : the name of the parameter
            parameter_desc (str) : description coming from the command_parameter_metadata

        Returns:

        """
        debug = True
        if self.debug:
            logger = logging.getLogger(__name__)
            logger.info("For parameter '" + parameter_name + "', adding description")
        parameter_desc_Label = QtWidgets.QLabel(self.parameter_QFrame)
        parameter_desc_Label.setObjectName("Command_Parameter_Description_Label")
        parameter_desc_Label.setText(parameter_desc)
        # parameter_desc_Label.setAlignment(QtCore.Qt.AlignLeft) # |QtCore.Qt.AlignCenter)
        self.parameter_QGridLayout.addWidget(parameter_desc_Label, self.y_parameter, 6, 1, 1)

    def ui_action_cancel_clicked(self):
        """
        Handle clicking on cancel button:

        1. What happens?

        Returns:
            None
        """
        # To cancel, call the standard reject() function, which will set the return value.
        # - this allows the return value to be checked in the calling code
        self.reject()

    def ui_action_ok_clicked(self):
        """
        Handle clicking on OK button:

        1. The parameters in the input components are validated.
        2. If OK, exit by calling accept()
        3. If not OK, the editor stays open until the user corrects or presses Cancel.

        Returns:
            None
        """
        # Check the input
        self.check_input()
        if self.error_wait:
            # User was shown a dialog and had to acknowledge it, so here just ignore the "OK"
            pass
        else:
            # No error so OK to exit
            # - call the standard accept() function to set the return value
            self.accept()

