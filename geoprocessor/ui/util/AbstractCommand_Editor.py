from PyQt5 import QtCore, QtWidgets
import webbrowser
import geoprocessor.ui.util.config as config
import functools

try:
    # _fromUtf8 = QtCore.QString.fromUtf8
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

class UI_AbstractDialog(object):

    def __init__(self, command_name, command_description, command_count, command_parameters, current_values):

        self.command_name = command_name
        self.command_description = command_description
        self.user_doc_url = config.user_doc_url
        self.command_count = command_count
        self.parameters_list = command_parameters
        self.input_edit_objects = {}
        self.command_parameter_current_values = current_values

    def setupUi_Abstract(self, Dialog):
        """
        Sets up a Dialog object with the features that are common across all GeoProcessor command dialog windows.

        Arg:
            Dialog: a QDialog window instance (QtGui.QDialog())

        Return: None
        """

        # Set the name, the initial size and the window title (the name of the command) of the Dialog window object.
        # The Dialog window object, Dialog, represents the entire dialog window.
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(684, 404)
        Dialog.setWindowTitle(_translate("Dialog", self.command_name, None))

        # Create a grid layout object. Apply the grid layout to the Dialog window object.
        # Set the name of the grid layout object.
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))

        # Create a frame object. Add the frame object to the Dialog window.
        # Set the shape, the shadow, and the name of the frame object.
        # The frame object, Command_Description, holds the command description and the view documentation button.
        self.Command_Description = QtWidgets.QFrame(Dialog)
        self.Command_Description.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Command_Description.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Command_Description.setObjectName(_fromUtf8("Command_Description"))
        self.gridLayout.addWidget(self.Command_Description, 0, 0, 1, 8)

        # Create a grid layout object. Apply to the Command_Description frame object.
        # Set the name of the grid layout object.
        self.gridLayout_2 = QtWidgets.QGridLayout(self.Command_Description)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))

        # Create a spacer. Add the spacer to the Command_Description frame object.
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 2, 0, 1, 1)

        # Create a push button. Add the button to the Command_Description frame object.
        # Set the name, the button text and the connection of the push button.
        # The push button, View_Documentation_Button, displays the command's online user documentation when clicked.
        self.View_Documentation_Button = QtWidgets.QPushButton(self.Command_Description)
        self.View_Documentation_Button.setObjectName(_fromUtf8("View_Documentation_Button"))
        self.View_Documentation_Button.setText(_translate("Dialog", "  View Documentation  ", None))
        self.View_Documentation_Button.clicked.connect(self.view_documentation)
        self.gridLayout_2.addWidget(self.View_Documentation_Button, 2, 1, 1, 1)

        # Create a label. Add the label to the Command_Description frame object.
        # Set the name and the text of the label.
        # The label, Command_Description_Label, briefly describes the command.
        self.Command_Description_Label = QtWidgets.QLabel(self.Command_Description)
        self.Command_Description_Label.setObjectName(_fromUtf8("Command_Description_Label"))
        self.Command_Description_Label.setText(_translate("Dialog", self.command_description, None))
        self.gridLayout_2.addWidget(self.Command_Description_Label, 0, 0, 1, 2)

        # Create a line (frame object with special specifications). Add the line to the Dialog window.
        # Set the size policy, the shape, the shadow, and the name of the frame object to create the line separator.
        # The frame object, Separator, separates the command description from the input form section of the Dialog box.
        self.Separator = QtWidgets.QFrame(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Separator.sizePolicy().hasHeightForWidth())
        self.Separator.setSizePolicy(sizePolicy)
        self.Separator.setFrameShape(QtWidgets.QFrame.HLine)
        self.Separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.Separator.setObjectName(_fromUtf8("Separator"))
        self.gridLayout.addWidget(self.Separator, 1, 0, 1, 8)

        # Create a button box object. Add the button box object to the Dialog window.
        # Set the orientation, the standard buttons, the name and the connections of the button box object.
        # The button box object, OK_Cancel_Buttons, allow the user to accept or reject the changes made in the dialog.
        self.OK_Cancel_Buttons = QtWidgets.QDialogButtonBox(Dialog)
        self.OK_Cancel_Buttons.setOrientation(QtCore.Qt.Horizontal)
        self.OK_Cancel_Buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.OK_Cancel_Buttons.setObjectName(_fromUtf8("OK_Cancel_Buttons"))
        self.OK_Cancel_Buttons.accepted.connect(Dialog.accept)
        self.OK_Cancel_Buttons.rejected.connect(Dialog.reject)
        self.gridLayout.addWidget(self.OK_Cancel_Buttons, self.command_count + 4, 6, 1, 2)

        # Create a text edit object. Add the text edit object to the Dialog window.
        # Set the size, the name and the html of the text edit object.
        # The text edit object, CommandDisplay_View_TextBrowser, displays a dynamic view of the command string.
        self.CommandDisplay_View_TextBrowser = QtWidgets.QTextEdit(Dialog)
        self.CommandDisplay_View_TextBrowser.setMinimumSize(QtCore.QSize(0, 100))
        self.CommandDisplay_View_TextBrowser.setMaximumSize(QtCore.QSize(16777215, 100))
        self.CommandDisplay_View_TextBrowser.setObjectName(_fromUtf8("CommandDisplay_View_TextBrowser"))
        html = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">" \
               "\n<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\np, li { " \
               "white-space: pre-wrap; }\n</style></head><body style=\" font-family:\'MS Shell Dlg 2\';" \
               " font-size:8.25pt; font-weight:400; font-style:normal;\">\n<p style=\" margin-top:0px;" \
               " margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">" \
               "<span style=\" font-size:8pt;\">ReadGeoLayerFromGeoJSON()</span></p></body></html>"
        self.CommandDisplay_View_TextBrowser.setHtml(_translate("Dialog", html, None))
        self.gridLayout.addWidget(self.CommandDisplay_View_TextBrowser, self.command_count + 3, 1, 1, -1)

        # Create a label object to the Dialog window.
        # Set the alignment, the name, and the text of the label.
        # The label, Command Display_Label, labels the CommandDisplay_View_TextBrowser text edit object.
        self.CommandDisplay_Label = QtWidgets.QLabel(Dialog)
        self.CommandDisplay_Label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.CommandDisplay_Label.setObjectName(_fromUtf8("CommandDisplay_Label"))
        self.CommandDisplay_Label.setText(_translate("Dialog", "Command: ", None))
        self.gridLayout.addWidget(self.CommandDisplay_Label, self.command_count + 3, 0, 1, 1)

        # Create a spacer. Add the spacer to the Dialog window.
        # The spacer separates the input parameter value fields from the Command Display text browser.
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, self.command_count + 2, 3, 1, -1)

        # This will wire up the signals and slots depending on names.
        # REF: http://joat-programmer.blogspot.com/2012/02/pyqt-signal-and-slots-to-capture-events.html
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def view_documentation(self):
        """
        Opens the command's user documentation in the default browser.

        Return: None
        """

        # The url of the command's user documentation.
        command_doc_url = "{}command-ref/{}/{}/".format(self.user_doc_url, self.command_name, self.command_name)

        # Open the command's user documentation in the default browser.
        webbrowser.open_new(command_doc_url)

    def configureLabel(self, label, parameter_name):
        """
        Configure a QtGui.QLabel object that meets the standards of the GeoProceossor's command dialog window.

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
        # and will occupy 1 row and 1 column.
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

        Return: None
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

    def configureDescriptionLabel(self, label_object, parameter_name, text):

        row_index = self.parameters_list.index(parameter_name) + 2
        label_object.setObjectName(_fromUtf8("{}_Description_Label".format(parameter_name)))
        self.gridLayout.addWidget(label_object, row_index, 5, 1, 3)
        label_object.setText(_translate("Dialog", text, None))

    def configureComboBox(self, combobox_object, parameter_name, choice_list, tooltip=None):

        row_index = self.parameters_list.index(parameter_name) + 2
        combobox_object.setObjectName(_fromUtf8("{}_ComboBox".format(parameter_name)))
        for i in range(len(choice_list) + 1):
            combobox_object.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(combobox_object, row_index, 1, 1, 2)

        combobox_object.setItemText(0, _fromUtf8(""))
        for i in range(len(choice_list)):
            combobox_object.setItemText(i+1, _translate("Dialog", choice_list[i], None))

        if tooltip:
            combobox_object.setToolTip(_translate("Dialog", tooltip, None))

        self.input_edit_objects[parameter_name] = combobox_object
        combobox_object.currentIndexChanged.connect(self.update_command_display)

    def get_current_value(self, obj):

        try:
            value =  obj.text()
        except:
            value = obj.currentText()

        return value

    def update_command_display(self):

        for command in self.parameters_list:
            ui_obj = self.input_edit_objects[command]
            value = self.get_current_value(ui_obj)
            self.command_parameter_current_values[command] = value

        if self.command_parameter_current_values.values().count("") == len(self.command_parameter_current_values):

            display = "{}()".format(self.command_name)

        else:

            parameter_string_text = ""
            for command_parameter in self.parameters_list:
                value = self.command_parameter_current_values[command_parameter]
                if value != "":
                    text = '{}="{}", '.format(command_parameter, value)
                    parameter_string_text += text

            updated_parameter_string_text = parameter_string_text.rsplit(", ", 1)[0]

            display = "{}({})".format(self.command_name, updated_parameter_string_text)

        self.CommandDisplay_View_TextBrowser.setText(display)

    def create_full_description(self, brief_description, default_value=None, optional=False):

        if optional:
            requirements = "Optional"
        else:
            requirements = "Required"

        if default_value:

            full_description = "{} - {}\n(default: {})".format(requirements, brief_description, default_value)

        else:

            full_description = "{} - {}".format(requirements, brief_description)

        return full_description

    def select_file(self, affected_object):

        affected_object.setText(QtWidgets.QFileDialog.getOpenFileName())
