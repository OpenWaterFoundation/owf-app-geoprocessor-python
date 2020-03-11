# SimpleCommandEditor - class for simple command editors
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

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from geoprocessor.app.GeoProcessorAppSession import GeoProcessorAppSession
from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand
from geoprocessor.ui.commands.abstract.AbstractCommandEditor import AbstractCommandEditor

import geoprocessor.ui.util.qt_util as qt_util
# import geoprocessor.util.io_util as io_util

import logging
# import os


class SimpleCommandEditor(AbstractCommandEditor):
    """
    Class for command editor using simple single-panel layout configured with command parameter_input_metadata.

    This editor is used by most commands.
    """

    def __init__(self, command: AbstractCommand, app_session: GeoProcessorAppSession) -> None:
        """
        Initialize the Abstract Dialog instance.

        Args:
            command (AbstractCommand): a command object derived from AbstractCommand
            app_session (GeoProcessorAppSession): the application session, used to determine the user's home directory.
        """

        # The following will initialize shared components
        super().__init__(command)

        # TODO smalers 2020-01-16 why is this needed here?  Does not seem to be used.
        # This is a session object to keep track of session variables such as command file history
        self.app_session = app_session

        # NOT defined in AbstractCommandEditor - local to this class
        # Turn localized debug on/off, useful for development
        # - should be False for production release
        # - this causes logger.info messages to be printed
        # - later can convert to logger.debug if still needed
        self.debug = False

        # NOT defined in AbstractCommandEditor - local to this class
        # Indicate if an error status is currently in effect, due to invalid parameters
        # - will be set in check_input() and is checked in ui_action_ok_clicked()
        self.error_wait = False

        # NOT defined in AbstractCommandEditor - local to this class
        # Indicate whether first time refresh_ui is called
        # - the first time the UI components may be initialized from data
        self.first_refresh_ui = True

        # Defined in AbstractCommandEditor
        # The QtWidgets.QFrame that is the UI element used to hold the parameter UI components
        # - instantiated in setup_ui()
        # self.parameter_QFrame = None

        # Defined in AbstractCommandEditor
        # The QtWidgets.QGridLayout manages the layout of self.parameter_QFrame
        # - instantiated in setup_ui()
        # self.parameter_QGridLayout = None

        # Defined in AbstractCommandEditor
        # The row position in the self.parameter_QGridLayout, used in setup_ui() and its helper functions.
        self.y_parameter = -1

        # Defined in AbstractCommandEditor
        # "input_ui_components" is a dictionary that relates each command parameter with its associated Qt Widget
        # input field
        # KEY (str): the command parameter name
        # VALUE (obj): the associated Qt Widget input component
        self.input_ui_components = {}

        # Setup the UI in the AbstractCommandEditor class, which will call back to setup_ui() in this class.
        # - the AbstractCommandEditor populates some UI components such as the buttons at the bottom
        self.setup_ui_core()

        # Defined here and NOT in AbstractCommandEditor
        # Initially call refresh to the UI in case updating a command
        # - will transfer command parameter values into the UI components
        self.refresh_ui()

    def check_input(self) -> None:
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
        self.command.initialize_command(command_string, self.command.command_processor, True)

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

    def refresh_ui(self) -> None:
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
                except KeyError:
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
        # noinspection PyBroadException
        try:
            # Add all parameters to a temporary dictionary
            parameters_from_ui = dict()
            for command_parameter_metadata in self.command.command_parameter_metadata:
                # Parameters listed in logical order such as input / analysis / output
                parameter_name = command_parameter_metadata.parameter_name
                try:
                    parameter_value = None
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
                except KeyError:
                    # Should not happen because all parameters should have at least a text field.
                    message = "No input component for parameter '" + parameter_name + "' - code problem."
                    logger.warning(message, exc_info=True)
                    continue
            # Have a dictionary of parameters extracted from UI components
            # - format the command string using the command instance
            # - this does not change the command string in the command instance
            command_string = self.command.to_string(parameters_from_ui)
            self.CommandDisplay_View_TextBrowser.setPlainText(command_string)
        except Exception:
            message = "Error refreshing command from parameters"
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

    def setup_ui(self) -> None:
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
        # 5. Calls setup_ui_2() to activate the first component so user does not need to position.

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

            input_metadata = None  # needed to avoid warning
            # noinspection PyBroadException
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
                # noinspection PyPep8Naming
                parameter_Description = None
                try:
                    # noinspection PyPep8Naming
                    parameter_Description = input_metadata[request_key]
                except KeyError:
                    # Default to a simple statement with parameter name.
                    logger.warning(parameter_name + " does not have parameter_input_metadata value " + request_key +
                                   ".  Defaulting to parameter name.")
                    # noinspection PyPep8Naming
                    parameter_Description = parameter_name

                # FileSelector.Type
                # - new is FileSelector.Type
                # - old is FileSelectorType
                request_key1 = parameter_name + "." + "FileSelector.Type"
                # noinspection PyPep8Naming
                parameter_FileSelectorType = None
                try:
                    # noinspection PyPep8Naming
                    parameter_FileSelectorType = input_metadata[request_key1]
                except KeyError:
                    # Old...
                    request_key2 = parameter_name + "." + "FileSelectorType"
                    try:
                        # noinspection PyPep8Naming
                        parameter_FileSelectorType = input_metadata[request_key2]
                        logger.warning('Need to convert FileSelectorType to FileSelector.Type for command ' +
                                       self.command.command_name)
                    except KeyError:
                        # Default is None because file selector is only used for files
                        pass  # None was assigned above

                # Group
                request_key = parameter_name + "." + "Group"
                # noinspection PyPep8Naming
                parameter_Group = None
                try:
                    # noinspection PyPep8Naming
                    parameter_Group = input_metadata[request_key]
                except KeyError:
                    # Group is only used for Tabbed editor type so it is optional in most cases
                    # - do need some logic somewhere that if Group is specified for one parameter,
                    #   it should probably be specified for all parameters
                    # - however, defaulting to the first group may make sense
                    pass  # None was assigned above

                # Label
                request_key = parameter_name + "." + "Label"
                # noinspection PyPep8Naming
                parameter_Label = None
                try:
                    # noinspection PyPep8Naming
                    parameter_Label = input_metadata[request_key]
                except KeyError:
                    # Default to the parameter name, but warn so developers can set the label intelligently.
                    # - the default of parameter name is likely less friendly to the user so should always configure
                    #   in metadata
                    logger.warning(parameter_name + " does not have parameter_input_metadata value " + request_key +
                                   ".  Defaulting to parameter name.")
                    # noinspection PyPep8Naming
                    parameter_Label = parameter_name

                # Required
                request_key = parameter_name + "." + "Required"
                # noinspection PyPep8Naming
                parameter_Required = None
                try:
                    # noinspection PyPep8Naming
                    parameter_Required = input_metadata[request_key]
                except KeyError:
                    # Default value is optional given that True is imposed as a special case
                    # noinspection PyPep8Naming
                    parameter_Required = False

                # Tooltip
                request_key = parameter_name + "." + "Tooltip"
                # noinspection PyPep8Naming
                parameter_Tooltip = None
                try:
                    # noinspection PyPep8Naming
                    parameter_Tooltip = input_metadata[request_key]
                except KeyError:
                    # Default is an empty string
                    # - components should check for None or empty string and not set tooltip in this case
                    # noinspection PyPep8Naming
                    parameter_Tooltip = ""

                # Value.Default
                request_key = parameter_name + "." + "Value.Default"
                # noinspection PyPep8Naming
                parameter_ValueDefault = None
                try:
                    # noinspection PyPep8Naming
                    parameter_ValueDefault = input_metadata[request_key]
                except KeyError:
                    # Default value is not required and and will be component-specific
                    # - for example, blank string for text field
                    # - for example, select first value in `Values` metadata
                    pass

                # Value.Default.Description
                request_key = parameter_name + "." + "Value.Default.Description"
                # noinspection PyPep8Naming
                parameter_ValueDefaultDescription = None
                try:
                    # noinspection PyPep8Naming
                    parameter_ValueDefaultDescription = input_metadata[request_key]
                except KeyError:
                    # Default value description but will be used if Value.Default is specified
                    # - for example, long description of internal default assignment
                    pass

                # Values
                request_key = parameter_name + "." + "Values"
                # noinspection PyPep8Naming
                parameter_Values = None
                try:
                    # noinspection PyPep8Naming
                    parameter_Values = input_metadata[request_key]
                except KeyError:
                    # Default is that Values is not used.
                    # - it is only required for choices and can print more specific warnings below
                    # - None was set above
                    pass

            except Exception:
                # Don't continue with edit because there could be major confusion
                # - this should NEVER happen unless there is a code error because above logic is basic
                message = 'Error getting command editor metadata - cannot edit command.'
                logger.warning(message)
                logger.warning(message, exc_info=True)
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
                # noinspection PyPep8Naming
                parameter_ValuesEditable = None
                try:
                    # noinspection PyPep8Naming
                    parameter_ValuesEditable = input_metadata[request_key]
                except KeyError:
                    # Default value is combo boxes are not editable
                    # noinspection PyPep8Naming
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
                                                    parameter_Description,
                                                    parameter_Required,
                                                    parameter_Tooltip,
                                                    parameter_ValueDefault,
                                                    parameter_ValueDefaultDescription)

            # Set column width for text entry fields
            self.parameter_QGridLayout.setColumnMinimumWidth(1, 350)

        if self.debug:
            logger.info("Successfully created UI components.  Entering edit/refresh mode.")

    def ui_action_cancel_clicked(self) -> None:
        """
        Handle clicking on cancel button:

        1. What happens?

        Returns:
            None
        """
        # To cancel, call the standard reject() function, which will set the return value.
        # - this allows the return value to be checked in the calling code
        self.reject()

    def ui_action_ok_clicked(self) -> None:
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
