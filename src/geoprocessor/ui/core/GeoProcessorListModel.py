# GeoProcessorListModel - data model for the GeoProcessor command list
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

import logging
import typing

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QModelIndex

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand


class GeoProcessorListModel(QtCore.QAbstractListModel):
    """
    Model for GeoProcessor command list.
    The model is used by the CommandListWidget's QListWidget to interact with the Command list via GeoProcessorListView.

    See "Model/View Programming":  https://doc.qt.io/qt-5/model-view-programming.html
    See "QAbstractListModel":  https://doc.qt.io/qtforpython/PySide2/QtCore/QAbstractListModel.html
    """

    def __init__(self, gp, *args, **kwargs):
        """
        Initialize an instance of the model
        """
        super(GeoProcessorListModel, self).__init__(*args, **kwargs)
        self.gp = gp

        # TODO smalers 2020-01-19 data model should not need any knowledge of the UI component,
        # use a listener to notify of changes
        # self.commands_CommandsListWidget = commands_CommandListWidget

        # Listeners for model changes
        self.model_listeners = []

        # Add the command list widget as a listener to be notified of changes made in this class
        # - this is mainly so that the numbered list on left and gutter on right can be adjusted
        # self.command_list_view.add_model_listener(self)

    def __len__(self) -> int:
        """
        Return the length of the data model, which is the number of commands.

        Returns:
            Number of commands in the data model.
        """
        if self.gp is None:
            return 0
        elif self.gp.commands is None:
            return 0
        else:
            return len(self.gp.commands)

    def add_model_listener(self, listener) -> None:
        """
        Add a listener to be notified when the model changes, for example when commands are deleted or inserted.
        The CommandListWidget should listen so that the UI components can be updated.

        Args:
            listener: object that will listen for events from command list widget, and implement the following
               methods in the listener instance:
                    list_model_clear_all_commands() - when clear_call_commands() has been completed
                    list_model_indent_change() - when decrease_indent_command_string() or
                        indent_command_string() have been completed
                    list_model_insert_commands() - when insert_commands*() as been completed
                    list_model_read_command_file() - when read_command_file() has been completed
                    list_model_clear_selected_commands() - when clear_selected_commands() has been completed

        Returns:
            None
        """
        if listener is None:
            return
        self.model_listeners.append(listener)

    def clear_all_commands(self) -> None:
        """
        Called when 'Clear Commands' button is pressed in
        CommandListWidget. Removes all commands from GeoProcessor.

        Returns:
            None
        """
        if len(self.gp.commands) == 0:
            # No need to do anything
            return
        logger = logging.getLogger(__name__)
        delete_row = 0
        delete_count = len(self.gp.commands)
        delete_row_last = delete_row + delete_count - 1
        logger.info("Inside clear_all_commands, removing commands from table model delete_row=" +
                    str(delete_row) + " delete_count=" +
                    str(delete_count) + " delete_row_last=" + str(delete_row_last))
        # Tell the list model which rows will be removed
        self.beginRemoveRows(QModelIndex(), delete_row, delete_row_last)
        # Remove them from the data
        self.gp.commands.clear()
        # Tell the list model that they have been removed - this will update the command list
        self.endRemoveRows()
        # Tell other listeners that the commands have been removed
        self.notify_listeners_about_clear_all_commands()

    def clear_selected_commands(self, selected_indices: [int] or [QModelIndex]) -> None:
        """
        Called when 'Clear Commands' button is pressed and commands are individually selected from the command list.
        Remove the selected commands from the command list in the GeoProcessor.

        Args:
            selected_indices: A list of int or QModelIndex containing the index of
                the selected commands to remove from GeoProcessor commands list

        Returns:
            None
        """
        # Make sure that selected_indices is [int]
        for i in range(len(selected_indices)):
            if isinstance(selected_indices[i], QModelIndex):
                selected_indices[i] = selected_indices[i].row()
            # Else the list already contains integers

        size = len(selected_indices)

        # Figure out if the indices are sequential, can remove the rows with one call
        # - TODO smalers 2020-01-19 best performance might be if groups of sequential
        rows_sequential = True  # Default for short list
        index_prev = -1
        for i in range(size):
            index_i = selected_indices[i]
            if index_prev < 0:
                # Should only occur for the first value
                index_prev = index_i
                continue
            else:
                if index_i != (index_prev + 1):
                    # Rows are not sequential
                    rows_sequential = False
                    break
                else:
                    # Rows are sequential - save the index as previous for the next loop
                    index_prev = index_i

        if rows_sequential:
            # Can call the model's built-in method
            self.removeRows(selected_indices[0], len(selected_indices), QtCore.QModelIndex())
        else:
            # Remove in reverse order so that commands are removed from the end of the list to the front,
            # which prevents the list from getting out of order when removing commands.
            # Each removal causes some overhead.
            model_index = QtCore.QModelIndex()
            for i in reversed(range(len(selected_indices))):
                self.removeRows(selected_indices[i], 1, model_index)

        # Tell other listeners that the commands have been removed
        # - this is done once so hopefully not a bit performance hit
        self.notify_listeners_about_clear_selected_commands(selected_indices)

    # def data(self, index: QtCore.QModelIndex, role: Qt.DisplayRole):
    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        """
        Method required by QtCore.QAbstractListModel.
        Return the data object at the given index.
        Args:
            index: data model row for display
            role: indicates role for data request

        Returns:
            data object to display, the command string
        """
        debug = False
        if debug:
            logger = logging.getLogger(__name__)
            logger.info("Inside data, index.row()=" + str(index.row()))
        if role == Qt.DisplayRole:
            # Return the command as text to display
            command = self.gp.commands[index.row()]
            # Return the text to display, with indentation
            return str(command)

    def decrease_indent_command_string(self, selected_indices: [int]) -> None:
        """
        Update the GeoProcessor command list to remove white space in front of the
        given command string in order to decrease the indent.
        Then update the command list widget to reflect in the user interface
        changes made in GeoProcessor.

        Args:
            selected_indices: A list of integers containing the index of the
                selected commands to decrease indent of in GeoProcessor

        Returns:
            None
        """
        if (selected_indices is None) or (len(selected_indices) == 0):
            return
        for i in selected_indices:
            self.gp.decrease_indent_command_string(i)
        # Update the CommandListWidget to reflect decreased indent commands
        # self.update_command_list_ui()
        # Emit signal to trigger repaint
        top_left = self.createIndex(0, 0)
        bottom_right = self.createIndex((len(self.gp) - 1), 0)
        self.dataChanged.emit(top_left, bottom_right)
        # Notify listeners
        self.notify_listeners_about_indent_change()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """
        Method required by QtCore.QAbstractListModel.
        Indicate the behavior of the list item.

        Args:
            index:  Row index of interest.

        Returns:
            Flags indicating the behavior of the row, from UI perspective.
        """
        return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        """
        Method required by QtCore.QAbstractListModel.
        Args:
            section:
            orientation:
            role:

        Returns:

        """
        pass

    def indent_command_string(self, selected_indices: [int]) -> None:
        """
        Update the GeoProcessor command list to add white space in the front of the
        given command string in order to increase the indent.
        Then update the command list widget to reflect changes
        made in GeoProcessor.

        Args:
            selected_indices: A list of integers representing the index of the
                selected commands to be indented in GeoProcessor

        Returns:
            None
        """
        if (selected_indices is None) or (len(selected_indices) == 0):
            return
        for i in selected_indices:
            self.gp.indent_command_string(i)
        # Update the CommandListWidget UI to reflect indented commands
        # self.update_command_list_ui()
        # Emit signal to trigger repaint
        top_left = self.createIndex(0, 0)
        bottom_right = self.createIndex((len(self.gp) - 1), 0)
        self.dataChanged.emit(top_left, bottom_right)
        # Notify listeners
        self.notify_listeners_about_indent_change()

    def insert_command_at_index(self, command: AbstractCommand, index: int) -> None:
        """
        Insert a command string at the specified index.
        This function also calls the data model methods to indicate begin and end of the insert.

        Args:
            command_string (str): Command string to be inserted to the command file.
            index (int): Index to insert.

        Returns:
            None
        """
        # Insert the command in the model
        commands = [command]
        self.insert_commands_at_index(commands, index)
        # Don't notify listeners because called method above will do it

    def insert_commands_at_index(self, commands: [AbstractCommand], insert_index: int) -> None:
        """
        Insert one or more command strings at the specified index.
        This function also calls the data model methods to indicate begin and end of the insert.

        Args:
            command_strings ([str]): Command strings to be inserted to the command file.
            insert_index (int): Index to insert.  The first command will be inserted at this position.

        Returns:
            None
        """
        logger = logging.getLogger(__name__)
        # Insert the command in the model
        insert_row = insert_index
        insert_count = len(commands)
        insert_row_last = insert_row + insert_count - 1
        logger.debug("Inserting commands insert_row=" + str(insert_row) + " insert_count=" +
                     str(insert_count) + " insert_row_last=" + str(insert_row_last))
        self.beginInsertRows(QtCore.QModelIndex(), insert_row, insert_row_last)
        for command in commands:
            # TODO smalers 2020-01-19 previously was operating on strings, now operating on command class
            #self.gp.add_command_at_index(command, insert_index)
            self.gp.commands.insert(insert_index, command)
            logger.debug("Inserting command [" + str(insert_index) + "]: " + command.command_string)
            insert_index += 1
        self.endInsertRows()

        # Notify listeners
        self.notify_listeners_about_insert_commands_at_index(insert_index)

    def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        """
        Method required by QtCore.QAbstractListModel.
        This method is typically not called in the table model because the following sequence is used in other code:
        1. beginInsertRows()
        2. add data to the GeoProcessor command list
        3. endInsertRows()
        Args:
            row:
            count:
            parent:

        Returns:

        """
        # See:  https://www.riverbankcomputing.com/pipermail/pyqt/2015-December/036666.html
        # This only inserts blank data in the view object
        # First indicate rows to be inserted
        logger = logging.getLogger(__name__)
        last_row = row + count - 1
        logger.info("Inside insertRows, row=" + str(row) + " count=" + str(count) + " last_row=" + str(last_row))
        self.beginInsertRows(QModelIndex(), row, last_row)
        # The following causes a call to data for for inserted/visible rows
        self.endInsertRows()
        return True

    def notify_listeners_about_clear_all_commands(self) -> None:
        """
        Notify listeners added with 'add_model-listener' that all commands have been cleared.

        Returns:
            None
        """
        for listener in self.model_listeners:
            listener.list_model_clear_all_commands(self)

    def notify_listeners_about_clear_selected_commands(self, selected_indices: [int]) -> None:
        """
        Notify listeners added with 'add_model-listener' that selected commands have been cleared.

        Returns:
            None
        """
        for listener in self.model_listeners:
            listener.list_model_clear_selected_commands(self, selected_indices)

    def notify_listeners_about_indent_change(self) -> None:
        """
        Notify listeners added with 'add_model-listener' that some indentation has changed.

        Returns:
            None
        """
        for listener in self.model_listeners:
            listener.list_model_indent_change(self)

    def notify_listeners_about_insert_commands_at_index(self, insert_index: int) -> None:
        """
        Notify listeners added with 'add_model-listener' that commands have been inserted.

        Returns:
            None
        """
        for listener in self.model_listeners:
            listener.list_model_insert_commands_at_index(self, insert_index)

    def notify_listeners_about_read_command_file(self, cmd_filepath: str) -> None:
        """
        Notify listeners added with 'add_model-listener' that a command file has been read.

        Args:
            cmd_filepath:
                Full path of the command file that was read.
        Returns:
            None
        """
        for listener in self.model_listeners:
            listener.list_model_read_command_file(self, cmd_filepath)

    def read_command_file(self, cmd_filepath) -> None:
        """
        Read the command file and populate the table model, triggering updates to the UI components.

        Args:
            cmd_filepath:
                Path to the command file to read.
        Returns:
            None.
        """
        logger = logging.getLogger(__name__)
        # If the commands file currently contains commands, remove in the UI and commands
        # - this will trigger an initial notification
        self.clear_all_commands()
        # The Qt convention is to notify the model base class how many items will be inserted, then insert.
        # Therefore, read the command count first.
        num_commands = self.gp.read_command_file(cmd_filepath, create_commands=False)
        insert_row = 0
        insert_count = num_commands
        insert_row_last = insert_row + insert_count - 1
        logger.info("Inserting commands insert_row=" + str(insert_row) + " insert_count=" +
                    str(insert_count) + " insert_row_last=" + str(insert_row_last))
        self.beginInsertRows(QtCore.QModelIndex(), insert_row, insert_row_last)
        # Now read and instantiate the commands in the GeoProcessor, and hence this table model
        self.gp.read_command_file(cmd_filepath)
        # Update the list model
        self.endInsertRows()

        # Notify listeners that the command file was read
        self.notify_listeners_about_read_command_file(cmd_filepath)

    def removeRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
        """
        Method required by QtCore.QAbstractListModel.
        Args:
            row:
            count:
            parent:

        Returns:

        """
        debug = True
        if debug:
            logger = logging.getLogger(__name__)
        if count == 0:
            # No need to do anything
            return True
        last_row = row + count - 1  # 0-index
        # Tell Qt list which rows will be removed
        self.beginRemoveRows(QModelIndex(), row, last_row)
        # Remove the rows from the end so that the positions do not get out of sync
        for i in reversed(range(row, (row + count), 1)):
            if debug:
                logger.debug("Removing command [" + str(i) + "]")
            del self.gp.commands[i]
        # Tell Qt list which rows have been removed
        self.endRemoveRows()
        return True

    def rowCount(self, parent: QModelIndex = ...) -> int:
        """
        Method required by QtCore.QAbstractListModel.
        Return the count of objects under the given index.
        For a list, the index is not used (it is used for hierarchical data structures like trees).

        Args:
            parent:  Index of the parent.

        Returns:
            The length of the list.
        """
        if parent is None:
            pass
        return len(self.gp.commands)

    # TODO smalers 2020-01-20 Not implemented because data editing occurs through the interactions with GeoProcessor
    # def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
