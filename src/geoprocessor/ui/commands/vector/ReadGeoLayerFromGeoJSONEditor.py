# ReadGeoLayerFromGeoJSON_Editor - editor for ReadGeoLayerFromGeoJSON command
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

from PyQt5 import QtGui, QtWidgets

from geoprocessor.commands.vector.ReadGeoLayerFromGeoJSON import ReadGeoLayerFromGeoJSON
from geoprocessor.ui.commands.abstract.AbstractCommandEditor import AbstractCommandEditor
from geoprocessor.ui.util.CommandParameter import CommandParameter
from geoprocessor.core import CommandParameterMetadata

try:
    fromUtf8 = lambda s: s
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


class ReadGeoLayerFromGeoJSON_Editor(AbstractCommandEditor):

    # CLASS VARIABLES: static across all classes

    # The GeoProcessor ReadGeoLayerFromGeoJSON object.
    command_obj = ReadGeoLayerFromGeoJSON()

    # The name of the command. Read from the GeoProcessor command object.
    command_name = command_obj.command_name

    # A list of the command parameters. Read from the GeoProcessor command object.
    command_parameters = CommandParameterMetadata.get_parameter_names(command_obj.command_parameter_metadata)

    # A brief description of the command. This is displayed in the UI dialog box at the top to give the user context.
    command_description = "The ReadGeoLayerFromGeoJSON command reads a GeoLayer from a .geojson file. \n\n Specify " \
                          "the GeoJSON file to read into the GeoProcessor."

    # The number of parameters within the command. Indirectly, read from the GeoProcessor command object.
    parameter_count = len(command_parameters)

    # UI label objects are to be assigned within the setupUI function
    # These label objects are non-changing and are present in each ReadGeoLayerFromGeoJSON dialog box.
    #   I: labels the InputFile input text field. Note that the InputFile parameter
    #   does not need a description label object because the parameter description is written in the text field as
    #   placeholder text.
    #   GeoLayerID_Label: labels the GeoLayerID inpubst text field
    #   GeoLayerID_Description_Label: describes the GeoLayerID parameter
    #   IfGeoLayerIDExists_Label: labels the IfGeoLayerIDExists input text field
    #   IfGeoLayerIDExists_Description_Label: describes the IfGeoLayerIDExists parameter
    InputFile_Label = None
    GeoLayerID_Label = None
    GeoLayerID_Description_Label = None
    IfGeoLayerIDExists_Label = None
    IfGeoLayerIDExists_Description_Label = None

    # Command parameter descriptions for the InputFile parameter.
    cp_InputFile = CommandParameter(name="InputFile",
                                          description="absolute or relative path to the input GeoJSON file",
                                          optional=False,
                                          tooltip="The GeoJSON file to read (relative or absolute path).\n${Property} "
                                                  "syntax is recognized.",
                                          default_value_description=None)

    # Command parameter descriptions for the GeoLayerID parameter.
    cp_GeoLayerID = CommandParameter(name="GeoLayerID",
                                     description="GeoLayer identifier",
                                     optional=True,
                                     tooltip="A GeoLayer identifier.\n Formatting characters and ${Property} syntax "
                                             "are recognized.",
                                     default_value_description="filename of the input input data file")

    # Command parameter descriptions for the IfGeoLayerIDExists parameter.
    cp_IfGeoLayerIDExists = CommandParameter(name="IfGeoLayerIDExists",
                                             description="action that occurs if GeoLayer ID is not unique",
                                             optional=True,
                                             tooltip="The action that occurs if the GeoLayerID already exists "
                                                     "within the GeoProcessor. \n\nReplace: The existing GeoLayer "
                                                     "within the GeoProcessor is overwritten with the new GeoLayer. "
                                                     "No warning is logged.\n\nReplaceAndWarn: The existing GeoLayer "
                                                     "within the GeoProcessor is overwritten with the new GeoLayer. A "
                                                     "warning is logged. \n\nWarn: The new GeoLayer is not created. "
                                                     "A warning is logged. \n\nFail: The new GeoLayer is not created. "
                                                     "A fail message is logged.",
                                             default_value_description="Replace")

    # "ui_commandparameters" is a list of the CommandParameter objects (UI-specific class).
    ui_commandparameters = [cp_InputFile, cp_GeoLayerID, cp_IfGeoLayerIDExists]

    def __init__(self, command: ReadGeoLayerFromGeoJSON) -> None:
        """
        Initialize the ReadGeoLayerFromGeoJSON dialog box.
        Assign the INSTANCE VARIABLES: values specific to each instance.
        """
        super().__init__(command)

        # Command_parameter_values is a dictionary that holds the entered command parameter values.
        # Key: the name of the command parameter
        # Value: the entered value of the command parameter
        self.command_parameter_values = {}

        # Add all of the command parameters to the command_parameter_values dictionary. By default, set all
        # parameter values to an empty string. The values are populated later as the user enters text in the dialog box.
        # # for command_parameter_name in UiDialog.command_parameters:
        # #     self.command_parameter_values[command_parameter_name] = ""

        # UI input field objects are to be assigned within the setupUI function
        # The values of these input field objects are dynamic and unique to the instance. They are, however, all
        # present in each ReadGeoLayerFromGeoJSON dialog box.
        #   InputFile_LineEdit: the input field (PyQt5 LineEdit obj) for the InputFile parameter
        #   InputFile_ToolButton: the button (PyQt5 ToolButton obj) to select a file for the InputFile
        #   parameter
        #   GeoLayerID_LineEdit: the input field (PyQt5 LineEdit obj) for the GeoLayerID parameter
        #   IfGeoLayerIDExists_ComboBox: the input field (PyQt5 ComboBox obj) for the IfGeoLayerIDExists parameter
        self.InputFile_LineEdit = None
        self.InputFile_ToolButton = None
        self.GeoLayerID_LineEdit = None
        self.IfGeoLayerIDExists_ComboBox = None

        # Initialize the parent Abstract Dialog class.
        # # UI_AbstractDialog.__init__(self, UiDialog.command_name, UiDialog.command_description,
        # #                            UiDialog.parameter_count,
        # #                            UiDialog.command_parameters, self.command_parameter_values)

    def setup_ui(self) -> None:
        pass

    def setup_ui(self, Dialog: QtGui.QDialog) -> None:
        """
        # Configure the Dialog window with the features that are consistent across all GeoProcessor command dialog
        # windows.
        self.setupUi_Abstract(Dialog)

        # InputFile
        # Initialize a Qt QLabel object for the InputFile label.
        UiDialog.InputFile_Label = QtWidgets.QLabel(Dialog)

        # Configure the label to display the parameter name and align with the left side of the dialog window.
        self.configureLabel(UiDialog.InputFile_Label, UiDialog.cp_InputFile.name)

        # Initialize a Qt QLineEdit object for the InputFile input field.
        self.InputFile_LineEdit = QtWidgets.QLineEdit(Dialog)

        # Configure the input field to be extra long, display the placeholder description and include tooltip help.
        self.configureLineEdit(self.InputFile_LineEdit, UiDialog.cp_InputFile.name, long=True,
                               placeholder_text=UiDialog.cp_InputFile.description,
                               tooltip=UiDialog.cp_InputFile.tooltip)

        # Initialize a Qt QToolButton to open a browser to select a file for the InputFile parameter.
        self.InputFile_ToolButton = QtWidgets.QToolButton(Dialog)

        # Configure the button to link the selection to the InputFile_LineEdit input field.
        self.configureToolButton(self.InputFIle_ToolButton, UiDialog.cp_InputFile.name,
                                 self.InputFile_LineEdit)

        # GeoLayerID ##
        # Initialize a Qt QLabel object for the GeoLayerID label.
        UiDialog.GeoLayerID_Label = QtWidgets.QLabel(Dialog)

        # Configure the label to display the parameter name and align with the left side of the dialog window.
        self.configureLabel(UiDialog.GeoLayerID_Label, UiDialog.cp_GeoLayerID.name)

        # Initialize a Qt QLineEdit object for the GeoLayerID input field.
        self.GeoLayerID_LineEdit = QtWidgets.QLineEdit(Dialog)

        # Configure the input field to include tooltip help.
        self.configureLineEdit(self.GeoLayerID_LineEdit, UiDialog.cp_GeoLayerID.name,
                               tooltip=UiDialog.cp_GeoLayerID.tooltip)

        # Initialize a Qt QLabel object for the GeoLayerID description.
        UiDialog.GeoLayerID_Description_Label = QtWidgets.QLabel(Dialog)

        # Configure the label to display the GeoLayerID parameter description.
        self.configureDescriptionLabel(UiDialog.GeoLayerID_Description_Label, UiDialog.cp_GeoLayerID.name,
                                       UiDialog.cp_GeoLayerID.description)

        # IfGeoLayerIDExists ##
        # Initialize a Qt QLabel object for the IfGeoLayerIDExists label.
        UiDialog.IfGeoLayerIDExists_Label = QtWidgets.QLabel(Dialog)

        # Configure the label to display the parameter name and align with the left side of the dialog window.
        self.configureLabel(UiDialog.IfGeoLayerIDExists_Label, UiDialog.cp_IfGeoLayerIDExists.name)

        # Initialize a Qt QComboBox object for the IfGeoLayerIDExists input field.
        self.IfGeoLayerIDExists_ComboBox = QtWidgets.QComboBox(Dialog)

        # Configure the input combo box to be populated with the available choices for the IfGeoLayerIDExists parameter.
        self.configureComboBox(self.IfGeoLayerIDExists_ComboBox, UiDialog.cp_IfGeoLayerIDExists.name,
                               UiDialog.command_obj.choices_IfGeoLayerIDExists,
                               tooltip=UiDialog.cp_IfGeoLayerIDExists.tooltip)

        # Initialize a Qt QLabel object for the IfGeoLayerIDExists description.
        UiDialog.IfGeoLayerIDExists_Description_Label = QtWidgets.QLabel(Dialog)

        # Configure the label to display the IfGeoLayerIDExists parameter description.
        self.configureDescriptionLabel(UiDialog.IfGeoLayerIDExists_Description_Label,
                                       UiDialog.cp_IfGeoLayerIDExists.name,
                                       UiDialog.cp_IfGeoLayerIDExists.description)
        """

    def refresh(self) -> None:
        """
        This updates the dialog box with the previously defined parameter values when editing a command within the UI.
        """

        # Get the values of the previously-defined command dialog box. Assign to static variables before updating
        # the command dialog window. As the command dialog window is updated, the command_parameter_values
        # dictionary is altered.
        inputfile_value = self.command_parameter_values["InputFile"]
        geolayerid_value = self.command_parameter_values["GeoLayerID"]
        ifgeolayeridexists_value = self.command_parameter_values["IfGeoLayerIDExists"]

        # Set the text of the InputFile input field to the predefined value of the InputFile parameter.
        self.InputFile_LineEdit.setText(inputfile_value)

        # Set the text of the InputFile input field to the predefined value of the InputFile parameter.
        self.GeoLayerID_LineEdit.setText(geolayerid_value)

        # If the predefined IfGeoLayerIDExists parameter value is within one of the available options, the index of
        # the value in the ComboBox object is the index of the value in the options list plus one. The one accounts
        #  for the blank option that is available in the ComboBox but is not in the available options list.
        # # if ifgeolayeridexists_value in UiDialog.command_obj.choices_IfGeoLayerIDExists:
        # #     index = UiDialog.command_obj.choices_IfGeoLayerIDExists.index(ifgeolayeridexists_value) + 1

        # If the predefined IfGeoLayerIDExists parameter value is NOT within one of the available options, set the
        # index to the location of the blank option.
        # # else:
        # #     index = 0

        # Set the value of the IfGeoLayerIDExists combo box to the predefined value of the IfGeoLayerIDExists parameter.
        # Combo boxes are set by indexes rather than by text.
        # # self.IfGeoLayerIDExists_ComboBox.setCurrentIndex(index)
