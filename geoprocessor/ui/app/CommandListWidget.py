# CommandListWidget - UI component to display list of commands with scrolling and status gutter
#_________________________________________________________________NoticeStart_
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
#_________________________________________________________________NoticeEnd___

import functools
import geoprocessor.ui.util.CommandListBackup as command_list_backup
import geoprocessor.ui.util.qt_util as qt_util
import geoprocessor.util.app_util as app_util
from PyQt5 import QtCore, QtGui, QtWidgets
import math

# The following code is generated by QT Designer and returns a QString from UTF-8 string.
try:
    # _fromUtf8 = QtCore.QString.fromUtf8
    _fromUtf8 = lambda s: s
except AttributeError:
    def _fromUtf8(s: object):
        return s

class CommandListWidget(object):

    """
    This class is designed to be a modular view that can be placed in the overall
    GeoProcessor UI design.
    """

    def __init__(self, commands_GroupBox):
        """
        Initialize the CommandListWidget object with necessary global variables
        :param commands_GroupBox:
        """

        # Initialize the group box that will contain the command list widget
        self.commands_GroupBox = commands_GroupBox

        # Create empty object to hold the model listener
        self.command_model_listener = None

        # Create empty object to hold main ui listener
        self.command_main_ui_listener = None

        # An array to hold the list of commands coming from the geoprocessor
        self.command_list = []

        # Global ui elements...
        # Layout
        self.commands_GridLayout = None
        self.commands_HBoxLayout_Commands = None
        self.commands_HBoxLayout_Buttons = None
        # List widgets
        self.commands_List = None
        self.numbered_List = None
        self.gutter = None
        # Buttons
        self.commands_RunAllCommands_PushButton = None
        self.commands_RunSelectedCommands_PushButton = None
        self.commands_ClearCommands_PushButton = None

        # Initialize a command list backup object. This will keep track of the command list and
        # notify the program if it has been edited since the previous save.
        self.command_list_backup = command_list_backup.CommandListBackup()

        # Keep track of errors and warnings in command list
        self.num_errors = 0
        self.num_warnings = 0

        # Setup the user interface elements of the command list widget
        self.setupUi()

    def add_model_listener(self, listener):
        """
        Initialize the model listener
        :param listener: Model object that will listen for events from
        command list widget
        :return: None
        """
        if not listener:
            return
        self.command_model_listener = listener

    def add_main_ui_listener(self, listener):
        """
        Initialize the main ui listener
        :param listener: model object that will listen for events from
        command list widget
        :return: None
        """
        if not listener:
            return
        self.command_main_ui_listener = listener

    def command_list_modified(self):
        """
        See if the command list has been modified.
        :return: Return True if modified, otherwise return False
        """
        return self.command_list_backup.command_list_modified(self.command_list)

    @staticmethod
    def command_list_vertical_scroll(vs, value):
        """
        Connect the vertical scrolling with command list and numbered list
        :param vs: vertical scroll bar to update
        :param value: the value to set the vertical scroll bar to
        :return:
        """
        vs.setValue(value)

    def delete_numbered_list_item(self, index):
        """
        Delete the row in the numbered list and update the other numbers
        accordingly so they are still in order
        :param index: numbered list item to be deleted
        :return: None
        """
        # Remove item at index
        self.numbered_List.takeItem(index)
        # Get the length of the numbered list
        count = self.numbered_List.count()

        # Update numbers past the deleted row
        for i in range(index, count):
            list_text = self.numbered_List.item(i).text()
            if list_text:
                num = int(self.numbered_List.item(i).text())
                num -= 1
                self.numbered_List.item(i).setText(str(num))

    def event_handler_commands_list_clicked(self, event):
        """
        When clicking on a command list item also select the same
        row in the numbered list and gutter
        :param event: Release click event from numbered list.
        :return: None
        """
        # First clear previous selections from numbered list and gutter
        self.numbered_List.clearSelection()
        self.gutter.clearSelection()

        # Update numbered list and gutter with selections
        selected_q_indices = self.commands_List.selectionModel().selectedIndexes()
        selected_indices = [item.row() for item in selected_q_indices]
        for index in selected_indices:
            self.numbered_List.item(index).setSelected(True)
            self.gutter.item(index).setSelected(True)

    def event_handler_button_run_all_commands_clicked(self, event):
        """
        Notify GeoProcessorListModel that the run all commands button has been clicked
        :param event: event.. this must be a parameter in order for PyQt5 to recognize
        it as being a function that will overwrite the default event handler
        :return: None
        """
        self.notify_model_listener_main_ui_listener_run_all_commands_clicked()

    def event_handler_button_run_selected_commands_clicked(self, event):
        """
        Notify GeoProcessorListModel that the run selected commands button has been clicked
        :param index_start: Index of first command list selected
        :param index_end: Index of last command list selected
        :return: None
        """
        selected_q_indices = self.commands_List.selectionModel().selectedIndexes()
        selected_indices = [item.row() for item in selected_q_indices]
        self.notify_model_listener_main_ui_listener_run_selected_commands_clicked(selected_indices)

    def event_handler_button_clear_commands_clicked(self, event):
        """
        When clicking on the clear commands button clear all commands if none
        individually selected or only clear the selected commands
        :param event: clicked event
        :return: None
        """
        selected_q_indices = self.commands_List.selectionModel().selectedIndexes()
        if selected_q_indices:
            # Open a message box to confirm with the user that they want to delete all of the commands.
            response = qt_util.new_message_box(
                QtWidgets.QMessageBox.Question,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                "Are you sure you want to delete selected commands?",
                "Clear Commands")

            # If the user confirms that they want to delete the selected commands, delete the commands.
            # - Delete using objects so indices are not an issue
            if response == QtWidgets.QMessageBox.Yes:
                selected_indices = [item.row() for item in selected_q_indices]
                self.notify_model_listener_clear_selected_commands(selected_indices)
        else:
            # Open a message box to confirm with the user that they want to delete all of the commands.
            response = qt_util.new_message_box(
                QtWidgets.QMessageBox.Question,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                "Are you sure you want to delete ALL the commands?",
                "Clear Commands")

            # If the user confirms that they want to delete the selected commands, delete the commands.
            # - Delete using objects so indices are not an issue
            if response == QtWidgets.QMessageBox.Yes:
                self.notify_model_listener_clear_all_commands()

        # Check to see if command list modified. If so notify the main ui
        self.command_main_ui_listener.update_ui_main_window_title()

    def event_handler_decrease_indent_button_clicked(self):
        """
        Notify the GeoProcessorListModel that one of the increase indent buttons have been clicked
        :return:
        """
        selected_q_indices = self.commands_List.selectionModel().selectedIndexes()
        selected_indices = [item.row() for item in selected_q_indices]
        self.notify_model_listener_decrease_indent_button_clicked(selected_indices)
        self.update_selected_commands(selected_indices)

        # Check to see if command list modified. If so notify the main ui
        self.command_main_ui_listener.update_ui_main_window_title()

    def event_handler_indent_button_clicked(self):
        """
        Notify the GeoProcessorListModel that one of the increase indent buttons have been clicked
        :return:
        """
        selected_q_indices = self.commands_List.selectionModel().selectedIndexes()
        selected_indices = [item.row() for item in selected_q_indices]
        self.notify_model_listener_indent_button_clicked(selected_indices)
        self.update_selected_commands(selected_indices)

        # Check to see if command list modified. If so notify the main ui
        self.command_main_ui_listener.update_ui_main_window_title()

    def event_handler_gutter_clicked(self, event):
        """
        When clicking on a gutter item also select the same
        row in the command list and the numbered list
        :param event:
        :return: QListWidgetItem
        """
        index = self.gutter.currentRow()
        self.numbered_List.setCurrentRow(index)
        self.commands_List.setCurrentRow(index)

    def event_handler_numbered_list_item_clicked(self, event):
        """
        When clicking on a numbered list item also select the same
        row in the command list and the gutter
        :param event: Release click event from numbered list.
        :return: None
        """
        index = self.numbered_List.currentRow()
        self.commands_List.setCurrentRow(index)
        self.gutter.setCurrentRow(index)

        selected_command = self.command_list[index]
        command_status = selected_command.command_status
        run_status = command_status.run_status
        if run_status == "WARNING" or run_status == "FAILURE":
            self.notify_main_ui_listener_numbered_list_clicked()

    def event_handler_numbered_list_item_hover(self, event):
        """
        Notify main ui that the numbered list is being hovered over
        :param event: event from mouseEnter event
        :return: None
        """
        self.notify_main_ui_listener_numbered_list_on_hover(event)

    def get_command_list_position(self):
        """
        :return: the current position of command list widget which is
        used in GeoProcessorUI to display the context menu on command list
        selection in the proper place
        """
        return self.commands_List.mapToGlobal(QtCore.QPoint(0, 0))

    def get_current_list_item_index(self):
        """
        :return: The current list widget item that is selected
        """
        return self.commands_List.currentRow()

    def group_box_resize(self, event):
        # """
        # Update the size of the gutter to ensure that it doesn't scroll and that it
        # appropriately displays a good overview of all issues.
        #
        # :return: None
        # """

        # Get the current height of the gutter
        current_height = self.gutter.height()
        # Check the count of all
        count = self.commands_List.count()
        # Get the height of all items
        current_items_height = 16 * count
        # Make sure count is never 0, if so set to 1
        if count == 0:
            count = 1

        item_height = math.floor(current_height / count)
        if current_items_height > current_height - 4:
            for i in range(0, self.commands_List.count()):
                item = self.gutter.item(i)
                item.setSizeHint(QtCore.QSize(-1, item_height))
        else:
            for i in range(0, self.commands_List.count()):
                item = self.gutter.item(i)
                item.setSizeHint(QtCore.QSize(-1, 16))

        # update last item in list to always fill whole space, for better appearance
        # and to also ensure there is never any scrolling
        # could be improved upon in the future
        # new gutter height
        new_height = item_height * count
        if new_height > current_height - 4:
            # 4 offers as a buffer
            last_item_height = item_height + (current_height - new_height - 4)
            # update height of last item
            # TODO smalers added the following check, otherwise the app crashed
            if self.gutter.item(count - 1) is not None:
                self.gutter.item(count - 1).setSizeHint(QtCore.QSize(-1, last_item_height))

    def gutter_error_at_row(self, index):
        """
        Set gutter row to red if there is a command line error on this row.
        :param index: index of row in gutter with error
        :return: None
        """
        item = self.gutter.item(index)
        item.setBackground(QtCore.Qt.red)

    def gutter_warning_at_row(self, index):
        """
        Set gutter row to yellow if there is a command line warning on this row.
        :param index: index of row in gutter with a warning
        :return: None
        """
        item = self.gutter.item(index)
        item.setBackground(QtCore.Qt.yellow)

    def notify_main_ui_listener_numbered_list_clicked(self):
        """
        Notify the main ui listener that the numbered list item has been clicked
        :return: None
        """
        self.command_main_ui_listener.show_command_status()

    def notify_main_ui_listener_numbered_list_on_hover(self, event):
        """
        Notify the main ui listener that the numbered list item is being hovered over
        :param: on hover event passed from numbered list mouseEnter event
        :return: None
        """
        self.command_main_ui_listener.show_command_status_tooltip(event)

    def notify_main_ui_listener_right_click(self, q_pos):
        """
        Notify the main ui listener that of a command line right click event
        :param q_pos: the position of the context menu
        :return: None
        """
        self.command_main_ui_listener.ui_action_command_list_right_click(q_pos)

    def notify_model_listener_clear_all_commands(self):
        """
        Notify the model listener that clear commands button has been clicked
        :return: None
        """
        self.command_model_listener.clear_all_commands()

    def notify_model_listener_clear_selected_commands(self, selected_indices):
        """
        Notify the model listener that clear selected commands has been clicked
        :param selected_indices: A list of integers representing the index of the
        selected commands
        :return: None
        """
        self.command_model_listener.clear_selected_commands(selected_indices)

    def notify_model_listener_decrease_indent_button_clicked(self, selected_indices):
        """
        Notify the model listener that one of the decrease indent button has been clicked
        :param selected_indices: A list of integers representing the index of the
        commands to decrease the indent of
        :return: None
        """
        self.command_model_listener.decrease_indent_command_string(selected_indices)

    def notify_model_listener_indent_button_clicked(self, selected_indices):
        """
        Notify the model listener that one of the indent button has been clicked
        :param selected_indices: A list of integers representing the index of the
        commands to add indent to
        :return: None
        """
        self.command_model_listener.indent_command_string(selected_indices)

    def notify_model_listener_main_ui_listener_run_all_commands_clicked(self):
        """
        Notify the model listener that the run all commands button has been clicked
        :return: None
        """
        self.command_model_listener.run_all_commands()
        self.command_main_ui_listener.show_results()

    def notify_model_listener_main_ui_listener_run_selected_commands_clicked(self, selected_indices):
        """
        Notify the model listener that the geoprocessor
        :param selected_indices:
        :return: None
        """
        self.command_model_listener.run_selected_commands(selected_indices)
        self.command_main_ui_listener.show_results()

    def notify_main_ui_listener_refresh_results(self):
        """
        Notify the main ui that the results should be refreshed
        :return: None
        """
        self.command_main_ui_listener.show_results()

    def numbered_list_error_at_row(self, index):
        """
        Add the error icon to the numbered list row with an error
        :param index: insert icon at numbered list index where error occurred
        :return: None
        """
        # Get item from index
        item = self.numbered_List.item(index)
        # Get the error icon from path
        icon_path = app_util.get_property("ProgramResourcesPath").replace('\\', '/')
        icon_path = icon_path + "/images/error.gif"
        # Create icon
        error_icon = QtGui.QIcon(icon_path)
        # Add icon to QListWidgetItem
        item.setIcon(error_icon)

    def numbered_list_warning_at_row(self, index):
        """
        Add the warning icon to the numbered list row with an warning
        :param index: insert icon at numbered list index where warning occurred
        :return: None
        """
        # Get item from index
        item = self.numbered_List.item(index)
        # Get the warning icon from path
        icon_path = app_util.get_property("ProgramResourcesPath").replace('\\', '/')
        icon_path = icon_path + "/images/warning.gif"
        # Create icon
        error_icon = QtGui.QIcon(icon_path)
        # Add icon to QListWidgetItem
        item.setIcon(error_icon)

    def numbered_list_unknown_at_row(self, index):
        """
        Add the unknown icon to the numbered list row with an unknown
        :param index: insert icon at numbered list index where unknown occurred
        :return: QListWidgetItem
        """
        item = self.numbered_List.item(index)
        # Get the unknown icon from path
        icon_path = app_util.get_property("ProgramResourcesPath").replace('\\', '/')
        icon_path = icon_path + "/images/unknown.gif"
        # Create icon
        error_icon = QtGui.QIcon(icon_path)
        # Add icon to QListWidgetItem
        item.setIcon(error_icon)

    def selected_command_list_indices(self):
        # selected_items = self.commands_List.selectedItems()
        # for item in selected_items:
        #     print(self.commands_List.indexFromItem(item))
        print(self.commands_List.selectionModel().selectedIndexes())

    def set_command_list(self, command_list):
        """
        Assign the command list to the passed in command list
        coming from geoprocessor in the GeoProessorListModel
        :param command_list: array of commands
        :return: None
        """
        self.command_list = command_list

    def set_command_list_backup(self):
        """
        Initialize the command list backup to check against later changes of the
        command list to see if modified
        :return: None
        """
        # Update the command list backup
        self.command_list_backup.update_command_list(self.command_list)

    def setupUi(self):
        """
        Setup all GUI elements of the CommandListWidget Area including the command list, the numbered
        list to the left of the commands and the gutter to the right of the commands.
        :return: None
        """

        # Add event handler for QGroupBox resize event
        self.commands_GroupBox.resizeEvent = self.group_box_resize
        self.commands_GroupBox.setObjectName(_fromUtf8("commands_GroupBox"))
        self.commands_GroupBox.setTitle("Commands (0 commands, 0  selected, 0 with failures, 0 with warnings)")

        # Add basic QListWidget elements to design the command list
        self.setup_ui_command_list_widget_layout()
        self.setup_ui_command_list_widget_numbered_list()
        self.setup_ui_command_list_widget_command_list()
        # Connect scrolling between commands list and numbered list
        vs1 = self.commands_List.verticalScrollBar()
        vs2 = self.numbered_List.verticalScrollBar()
        vs1.valueChanged.connect(functools.partial(self.command_list_vertical_scroll, vs2))
        vs2.valueChanged.connect(functools.partial(self.command_list_vertical_scroll, vs1))
        self.setup_ui_command_list_widget_gutter()

        # Buttons
        self.setup_ui_command_list_widget_button_run_selected_commands()
        self.setup_ui_command_list_widget_button_run_all_commands()
        # Spacer makes sure that buttons on left and right are correctly positioned
        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.commands_HBoxLayout_Buttons.addItem(spacer_item)
        self.setup_ui_command_list_widget_button_clear_commands()

    def setup_ui_command_list_widget_command_list(self):
        """
        Setup the command list for the command list widget
        :return: None
        """
        # Commands area list
        self.commands_List = QtWidgets.QListWidget(self.commands_GroupBox)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("MS Shell Dlg 2"))
        self.commands_List.setFont(font)
        self.commands_List.setAutoScroll(True)
        self.commands_List.setDragDropOverwriteMode(False)
        self.commands_List.setAlternatingRowColors(True)
        self.commands_List.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.commands_List.setProperty("isWrapping", False)
        self.commands_List.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.commands_List.setWordWrap(False)
        self.commands_List.setSelectionRectVisible(False)
        self.commands_List.mouseReleaseEvent = self.event_handler_commands_list_clicked
        self.commands_List.setObjectName(_fromUtf8("commands_List"))
        self.commands_List.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.commands_HBoxLayout_Commands.addWidget(self.commands_List)
        # Define listeners to handle events
        # Listen for a change in item selection within the commands_List widget.
        self.commands_List.itemSelectionChanged.connect(self.update_ui_status_commands)
        # Other connections
        # Connect right-click of commands_List widget item.
        self.commands_List.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.commands_List.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.commands_List.customContextMenuRequested.connect(self.notify_main_ui_listener_right_click)

    def setup_ui_command_list_widget_gutter(self):
        """
        Setup the gutter to the right of the command list for command list widget
        :return: None
        """
        # Gutter
        self.gutter = QtWidgets.QListWidget(self.commands_GroupBox)
        self.gutter.setFixedWidth(21)
        self.gutter.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.gutter.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.gutter.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.gutter.setObjectName('gutter')
        # Connect gutter click to custom gutter_clicked function
        self.gutter.mouseReleaseEvent = self.event_handler_gutter_clicked
        self.commands_HBoxLayout_Commands.addWidget(self.gutter)

    def setup_ui_command_list_widget_layout(self):
        """
        Setup the layout for the command list widget
        :return: None
        """
        # Add a grid layout to group box
        self.commands_GridLayout = QtWidgets.QGridLayout(self.commands_GroupBox)

        # Create a horizontal box layout for the numbered list, command list, and the gutter
        self.commands_HBoxLayout_Commands = QtWidgets.QHBoxLayout()
        self.commands_GridLayout.addLayout(self.commands_HBoxLayout_Commands, 0, 0)

        # Create a horizontal box layout for the buttons
        self.commands_HBoxLayout_Buttons = QtWidgets.QHBoxLayout()
        self.commands_GridLayout.addLayout(self.commands_HBoxLayout_Buttons, 1, 0)

        # Set spacing between the two horizontal layouts to none
        self.commands_HBoxLayout_Commands.setSpacing(0)

    def setup_ui_command_list_widget_numbered_list(self):
        """
        Setup the numbered list to left of command list
        :return: None
        """
        # Create a list next to command list that reflects command line numbers
        self.numbered_List = QtWidgets.QListWidget()
        self.numbered_List.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.numbered_List.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.numbered_List.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.numbered_List.setFocusPolicy(QtCore.Qt.NoFocus)
        self.numbered_List.setMouseTracking(True)
        self.numbered_List.mouseReleaseEvent = self.event_handler_numbered_list_item_clicked
        self.numbered_List.mouseMoveEvent = self.event_handler_numbered_list_item_hover
        self.numbered_List.setObjectName("numbered_list")
        self.numbered_List.addItem('')
        self.commands_HBoxLayout_Commands.addWidget(self.numbered_List)
        self.update_numbered_list_width()

    def setup_ui_command_list_widget_button_run_selected_commands(self):
        """
        Setup the run selected commands button for the command list widget
        :return: None
        """
        # Commands area buttons under the list
        self.commands_RunSelectedCommands_PushButton = QtWidgets.QPushButton(self.commands_GroupBox)
        self.commands_RunSelectedCommands_PushButton.setEnabled(False)
        self.commands_RunSelectedCommands_PushButton.setDefault(False)
        self.commands_RunSelectedCommands_PushButton.setFlat(False)
        self.commands_RunSelectedCommands_PushButton.setObjectName(_fromUtf8("commands_RunSelectedCommands_PushButton"))
        self.commands_RunSelectedCommands_PushButton.setText("Run Selected Commands")
        self.commands_RunSelectedCommands_PushButton.setToolTip("Run selected commands from above to generate results.")
        self.commands_HBoxLayout_Buttons.addWidget(self.commands_RunSelectedCommands_PushButton)
        # Connect the Run Selected Commands button.
        self.commands_RunSelectedCommands_PushButton.clicked.connect(self.event_handler_button_run_selected_commands_clicked)

    def setup_ui_command_list_widget_button_run_all_commands(self):
        """
        Setup the run all commands button for the command list widget
        :return: None
        """
        self.commands_RunAllCommands_PushButton = QtWidgets.QPushButton(self.commands_GroupBox)
        self.commands_RunAllCommands_PushButton.setEnabled(False)
        self.commands_RunAllCommands_PushButton.setObjectName(_fromUtf8("commands_RunAllCommands_PushButton"))
        self.commands_RunAllCommands_PushButton.setText("Run All Commands")
        self.commands_RunAllCommands_PushButton.setToolTip("Run all commands from above to generate results.")
        self.commands_HBoxLayout_Buttons.addWidget(self.commands_RunAllCommands_PushButton)
        # Connect the Run All Commands button.
        self.commands_RunAllCommands_PushButton.clicked.connect(self.event_handler_button_run_all_commands_clicked)

    def setup_ui_command_list_widget_button_clear_commands(self):
        """
        Setup the clear commands button for the command list widget
        :return: None
        """
        self.commands_ClearCommands_PushButton = QtWidgets.QPushButton(self.commands_GroupBox)
        self.commands_ClearCommands_PushButton.setEnabled(False)
        self.commands_ClearCommands_PushButton.setObjectName(_fromUtf8("commands_ClearCommands_PushButton"))
        self.commands_ClearCommands_PushButton.setText("Clear Commands")
        self.commands_ClearCommands_PushButton.setToolTip(
            "Clear selected commands.  Clear all commands if none are selected.")
        self.commands_HBoxLayout_Buttons.addWidget(self.commands_ClearCommands_PushButton)
        # Connect the Clear Commands button.
        self.commands_ClearCommands_PushButton.clicked.connect(self.event_handler_button_clear_commands_clicked)

    def update_selected_commands(self, selected_indices):
        """
        Update which commands are selected. Selected commands get
        reset when refreshing UI content with commands in GeoProcessor but
        we want the selected items to stay selected unless the user de-selects
        them.
        :param selected_indices: A list of integers representing the index of the
        selected items
        :return: None
        """
        for i in range(0, len(selected_indices)):
            index = selected_indices[i]
            self.commands_List.item(index).setSelected(True)
            self.numbered_List.item(index).setSelected(True)
            self.gutter.item(index).setSelected(True)

    def update_ui_status_commands(self):
        """
        Update the UI status for Commands area.
        Count the number of items (each item is a command string) in the Command_List widget. Update the total_commands
        class variable to the current number of command items in the Command_List widget. Update the selected_commands
        class variable to the current number of selected command items in the Command_List widget. Update the
        Command_List widget label to display the total and selected number of commands within the widget.

        Returns: None
        """
        # Count the number of items (each item is a command string) in the Command_List widget.
        total_commands = self.commands_List.count()

        # If there is at least one command in the Command_List widget, enable the "Run All Commands" button and the
        # "Clear Commands" button. If not, disable the "Run All Commands" button and the "Clear Commands" button.
        if total_commands > 0:
            self.commands_RunAllCommands_PushButton.setEnabled(True)
            self.commands_ClearCommands_PushButton.setEnabled(True)
        else:
            self.commands_RunAllCommands_PushButton.setEnabled(False)
            self.commands_ClearCommands_PushButton.setEnabled(False)

        # Count the number of selected items (each item is a command string) in the Command_List widget.
        selected_commands = len(self.commands_List.selectedItems())

        # If there is at least one selected command in the Command_List widget, enable the "Run Selected Commands"
        # button. If not, disable the "Run Selected Commands" button.
        if selected_commands > 0:
            self.commands_RunSelectedCommands_PushButton.setEnabled(True)
        else:
            self.commands_RunSelectedCommands_PushButton.setEnabled(False)

        # Update the Command_List widget label to display the total and selected number of commands.
        self.commands_GroupBox.setTitle(
            "Commands ({} commands, {} selected, {} with failures, {} with warnings)".format(
                total_commands, selected_commands, self.num_errors, self.num_warnings))

    def update_command_list(self, command_string):
        """
        Add data to the command list
        :param command_string: a command string to add to the command list
        :return: None
        """
        item = QtWidgets.QListWidgetItem()
        item.setText(command_string.rstrip())
        qsize = QtCore.QSize()
        qsize.setHeight(16)
        qsize.setWidth(self.commands_List.size().width())
        item.setSizeHint(qsize)
        if command_string.strip()[0] == '#':
            item.setForeground(QtGui.QColor(68, 121, 206))
        self.commands_List.addItem(item)

    def update_command_list_widget(self):
        """
        Update the command list widget from a command list that
        has already been initialized
        :return: None
        """

        # Start by clearing all data from the command list widget
        self.commands_List.clear()
        self.numbered_List.clear()
        self.gutter.clear()

        # Loop through command_list from geoprocessor and add data to command list widget
        for i, command in enumerate(self.command_list):
            command_string = command.command_string
            self.update_command_list(command_string)
            self.update_numbered_list(i)
            self.update_gutter()

        self.numbered_List.addItem("")

    def update_numbered_list(self, index):
        """
        Add a new line to numbered list in accordance with command list
        given the index of the command list
        :param index: index of numbered list to add
        :return:
        """
        # Increment index to index starting at 1
        index += 1
        # Add numbers to numbered list
        item = QtWidgets.QListWidgetItem()
        item.setText(str(index))
        item.setTextAlignment(QtCore.Qt.AlignRight)
        item.setSizeHint(QtCore.QSize(-1, 16))
        ## item.mouseReleaseEvent = self.show_command_status_tooltip
        self.numbered_List.addItem(item)
        self.update_numbered_list_width()

    def update_numbered_list_width(self):
        largest_int = self.numbered_List.count()
        myFont = QtGui.QFont()
        string = str(largest_int)
        fm = QtGui.QFontMetrics(myFont)
        maximum_int_width = fm.width(string)
        width = maximum_int_width + 38
        self.numbered_List.setFixedWidth(width)

    def update_ui_command_list_errors(self):
        """
        Once commands have been run. Loop through and check for any errors or warnings.
        :return: None
        """
        # Start by clearing previous icons from numbered list and gutter
        for i in range(0, len(self.command_list)):
            numbered_list_item = self.numbered_List.item(i)
            numbered_list_item.setIcon(QtGui.QIcon())
            gutter_item = self.gutter.item(i)
            gutter_item.setBackground(QtCore.Qt.white)

        # Clear number of warnings and errors
        self.num_errors = 0
        self.num_warnings = 0

        # Now update the numbered list and gutter with current errors and warnings
        for i in range(0, len(self.command_list)):
            command_status = self.command_list[i].command_status.run_status
            if command_status == "FAILURE":
                self.numbered_list_error_at_row(i)
                self.gutter_error_at_row(i)
                self.num_errors += 1
            elif command_status == "WARNING":
                self.numbered_list_warning_at_row(i)
                self.gutter_warning_at_row(i)
                self.num_warnings += 1

    def update_gutter(self):
        """
        Add a new item to the gutter when a new command line has been
        added to the command list
        :return: None
        """
        # Add items to gutter
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(QtCore.QSize(-1, 16))
        self.gutter.addItem(item)
