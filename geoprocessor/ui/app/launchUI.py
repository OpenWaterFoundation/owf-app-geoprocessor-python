from geoprocessor.ui.app.mainWindow import Ui_MainWindow
from geoprocessor.ui.commands.layers.ReadGeoLayerFromGeoJSON import Ui_Dialog as Ui_Dialog_ReadGeoLayerFromGeoJSON
from PyQt4 import QtGui
import functools


class GeoProcessorUI(Ui_MainWindow):

    def __init__(self, window, geoprocessor):
        Ui_MainWindow.__init__(self)
        self.setupUi(window)

        # Counts the total and selected commands within the Command_List widget.
        self.total_commands = 0
        self.selected_commands = 0

        # Passes the GeoProcessor object to a class variable for future use.
        self.gp = geoprocessor

        # Listeners
        # Listens for a change in command selection within the Command_List widget.
        self.Commands_List.itemSelectionChanged.connect(self.update_command_count)


        # Connects the `Run All Commands` to an action that will run all of the commands within the workflow.
        self.Commands_RunAll_Button.clicked.connect(self.run_commands)

        # Connects the `Run Selected Commands` to an action that will run the selected commands within the workflow.
        self.Commands_RunSelected_Button.clicked.connect(functools.partial(self.run_commands, True))

        # Connects the Main Window's menu bar of commands to each command's dialog window.
        self.GeoLayers_Read_ReadGeoLayerFromGeoJSON.triggered.connect(
            functools.partial(self.open_command_dialog, Ui_Dialog_ReadGeoLayerFromGeoJSON()))

    def open_command_dialog(self, cmd_dialog_design_object):
        """
        Opens the dialog window for the selected command. If the users clicks "OK" within the dialog window, the
        command string (with the desired parameter values) is added to the Command_List widget within the Main Window
        user interface. Other UI components are also updated - including the total and selected command count, the
        Command_List Widget Label, and the GeoProcessor's list of commands.

        Args:
            cmd_dialog_design_object (obj instance): a new instance of the Dialog window design class for the desired
            command

        Returns: None


        """

        # Create a QDialog window instance.
        d = QtGui.QDialog()

        # Create the dialog design instance for the specific input command.
        ui = cmd_dialog_design_object

        # Apply the command-specific dialog design to the QDialog window.
        ui.setupUi(d)

        # If the "OK" button is clicked within the dialog window, continue.
        # Else, if the "Cancel" button is clicked, do nothing.
        if d.exec_():

            # Get the command string from the dialog window.
            command_string = cmd_dialog_design_object.CommandDisplay_View_TextBrowser.toPlainText()

            # Add the command string to the Command_List widget.
            self.Commands_List.addItem(command_string)

            # Update the command count and Command_List label to show that a command was added to the workflow.
            self.update_command_count()

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
            self.Results_Tables_Table.setItem(new_row_index, 1, QtGui.QTableWidgetItem(table.count(returnCol=True)))

            # Retrieve the number of rows in the Table and set as the attribute for the Row Count column.
            self.Results_Tables_Table.setItem(new_row_index, 2, QtGui.QTableWidgetItem(table.count(returnCol=False)))

        # TODO egiles 2018-05-14 Populate the Results Maps Table
        # TODO egiles 2018-05-14 Populate the Results Output Files Table

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

        # If there is at least one command in the Command_List widget, enable the "Run All Commands" button. If not,
        # disable the "Run All Commands" button.
        if self.total_commands > 0:
            self.Commands_RunAll_Button.setEnabled(True)
        else:
            self.Commands_RunAll_Button.setEnabled(False)

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
