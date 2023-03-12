# TabbedCommandEditor - class for tabbed command editors
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

from PyQt5 import QtCore, QtWidgets
from geoprocessor.ui.commands.abstract.AbstractCommandEditor import AbstractCommandEditor

import geoprocessor.ui.util.qt_util as qt_util


class TabbedCommandEditor(AbstractCommandEditor):
    """
    Tabbed command editor interface, used for commands with many parameters or when parameters need to be grouped.

    **This editor is not currently functional and is not used by any commands.**
    """

    def __init__(self, command) -> None:
        """
        Initialize the TabbedCommandEditor dialog instance.

        Args:
        """
        # TODO smalers 2020-01-16 need to figure out what this is.
        # command_name (str): the name of the GeoProcessor command that the Dialog box is representing
        # command_description (str): the description of the GeoProcessor command that the Dialog box is representing
        # parameter_count (int):
        #     the number of command parameters of the GeoProcessor command that the Dialog box is representing
        # command_parameters (list): a list of string representing the command parameter names (in order) of the
        #     GeoProcessor command that the Dialog box is representing
        # current_values (dic):  a dictionary that holds the command parameters and their current values
        #     Key: the name of the command parameter
        #     Value: the entered value of the command parameter
        super().__init__(command)

        # The name of the GeoProcessor command that the Dialog box is representing.
        # #self.command_name = command_name

        # TODO smales 2020-01-16 evaluate standardizing the buttons.
        # NOT defined in AbstractCommandEditor - local to this class.
        # UI components at the top of the dialog.
        # Description of the GeoProcessor command that the Dialog box is representing.
        # #self.command_description = command_description
        self.Command_Description: QtWidgets.QFrame or None = None
        self.gridLayout: QtWidgets.QGridLayout or None = None

        # The number of command parameters of the GeoProcessor command that the Dialog box is representing.
        # #self.parameter_count = parameter_count

        # List of strings representing the command parameter names (in order) of the
        # GeoProcessor command that the Dialog box is editing.
        # #self.parameters_list = command_parameters

        # TODO smales 2020-01-16 evaluate standardizing the buttons.
        # NOT defined in AbstractCommandEditor - local to this class.
        # Buttons at the bottom of the dialog.
        self.OK_Cancel_Buttons: QtWidgets.QDialogButtonBox or None = None

        # Defined in AbstractCommandEditor.
        # The dictionary that relates each command parameter with its associated Qt Widget input field.
        # KEY (str): the command parameter name
        # VALUE (obj): the associated Qt Widget input field
        self.input_edit_objects = {}

        # The dictionary that holds the command parameters and their current values.
        # KEY (str): the name of the command parameter
        # VALUE (str): the entered value of the command parameter
        # #self.command_parameter_current_values = current_values

    # TODO smalers 2020-01-14 evaluate whether this function is ever called - is it needed?
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

    def get_current_value(self, obj: QtWidgets.QWidget) -> str:
        """
        Get the value within a QtGui.Widget object.

        Arg:
            obj (obj): the a QtGui.Widget object to read the value from

        Return: the value within the QtGui.Widget object
        """

        # Different QtGui widgets have different ways of reading their input data.
        # Try both versions and assign the value when one works.
        # Reads LineEdit widgets.
        # noinspection PyBroadException
        try:
            value = obj.text()

        # Reads ComboBox widgets.
        except Exception:
            value = obj.currentText()

        # Return the value within the input QtGui.Widget object.
        return value

    # noinspection PyPep8Naming
    def setup_ui_abstract(self, Dialog: QtWidgets.QDialog) -> None:
        """
        Sets up a Dialog object with the features that are common across all GeoProcessor command dialog windows.

        Arg:
            Dialog: a QDialog window instance (QtGui.QDialog())

        Return: None
        """

        # Set the name, the initial size and the window title (the name of the command) of the Dialog window object.
        # The Dialog window object, Dialog, represents the entire dialog window.
        Dialog.setObjectName(qt_util.from_utf8("Dialog"))
        Dialog.resize(684, 404)

        # See if title is specified as 'EditorTitle' property (used for commands that don't follow the normal pattern).
        editor_title = None
        try:
            editor_title = self.command.command_metadata['EditorTitle']
        except KeyError:
            editor_title = None
        if editor_title is not None:
            self.setWindowTitle(editor_title)
        else:
            # Typical CommandName() command.
            self.setWindowTitle("Edit " + self.command.command_name + " command")

        # Create a grid layout object. Apply the grid layout to the Dialog window object.
        # Set the name of the grid layout object.
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName(qt_util.from_utf8("gridLayout"))

        # Create a frame object. Add the frame object to the Dialog window.
        # Set the shape, the shadow, and the name of the frame object.
        # The frame object, Command_Description, holds the command description and the view documentation button.
        self.Command_Description = QtWidgets.QFrame(Dialog)
        self.Command_Description.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Command_Description.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Command_Description.setObjectName(qt_util.from_utf8("Command_Description"))
        self.gridLayout.addWidget(self.Command_Description, 0, 0, 1, 8)

        # Create a grid layout object. Apply to the Command_Description frame object.
        # Set the name of the grid layout object.
        grid_layout_2 = QtWidgets.QGridLayout(self.Command_Description)
        grid_layout_2.setObjectName(qt_util.from_utf8("grid_layout_2"))

        # Create a spacer. Add the spacer to the Command_Description frame object.
        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        grid_layout_2.addItem(spacer_item, 2, 0, 1, 1)

        # Create a push button. Add the button to the Command_Description frame object.
        # Set the name, the button text and the connection of the push button.
        # The push button, View_Documentation_Button, displays the command's online user documentation when clicked.
        self.View_Documentation_Button = QtWidgets.QPushButton(self.Command_Description)
        self.View_Documentation_Button.setObjectName(qt_util.from_utf8("View_Documentation_Button"))
        self.View_Documentation_Button.setText(qt_util.translate("Dialog", "  View Documentation  ", None))
        # Use the following because connect() is shown as unresolved reference in PyCharm.
        # noinspection PyUnresolvedReferences
        self.View_Documentation_Button.clicked.connect(self.view_documentation)
        grid_layout_2.addWidget(self.View_Documentation_Button, 2, 1, 1, 1)

        # Create a label. Add the label to the Command_Description frame object.
        # Set the name and the text of the label.
        # The label, Command_Description_Label, briefly describes the command.
        self.Command_Description_Label = QtWidgets.QLabel(self.Command_Description)
        self.Command_Description_Label.setObjectName(qt_util.from_utf8("Command_Description_Label"))
        self.Command_Description_Label.setText(qt_util.translate("Dialog", self.command_description, None))
        grid_layout_2.addWidget(self.Command_Description_Label, 0, 0, 1, 2)

        # Create a line (frame object with special specifications). Add the line to the Dialog window.
        # Set the size policy, the shape, the shadow, and the name of the frame object to create the line separator.
        # The frame object, Separator, separates the command description from the input form section of the Dialog box.
        self.Separator = QtWidgets.QFrame(Dialog)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.Separator.sizePolicy().hasHeightForWidth())
        self.Separator.setSizePolicy(size_policy)
        self.Separator.setFrameShape(QtWidgets.QFrame.HLine)
        self.Separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.Separator.setObjectName(qt_util.from_utf8("Separator"))
        self.gridLayout.addWidget(self.Separator, 1, 0, 1, 8)

        # Create a button box object. Add the button box object to the Dialog window.
        # Set the orientation, the standard buttons, the name and the connections of the button box object.
        # The button box object, OK_Cancel_Buttons, allow the user to accept or reject the changes made in the dialog.
        self.OK_Cancel_Buttons = QtWidgets.QDialogButtonBox(Dialog)
        self.OK_Cancel_Buttons.setOrientation(QtCore.Qt.Horizontal)
        self.OK_Cancel_Buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.OK_Cancel_Buttons.setObjectName(qt_util.from_utf8("OK_Cancel_Buttons"))
        # Use the following because connect() is shown as unresolved reference in PyCharm.
        # noinspection PyUnresolvedReferences
        self.OK_Cancel_Buttons.accepted.connect(Dialog.accept)
        # Use the following because connect() is shown as unresolved reference in PyCharm.
        # noinspection PyUnresolvedReferences
        self.OK_Cancel_Buttons.rejected.connect(Dialog.reject)
        self.gridLayout.addWidget(self.OK_Cancel_Buttons, self.parameter_count + 4, 6, 1, 2)

        # Create a text edit object. Add the text edit object to the Dialog window.
        # Set the size, the name and the html of the text edit object.
        # The text edit object, CommandDisplay_View_TextBrowser, displays a dynamic view of the command string.
        self.CommandDisplay_View_TextBrowser = QtWidgets.QTextEdit(Dialog)
        self.CommandDisplay_View_TextBrowser.setMinimumSize(QtCore.QSize(0, 100))
        self.CommandDisplay_View_TextBrowser.setMaximumSize(QtCore.QSize(16777215, 100))
        self.CommandDisplay_View_TextBrowser.setObjectName(qt_util.from_utf8("CommandDisplay_View_TextBrowser"))
        html = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">" \
               "\n<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\np, li { " \
               "white-space: pre-wrap; }\n</style></head><body style=\" font-family:\'MS Shell Dlg 2\';" \
               " font-size:8.25pt; font-weight:400; font-style:normal;\">\n<p style=\" margin-top:0px;" \
               " margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">" \
               "<span style=\" font-size:8pt;\">ReadGeoLayerFromGeoJSON()</span></p></body></html>"
        self.CommandDisplay_View_TextBrowser.setHtml(qt_util.translate("Dialog", html, None))
        self.gridLayout.addWidget(self.CommandDisplay_View_TextBrowser, self.parameter_count + 3, 1, 1, -1)

        # Create a label object to the Dialog window.
        # Set the alignment, the name, and the text of the label.
        # The label, Command Display_Label, labels the CommandDisplay_View_TextBrowser text edit object.
        self.CommandDisplay_Label = QtWidgets.QLabel(Dialog)
        self.CommandDisplay_Label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.CommandDisplay_Label.setObjectName(qt_util.from_utf8("CommandDisplay_Label"))
        self.CommandDisplay_Label.setText(qt_util.translate("Dialog", "Command: ", None))
        self.gridLayout.addWidget(self.CommandDisplay_Label, self.parameter_count + 3, 0, 1, 1)

        # Create a spacer. Add the spacer to the Dialog window.
        # The spacer separates the input parameter value fields from the Command Display text browser.
        spacer_item2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacer_item2, self.parameter_count + 2, 3, 1, -1)

        # This will wire up the signals and slots depending on names.
        # REF: http://joat-programmer.blogspot.com/2012/02/pyqt-signal-and-slots-to-capture-events.html
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def update_command_display(self) -> None:
        """
        Each command dialog box has a command display that shows the string representation of the command with the
        user-specified input parameters. It is updated dynamically as the user enters/selects values for the different
        command parameter fields (this function is called when any text is changed in the input field Qt widgets).
        The function is responsible for reading the inputs, creating the updated string representation of the command
        and updating the CommandDisplay widget.

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
                # "CommandParameterName=CommandParameterValue" format.
                # A comma is added at the end in order to set up for the next command parameter.
                if value != "":
                    text = '{}="{}", '.format(command_parameter, value)
                    parameter_string_text += text

            # After all the command parameters with user-specified values have been added to the
            # parameter_string_text, remove the final comma.
            updated_parameter_string_text = parameter_string_text.rsplit(", ", 1)[0]

            # The Command Display field should print the command name followed by a parenthesis filled with the
            # command parameters and associated values.
            # Ex: ReadGeoLayerFromGeoJSON(InputFile="C:/example/path.geojson", GeoLayerID="Example")
            display = "{}({})".format(self.command_name, updated_parameter_string_text)

        # Update the Command Display Qt Widget to display the dynamic command display text.
        self.CommandDisplay_View_TextBrowser.setText(display)

    @staticmethod
    def select_file(qt_widget: QtWidgets.QWidget) -> None:
        """
        Opens a file browser to allow a user to select a file through a Qt predefined user interface.
        The path of the selected file is added to the qt_widget Qt Widget input field.

        Args:
            qt_widget (obj): the Qt Widget that will display the full path of the selected file

        Return: None
        """

        # Open the browser for file selection. Save the full path of the selected file as a string.
        file_name_text = QtWidgets.QFileDialog.getOpenFileName()[0]

        # Add the full path of the selected file string to the specified input Qt Widget.
        qt_widget.setText(file_name_text)
