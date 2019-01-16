# CommentBlockEndEditor - editor for */ command editor
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

from PyQt5 import QtCore, QtGui, QtWidgets
import geoprocessor.util.app_util as app_util
import geoprocessor.ui.util.qt_util as qt_util
import functools
import logging
import webbrowser

try:
    _fromUtf8 = lambda s: s
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

# Combining code from GenericCommandEditor and AbstractCommandEditor to create
# one stand alone editor


class InsertLineEditor(QtWidgets.QDialog):
    """
    Abstract command editor used as parent of command editor dialog implementations.
    This class maintains core layout information and provides functions to add components.
    """

    # def __init__(self, command_name, command_description, parameter_count, command_parameters, current_values):
    def __init__(self, command):
        """
        Initialize the Abstract Dialog instance.

        Args:
            command_name (str): the name of the GeoProcessor command that the Dialog box is representing
            # command_description (str): the description of the GeoProcessor command that the Dialog box is representing
            # parameter_count (int): the number of command parameters of the GeoProcessor command that the Dialog box is
            #    representing
            # command_parameters (list): a list of string representing the command parameter names (in order) of the
            #    GeoProcessor command that the Dialog box is representing
            # current_values (dic):  a dictionary that holds the command parameters and their current values
            #    Key: the name of the command parameter
            #    Value: the entered value of the command parameter
        """
        # Call the parent class
        super().__init__()

        # Command being edited
        self.command = command

        # "input_edit_objects" is a dictionary that relates each command parameter with its associated Qt Widget
        # input field
        # KEY (str): the command parameter name
        # VALUE (obj): the associated Qt Widget input field
        # self.input_edit_objects = {}

        # "command_parameter_current_values" is a dictionary that holds the command parameters and their current values
        # KEY (str): the name of the command parameter
        # VALUE (str): the entered value of the command parameter
        # self.command_parameter_current_values = current_values

        # Initialize components that will be used
        self.CommandDisplay_View_TextBrowser = None

        # Layout used for the main editor
        # - other layouts may be added as needed to organize components
        self.grid_layout = None

        # Position in the layout for components as they are added, 0=row at top, 1 is next down, etc.
        # - each addition should increment before adding a component
        self.grid_layout_row = -1

        # Set up the UI for the command editor window
        self.setup_ui_core()

        # Create variable to know if we are updating an existing command
        # or inserting a new command into the command list
        self.update = False
        # if command parameters have already been defined for command
        # we know that we are updating an existing command
        if command.command_parameters:
            self.update = True

    def add_ui_horizontal_separator(self):
        # Create a line (frame object with special specifications). Add the line to the Dialog window.
        # Set the size policy, the shape, the shadow, and the name of the frame object to create the line separator.
        # The frame object, Separator, separates the command description from the input form section of the Dialog box.
        self.Separator = QtWidgets.QFrame(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Separator.sizePolicy().hasHeightForWidth())
        self.Separator.setSizePolicy(sizePolicy)
        self.Separator.setFrameShape(QtWidgets.QFrame.HLine)
        self.Separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.Separator.setObjectName(_fromUtf8("Separator"))
        self.grid_layout_row = self.grid_layout_row + 1
        self.grid_layout.addWidget(self.Separator, self.grid_layout_row, 0, 1, 8)

    def setup_ui_core(self):
        # Set up the editor core elements, which apply to any command.
        self.setup_ui_core_top()
        # Add separator
        self.add_ui_horizontal_separator()
        # Set up the core components at the bottom
        self.setup_ui_core_bottom()

        # This will wire up the signals and slots depending on names.
        # REF: http://joat-programmer.blogspot.com/2012/02/pyqt-signal-and-slots-to-capture-events.html
        # - don't do this because not using QtDesigner
        # QtCore.QMetaObject.connectSlotsByName(self)

    def setup_ui_core_bottom(self):
        """
        Setup core UI components at the bottom of the dialog.

        Returns:  None
        """
        self.setup_ui_core_command_area()
        self.setup_ui_core_command_buttons()

    def setup_ui_core_top(self):
        """
        Setup core UI components at the top of the dialog.

        Returns:  None
        """
        # Set the window title to the command name
        self.setObjectName("InsertLineCommand")
        self.setWindowTitle("Edit " + self.command.command_name + " command")
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        icon_path = app_util.get_property("ProgramIconPath").replace('\\','/')
        self.setWindowIcon(QtGui.QIcon(icon_path))

        # Because components are added to the UI the dialog will have a size.
        # - don't set the size unless a dialog misbehaves, perhaps a maximum size
        # self.resize(684, 404)

        # Add a grid layout for components to be added
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setObjectName(_fromUtf8("gridLayout"))

        self.setup_ui_core_command_description()

    def setup_ui_core_command_area(self):
        # Create a label object to the Dialog window.
        # Set the alignment, the name, and the text of the label.
        # The label, Command Display_Label, labels the CommandDisplay_View_TextBrowser text edit object.
        self.grid_layout_row = self.grid_layout_row + 1
        self.CommandDisplay_Label = QtWidgets.QLabel(self)
        self.CommandDisplay_Label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.CommandDisplay_Label.setObjectName(_fromUtf8("CommandDisplay_Label"))
        self.CommandDisplay_Label.setText(_translate("Dialog", "Command: ", None))
        self.grid_layout.addWidget(self.CommandDisplay_Label, self.grid_layout_row, 0, 2, 1)
        # Create a text edit object. Add the text edit object to the Dialog window.
        # Set the size, the name and the html of the text edit object.
        # The text edit object, CommandDisplay_View_TextBrowser, displays a dynamic view of the command string.
        self.CommandDisplay_View_TextBrowser = QtWidgets.QTextEdit(self)
        self.CommandDisplay_View_TextBrowser.setObjectName("CommandDisplay_View_TextBrowser")
        command_string = self.command.command_string
        print(command_string)
        if command_string == "Blank()":
            command_string = ""
        if command_string.endswith("()"):
            command_string = command_string[:-2]
        self.CommandDisplay_View_TextBrowser.setText(command_string)
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
        self.grid_layout.addWidget(self.CommandDisplay_View_TextBrowser, self.grid_layout_row, 1, 1, -1)

    def setup_ui_core_command_buttons(self):
        # Create a button box object. Add the button box object to the Dialog window.
        # Set the orientation, the standard buttons, the name and the connections of the button box object.
        # The button box object, OK_Cancel_Buttons, allow the user to accept or reject the changes made in the dialog.
        self.OK_Cancel_Buttons = QtWidgets.QDialogButtonBox(self)
        self.OK_Cancel_Buttons.setOrientation(QtCore.Qt.Horizontal)
        self.OK_Cancel_Buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.OK_Cancel_Buttons.setObjectName(_fromUtf8("OK_Cancel_Buttons"))
        self.OK_Cancel_Buttons.button(QtWidgets.QDialogButtonBox.Cancel).setToolTip(
            "Cancel command edit and ignore changes.")
        self.OK_Cancel_Buttons.button(QtWidgets.QDialogButtonBox.Ok).setToolTip("Save edits to command.")
        self.OK_Cancel_Buttons.accepted.connect(self.accept)
        self.OK_Cancel_Buttons.rejected.connect(self.reject)
        self.grid_layout_row = self.grid_layout_row + 1
        self.grid_layout.addWidget(self.OK_Cancel_Buttons, self.grid_layout_row, 6, 1, 2)

    def setup_ui_core_command_description(self):
        """
        Setup the description component at the top of the dialog.
        """
        # Create a frame object. Add the frame object to the Dialog window.
        # Set the shape, the shadow, and the name of the frame object.
        # The frame object, Command_Description, holds the command description and the view documentation button.
        description_Frame = QtWidgets.QFrame(self)
        description_Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        description_Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        description_Frame.setObjectName(_fromUtf8("Command_Description"))
        self.grid_layout_row = self.grid_layout_row + 1
        self.grid_layout.addWidget(description_Frame, self.grid_layout_row, 0, 1, 0)

        # Create a grid layout object. Apply to the Command_Description frame object.
        # Set the name of the grid layout object.
        self.gridLayout_2 = QtWidgets.QGridLayout(description_Frame)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))

        # Create a label. Add the label to the Command_Description frame object.
        # Set the name and the text of the label.
        # The label, Command_Description_Label, briefly describes the command.
        self.Command_Description_Label = QtWidgets.QLabel(description_Frame)
        self.Command_Description_Label.setObjectName(_fromUtf8("Command_Description_Label"))
        self.Command_Description_Label.setText("This command ends a multi-line comment block, which is useful for "
                                               "commenting out multiple commands.\n"
                                               "Use the /* command to start the comment block.\n"
                                               "See also the # command for commenting single lines.\n")
        self.gridLayout_2.addWidget(self.Command_Description_Label, 0, 0, 1, 2)

    def update_command_display(self):
        """
        Each command dialog box has a command display that shows the string representation of the command with the
        user-specified input parameters. It is updated dynamically as the user enters/selects values for the different
        command parameter fields (this function is called when any text is changed in the input field Qt widgets). The
        function is responsible for reading the inputs, creating the updated string representation of the command and
        updating the CommandDisplay widget.

        Returns:
            None
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

    def get_current_value(self, obj):
        """
        Get the value within a QtGui.Widget object.

        Args:
            obj (obj): the a QtGui.Widget object to read the value from

        Returns:
            the value within the QtGui.Widget object
        """

        # Different QtGui widgets have different ways of reading their input data. Try both versions and assign the
        # value when one works.
        # Reads LineEdit widgets.
        try:
            value = obj.text()

        # Reads ComboBox widgets.
        except:
            value = obj.currentText()

        # Return the value within the input QtGui.Widget object.
        return value
