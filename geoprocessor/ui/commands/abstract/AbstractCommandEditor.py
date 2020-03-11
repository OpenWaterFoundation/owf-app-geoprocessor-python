# AbstractCommandEditor - parent class for all command editors
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
import geoprocessor.util.app_util as app_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.os_util as os_util
import geoprocessor.ui.util.qt_util as qt_util

import logging
import os
import webbrowser


class AbstractCommandEditor(QtWidgets.QDialog):
    """
    Abstract command editor used as parent of command editor dialog implementations.
    This class maintains core layout information and provides functions to add components.
    Derived classes should use the data and methods in this class as much as possible.
    """

    def __init__(self, command: AbstractCommand) -> None:
        """
        Initialize the Abstract Dialog instance.

        Args:
            command (derived from AbstractCommand): the GeoProcessor command to edit
        """
        # Call the parent class
        super().__init__()

        # Command being edited
        self.command: AbstractCommand = command

        # GeoProcessorUI
        self.geoprocessor_ui = None

        # "input_edit_objects" is a dictionary that relates each command parameter with its associated Qt Widget
        # input field
        # KEY (str): the command parameter name
        # VALUE (obj): the associated Qt Widget input field
        # self.input_edit_objects = {}

        # "command_parameter_current_values" is a dictionary that holds the command parameters and their current values
        # KEY (str): the name of the command parameter
        # VALUE (str): the entered value of the command parameter
        # self.command_parameter_current_values = current_values

        # "input_ui_components" is a dictionary that relates each command parameter with its associated Qt Widget
        # input field
        # KEY (str): the command parameter name
        # VALUE (obj): the associated Qt Widget input component
        self.input_ui_components = {}

        # Initialize components that will be used
        # Command text area
        self.CommandDisplay_View_TextBrowser: QtWidgets.QTextEdit or None = None

        # The first input component
        # - will be activated after initial setup, in setup_ui_2()
        self.first_input_component = None

        # Layout used for the main editor
        # - other layouts may be added as needed to organize components
        # TODO smalers 2020-01-16 could name to indicate top
        self.grid_layout: QtWidgets.QGridLayout or None = None
        # TODO smalers 2020-01-16 could name to indicate parameter area
        self.gridLayout2: QtWidgets.QGridLayout or None = None

        # Position in the layout for components as they are added, 0=row at top, 1 is next down, etc.
        # - each addition should increment before adding a component
        self.grid_layout_row = -1

        # Set initial size of window
        self.resize(500, 300)
        # Set the maximum width of a command editor
        self.setMaximumWidth(800)

        # Top of dialog
        self.CommandDisplay_Label: QtWidgets.QLabel or None = None
        self.Command_Description_Label: QtWidgets.QLabel or None = None
        self.View_Documentation_Button: QtWidgets.QPushButton or None = None
        self.View_Documentation_Button: QtWidgets.QPushButton or None = None

        # Separator between description and parameters
        self.Separator: QtWidgets.QFrame or None = None

        # Parameter area
        # The QtWidgets.QGridLayout manages the layout of self.parameter_QFrame
        # - instantiated in setup_ui()
        self.parameter_QGridLayout: QtWidgets.QGridLayout or None = None

        self.y_parameter: int or None = None
        # The QtWidgets.QFrame that is the UI element used to hold the parameter UI components
        # - instantiated in setup_ui()
        self.parameter_QFrame: QtWidgets.QFrame or None = None

        # Buttons at the bottom of the dialog
        self.dialog_ButtonBox: QtWidgets.QDialogButtonBox or None = None
        self.ok_button: QtWidgets.QPushButton or None = None
        self.cancel_button: QtWidgets.QPushButton or None = None

        # Derived editor classes __init__() functions will then call methods that build the UI

    # def add_text_field(self, label, parameter_name, tooltip=None):
    #     """
    #     Add a text input field as  a QtGui.QLineEdit object that meets the standards of the
    #     GeoProceossor's command dialog window.
    #
    #     Args:
    #         label (str): label to display for text field.
    #         parameter_name (str): the name of the command parameter that is using the line edit field
    #         tooltip (str): optional. The text that will display in a pop-up when the user mouses over the
    #             QtGui.QLineEdit object. This is a good place to expand description of the parameter/parameter values.
    #
    #     Return: None
    #     """
    #
    #     # Set the line edit's object name (XXX_LineEdit where XXX is the name of the command parameter).
    #     line_edit.setObjectName(_fromUtf8("{}_LineEdit".format(parameter_name)))
    #
    #     # Get the dialog box row index that is used to display the command parameter objects
    #     # This is a dynamic index that takes into consideration the order of the command's parameters.
    #     row_index = self.parameters_list.index(parameter_name) + 2
    #
    #     # Add the line edit field to the Dialog box in the correct row. Command line edit fields will always start in
    #     # the second column (1) and will occupy 1 row.
    #     # If the field is set to long, the line edit field will occupy 6 columns.
    #     if long:
    #         self.gridLayout.addWidget(line_edit, row_index, 1, 1, 6)
    #
    #     # If not set to long, the line edit field will occupy 3 columns.
    #     else:
    #         self.gridLayout.addWidget(line_edit, row_index, 1, 1, 3)
    #
    #     # If placeholder text has been specified, add the desired text as placeholder text.
    #     if placeholder_text:
    #         line_edit.setPlaceholderText(_translate("Dialog", placeholder_text, None))
    #
    #     # If tool tip text has been specified, add the desired text as tool tip text.
    #     if tooltip:
    #         line_edit.setToolTip(_translate("Dialog", tooltip, None))
    #
    #     # Create a listener that reacts if the line edit field has been changed. If so, run the
    #     # update_command_display function.
    #     line_edit.textChanged.connect(self.update_command_display)
    #
    #     # Add the QtGui.QLineEdit object to the dictionary of input edit objects. Use the parameter name as the key
    #     # and the QtGui.QLineEdit object as the value.
    #     self.input_edit_objects[parameter_name] = line_edit

    def add_ui_horizontal_separator(self) -> None:
        # Create a line (frame object with special specifications). Add the line to the Dialog window.
        # Set the size policy, the shape, the shadow, and the name of the frame object to create the line separator.
        # The frame object, Separator, separates the command description from the input form section of the Dialog box.
        self.Separator = QtWidgets.QFrame(self)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.Separator.sizePolicy().hasHeightForWidth())
        self.Separator.setSizePolicy(size_policy)
        self.Separator.setFrameShape(QtWidgets.QFrame.HLine)
        self.Separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.Separator.setObjectName(qt_util.from_utf8("Separator"))
        self.grid_layout_row = self.grid_layout_row + 1
        self.grid_layout.addWidget(self.Separator, self.grid_layout_row, 0, 1, 8)

    # TODO smalers 2020-01-14 This method does not seem to be used - need to remove?
    def are_required_parameters_specified(self, ui_command_parameter_list: []) -> bool:
        """
        Checks if the required parameters of a command are specified by the user in the command dialog window.

        ui_command_parameter_list (list of objects):  a list of the CommandParameter objects (UI-specific class)

        Returns:
            Boolean. If TRUE, all required parameters have been met. If FALSE, one or more of the required parameters
            are not specified.
        """

        # Specified is set to True until proven False.
        specified = True

        # Iterate over the UI CommandParameter objects.
        for ui_parameter in ui_command_parameter_list:

            # If the command parameter is set as "REQUIRED", continue.
            if ui_parameter.optional is False:

                # If the value of the required command parameter has not been specified by the user, set specified
                # to False.
                if self.command_parameter_values[ui_parameter.name] is "":
                    specified = False

        # Return the specified Boolean.
        return specified

    def check_command_file_saved(self) -> None:
        """
        Before user is able to select a file path from command editor. Make sure that the command file has
        been saved, or at the very least notify the user that if they choose not to save
        the relative paths will be relative to default working directory, not where the command file
        is saved.

        Returns:

        """
        geoprocessor_ui = self.command.geoprocessor_ui

        if not geoprocessor_ui.command_file_saved:
            print("working with initial dir. need to save")
            button_selected = qt_util.new_message_box(
                QtWidgets.QMessageBox.Question,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                "This command file has not been saved. Would you like to save to "
                "ensure relative paths are relative to command file location?",
                "Save Commands File?")
            # button_selected = qt_util.question_box("This command file has not been saved. Would you like to save to "
            # "ensure relative paths are relative to command file location?")
            if button_selected == QtWidgets.QMessageBox.Yes:
                # User selected ok. Open a window to save the command file
                # Get geoprocessor ui
                geoprocessor_ui = self.command.geoprocessor_ui
                geoprocessor_ui.ui_action_save_commands_as()
                if geoprocessor_ui.saved_file == "":
                    qt_util.new_message_box(
                        QtWidgets.QMessageBox.Warning,
                        QtWidgets.QMessageBox.Ok,
                        "New command file has not been saved. \nThis may cause problems with relative paths.",
                        "File Not Saved")
                else:
                    qt_util.new_message_box(
                        QtWidgets.QMessageBox.Information,
                        QtWidgets.QMessageBox.Ok,
                        "New command file has been saved.",
                        "File Saved")
            else:
                qt_util.new_message_box(
                    QtWidgets.QMessageBox.Warning,
                    QtWidgets.QMessageBox.Ok,
                    "New command file has not been saved. \nThis may cause problems with relative paths.",
                    "File Not Saved")
                pass

    def check_command_parameters(self) -> None:
        """
        Check to confirm that the command parameters are valid.

        Returns:
        """
        param_dict = self.get_parameter_dict_from_ui()
        self.command.check_command_parameters(param_dict)

    def get_current_value(self, obj: QtWidgets.QWidget) -> str:
        """
        Get the value within a QtGui.Widget object.

        Arg:
            obj (obj): the a QtGui.Widget object, as a string.

        Return: the value within the QtGui.Widget object
        """

        # Different QtGui widgets have different ways of reading their input data. Try both versions and assign the
        # value when one works.
        # Reads LineEdit widgets.
        # noinspection PyBroadException
        try:
            value = obj.text()

        # Reads ComboBox widgets.
        except Exception:
            value = obj.currentText()

        # Return the value within the input QtGui.Widget object.
        return value

    @staticmethod
    def select_file(qt_widget: QtWidgets.QWidget) -> None:
        """
        Opens a file browser to allow a user to select a file through a Qt predefined user interface. The path of the
        selected file is added to the qt_widget Qt Widget input field.

        Args:
            qt_widget (obj): the Qt Widget that will display the full path of the selected file

        Return: None
        """

        # Open the browser for file selection. Save the full path of the selected file as a string.
        file_name_text = QtWidgets.QFileDialog.getOpenFileName()[0]

        # Add the full path of the selected file string to the specified input Qt Widget.
        qt_widget.setText(file_name_text)

    def setup_ui(self) -> None:
        """
        Set up the user interface.
        It should be implemented in a child class, although helper functions are defined in this abstract class.

        Returns: None
        """
        # This should not normally happen but will be the case if a child editor has not implemented the function
        raise Exception("In AbstractCommandEditor.setup_ui - need to define setup_ui() in derived editor class.")

    def setup_ui_2(self) -> None:
        """
        Set up the user interface after components have been added.
        It should be implemented in a child class, although helper functions are defined in this abstract class.
        Typically this sets as active the top component in the dialog.

        Returns: None
        """
        # This should not normally happen but will be the case if a child editor has not implemented the function
        if self.first_input_component is not None:
            # Set the focus onto the first component
            self.first_input_component.setFocus()

    def setup_ui_core(self) -> None:
        # Set up the editor core elements, which apply to any command.
        self.setup_ui_core_top()
        # Set up the editor specific to the command.
        # - this code should be implemented in child class
        self.setup_ui()
        # Set up the core components at the bottom
        self.setup_ui_core_bottom()
        # Set up the editor after components have been added
        # - currently, focus on the first entry point for the mouse
        self.setup_ui_2()

        # This will wire up the signals and slots depending on names.
        # REF: http://joat-programmer.blogspot.com/2012/02/pyqt-signal-and-slots-to-capture-events.html
        # - don't do this because not using QtDesigner
        # QtCore.QMetaObject.connectSlotsByName(self)

    def setup_ui_core_bottom(self) -> None:
        """
        Setup core UI components at the bottom of the dialog.

        Returns:  None
        """
        self.setup_ui_core_command_area()
        self.setup_ui_core_command_buttons()

    def setup_ui_core_command_area(self) -> None:
        # Create a label object to the Dialog window.
        # Set the alignment, the name, and the text of the label.
        # The label, Command Display_Label, labels the CommandDisplay_View_TextBrowser text edit object.
        # noinspection PyPep8Naming
        commandArea_Frame = QtWidgets.QFrame(self)
        commandArea_Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        commandArea_Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        commandArea_Frame.setObjectName("Command_Parameters")
        self.grid_layout_row = self.grid_layout_row + 1
        # TODO smalers 2019-01-20 Need to understand why things work differently on each OS
        if os_util.is_linux_os() and not os_util.is_cygwin_os():
            # Full Linux
            self.grid_layout.addWidget(commandArea_Frame, self.grid_layout_row, 0, 1, 1)
        else:
            # Cygwin and Windows
            self.grid_layout.addWidget(commandArea_Frame, self.grid_layout_row, 0, 1, -1)

        # Create a grid layout object. Apply to the Command_Parameters frame object.
        # Set the name of the grid layout object.
        # noinspection PyPep8Naming
        commandArea_GridLayout = QtWidgets.QGridLayout(commandArea_Frame)
        commandArea_GridLayout.setObjectName("Command_Parameters_Layout")

        self.grid_layout_row = self.grid_layout_row + 1
        self.CommandDisplay_Label = QtWidgets.QLabel(self)
        self.CommandDisplay_Label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.CommandDisplay_Label.setObjectName(qt_util.from_utf8("CommandDisplay_Label"))
        self.CommandDisplay_Label.setText(qt_util.translate("Dialog", "Command: ", None))
        commandArea_GridLayout.addWidget(self.CommandDisplay_Label, self.grid_layout_row, 0, 1, 1)
        # Create a text edit object. Add the text edit object to the Dialog window.
        # Set the size, the name and the html of the text edit object.
        # The text edit object, CommandDisplay_View_TextBrowser, displays a dynamic view of the command string.
        self.CommandDisplay_View_TextBrowser = QtWidgets.QTextEdit(self)
        self.CommandDisplay_View_TextBrowser.setObjectName("CommandDisplay_View_TextBrowser")
        self.CommandDisplay_View_TextBrowser.setReadOnly(True)
        self.CommandDisplay_View_TextBrowser.setMaximumHeight(60)
        # self.CommandDisplay_View_TextBrowser.setMinimumSize(QtCore.QSize(0, 100))
        # self.CommandDisplay_View_TextBrowser.setMaximumSize(QtCore.QSize(16777215, 100))
        # #html = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">" \
        # #       "\n<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\np, li { " \
        # #       "white-space: pre-wrap; }\n</style></head><body style=\" font-family:\'MS Shell Dlg 2\';" \
        # #       " font-size:8.25pt; font-weight:400; font-style:normal;\">\n<p style=\" margin-top:0px;" \
        # #       " margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">" \
        # #       "<span style=\" font-size:8pt;\">ReadGeoLayerFromGeoJSON()</span></p></body></html>"
        # #self.CommandDisplay_View_TextBrowser.setHtml(_translate("Dialog", html, None))
        # TODO smalers 2019-01-20 Need to understand why things work differently on each OS
        if os_util.is_linux_os() and not os_util.is_cygwin_os():
            # Full Linux
            commandArea_GridLayout.addWidget(self.CommandDisplay_View_TextBrowser, self.grid_layout_row, 1, 1, 1)
        else:
            # Cygwin and Windows
            commandArea_GridLayout.addWidget(self.CommandDisplay_View_TextBrowser, self.grid_layout_row, 1, 1, -1)

    def setup_ui_core_command_buttons(self) -> None:

        # noinspection PyPep8Naming
        buttons_Frame = QtWidgets.QFrame(self)
        buttons_Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        buttons_Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        buttons_Frame.setObjectName("Command_Parameters")
        self.grid_layout_row = self.grid_layout_row + 1
        self.grid_layout.addWidget(buttons_Frame, self.grid_layout_row, 0, 1, -1)

        # Create a grid layout object. Apply to the Command_Parameters frame object.
        # Set the name of the grid layout object.
        # noinspection PyPep8Naming
        buttons_GridLayout = QtWidgets.QGridLayout(buttons_Frame)
        buttons_GridLayout.setObjectName("Command_Parameters_Layout")

        # Create a button box object. Add the button box object to the Dialog window.
        # Set the orientation, the standard buttons, the name and the connections of the button box object.
        # The button box object, OK_Cancel_Buttons, allow the user to accept or reject the changes made in the dialog.
        self.dialog_ButtonBox = QtWidgets.QDialogButtonBox(self)
        self.dialog_ButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.dialog_ButtonBox.setObjectName(qt_util.from_utf8("dialog_ButtonBox"))
        self.grid_layout_row = self.grid_layout_row + 1
        # Add buttons to enable event handling
        # - use custom buttons rather than defaults because events need to be handled
        # OK button
        # ---------
        self.ok_button = QtWidgets.QPushButton("OK")
        # Object name has parameter at front, which can be parsed out in event-handling code
        self.ok_button.setObjectName(qt_util.from_utf8("OK"))
        self.ok_button.setToolTip("Save edits to command.")
        # self.ok_button.clicked.connect(
        # lambda clicked, f.y_parameter: self.ui_action_open_file(self.load_file_button))
        # Use action role because action is handled in the dialog
        self.dialog_ButtonBox.addButton(self.ok_button, QtWidgets.QDialogButtonBox.ActionRole)
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.ok_button.clicked.connect(self.ui_action_ok_clicked)
        # Cancel button
        # ---------
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        # Object name has parameter at front, which can be parsed out in event-handling code
        self.cancel_button.setObjectName(qt_util.from_utf8("Cancel"))
        self.cancel_button.setToolTip("Cancel without saving edits to command.")
        # self.cancel_button.clicked.connect(
        # lambda clicked, f.y_parameter: self.ui_action_open_file(self.load_file_button))
        # Use action role because action is handled in the dialog
        self.dialog_ButtonBox.addButton(self.cancel_button, QtWidgets.QDialogButtonBox.ActionRole)
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.cancel_button.clicked.connect(self.ui_action_cancel_clicked)
        # Button box is added regardless of how buttons are defined
        buttons_GridLayout.addWidget(self.dialog_ButtonBox, self.grid_layout_row, 6, 1, 2)

    def setup_ui_core_command_description(self) -> None:
        """
        Setup the description component at the top of the dialog.
        """
        # Create a frame object. Add the frame object to the Dialog window.
        # Set the shape, the shadow, and the name of the frame object.
        # The frame object, Command_Description, holds the command description and the view documentation button.
        # noinspection PyPep8Naming
        description_Frame = QtWidgets.QFrame(self)
        description_Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        description_Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        description_Frame.setObjectName(qt_util.from_utf8("Command_Description"))
        self.grid_layout_row = self.grid_layout_row + 1
        self.grid_layout.addWidget(description_Frame, self.grid_layout_row, 0, 1, 8)

        # Create a grid layout object. Apply to the Command_Description frame object.
        # Set the name of the grid layout object.
        self.gridLayout2 = QtWidgets.QGridLayout(description_Frame)
        self.gridLayout2.setObjectName(qt_util.from_utf8("gridLayout2"))

        # Create a spacer. Add the spacer to the Command_Description frame object.
        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout2.addItem(spacer_item, 2, 0, 1, 1)

        # Create a push button. Add the button to the Command_Description frame object.
        # Set the name, the button text and the connection of the push button.
        # The push button, View_Documentation_Button, displays the command's online user documentation when clicked.
        self.View_Documentation_Button = QtWidgets.QPushButton(description_Frame)
        self.View_Documentation_Button.setObjectName(qt_util.from_utf8("View_Documentation_Button"))
        self.View_Documentation_Button.setText(qt_util.translate("Dialog", "  View Documentation  ", None))
        self.View_Documentation_Button.setToolTip("View command documentation in web browser.")
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.View_Documentation_Button.clicked.connect(self.view_documentation)
        self.gridLayout2.addWidget(self.View_Documentation_Button, 2, 1, 1, 1)

        # Create a label. Add the label to the Command_Description frame object.
        # Set the name and the text of the label.
        # The label, Command_Description_Label, briefly describes the command.
        self.Command_Description_Label = QtWidgets.QLabel(description_Frame)
        self.Command_Description_Label.setObjectName(qt_util.from_utf8("Command_Description_Label"))
        self.Command_Description_Label.setText(self.command.command_metadata['Description'])
        self.gridLayout2.addWidget(self.Command_Description_Label, 0, 0, 1, 2)

    def setup_ui_core_top(self) -> None:
        """
        Setup core UI components at the top of the dialog.

        Returns:  None
        """
        # Set the window title to the command name
        self.setObjectName(qt_util.from_utf8(self.command.command_name))
        self.setWindowTitle("Edit " + self.command.command_name + " command")
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        icon_path = app_util.get_property("ProgramIconPath").replace('\\', '/')
        self.setWindowIcon(QtGui.QIcon(icon_path))

        # Because components are added to the UI the dialog will have a size.
        # - don't set the size unless a dialog misbehaves, perhaps a maximum size
        # self.resize(684, 404)

        # Add a grid layout for components to be added
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setObjectName(qt_util.from_utf8("gridLayout"))

        self.setup_ui_core_command_description()
        self.add_ui_horizontal_separator()

    # noinspection PyPep8Naming
    def setup_ui_parameter_combobox(self, parameter_name: str,
                                    parameter_ValueDefaultForDisplay: str,
                                    parameter_Tooltip: str,
                                    parameter_Values: str,
                                    parameter_ValuesEditable: bool) -> None:
        """
        Add combobox UI components for a command parameter.

        Args:
            parameter_name (str):  Parameter name, used for troubleshooting
            parameter_ValueDefaultForDisplay (str):  Display value corresponding to Value.Default, added to
            parameter_Tooltip (str):  Tooltip text.
            parameter_Values (str):  List of values for list, comma-delimited
            parameter_ValuesEditable (bool):  Whether the list of values is editable in the text field.

        Returns:
            None
        """
        # try:
        #     parameter_Values, parameter_Tooltip, parameter_FileSelectorType
        # except Exception as e:
        #     message = "Could not find necessary parameter metadata in command file for " + parameter_name + \
        #               ". Could not build simple command editor. Defaulting to generic command editor. " \
        #               "See log file for more details."
        #     logger.warning(message, exc_info=True)
        #     qt_util.warning_message_box(message)
        # ComboBox, indicated by 'Values' property
        debug = True
        if self.debug:
            logger = logging.getLogger(__name__)
            logger.info("For parameter '" + parameter_name + "', adding combobox")
        # noinspection PyPep8Naming
        parameter_QComboBox = QtWidgets.QComboBox(self.parameter_QFrame)
        parameter_QComboBox.setObjectName(qt_util.from_utf8("Drop_Down_Menu"))
        parameter_QComboBox.setEditable(True)
        # Handle blank value at start of the list
        # - a blank item is not automatically added but will be added if Value.DefaultForDisplay is ""
        # - the Values list can also have a blank at the start
        # - considering the above, only add one blank at the beginning
        # Add a blank item so that there is not an initial response for the drop down
        if parameter_ValueDefaultForDisplay is not None:
            parameter_QComboBox.addItem(parameter_ValueDefaultForDisplay)
        # Add values in the 'Values' list, but don't re-add Value.DefaultForDisplay
        for i, value in enumerate(parameter_Values):
            parameter_QComboBox.addItem(value)
        # Add an event to refresh the command if anything changes
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        parameter_QComboBox.currentIndexChanged.connect(self.refresh_ui)
        if parameter_Tooltip is not None and parameter_Tooltip != "":
            parameter_QComboBox.setToolTip(parameter_Tooltip)
        # Set whether editable
        parameter_QComboBox.setEditable(parameter_ValuesEditable)
        self.parameter_QGridLayout.addWidget(parameter_QComboBox, self.y_parameter, 1, 1, 2)
        # Add the component to the list maintained to get values out of UI components
        self.input_ui_components[parameter_name] = parameter_QComboBox

        # Set the component as the first in dialog, so that focus can be set to it
        if self.first_input_component is None:
            self.first_input_component = parameter_QComboBox

    # noinspection PyPep8Naming
    def setup_ui_parameter_description(self, parameter_name: str,
                                       parameter_Description: str,
                                       parameter_Required: bool,
                                       parameter_Tooltip: str,
                                       parameter_ValueDefault: str,
                                       parameter_ValueDefaultDescription: str):
        """
        Add description UI components for a command parameter.
        This is not done for file selector component.

        Args:
            parameter_name (str):  Parameter name, used for troubleshooting
            parameter_Description (str):  Parameter description, before combining with other data here.
            parameter_Required (boolean):  Whether the parameter is required.
            parameter_Tooltip (str):  Tooltip text.
            parameter_ValueDefault (str):  Parameter default value if not specified.
            parameter_ValueDefaultDescription (str):  Description for default value.

        Returns:
            None
        """
        # try:
        #     parameter_Required, parameter_Description, parameter_ValueDefault
        # except Exception as e:
        #     message = "Could not find necessary parameter metadata in command file for " + parameter_name + \
        #               ". Could not build simple command editor. Defaulting to generic command editor. " \
        #               "See log file for more details."
        #     logger.warning(message, exc_info=True)
        #     qt_util.warning_message_box(message)
        debug = True
        if self.debug:
            logger = logging.getLogger(__name__)
            logger.info("For parameter '" + parameter_name + "', adding description")
        # noinspection PyPep8Naming
        parameter_desc_Label = QtWidgets.QLabel(self.parameter_QFrame)
        parameter_desc_Label.setObjectName("Command_Parameter_Description_Label")
        parameter_desc = ""
        if parameter_Required:
            parameter_desc += "Required"
        else:
            parameter_desc += "Optional"
        if parameter_Description != "":
            if parameter_desc != "":
                parameter_desc += " - "
            parameter_desc += parameter_Description
        if not parameter_Required:
            # Only show the default value if an optional argument
            # - if required, check_command_parameters should will not allow blank input
            if parameter_ValueDefaultDescription is not None and parameter_ValueDefaultDescription != "":
                # A description is provided for the default value so use in the description rather than Value.Default
                if len(parameter_ValueDefaultDescription) > 15:
                    # Default value description is long so don't show in full description and put in the
                    # input component tooltip
                    parameter_desc += " (default=see tooltip)."
                    parameter_Tooltip += "\n(default=" + parameter_ValueDefaultDescription + ")."
                    # Update the tooltip for the input component
                    try:
                        parameter_ui_component = self.input_ui_components[parameter_name]
                        parameter_ui_component.setToolTip(parameter_Tooltip)
                    except KeyError:
                        # Should not happen
                        pass
                else:
                    # Default value is short so show in the full description
                    parameter_desc += " (default=" + parameter_ValueDefaultDescription + ")."
            elif parameter_ValueDefault is not None and parameter_ValueDefault != "":
                # A default value is provided so include in the description
                if len(parameter_ValueDefault) > 15:
                    # Default value is long so don't show in full description and put in the input component tooltip
                    parameter_desc += " (default=see tooltip)."
                    parameter_Tooltip += "\n(default=" + parameter_ValueDefault + ")."
                    # Update the tooltip for the input component
                    try:
                        parameter_ui_component = self.input_ui_components[parameter_name]
                        parameter_ui_component.setToolTip(parameter_Tooltip)
                    except KeyError:
                        # Should not happen
                        pass
                else:
                    # Default value is short so show in the full description
                    parameter_desc += " (default=" + parameter_ValueDefault + ")."
            else:
                # There is no default value specified so default of None is likely
                # - OK to show None to mean use None literally or it means the parameter won't be used
                # - however, it is probably better to find an actual default value if possible and update the code
                parameter_desc += " (default=None)."
        else:
            # Need a period at the end
            parameter_desc += "."
        # Set the text description as the label
        parameter_desc_Label.setText(parameter_desc)
        # parameter_desc_Label.setAlignment(QtCore.Qt.AlignLeft) # |QtCore.Qt.AlignCenter)
        self.parameter_QGridLayout.addWidget(parameter_desc_Label, self.y_parameter, 6, 1, 1)

    # noinspection PyPep8Naming
    def setup_ui_parameter_file_selector(self, input_metadata: dict, parameter_name: str,
                                         parameter_Tooltip: str) -> None:
        """
        Add file selector UI components for a command parameter.

        Args:
            input_metadata (dict):  input metadata, to retrieve additional properties
            parameter_name (str):  Parameter name.
            parameter_Tooltip (str):  Tooltip to be used for the main text field.

        Returns:
            None
        """
        debug = True
        if self.debug:
            logger = logging.getLogger(__name__)
            logger.info("For parameter '" + parameter_name + "', adding file selector")
        # Create the text field that will receive the file path
        # noinspection PyPep8Naming
        parameter_QLineEdit = QtWidgets.QLineEdit(self.parameter_QFrame)
        parameter_QLineEdit.setObjectName(parameter_name)
        self.parameter_QGridLayout.addWidget(parameter_QLineEdit, self.y_parameter, 1, 1, 4)
        self.parameter_QGridLayout.setColumnStretch(1, 4)
        if parameter_Tooltip != "":
            parameter_QLineEdit.setToolTip(parameter_Tooltip)
        # Create a listener that reacts if the line edit field has been changed. If so, run the
        # refresh_ui function.
        # If this command is being updated add the command parameters to the text fields
        if self.update:
            parameter_value = self.command.get_parameter_value(parameter_name)
            parameter_QLineEdit.setText(parameter_value)
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        parameter_QLineEdit.textChanged.connect(self.refresh_ui)
        # Save the UI component
        self.input_ui_components[parameter_name] = parameter_QLineEdit
        # -----------------
        # Add a "..." button
        # -----------------
        request_key = parameter_name + "." + "FileSelector.SelectFolder"
        select_folder = False
        try:
            # The following should match ParameterName.FileSelector.SelectFolder
            select_folder = self.command.parameter_input_metadata[request_key]
        except KeyError:
            # Default was specified above...
            pass
        request_key = parameter_name + "." + "FileSelector.Button.Tooltip"
        file_selector_button_tooltip = ""
        try:
            file_selector_button_tooltip = input_metadata[request_key]
        except KeyError:
            # Default...
            if select_folder:
                file_selector_button_tooltip = "Browse for folder"
            else:
                file_selector_button_tooltip = "Browse for file"
        # noinspection PyPep8Naming
        parameter_select_file_QPushButton = QtWidgets.QPushButton(self.parameter_QFrame)
        # Object name has parameter at front, which can be parsed out in event-handling code
        # - IMPORTANT - don't change the object name without changing elsewhere
        parameter_select_file_QPushButton.setObjectName(qt_util.from_utf8(parameter_name + ".FileSelector.Button"))
        parameter_select_file_QPushButton.setText(qt_util.translate("Dialog", "...", None))
        if file_selector_button_tooltip != "":
            parameter_select_file_QPushButton.setToolTip(file_selector_button_tooltip)
        parameter_select_file_QPushButton.setMaximumWidth(50)
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        parameter_select_file_QPushButton.clicked.connect(
            lambda clicked, y_param=self.y_parameter: self.ui_action_select_file(parameter_select_file_QPushButton))
        self.parameter_QGridLayout.addWidget(parameter_select_file_QPushButton, self.y_parameter, 6, 1, 1)
        # Set the component as the first in dialog, so that focus can be set to it
        if self.first_input_component is None:
            self.first_input_component = parameter_QLineEdit

    # noinspection PyPep8Naming
    def setup_ui_parameter_label(self, parameter_name: str, parameter_Label: str) -> None:
        """
        Add label UI components for a command parameter.

        Args:
            parameter_name (str):  Parameter name.
            parameter_Label (str):  Parameter label, for start of input line.

        Returns:
            None
        """
        # try:
        #     parameter_Label
        # except Exception as e:
        #     message = "Could not find necessary parameter metadata in command file for " + parameter_name + \
        #               ". Could not build simple command editor. Defaulting to generic command editor. " \
        #               "See log file for more details."
        #     logger.warning(message, exc_info=True)
        #     qt_util.warning_message_box(message)
        debug = True
        if self.debug:
            logger = logging.getLogger(__name__)
            logger.info("For parameter '" + parameter_name + "', adding label")
        # Increment the y-position in the GridLayout since starting a new row in the UI
        self.y_parameter = self.y_parameter + 1
        # noinspection PyPep8Naming
        parameter_QLabel = QtWidgets.QLabel(self.parameter_QFrame)
        parameter_QLabel.setObjectName("Command_Parameter_Label")
        parameter_QLabel.setText(parameter_Label + ":")
        parameter_QLabel.setAlignment(QtCore.Qt.AlignRight)  # |QtCore.Qt.AlignCenter)
        # Allow expanding horizontally
        parameter_QLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.parameter_QGridLayout.addWidget(parameter_QLabel, self.y_parameter, 0, 1, 1)
        self.parameter_QGridLayout.setColumnStretch(0, 0)

    # noinspection PyPep8Naming
    def setup_ui_parameter_text_field(self, parameter_name: str, parameter_Tooltip: str) -> None:
        """
        Add text field (Qt LineEdit) UI components for a command parameter.

        Args:
            parameter_name (str):  Parameter name.
            parameter_Tooltip (str):  Tooltip text.

        Returns:
            None
        """
        debug = True
        if self.debug:
            logger = logging.getLogger(__name__)
            logger.info("For parameter '" + parameter_name + "', adding label")
        # noinspection PyPep8Naming
        parameter_QLineEdit = QtWidgets.QLineEdit(self.parameter_QFrame)
        parameter_QLineEdit.setObjectName(parameter_name)
        self.parameter_QGridLayout.addWidget(parameter_QLineEdit, self.y_parameter, 1, 1, 4)
        self.parameter_QGridLayout.setColumnStretch(1, 4)
        if parameter_Tooltip != "":
            parameter_QLineEdit.setToolTip(parameter_Tooltip)
        # Create a listener that reacts if the line edit field has been changed. If so, run the
        # refresh_ui function.
        # If this command is being updated add the command parameters to the text fields
        if self.update:
            parameter_value = self.command.get_parameter_value(parameter_name)
            parameter_QLineEdit.setText(parameter_value)
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        parameter_QLineEdit.textChanged.connect(self.refresh_ui)
        # Add the component to the list maintained to get values out of UI components
        self.input_ui_components[parameter_name] = parameter_QLineEdit
        # Set the component as the first in dialog, so that focus can be set to it
        if self.first_input_component is None:
            self.first_input_component = parameter_QLineEdit

    def ui_action_select_file(self, event_button: QtWidgets.QPushButton) -> None:
        """
        Open a file selector dialog to select an input or output file (or folder) to be used as a command
        parameter value.

        Args:
            event_button (QPushButton): the instance of the button for which the event is generated.
            Use to get the parameter name, so as to get other parameter/component data.

        Returns:
            None
        """

        logger = logging.getLogger(__name__)

        self.check_command_file_saved()

        # Initialize folder to None and determine below with several checks.
        folder_start = None

        # Get properties to configure the file selector.
        # - use the object name to parse out the parameter name
        object_name = event_button.objectName()
        print("object_name=" + str(object_name))
        parameter_name = object_name.split(".")[0]
        # Do the following first because it influences defaults below
        request_key = parameter_name + "." + "FileSelector.SelectFolder"
        select_folder = False
        try:
            # The following should match ParameterName.FileSelectorTitle
            select_folder = self.command.command_parameter_metadata[request_key]
        except KeyError:
            # Default was specified above...
            pass
        request_key = parameter_name + "." + "FileSelector.Title"
        if select_folder:
            select_file_title = "Select folder"
        else:
            select_file_title = "Select file"
        try:
            # The following should match ParameterName.FileSelectorTitle
            select_file_title = self.command.command_parameter_metadata[request_key]
        except KeyError:
            # Default was specified above...
            pass

        # Get the existing value in the text field, which will correspond to the parameter name value.
        # - if specified as absolute path, use it as is
        # - if a relative path, append to the working directory or if that is not available the user's home folder
        # noinspection PyPep8Naming
        parameter_QLineEdit = None
        working_dir = self.command.command_processor.get_property('WorkingDir')
        user_folder = self.app_session.get_user_folder()
        try:
            # noinspection PyPep8Naming
            parameter_QLineEdit = self.input_ui_components[parameter_name]
            # Get the parameter value
            parameter_value = parameter_QLineEdit.text()
            # If the parameter is empty or null
            if parameter_value is None or parameter_value == "":
                # Try to set the folder to the working directory first
                if working_dir is not None:
                    folder_start = working_dir
                else:
                    # Finally, use the user's home folder
                    folder_start = self.app_session.get_user_folder()
            else:
                # The parameter is specified.
                if os.path.isabs(parameter_value):
                    # The input is an absolute path so use as is
                    folder_start = parameter_value
                else:
                    # The input is relative to the working directory so append to working directory with
                    # filesystem separator.
                    if working_dir is not None:
                        folder_start = io_util.to_absolute_path(working_dir, parameter_value)
                    else:
                        folder_start = io_util.to_absolute_path(user_folder, parameter_value)
        except KeyError:
            # Can't determine the input component so will assume the working directory, if available
            if working_dir is not None:
                folder_start = working_dir
            else:
                # Finally, use the user's home folder
                folder_start = user_folder

        # A browser window will appear to allow the user to browse to the desired file.
        # The absolute pathname of the command file is added to the cmd_filepath variable.
        use_qt_dialog = True  # For now use Qt build-in dialog but may want to try native dialog
        filepath_selected = None
        if use_qt_dialog:
            # noinspection PyPep8Naming
            parameter_QFileDialog = QtWidgets.QFileDialog(self, select_file_title, folder_start)
            if select_folder:
                # A directory is being selected
                parameter_QFileDialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
            if parameter_QFileDialog.exec_() == QtWidgets.QFileDialog.Accepted:
                filepath_selected = parameter_QFileDialog.selectedFiles()[0]

        if not filepath_selected:
            # The file selection was canceled
            return

        # Convert the selected file path to relative path, using the command file folder as the working directory.
        if working_dir is not None:
            filepath_selected = io_util.to_relative_path(working_dir, filepath_selected)

        # Set the file in the text field.
        parameter_QLineEdit.setText(filepath_selected)

        # Set the component as the first in dialog, so that focus can be set to it
        if self.first_input_component is None:
            self.first_input_component = parameter_QLineEdit

    def update_command_display(self):
        """
        Each command dialog box has a command display that shows the string representation of the command with the
        user-specified input parameters. It is updated dynamically as the user enters/selects values for the different
        command parameter fields (this function is called when any text is changed in the input field Qt widgets). The
        function is responsible for reading the inputs, creating the updated string representation of the command and
        updating the CommandDisplay widget.

        Return: None
        """

        # Iterate over the command parameters.
        for command_parameter in self.parameters_list:

            # Get the Qt Widget associated with the command parameter.
            ui_obj = self.input_edit_objects[command_parameter]

            # Get the user-specified value entered in the command parameter Qt Widget input field.
            value = self.get_current_value(ui_obj)

            # Update the current values dictionary with the new user-specified value.
            self.command_parameter_current_values[command_parameter] = value

        # If all of the command parameter values are set to "" (not set), continue.
        if list(self.command_parameter_current_values.values()).count("") == len(self.command_parameter_current_values):

            # The Command Display field should print the command name followed by an empty parenthesis.
            # Ex: ReadGeoLayerFromGeoJSON()
            display = "{}()".format(self.command_name)

        # If AT LEAST ONE command parameter value has been set by the user, continue.
        else:

            # The parameter string text is a string that holds the user-specified parameter values for the
            # command's parameters in a "CommandParameterName=CommandParameterValue" format.
            parameter_string_text = ""

            # Iterate over the command parameters.
            for command_parameter in self.parameters_list:

                # Get the current user-specified value.
                value = self.command_parameter_current_values[command_parameter]

                # If there is a value, add the parameter name and parameter value to the parameter_string_text in a
                # "CommandParameterName=CommandParameterValue" format. A comma is added at the end in order to set up
                # for the next command parameter.
                if value != "":
                    text = '{}="{}", '.format(command_parameter, value)
                    parameter_string_text += text

            # After all of the command parameters with user-specified values have been added to the
            # parameter_string_text, remove the final comma.
            updated_parameter_string_text = parameter_string_text.rsplit(", ", 1)[0]

            # The Command Display field should print the command name followed by a parenthesis filled with the
            # command parameters and associated values.
            # Ex: ReadGeoLayerFromGeoJSON(SpatialDataFile="C:/example/path.geojson", GeoLayerID="Example")
            display = "{}({})".format(self.command_name, updated_parameter_string_text)

        # Update the Command Display Qt Widget to display the dynamic command display text.
        self.CommandDisplay_View_TextBrowser.setText(display)

    def view_documentation(self, ref_command_name: str = None) -> None:
        """
        View the command's user documentation in the default browser.

        Args:
            ref_command_name (str):  Command name for command reference, defaults to the command name.

        Returns:
            None
        """

        # Open the command's user documentation in the default browser.
        logger = logging.getLogger(__name__)
        command_doc_url = None
        command_name = self.command.command_name
        if ref_command_name is not None and ref_command_name != "":
            # Use the specific command name for documentation
            # TODO smalers 2019-01-19 why does ref_command_name have a value of False here?
            # logger.info("Viewing documentation for command name '" + str(command_name) +
            #             "' ref='"+str(ref_command_name)+"'")
            # command_name = ref_command_name
            pass
        # noinspection PyBroadException
        try:
            user_doc_url = app_util.get_property('ProgramUserDocumentationUrl')
            if user_doc_url is None:
                qt_util.warning_message_box(
                    "Can't view documentation...no application configuration value for 'ProgramUserDocumenationUrl'")
                return
            # Append the command name to the documentation
            logger.info("Now, command name '" + str(command_name) + "'")
            command_doc_url = "{}/command-ref/{}/{}/".format(user_doc_url, command_name, command_name)
            # message = "Displaying command documentation using URL: " + command_doc_url
            # logger.info(message)
            # Open the command's user documentation in the default browser.
            # - open in a new tab or if this fails open a new window
            # noinspection PyBroadException
            try:
                webbrowser.open_new_tab(command_doc_url)
            except Exception:
                # Try the other variant, may work on different operating system
                webbrowser.open(command_doc_url)
        except Exception:
            message = 'Error viewing command documentation using url "' + str(command_doc_url) + '"'
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
