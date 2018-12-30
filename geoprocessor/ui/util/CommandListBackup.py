# CommandListBackup - ?
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
