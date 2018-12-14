
import copy
from PyQt5 import QtWidgets

class CommandListBackup(object):

    """
    This class is used to keep track of the command list to determine if the command file has been
    modified in any way since the previous save, or if it has been returned to the original saved state.
    """

    def __init__(self):

        # Create a new command list QListWidget object
        self.command_list = []

    def command_list_modified(self, command_list):
        """
        Check to see if the command list has been modified since the last save. The last saved
        command list should have been updated by update_command_list()
        :param command_list: the current command_list in geoprocessor
        :return: True if file has been modified, otherwise False
        """

        if len(self.command_list) != len(command_list):
            return True

        size = len(command_list)

        for i in range(0, size):

            text = command_list[i].command_string

            original_text = self.command_list[i]

            if text != original_text:
                return True

        return False

    def update_command_list(self, command_list):
        """
        Update the command list with what is currently saved or opened in geoprocessor
        :param command_list: the command list being saved or opened by geoprocessor
        :return: None
        """

        del self.command_list[:]

        for command in command_list:
            text = command.command_string
            self.command_list.append(text)
