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


class GeoProcessorListModel(object):
    """
    This class acts as a way to interface between the user interface components of
    CommandListWidget.py and the logic being processed by GeoProcessor.py.
    """

    def __init__(self, geoprocessor, command_list_view):
        """
        Initialize the class elements

        Args:
            geoprocessor: The GeoProcessor object from GeoProcessor.py
            command_list_view: The user interface Command List Widget from CommandListWidget.py

        Returns:
            None
        """
        # Initialize the geoprocessor
        self.gp = geoprocessor
        # Add the geoprocessor as a listener to be notified to changes made in this class
        self.gp.add_model_listener(self)

        # Initialize the command list widget
        self.command_list_view = command_list_view
        # Add the command list widget as a listener to be notified of changes made in this class
        self.command_list_view.add_model_listener(self)

    def clear_all_commands(self):
        """
        Called when 'Clear Commands' button is pressed in
        CommandListWidget. Removes all commands from GeoProcessor.

        Returns:
            None
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

        Args:
            selected_indices: A list of integers representing the index of
                the selected commands to remove from GeoProcessor commands list

        Returns:
            None
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

    def command_file_read(self):
        """
        After commands are read in GeoProcessor the following functions
        can be ran in CommandListWidget to update elements of the UI.

        Returns:
            None
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
        Called after the commands have been ran in GeoProcessor.

        Returns:
            None
        """
        # Check for errors or warnings in CommandListWidget and update icons
        # if necessary
        self.command_list_view.update_ui_command_list_errors()
        # Update status of commands
        self.command_list_view.update_ui_status_commands()

    def decrease_indent_command_string(self, selected_indices):
        """
        Update the GeoProcessor command list to remove white space in front of the
        given command string in order to decrease the indent.
        Then update the command list widget to reflect in the user interface
        changes made in GeoProcessor.

        Args:
            selected_indices: A list of integers representing the index of the
                selected commands to decrease indent of in GeoProcessor

        Returns:
            None
        """
        size = len(selected_indices)
        for i in range(0, size):
            index = selected_indices[i]
            self.gp.decrease_indent_command_string(index)
        # Update the CommandListWidget to reflect decreased indent commands
        self.update_command_list_ui()

    def indent_command_string(self,selected_indices):
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
        size = len(selected_indices)
        for i in range(0, size):
            index = selected_indices[i]
            self.gp.indent_command_string(index)
        # Update the CommandListWidget UI to reflect indented commands
        self.update_command_list_ui()

    def new_command_list(self):
        """
        Reset the command list backup in the command list widget in order to
        be able to check if there have been any changes to the command file.

        Returns:
            None
        """
        # Initialize the backup command list for checking if changes were made on exit
        self.command_list_view.set_command_list_backup()

        # Notify the main ui that results should be refreshed
        self.command_list_view.notify_main_ui_listener_refresh_results()

    def run_all_commands(self):
        """
        Run all commands in GeoProcessor

        Returns:
            None
        """
        # Runs the geoprocessor's processor_run_commands function to run the existing commands
        # that exist in the processor.
        print("Running commands in processor...")
        self.gp.run_commands()

    def run_selected_commands(self, selected_indices):
        """
        Run only the selected commands in GeoProcessor

        Args:
            selected_indices: A list of integers representing the index of the
                selected commands to be ran in GeoProcessor

        Returns:
            None
        """
        print("Running selected commands in processor...")
        self.gp.run_selected_commands(selected_indices)

    def update_command_list_backup(self):
        """
        Will update the command list backup command list to reflect
        whatever the current state of the command list is in the CommandListWidget
        class, which is updated whenever changes are made to the command list in
        GeoProcessor

        Returns:
            None
        """
        self.command_list_view.set_command_list_backup()

    def update_command_list_ui(self):
        """
        Update the commands list UI in CommandListWidget

        Returns:
            None
        """
        # Get the current state of the commands list from GeoProcessor
        command_list = self.gp.commands
        # Set the commands list in the CommandListWidget to the updated
        # commands list from GeoProcessor
        self.command_list_view.set_command_list(command_list)
        # Update the commands list UI in CommandListWidget
        self.command_list_view.update_command_list_widget()
