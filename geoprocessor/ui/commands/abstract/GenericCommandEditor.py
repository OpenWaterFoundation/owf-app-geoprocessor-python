# GenericCommandEditor - default generic command editor
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

from geoprocessor.core import CommandParameterMetadata
from geoprocessor.ui.commands.abstract.AbstractCommandEditor import AbstractCommandEditor
from geoprocessor.ui.util.command_parameter import CommandParameter

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

        # Indicate if an error status is currently in effect, due to invalid parameters
        # - will be set in check_input() and is checked in ui_action_ok_clicked()
        self.error_wait = False

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

        # Setup the UI in the abstract class, which will call back to set_ui() in this class.
        self.setup_ui_core()

        # Initially call refresh in case updating a command
        self.refresh_command()

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

    # TODO smalers 2019-01-18 can this function be removed?
    def get_parameter_dict_from_ui(self):
        """
        Get the list of parameters from the UI, used to validate the parameters.

        Returns:
        """
        param_dict = dict()
        for parameter_LineEdit in self.parameter_LineEdit:
            param_name = parameter_LineEdit.getObjectName()
            param_value = parameter_LineEdit.getText()
            param_dict[param_name] = param_value

    def setup_ui(self):
        """
        Set up the dialog UI elements.  This generic editor provides text fields for each property.

        Returns:
            None
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
            self.parameter_LineEdit[parameter_name] = QtWidgets.QLineEdit(parameter_Frame)
            self.parameter_LineEdit[parameter_name].setObjectName(parameter_name)
            parameter_GridLayout.addWidget(self.parameter_LineEdit[parameter_name], y_parameter, 1, 1, 1)
            tooltip = command_parameter_metadata.editor_tooltip
            if tooltip is not None:
                self.parameter_LineEdit[parameter_name].setToolTip(tooltip)
            # Create a listener that reacts if the line edit field has been changed. If so, run the
            # update_command_display function.
            # If this command is being updated add the command parameters to the text fields
            if self.update:
                parameter_value = self.command.get_parameter_value(parameter_name)
                self.parameter_LineEdit[parameter_name].setText(parameter_value)
            self.parameter_LineEdit[parameter_name].textChanged.connect(self.refresh_command)
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

    # def setupUi(self, Dialog):
    #     """
    #     # Configure the Dialog window with the features that are consistent across all GeoProcessor command dialog
    #     # windows.
    #     self.setupUi_Abstract(Dialog)
    #
    #     # SpatialDataFile ##
    #     # Initialize a Qt QLabel object for the SpatialDataFile label.
    #     UiDialog.SpatialDataFile_Label = QtWidgets.QLabel(Dialog)
    #
    #     # Configure the label to display the parameter name and align with the left side of the dialog window.
    #     self.configureLabel(UiDialog.SpatialDataFile_Label, UiDialog.cp_SpatialDataFile.name)
    #
    #     # Initialize a Qt QLineEdit object for the SpatialDataFile input field.
    #     self.SpatialDataFile_LineEdit = QtWidgets.QLineEdit(Dialog)
    #
    #     # Configure the input field to be extra long, display the placeholder description and include tooltip help.
    #     self.configureLineEdit(self.SpatialDataFile_LineEdit, UiDialog.cp_SpatialDataFile.name, long=True,
    #                            placeholder_text=UiDialog.cp_SpatialDataFile.description,
    #                            tooltip=UiDialog.cp_SpatialDataFile.tooltip)
    #
    #     # Initialize a Qt QToolButton to open a browser to select a file for the SpatialDataFile parameter.
    #     self.SpatialDataFile_ToolButton = QtWidgets.QToolButton(Dialog)
    #
    #     # Configure the button to link the selection to the SpatialDataFile_LineEdit input field.
    #     self.configureToolButton(self.SpatialDataFile_ToolButton, UiDialog.cp_SpatialDataFile.name,
    #                              self.SpatialDataFile_LineEdit)
    #
    #     # GeoLayerID ##
    #     # Initialize a Qt QLabel object for the GeoLayerID label.
    #     UiDialog.GeoLayerID_Label = QtWidgets.QLabel(Dialog)
    #
    #     # Configure the label to display the parameter name and align with the left side of the dialog window.
    #     self.configureLabel(UiDialog.GeoLayerID_Label, UiDialog.cp_GeoLayerID.name)
    #
    #     # Initialize a Qt QLineEdit object for the GeoLayerID input field.
    #     self.GeoLayerID_LineEdit = QtWidgets.QLineEdit(Dialog)
    #
    #     # Configure the input field to include tooltip help.
    #     self.configureLineEdit(self.GeoLayerID_LineEdit, UiDialog.cp_GeoLayerID.name,
    #                            tooltip=UiDialog.cp_GeoLayerID.tooltip)
    #
    #     # Initialize a Qt QLabel object for the GeoLayerID description.
    #     UiDialog.GeoLayerID_Description_Label = QtWidgets.QLabel(Dialog)
    #
    #     # Configure the label to display the GeoLayerID parameter description.
    #     self.configureDescriptionLabel(UiDialog.GeoLayerID_Description_Label, UiDialog.cp_GeoLayerID.name,
    #                                    UiDialog.cp_GeoLayerID.description)
    #
    #     # IfGeoLayerIDExists ##
    #     # Initialize a Qt QLabel object for the IfGeoLayerIDExists label.
    #     UiDialog.IfGeoLayerIDExists_Label = QtWidgets.QLabel(Dialog)
    #
    #     # Initialize a Qt QComboBox object for the IfGeoLayerIDExists input field.
    #     self.IfGeoLayerIDExists_ComboBox = QtWidgets.QComboBox(Dialog)
    #
    #     # Configure the input combo box to be populated with the available choices for the
    #     # IfGeoLayerIDExists parameter.
    #     self.configureComboBox(self.IfGeoLayerIDExists_ComboBox, UiDialog.cp_IfGeoLayerIDExists.name,
    #                            UiDialog.command_obj.choices_IfGeoLayerIDExists,
    #                            tooltip=UiDialog.cp_IfGeoLayerIDExists.tooltip)
    #
    #     # Initialize a Qt QLabel object for the IfGeoLayerIDExists description.
    #     UiDialog.IfGeoLayerIDExists_Description_Label = QtWidgets.QLabel(Dialog)
    #
    #     # Configure the label to display the IfGeoLayerIDExists parameter description.
    #     self.configureDescriptionLabel(UiDialog.IfGeoLayerIDExists_Description_Label,
    #                                    UiDialog.cp_IfGeoLayerIDExists.name,
    #                                    UiDialog.cp_IfGeoLayerIDExists.description)
    #     """
    #     return

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
                parameter_value = self.parameter_LineEdit[parameter_name].text()
                if parameter_value is not None and parameter_value != "":
                    command_string = command_string + sep + parameter_name + '="' + parameter_value + '"'
            command_string = command_string + ")"
            self.CommandDisplay_View_TextBrowser.setPlainText(command_string)
        except Exception as e:
            message="Error refreshing command from parameters"
            logger = logging.getLogger(__name__)
            logger.error(message, e, exc_info=True)
            qt_util.warning_message_box(message)

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

