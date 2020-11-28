# qt_util - Qt utility functions
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
from typing import Optional

from PyQt5 import QtGui, QtWidgets

import geoprocessor.util.app_util as app_util
import geoprocessor.util.string_util as string_util


def from_utf8(s):
    """
    Function to convert strings from UTF8 representation to Python string.
    The following code was autogenerated by Qt Designer:

    try:
        _fromUtf8 = lambda s: s
    except AttributeError:
        def _fromUtf8(s):
            return s

    The above generates warnings in PyCharm and web information indicate to just use a function,
    so this is the function.

    Args:
        s (str): string to convert.

    Returns:
        A string converted from UTF-8.
    """
    return s


def get_table_rows_from_indexes(indexes: [int]) -> [int]:
    """
    Get the list of unique rows from a list of indexes, for example, indexes selected in a table.

    Args:
        indexes: list of indexes from Qt table

    Returns:
        List of rows corresponding to the indexes, without duplicates.
    """
    rows = []
    for index in indexes:
        if index.isValid():
            # See if index is already in the list
            found = False
            row = index.row()
            for irow in rows:
                if irow == row:
                    found = True
                    break
            if not found:
                rows.append(row)

    return rows


def info_message_box(message: str or [str], app_name: str = None, title: str = "Information") -> int:
    """
    Display an information message dialog.

    Args:
        message (str or [str]): Message string.
        app_name (str): Application name to use in dialog title
            (default if None is to get from app_util.get_property("ProgramName")
        title (str): Title for dialog.

    Returns:
        Which button was selected as QtWidgets.QMessageBox.Ok (only one button is available).
    """
    if app_name is None:
        # Use the application name from properties
        app_name = app_util.get_property("ProgramName")
    if app_name is not None:
        # Use the application name in the title
        title = app_name + " - " + title
    if isinstance(message, list):
        # Convert the list to a string
        message = string_util.list_to_string(message)
    message_box = new_message_box(QtWidgets.QMessageBox.Information, QtWidgets.QMessageBox.Ok, message, title)
    return message_box


def new_message_box(message_type: QtWidgets.QMessageBox.Icon,
                    standard_buttons_mask: QtWidgets.QMessageBox.StandardButton, message: str, title: str) -> int:
    """
    Create and execute a message box, returning an indicator for the button that was selected.
    REF: https://www.tutorialspoint.com/pyqt/pyqt_qmessagebox.htm

    Args:
            message_type (QIcon): the type of message box, for example QtWidgets.QMessageBox.Question
            standard_buttons_mask (StandardButton): a bitmask indicating the buttons to include in the message box,
                    for example QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            message (str): a message to display in the message box
            title (str) a title for the message box. Appears in the top window bar.

    Returns:
        The clicked button name. See the button_value_dic for more information.
    """

    # Create the Message Box object.
    message_box = QtWidgets.QMessageBox()

    # Set the Message Box icon.
    message_box.setIcon(message_type)

    # Set the Message Box message text.
    message_box.setText(message)

    # Set the Message Box title text.
    message_box.setWindowTitle(title)

    # Set the Message Box standard buttons.
    message_box.setStandardButtons(standard_buttons_mask)

    # Set the icon
    # - icon path should use Qt / notation
    icon_path = app_util.get_property("ProgramIconPath").replace('\\', '/')
    # logger = logging.getLogger(__name__)
    # logger.debug("icon path=\"" + str(icon_path) + "\"")
    # print("Icon path='" + icon_path + "'")
    # message_box.setWindowIcon(QtGui.QIcon(icon_path))
    message_box.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(icon_path)))

    # Execute the Message Box and retrieve the clicked button enumerator.
    btn_value = message_box.exec_()

    # Return the clicked button Qt type
    return btn_value


def print_application_stylesheet():
    """
    Print the application's stylesheet for common components that are used.

    Returns:
        None
    """
    logger = logging.getLogger(__name__)
    # TODO smalers 2020-01-15 is there a way to get styles without instantiating an instance of a component?
    # - printing styles only seems to print when additional styles have been set beyond the defaults

    # Create some objects
    qpushbutton = QtWidgets.QPushButton()
    qmenu = QtWidgets.QMenu()

    # Print the stylesheet
    logger.info('Properties for common Qt elements follows (from stylesheets)...')
    logger.info(str(qpushbutton.styleSheet()))
    logger.info('...done printing properties from common Qt components (from stylesheets)')

    # Print the properties directly
    logger.info('Properties for common Qt elements follows (from direct calls)...')
    logger.info("QMenu font family: " + str(qmenu.fontInfo().family()))
    logger.info("QMenu font size (points): " + str(qmenu.fontInfo().pointSize()))
    logger.info("QMenu font size (points): " + str(qmenu.font().pointSize()))
    logger.info("QPushButton font family: " + str(qpushbutton.fontInfo().family()))
    logger.info("QPushButton font size (points): " + str(qpushbutton.font().pointSize()))
    logger.info('...done printing properties for common Qt elements (from direct calls).')


def question_box(message: str, app_name: str = None, title: str = "Question") -> int:
    """
    Display an information message dialog.

    Args:
        message (str): Message string.
        app_name (str): Application name to use in dialog title
            (default if None is to get from app_util.get_property("ProgramName")
        title (str): Title for dialog.

    Returns:
        Which button was selected as QtWidgets.QMessageBox.Ok (only one button is available).
    """
    if app_name is None:
        # Use the default from application property
        app_name = app_util.get_property("ProgramName")
    if app_name is not None:
        # Use the application name in the title (otherwise use the title as passed in)
        title = app_name + " - " + title
    message_box = new_message_box(QtWidgets.QMessageBox.Question,
                                  QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel, message, title)
    return message_box


# TODO smalers 2019-01-19 need to figure out what this really does.
def translate(context: str, text: str, disambig: Optional[str]) -> str:
    """
    Function to translate a string between human languages?
    The following code was autogenerated by Qt Designer:

    try:
        _encoding = QtWidgets.QApplication.UnicodeUTF8
        def _translate(context, text, disambig):
            return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
    except AttributeError:
        def _translate(context, text, disambig):
            return QtWidgets.QApplication.translate(context, text, disambig)

    The above generates warnings in PyCharm and web information indicate to just use a function,
    so this is the function.

    Args:
        context (str):  ? - need to figure out
        text (str):  text to translate
        disambig (str): ? - need to figure out

    Returns:
        A string converted from UTF-8.
    """
    try:
        _encoding = QtWidgets.QApplication.UnicodeUTF8
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
    except AttributeError:
        return QtWidgets.QApplication.translate(context, text, disambig)


def warning_message_box(message: str, app_name: str = None, title: str = "Warning") -> int:
    """
    Display a warning message dialog.

    Args:
        message (str): Message string.
        app_name (str): Application name to use in dialog title
            (default if None is to get from app_util.get_property("ProgramName")
        title (str): Title for dialog.

    Returns:
        Which button was selected as QtWidgets.QMessageBox.Ok (only one button is available).
    """
    if app_name is None:
        app_name = app_util.get_property("ProgramName")
    if app_name is not None:
        # Use the application name in the title
        title = app_name + " - " + title
    message_box = new_message_box(QtWidgets.QMessageBox.Warning, QtWidgets.QMessageBox.Ok, message, title)
    return message_box
