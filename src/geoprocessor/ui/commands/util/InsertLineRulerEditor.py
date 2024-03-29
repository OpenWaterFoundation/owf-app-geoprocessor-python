# CommentEditor - editor for Comment command
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

from PyQt5 import QtCore, QtGui, QtWidgets

import geoprocessor.util.app_util as app_util
from geoprocessor.ui.commands.abstract.AbstractCommandEditor import AbstractCommandEditor
import geoprocessor.ui.util.qt_util as qt_util

import functools


class InsertLineRulerEditor(AbstractCommandEditor):
    """
    Command editor dialog for one or more # comments, which shows a rule for column spaces.
    This editor could be enabled for other commands but currently is only used with # comment blocks
    that can span multiple lines.
    """

    def __init__(self, command) -> None:
        """
        Initialize the InsertLineRulerEditor dialog instance.

        Args:
            command: the command to edit
        """
        # Call the parent class.
        super().__init__(command)

        # Defined in AbstractCommandEditor.
        # Initialize components that will be used>
        # self.CommandDisplay_View_TextBrowser = None

        # NOT defined in AbstractCommandEditor - local to this class:
        # - ruler above the comment area
        self.CommandDisplay_View_Ruler: QtWidgets.QTextEdit or None = None

        # NOT defined in AbstractCommandEditor - local to this class:
        # - used for fixed-width font in comment editor area
        self.CommandDisplay_View_Font: QtGui.QFont or None = None

        # Defined in AbstractCommandEditor.
        # Layout used for the main editor:
        # - other layouts may be added as needed to organize components
        # self.grid_layout = None

        # Defined in AbstractCommandEditor.
        # Position in the layout for components as they are added, 0=row at top, 1 is next down, etc.:
        # - each addition should increment before adding a component
        # self.grid_layout_row = -1

        # NOT defined in AbstractCommandEditor - local to this class.
        # Indicate if an error status is currently in effect, due to invalid parameters:
        # - will be set in check_input() and is checked in ui_action_ok_clicked()
        self.error_wait = False

        # NOT defined in AbstractCommandEditor - local to this class.
        # If command parameters have already been defined for the command, know that are updating an existing command.
        if command.command_parameters:
            self.update = True

        # NOT defined in AbstractCommandEditor - local to this class.
        # Create variable to know whether updating an existing command or inserting a new command into the command list.
        self.update = False

        # Set up the UI for the command editor window:
        # - this calls the AbstractCommandEditor method, which in turn calls specific methods to setup parts of the UI
        self.setup_ui_core()

    def check_input(self) -> None:
        """
        Check the parameter values shown in the editor to make sure all values are valid.
        There is nothing to check since no parameters.

        Returns:
            None.
        """
        pass

    def get_command_string_list(self) -> [str]:
        """
        Return the command strings from the edited text, can be an empty list (but using the editor to
        delete all existing comments is not usually done).
        This function can be called by the main GeoProcessorUI after editing to retrieve the result of the edit.

        Returns:
            A list of strings corresponding to each comment line.
        """
        # logger = logging.getLogger(__name__)
        # First split the text area using newline delimiter.
        command_text = self.CommandDisplay_View_TextBrowser.toPlainText()
        command_string_list = []
        if len(command_text) == 0:
            # Return an empty list, which should be handled in calling code.
            return command_string_list
        else:
            # Split the text by newlines according to Python universal newlines.
            command_string_list = command_text.splitlines()
            # Add the # with determined indent.
            # Verify that each line edited by user starts with '#'.
            for i in range(len(command_string_list)):
                command_string_stripped = command_string_list[i].strip()
                # Check if the stripped line starts with # and if so, it is OK:
                # - otherwise, add # at the start, indented appropriately
                if not command_string_stripped.startswith('#'):
                    # Figure out how many spaces to indent by examining the comment lines:
                    # - assume that indent should be consistent with nearest previous indented, commented line
                    # - if that is not found, search after the current line (TODO smalers 2019-01-18 need to do)
                    indent = ""
                    for j in range(i - 1, 0, -1):
                        indent_pos = command_string_list[j].find('#')
                        if indent_pos >= 0:
                            # Found a previous comment line so use its indent:
                            # - the following one-liner sets the indent to the number of spaces
                            indent += ' ' * indent_pos
                            break
                    command_string_list[i] = indent + "# " + command_string_list[i]
            # Return a list with one item for each line that was edited.
            return command_string_list

    def set_text(self, text: str) -> None:
        """
        Set the text in the text browser for the command editor.
        Typically, this is called when a multi-line comment is being edited.

        Args:
            text: String to insert as text in the command editor.

        Returns:
            None
        """
        # For now display the comment character in the editor if previously present.
        # text = text.replace("# ", "")
        # text = text.replace("#", "")
        self.CommandDisplay_View_TextBrowser.setText(text)

    def setup_ui(self) -> None:
        """
        This function is called by AbstractCommandEditor.setup_ui_core(), which sets up the editor dialog.
        A text area is displayed to enter comments.

        Returns:
            None
        """

        # The command has a custom editor area.
        # Set up the fixed-font ruler that is used when editing the comments.
        self.setup_ui_core_ruler()
        # TODO smalers 2020-03-12 the following don't appear to be needed.
        # self.setup_ui_core_command_area()
        # self.setup_ui_horizontal_scrolling()
        # The following sets the window size and sets to resizable.
        self.setup_ui_window()

    def setup_ui_2(self) -> None:
        """
        Set up the user interface after components have been added.
        Set the focus to the command text area.

        Returns:
            None
        """
        # logger = logging.getLogger(__name__)
        self.CommandDisplay_View_TextBrowser.setFocus()
        # TODO smalers 2020-03-15 the following only seems to work for new commands.
        # Set the position of the cursor the end of the document (same as TSTool):
        # - see:  https://doc.qt.io/qt-5/qtextcursor.html#MoveOperation-enum
        # - see:  https://forum.qt.io/topic/12336/solved-always-show-the-end-of-qtextbrowser/4
        # logger.debug("Command string: '" + str(self.command.command_string) + "'")
        self.CommandDisplay_View_TextBrowser.moveCursor(QtGui.QTextCursor.End)
        self.CommandDisplay_View_TextBrowser.verticalScrollBar().setValue(
            self.CommandDisplay_View_TextBrowser.verticalScrollBar().maximum())

    def setup_ui_window(self) -> None:
        """
        Setup specific elements in relation to the entire window.

        Returns:
            None
        """
        # Set the size of the window:
        # - this is necessary because the AbstractCommandEditor sets the size to smaller
        # - TODO smalers 2020-03-12 maybe need a property in command metadata to set
        self.setMaximumWidth(1150)
        self.resize(1150, 300)

    def setup_ui_core_command_area(self) -> None:
        """
        This overrides the method in AbstractCommandEditor.
        Set up the editing area for comments.
        A custom command area is needed because:

        1. The label is "Comments:" instead of "Command:".
        2. The command area is editable.
        3. The command area is aligned with the horizontal rule that shows character position.

        Returns:
            None

        """
        # The grid_layout_row is managed in AbstractCommandEditor.
        self.grid_layout_row = self.grid_layout_row + 1
        self.CommandDisplay_Label = QtWidgets.QLabel(self)
        self.CommandDisplay_Label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.CommandDisplay_Label.setObjectName(qt_util.from_utf8("CommandDisplay_Label"))
        self.CommandDisplay_Label.setText(qt_util.translate("Dialog", "Comments: ", None))
        comment_area_rows = 4  # How many layout rows the comment area fills.
        self.grid_layout.addWidget(self.CommandDisplay_Label, self.grid_layout_row, 0, comment_area_rows, 1)
        # Create a text edit object. Add the text edit object to the Dialog window.
        # Set the size, the name and the html of the text edit object.
        # The text edit object, CommandDisplay_View_TextBrowser, displays a dynamic view of the command string.
        # Use a font that is the same as the ruler.
        self.CommandDisplay_View_TextBrowser = QtWidgets.QTextEdit(self)
        self.CommandDisplay_View_TextBrowser.setObjectName("CommandDisplay_View_TextBrowser")
        self.CommandDisplay_View_TextBrowser.setMaximumHeight(200)
        self.CommandDisplay_View_Font = QtGui.QFont("Monospace")
        self.CommandDisplay_View_Font.setStyleHint(QtGui.QFont.TypeWriter)
        self.CommandDisplay_View_Font.setPointSize(10)
        self.CommandDisplay_View_TextBrowser.setFont(self.CommandDisplay_View_Font)
        self.CommandDisplay_View_TextBrowser.setWordWrapMode(QtGui.QTextOption.NoWrap)
        # Do not display default command string when editing a new comment.
        # If command_string is default reset to empty.
        command_string = self.command.command_string
        # Existing comments should be shown as is without stripping the leading #.
        self.CommandDisplay_View_TextBrowser.setText(command_string)
        # self.CommandDisplay_View_TextBrowser.setMinimumSize(QtCore.QSize(0, 100))
        # self.CommandDisplay_View_TextBrowser.setMaximumSize(QtCore.QSize(16777215, 100))
        # #html = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">" \
        # #       "\n<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\np, li { " \
        # #       "white-space: pre-wrap; }\n</style></head><body style=\" font-family:\'MS Shell Dlg 2\';" \
        # #       " font-size:8.25pt; font-weight:400; font-style:normal;\">\n<p style=\" margin-top:0px;" \
        # #       " margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">" \
        # #       "<span style=\" font-size:8pt;\">ReadGeoLayerFromGeoJSON()</span></p></body></html>"
        # #self.CommandDisplay_View_TextBrowser.setHtml(qt_util.translate("Dialog", html, None))
        self.grid_layout.addWidget(self.CommandDisplay_View_TextBrowser, self.grid_layout_row, 1, 4, -1)
        # Increment the row so that it is positioned at the last row of the text area, so it can be incremented again:
        # - already incremented by one above, so subtract one below
        if comment_area_rows > 1:
            self.grid_layout_row = self.grid_layout_row + (comment_area_rows - 1)

    def setup_ui_core_ruler(self) -> None:
        """
        Create a text box that shows a ruler across the top of the comments section.

        Returns:
            None.
        """

        self.grid_layout_row = self.grid_layout_row + 1
        self.CommandDisplay_View_Ruler = QtWidgets.QTextEdit(self)
        self.CommandDisplay_View_Ruler.setObjectName("CommandDisplay_View_Ruler")
        self.CommandDisplay_View_Font = QtGui.QFont("Monospace")
        self.CommandDisplay_View_Font.setStyleHint(QtGui.QFont.TypeWriter)
        self.CommandDisplay_View_Font.setPointSize(10)
        self.CommandDisplay_View_Ruler.setFont(self.CommandDisplay_View_Font)
        self.CommandDisplay_View_Ruler.setText("0         10        20        30        40        50        "
                                               "60        70        80        90        100       110\n"
                                               "0123456789012345678901234567890123456789012345678901234567890123456789"
                                               "012345678901234567890123456879012345678901234567890")
        self.CommandDisplay_View_Ruler.setReadOnly(True)
        self.CommandDisplay_View_Ruler.setMaximumHeight(45)
        self.CommandDisplay_View_Ruler.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.CommandDisplay_View_Ruler.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.CommandDisplay_View_Ruler.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.CommandDisplay_View_Ruler.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.grid_layout.addWidget(self.CommandDisplay_View_Ruler, self.grid_layout_row, 1, 1, -1)

    def ui_action_cancel_clicked(self) -> None:
        """
        Handle clicking on cancel button.

        Returns:
            None
        """
        # To cancel, call the standard reject() function, which will set the return value:
        # - this allows the return value to be checked in the calling code
        self.reject()

    def ui_action_ok_clicked(self) -> None:
        """
        Handle clicking on OK button:

        1. The parameters in the input components are validated - in this case no parameters need to be checked.
        2. If OK, exit by calling accept().
        3. If not OK, the editor stays open until the user corrects or presses Cancel.

        Returns:
            None
        """
        # Check the input
        self.check_input()
        if self.error_wait:
            # User was shown a warning dialog and had to acknowledge it, so here just ignore the "OK":
            # - errors in input parameters need to be fixed before OK works
            pass
        else:
            # No error so OK to exit:
            # - call the standard accept() function to set the return value
            # Set the comment string in the command:
            # - multiple lines will be parsed into separate lines, each with a Comment command
            self.command.command_string = self.CommandDisplay_View_TextBrowser.toPlainText()
            self.accept()

    # TODO smalers 2020-03-12 Keep the following functions for now but need to remove if not needed:
    # - some of these are already in AbstractCommandEditor
    # - others have been rewritten
    def x_add_ui_horizontal_separator(self) -> None:
        """
        Create a line (frame object with special specifications). Add the line to the Dialog window.
        Set the size policy, the shape, the shadow, and the name of the frame object to create the line separator.
        The frame object, Separator, separates the command description from the input form section of the Dialog box.

        Returns:
            None
        """
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


    def x_get_current_value(self, obj: QtWidgets.QWidget) -> str:
        """
        Get the value within a QtGui.Widget object.

        Args:
            obj (obj): the a QtGui.Widget object to read the value from

        Returns:
            the value within the QtGui.Widget object
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

    def x_horizontal_scroll(self, hs: QtWidgets.QScrollBar, value: int) -> None:
        """
        Connect the horizontal scrolling with command list and numbered list.

        Args:
            hs: Horizontal scroll bar to update.
            value: The value to set the horizontal scroll bar to.

        Returns:
            None
        """
        hs.setValue(value)

    def x_setup_ui_core(self) -> None:
        # Set up QDialog specifications.
        self.setup_ui_window()
        # Set up the editor core elements, which apply to any command.
        self.setup_ui_core_top()
        # Add separator.
        self.add_ui_horizontal_separator()
        # Set up the core components at the bottom.
        self.setup_ui_core_bottom()

        # This will wire up the signals and slots depending on names.
        # REF: http://joat-programmer.blogspot.com/2012/02/pyqt-signal-and-slots-to-capture-events.html
        # - don't do this because not using QtDesigner
        # QtCore.QMetaObject.connectSlotsByName(self)

        # Make sure the text area has the focus since that is where input will be typed.
        self.CommandDisplay_View_TextBrowser.setFocus()

    def x_setup_ui_core_bottom(self) -> None:
        """
        Setup core UI components at the bottom of the dialog.

        Returns:
            None
        """
        self.setup_ui_core_ruler()
        self.setup_ui_core_command_area()
        self.setup_ui_horizontal_scrolling()
        self.setup_ui_core_command_buttons()

    def x_setup_ui_core_top(self) -> None:
        """
        Setup core UI components at the top of the dialog.

        Returns:
            None
        """
        # Set the window title to the command name.
        self.setObjectName("InsertLineRulerEditor")
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
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        icon_path = app_util.get_property("ProgramIconPath").replace('\\', '/')
        self.setWindowIcon(QtGui.QIcon(icon_path))

        # Because components are added to the UI the dialog will have a size:
        # - don't set the size unless a dialog misbehaves, perhaps a maximum size
        # self.resize(684, 404)

        # Add a grid layout for components to be added.
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setObjectName(qt_util.from_utf8("gridLayout"))

        self.setup_ui_core_command_description()

    def x_setup_ui_core_command_buttons(self) -> None:
        # Create a button box object. Add the button box object to the Dialog window.
        # Set the orientation, the standard buttons, the name and the connections of the button box object.
        # The button box object, OK_Cancel_Buttons, allow the user to accept or reject the changes made in the dialog.
        self.OK_Cancel_Buttons = QtWidgets.QDialogButtonBox(self)
        self.OK_Cancel_Buttons.setOrientation(QtCore.Qt.Horizontal)
        self.OK_Cancel_Buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.OK_Cancel_Buttons.setObjectName(qt_util.from_utf8("OK_Cancel_Buttons"))
        self.OK_Cancel_Buttons.button(QtWidgets.QDialogButtonBox.Cancel).setToolTip(
            "Cancel command edit and ignore changes.")
        self.OK_Cancel_Buttons.button(QtWidgets.QDialogButtonBox.Ok).setToolTip("Save edits to command.")
        self.OK_Cancel_Buttons.accepted.connect(self.accept)
        self.OK_Cancel_Buttons.rejected.connect(self.reject)
        self.grid_layout_row = self.grid_layout_row + 4
        self.grid_layout.addWidget(self.OK_Cancel_Buttons, self.grid_layout_row, 6, 1, 2)

    def x_setup_ui_core_command_description(self) -> None:
        """
        Set up the description component at the top of the dialog.
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
        self.grid_layout.addWidget(description_Frame, self.grid_layout_row, 0, 1, 0)

        # Create a grid layout object. Apply to the Command_Description frame object.
        # Set the name of the grid layout object.
        self.gridLayout_2 = QtWidgets.QGridLayout(description_Frame)
        self.gridLayout_2.setObjectName(qt_util.from_utf8("gridLayout_2"))

        # Create a label. Add the label to the Command_Description frame object.
        # Set the name and the text of the label.
        # The label, Command_Description_Label, briefly describes the command.
        self.Command_Description_Label = QtWidgets.QLabel(description_Frame)
        self.Command_Description_Label.setObjectName(qt_util.from_utf8("Command_Description_Label"))
        self.Command_Description_Label.setText("Enter one or more comments.\n"
                                               "If not present, # will be automatically added when OK is pressed."
                                               "  # at the start of existing lines will be shown.\n"
                                               "See also the /* and */ commands for multi-line comments, which are "
                                               "useful for commenting out multiple commands.")
        self.gridLayout_2.addWidget(self.Command_Description_Label, 0, 0, 1, 2)

    def x_update_command_display(self) -> None:
        """
        Each command dialog box has a command display that shows the string representation of the command with the
        user-specified input parameters.
        It is updated dynamically as the user enters/selects values for the different command parameter fields
        (this function is called when any text is changed in the input field Qt widgets).
        The function is responsible for reading the inputs,
        creating the updated string representation of the command and updating the CommandDisplay widget.

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

        # If all the command parameter values are set to "" (not set), continue.
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

    # TODO smalers 2020-03-12 may need to enable this legacy code but resizable window seems to work OK.
    def x_setup_ui_horizontal_scrolling(self) -> None:
        """
        Connect the horizontal scrolling between the comment editor and the ruler up top.

        Returns:
            None
        """
        hs1 = self.CommandDisplay_View_TextBrowser.horizontalScrollBar()
        hs2 = self.CommandDisplay_View_Ruler.horizontalScrollBar()
        hs1.valueChanged.connect(functools.partial(self.horizontal_scroll, hs2))
        hs2.valueChanged.connect(functools.partial(self.horizontal_scroll, hs1))

