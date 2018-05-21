from geoprocessor.ui.app.GeoProcessorUI_Design import Ui_MainWindow
import geoprocessor.util.io_util as io_util
import geoprocessor.util.command_util as command_util
from geoprocessor.ui.commands.layers.ReadGeoLayerFromGeoJSON_Editor import Ui_Dialog as ReadGeoLayerFromGeoJSON_Editor
from PyQt4 import QtGui, QtCore
import functools
import webbrowser
import geoprocessor.ui.util.config as config


class GeoProcessorUI(Ui_MainWindow):

    def __init__(self, window, geoprocessor):
        Ui_MainWindow.__init__(self)
        self.setupUi(window)

        # The count of commands within the Commands_List widget (total).
        self.total_commands = 0

        # The count of commands within the Commands_List widget (selected).
        self.selected_commands = 0

        # Ingest the GeoProcessor object.
        self.gp = geoprocessor

        # The most recent file save location.
        self.saved_file = None

        # The URL to the user documentation main page
        self.user_doc_url = config.user_doc_url

        # CommandDialogFactory
        self.command_dialog_factory_dic = {"READGEOLAYERFROMGEOJSON": ReadGeoLayerFromGeoJSON_Editor()}

        # Listeners - listens for a change event.

        # Listen for a change in item selection within the Commands_List widget.
        self.Commands_List.itemSelectionChanged.connect(self.update_command_count)
        # Listen for a change in item selection within the Results_GeoLayers_Table widget.
        self.Results_GeoLayers_Table.itemSelectionChanged.connect(self.update_results_count)
        # Listen for a change in item selection within the Results_Tables_Table widget.
        self.Results_Tables_Table.itemSelectionChanged.connect(self.update_results_count)
        # Listen for a change in item selection within the Results_Maps_Table widget.
        self.Results_Maps_Table.itemSelectionChanged.connect(self.update_results_count)
        # Listen for a change in item selection within the Results_OutputFiles_Table widget.
        self.Results_OutputFiles_Table.itemSelectionChanged.connect(self.update_results_count)

        # Button connections - connects the buttons to their appropriate actions.

        # Connect the Run All Commands button.
        self.Commands_RunAll_Button.clicked.connect(self.run_commands, False)
        # Connect the Clear Commands button.
        self.Commands_Clear_Button.clicked.connect(self.clear_commands_from_button)
        # Connect the Run Selected Commands button.
        self.Commands_RunSelected_Button.clicked.connect(functools.partial(self.run_commands, True))

        # Menu connections - connects the menu tab buttons to their appropriate actions.

        # Connect the File > Open > Command File menu tab.
        self.File_Open_CommandFile.triggered.connect(self.open_command_file)
        # Connect the File > Save > Commands menu tab.
        self.File_Save_Commands.triggered.connect(self.save_commands)
        # Connect the File > Save > Commands As menu tab.
        self.File_Save_CommandsAs.triggered.connect(self.save_commands_as)
        # Connect the File > Set Working Directory menu tab.
        self.File_SetWorkingDirectory.triggered.connect(self.set_working_directory)
        # Connect the Commands > GeoLayers > Read > ReadGeoLayerFromGeoJSON menu tab.
        self.GeoLayers_Read_ReadGeoLayerFromGeoJSON.triggered.connect(
            functools.partial(self.new_command_editor, "ReadGeoLayerFromGeoJSON"))
        # Connect the Help > View Documentation menu tab.
        self.Help_ViewDocumentation.triggered.connect(self.view_documentation)

        # Other connections

        # Connect right-click of Commands_List widget item.
        self.Commands_List.connect(self.Commands_List, QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
                                   self.open_command_list_right_click_menu)

    def clear_commands_from_button(self):
        """
        Clear one or more of the commands from the Command List widget.

        Return: None
        """

        # If at least one command is selected, remove only the selected commands.
        if self.selected_commands > 0:

            # Set the message box message depending on if 1 item is selected or more than 1 items are selcted.
            if self.selected_commands == 1:
                message_box_message = "Do you want to delete the 1 selected command?"
            else:
                message_box_message = "Do you want to delete the {} selected commands?".format(self.selected_commands)

            # Open a message box to confirm with the user that they want to delete the selected commands.
            response = self.new_message_box("question",
                                             "yes,no",
                                             message_box_message,
                                             "Clear Commands")

            # If the user confirms that they want to delete the selected commands, continue. Otherwise, pass.
            if response.upper() == "YES":

                # Iterate over and remove each selected item (command).
                for selected_item in self.Commands_List.selectedItems():
                    self.Commands_List.takeItem(self.Commands_List.row(selected_item))

        # If no commands are selected, remove all commands.
        else:

            # Open a message box to confirm with the user that they want to delete all of the commands.
            response = self.new_message_box("question",
                                             "yes,no",
                                             "Do you want to delete all of the commands?",
                                             "Clear Commands")

            # If the user confirms that they want to delete all of the commands, continue. Otherwise, pass.
            if response.upper() == "YES":

                # Iterate over and remove all of the items (commands).
                while self.Commands_List.count() > 0:
                    self.Commands_List.takeItem(0)

        # Update the command count and Command_List label to show that commands were deleted.
        self.update_command_count()

    def clear_command_from_rightclick(self):
        """
        Clear the right-clicked command from the Command List widget.

        Return: None
        """

        # Open a message box to confirm with the user that they want to delete the command.
        response = self.new_message_box("question",
                                         "yes,no",
                                         "Do you want to delete this command?",
                                         "Clear Commands")

        # If the user confirms that they want to delete the command, continue. Otherwise, pass.
        if response.upper() == "YES":

            # Get the index of the right-clicked command (item) and remove it from the Command_List widget.
            index_of_item_to_remove = self.Commands_List.currentRow()
            self.Commands_List.takeItem(index_of_item_to_remove)

        # Update the command count and Command_List label to show that commands were deleted.
        self.update_command_count()

    def edit_command_editor(self):
        """
        Opens a dialog box that allows users to edit existing commands.

        Return: None
        """

        # Get the command line string of the right-clicked item in the Commands_List widget.
        cmd_line_string = self.Commands_List.currentItem().text()

        # Get the command name of the command line string. All text before the first open parenthesis.
        command_name = command_util.parse_command_name_from_command_string(cmd_line_string)

        # Get the parameter string of the command line string. All text inside parenthesis.
        parameter_string = command_util.parse_parameter_string_from_command_string(cmd_line_string)

        # Convert the parameter string into a list of key value pairs. [ParamterName1=ParmaterValue1, ... ]
        parameter_key_values = command_util.parse_parameter_string_into_key_value_pairs(parameter_string)

        # Convert hte list of key value pairs into a parameter dictionary. {ParameterName1: ParameterValue1}
        input_parameter_dictionary = command_util.parse_key_value_pairs_into_dictionary(parameter_key_values)

        # Create a QDialog window instance.
        d = QtGui.QDialog()

        # Create the dialog design instance for the specific input command.
        ui = self.command_dialog_factory_dic[command_name.upper()]

        # Apply the command-specific dialog design to the QDialog window.
        ui.setupUi(d)

        # Update the dialog window with the parameter values included in the cmd_line_string.
        # Iterate over the dictionary entries of the input_parameter_dictionary.
        # Each entry represents a parameter.
        # Key: parameter name
        # Value: existing parameter value
        for input_parameter_name, input_parameter_value in input_parameter_dictionary.iteritems():

            # Iterate over the dictionary entries of the default command_parameter_dictionary within the dialog design
            # instance object.
            # Each entry represents a parameter.
            # Key: parameter name
            # Value: default parameter value
            for default_parameter_name, default_parameter_value in ui.command_parameter_values.iteritems():

                # If a command parameter is NOT set to default in the cmd_line_string, set the
                # parameter value within the dialog design instance object to the parameter value indicated by the
                # cmd_line_string.
                if input_parameter_name == default_parameter_name:
                    ui.command_parameter_values[default_parameter_name] = input_parameter_value

        # Update the dialog window with the parameter values from the command line string.
        print input_parameter_dictionary
        print ui.command_parameter_values
        ui.refresh()

        # If the "OK" button is clicked within the dialog window, continue.
        # Else, if the "Cancel" button is clicked, do nothing.
        if d.exec_():
            # Get the index of the selected command (item).
            index = self.Commands_List.currentRow()

            # Remove the original command (item) from the Command_List widget.
            self.Commands_List.takeItem(index)

            # Get the updated command string from the dialog window.
            command_string = ui.CommandDisplay_View_TextBrowser.toPlainText()

            # Add the command string to the Command_List widget in the same location as the previous command item.
            self.Commands_List.insertItem(index, command_string)

            # Update the command count and Command_List label to show that a command was added to the workflow.
            self.update_command_count()

    def new_command_editor(self, command_name):
        """
        Opens the dialog window for the selected command. If the users clicks "OK" within the dialog window, the
        command string (with the desired parameter values) is added to the Command_List widget within the Main Window
        user interface. Other UI components are also updated - including the total and selected command count, the
        Command_List Widget Label, and the GeoProcessor's list of commands.

        Args:
            command_name (str): the name of the command

        Returns: None
        """

        # Create a QDialog window instance.
        d = QtGui.QDialog()

        # Create the dialog design instance for the specific input command.
        ui = self.command_dialog_factory_dic[command_name.upper()]

        # Apply the command-specific dialog design to the QDialog window.
        ui.setupUi(d)

        # If the "OK" button is clicked within the dialog window, continue.
        # Else, if the "Cancel" button is clicked, do nothing.
        if d.exec_():

            # Get the command string from the dialog window.
            command_string = ui.CommandDisplay_View_TextBrowser.toPlainText()

            # Add the command string to the Command_List widget.
            self.Commands_List.addItem(command_string)

            # Update the command count and Command_List label to show that a command was added to the workflow.
            self.update_command_count()

    @staticmethod
    def new_message_box(message_type, standard_buttons, message, title):
        """
        Create and execute a message box.
        REF: https://www.tutorialspoint.com/pyqt/pyqt_qmessagebox.htm

        Args:
            message_type (str): the type of message box. Choose one of the following (question, information, warning,
                critical)
            standard_buttons (str): the buttons to include in the message box (available options are in the buttons_dic
                dictionary. More options can be added to the dictionary as needed.
            message (str): a message to display in the message box
            title (str) a title for the message box. Appears in the top window bar.

        Return: The clicked button name. See the button_value_dic for more information.
        """

        # Relates the input variable TYPE to the appropriate QtGui Icon for the message box.
        icon_dic = {"QUESTION": QtGui.QMessageBox.Question,
                    "INFORMATION": QtGui.QMessageBox.Information,
                    "WARNING": QtGui.QMessageBox.Warning,
                    "CRITICAL": QtGui.QMessageBox.Critical}

        # Relates the input variable STANDARD_BUTTONS to the appropriate QtGui buttons for the message box.
        buttons_dic = {"YES,NO": QtGui.QMessageBox.Yes | QtGui.QMessageBox.No}

        # Relates the enumerated clicked button value to the clicked button name.
        # REF: http://ftp.ics.uci.edu/pub/centos0/ics-custom-build/BUILD/PyQt-x11-gpl-4.7.2/doc/html/
        # qdialogbuttonbox.html#StandardButton-enum
        button_value_dic = {16384: "Yes",
                            65536: "No"}

        # Create the Message Box object.
        msg = QtGui.QMessageBox()

        # Set the Message Box icon.
        msg.setIcon(icon_dic[message_type.upper()])

        # Set the Message Box message text.
        msg.setText(message)

        # Set the Message Box title text.
        msg.setWindowTitle(title)

        # Set the Message Box standard buttons.
        msg.setStandardButtons(buttons_dic[standard_buttons.upper()])

        # Execute the Message Box and retrieve the clicked button enumerator.
        btn_value = msg.exec_()

        # Return the clicked button common name.
        return button_value_dic[btn_value]

    def open_command_file(self):
        """
        Opens a new command file. Each line of the command file is a separate item in the Command_List QList Widget.

        Returns: None
        """

        # Clear the items from the current Command_List widget.
        self.Commands_List.clear()

        # A browser window will appear to allow the user to browse to the desired command file. The absolute pathname
        # of the command file is added to the cmd_filepath variable.
        cmd_filepath = QtGui.QFileDialog.getOpenFileName()

        # Open the command file.
        with open(cmd_filepath, 'r') as comand_file:

            # Iterate over the lines of the command file.
            for line in comand_file:

                # Strip the line of any excess whitespace and add it as an item to the Command_List widget.
                self.Commands_List.addItem(line.strip())

        # Update the command count and Command_List label to show that new commands were added to the workflow.
        self.update_command_count()

    def open_command_list_right_click_menu(self, q_pos):
        """
        Open the Command_List widget right-click menu.
        REF: https://stackoverflow.com/questions/31380457/add-right-click-functionality-to-listwidget-in-pyqt4?
        utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

        Arg:
            q_pos: The position of the right-click. Updated automatically within interface. Do not need to manually
                pass a value to this variable. Used to determine where to display the popup menu.

        Return: None
        """

        # Create the Qt Menu object.
        self.rightClickMenu = QtGui.QMenu()

        # Add the menu options to the right-click menu.
        menu_item_edit_command = self.rightClickMenu.addAction("Edit Command")
        menu_item_delete_command = self.rightClickMenu.addAction("Delete Command")

        # Connect the menu options to the appropriate actions.
        self.Commands_List.connect(menu_item_edit_command, QtCore.SIGNAL("triggered()"), self.edit_command_editor)
        self.Commands_List.connect(menu_item_delete_command, QtCore.SIGNAL("triggered()"),
                                   self.clear_command_from_rightclick)

        # Set the position on the right-click menu to appear at the click point.
        parent_pos = self.Commands_List.mapToGlobal(QtCore.QPoint(0, 0))
        self.rightClickMenu.move(parent_pos + q_pos)

        # Display the right-click menu.
        self.rightClickMenu.show()

    def populate_results_tables(self):
        """
        Populates the Results tables of the UI to reflect the existing geolayers, tables, maps, output files and
        properties created/within the GeoProcessor.

        Return: None
        """

        # Remove items from the Results GeoLayers table (from a previous run).
        self.Results_GeoLayers_Table.setRowCount(0)

        # Remove items from the Results Tables table (from a previous run).
        self.Results_Tables_Table.setRowCount(0)

        # Remove items from the Results Maps table (from a previous run).
        self.Results_Maps_Table.setRowCount(0)

        # Remove items from the Results Output Files table (from a previous run).
        self.Results_OutputFiles_Table.setRowCount(0)

        # Remove items from the Results Properties table (from a previous run).
        self.Results_Properties_Table.setRowCount(0)

        # Populate the Results GeoLayers Table.
        # Iterate through all of the GeoLayer objects in the GeoProcessor.
        for geolayer in self.gp.geolayers:

            # Get the index of the next available row in the table. Add a new row to the table.
            new_row_index = self.Results_GeoLayers_Table.rowCount()
            self.Results_GeoLayers_Table.insertRow(new_row_index)

            # Retrieve the GeoLayer's GeoLayer ID and set as the attribute for the GeoLayer ID column.
            self.Results_GeoLayers_Table.setItem(new_row_index, 0, QtGui.QTableWidgetItem(geolayer.id))

            # Retrieve the GeoLayer's geometry and set as the attribute for the Geometry column.
            self.Results_GeoLayers_Table.setItem(new_row_index, 1, QtGui.QTableWidgetItem(geolayer.get_geometry()))

            # Retrieve the number of features within the GeoLayer and set as the attribute for the Feature Count column.
            self.Results_GeoLayers_Table.setItem(new_row_index, 2,
                                                 QtGui.QTableWidgetItem(str(geolayer.get_feature_count())))

            # Retrieve the GeoLayer's CRS and set as the attribute for the Coordinate Reference System column.
            self.Results_GeoLayers_Table.setItem(new_row_index, 3, QtGui.QTableWidgetItem(geolayer.get_crs()))

        # Populate the Results Tables Table.
        # Iterate through all of the Table objects in the GeoProcessor.
        for table in self.gp.tables:

            # Get the index of the next available row in the table. Add a new row to the table.
            new_row_index = self.Results_Tables_Table.rowCount()
            self.Results_Tables_Table.insertRow(new_row_index)

            # Retrieve the Tables's Table ID and set as the attribute for the Table ID column.
            self.Results_Tables_Table.setItem(new_row_index, 0, QtGui.QTableWidgetItem(table.id))

            # Retrieve the number of columns in the Table and set as the attribute for the Column Count column.
            self.Results_Tables_Table.setItem(new_row_index, 1,
                                              QtGui.QTableWidgetItem(str(table.count(returnCol=True))))

            # Retrieve the number of rows in the Table and set as the attribute for the Row Count column.
            self.Results_Tables_Table.setItem(new_row_index, 2,
                                              QtGui.QTableWidgetItem(str(table.count(returnCol=False))))

        # TODO egiles 2018-05-14 Populate the Results Maps Table

        # Populate the Results Output Files Table
        # Iterate through all of the Output Files in the GeoProcessor.
        for output_file in self.gp.output_files:

            # Get the index of the next available row in the table. Add a new row to the table.
            new_row_index = self.Results_OutputFiles_Table.rowCount()
            self.Results_OutputFiles_Table.insertRow(new_row_index)

            # Retrieve the absolute pathname of the output file and set as the attribute for the Output File column.
            self.Results_OutputFiles_Table.setItem(new_row_index, 0, QtGui.QTableWidgetItem(output_file))

            # Get the extension of the output file.
            output_file_ext = io_util.get_extension(output_file)

            # A dictionary that relates common file extensions to the appropriate file name.
            extension_dictionary = {'.xlsx': 'Microsoft Excel Open XML Format Spreadsheet',
                                    '.geojson': 'GeoJSON',
                                    '.xls': 'Microsoft Excel 97-2003 Worksheet'}

            # Retrieve the output file type and set as the attribute for the File Type column. If h
            if output_file_ext in extension_dictionary.keys():
                self.Results_OutputFiles_Table.setItem(new_row_index, 1,
                                                       QtGui.QTableWidgetItem(extension_dictionary[output_file_ext]))
            else:
                self.Results_OutputFiles_Table.setItem(new_row_index, 1,
                                                       QtGui.QTableWidgetItem("Unknown"))

        # Populate the Results Properties Table.
        # Iterate through all of the properties in the GeoProcessor.
        for prop_name, prop_value in self.gp.properties.iteritems():

            # Get the index of the next available row in the table. Add a new row to the table.
            new_row_index = self.Results_Properties_Table.rowCount()
            self.Results_Properties_Table.insertRow(new_row_index)

            # Set the property name as the attribute for the Property Name column.
            self.Results_Properties_Table.setItem(new_row_index, 0, QtGui.QTableWidgetItem(prop_name))

            # Set the property value as the attribute for the Property Value column.
            self.Results_Properties_Table.setItem(new_row_index, 1, QtGui.QTableWidgetItem(prop_value))

        # Update the results count and results' tables' labels to show that the results were populated.
        self.update_results_count()

    def run_commands(self, selected=False):
        """
        Runs the commands from the Command_List widget within the GeoProcessor.

        Args:
            selected: Boolean. If FALSE, all commands within Command_List widget are processed. If TRUE, only selected
            commands within Command_List widget are processed.

        Returns:
            None
        """

        # If ALL of the commands should be run, continue.
        if not selected:

            # Update the GeoProcessor's list of commands to include ALL of the commands in the Command_List widget.
            self.update_gp_command_list()

        # If only the SELECTED commands should be run, continue.
        else:

            # Update the GeoProcessor's list of commands to include only the SELECTED commands in the Command_List
            # widget.
            self.update_gp_command_list(selected=True)

        # Runs the geoprocessor's run_commands function to run the existing commands that exist in the processor.
        self.gp.run_commands()

        # After commands have been run, update the UI Results section to reflect the output & intermediary products.
        self.populate_results_tables()

    def save_commands(self):
        """
        Saves the commands to a previously saved file location (overwrite).

        Return: None
        """

        # If there is not a previously saved file location, save the file with the save_command_as function.
        if self.saved_file is None:
            self.save_commands_as()

        # If there is a previously saved file location, continue.
        else:

            # A list to hold each command as a separate string.
            list_of_cmds = []

            # Iterate over the items in the Commands_List widget.
            for i in range(self.Commands_List.count()):

                # Add the command string text ot the list_of_cmds list.
                list_of_cmds.append(self.Commands_List.item(i).text())

            # Join all of the command strings together (separated by a line break).
            all_commands_string = '\n'.join(list_of_cmds)

            # Write the commands to the previously saved file location (overwrite).
            file = open(self.saved_file, 'w')
            file.write(all_commands_string)
            file.close()

    def save_commands_as(self):
        """
        Saves the commands to a file.

        Return: None
        """

        # TODO egiles 2018-16-05 Discuss with Steve about line breaks for Linux/Windows OS

        # A list to hold each command as a separate string.
        list_of_cmds = []

        # Iterate over the items in the Commands_List widget.
        for i in range(self.Commands_List.count()):

            # Add the command string text ot the list_of_cmds list.
            list_of_cmds.append(self.Commands_List.item(i).text())

        # Join all of the command strings together (separated by a line break).
        all_commands_string = '\n'.join(list_of_cmds)

        # Create a QDialog window instance.
        d = QtGui.QDialog()

        # Open a browser for the user to select a location and filename to save the command file. Set the most recent
        #  file save location.
        self.saved_file = QtGui.QFileDialog.getSaveFileName(d, 'Save Command File As')

        # Write the commands to the file.
        file = open(self.saved_file, 'w')
        file.write(all_commands_string)
        file.close()

    def set_working_directory(self):

        # TODO egiles 2018-05-17 Discuss with Steve the mechanics of a working directory and an initial working directory
        pass

    def update_command_count(self):
        """
        Count the number of items (each item is a command string) in the Command_List widget. Update the total_commands
        class variable to the current number of command items in the Command_List widget. Update the selected_commands
        class variable to the current number of selected command items in the Command_List widget. Update the
        Command_List widget label to display the total and selected number of commands within the widget.

        Return: None
        """

        # Count the number of items (each item is a command string) in the Command_List widget.
        self.total_commands = self.Commands_List.count()

        # If there is at least one command in the Command_List widget, enable the "Run All Commands" button and the
        # "Clear Commands" button. If not, disable the "Run All Commands" button and the "Clear Commands" button.
        if self.total_commands > 0:
            self.Commands_RunAll_Button.setEnabled(True)
            self.Commands_Clear_Button.setEnabled(True)
        else:
            self.Commands_RunAll_Button.setEnabled(False)
            self.Commands_Clear_Button.setEnabled(False)

        # Count the number of selected items (each item is a command string) in the Command_List widget.
        self.selected_commands = len(self.Commands_List.selectedItems())

        # If there is at least one selected command in the Command_List widget, enable the "Run Selected Commands"
        # button. If not, disable the "Run Selected Commands" button.
        if self.selected_commands > 0:
            self.Commands_RunSelected_Button.setEnabled(True)
        else:
            self.Commands_RunSelected_Button.setEnabled(False)

        # Update the Command_List widget label to display the total and selected number of commands.
        self.Commands_GroupBox.setTitle(
            "Commands ({} commands, {} selected)".format(self.total_commands, self.selected_commands))

    def update_gp_command_list(self, selected=False):
        """
        Updates the GeoProcessor's command list with the existing command strings in the Command_List widget.

        Returns: None
        """

        # An empty list. Will hold the command strings. One item for each existing command within the Command_List
        # widget.
        cmd_string_list = []

        # If the GeoProcessor should be updated with ALL commands, continue.
        if not selected:

            # Iterate over ALL of the items in the Command_List widget.
            for i in range(self.Commands_List.count()):

                # Add the item's text (the command string) to the cmd_string_list.
                cmd_string_list.append(self.Commands_List.item(i).text())

        # If the GeoProcessor should be updated with the SELECTED commands, continue.
        else:

            # Iterate over the SELECTED items in the Command_List widget.
            for item in list(self.Commands_List.selectedItems()):

                # Add the item's text (the command string) to the cmd_string_list.
                cmd_string_list.append(item.text())

        # Read the command strings into GeoProcessor command objects. Pass the objects to the GeoProcessor.
        self.gp.read_ui_command_workflow(cmd_string_list)

    def update_results_count(self):
        """
        Update the labels of the Results' Tables to disply the total number of rows in each table and the total
        number of selected rows in each table.

        Return: None
        """

        # Count the total and selected number of rows within the GeoLayers table. Update the label to reflect counts.
        row_num = str(self.Results_GeoLayers_Table.rowCount())
        slct_row_num = str(len(set(index.row() for index in self.Results_GeoLayers_Table.selectedIndexes())))
        self.Results_GeoLayers_GroupBox.setTitle("GeoLayers ({} GeoLayers, {} selected)".format(row_num, slct_row_num))

        # Count the total and selected number of rows within the Tables table. Update the label to reflect counts.
        row_num = str(self.Results_Tables_Table.rowCount())
        slct_row_num = str(len(set(index.row() for index in self.Results_Tables_Table.selectedIndexes())))
        self.Results_Tables_GroupBox.setTitle("Tables ({} Tables, {} selected)".format(row_num, slct_row_num))

        # Count the total and selected number of rows within the Maps table. Update the label to reflect counts.
        row_num = str(self.Results_Maps_Table.rowCount())
        slct_row_num = str(len(set(index.row() for index in self.Results_Maps_Table.selectedIndexes())))
        self.Results_Maps_GroupBox.setTitle("Maps ({} Maps, {} selected)".format(row_num, slct_row_num))

        # Count the total and selected number of rows within the Output Files table. Update the label to reflect counts.
        row_num = str(self.Results_OutputFiles_Table.rowCount())
        slct_row_num = str(len(set(index.row() for index in self.Results_OutputFiles_Table.selectedIndexes())))
        self.Results_OutputFiles_GroupBox.setTitle("Output Files ({} Output Files, {} selected)".format(row_num,
                                                                                                        slct_row_num))

    def view_documentation(self):
        """
        Opens the GeoProcessor user documentation in the user's default browser.

        Return: None
        """

        # Open the GeoProcessor user documentation in the default browser (new window).
        webbrowser.open_new(self.user_doc_url)
