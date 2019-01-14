# AbstractCommandEditor_Simple - class for simple command editors
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

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from geoprocessor.ui.commands.abstract.AbstractCommandEditor import AbstractCommandEditor
import functools
import webbrowser

import geoprocessor.ui.util.qt_util as qt_util

import logging

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

class AbstractCommandEditor_Simple(AbstractCommandEditor):

    def __init__(self, command, app_session):
        """
        Initialize the Abstract Dialog instance.

        Args:
            command_name (str): the name of the GeoProcessor command that the Dialog box is representing
            command_description (str): the description of the GeoProcessor command that the Dialog box is representing
            parameter_count (int): the number of command parameters of the GeoProcessor command that the Dialog box is
                representing
            command_parameters (list): a list of string representing the command parameter names (in order) of the
                GeoProcessor command that the Dialog box is representing
            current_values (dic):  a dictionary that holds the command parameters and their current values
                Key: the name of the command parameter
                Value: the entered value of the command parameter
        """

        super().__init__(command)

        # "command_name" is the name of the GeoProcessor command that the Dialog box is representing.
        self.command_name = command.command_name

        # Array of text fields (Qt LineEdit) containing parameter values, with object name matching parameter name
        self.parameter_LineEdit = [None] * len(self.command.command_parameter_metadata)
        # Array of drop down menus
        self.drop_down_menu = [None] * len(self.command.command_parameter_metadata)

        # This is a session object to keep track of session variables such as command file history
        self.app_session = app_session

        # "command_description" is the description of the GeoProcessor command that the Dialog box is representing
        ##self.command_description = command_description

        # "parameter_count" is the number of command parameters of the GeoProcessor command that the Dialog box is
        # representing
        ##self.parameter_count = parameter_count

        # "parameters_list" is a list of strings representing the command parameter names (in order) of the
        # GeoProcessor command that the Dialog box is representing
        ##self.parameters_list = command_parameters

        # "input_edit_objects" is a dictionary that relates each command parameter with its associated Qt Widget
        # input field
        # KEY (str): the command parameter name
        # VALUE (obj): the associated Qt Widget input field
        self.input_edit_objects = {}

        # "command_parameter_current_values" is a dictionary that holds the command parameters and their current values
        # KEY (str): the name of the command parameter
        # VALUE (str): the entered value of the command parameter
        ##self.command_parameter_current_values = current_values

        # Setup the UI in the abstract class, which will call back to set_ui() in this class.
        self.setup_ui_core()

        # Initially call refresh in case updating a command
        self.refresh_command()

    def are_required_parameters_specified(self, ui_command_parameter_list):
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

    def configureLabel(self, label, parameter_name):
        """
        Configure a QtGui.QLabel object (parameter name label) that meets the standards of the GeoProceossor's
        command dialog window.

        Args:
            label (obj): a QtGui.QLabel object
            parameter_name (str): the name of the command parameter that is using the label

        Return: None
        """

        # Set the label to align right so that it butts up next to the input field.
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        # Set the label's object name (XXX_Label where XXX is the name of the command parameter).
        label.setObjectName(_fromUtf8("{}_Label".format(parameter_name)))

        # Get the dialog box row index that is used to display the command parameter objects
        # This is a dynamic index that takes into consideration the order of the command's parameters.
        row_index = self.parameters_list.index(parameter_name) + 2

        # Add the label to the Dialog box in the correct row. Command labels will always be in the first column (0),
        # and will occupy 1 column and 1 row.
        self.gridLayout.addWidget(label, row_index, 0, 1, 1)

        # Set the text of the label to be the name of the command parameter.
        label.setText(_translate("Dialog", "{}: ".format(parameter_name), None))

    def configureLineEdit(self, line_edit, parameter_name, long=False, placeholder_text=None, tooltip=None):
        """
        Configure a QtGui.QLineEdit object that meets the standards of the GeoProceossor's command dialog window.

        Args:
            line_edit (obj): a QtGui.QLineEdit object
            parameter_name (str): the name of the command parameter that is using the line edit field
            long (bool): if TRUE, the QtGui.QLineEdit object spans the majority of the dialog window. This is good
                for parameter values that will be an absolute file path. if FALSE, the QtGui.QLineEdit object spans a
                subset of the dialog window. This is good gor parameter value that one require a one/few word value.
            placeholder_text (str): optional. The text that will display within the QtGui.QLineEdit object before the
                user enters a value. This is helpful to supply a parameter description when `long` is set to `True`.
            tooltip (str): optional. The text that will display in a pop-up when the user mouses over the
                QtGui.QLineEdit object. This is a good place to expand description of the parameter/parameter values.

        Return: None
        """

        # Set the line edit's object name (XXX_LineEdit where XXX is the name of the command parameter).
        line_edit.setObjectName(_fromUtf8("{}_LineEdit".format(parameter_name)))

        # Get the dialog box row index that is used to display the command parameter objects
        # This is a dynamic index that takes into consideration the order of the command's parameters.
        row_index = self.parameters_list.index(parameter_name) + 2

        # Add the line edit field to the Dialog box in the correct row. Command line edit fields will always start in
        # the second column (1) and will occupy 1 row.
        # If the field is set to long, the line edit field will occupy 6 columns.
        if long:
            self.gridLayout.addWidget(line_edit, row_index, 1, 1, 6)

        # If not set to long, the line edit field will occupy 3 columns.
        else:
            self.gridLayout.addWidget(line_edit, row_index, 1, 1, 3)

        # If placeholder text has been specified, add the desired text as placeholder text.
        if placeholder_text:
            line_edit.setPlaceholderText(_translate("Dialog", placeholder_text, None))

        # If tool tip text has been specified, add the desired text as tool tip text.
        if tooltip:
            line_edit.setToolTip(_translate("Dialog", tooltip, None))

        # Create a listener that reacts if the line edit field has been changed. If so, run the
        # update_command_display function.
        line_edit.textChanged.connect(self.update_command_display)

        # Add the QtGui.QLineEdit object to the dictionary of input edit objects. Use the parameter name as the key
        # and the QtGui.QLineEdit object as the value.
        self.input_edit_objects[parameter_name] = line_edit

    def configureToolButton(self, tool_button, parameter_name, line_edit_obj_affected):
        """
        Configures a QtGui.QToolButton object that meets the standards of the GeoProceossor's command dialog window.

        Args:
            tool_button (obj): a QtGui.QToolButton object
            parameter_name (str): the name of the command parameter that is using the tool button
            line_edit_obj_affected (obj): a QtGui.QLineEdit object that will be populated with the filepath text of
                the selected file selected with the tool button

        Returns: the path to the selected file
        """

        # Set the tool buttons's object name (XXX_ToolButton where XXX is the name of the command parameter).
        tool_button.setObjectName(_fromUtf8("{}_ToolButton".format(parameter_name)))

        # Set the tool button's text. (Default value is `...` but this can be pulled out into a function argument if
        # needed.)
        tool_button.setText(_translate("Dialog", "...", None))

        # Get the dialog box row index that is used to display the command parameter objects
        # This is a dynamic index that takes into consideration the order of the command's parameters.
        row_index = self.parameters_list.index(parameter_name) + 2

        # Add the tool button to the Dialog box in the correct row. Command tool buttons will always be in the
        # last column (7), and will occupy 1 row and 1 column.
        self.gridLayout.addWidget(tool_button, row_index, 7, 1, 1)

        # Create a listener that reacts if the tool button is clicked. If so, run the select_file function to allow
        # the user to browse to a local file.
        tool_button.clicked.connect(functools.partial(self.select_file, line_edit_obj_affected))

    def configureDescriptionLabel(self, label, parameter_name, text):
        """
        Configure a QtGui.QLabel object (parameter description label) that meets the standards of the GeoProcessor's
        command dialog window.

        Args:
            label (obj): a QtGui.QLabel object
            parameter_name (str): the name of the command parameter that is using the label
            text (str): the parameter description to use as the label text

        Return: None
        """

        # Get the dialog box row index that is used to display the command parameter objects
        # This is a dynamic index that takes into consideration the order of the command's parameters.
        row_index = self.parameters_list.index(parameter_name) + 2

        # Set the label's object name (XXX_Description_Label where XXX is the name of the command parameter).
        label.setObjectName(_fromUtf8("{}_Description_Label".format(parameter_name)))

        # Add the label to the Dialog box in the correct row. Command description labels will always be in the
        # third-to-last column (5), and will occupy 1 column and 3 rows.
        self.gridLayout.addWidget(label, row_index, 5, 1, 3)

        # Set the text of the label to be the command parameter description.
        label.setText(_translate("Dialog", text, None))

    def configureComboBox(self, combobox, parameter_name, choice_list, tooltip=None):
        """
        Configure a QtGui.QComboBox object that meets the standards of the GeoProceossor's command dialog window.

        Args:
            combobox(obj): a QtGui.QComboBox object
            parameter_name (str): the name of the command parameter that is using the combobox field
            choice_list (list): a list of available values for the command parameter
            tooltip (str): optional. The text that will display in a pop-up when the user mouses over the
                QtGui.QComboBox object. This is a good place to expand description of the parameter/parameter values.

        Return: None
        """

        # Get the dialog box row index that is used to display the command parameter objects
        # This is a dynamic index that takes into consideration the order of the command's parameters.
        row_index = self.parameters_list.index(parameter_name) + 2

        # Set the combo box's object name (XXX_ComboBox where XXX is the name of the command parameter).
        combobox.setObjectName(_fromUtf8("{}_ComboBox".format(parameter_name)))

        # Add "spaces" to the ComboBox for each of the available options including a blank option to display that an
        # option has not been selected.
        for i in range(len(choice_list) + 1):
            combobox.addItem(_fromUtf8(""))

        # Add the combo box field to the Dialog box in the correct row. Command combo box fields will always start in
        # the second column (1) and will occupy 1 column and 2 rows.
        self.gridLayout.addWidget(combobox, row_index, 1, 1, 2)

        # Set the combo box default option to the blank option - the first (0) in the list of choices.
        combobox.setItemText(0, _fromUtf8(""))

        # Add the text associated with each parameter option to the appropriate ComboBox "space".
        for i in range(len(choice_list)):
            combobox.setItemText(i+1, _translate("Dialog", choice_list[i], None))

        # If tool tip text has been specified, add the desired text as tool tip text.
        if tooltip:
            combobox.setToolTip(_translate("Dialog", tooltip, None))

        # Add the QtGui.QComboBox object to the dictionary of input edit objects. Use the parameter name as the key
        # and the QtGui.QComboBox object as the value.
        self.input_edit_objects[parameter_name] = combobox

        # Create a listener that reacts if the ComboBox field has been changed. If so, run the
        # update_command_display function.
        combobox.currentIndexChanged.connect(self.update_command_display)

    def get_current_value(self, obj):
        """
        Get the value within a QtGui.Widget object.

        Arg:
            obj (obj): the a QtGui.Widget object to read the value from

        Return: the value within the QtGui.Widget object
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

    def setup_ui(self):
        """
        Set up the dialog UI elements.  This generic editor provides text fields for each property.

        Returns: None

        """

        # The AbstractCommandEditor sets up the editor by:
        # 1. Initializes the dialog.
        # 2. Setting up standard editor top.
        # 3. Calls this method to set up command editor specifics.
        #    Set up a simple list of command parameter text fields
        # 4. Setting up the standard editor bottom.
        # Set up an area for a list of parameters
        parameter_Frame = QtWidgets.QFrame(self)
        parameter_Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        parameter_Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        parameter_Frame.setObjectName("Command_Parameters")
        self.grid_layout_row = self.grid_layout_row + 1
        self.grid_layout.addWidget(parameter_Frame, self.grid_layout_row, 0, 1, 8)

        # Create a grid layout object. Apply to the Command_Parameters frame object.
        # Set the name of the grid layout object.
        parameter_GridLayout = QtWidgets.QGridLayout(parameter_Frame)
        parameter_GridLayout.setObjectName("Command_Parameters_Layout")

        # Add entry fields for each parameter
        self.y_parameter = -1
        for command_parameter_metadata in self.command.command_parameter_metadata:
            # # Parse through the parameter metadata and locate all the parameters
            # # that are specific to the parameter that we are working with
            # for parameter_key in self.command.parameter_input_metadata:
            #     # Split the key name
            #     # ex: URL.Group
            #     parameter_key_split = parameter_key.split(".")
            #     # "URL"
            #     parameter_name = parameter_key_split[0]
            #     # "Group"
            #     parameter_value = parameter_key_split[1]
            #     # If the parameter name matches we want to get it's metadata
            #     if command_parameter_metadata.parameter_name == parameter_name:
            #         print(parameter_value)

            # Parameter input metatata
            input_metadata = self.command.parameter_input_metadata

            # Get the parameter name for retrieving all other parameter variables from
            # parameter_input_metadata
            parameter_name = command_parameter_metadata.parameter_name
            # Get all the parameter values from parameter_input_metadata
            # Group
            request_key = parameter_name + "." + "Group"
            parameter_group = input_metadata[request_key]
            # Description
            request_key = parameter_name + "." + "Description"
            parameter_description = input_metadata[request_key]
            # Label
            request_key = parameter_name + "." + "Label"
            parameter_label = input_metadata[request_key]
            # Tooltip
            request_key = parameter_name + "." + "Tooltip"
            parameter_tooltip = input_metadata[request_key]
            # Required
            request_key = parameter_name + "." + "Required"
            parameter_required = input_metadata[request_key]
            # Values
            request_key = parameter_name + "." + "Values"
            parameter_values = input_metadata[request_key]
            # Default Value
            request_key = parameter_name + "." + "DefaultValue"
            parameter_defaultValue = input_metadata[request_key]
            # File Selector Type
            request_key = parameter_name + "." + "FileSelectorType"
            parameter_fileSelectorType = input_metadata[request_key]

            # Parameters listed in logical order
            self.y_parameter = self.y_parameter + 1
            # ---------------
            # Label component
            # ---------------
            parameter_Label = QtWidgets.QLabel(parameter_Frame)
            parameter_Label.setObjectName("Command_Parameter_Label")
            parameter_Label.setText(parameter_name + ":")
            parameter_Label.setAlignment(QtCore.Qt.AlignRight) # |QtCore.Qt.AlignCenter)
            # Allow expanding horizontally
            parameter_Label.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)
            parameter_GridLayout.addWidget(parameter_Label, self.y_parameter, 0, 1, 1)
            # --------------------
            # Text entry component
            # --------------------
            if parameter_values != "":
                self.drop_down_menu[self.y_parameter] = QtWidgets.QComboBox(parameter_Frame)
                self.drop_down_menu[self.y_parameter].setObjectName(_fromUtf8("Drop_Down_Menu"))
                self.drop_down_menu[self.y_parameter].setEditable(True)
                # Add a blank item so that there is not an initial response for the drop down
                self.drop_down_menu[self.y_parameter].addItem("")
                for i, value in enumerate(parameter_values):
                   self.drop_down_menu[self.y_parameter].addItem(value)
                self.drop_down_menu[self.y_parameter].currentIndexChanged.connect(self.refresh_command)
                parameter_GridLayout.addWidget(self.drop_down_menu[self.y_parameter], self.y_parameter, 2, 1, 1)
            else:
                self.parameter_LineEdit[self.y_parameter] = QtWidgets.QLineEdit(parameter_Frame)
                self.parameter_LineEdit[self.y_parameter].setObjectName(parameter_name)
                parameter_GridLayout.addWidget(self.parameter_LineEdit[self.y_parameter], self.y_parameter, 2, 1, 1)
                tooltip = command_parameter_metadata.editor_tooltip
                if tooltip is not None:
                    self.parameter_LineEdit[self.y_parameter].setToolTip(tooltip)
                # Create a listener that reacts if the line edit field has been changed. If so, run the
                # update_command_display function.
                # If this command is being updated add the command parameters to the text fields
                if self.update:
                    parameter_value = self.command.get_parameter_value(parameter_name)
                    self.parameter_LineEdit[self.y_parameter].setText(parameter_value)
                self.parameter_LineEdit[self.y_parameter].textChanged.connect(self.refresh_command)
                if parameter_fileSelectorType != "":
                    # -----------------
                    # Add a button
                    # -----------------
                    self.load_file_button = QtWidgets.QPushButton(parameter_Frame)
                    self.load_file_button.setObjectName(_fromUtf8("Open_File_Button"))
                    self.load_file_button.setText(_translate("Dialog", "...", None))
                    self.load_file_button.setToolTip("Open a file.")
                    print("Y PARAM: " + str(self.y_parameter))
                    self.load_file_button.clicked.connect(
                         lambda clicked, y_param=self.y_parameter: self.ui_action_open_file(y_param))
                    parameter_GridLayout.addWidget(self.load_file_button, self.y_parameter, 3, 1, 1)
            # ----------------------------------------------------
            # Description component, optionally with default value
            # ----------------------------------------------------
            # If we are not working with a file opening text option add labels to the right
            if parameter_fileSelectorType == "":
                parameter_desc_Label = QtWidgets.QLabel(parameter_Frame)
                parameter_desc_Label.setObjectName("Command_Parameter_Description_Label")
                parameter_desc = ""
                if parameter_required:
                    parameter_desc += "Required"
                if parameter_description != "":
                    if parameter_desc != "":
                        parameter_desc += " - "
                    parameter_desc += parameter_description
                if parameter_defaultValue != "":
                    if parameter_desc != "":
                        parameter_desc += " - "
                    parameter_desc = parameter_desc + " (default=" + parameter_defaultValue + ")"
                parameter_desc_Label.setText(parameter_desc)
                # parameter_desc_Label.setAlignment(QtCore.Qt.AlignLeft) # |QtCore.Qt.AlignCenter)
                parameter_GridLayout.addWidget(parameter_desc_Label, self.y_parameter, 4, 1, 1)

    def refresh_command(self):
        """
        Update the command string.

        Returns:  None
        """

        # Loop through the command parameter metadata and retrieve the values from editor components
        try:
            y_parameter = -1
            # Initial part of command string
            command_string = self.command.command_name + "("
            # Add all parameters to the command string
            for command_parameter_metadata in self.command.command_parameter_metadata:
                # Parameters listed in logical order
                y_parameter = y_parameter + 1
                if y_parameter == 0:
                    sep = ""
                else:
                    sep = ","
                parameter_name = command_parameter_metadata.parameter_name
                try:
                    parameter_value = self.parameter_LineEdit[y_parameter].text()
                except:
                    parameter_value = self.drop_down_menu[y_parameter].itemText(
                        self.drop_down_menu[y_parameter].currentIndex())
                if parameter_value is not None and parameter_value != "":
                    command_string = command_string + sep + parameter_name + '="' + parameter_value + '"'
            command_string = command_string + ")"
            self.CommandDisplay_View_TextBrowser.setPlainText(command_string)
        except Exception as e:
            message="Error refreshing command from parameters"
            logger = logging.getLogger(__name__)
            logger.error(message, e, exc_info=True)
            qt_util.warning_message_box(message)

    def ui_action_open_file(self, y_parameter):
        """
        Open a command file. Each line of the command file is a separate item in the Command_List QList Widget.
        If the existing commands have not been saved, the user is prompted to ask if they should be saved.

        Args:
            filename (str):
                the absolute path to the command file to open, if blank prompt for the file and otherwise
                open the file

        Returns:
            None
        """

        print("inside ui_action_open_file")
        print("y_param: " + str(y_parameter))
        print(type(y_parameter))

        logger = logging.getLogger(__name__)
        self.opened_file = True

        # The "..." QPushButton has been selected, in which case the user is
        # browsing for a file. For now open users home folder.
        folder = self.app_session.get_user_folder()

        # A browser window will appear to allow the user to browse to the desired command file.
        # The absolute pathname of the command file is added to the cmd_filepath variable.
        filepath = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", folder)[0]
        if not filepath:
            return

        self.parameter_LineEdit[y_parameter].setText(filepath)

        # # Read the command file in GeoProcessor
        # # GeoProcessor should handle necessary event handling and notify
        # # the GeoProessorListModel to update the User Interface
        # try:
        #     self.gp.read_command_file(cmd_filepath)
        # except FileNotFoundError as e:
        #     # The file should exist but may have been deleted outside of the UI
        #     message = 'Selected command file does not exist (maybe deleted or renamed?):\n"' + cmd_filepath + '"'
        #     logger.warning(message, e, exc_info=True)
        #     qt_util.warning_message_box(message)
        #     # Return so history is not changed to include a file that does not exist
        #     return

        # Push new command onto history
        # self.app_session.push_history(cmd_filepath)

        # Set this file path as the path to save if the user click "Save Commands ..."
        # self.saved_file = cmd_filepath

        # Set the title for the main window
        # self.ui_set_main_window_title('"' + cmd_filepath + '"')

        # Update recently opened files in file menu
        # self.ui_init_file_open_recent_files()

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

    def view_documentation(self):
        """
        Opens the command's user documentation in the default browser.

        Return: None
        """

        # The url of the command's user documentation.
        command_doc_url = "{}command-ref/{}/{}/".format(self.user_doc_url, self.command_name, self.command_name)

        # Open the command's user documentation in the default browser.
        webbrowser.open_new(command_doc_url)

    @staticmethod
    def select_file(qt_widget):
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
