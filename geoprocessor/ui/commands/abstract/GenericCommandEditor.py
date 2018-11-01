from PyQt5 import QtCore, QtGui, QtWidgets

from geoprocessor.ui.commands.abstract.AbstractCommandEditor import AbstractCommandEditor
from geoprocessor.ui.util.command_parameter import CommandParameter
import geoprocessor.ui.util.qt_util as qt_util
from geoprocessor.core import CommandParameterMetadata

import logging

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


class GenericCommandEditor(AbstractCommandEditor):
    """
    Command editor with general interface, which will provide text fields for each property.
    """

    def __init__(self, command):
        """
        Create the generic command editor dialog box, used to edit commands that don't have a specific editor.
        """
        # Initialize the parent abstract editor
        # - this will do basic setup of the dialog
        super().__init__(command)

        # Array of text fields (Qt LineEdit) containing parameter values, with object name matching parameter name
        self.parameter_LineEdit = [None]*len(self.command.command_parameter_metadata)

        # Setup the UI in the abstract class, which will call back to set_ui() in this class.
        self.setup_ui_core()

    def get_parameter_dict_from_ui(self):
        """
        Get the list of parameters from the UI, used to validate the parameters.

        Returns:
        """
        param_dict = {}
        for parameter_LineEdit in self.parameter_LineEdit:
            param_name = parameter_LineEdit.getObjectName()
            param_value = parameter_LineEdit.getText()
            param_dict[param_name] = param_value

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
        y_parameter = -1
        for command_parameter_metadata in self.command.command_parameter_metadata:
            # Parameters listed in logical order
            y_parameter = y_parameter + 1
            # ---------------
            # Label component
            # ---------------
            parameter_name = command_parameter_metadata.parameter_name
            parameter_Label = QtWidgets.QLabel(parameter_Frame)
            parameter_Label.setObjectName("Command_Parameter_Label")
            parameter_Label.setText(parameter_name + ":")
            parameter_Label.setAlignment(QtCore.Qt.AlignRight) # |QtCore.Qt.AlignCenter)
            # Allow expanding horizontally
            parameter_Label.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)
            parameter_GridLayout.addWidget(parameter_Label, y_parameter, 0, 1, 1)
            # --------------------
            # Text entry component
            # --------------------
            self.parameter_LineEdit[y_parameter] = QtWidgets.QLineEdit(parameter_Frame)
            self.parameter_LineEdit[y_parameter].setObjectName(parameter_name)
            parameter_GridLayout.addWidget(self.parameter_LineEdit[y_parameter], y_parameter, 1, 2, 1)
            tooltip = command_parameter_metadata.editor_tooltip
            if tooltip is not None:
                self.parameter_LineEdit[y_parameter].setToolTip(tooltip)
            # Create a listener that reacts if the line edit field has been changed. If so, run the
            # update_command_display function.
            self.parameter_LineEdit[y_parameter].textChanged.connect(self.refresh_command)
            # ----------------------------------------------------
            # Description component, optionally with default value
            # ----------------------------------------------------
            parameter_description = command_parameter_metadata.parameter_description
            parameter_desc_Label = QtWidgets.QLabel(parameter_Frame)
            parameter_desc_Label.setObjectName("Command_Parameter_Description_Label")
            parameter_desc = command_parameter_metadata.parameter_description
            if parameter_desc is None:
                parameter_desc = ""
            default_value = command_parameter_metadata.default_value
            if default_value is not None:
                parameter_desc = parameter_desc + " (default=" + default_value + ")"
            parameter_desc_Label.setText(parameter_desc)
            parameter_desc_Label.setAlignment(QtCore.Qt.AlignLeft) # |QtCore.Qt.AlignCenter)
            parameter_GridLayout.addWidget(parameter_desc_Label, y_parameter, 3, 4, 1)

    def setupUi(self, Dialog):
        """
        # Configure the Dialog window with the features that are consistent across all GeoProcessor command dialog
        # windows.
        self.setupUi_Abstract(Dialog)

        # SpatialDataFile ##
        # Initialize a Qt QLabel object for the SpatialDataFile label.
        UiDialog.SpatialDataFile_Label = QtWidgets.QLabel(Dialog)

        # Configure the label to display the parameter name and align with the left side of the dialog window.
        self.configureLabel(UiDialog.SpatialDataFile_Label, UiDialog.cp_SpatialDataFile.name)

        # Initialize a Qt QLineEdit object for the SpatialDataFile input field.
        self.SpatialDataFile_LineEdit = QtWidgets.QLineEdit(Dialog)

        # Configure the input field to be extra long, display the placeholder description and include tooltip help.
        self.configureLineEdit(self.SpatialDataFile_LineEdit, UiDialog.cp_SpatialDataFile.name, long=True,
                               placeholder_text=UiDialog.cp_SpatialDataFile.description,
                               tooltip=UiDialog.cp_SpatialDataFile.tooltip)

        # Initialize a Qt QToolButton to open a browser to select a file for the SpatialDataFile parameter.
        self.SpatialDataFile_ToolButton = QtWidgets.QToolButton(Dialog)

        # Configure the button to link the selection to the SpatialDataFile_LineEdit input field.
        self.configureToolButton(self.SpatialDataFile_ToolButton, UiDialog.cp_SpatialDataFile.name,
                                 self.SpatialDataFile_LineEdit)

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
        return

    def refresh(self):
        """
        This updates the dialog box with the previously defined parameter values when editing a command within the UI.
        """

        # Get the values of the previously-defined command dialog box. Assign to static variables before updating
        # the command dialog window. As the command dialog window is updated, the command_parameter_values
        # dictionary is altered.
        spatialdatafile_value = self.command_parameter_values["SpatialDataFile"]
        geolayerid_value = self.command_parameter_values["GeoLayerID"]
        ifgeolayeridexists_value = self.command_parameter_values["IfGeoLayerIDExists"]

        # Set the text of the SpatialDataFile input field to the predefined value of the SpatialDataFile parameter.
        self.SpatialDataFile_LineEdit.setText(spatialdatafile_value)

        # Set the text of the SpatialDataFile input field to the predefined value of the SpatialDataFile parameter.
        self.GeoLayerID_LineEdit.setText(geolayerid_value)

        # If the predefined IfGeoLayerIDExists parameter value is within one of the available options, the index of
        # the value in the ComboBox object is the index of the value in the options list plus one. The one accounts
        #  for the blank option that is available in the ComboBox but is not in the available options list.
        ## if ifgeolayeridexists_value in UiDialog.command_obj.choices_IfGeoLayerIDExists:
            ## index = UiDialog.command_obj.choices_IfGeoLayerIDExists.index(ifgeolayeridexists_value) + 1

        # If the predefined IfGeoLayerIDExists parameter value is NOT within one of the available options, set the
        # index to the location of the blank option.
        ## else:
            ## index = 0

        # Set the value of the IfGeoLayerIDExists combo box to the predefined value of the IfGeoLayerIDExists parameter.
        # Combo boxes are set by indexes rather than by text.
        ## self.IfGeoLayerIDExists_ComboBox.setCurrentIndex(index)

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
                parameter_value = self.parameter_LineEdit[y_parameter].text()
                if parameter_value is not None and parameter_value != "":
                    command_string = command_string + sep + parameter_name + '="' + parameter_value + '"'
            command_string = command_string + ")"
            self.CommandDisplay_View_TextBrowser.setPlainText(command_string)
        except Exception as e:
            message="Error refreshing command from parameters"
            logger = logging.getLogger(__name__)
            logger.error(message, e, exc_info=True)
            qt_util.warning_message_box(message)