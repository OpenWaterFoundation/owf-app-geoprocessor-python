# SimpleCommandEditor - class for simple command editors
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

import geoprocessor.ui.util.qt_util as qt_util
import geoprocessor.util.io_util as io_util

import logging
import os


class SimpleCommandEditor(AbstractCommandEditor):
    """
    Class for command editor using single-panel layout configured with command parameter_input_metadata.
    """

    def __init__(self, command, app_session):
        """
        Initialize the Abstract Dialog instance.

        Args:
            command (AbstractCommand): a command object derived from AbstractCommand
            app_session (GeoProcessorAppSession): the application session, used to determine the user's home directory.
        """

        super().__init__(command)

        self.command = command

        # "command_name" is the name of the GeoProcessor command that the Dialog box is representing.
        # - TODO smalers 2019-01-19 why is this needed isntead of using the self.command.command_name?
        self.command_name = command.command_name

        # This is a session object to keep track of session variables such as command file history
        self.app_session = app_session

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

        # The QtWidgets.QFrame that is the UI element used to hold the parameter UI components
        # - instantiated in setup_ui()
        self.parameter_QFrame = None

        # The QtWidgets.QGridLayout manages the layout of self.parameter_QFrame
        # - instantiated in setup_ui()
        self.parameter_QGridLayout = None

        # The row position in the self.parameter_QGridLayout, used in setup_ui() and its helper functions.
        self.y_parameter = -1

        # "input_ui_components" is a dictionary that relates each command parameter with its associated Qt Widget
        # input field
        # KEY (str): the command parameter name
        # VALUE (obj): the associated Qt Widget input component
        self.input_ui_components = {}

        # Setup the UI in the AbstractCommandEditor class, which will call back to setup_ui() in this class.
        # - the AbstractCommandEditor populates some UI components such as the buttons at the bottom
        self.setup_ui_core()

        # Initially call refresh to the UI in case updating a command
        # - will transfer command parameter values into the UI components
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
            # Indicate that an error occurred so that calling code can handle
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
                    elif isinstance(parameter_ui, QtWidgets.QComboBox):
                        # TODO smalers 2019-01-19 does this aways return something?
                        # - in Java combo boxes have text value and list value and
                        index = parameter_ui.findText(parameter_value, QtCore.Qt.MatchFixedString)
                        if index >= 0:
                            parameter_ui.setCurrentIndex(index)
                        else:
                            message = "Unable to set parameter '" + parameter_name +\
                                      "' value to '" + str(parameter_value) + "' - specify a different value."
                            logger.warning(message)
                            qt_util.warning_message_box(message)
                    else:
                        # Should not happen
                        logger.warning("Unknown input component type '" + ui_type + "' for parameter '" +
                                       parameter_name + "' - code problem.")
                        continue
                except KeyError as e:
                    # Should not happen because all parameters should have at least a text field.
                    message = "No input component for parameter '" + parameter_name + "' - code problem."
                    logger.warning(message)
                    logger.error(message, e, exc_info=True)
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
                    elif isinstance(parameter_ui, QtWidgets.QComboBox):
                        # TODO smalers 2019-01-19 does this aways return something?
                        # - in Java combo boxes have text value and list value and
                        parameter_value = parameter_ui.currentText()
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
                    logger.warning(message)
                    logger.error(message, e, exc_info=True)
                    continue
            # Have a dictionary of parameters extracted from UI components
            # - format the command string using the command instance
            # - this does not change the command string in the command instance
            command_string = self.command.to_string(parameters_from_ui)
            self.CommandDisplay_View_TextBrowser.setPlainText(command_string)
        except Exception as e:
            message = "Error refreshing command from parameters"
            logger = logging.getLogger(__name__)
            logger.error(message, e, exc_info=True)
            qt_util.warning_message_box(message)

    def setup_ui(self):
        """
        Set up the dialog UI elements.  This simple editor provides standard input components such as
        text field (QLineEdit) and choices (QComboBox).

        Returns:
            None
        """

        logger = logging.getLogger(__name__)

        # The AbstractCommandEditor sets up the editor by:
        # 1. Initializes the dialog.
        # 2. Setting up standard editor top.
        # 3. Calls this method to set up command editor specifics, mainly the parameters.
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

        # Add input components for each parameter
        # - add in the order of the command_parameter_metdata
        # - details of the UI are determined from parameter_input_metadata
        self.y_parameter = -1
        for command_parameter_metadata in self.command.command_parameter_metadata:
            # Get the parameter name for retrieving all other parameter variables
            # - the command parameter_input_metadata dictionary contains UI configuration properties
            # - each dictionary key starts with `ParameterName.', for example 'LogFile.Label'
            parameter_name = command_parameter_metadata.parameter_name

            try:
                try:
                    input_metadata = self.command.parameter_input_metadata
                except AttributeError:
                    # It is likely tha the command class has not been updated to the latest design
                    # that uses parameter_input_metadata so create an empty dictionary.
                    # - all values will be defaulted below, possibly resulting in GenericCommandEditor being used
                    logger.info(parameter_name +
                                " does not have parameter_input_metadata defined.  Command '" +
                                self.command.command_name + " code needs to be updated.")
                    self.command.parameter_input_metadata = dict()

                # Get standard metadata values from parameter_input_metadata.
                # - alphabetize these and use metadata name spelled exactly to avoid confusion
                # - these are used to make decisions about which UI component to use
                # - other metadata values are retrieved as needed based on the UI component
                # - this allows metadata in commands to be minimally-specified
                # - default to values of None indicating that the metadata value was not specified, as opposed
                #   to "", which would indicate it is specified and is an empty string (e.g., for Value.Default)
                #   EXCEPT in cases where a better default than None can be assigned

                # Description
                request_key = parameter_name + "." + "Description"
                parameter_Description = None
                try:
                    parameter_Description = input_metadata[request_key]
                except KeyError:
                    # Default to a simple statement with parameter name.
                    logger.warning(parameter_name + " does not have parameter_input_metadata value " + request_key +
                                   ".  Defaulting to parameter name.")
                    parameter_Description = parameter_name

                # FileSelector.Type
                # - new is FileSelector.Type
                # - old is FileSelectorType
                request_key1 = parameter_name + "." + "FileSelector.Type"
                parameter_FileSelectorType = None
                try:
                    parameter_FileSelectorType = input_metadata[request_key1]
                except KeyError:
                    # Old...
                    request_key2 = parameter_name + "." + "FileSelectorType"
                    try:
                        parameter_FileSelectorType = input_metadata[request_key2]
                        logger.warning('Need to convert FileSelectorType to FileSelector.Type for command ' +
                                       self.command_name)
                    except KeyError:
                        # Default is None because file selector is only used for files
                        pass  # None was assigned above

                # Group
                request_key = parameter_name + "." + "Group"
                parameter_Group = None
                try:
                    parameter_Group = input_metadata[request_key]
                except KeyError:
                    # Group is only used for Tabbed editor type so it is optional in most cases
                    # - do need some logic somewhere that if Group is specified for one parameter,
                    #   it should probably be specified for all parameters
                    # - however, defaulting to the first group may make sense
                    pass  # None was assigned above

                # Label
                request_key = parameter_name + "." + "Label"
                parameter_Label = None
                try:
                    parameter_Label = input_metadata[request_key]
                except KeyError:
                    # Default to the parameter name, but warn so developers can set the label intelligently.
                    # - the default of parameter name is likely less friendly to the user so should always configure
                    #   in metadata
                    logger.warning(parameter_name + " does not have parameter_input_metadata value " + request_key +
                                   ".  Defaulting to parameter name.")
                    parameter_Label = parameter_name

                # Required
                request_key = parameter_name + "." + "Required"
                parameter_Required = None
                try:
                    parameter_Required = input_metadata[request_key]
                except KeyError:
                    # Default value is optional given that True is imposed as a special case
                    parameter_Required = False

                # Tooltip
                request_key = parameter_name + "." + "Tooltip"
                parameter_Tooltip = None
                try:
                    parameter_Tooltip = input_metadata[request_key]
                except KeyError:
                    # Default is an empty string
                    # - components should check for None or empty string and not set tooltip in this case
                    parameter_Tooltip = ""

                # Value.Default
                request_key = parameter_name + "." + "Value.Default"
                parameter_ValueDefault = None
                try:
                    parameter_ValueDefault = input_metadata[request_key]
                except KeyError:
                    # Default value is not required and and will be component-specific
                    # - for example, blank string for text field
                    # - for example, select first value in `Values` metadata
                    pass

                # Values
                request_key = parameter_name + "." + "Values"
                parameter_Values = None
                try:
                    parameter_Values = input_metadata[request_key]
                except KeyError:
                    # Default is that Values is not used.
                    # - it is only required for choices and can print more specific warnings below
                    # - None was set above
                    pass

            except Exception as e:
                # Don't continue with edit because there could be major confusion
                # - this should NEVER happen unless there is a code error because above logic is basic
                message = 'Error getting command editor metadata - cannot edit command.'
                logger.warning(message)
                logger.warning(message, e, exc_info=True)
                # Show the user a warning
                qt_util.warning_message_box(message)
                self.reject()

            # Parameters listed in logical order, from left to right

            # ---------------
            # Leftmost UI component, which is the label
            # ---------------
            # Label component, consistent for all input component types
            # ---------------
            self.setup_ui_parameter_label(parameter_name, parameter_Label)

            # ---------------
            # Next from the left is the primary input components
            # - one of the types can be used: combobox, file selector, text field
            # - metadata values determined above are checked to see which UI component should be used
            # ---------------
            if parameter_Values is not None and parameter_Values != "":
                # --------------------
                # Choice (Qt combobox) component
                # - indicated by 'Values' metadata
                # --------------------
                # Get the input metadata here and pass to the code that creates the UI.
                # - need Value.DefaultForDisplay, for example to display blank corresponding to Value.Default.
                # - need Values.Editable
                request_key = parameter_name + "." + "Value.DefaultForDisplay"
                parameter_ValueDefaultForDisplay = None
                try:
                    parameter_ValueDefaultForDisplay = input_metadata[request_key]
                except KeyError:
                    # Default value cannot be determined, even though often ""
                    # - handle in the combobox
                    pass
                request_key = parameter_name + "." + "Values.Editable"
                parameter_ValuesEditable = None
                try:
                    parameter_ValuesEditable = input_metadata[request_key]
                except KeyError:
                    # Default value is combo boxes are not editable
                    parameter_ValuesEditable = False
                self.setup_ui_parameter_combobox(parameter_name,
                                                 parameter_ValueDefaultForDisplay,
                                                 parameter_Tooltip,
                                                 parameter_Values,
                                                 parameter_ValuesEditable)
            elif parameter_FileSelectorType is not None and parameter_FileSelectorType != "":
                # --------------------
                # File selector
                # - indicated by `FileSelector.Type` metadata
                # - wide text field because file names can be long
                # - browse button to select the file
                # - no description because text field is otfen wide
                # --------------------
                self.setup_ui_parameter_file_selector(input_metadata, parameter_name, parameter_Tooltip)
            else:
                # --------------------
                # LineEdit (text field)
                # - default if properties don't indicate any other component
                # --------------------
                self.setup_ui_parameter_text_field(parameter_name, parameter_Tooltip)

            # ---------------
            # Next from the left is the parameter description components
            # - uses several properties to form the description
            # - is not used for file selector parameters because the file selector text field is wide
            # ----------------------------------------------------
            if parameter_FileSelectorType is None or parameter_FileSelectorType == "":
                self.setup_ui_parameter_description(parameter_name,
                                                    parameter_ValueDefault,
                                                    parameter_Description,
                                                    parameter_Required,
                                                    parameter_Tooltip)

            # Set column width for text entry fields
            self.parameter_QGridLayout.setColumnMinimumWidth(1, 350)

        if self.debug:
            logger.info("Successfully created UI components.  Entering edit/refresh mode.")

    def setup_ui_parameter_combobox(self, parameter_name,
                                    parameter_ValueDefaultForDisplay,
                                    parameter_Tooltip,
                                    parameter_Values,
                                    parameter_ValuesEditable):
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
        #     logger.error(message, e, exc_info=True)
        #     qt_util.warning_message_box(message)
        # ComboBox, indicated by 'Values' property
        debug = True
        if self.debug:
            logger = logging.getLogger(__name__)
            logger.info("For parameter '" + parameter_name + "', adding combobox")
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
        parameter_QComboBox.currentIndexChanged.connect(self.refresh_ui)
        if parameter_Tooltip is not None and parameter_Tooltip != "":
            parameter_QComboBox.setToolTip(parameter_Tooltip)
        # Set whether editable
        parameter_QComboBox.setEditable(parameter_ValuesEditable)
        self.parameter_QGridLayout.addWidget(parameter_QComboBox, self.y_parameter, 1, 1, 2)
        # Add the component to the list maintained to get values out of UI components
        self.input_ui_components[parameter_name] = parameter_QComboBox

    def setup_ui_parameter_description(self, parameter_name,
                                       parameter_ValueDefault,
                                       parameter_Description,
                                       parameter_Required,
                                       parameter_Tooltip):
        """
        Add description UI components for a command parameter.
        This is not done for file selector component.

        Args:
            parameter_name (str):  Parameter name, used for troubleshooting
            parameter_ValueDefault (str):  Parameter default value if not specified.
            parameter_Description (str):  Parameter description, before combining with other data here.
            parameter_Required (boolean):  Whether the parameter is required.
            parameter_Tooltip (str):  Tooltip text.

        Returns:
            None
        """
        # try:
        #     parameter_Required, parameter_Description, parameter_ValueDefault
        # except Exception as e:
        #     message = "Could not find necessary parameter metadata in command file for " + parameter_name + \
        #               ". Could not build simple command editor. Defaulting to generic command editor. " \
        #               "See log file for more details."
        #     logger.error(message, e, exc_info=True)
        #     qt_util.warning_message_box(message)
        debug = True
        if self.debug:
            logger = logging.getLogger(__name__)
            logger.info("For parameter '" + parameter_name + "', adding description")
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
        if parameter_ValueDefault is not None and parameter_ValueDefault != "":
            if len(parameter_ValueDefault) > 15:
                # Default value is long so don't show in full description and put in the input component toolip
                parameter_desc += " (default=see tooltip)"
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
            parameter_desc += " (default=None)."
        parameter_desc_Label.setText(parameter_desc)
        # parameter_desc_Label.setAlignment(QtCore.Qt.AlignLeft) # |QtCore.Qt.AlignCenter)
        self.parameter_QGridLayout.addWidget(parameter_desc_Label, self.y_parameter, 6, 1, 1)

    def setup_ui_parameter_file_selector(self, input_metadata, parameter_name, parameter_Tooltip):
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
        parameter_select_file_QPushButton = QtWidgets.QPushButton(self.parameter_QFrame)
        # Object name has parameter at front, which can be parsed out in event-handling code
        # - IMPORTANT - don't change the object name without changing elsewhere
        parameter_select_file_QPushButton.setObjectName(qt_util.from_utf8(parameter_name + ".FileSelector.Button"))
        parameter_select_file_QPushButton.setText(qt_util.translate("Dialog", "...", None))
        if file_selector_button_tooltip != "":
            parameter_select_file_QPushButton.setToolTip(file_selector_button_tooltip)
        parameter_select_file_QPushButton.setMaximumWidth(50)
        parameter_select_file_QPushButton.clicked.connect(
            lambda clicked, y_param=self.y_parameter: self.ui_action_select_file(y_param,
                                                                                 parameter_select_file_QPushButton))
        self.parameter_QGridLayout.addWidget(parameter_select_file_QPushButton, self.y_parameter, 6, 1, 1)

    def setup_ui_parameter_label(self, parameter_name, parameter_Label):
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
        #     logger.error(message, e, exc_info=True)
        #     qt_util.warning_message_box(message)
        debug = True
        if self.debug:
            logger = logging.getLogger(__name__)
            logger.info("For parameter '" + parameter_name + "', adding label")
        # Increment the y-position in the GridLayout since starting a new row in the UI
        self.y_parameter = self.y_parameter + 1
        parameter_QLabel = QtWidgets.QLabel(self.parameter_QFrame)
        parameter_QLabel.setObjectName("Command_Parameter_Label")
        parameter_QLabel.setText(parameter_Label + ":")
        parameter_QLabel.setAlignment(QtCore.Qt.AlignRight)  # |QtCore.Qt.AlignCenter)
        # Allow expanding horizontally
        parameter_QLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Fixed)
        self.parameter_QGridLayout.addWidget(parameter_QLabel, self.y_parameter, 0, 1, 1)
        self.parameter_QGridLayout.setColumnStretch(0,0)

    def setup_ui_parameter_text_field(self, parameter_name, parameter_Tooltip):
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
        parameter_QLineEdit.textChanged.connect(self.refresh_ui)
        # Add the component to the list maintained to get values out of UI components
        self.input_ui_components[parameter_name] = parameter_QLineEdit

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
            # User was shown a warning dialog and had to acknowledge it, so here just ignore the "OK"
            # - errors in input parameters need to be fixed before OK works
            pass
        else:
            # No error so OK to exit
            # - call the standard accept() function to set the return value
            self.accept()

    def ui_action_select_file(self, y_parameter, event_button):
        """
        Open a file selector dialog to select an input or output file (or folder) to be used as a command
        parameter value.

        Args:
            y_parameter (int): the y-position in layout for the button, used to access components.
            TODO smalers 2019-01-18 need to move to dictionary of components.
            event_button (QPushButton): the instance of the button for which the event is generated.
            Use to get the parameter name, so as to get other parameter/component data.

        Returns:
            None
        """

        logger = logging.getLogger(__name__)

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
            select_folder = self.command.parameter_input_metadata[request_key]
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
            select_file_title = self.command.parameter_input_metadata[request_key]
        except KeyError:
            # Default was specified above...
            pass

        # Get the existing value in the text field, which will correspond to the parameter name value.
        # - if specified as absolute path, use it as is
        # - if a relative path, append to the working directory or if that is not available the user's home folder
        parameter_QLineEdit = None
        working_dir = self.command.command_processor.get_property('WorkingDir')
        user_folder = self.app_session.get_user_folder()
        try:
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
