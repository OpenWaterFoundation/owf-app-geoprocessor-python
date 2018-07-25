# Qt utility functions

from PyQt5 import QtWidgets


def new_message_box(message_type, standard_buttons_mask, message, title):
    """
    Create and execute a message box.
    REF: https://www.tutorialspoint.com/pyqt/pyqt_qmessagebox.htm

    Args:
            message_type (str): the type of message box, for example QtWidgets.QMessageBox.Question
            standard_buttons_mask (str): a bitmask indicating the buttons to include in the message box,
                    for example QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            message (str): a message to display in the message box
            title (str) a title for the message box. Appears in the top window bar.

    Return: The clicked button name. See the button_value_dic for more information.
    """

    # Create the Message Box object.
    msg = QtWidgets.QMessageBox()

    # Set the Message Box icon.
    msg.setIcon(message_type)

    # Set the Message Box message text.
    msg.setText(message)

    # Set the Message Box title text.
    msg.setWindowTitle(title)

    # Set the Message Box standard buttons.
    msg.setStandardButtons(standard_buttons_mask)

    # Execute the Message Box and retrieve the clicked button enumerator.
    btn_value = msg.exec_()

    # Return the clicked button Qt type
    return btn_value
