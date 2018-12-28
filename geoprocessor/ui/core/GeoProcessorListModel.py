# GeoProcessorListModel - data model for the GeoProcessor command list
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

class GeoProcessorListModel(object):

    def __init__(self, geoprocessor, command_list_view):
        self.gp = geoprocessor
        self.gp.add_model_listener(self)

        self.command_list_view = command_list_view
        self.command_list_view.add_model_listener(self)

    # def add_element(self, command_string):
    #     """
    #     Add a command to the end of the list
    #     :param command_string:
    #     :return:
    #     """
    #     self.gp.add_command_string(command_string)

    def clear_all_commands(self):
        """
        Called when 'Clear Commands' button is pressed in
        CommandListWidget. Removes all commands from GeoProcessor.
        :return: None
        """
        # Remove all the commands from GeoProcessor
        self.gp.remove_all_commands()
        # Update status of commands
        self.command_list_view.update_ui_status_commands()

    def clear_selected_commands(self, selected_indices):
        """
        Called when 'Clear Commands' button is pressed in
        CommandListWidget and when commands are individually selected from the
        command list. Remove the selected commands from the command list in
        GeoProcessor
        :param selected_indices: A list of integers representing the index of
        the selected commands to remove from GeoProcessor commands list
        :return: None
        """
        size = len(selected_indices)
        # Sort the list in reverse so we remove commands from the bottom of the list up
        # which prevents the list from getting out of order when removing commands
        selected_indices_sorted = sorted(selected_indices, reverse=True)
        for i in range(0, size):
            i_command = selected_indices_sorted[i]
            self.gp.remove_command(i_command)

        # Update status of commands
        self.command_list_view.update_ui_status_commands()

    def command_list_read(self):
        """
        After commands are read in GeoProcessor the following functions
        can be ran in CommandListWidget to update elements of the UI.
        :return: None
        """
        # Get the command list from the GeoProcessor
        command_list = self.gp.commands
        # Initialize the command list array in CommandListWidget
        self.command_list_view.set_command_list(command_list)
        # Initialize the backup command list for checking if changes were made on exit
        self.command_list_view.set_command_list_backup()
        # Add command strings to the command list widget in CommandListWidget
        self.command_list_view.update_command_list_widget()
        # Update the command status
        self.command_list_view.update_ui_status_commands()
        # Enable the 'Run All Commands' and 'Clear Commands' buttons
        # self.command_list_view.enable_buttons()
        self.command_list_view.commands_RunAllCommands_PushButton.setEnabled(True)
        self.command_list_view.commands_ClearCommands_PushButton.setEnabled(True)
        #self.initialize_command_list()
        # Notify the main ui that results should be refreshed
        self.command_list_view.notify_main_ui_listener_refresh_results()

    def command_list_ran(self):
        """
        Called after the commands have been ran in GeoProcessor
        :return: None
        """
        # Check for errors or warnings in CommandListWidget and update icons
        # if necessary
        self.command_list_view.update_ui_command_list_errors()
        # Update status of commands
        self.command_list_view.update_ui_status_commands()

    # def get_command_list(self):
    #
    #     return self.gp.get_command_list()

    def decrease_indent_command_string(self, selected_indices):
        size = len(selected_indices)
        for i in range(0, size):
            index = selected_indices[i]
            self.gp.decrease_indent_command_string(index)
        # Update the CommandListWidget to reflect decreased indent commands
        self.update_command_list_ui()

    def indent_command_string(self,selected_indices):
        """
        Indent the selected commands in the GeoProcessor
        :param selected_indices: A list of integers representing the index of the
        selected commands to be indented in GeoProcessor
        :return: None
        """
        size = len(selected_indices)
        for i in range(0, size):
            index = selected_indices[i]
            self.gp.indent_command_string(index)
        # Update the CommandListWidget UI to reflect indented commands
        self.update_command_list_ui()

    def run_all_commands(self):
        """
        Run all commands in GeoProcessor
        :return: None
        """
        # Runs the geoprocessor's processor_run_commands function to run the existing commands
        # that exist in the processor.
        print("Running commands in processor...")
        self.gp.run_commands()

    def run_selected_commands(self, selected_indices):
        """
        Run only the selected commands in GeoProcessor
        :param selected_indices: A list of integers representing the index of the
        selected commands to be ran in GeoProcessor
        :return:
        """
        print("Running selected commands in processor...")
        self.gp.run_selected_commands(selected_indices)

    # def initialize_command_list(self):
    #
    #     self.command_list_view.initialize_command_list_backup()
    #     self.command_list_view.update_command_list_widget()
    #     self.command_list_view.enable_buttons()

    def update_command_list_backup(self):
        """
        Will update the command list backup command list to reflect
        whatever the current state of the command list is in the CommandListWidget
        class, which is updated whenever changes are made to the command list in
        GeoProcessor
        :return: None
        """
        self.command_list_view.set_command_list_backup()

    def update_command_list_ui(self):
        """
        Update the commands list UI in CommandListWidget
        :return: None
        """
        # Get the current state of the commands list from GeoProcessor
        command_list = self.gp.commands
        # Set the commands list in the CommandListWidget to the updated
        # commands list from GeoProcessor
        self.command_list_view.set_command_list(command_list)
        # Update the commands list UI in CommandListWidget
        self.command_list_view.update_command_list_widget()
