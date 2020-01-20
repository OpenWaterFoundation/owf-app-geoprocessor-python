# GeoProcessorUI - class for main GeoProcessor UI
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

# The following is needed to allow type hinging -> GeoLayer, and requires Python 3.7+
# See:  https://stackoverflow.com/questions/33533148/
#         how-do-i-specify-that-the-return-type-of-a-method-is-the-same-as-the-class-itsel
from __future__ import annotations

from geoprocessor.app.GeoProcessorAppSession import GeoProcessorAppSession
from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand
# TODO smalers 2020-01-15 cannot type hint GeoProcessor because it results in circular import
# from geoprocessor.core.GeoProcessor import GeoProcessor
from geoprocessor.core.GeoProcessorCommandFactory import GeoProcessorCommandFactory
from geoprocessor.core.CommandStatusType import CommandStatusType
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.ui.core.GeoProcessorCommandEditorFactory import GeoProcessorCommandEditorFactory
# The following allows declaring QtWidgets.QMenu, QtWidgets.QAction, etc.
from PyQt5 import QtCore, QtGui, QtWidgets, Qt

from sip import SIP_VERSION_STR  # Used for info, others extracted from above objects

import geoprocessor.util.app_util as app_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.log_util as log_util
import geoprocessor.util.os_util as os_util
import geoprocessor.util.qgis_util as qgis_util
from geoprocessor.ui.app.CommandListWidget import CommandListWidget  # previously command_list_view
# from geoprocessor.ui.core.GeoProcessorListModel import GeoProcessorListModel  # previously gp_list_model
from geoprocessor.ui.core.GeoProcessorListModel import GeoProcessorListModel
from geoprocessor.ui.util.CommandListBackup import CommandListBackup  # previously command_list_backup
import geoprocessor.ui.util.qt_util as qt_util

import datetime
import functools
import logging
import os
import platform
import qgis.utils
import qgis.gui
import struct
import subprocess
import sys
import webbrowser


class GeoProcessorUI(QtWidgets.QMainWindow):  # , Ui_MainWindow):
    """
    Main GeoProcessor UI class, which instantiates a main application window that the user interacts with.
    This class is a child of the core Qt window classes.
    """
    def __init__(self, geoprocessor, runtime_properties: dict,
                 app_session: GeoProcessorAppSession) -> None:
        """
        Initialize the GeoProcessorUI class instance.

        Args:
            geoprocessor (GeoProcessor):  the instance of the GeoProcessor to use with the UI
            runtime_properties (dict): properties to use at runtime
            app_session (GeoProcessorAppSession): application session instance
        """

        # ---------------------------------------------
        # Start GeoProcessor and application data used in the UI

        # This is a session object to keep track of session variables such as command file history
        self.app_session: GeoProcessorAppSession = app_session

        # The GeoProcessor object from calling code (main app) will be used for processing.
        self.gp = geoprocessor

        # End properties that are used in the UI
        # ---------------------------------------------

        # Initialize UI components to None so that PyCharm does not complain about initializing outside of __init__
        # and to emphasize UI components.
        # Start properties that are used in the UI, referenced in the setup_ui() function.

        # Menubar
        self.menubar: QtWidgets.QMenuBar or None = None

        # Toolbar
        # self.toolbar: ?
        self.toolbar = None
        self.increase_indent_button: QtWidgets.QAction or None = None
        self.decrease_indent_button: QtWidgets.QAction or None = None

        # Layer catalog
        # - TODO smales 2020-01-15 catalog area has not yet been implemented
        self.catalog_GroupBox: QtWidgets.QGroupBox or None = None
        self.catalog_GridLayout: QtWidgets.QGridLayout or None = None
        self.pushButton: QtWidgets.QPushButton or None = None
        self.lineEdit: QtWidgets.QLineEdit or None = None
        self.listWidget: QtWidgets.QListWidget or None = None

        # Command list
        self.command_CommandListWidget: CommandListWidget or None = None  # previously command_ListWidget
        self.commands_GroupBox: QtWidgets.QGroupBox or None = None
        # # self.gp_model: GeoProcessorListModel or None = None
        # self.command_list_model: GeoProcessorListModel or None = None

        # Command list - popup menu
        self.rightClickMenu_Commands: QtWidgets.QMenu or None = None
        self.menu_item_command_status: QtWidgets.QAction or None = None
        self.menu_item_edit_command: QtWidgets.QAction or None = None
        self.menu_item_delete_commands: QtWidgets.QAction or None = None
        self.menu_item_increase_indent_command: QtWidgets.QAction or None = None
        self.menu_item_decrease_indent_command: QtWidgets.QAction or None = None
        self.menu_item_convert_from_command: QtWidgets.QAction or None = None
        self.menu_item_convert_to_command: QtWidgets.QAction or None = None
        self.menu_item_select_all_commands: QtWidgets.QAction or None = None
        self.menu_item_deselect_all_commands: QtWidgets.QAction or None = None

        self.__commands_cut_buffer = []  # List of commands for cut/copy/paste

        # Results area
        self.results_GroupBox: QtWidgets.QGroupBox or None = None
        self.results_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_TabWidget: QtWidgets.QTabWidget or None = None

        # Results / GeoLayers
        self.rightClickMenu_GeoLayers: QtWidgets.QMenu or None = None
        self.results_GeoLayers_Tab: QtWidgets.QWidget or None = None
        self.results_GeoLayers_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_GeoLayers_GroupBox: QtWidgets.QGroupBox or None = None
        self.results_GeoLayers_GroupBox_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_GeoLayers_Table: QtWidgets.QTableWidget or None = None

        # Results / Map
        self.results_Maps_Tab: QtWidgets.QWidget or None = None
        self.results_Maps_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_Maps_GroupBox: QtWidgets.QGroupBox or None = None
        self.results_Maps_GroupBox_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_Maps_Table: QtWidgets.QTableWidget or None = None

        # Map canvas components and actions
        self.map_window: QtWidgets.QDialog or None = None
        self.map_window_layout: QtWidgets.QVBoxLayout or None = None
        self.map_toolbar: QtWidgets.QToolBar or None = None

        self.toolPan: qgis.gui.QgsMapToolPan or None = None
        self.toolZoomIn: qgis.gui.QgsMapToolZoom or None = None
        self.toolZoomOut: qgis.gui.QgsMapToolZoom or None = None

        self.actionZoomIn: QtWidgets.QAction or None = None
        self.actionZoomOut: QtWidgets.QAction or None = None
        self.actionPan: QtWidgets.QAction or None = None
        self.map_window_widget: QtWidgets.QWidget or None = None

        self.canvas: qgis.gui.QgsMapCanvas or None = None

        # Results / Output Files
        self.results_OutputFiles_Tab: QtWidgets.QWidget or None = None
        self.results_OutputFiles_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_OutputFiles_GroupBox: QtWidgets.QGroupBox or None = None
        self.results_OutputFiles_GroupBox_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_OutputFiles_Table: QtWidgets.QTableWidget or None = None

        # Results / Properties
        self.results_Properties_Tab: QtWidgets.QWidget or None = None
        self.results_Properties_Tab_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_Properties_GroupBox: QtWidgets.QGroupBox or None = None
        self.results_Properties_GroupBox_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_Properties_Table: QtWidgets.QTableWidget or None = None

        # Results / Tables
        self.results_Tables_Tab: QtWidgets.QWidget or None = None
        self.results_Tables_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_Tables_GroupBox: QtWidgets.QGroupBox or None = None
        self.results_Tables_GroupBox_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_Tables_Table: QtWidgets.QTableWidget or None = None

        # Tables attribute table window
        self.attributes_window: QtWidgets.QDialog or None = None
        self.attributes_window_layout: QtWidgets.QVBoxLayout or None = None
        self.attributes_table: QtWidgets.QTableWidget or None = None

        # Status area at bottom of main UI
        self.statusbar: QtWidgets.QStatusBar or None = None
        self.status_GridLayout: QtWidgets.QGridLayout or None = None
        self.status_CommandWorkflow_StatusBar: QtWidgets.QProgressBar or None = None
        self.status_CurrentCommand_StatusBar: QtWidgets.QProgressBar or None = None
        self.status_Label: QtWidgets.QLabel or None = None
        self.status_Label_Hint: QtWidgets.QLabel or None = None

        # Define all application menus
        # - This won't be needed for dynamically-loaded features.
        # - Menus and submenus are of type QtWidgets.QMenu, and menu items are of type QtWidgets.QAction.

        # File menu
        self.Menu_File: QtWidgets.QMenu or None = None
        self.Menu_File_New: QtWidgets.QMenu or None = None
        self.Menu_File_New_CommandFile: QtWidgets.QAction or None = None
        self.Menu_File_Open: QtWidgets.QMenu or None = None
        self.Menu_File_Open_CommandFile: QtWidgets.QAction or None = None
        # List of 20 most recent command files, dynamic menus
        self.Menu_File_Open_CommandFileHistory_List: list or None = None
        # Maximum number of command files in the File / Open / Command File menu
        self.command_file_menu_max: int = 20
        self.Menu_File_Save: QtWidgets.QMenu or None = None
        self.Menu_File_Save_Commands: QtWidgets.QAction or None = None
        self.Menu_File_Save_CommandsAs: QtWidgets.QAction or None = None
        self.Menu_File_Print: QtWidgets.QAction or None = None
        self.Menu_File_Exit: QtWidgets.QAction or None = None

        # Edit menu
        self.Menu_Edit: QtWidgets.QMenu or None = None
        self.Menu_Edit_Format: QtWidgets.QAction or None = None

        # Commands menu
        self.Menu_Commands: QtWidgets.QMenu or None = None
        # Commands / Select, Free GeoLayer menu
        self.Menu_Commands_Select_Free_GeoLayers: QtWidgets.QMenu or None = None
        self.Menu_Commands_Select_Free_FreeGeoLayers: QtWidgets.QAction or None = None

        # Commands / Create GeoLayer menu
        self.Menu_Commands_Create_GeoLayers: QtWidgets.QMenu or None = None
        self.Menu_Commands_Create_CopyGeoLayer: QtWidgets.QAction or None = None
        self.Menu_Commands_Create_CreateGeoLayerFromGeometry: QtWidgets.QAction or None = None

        # Commands / Read GeoLayer
        self.Menu_Commands_Read_GeoLayers: QtWidgets.QMenu or None = None
        self.Menu_Commands_Read_ReadGeoLayerFromDelimitedFile: QtWidgets.QAction or None = None
        self.Menu_Commands_Read_ReadGeoLayerFromGeoJSON: QtWidgets.QAction or None = None
        self.Menu_Commands_Read_ReadGeoLayerFromShapefile: QtWidgets.QAction or None = None
        self.Menu_Commands_Read_ReadGeoLayersFromFGDB: QtWidgets.QAction or None = None
        self.Menu_Commands_Read_ReadGeoLayersFromFolder: QtWidgets.QAction or None = None

        # Commands / Fill GeoLayer
        self.Menu_Commands_FillGeoLayerMissingData: QtWidgets.QMenu or None = None

        # Commands / Set GeoLayer
        self.Menu_Commands_SetGeoLayer_Contents: QtWidgets.QMenu or None = None
        self.Menu_Commands_SetContents_AddGeoLayerAttribute: QtWidgets.QAction or None = None
        self.Menu_Commands_SetContents_RemoveGeoLayerAttributes: QtWidgets.QAction or None = None
        self.Menu_Commands_SetContents_RenameGeoLayerAttribute: QtWidgets.QAction or None = None
        self.Menu_Commands_SetContents_SetGeoLayerCRS: QtWidgets.QAction or None = None
        self.Menu_Commands_SetContents_SetGeoLayerProperty: QtWidgets.QAction or None = None

        # Commands / Manipulate GeoLayer
        self.Menu_Commands_Manipulate_GeoLayers: QtWidgets.QMenu or None = None
        self.Menu_Commands_Manipulate_ClipGeoLayer: QtWidgets.QAction or None = None
        self.Menu_Commands_Manipulate_IntersectGeoLayer: QtWidgets.QAction or None = None
        self.Menu_Commands_Manipulate_MergeGeoLayers: QtWidgets.QAction or None = None
        self.Menu_Commands_Manipulate_SimplifyGeoLayerGeometry: QtWidgets.QAction or None = None
        self.Menu_Commands_Manipulate_SplitGeoLayerByAttribute: QtWidgets.QAction or None = None

        # Commands / Analyze GeoLayer
        self.Menu_Commands_Analyze_GeoLayers: QtWidgets.QMenu or None = None

        # Commands / Check GeoLayer
        self.Menu_Commands_Check_GeoLayers: QtWidgets.QMenu or None = None

        # Commands / Write GeoLayer
        self.Menu_Commands_Write_GeoLayers: QtWidgets.QMenu or None = None
        self.Menu_Commands_Write_WriteGeoLayerToDelimitedFile: QtWidgets.QAction or None = None
        self.Menu_Commands_Write_WriteGeoLayerToGeoJSON: QtWidgets.QAction or None = None
        self.Menu_Commands_Write_WriteGeoLayerToKML: QtWidgets.QAction or None = None
        self.Menu_Commands_Write_WriteGeoLayerToShapefile: QtWidgets.QAction or None = None

        # Commands / Datastore Processing
        self.Menu_Commands_DatastoreProcessing: QtWidgets.QMenu or None = None
        self.Menu_Commands_DatastoreProcessing_OpenDataStore: QtWidgets.QAction or None = None
        self.Menu_Commands_DatastoreProcessing_ReadTableFromDataStore: QtWidgets.QAction or None = None

        # Commands/ Network Processing
        self.Menu_Commands_NetworkProcessing: QtWidgets.QMenu or None = None

        # Commands/ Spreadsheet Processing
        self.Menu_Commands_SpreadsheetProcessing: QtWidgets.QMenu or None = None

        # Commands/ Template Processing
        self.Menu_Commands_TemplateProcessing: QtWidgets.QMenu or None = None

        # Commands/ Visualization Processing
        self.Menu_Commands_VisualizationProcessing: QtWidgets.QMenu or None = None

        # Commands / General
        # Commands / General - Comments
        self.Menu_Commands_General_Comments: QtWidgets.QMenu or None = None
        self.Menu_Commands_General_Comments_Single: QtWidgets.QAction or None = None
        self.Menu_Commands_General_Comments_MultipleStart: QtWidgets.QAction or None = None
        self.Menu_Commands_General_Comments_MultipleEnd: QtWidgets.QAction or None = None
        self.Menu_Commands_General_Comments_EnabledFalse: QtWidgets.QAction or None = None
        self.Menu_Commands_General_Comments_ExpectedStatusFail: QtWidgets.QAction or None = None
        self.Menu_Commands_General_Comments_ExpectedStatusWarn: QtWidgets.QAction or None = None
        self.Menu_Commands_General_Comments_Blank: QtWidgets.QAction or None = None

        # Commands / General - File Handling
        self.Menu_Commands_General_FileHandling: QtWidgets.QMenu or None = None
        self.Menu_Commands_General_FileHandling_CopyFile: QtWidgets.QAction or None = None
        self.Menu_Commands_General_FileHandling_ListFiles: QtWidgets.QAction or None = None
        self.Menu_Commands_General_FileHandling_RemoveFile: QtWidgets.QAction or None = None
        self.Menu_Commands_General_FileHandling_UnzipFile: QtWidgets.QAction or None = None
        self.Menu_Commands_General_FileHandling_WebGet: QtWidgets.QAction or None = None

        # Commands / General - Logging and Messaging
        self.Menu_Commands_General_LoggingMessaging: QtWidgets.QMenu or None = None
        self.Menu_Commands_General_LoggingMessaging_Message: QtWidgets.QAction or None = None
        self.Menu_Commands_General_LoggingMessaging_StartLog: QtWidgets.QAction or None = None

        # Commands / General - Running and Properties
        self.Menu_Commands_General_RunningProperties: QtWidgets.QMenu or None = None
        self.Menu_Commands_General_RunningProperties_If: QtWidgets.QAction or None = None
        self.Menu_Commands_General_RunningProperties_EndIf: QtWidgets.QAction or None = None
        self.Menu_Commands_General_RunningProperties_For: QtWidgets.QAction or None = None
        self.Menu_Commands_General_RunningProperties_EndFor: QtWidgets.QAction or None = None
        self.Menu_Commands_General_RunningProperties_RunCommands: QtWidgets.QAction or None = None
        self.Menu_Commands_General_RunningProperties_RunGdalProgram: QtWidgets.QAction or None = None
        self.Menu_Commands_General_RunningProperties_RunOgrProgram: QtWidgets.QAction or None = None
        self.Menu_Commands_General_RunningProperties_RunProgram: QtWidgets.QAction or None = None
        self.Menu_Commands_General_RunningProperties_SetProperty: QtWidgets.QAction or None = None
        self.Menu_Commands_General_RunningProperties_SetPropertyFromGeoLayer: QtWidgets.QAction or None = None
        self.Menu_Commands_General_RunningProperties_WritePropertiesToFile: QtWidgets.QAction or None = None

        # Commands / General - Test Processing
        self.Menu_Commands_General_TestProcessing: QtWidgets.QMenu or None = None
        self.Menu_Commands_General_TestProcessing_CompareFiles: QtWidgets.QAction or None = None
        self.Menu_Commands_General_TestProcessing_CreateRegressionTestCommandFile: QtWidgets.QAction or None = None
        self.Menu_Commands_General_TestProcessing_StartRegressionTestResultsReport: QtWidgets.QAction or None = None
        self.Menu_Commands_General_TestProcessing_WriteCommandSummaryToFile: QtWidgets.QAction or None = None
        self.Menu_Commands_General_TestProcessing_WriteGeoLayerPropertiesToFile: QtWidgets.QAction or None = None

        # Commands(Raster) menu
        self.Menu_Commands_Raster: QtWidgets.QMenu or None = None

        # Commands(Raster) / Create GeoLayer
        self.Menu_Commands_Raster_Create_RasterGeoLayers: QtWidgets.QMenu or None = None
        self.Menu_Commands_Raster_Create_CreateRasterGeoLayer: QtWidgets.QAction or None = None

        # Commands(Raster) / Read GeoLayer
        self.Menu_Commands_Raster_Read_RasterGeoLayers: QtWidgets.QMenu or None = None
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromFile: QtWidgets.QAction or None = None

        # Commands(Table) menu
        self.Menu_Commands_Table: QtWidgets.QMenu or None = None
        self.Menu_Commands_Tables_Read: QtWidgets.QMenu or None = None
        self.Menu_Commands_Table_ReadTableFromDataStore: QtWidgets.QAction or None = None
        self.Menu_Commands_Table_ReadTableFromDelimitedFile: QtWidgets.QAction or None = None
        self.Menu_Commands_Table_ReadTableFromExcel: QtWidgets.QAction or None = None
        self.Menu_Commands_Tables_Process: QtWidgets.QMenu or None = None
        self.Menu_Commands_Tables_Write: QtWidgets.QMenu or None = None
        self.Menu_Commands_Table_WriteTableToDataStore: QtWidgets.QAction or None = None
        self.Menu_Commands_Table_WriteTableToDelimitedFile: QtWidgets.QAction or None = None
        self.Menu_Commands_Table_WriteTableToExcel: QtWidgets.QAction or None = None

        # Tools menu
        self.Menu_Tools: QtWidgets.QMenu or None = None
        self.Menu_Tools_ViewLog: QtWidgets.QAction or None = None
        self.Menu_Tools_ViewStartupLog: QtWidgets.QAction or None = None

        # Help menu
        self.Menu_Help: QtWidgets.QMenu or None = None
        self.Menu_Help_About: QtWidgets.QAction or None = None
        self.Menu_Help_SoftwareSystemInformation: QtWidgets.QAction or None = None
        self.Menu_Help_ViewDocumentation: QtWidgets.QAction or None = None

        self.sys_info: QtWidgets.QDialog or None = None
        self.sys_info_text_browser: QtWidgets.QTextBrowser or None = None

        # Old way was to initialize generically
        # super().__init__()
        # New way is to inherit from Qt main window
        QtWidgets.QMainWindow.__init__(self)
        print('Inside GeoProcessorUI constructor, calling setup_ui')
        # Call the setupUi function to instantiate UI components
        # - This is code that was originally auto-generated by QT Designer
        self.setup_ui()

        # 2020-01-18 moved the following logic into setup_ui_commands()
        # Model to map GeoProcessor commands to the CommandListWidget
        # # self.gp_model = GeoProcessorListModel(self.gp, self.command_CommandListWidget)
        # self.gp_model = GeoProcessorListModel(self.gp)
        # self.command_CommandListWidget.set_gp_model(self.gp_model)

        # Initialize a command list backup object. This will keep track of the command list and
        # notify the program if it has been edited since the previous save.
        self.command_list_backup = CommandListBackup()

        # Save runtime properties
        # - Initially the AppVersion and AppVersionDate, for use in Help About
        if runtime_properties is None:
            self.runtime_properties = {}
        else:
            self.runtime_properties = runtime_properties

        # The most recent file save location, used to help file dialog start with recent location
        # - could be command file or other files
        self.saved_file = None

        # Keep track of whether the user has opened a command file,
        # used to decide whether to save command or save command as on exit
        self.opened_command_file = False

        # Has the command file been saved? False only if new command file has not yet been saved
        self.command_file_saved = False

        # All event handlers and connections are configured in the setup_ui*() functions grouped by component.

        self.gp.add_command_processor_listener(self)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        When exiting out of the main window do checks to see if the command file has been modified.
        If modified warn user and ask if command file should be saved.
        
        Args:
            event: close event
        
        Returns:
            None
        """

        self.closeEvent_save_command_file()
        self.closeEvent_confirm_exit(event)

    # noinspection PyPep8Naming
    def closeEvent_confirm_exit(self, event: QtGui.QCloseEvent) -> None:
        """
        Prompt user with a dialog window that asks if the user really wants to exit
        GeoProcessor.

        Args:
            event: Event being the exit button clicked

        Returns:
            None
        """
        exit_dialog = QtWidgets.QMessageBox.question(self, 'GeoProcessor',
                                                     'Are you sure you want to exit GeoProcessor?',
                                                     QtWidgets.QMessageBox.Yes |
                                                     QtWidgets.QMessageBox.No)

        # If user selects yes to save commands
        if exit_dialog == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    # noinspection PyPep8Naming
    def closeEvent_save_command_file(self) -> None:
        """
        Before exiting check to see if the command file has been edited. If so ask if the user
        would like to save the command file.

        Returns:
            None
        """
        # Check to see if command list has been modified
        command_list_modified = self.command_CommandListWidget.command_list_modified()

        # If modified, open dialog box to ask if user wants to save file
        if command_list_modified:
            save_command_dialog = QtWidgets.QMessageBox.question(self, 'GeoProcessor',
                                                                 'Do you want to save the changes you made?',
                                                                 QtWidgets.QMessageBox.Yes |
                                                                 QtWidgets.QMessageBox.No |
                                                                 QtWidgets.QMessageBox.Cancel)

            # If user selects yes to save commands
            if save_command_dialog == QtWidgets.QMessageBox.Yes:
                # Open Save Window
                if not self.opened_command_file:
                    self.ui_action_save_commands_as()
                else:
                    self.ui_action_save_commands()

    def command_completed(self, icommand: int, ncommand: int, command: AbstractCommand,
                          percent_completed: float, message: str) -> None:
        """
        Indicate that a command has completed. The success/failure of the command is not indicated.

        Args:
            icommand (int):  The command index (0+).
            ncommand (int): The total number of commands to process
            command (Command): The reference to the command that is starting to run,
                provided to allow future interaction with the command.
            percent_completed (float):  If >= 0, the value can be used to indicate progress
                running a list of commands (not the single command). If less than zero, then no
                estimate is given for the percent complete and calling code can make its own determination
                (e.g. ((icommand + 1)/ncommand)*100)
            message (str):  A short message describing the status (e.g. "Running command...")

        Returns:
            None
        """

        if command is None:
            # Not really needed but prevents a warning
            return

        # Update the progress to indicate progress (1 to number of commands... completed).
        self.status_CommandWorkflow_StatusBar.setValue(icommand + 1)
        self.status_CurrentCommand_StatusBar.setValue(100)

        # Set the tooltip text for the progress bar to indicate the numbers
        hint = ("Completed command " + str(icommand + 1) + " of " + str(ncommand))
        self.status_CommandWorkflow_StatusBar.setToolTip(hint)

        self.status_Label.setText("Ready")
        self.status_Label_Hint.setText("Completed running commands. Use Results and Tools menus.")

        # TODO Last command has complete or Exit() command. Check TSTool
        # Is instance of exit_command ???
        # if (icommand + 1) == ncommand:
        #    # Last command has completed so refresh the time series results.
        #    # command_string = command.

    def command_started(self, icommand: int, ncommand: int, command: AbstractCommand,
                        percent_completed: float, message: str) -> None:
        """
        Indicate that a command has started running.

        Args:
            icommand (int): The command index (0+) in the list of commands being run (see ncommand)
            ncommand (int): The total number of commands to process (will be selected number if running selected)
            command (Command): The reference to the command that is starting to run,
                provided to allow future interaction with the command.
            percent_completed (float): If >= 0, the value can be used to indicate progress
                running a list of commands (not the single command). If less than zero, then no estimate is given
                for the percent complete and calling code can make its own determination
                (e.g. ((icommand +1)/ncommand)*100).
            message (str): A short message describing the status (e.g. "Running command...")

        Returns:
            None
        """

        # command_completed updates the progress bar after each command.
        # For this method, only reset the bounds of the progress bar and
        # clear if the first command.
        hint = ("Running command " + str(icommand + 1) + " of " + str(ncommand))
        self.status_Label_Hint.setText(hint)
        # TODO check if run commands is being run then also put the input file name to make it easeir to understand
        # TODO progress. Check TSTool.
        # run_commands()/additional info?
        # Use level zero because the command processor is already printing a log message when each command is run

        self.status_Label.setText("Wait")

        if icommand == 0:
            self.status_CommandWorkflow_StatusBar.setMinimum(0)
            self.status_CommandWorkflow_StatusBar.setMaximum(ncommand)
            self.status_CommandWorkflow_StatusBar.setValue(0)
        # Set the tooltip text for the progress bar to indicate the numbers
            self.status_CommandWorkflow_StatusBar.setToolTip(hint)
        # Always set the value for the command progress sot hat it shows up
        # as zero. The command_progress() method will do a better job of setting
        # the limits and current status for each specific command.
        self.status_CurrentCommand_StatusBar.setMinimum(0)
        self.status_CurrentCommand_StatusBar.setMaximum(100)
        self.status_CurrentCommand_StatusBar.setValue(0)

    def copy_commands_to_clipboard(self) -> None:
        """
        Copy selected commands in the command list (to be used with paste) to the internal cut buffer and clipboard.

        Returns:
            None
        """
        selected_indices = self.command_CommandListWidget.get_selected_indices()
        if selected_indices is not None:
            size = len(selected_indices)
        if size == 0:
            return

        # Clear what may previously have been in the cut buffer...
        self.__commands_cut_buffer.clear()

        # Transfer Command instances to the cut buffer...
        command = None  # Command instance to process
        """
        for i = 0 in range(size):
            command = self.__commands_ListWidget.item(selected_indices[i]).data()
            __commandsCutBuffer.add( command.clone() )

        if remove_original:
            # If removing, delete the selected commands from the list ...
            commandList_RemoveCommandsBasedOnUI()
        """

    def cut_commands_to_clipboard(self) -> None:
        """
        Cut commands in the command list (to be used with paste).

        Returns:
            None
        """
        # TODO smalers 2020-01-18 need to implement
        pass

    # TODO smalers 2020-01-18 does not seem to be called by anything
    def delete_numbered_list_item(self, index: int) -> None:
        """
        Delete the row in the numbered list and update the other numbers.

        Args:
            index (int): numbered list item to be deleted, 0+.

        Returns:
            None
        """
        # Remove item at index
        self.number_ListWidget.takeItem(index)
        # Get the length of the numbered list
        count = self.number_ListWidget.count()

        # Update numbers past the deleted row
        for i in range(index, count):
            list_text = self.number_ListWidget.item(i).text()
            if list_text:
                num = int(self.number_ListWidget.item(i).text())
                num = num - 1
                self.number_ListWidget.item(i).setText(str(num))

    def deselect_all_commands(self) -> None:
        """
        Connected to command list popup "Deselect All Commands" menu.
        Deselect all commands in the command list.

        Returns:
            None
        """
        self.command_CommandListWidget.command_list_deselect_all()

    def edit_command_editor(self) -> None:
        """
        Opens a dialog box to edit an existing command.

        Returns:
            None
        """

        logger = logging.getLogger(__name__)

        # Get the original command

        # Create a new command to edit without affecting the old command in case of cancelled.

        # Get the list of selected indices.
        # - ensure that if any are comments that all are comments and are contiguous
        # The following returns a list of PyQt5.QtCore.QModelIndex, an empty list if somehow none are selected

        selected_indices = self.command_CommandListWidget.get_selected_indices()
        num_selected = len(selected_indices)
        num_selected_are_comments = 0
        # Get the count of how many of the selected commands are comments
        for index in selected_indices:
            if self.gp.commands[index].command_string.strip().startswith('#'):
                num_selected_are_comments = num_selected_are_comments + 1
        if (num_selected_are_comments > 0) and (num_selected != num_selected_are_comments):
            # The selected commands have at least one comment but are not all comments, don't allow the edit
            # - could improve this to only automatically edit the first contiguous block comments or ask the user
            #   whether to edit the first contiguous block
            qt_util.warning_message_box('Cannot edit # comments when other commands are also selected.')
            return

        # Check to see if working with block comments
        comment_block = False
        comment_block_text = ""  # Will contain newline-separated comment lines
        command_object = None
        if num_selected_are_comments > 0:
            # Detected that a block of 1+ comment lines are edited.
            # - additional logic because this is different than a normal command editor that edits a single command.
            comment_block = True
            # Check to see if selected comments are contiguous
            contiguous = True
            num = selected_indices[0]  # First selected command index
            for index in selected_indices:
                if index != num:
                    # Check all but first index
                    if index != num + 1:
                        # Not in a contiguous sequence
                        contiguous = False
                        break
                num += 1
            if not contiguous:
                qt_util.warning_message_box('Cannot edit the selected # comments because they are not contiguous.')
                return
            # If here the comments are verified to be a contiguous block of # comments.
            # The Comment command editor takes a string with newlines separating multiple command lines.
            for index in selected_indices:
                # The object is used to retrieve the command string and also to create a command editor
                # using the factory below.
                command_object = self.gp.commands[index]
                if index != selected_indices[0]:
                    # Add a newline separator
                    comment_block_text += "\n"
                command_string = command_object.command_string
                comment_block_text += command_string
        else:
            # Editing a one-line command.
            # - get the index of the single currently selected command for first selected command
            index = self.command_CommandListWidget.get_selected_index()
            if index is None:
                # TODO smalers 2020-01-19 should not get here because Edit menu should be disabled.
                # Nothing was selected
                return
            # Get the command object at that index from GeoProcessor
            command_object = self.gp.commands[index]

        # Pass UI to command object
        command_object.initialize_geoprocessor_ui(self)

        # The following code is used for all commands, including comments:
        # - create a command editor using the factory
        # noinspection PyBroadException
        try:
            # Create the editor for the command
            # - initialization occurs in the dialog
            command_editor_factory = GeoProcessorCommandEditorFactory()
            command_editor = command_editor_factory.new_command_editor(command_object, self.app_session)
            if comment_block:
                # Comment block editor is for 1+ comment lines separated by newline as formed above
                command_editor.set_text(comment_block_text)
        except Exception:
            message = "Error creating editor for existing command."
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
            return

        # Now edit the new command in the editor
        # noinspection PyBroadException
        try:
            # If the "OK" button is clicked within the dialog window, continue.
            # Else, if the "Cancel" button is clicked, do nothing.
            button_clicked = command_editor.exec_()
            if button_clicked == QtWidgets.QDialog.Accepted:
                # OK button was clicked in the editor and validation passed so OK to use the changes.

                # Get the command string from the dialog window.
                command_string = command_editor.CommandDisplay_View_TextBrowser.toPlainText()

                # Update command in GeoProcessor list of commands
                if num_selected_are_comments > 0:
                    if comment_block:
                        # The editor will result in 0+ newline-separated comments
                        # - let the command editor deal with formatting
                        # - the get_text() function is similar to TSTool Command_JDialog.getText().
                        command_string_list = command_editor.get_command_string_list()
                        # Update or insert into the GeoProcessor
                        # - the number of comments as per num_selected_are_comments may be different from the
                        #   number of comments returned from the editor
                        # First, remove the selected comments from before
                        # - remove at the same index for the number of original comments since contiguous
                        for i in range(len(selected_indices)):
                            self.gp.remove_command(selected_indices[0])
                        # Second, add the new comments at the same position as before
                        # - add in reverse order so the shifting results in correct order
                        # - TODO smalers 2019-01-10 need to confirm all case, including working with empty command list
                        for command_string in reversed(command_string_list):
                            self.gp.add_command_at_index(command_string, selected_indices[0])

                # TODO smalers 2020-01-19 the command list should be updated automatically
                # Update the command list to match the status of GeoProcessor
                # self.gp_model.update_command_list_ui()

                # Manually set the run all commands and clear commands buttons to enabled
                self.command_CommandListWidget.commands_RunAllCommands_PushButton.setEnabled(True)
                self.command_CommandListWidget.commands_ClearCommands_PushButton.setEnabled(True)

                # update the window title in case command file has been modified
                self.update_ui_main_window_title()

            else:
                # Cancel was clicked so don't do anything
                pass

        except Exception:
            message = "Error editing existing command."
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
            return

    def new_command_editor(self, command_name: str) -> None:
        """
        Opens the dialog window for the selected command, editing a new command.
        This function is called when the user selects a Command menu item.
        If the users clicks "OK" within the dialog window, the command is added to the Command_List view
        within the Main Window user interface.
        Other UI components are also updated - including the total and selected command count, the
        Command_List Widget Label, and the GeoProcessor's list of commands.

        Args:
            command_name (str): the name of the command

        Returns:
            None (results of the function are propagated to the command list)
        """
        logger = logging.getLogger(__name__)
        # Check to see if command is a comment block with "#"
        comment_block = False
        if command_name == "#":
            comment_block = True
        # Create a full command string, to parse in the command factory
        # - TODO smalers 2019-01-18 This is cumbersome
        # - the command factory should be able to handle Command() as well as #, /*, */ without adding () to all here
        command_string = command_name + "()"
        # Create a new command object for the command name using the command factory
        # noinspection PyBroadException
        try:
            command_factory = GeoProcessorCommandFactory()

            # Initialize the command object (without parameters).
            # Work is done in the GeoProcessorCommandFactory class.
            create_unknown_command_if_not_recognized = False  # Results in UnknownCommand instance
            command_object = command_factory.new_command(
                command_string,
                create_unknown_command_if_not_recognized)

            # Initialize additional command object data.
            # - work is done in the AbstractCommand class
            # - the processor is set in the command
            # - full_initialization parses the command string, which won't do much here since new and no parameters
            full_initialization = True
            command_object.initialize_command(command_string, self.gp_model.gp, full_initialization)
            command_object.initialize_geoprocessor_ui(self)
        except Exception:
            message = "Error creating new command, unable to edit for command string: " + command_string
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
            return

        # If here, a new command instance was successfully created above, but could be an UnknownCommand instance.
        # Use the command object to create a corresponding editor based on the command's
        # command_metadata[`EditorType`] value.
        # noinspection PyBroadException
        try:
            # Create the editor for the command
            # - initialization occurs in the dialog
            command_editor_factory = GeoProcessorCommandEditorFactory()
            command_editor = command_editor_factory.new_command_editor(command_object, self.app_session)
        except Exception:
            message = "Error creating editor for new command:  " + str(command_object.command_string)
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
            return

        # Now edit the new command in the editor.
        # - the editor will check command parameters for validity
        # - if command parameters are validated, the user can press "OK" to accept the new command
        # - if command parameters do not validate, the user can press "Cancel"
        # noinspection PyBroadException
        try:
            # If the "OK" button is clicked within the dialog window, commit the edits to the command list.
            # Else, if the "Cancel" button is clicked, do nothing.
            button_clicked = command_editor.exec_()
            logger.info("Command string after editing:  " + str(command_object.command_string))
            if button_clicked == QtWidgets.QDialog.Accepted:
                # TODO smalers 2020-01-19 working with strings is no longer done because table model handles commands.
                # Get the command string from the dialog window.
                # - Note that this does not use the instance of the command modified by the editor,
                #   but uses the string corresponding to that command.
                # command_string = command_editor.CommandDisplay_View_TextBrowser.toPlainText()

                # Add the command to the GeoProcessor commands.
                # Get the first selected index.
                selected_index = 0
                # If there are already commands in the command list, see if any are selected.
                insert_row = -1  # used to update the UI table model
                insert_count = 0  # used to update the UI table model
                if len(self.gp.commands) > 0:
                    logger.info("Adding command to command list with size > 0.")
                    selected_indices = self.command_CommandListWidget.command_ListView.selectedIndexes()
                    if (selected_indices is not None) and (len(selected_indices) > 0):
                        # Have selected commands
                        # - selected_indices are QModelIndex so get the integer row
                        selected_index = selected_indices[0].row()
                        if comment_block:
                            # If working with a comment block with potential multiple lines,
                            # must add those lines individually to the GeoProcessor.
                            command_string_by_line = command_string.splitlines()
                            # Make sure that the lines start with the comment character
                            comment_commands = []
                            for i in range(len(command_string_by_line)):
                                command_string_by_line[i] = "# " + command_string_by_line[i]
                                command_object = command_factory.new_command(
                                    command_string_by_line[i],
                                    create_unknown_command_if_not_recognized)
                                comment_commands.append(command_object)
                            self.gp_model.insert_commands_at_index(comment_commands, selected_index)
                        else:
                            # Otherwise just add the command line to the GeoProcessor.
                            self.gp_model.insert_command_at_index(command_object, selected_index)
                    else:
                        # Nothing is selected
                        if comment_block:
                            # If working with a comment block with potential multiple lines,
                            # must add those lines individually to the GeoProcessor.
                            command_string_by_line = command_string.splitlines()
                            insert_row = selected_index
                            insert_count = len(command_string_by_line)
                            insert_row_last = insert_row + insert_count - 1
                            logger.info("Inserting command insert_row=" + str(insert_row) + " insert_count=" +
                                        str(insert_count) + " insert_row_last=" + str(insert_row_last))
                            self.gp_model.beginInsertRows(QtCore.QModelIndex(), insert_row, insert_row_last)
                            for command in command_string_by_line:
                                command = "# " + command
                                self.gp.add_command(command)
                            self.gp_model.endInsertRows()
                        else:
                            # Otherwise just add the command line to the GeoProcessor.
                            self.gp_model.insert_command_at_index(command_object, len(self.gp_model))
                else:
                    logger.info("Adding command to command list with size = 0.")
                    # Nothing in the list so nothing will be selected
                    if comment_block:
                        # If working with a comment block with potential multiple lines,
                        # must add those lines individually to the GeoProcessor.
                        command_string_by_line = command_string.splitlines()
                        insert_row = 0
                        insert_count = len(command_string_by_line)
                        insert_row_last = insert_row + insert_count - 1
                        logger.info("Inserting command insert_row=" + str(insert_row) + " insert_count=" +
                                    str(insert_count) + " insert_row_last=" + str(insert_row_last))
                        self.gp_model.beginInsertRows(QtCore.QModelIndex(), insert_row, insert_row_last)
                        for command in command_string_by_line:
                            command = "# " + command
                            self.gp.add_command(command)
                        self.gp_model.endInsertRows()
                    else:
                        # Otherwise just add the command line to the GeoProcessor.
                        self.gp_model.insert_command_at_index(command_object, 0)
                # The item has been added to the GeoProcessor command list but the Widget needs to be informed
                # of the insert and refreshed
                # For GeoProcessorListModelOld...
                # self.gp_model.update_command_list_ui()

                # Manually set the 'Run all commands' and 'Clear commands' buttons to enabled
                # self.command_CommandListWidget.commands_RunAllCommands_PushButton.setEnabled(True)
                # self.command_CommandListWidget.commands_ClearCommands_PushButton.setEnabled(True)
                # Check the command view UI status
                # Synchronize the other lists with the main command list
                self.command_CommandListWidget.number_list_sync_with_commands()
                self.command_CommandListWidget.gutter_list_sync_with_commands()
                self.command_CommandListWidget.update_ui_status_commands()

                # Update the window title in case command file has been modified.
                self.update_ui_main_window_title()

            else:
                # Cancel was clicked so don't do anything.
                pass

        except Exception:
            # Unexpected error.
            message = "Error editing new command"
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
            return

    def paste_commands_from_clipboard(self) -> None:
        """
        Paste commands in the command list (to be used with copy and cut).

        Returns:
            None
        """
        # TODO smalers 2020-01-18 need to implement
        pass

    def select_all_commands(self) -> None:
        """
        Connected to command list popup "Select All Commands" menu.
        Select all commands in the command list.

        Returns:
            None
        """
        self.command_CommandListWidget.command_list_select_all()

    def setup_ui(self) -> None:
        """
        Set up the user interface.
        This code was included from GeoProcessor_Design.py, which was generated by QT Designer by converting
        its '.ui' file to '.py'.
        However, subsequent customization has edited this code directly without reprocessing the '.ui' file,
        and this will continue into the future.

        Returns:
            None
        """
        print("Entering setup_ui")
        main_window = self  # The main window, in this case self
        # Main window that will contain all other components
        main_window.setObjectName(qt_util.from_utf8("MainWindow"))
        self.ui_set_main_window_title("commands not saved")
        main_window.resize(1038, 834)
        font = QtGui.QFont()
        font.setFamily(qt_util.from_utf8("MS Shell Dlg 2"))
        main_window.setFont(font)
        main_window.setWindowOpacity(1.0)
        # Set the main window title bar icon
        icon_path = app_util.get_property("ProgramIconPath").replace('\\', '/')
        main_window.setWindowIcon(QtGui.QIcon(icon_path))
        # main_window.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(icon_path)))

        # Central widget is the place where the main content is placed
        # - See http://doc.qt.io/qt-5/qmainwindow.html
        # - Use 6 columns for grid layout
        main_window.centralwidget = QtWidgets.QWidget(main_window)
        main_window.centralwidget.setObjectName(qt_util.from_utf8("centralwidget"))
        main_window.centralwidget_GridLayout = QtWidgets.QGridLayout(self.centralwidget)
        main_window.centralwidget_GridLayout.setObjectName(qt_util.from_utf8("centralwidget_GridLayout"))

        # Row position within central widget grid layout
        # - will be incremented by one before adding a component so first use will set to zero
        y_centralwidget = 2

        # Set up the Catalog area
        # y_centralwidget = y_centralwidget + 1
        # self.setup_ui_catalog(y_centralwidget)

        # Set up the Commands area
        y_centralwidget = y_centralwidget + 1
        self.setup_ui_commands(y_centralwidget)

        # Setup the Results components
        y_centralwidget = y_centralwidget + 1
        self.setup_ui_results(y_centralwidget)

        # Setup the Status components
        y_centralwidget = y_centralwidget + 1
        self.setup_ui_status(main_window, y_centralwidget)

        # Now set the central widget, which will have been populated with the above components
        main_window.setCentralWidget(self.centralwidget)

        # Setup the Menu components
        self.setup_ui_menus(main_window)
        # Setup the Toolbar components
        self.setup_ui_toolbar(main_window)

        # Triggering the exit event on the main window closes the window.
        self.Menu_File_Exit.triggered.connect(main_window.close)
        # QtCore.QObject.connect(self.Menu_File_Exit, QtCore.SIGNAL(qt_util.from_utf8("triggered()")), MainWindow.close)
        # Don't need to do the following anymore because Qt Designer approach is not used?
        # - Use the new-style approach documented here:
        # http://joat-programmer.blogspot.com/2012/02/pyqt-signal-and-slots-to-capture-events.html
        # QtCore.QMetaObject.connectSlotsByName(main_window)
        # print("Leaving setup_ui")

    def setup_ui_catalog(self, y_centralwidget: int) -> None:
        """
        Set up the Catalog area of the UI.

        Args:
            y_centralwidget (int):  Row position in the central widget to add this component.

        Returns:
            None
        """
        # Catalog area is in the top of the central widget
        # - enable this area later since don't currently have browser for layers or datastores
        # - double hash below is what is commented out
        self.catalog_GroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.catalog_GroupBox.setObjectName(qt_util.from_utf8("catalog_GroupBox"))
        self.catalog_GridLayout = QtWidgets.QGridLayout(self.catalog_GroupBox)
        self.catalog_GridLayout.setObjectName(qt_util.from_utf8("catalog_GridLayout"))
        self.pushButton = QtWidgets.QPushButton(self.catalog_GroupBox)
        self.pushButton.setObjectName(qt_util.from_utf8("pushButton"))
        self.catalog_GridLayout.addWidget(self.pushButton, 0, 1, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.catalog_GroupBox)
        self.lineEdit.setObjectName(qt_util.from_utf8("lineEdit"))
        self.catalog_GridLayout.addWidget(self.lineEdit, 0, 0, 1, 1)
        self.listWidget = QtWidgets.QListWidget(self.catalog_GroupBox)
        self.listWidget.setObjectName(qt_util.from_utf8("listWidget"))
        self.catalog_GridLayout.addWidget(self.listWidget, 1, 0, 1, 2)
        self.catalog_GroupBox.setTitle("Catalog")
        self.centralwidget_GridLayout.addWidget(self.catalog_GroupBox, y_centralwidget, 0, 1, 6)

    def setup_ui_commands(self, y_centralwidget: int) -> None:
        """
        Set up the Commands area of the UI.

        Args:
            y_centralwidget (int):  Row position in the central widget to add this component.

        Returns:
            None
        """
        # Commands area is in the middle of the central widget
        # First the main commands area with border
        self.commands_GroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.commands_GroupBox.setObjectName(qt_util.from_utf8("commands_GroupBox"))
        self.commands_GroupBox.setTitle("Commands (0 commands, 0  selected, 0 with failures, 0 with warnings)")
        # self.commands_GridLayout = QtWidgets.QGridLayout(self.commands_GroupBox)

        self.command_CommandListWidget = CommandListWidget(self.commands_GroupBox)
        # Add double click event
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        # FIXME self.command_CommandListWidget.command_ListView.itemDoubleClicked.connect(self.edit_command_editor)

        # Model to map GeoProcessor commands to the CommandListWidget
        # self.gp_model = GeoProcessorListModel(self.gp, self.command_CommandListWidget)
        self.gp_model = GeoProcessorListModel(self.gp)
        #self.command_CommandListWidget.command_ListWidget.set_gp_model(self.gp_model)
        self.command_CommandListWidget.set_gp_model(self.gp_model)

        # Add listener
        self.command_CommandListWidget.add_main_ui_listener(self)

        # Add the commands to the central widget
        self.centralwidget_GridLayout.addWidget(self.commands_GroupBox, y_centralwidget, 0, 1, 6)

    def setup_ui_menus(self, main_window: GeoProcessorUI) -> None:
        """
        Set up the Menus for the UI.

        Args:
            main_window: the main window that will be initialized with components (same as self in this case).

        Returns:
            None
        """
        # Menu bar for the application
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1038, 20))
        self.menubar.setObjectName(qt_util.from_utf8("menubar"))

        # ============================================================================================================
        # File menu
        # ============================================================================================================

        self.Menu_File = QtWidgets.QMenu(self.menubar)
        self.Menu_File.setObjectName(qt_util.from_utf8("Menu_File"))
        self.Menu_File.setTitle("File")

        # File / New menu
        self.Menu_File_New = QtWidgets.QMenu(self.Menu_File)
        self.Menu_File_New.setObjectName(qt_util.from_utf8("Menu_File_New"))
        self.Menu_File_New.setTitle("New")
        self.Menu_File.addAction(self.Menu_File_New.menuAction())

        # File / New / Command File menu
        self.Menu_File_New_CommandFile = QtWidgets.QAction(main_window)
        self.Menu_File_New_CommandFile.setObjectName(qt_util.from_utf8("Menu_File_New_CommandFile"))
        self.Menu_File_New_CommandFile.setText("Command File")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_File_New_CommandFile.triggered.connect(self.ui_action_new_command_file)
        self.Menu_File_New.addAction(self.Menu_File_New_CommandFile)

        # File / Open menu
        self.Menu_File_Open = QtWidgets.QMenu(self.Menu_File)
        self.Menu_File_Open.setObjectName(qt_util.from_utf8("Menu_File_Open"))
        self.Menu_File_Open.setTitle("Open")
        self.Menu_File.addAction(self.Menu_File_Open.menuAction())

        # File / Open / Command File menu
        self.Menu_File_Open_CommandFile = QtWidgets.QAction(main_window)
        self.Menu_File_Open_CommandFile.setObjectName(qt_util.from_utf8("Menu_File_Open_CommandFile"))
        self.Menu_File_Open_CommandFile.setText("Command File ...")
        icon_path = app_util.get_property("ProgramResourcesPath").replace('\\', '/')
        icon_path = icon_path + "/images/baseline_folder_open_black_18dp.png"
        self.Menu_File_Open_CommandFile.setIcon(QtGui.QIcon(QtGui.QPixmap(icon_path)))
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_File_Open_CommandFile.triggered.connect(lambda: self.ui_action_open_command_file())
        self.Menu_File_Open.addAction(self.Menu_File_Open_CommandFile)
        self.Menu_File_Open.addSeparator()

        # File / Open / Command File menu
        # - initialize enough menu objects for the maximum, but will only actually use 0 to the maximum
        self.Menu_File_Open_CommandFileHistory_List =\
            [QtWidgets.QAction(main_window) for i in range(0, self.command_file_menu_max)]
        for i in range(0, self.command_file_menu_max):
            qt_action = QtWidgets.QAction(main_window)
            # Initially assigned a callback function so that it can be cleared in the first step of reassigning
            # a new callback in ui_init_file_open_recent()
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            qt_action.triggered.connect(lambda: self.ui_action_open_command_file(""))
            self.Menu_File_Open_CommandFileHistory_List[i] = qt_action
        self.ui_init_file_open_recent_files()

        # File / Save menu
        self.Menu_File_Save = QtWidgets.QMenu(self.Menu_File)
        self.Menu_File_Save.setObjectName(qt_util.from_utf8("Menu_File_Save"))
        self.Menu_File_Save.setTitle("Save")
        self.Menu_File.addAction(self.Menu_File_Save.menuAction())

        # File / Save / Commands menu
        self.Menu_File_Save_Commands = QtWidgets.QAction(main_window)
        self.Menu_File_Save_Commands.setObjectName(qt_util.from_utf8("Menu_File_Save_Commands"))
        self.Menu_File_Save_Commands.setText("Commands ...")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_File_Save_Commands.triggered.connect(self.ui_action_save_commands)
        self.Menu_File_Save.addAction(self.Menu_File_Save_Commands)

        # File / Save / Commands As menu
        self.Menu_File_Save_CommandsAs = QtWidgets.QAction(main_window)
        self.Menu_File_Save_CommandsAs.setObjectName(qt_util.from_utf8("Menu_File_Save_CommandsAs"))
        self.Menu_File_Save_CommandsAs.setText("Commands as ...")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_File_Save_CommandsAs.triggered.connect(self.ui_action_save_commands_as)
        self.Menu_File_Save.addAction(self.Menu_File_Save_CommandsAs)

        # File / Print menu
        self.Menu_File_Print = QtWidgets.QAction(main_window)
        self.Menu_File_Print.setObjectName(qt_util.from_utf8("Menu_File_Print"))
        self.Menu_File_Print.setText("Print")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_File_Print.triggered.connect(self.ui_action_print_commands)
        self.Menu_File.addSeparator()
        self.Menu_File.addAction(self.Menu_File_Print)

        # File / Properties menu - TODO smalers 2018-07-29 evaluate whether needed
        # self.Menu_File_Properties = QtWidgets.QAction(main_window)
        # self.Menu_File_Properties.setObjectName(qt_util.from_utf8("Menu_File_Properties"))
        # self.Menu_File_Properties.setText("Properties")
        # self.Menu_File.addSeparator()
        # self.Menu_File.addAction(self.Menu_File_Properties)

        # File / Exit menu
        self.Menu_File_Exit = QtWidgets.QAction(main_window)
        self.Menu_File_Exit.setObjectName(qt_util.from_utf8("Menu_File_Exit"))
        self.Menu_File_Exit.setText("Exit")
        self.Menu_File.addSeparator()
        self.Menu_File.addAction(self.Menu_File_Exit)

        # Set the menu bar
        main_window.setMenuBar(self.menubar)
        self.menubar.addAction(self.Menu_File.menuAction())

        # ============================================================================================================
        # Edit menu
        # ============================================================================================================

        self.Menu_Edit = QtWidgets.QMenu(self.menubar)
        self.Menu_Edit.setObjectName(qt_util.from_utf8("Menu_Edit"))
        self.Menu_Edit.setTitle("Edit")

        # Edit / Format menu
        self.Menu_Edit_Format = QtWidgets.QAction(main_window)
        self.Menu_Edit_Format.setObjectName(qt_util.from_utf8("Menu_Tools_ViewStartupLog"))
        self.Menu_Edit_Format.setText("Format")
        self.Menu_Edit.addAction(self.Menu_Edit_Format)
        # TODO add action to button
        # self.Menu_Tools_ViewStartupLog.triggered.connect(self.ui_action_view_startup_log_file)

        # Add Help menu to menubar
        self.menubar.addAction(self.Menu_Edit.menuAction())

        # ============================================================================================================
        # Commands menu
        # ============================================================================================================

        self.Menu_Commands = QtWidgets.QMenu(self.menubar)
        self.Menu_Commands.setObjectName(qt_util.from_utf8("Menu_Commands"))
        self.Menu_Commands.setTitle("Commands")

        # Commands / Select, Free - GeoLayers menu
        self.Menu_Commands_Select_Free_GeoLayers = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Select_Free_GeoLayers.setObjectName(
            qt_util.from_utf8("Menu_Commands_Select_Free_GeoLayers"))
        self.Menu_Commands_Select_Free_GeoLayers.setTitle("Select, Free GeoLayer")
        self.Menu_Commands.addAction(self.Menu_Commands_Select_Free_GeoLayers.menuAction())

        # FreeGeoLayers
        self.Menu_Commands_Select_Free_FreeGeoLayers = QtWidgets.QAction(main_window)
        self.Menu_Commands_Select_Free_FreeGeoLayers.setObjectName(
            qt_util.from_utf8("Menu_Commands_Select_Free_FreeGeoLayers"))
        self.Menu_Commands_Select_Free_FreeGeoLayers.setText(
            "FreeGeoLayers()... <removes one or more GeoLayers from the GeoProcessor>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Select_Free_FreeGeoLayers.triggered.connect(
            functools.partial(self.new_command_editor, "FreeGeoLayers"))
        self.Menu_Commands_Select_Free_GeoLayers.addAction(self.Menu_Commands_Select_Free_FreeGeoLayers)

        # Commands / Create - GeoLayers menu
        self.Menu_Commands_Create_GeoLayers = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Create_GeoLayers.setObjectName(qt_util.from_utf8("Menu_Commands_Create_GeoLayers"))
        self.Menu_Commands_Create_GeoLayers.setTitle("Create GeoLayer")
        self.Menu_Commands.addAction(self.Menu_Commands_Create_GeoLayers.menuAction())

        # CopyGeoLayer
        self.Menu_Commands_Create_CopyGeoLayer = QtWidgets.QAction(main_window)
        self.Menu_Commands_Create_CopyGeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_Create_CopyGeoLayer"))
        self.Menu_Commands_Create_CopyGeoLayer.setText(
            "CopyGeoLayer()... <copy a GeoLayer to a new GeoLayer>")
        self.Menu_Commands_Create_GeoLayers.addAction(self.Menu_Commands_Create_CopyGeoLayer)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Create_CopyGeoLayer.triggered.connect(
            functools.partial(self.new_command_editor, "CopyGeoLayer"))

        # CreateGeoLayerFromGeometry
        self.Menu_Commands_Create_CreateGeoLayerFromGeometry = QtWidgets.QAction(main_window)
        self.Menu_Commands_Create_CreateGeoLayerFromGeometry.setObjectName(
            qt_util.from_utf8("Menu_Commands_Create_CreateGeoLayerFromGeomtery"))
        self.Menu_Commands_Create_CreateGeoLayerFromGeometry.setText(
            "CreateGeoLayerFromGeometry()... <create a GeoLayer from input geometry data>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Create_CreateGeoLayerFromGeometry.triggered.connect(
            functools.partial(self.new_command_editor, "CreateGeoLayerFromGeometry"))
        self.Menu_Commands_Create_GeoLayers.addAction(self.Menu_Commands_Create_CreateGeoLayerFromGeometry)

        # Commands / Read - GeoLayers menu
        self.Menu_Commands_Read_GeoLayers = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Read_GeoLayers.setObjectName(qt_util.from_utf8("Menu_Commands_Read_GeoLayers"))
        self.Menu_Commands_Read_GeoLayers.setTitle("Read GeoLayer")
        self.Menu_Commands.addAction(self.Menu_Commands_Read_GeoLayers.menuAction())

        # ReadGeoLayerFromDelimitedFile
        self.Menu_Commands_Read_ReadGeoLayerFromDelimitedFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_Read_ReadGeoLayerFromDelimitedFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_GeoLayer_Read_ReadGeoLayerFromDelimitedFile"))
        self.Menu_Commands_Read_ReadGeoLayerFromDelimitedFile.setText(
            "ReadGeoLayerFromDelimitedFile()... <read a GeoLayer from a file in delimited file format>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Read_ReadGeoLayerFromDelimitedFile.triggered.connect(
            functools.partial(self.new_command_editor, "ReadGeoLayerFromDelimitedFile"))
        self.Menu_Commands_Read_GeoLayers.addAction(self.Menu_Commands_Read_ReadGeoLayerFromDelimitedFile)

        # ReadGeoLayerFromGeoJSON
        self.Menu_Commands_Read_ReadGeoLayerFromGeoJSON = QtWidgets.QAction(main_window)
        self.Menu_Commands_Read_ReadGeoLayerFromGeoJSON.setObjectName(
            qt_util.from_utf8("Menu_Commands_GeoLayers_Read_ReadGeoLayerFromGeoJSON"))
        self.Menu_Commands_Read_ReadGeoLayerFromGeoJSON.setText(
            "ReadGeoLayerFromGeoJSON()... <reads a GeoLayer from a .geojson file>")
        self.Menu_Commands_Read_GeoLayers.addAction(self.Menu_Commands_Read_ReadGeoLayerFromGeoJSON)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Read_ReadGeoLayerFromGeoJSON.triggered.connect(
            functools.partial(self.new_command_editor, "ReadGeoLayerFromGeoJSON"))

        # ReadGeoLayersFromShapefile
        self.Menu_Commands_Read_ReadGeoLayerFromShapefile = QtWidgets.QAction(main_window)
        self.Menu_Commands_Read_ReadGeoLayerFromShapefile.setObjectName(
            qt_util.from_utf8("GeoLayers_Read_ReadGeoLayerFromShapefile"))
        self.Menu_Commands_Read_ReadGeoLayerFromShapefile.setText(
            "ReadGeoLayerFromShapefile()... <reads a GeoLayer from a shapefile>")
        self.Menu_Commands_Read_GeoLayers.addAction(self.Menu_Commands_Read_ReadGeoLayerFromShapefile)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Read_ReadGeoLayerFromShapefile.triggered.connect(
            functools.partial(self.new_command_editor, "ReadGeoLayerFromShapefile"))

        # ReadGeoLayersFromFGDB
        self.Menu_Commands_Read_ReadGeoLayersFromFGDB = QtWidgets.QAction(main_window)
        self.Menu_Commands_Read_ReadGeoLayersFromFGDB.setObjectName(
            qt_util.from_utf8("GeoLayers_Read_ReadGeoLayersFromFGDB"))
        self.Menu_Commands_Read_ReadGeoLayersFromFGDB.setText(
            "ReadGeoLayersFromFGDB()... <reads 1+ GeoLayer(s) from the feature classes of a file geodatabase>")
        self.Menu_Commands_Read_GeoLayers.addAction(self.Menu_Commands_Read_ReadGeoLayersFromFGDB)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Read_ReadGeoLayersFromFGDB.triggered.connect(
            functools.partial(self.new_command_editor, "ReadGeoLayersFromFGDB"))

        # ReadGeoLayersFromFolder
        self.Menu_Commands_Read_ReadGeoLayersFromFolder = QtWidgets.QAction(main_window)
        self.Menu_Commands_Read_ReadGeoLayersFromFolder.setObjectName(
            qt_util.from_utf8("GeoLayers_Read_ReadGeoLayersFromFolder"))
        self.Menu_Commands_Read_ReadGeoLayersFromFolder.setText(
            "ReadGeoLayersFromFolder()... <reads 1+ GeoLayer(s) from a local folder>")
        self.Menu_Commands_Read_GeoLayers.addAction(self.Menu_Commands_Read_ReadGeoLayersFromFolder)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Read_ReadGeoLayersFromFolder.triggered.connect(
            functools.partial(self.new_command_editor, "ReadGeoLayersFromFolder"))

        # Commands / Fill GeoLayer Missing Data menu (disabled)
        self.Menu_Commands_FillGeoLayerMissingData = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_FillGeoLayerMissingData.setObjectName(
            qt_util.from_utf8("Menu_Commands_FillGeoLayerMissingData"))
        self.Menu_Commands_FillGeoLayerMissingData.setTitle("Fill GeoLayer Missing Data")
        self.Menu_Commands_FillGeoLayerMissingData.setEnabled(False)
        self.Menu_Commands.addAction(self.Menu_Commands_FillGeoLayerMissingData.menuAction())

        # Commands / Set Contents - GeoLayers menu
        self.Menu_Commands_SetGeoLayer_Contents = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_SetGeoLayer_Contents.setObjectName(
            qt_util.from_utf8("Menu_Commands_SetContents_GeoLayers"))
        self.Menu_Commands_SetGeoLayer_Contents.setTitle("Set GeoLayer Contents")
        self.Menu_Commands.addAction(self.Menu_Commands_SetGeoLayer_Contents.menuAction())

        # AddGeoLayerAttribute
        self.Menu_Commands_SetContents_AddGeoLayerAttribute = QtWidgets.QAction(main_window)
        self.Menu_Commands_SetContents_AddGeoLayerAttribute.setObjectName(
            qt_util.from_utf8("Menu_Commands_SetContents_AddGeoLayerAttribute"))
        self.Menu_Commands_SetContents_AddGeoLayerAttribute.setText(
            "AddGeoLayerAttribute()... <add an attribute to a GeoLayer>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_SetContents_AddGeoLayerAttribute.triggered.connect(
            functools.partial(self.new_command_editor, "AddGeoLayerAttribute"))
        self.Menu_Commands_SetGeoLayer_Contents.addAction(self.Menu_Commands_SetContents_AddGeoLayerAttribute)

        # RemoveGeoLayerAttributes
        self.Menu_Commands_SetContents_RemoveGeoLayerAttributes = QtWidgets.QAction(main_window)
        self.Menu_Commands_SetContents_RemoveGeoLayerAttributes.setObjectName(
            qt_util.from_utf8("Menu_Commnads_SetContents_RemoveGeoLayerAttributes"))
        self.Menu_Commands_SetContents_RemoveGeoLayerAttributes.setText(
            "RemoveGeoLayerAttributes()... <remove one or more attributes from GeoLayer>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_SetContents_RemoveGeoLayerAttributes.triggered.connect(
            functools.partial(self.new_command_editor, "RemoveGeoLayerAttributes"))
        self.Menu_Commands_SetGeoLayer_Contents.addAction(self.Menu_Commands_SetContents_RemoveGeoLayerAttributes)

        # RenameGeoLayerAttribute
        self.Menu_Commands_SetContents_RenameGeoLayerAttribute = QtWidgets.QAction(main_window)
        self.Menu_Commands_SetContents_RenameGeoLayerAttribute.setObjectName(
            qt_util.from_utf8("Menu_Commands_SetContents_RenameGeoLayerAttribute"))
        self.Menu_Commands_SetContents_RenameGeoLayerAttribute.setText(
            "RenameGeoLayerAttribute()... <rename a GeoLayer's attribute>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_SetContents_RenameGeoLayerAttribute.triggered.connect(
            functools.partial(self.new_command_editor, "RenameGeoLayerAttribute"))
        self.Menu_Commands_SetGeoLayer_Contents.addAction(self.Menu_Commands_SetContents_RenameGeoLayerAttribute)

        # SetGeoLayerCRS
        self.Menu_Commands_SetContents_SetGeoLayerCRS = QtWidgets.QAction(main_window)
        self.Menu_Commands_SetContents_SetGeoLayerCRS.setObjectName(
            qt_util.from_utf8("Menu_Commands_SetContents_SetGeoLayerCRS"))
        self.Menu_Commands_SetContents_SetGeoLayerCRS.setText(
            "SetGeoLayerCRS()... <sets a GeoLayer's coordinate reference system>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_SetContents_SetGeoLayerCRS.triggered.connect(
            functools.partial(self.new_command_editor, "SetGeoLayerCRS"))
        self.Menu_Commands_SetGeoLayer_Contents.addAction(self.Menu_Commands_SetContents_SetGeoLayerCRS)

        # SetGeoLayerProperty
        self.Menu_Commands_SetContents_SetGeoLayerProperty = QtWidgets.QAction(main_window)
        self.Menu_Commands_SetContents_SetGeoLayerProperty.setObjectName(
            qt_util.from_utf8("Menu_Commands_SetContents_SetGeoLayerProperty"))
        self.Menu_Commands_SetContents_SetGeoLayerProperty.setText(
            "SetGeoLayerProperty()... <set a GeoLayer property>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_SetContents_SetGeoLayerProperty.triggered.connect(
            functools.partial(self.new_command_editor, "SetGeoLayerProperty"))
        self.Menu_Commands_SetGeoLayer_Contents.addAction(self.Menu_Commands_SetContents_SetGeoLayerProperty)

        # Commands / Manipulate GeoLayer menu
        self.Menu_Commands_Manipulate_GeoLayers = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Manipulate_GeoLayers.setObjectName(
            qt_util.from_utf8("Menu_Commands_Manipulate_GeoLayers"))
        self.Menu_Commands_Manipulate_GeoLayers.setTitle("Manipulate GeoLayer")
        self.Menu_Commands.addAction(self.Menu_Commands_Manipulate_GeoLayers.menuAction())

        # ClipGeoLayer
        self.Menu_Commands_Manipulate_ClipGeoLayer = QtWidgets.QAction(main_window)
        self.Menu_Commands_Manipulate_ClipGeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_Manipulate_ClipGeoLayer"))
        self.Menu_Commands_Manipulate_ClipGeoLayer.setText(
            "ClipGeoLayer()... <clip a GeoLayer by the boundary of another GeoLayer>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Manipulate_ClipGeoLayer.triggered.connect(
            functools.partial(self.new_command_editor, "ClipGeoLayer"))
        self.Menu_Commands_Manipulate_GeoLayers.addAction(self.Menu_Commands_Manipulate_ClipGeoLayer)

        # IntersectGeoLayer
        self.Menu_Commands_Manipulate_IntersectGeoLayer = QtWidgets.QAction(main_window)
        self.Menu_Commands_Manipulate_IntersectGeoLayer.setObjectName(
            qt_util.from_utf8("Menu_commands_Manipulate_IntersectGeoLayer"))
        self.Menu_Commands_Manipulate_IntersectGeoLayer.setText(
            "IntersectGeoLayer()... <intersects a GeoLayer by another GeoLayer>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Manipulate_IntersectGeoLayer.triggered.connect(
            functools.partial(self.new_command_editor, "IntersectGeoLayer"))
        self.Menu_Commands_Manipulate_GeoLayers.addAction(
            self.Menu_Commands_Manipulate_IntersectGeoLayer)

        # MergeGeoLayers
        self.Menu_Commands_Manipulate_MergeGeoLayers = QtWidgets.QAction(main_window)
        self.Menu_Commands_Manipulate_MergeGeoLayers.setObjectName(
            qt_util.from_utf8("Menu_Commands_Manipulate_MergeGeoLayers"))
        self.Menu_Commands_Manipulate_MergeGeoLayers.setText(
            "MergeGeoLayers()... <merge multiple GeoLayers into one GeoLayer>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Manipulate_MergeGeoLayers.triggered.connect(
            functools.partial(self.new_command_editor, "MergeGeoLayers"))
        self.Menu_Commands_Manipulate_GeoLayers.addAction(self.Menu_Commands_Manipulate_MergeGeoLayers)

        # SimplifyGeoLayerGeometry
        self.Menu_Commands_Manipulate_SimplifyGeoLayerGeometry = QtWidgets.QAction(main_window)
        self.Menu_Commands_Manipulate_SimplifyGeoLayerGeometry.setObjectName(
            qt_util.from_utf8("Menu_Commands_Manipulate_SimplifyGeoLayerGeometry"))
        self.Menu_Commands_Manipulate_SimplifyGeoLayerGeometry.setText(
            "SimplifyGeoLayerGeometry()... <decreases the vertices in a polygon or line GeoLayer>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Manipulate_SimplifyGeoLayerGeometry.triggered.connect(
            functools.partial(self.new_command_editor, "SimplifyGeoLayerGeometry"))
        self.Menu_Commands_Manipulate_GeoLayers.addAction(
            self.Menu_Commands_Manipulate_SimplifyGeoLayerGeometry)

        # SplitGeoLayerByAttribute
        self.Menu_Commands_Manipulate_SplitGeoLayerByAttribute = QtWidgets.QAction(main_window)
        self.Menu_Commands_Manipulate_SplitGeoLayerByAttribute.setObjectName(
            qt_util.from_utf8("Menu_Commands_Manipulate_SplitGeoLayerByAttribute"))
        self.Menu_Commands_Manipulate_SplitGeoLayerByAttribute.setText(
            "SplitGeoLayerByAttribute()... <splits a GeoLayer into multiple GeoLayers by an attribute>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Manipulate_SplitGeoLayerByAttribute.triggered.connect(
            functools.partial(self.new_command_editor, "SplitGeoLayerByAttribute"))
        self.Menu_Commands_Manipulate_GeoLayers.addAction(
            self.Menu_Commands_Manipulate_SplitGeoLayerByAttribute)

        # Commands / Analyze GeoLayer menu (disabled)
        self.Menu_Commands_Analyze_GeoLayers = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Analyze_GeoLayers.setObjectName(
            qt_util.from_utf8("Menu_Commands_Analyze_GeoLayers"))
        self.Menu_Commands_Analyze_GeoLayers.setTitle("Analyze GeoLayer")
        self.Menu_Commands_Analyze_GeoLayers.setEnabled(False)
        self.Menu_Commands.addAction(self.Menu_Commands_Analyze_GeoLayers.menuAction())

        # Commands / Check GeoLayer menu (disabled)
        self.Menu_Commands_Check_GeoLayers = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Check_GeoLayers.setObjectName(
            qt_util.from_utf8("Menu_Commands_Check_GeoLayers"))
        self.Menu_Commands_Check_GeoLayers.setTitle("Check GeoLayer")
        self.Menu_Commands_Check_GeoLayers.setEnabled(False)
        self.Menu_Commands.addAction(self.Menu_Commands_Check_GeoLayers.menuAction())

        # Commands / Write GeoLayer menu
        self.Menu_Commands_Write_GeoLayers = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Write_GeoLayers.setObjectName(
            qt_util.from_utf8("Menu_Commands_Write_GeoLayers"))
        self.Menu_Commands_Write_GeoLayers.setTitle("Write GeoLayer")
        self.Menu_Commands.addAction(self.Menu_Commands_Write_GeoLayers.menuAction())

        # WriteGeoLayerToDelimitedFile
        self.Menu_Commands_Write_WriteGeoLayerToDelimitedFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_Write_WriteGeoLayerToDelimitedFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_Write_WriteGeoLayerToDelimitedFile"))
        self.Menu_Commands_Write_WriteGeoLayerToDelimitedFile.setText(
            "WriteGeoLayerToDelimitedFile()... write GeoLayer to a file in delimited file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Write_WriteGeoLayerToDelimitedFile.triggered.connect(
            functools.partial(self.new_command_editor, "WriteGeoLayerToDelimitedFile"))
        self.Menu_Commands_Write_GeoLayers.addAction(self.Menu_Commands_Write_WriteGeoLayerToDelimitedFile)

        # WriteGeoLayerToGeoJSON
        self.Menu_Commands_Write_WriteGeoLayerToGeoJSON = QtWidgets.QAction(main_window)
        self.Menu_Commands_Write_WriteGeoLayerToGeoJSON.setObjectName(
            qt_util.from_utf8("Menu_Commands_Write_WriteGeoLayerToGeoJSON"))
        self.Menu_Commands_Write_WriteGeoLayerToGeoJSON.setText(
            "WriteGeoLayerToGeoJSON()... <write GeoLayer to a file in GeoJSON format>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Write_WriteGeoLayerToGeoJSON.triggered.connect(
            functools.partial(self.new_command_editor, "WriteGeoLayerToGeoJSON"))
        self.Menu_Commands_Write_GeoLayers.addAction(self.Menu_Commands_Write_WriteGeoLayerToGeoJSON)

        # WriteGeoLayerToKML
        self.Menu_Commands_Write_WriteGeoLayerToKML = QtWidgets.QAction(main_window)
        self.Menu_Commands_Write_WriteGeoLayerToKML.setObjectName(
            qt_util.from_utf8("Menu_Commands_Write_WriteGeoLayerToKML"))
        self.Menu_Commands_Write_WriteGeoLayerToKML.setText(
            "WriteGeoLayerToKML()... <write GeoLayer to a file in KML format>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Write_WriteGeoLayerToKML.triggered.connect(
            functools.partial(self.new_command_editor, "WriteGeoLayerToKML"))
        self.Menu_Commands_Write_GeoLayers.addAction(self.Menu_Commands_Write_WriteGeoLayerToKML)

        # WriteGeoLayerToShapefile
        self.Menu_Commands_Write_WriteGeoLayerToShapefile = QtWidgets.QAction(main_window)
        self.Menu_Commands_Write_WriteGeoLayerToShapefile.setObjectName(
            qt_util.from_utf8("Menu_Commands_Write_WriteGeoLayerToShapefile"))
        self.Menu_Commands_Write_WriteGeoLayerToShapefile.setText(
            "WriteGeoLayerToShapefile()... <write GeoLayer to a file shapefile format>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Write_WriteGeoLayerToShapefile.triggered.connect(
            functools.partial(self.new_command_editor, "WriteGeoLayerToShapefile"))
        self.Menu_Commands_Write_GeoLayers.addAction(self.Menu_Commands_Write_WriteGeoLayerToShapefile)

        self.Menu_Commands.addSeparator()

        # Commands / Datastore Processing menu
        self.Menu_Commands_DatastoreProcessing = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_DatastoreProcessing.setObjectName(
            qt_util.from_utf8("Menu_Commands_DatastoreProcessing"))
        self.Menu_Commands_DatastoreProcessing.setTitle("Datastore Processing")
        self.Menu_Commands.addAction(self.Menu_Commands_DatastoreProcessing.menuAction())

        # OpenDataStore
        self.Menu_Commands_DatastoreProcessing_OpenDataStore = QtWidgets.QAction(main_window)
        self.Menu_Commands_DatastoreProcessing_OpenDataStore.setObjectName(
            qt_util.from_utf8("Menu_Commands_DatastoreProcessing_OpenDataStore"))
        self.Menu_Commands_DatastoreProcessing_OpenDataStore.setText(
            "OpenDataStore()... <create a DataStore connection>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_DatastoreProcessing_OpenDataStore.triggered.connect(
            functools.partial(self.new_command_editor, "OpenDataStore"))
        self.Menu_Commands_DatastoreProcessing.addAction(self.Menu_Commands_DatastoreProcessing_OpenDataStore)

        # ReadTableFromDataStore
        self.Menu_Commands_DatastoreProcessing_ReadTableFromDataStore = QtWidgets.QAction(main_window)
        self.Menu_Commands_DatastoreProcessing_ReadTableFromDataStore.setObjectName(
            qt_util.from_utf8("Menu_Commands_DatastoreProcessing_ReadTableFromDataStore"))
        self.Menu_Commands_DatastoreProcessing_ReadTableFromDataStore.setText(
            "ReadTableFromDataStore()... <read a table from a DataStore>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_DatastoreProcessing_ReadTableFromDataStore.triggered.connect(
            functools.partial(self.new_command_editor, "ReadTableFromDataStore"))
        self.Menu_Commands_DatastoreProcessing.addAction(self.Menu_Commands_DatastoreProcessing_ReadTableFromDataStore)

        # Commands / Network Processing menu (disabled)
        self.Menu_Commands_NetworkProcessing = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_NetworkProcessing.setObjectName(
            qt_util.from_utf8("Menu_Commands_NetworkProcessing"))
        self.Menu_Commands_NetworkProcessing.setTitle("Network Processing")
        self.Menu_Commands_NetworkProcessing.setEnabled(False)
        self.Menu_Commands.addAction(self.Menu_Commands_NetworkProcessing.menuAction())

        # Commands / Spreadsheet Processing menu (disabled)
        self.Menu_Commands_SpreadsheetProcessing = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_SpreadsheetProcessing.setObjectName(
            qt_util.from_utf8("Menu_Commands_SpreadsheetProcessing"))
        self.Menu_Commands_SpreadsheetProcessing.setTitle("Spreadsheet Processing")
        self.Menu_Commands_SpreadsheetProcessing.setEnabled(False)
        self.Menu_Commands.addAction(self.Menu_Commands_SpreadsheetProcessing.menuAction())

        # Commands / Template Processing menu (disabled)
        self.Menu_Commands_TemplateProcessing = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_TemplateProcessing.setObjectName(
            qt_util.from_utf8("Menu_Commands_TemplateProcessing"))
        self.Menu_Commands_TemplateProcessing.setTitle("Template Processing")
        self.Menu_Commands_TemplateProcessing.setEnabled(False)
        self.Menu_Commands.addAction(self.Menu_Commands_TemplateProcessing.menuAction())

        # Commands / Visualization Processing (disabled)
        self.Menu_Commands_VisualizationProcessing = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_VisualizationProcessing.setObjectName(
            qt_util.from_utf8("Menu_Commands_VisualizationProcessing"))
        self.Menu_Commands_VisualizationProcessing.setTitle("Visualization Processing")
        self.Menu_Commands_VisualizationProcessing.setEnabled(False)
        self.Menu_Commands.addAction(self.Menu_Commands_VisualizationProcessing.menuAction())

        # Commands / General - Comments menu
        self.Menu_Commands_General_Comments = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_General_Comments.setObjectName(qt_util.from_utf8("Menu_Commands_General_Comments"))
        self.Menu_Commands_General_Comments.setTitle("General - Comments")
        self.Menu_Commands.addSeparator()
        self.Menu_Commands.addAction(self.Menu_Commands_General_Comments.menuAction())

        # Comments / General - Comments / Single menu
        self.Menu_Commands_General_Comments_Single = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_Comments_Single.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_Comments_Single"))
        self.Menu_Commands_General_Comments_Single.setText("# comments <enter 1+ comments each starting with #>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_Comments_Single.triggered.connect(
            functools.partial(self.new_command_editor, "#"))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_Single)

        # Comments / General - Comments / Multi-line menus
        self.Menu_Commands_General_Comments_MultipleStart = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_Comments_MultipleStart.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_Comments_MultipleStart"))
        self.Menu_Commands_General_Comments_MultipleStart.setText("/* <start multi-line comment section> ")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_Comments_MultipleStart.triggered.connect(
            functools.partial(self.new_command_editor, "/*"))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_MultipleStart)

        # MultipleEnd
        self.Menu_Commands_General_Comments_MultipleEnd = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_Comments_MultipleEnd.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_Comments_MultipleEnd"))
        self.Menu_Commands_General_Comments_MultipleEnd.setText("*/ <end multi-line comment section>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_Comments_MultipleEnd.triggered.connect(
            functools.partial(self.new_command_editor, "*/"))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_MultipleEnd)
        self.Menu_Commands_General_Comments.addSeparator()

        # Comments / General - Comments / Enabled menu
        self.Menu_Commands_General_Comments_EnabledFalse = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_Comments_EnabledFalse.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_Comments_Enabled"))
        self.Menu_Commands_General_Comments_EnabledFalse.setText("#@enabled False <disables the test>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_Comments_EnabledFalse.triggered.connect(
            functools.partial(self.new_command_editor, "#@enabled False"))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_EnabledFalse)

        # Comments / General - Comments / Expected Status menus
        # Comments / General - Comments / Expected Status Fail
        self.Menu_Commands_General_Comments_ExpectedStatusFail = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_Comments_ExpectedStatusFail.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_Comments_ExpectedStatusFail"))
        self.Menu_Commands_General_Comments_ExpectedStatusFail.setText(
            "#@expectedStatus Failure <used to test commands>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_Comments_ExpectedStatusFail.triggered.connect(
            functools.partial(self.new_command_editor, "#@expectedStatus Failure"))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_ExpectedStatusFail)

        # Comments / General - Comments / Expected Status Warn
        self.Menu_Commands_General_Comments_ExpectedStatusWarn = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_Comments_ExpectedStatusWarn.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_Comments_ExpectedStatusWarn"))
        self.Menu_Commands_General_Comments_ExpectedStatusWarn.setText(
            "#@expectedStatus Warning <used to test commands>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_Comments_ExpectedStatusWarn.triggered.connect(
            functools.partial(self.new_command_editor, "#@expectedStatus Warning"))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_ExpectedStatusWarn)
        # Add to menu bar
        self.menubar.addAction(self.Menu_Commands.menuAction())

        self.Menu_Commands_General_Comments.addSeparator()

        # Blank
        self.Menu_Commands_General_Comments_Blank = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_Comments_Blank.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_Comments_Blank"))
        self.Menu_Commands_General_Comments_Blank.setText(
            "Blank()... <used for blank lines>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_Comments_Blank.triggered.connect(
            functools.partial(self.new_command_editor, "Blank"))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_Blank)

        # Commands / General - File Handling
        self.Menu_Commands_General_FileHandling = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_General_FileHandling.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_FileHandling"))
        self.Menu_Commands_General_FileHandling.setTitle("General - File Handling")
        self.Menu_Commands.addAction(self.Menu_Commands_General_FileHandling.menuAction())

        # CopyFile
        self.Menu_Commands_General_FileHandling_CopyFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_FileHandling_CopyFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_FileHandling_CopyFile"))
        self.Menu_Commands_General_FileHandling_CopyFile.setText(
            "CopyFile()... <copy a file to a new file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_FileHandling_CopyFile.triggered.connect(
            functools.partial(self.new_command_editor, "CopyFile"))
        self.Menu_Commands_General_FileHandling.addAction(self.Menu_Commands_General_FileHandling_CopyFile)

        # ListFiles
        self.Menu_Commands_General_FileHandling_ListFiles = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_FileHandling_ListFiles.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_FileHandling_ListFiles"))
        self.Menu_Commands_General_FileHandling_ListFiles.setText(
            "ListFiles()... <list the files and folder within a folder or a URL>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_FileHandling_ListFiles.triggered.connect(
            functools.partial(self.new_command_editor, "ListFiles"))
        self.Menu_Commands_General_FileHandling.addAction(self.Menu_Commands_General_FileHandling_ListFiles)

        # RemoveFile
        self.Menu_Commands_General_FileHandling_RemoveFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_FileHandling_RemoveFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_FileHandling_RemoveFile"))
        self.Menu_Commands_General_FileHandling_RemoveFile.setText(
            "RemoveFile()... <remove a file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_FileHandling_RemoveFile.triggered.connect(
            functools.partial(self.new_command_editor, "RemoveFile"))
        self.Menu_Commands_General_FileHandling.addAction(self.Menu_Commands_General_FileHandling_RemoveFile)

        # UnzipFile
        self.Menu_Commands_General_FileHandling_UnzipFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_FileHandling_UnzipFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_FileHandling_UnzipFile"))
        self.Menu_Commands_General_FileHandling_UnzipFile.setText(
            "UnzipFile()... <unzip a file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_FileHandling_UnzipFile.triggered.connect(
            functools.partial(self.new_command_editor, "UnzipFile"))
        self.Menu_Commands_General_FileHandling.addAction(self.Menu_Commands_General_FileHandling_UnzipFile)

        # WebGet
        self.Menu_Commands_General_FileHandling_WebGet = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_FileHandling_WebGet.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_FileHandling_WebGet"))
        self.Menu_Commands_General_FileHandling_WebGet.setText(
            "WebGet()... <download a file from URL>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_FileHandling_WebGet.triggered.connect(
            functools.partial(self.new_command_editor, "WebGet"))
        self.Menu_Commands_General_FileHandling.addAction(self.Menu_Commands_General_FileHandling_WebGet)

        # Commands / General - Logging and Messaging menu
        self.Menu_Commands_General_LoggingMessaging = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_General_LoggingMessaging.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_LoggingMessaging"))
        self.Menu_Commands_General_LoggingMessaging.setTitle("General - Logging and Messaging")
        self.Menu_Commands.addAction(self.Menu_Commands_General_LoggingMessaging.menuAction())

        # Message
        self.Menu_Commands_General_LoggingMessaging_Message = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_LoggingMessaging_Message.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_LoggingMessaging_Message"))
        self.Menu_Commands_General_LoggingMessaging_Message.setText(
            "Message()... <print a message to the log file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_LoggingMessaging_Message.triggered.connect(
            functools.partial(self.new_command_editor, "Message"))
        self.Menu_Commands_General_LoggingMessaging.addAction(self.Menu_Commands_General_LoggingMessaging_Message)

        # StartLog
        self.Menu_Commands_General_LoggingMessaging_StartLog = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_LoggingMessaging_StartLog.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_LoggingMessaging_StartLog"))
        self.Menu_Commands_General_LoggingMessaging_StartLog.setText(
            "StartLog()... <start a new log file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_LoggingMessaging_StartLog.triggered.connect(
            functools.partial(self.new_command_editor, "StartLog"))
        self.Menu_Commands_General_LoggingMessaging.addAction(self.Menu_Commands_General_LoggingMessaging_StartLog)

        # Commands / General - Running and Properties menu
        self.Menu_Commands_General_RunningProperties = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_General_RunningProperties.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties"))
        self.Menu_Commands_General_RunningProperties.setTitle("General - Running and Properties")
        self.Menu_Commands.addAction(self.Menu_Commands_General_RunningProperties.menuAction())

        # If
        self.Menu_Commands_General_RunningProperties_If = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_RunningProperties_If.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties_If"))
        self.Menu_Commands_General_RunningProperties_If.setText(
            "If()... <indicate the start of an 'if' block>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_RunningProperties_If.triggered.connect(
            functools.partial(self.new_command_editor, "If"))
        self.Menu_Commands_General_RunningProperties.addAction(self.Menu_Commands_General_RunningProperties_If)

        # EndIf
        self.Menu_Commands_General_RunningProperties_EndIf = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_RunningProperties_EndIf.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties_EndIf"))
        self.Menu_Commands_General_RunningProperties_EndIf.setText(
            "EndIf()... <indicate the end of an 'if' block>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_RunningProperties_EndIf.triggered.connect(
            functools.partial(self.new_command_editor, "EndIf"))
        self.Menu_Commands_General_RunningProperties.addAction(self.Menu_Commands_General_RunningProperties_EndIf)

        self.Menu_Commands_General_RunningProperties.addSeparator()

        # For
        self.Menu_Commands_General_RunningProperties_For = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_RunningProperties_For.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties_For"))
        self.Menu_Commands_General_RunningProperties_For.setText(
            "For()... <indicate the start of a 'for' block>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_RunningProperties_For.triggered.connect(
            functools.partial(self.new_command_editor, "For"))
        self.Menu_Commands_General_RunningProperties.addAction(self.Menu_Commands_General_RunningProperties_For)

        # EndFor
        self.Menu_Commands_General_RunningProperties_EndFor = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_RunningProperties_EndFor.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties_EndFor"))
        self.Menu_Commands_General_RunningProperties_EndFor.setText(
            "EndFor()... <indicate the end of a 'for' block>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_RunningProperties_EndFor.triggered.connect(
            functools.partial(self.new_command_editor, "EndFor"))
        self.Menu_Commands_General_RunningProperties.addAction(self.Menu_Commands_General_RunningProperties_EndFor)

        self.Menu_Commands_General_RunningProperties.addSeparator()

        # RunCommands
        self.Menu_Commands_General_RunningProperties_RunCommands = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_RunningProperties_RunCommands.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties_RunCommands"))
        self.Menu_Commands_General_RunningProperties_RunCommands.setText(
            "RunCommands()... <run a command file, useful to automate running all tests or a multi-step workflow>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_RunningProperties_RunCommands.triggered.connect(
            functools.partial(self.new_command_editor, "RunCommands"))
        self.Menu_Commands_General_RunningProperties.addAction(self.Menu_Commands_General_RunningProperties_RunCommands)

        # RunGdalProgram
        self.Menu_Commands_General_RunningProperties_RunGdalProgram = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_RunningProperties_RunGdalProgram.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties_RunGdalProgram"))
        self.Menu_Commands_General_RunningProperties_RunGdalProgram.setText(
            "RunGdalProgram()... <run GDAL raster layer processing program>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_RunningProperties_RunGdalProgram.triggered.connect(
            functools.partial(self.new_command_editor, "RunGdalProgram"))
        self.Menu_Commands_General_RunningProperties.addAction(
            self.Menu_Commands_General_RunningProperties_RunGdalProgram)

        # RunOgrProgram
        self.Menu_Commands_General_RunningProperties_RunOgrProgram = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_RunningProperties_RunOgrProgram.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties_RunOgrProgram"))
        self.Menu_Commands_General_RunningProperties_RunOgrProgram.setText(
            "RunOgrProgram()... <run OGR vector layer processing program>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_RunningProperties_RunOgrProgram.triggered.connect(
            functools.partial(self.new_command_editor, "RunOgrProgram"))
        self.Menu_Commands_General_RunningProperties.addAction(
            self.Menu_Commands_General_RunningProperties_RunOgrProgram)

        # RunProgram
        self.Menu_Commands_General_RunningProperties_RunProgram = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_RunningProperties_RunProgram.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties_RunProgram"))
        self.Menu_Commands_General_RunningProperties_RunProgram.setText(
            "RunProgram()... <run a program>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_RunningProperties_RunProgram.triggered.connect(
            functools.partial(self.new_command_editor, "RunProgram"))
        self.Menu_Commands_General_RunningProperties.addAction(self.Menu_Commands_General_RunningProperties_RunProgram)

        # SetProperty
        self.Menu_Commands_General_RunningProperties_SetProperty = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_RunningProperties_SetProperty.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties_SetProperty"))
        self.Menu_Commands_General_RunningProperties_SetProperty.setText(
            "SetProperty()... <set a GeoProcessor property>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_RunningProperties_SetProperty.triggered.connect(
            functools.partial(self.new_command_editor, "SetProperty"))
        self.Menu_Commands_General_RunningProperties.addAction(self.Menu_Commands_General_RunningProperties_SetProperty)

        # SetPropertyFromGeoLayer
        self.Menu_Commands_General_RunningProperties_SetPropertyFromGeoLayer = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_RunningProperties_SetPropertyFromGeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties_SetPropertyFromGeoLayer"))
        self.Menu_Commands_General_RunningProperties_SetPropertyFromGeoLayer.setText(
            "SetPropertyFromGeoLayer()... <set a GeoProcessor property from a GeoLayer property>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_RunningProperties_SetPropertyFromGeoLayer.triggered.connect(
            functools.partial(self.new_command_editor, "SetPropertyFromGeoLayer"))
        self.Menu_Commands_General_RunningProperties.addAction(
            self.Menu_Commands_General_RunningProperties_SetPropertyFromGeoLayer)

        # WritePropertiesToFile
        self.Menu_Commands_General_RunningProperties_WritePropertiesToFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_RunningProperties_WritePropertiesToFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties_WritePropertiesToFile"))
        self.Menu_Commands_General_RunningProperties_WritePropertiesToFile.setText(
            "WritePropertiesToFile()... <write properties to file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_RunningProperties_WritePropertiesToFile.triggered.connect(
            functools.partial(self.new_command_editor, "WritePropertiesToFile"))
        self.Menu_Commands_General_RunningProperties.addAction(
            self.Menu_Commands_General_RunningProperties_WritePropertiesToFile)

        # Commands / General - Test Processing menu
        self.Menu_Commands_General_TestProcessing = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_General_TestProcessing.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_TestProcessing"))
        self.Menu_Commands_General_TestProcessing.setTitle("General - Test Processing")
        self.Menu_Commands.addAction(self.Menu_Commands_General_TestProcessing.menuAction())

        # CompareFiles
        self.Menu_Commands_General_TestProcessing_CompareFiles = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_TestProcessing_CompareFiles.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_TestProcessing_CompareFiles"))
        self.Menu_Commands_General_TestProcessing_CompareFiles.setText(
            "CompareFiles()... <compare files and optionally warn/fail if different/same>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_TestProcessing_CompareFiles.triggered.connect(
            functools.partial(self.new_command_editor, "CompareFiles"))
        self.Menu_Commands_General_TestProcessing.addAction(
            self.Menu_Commands_General_TestProcessing_CompareFiles)

        # CreateRegressionTestCommandFile
        self.Menu_Commands_General_TestProcessing_CreateRegressionTestCommandFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_TestProcessing_CreateRegressionTestCommandFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_TestProcessing_CreateRegressionTestCommandFile"))
        self.Menu_Commands_General_TestProcessing_CreateRegressionTestCommandFile.setText(
            "CreateRegressionTestCommandFile()... <create a master command file to automate running all tests>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_TestProcessing_CreateRegressionTestCommandFile.triggered.connect(
            functools.partial(self.new_command_editor, "CreateRegressionTestCommandFile"))
        self.Menu_Commands_General_TestProcessing.addAction(
            self.Menu_Commands_General_TestProcessing_CreateRegressionTestCommandFile)

        # StartRegressionTestResultsReport
        self.Menu_Commands_General_TestProcessing_StartRegressionTestResultsReport = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_TestProcessing_StartRegressionTestResultsReport.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_TestProcessing_StartRegressionTestResultsReport"))
        self.Menu_Commands_General_TestProcessing_StartRegressionTestResultsReport.setText(
            "StartRegressionTestResultsReport()... <start (open) a file to receive regression test results>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_TestProcessing_StartRegressionTestResultsReport.triggered.connect(
            functools.partial(self.new_command_editor, "StartRegressionTestResultsReport"))
        self.Menu_Commands_General_TestProcessing.addAction(
            self.Menu_Commands_General_TestProcessing_StartRegressionTestResultsReport)

        # WriteCommandSummaryToFile
        self.Menu_Commands_General_TestProcessing_WriteCommandSummaryToFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_TestProcessing_WriteCommandSummaryToFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_TestProcessing_WriteCommandSummaryToFile"))
        self.Menu_Commands_General_TestProcessing_WriteCommandSummaryToFile.setText(
            "WriteCommandSummaryToFile()... <write a summary of command log messages to a file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_TestProcessing_WriteCommandSummaryToFile.triggered.connect(
            functools.partial(self.new_command_editor, "WriteCommandSummaryToFile"))
        self.Menu_Commands_General_TestProcessing.addAction(
            self.Menu_Commands_General_TestProcessing_WriteCommandSummaryToFile)

        # WriteGeoLayerPropertiesToFile
        self.Menu_Commands_General_TestProcessing_WriteGeoLayerPropertiesToFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_TestProcessing_WriteGeoLayerPropertiesToFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_TestProcessing_WriteGeoLayerPropertiesToFile"))
        self.Menu_Commands_General_TestProcessing_WriteGeoLayerPropertiesToFile.setText(
            "WriteGeoLayerPropertiesToFile()... <write GeoLayer properties to file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_TestProcessing_WriteGeoLayerPropertiesToFile.triggered.connect(
            functools.partial(self.new_command_editor, "WriteGeoLayerPropertiesToFile"))
        self.Menu_Commands_General_TestProcessing.addAction(
            self.Menu_Commands_General_TestProcessing_WriteGeoLayerPropertiesToFile)

        # ============================================================================================================
        # Commands(Raster) menu
        # ============================================================================================================

        self.Menu_Commands_Raster = QtWidgets.QMenu(self.menubar)
        self.Menu_Commands_Raster.setObjectName(qt_util.from_utf8("Menu_Commands_Raster"))
        self.Menu_Commands_Raster.setTitle("Commands(Raster)")
        # Add to menu bar
        self.menubar.addAction(self.Menu_Commands_Raster.menuAction())

        # Commands / Create - Raster GeoLayer menu
        self.Menu_Commands_Raster_Create_RasterGeoLayers = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Raster_Create_RasterGeoLayers.setObjectName(
            qt_util.from_utf8("Menu_Commands_Raster_Create_RasterGeoLayers"))
        self.Menu_Commands_Raster_Create_RasterGeoLayers.setTitle("Create Raster GeoLayers")
        self.Menu_Commands_Raster.addAction(self.Menu_Commands_Raster_Create_RasterGeoLayers.menuAction())

        # CreateRasterGeoLayer
        self.Menu_Commands_Raster_Create_CreateRasterGeoLayer = QtWidgets.QAction(main_window)
        self.Menu_Commands_Raster_Create_CreateRasterGeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_Raster_Create_CreateRasterGeoLayer"))
        self.Menu_Commands_Raster_Create_CreateRasterGeoLayer.setText(
            "CreateRasterGeoLayer()... <create a Raster GeoLayer>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Raster_Create_CreateRasterGeoLayer.triggered.connect(
            functools.partial(self.new_command_editor, "CreateRasterGeoLayer"))
        self.Menu_Commands_Raster_Create_RasterGeoLayers.addAction(
            self.Menu_Commands_Raster_Create_CreateRasterGeoLayer)

        # Commands / Read - Raster GeoLayer menu
        self.Menu_Commands_Raster_Read_RasterGeoLayers = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Raster_Read_RasterGeoLayers.setObjectName(
            qt_util.from_utf8("Menu_Commands_Raster_Read_Raster_GeoLayers"))
        self.Menu_Commands_Raster_Read_RasterGeoLayers.setTitle("Read Raster GeoLayers")
        self.Menu_Commands_Raster.addAction(self.Menu_Commands_Raster_Read_RasterGeoLayers.menuAction())

        # ReadRasterGeoLayerFromFile
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_Raster_Read_ReadRasterGeoLayerFromFile"))
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromFile.setText(
            "ReadRasterGeoLayerFromFile()... <read a Raster GeoLayer from a TIF file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromFile.triggered.connect(
            functools.partial(self.new_command_editor, "ReadRasterGeoLayerFromFile"))
        self.Menu_Commands_Raster_Read_RasterGeoLayers.addAction(
            self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromFile)

        # ============================================================================================================
        # Commands(Table) menu
        # ============================================================================================================

        self.Menu_Commands_Table = QtWidgets.QMenu(self.menubar)
        self.Menu_Commands_Table.setObjectName(qt_util.from_utf8("Menu_Commands_Table"))
        self.Menu_Commands_Table.setTitle("Commands(Table)")

        # Commands / Tables / Read menu
        self.Menu_Commands_Tables_Read = QtWidgets.QMenu(self.Menu_Commands_Table)
        self.Menu_Commands_Tables_Read.setObjectName(qt_util.from_utf8("Menu_Commands_Tables_Read"))
        self.Menu_Commands_Tables_Read.setTitle("Read Table")
        self.Menu_Commands_Table.addAction(self.Menu_Commands_Tables_Read.menuAction())

        # ReadTableFromDataStore
        self.Menu_Commands_Table_ReadTableFromDataStore = QtWidgets.QAction(main_window)
        self.Menu_Commands_Table_ReadTableFromDataStore.setObjectName(
            qt_util.from_utf8("Menu_Commands_Table_ReadTableFromDataStore"))
        self.Menu_Commands_Table_ReadTableFromDataStore.setText(
            "ReadTableFromDataStore()... <read a table from a DataStore>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Table_ReadTableFromDataStore.triggered.connect(
            functools.partial(self.new_command_editor, "ReadTableFromDataStore"))
        self.Menu_Commands_Tables_Read.addAction(self.Menu_Commands_Table_ReadTableFromDataStore)

        # ReadTableFromDelimitedFile
        self.Menu_Commands_Table_ReadTableFromDelimitedFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_Table_ReadTableFromDelimitedFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_Table_ReadTableFromDelimitedFile"))
        self.Menu_Commands_Table_ReadTableFromDelimitedFile.setText(
            "ReadTableFromDelimitedFile()... <read a table from a delimited file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Table_ReadTableFromDelimitedFile.triggered.connect(
            functools.partial(self.new_command_editor, "ReadTableFromDelimitedFile"))
        self.Menu_Commands_Tables_Read.addAction(self.Menu_Commands_Table_ReadTableFromDelimitedFile)

        # ReadTableFromExcel
        self.Menu_Commands_Table_ReadTableFromExcel = QtWidgets.QAction(main_window)
        self.Menu_Commands_Table_ReadTableFromExcel.setObjectName(
            qt_util.from_utf8("Menu_Commands_Table_ReadTableFromExcel"))
        self.Menu_Commands_Table_ReadTableFromExcel.setText(
            "ReadTableFromExcel()... <read a table from an Excel file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Table_ReadTableFromExcel.triggered.connect(
            functools.partial(self.new_command_editor, "ReadTableFromExcel"))
        self.Menu_Commands_Tables_Read.addAction(self.Menu_Commands_Table_ReadTableFromExcel)

        # Commands / Tables / Process menu
        self.Menu_Commands_Tables_Process = QtWidgets.QMenu(self.Menu_Commands_Table)
        self.Menu_Commands_Tables_Process.setObjectName(qt_util.from_utf8("Menu_Commands_Tables_Process"))
        self.Menu_Commands_Tables_Process.setTitle("Process Table")
        self.Menu_Commands_Tables_Process.setEnabled(False)
        self.Menu_Commands_Table.addAction(self.Menu_Commands_Tables_Process.menuAction())

        # Commands / Tables / Write menu
        self.Menu_Commands_Tables_Write = QtWidgets.QMenu(self.Menu_Commands_Table)
        self.Menu_Commands_Tables_Write.setObjectName(qt_util.from_utf8("Menu_Commands_Tables_Write"))
        self.Menu_Commands_Tables_Write.setTitle("Write Table")
        self.Menu_Commands_Table.addAction(self.Menu_Commands_Tables_Write.menuAction())
        # Add to menu bar
        self.menubar.addAction(self.Menu_Commands_Table.menuAction())

        # WriteTableToDataStore
        self.Menu_Commands_Table_WriteTableToDataStore = QtWidgets.QAction(main_window)
        self.Menu_Commands_Table_WriteTableToDataStore.setObjectName(
            qt_util.from_utf8("Menu_Commands_Table_WriteTableToDataStore"))
        self.Menu_Commands_Table_WriteTableToDataStore.setText(
            "WriteTableToDataStore()... <write a table to a DataStore>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Table_WriteTableToDataStore.triggered.connect(
            functools.partial(self.new_command_editor, "WriteTableToDataStore"))
        self.Menu_Commands_Tables_Write.addAction(self.Menu_Commands_Table_WriteTableToDataStore)

        # WriteTableToDelimitedFile
        self.Menu_Commands_Table_WriteTableToDelimitedFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_Table_WriteTableToDelimitedFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_Table_WriteTableToDelimitedFile"))
        self.Menu_Commands_Table_WriteTableToDelimitedFile.setText(
            "WriteTableToDelimitedFile()... <write a table to a delimited file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Table_WriteTableToDelimitedFile.triggered.connect(
            functools.partial(self.new_command_editor, "WriteTableToDelimitedFile"))
        self.Menu_Commands_Tables_Write.addAction(self.Menu_Commands_Table_WriteTableToDelimitedFile)

        # WriteTableToExcel
        self.Menu_Commands_Table_WriteTableToExcel = QtWidgets.QAction(main_window)
        self.Menu_Commands_Table_WriteTableToExcel.setObjectName(
            qt_util.from_utf8("Menu_Commands_Table_WriteTableToExcel"))
        self.Menu_Commands_Table_WriteTableToExcel.setText(
            "WriteTableToExcel()... <write a table to an Excel file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Table_WriteTableToExcel.triggered.connect(
            functools.partial(self.new_command_editor, "WriteTableToExcel"))
        self.Menu_Commands_Tables_Write.addAction(self.Menu_Commands_Table_WriteTableToExcel)

        # ============================================================================================================
        # Tools menu
        # ============================================================================================================
        self.Menu_Tools = QtWidgets.QMenu(self.menubar)
        self.Menu_Tools.setObjectName(qt_util.from_utf8("Menu_Tools"))
        self.Menu_Tools.setTitle("Tools")
        # Add Tools menu to menubar
        self.menubar.addAction(self.Menu_Tools.menuAction())

        # Tools / View Log File menu (for current log file from log_util)
        self.Menu_Tools_ViewLog = QtWidgets.QAction(main_window)
        self.Menu_Tools_ViewLog.setObjectName(qt_util.from_utf8("Menu_Tools_ViewLog"))
        self.Menu_Tools_ViewLog.setText("View Log File")
        self.Menu_Tools.addAction(self.Menu_Tools_ViewLog)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Tools_ViewLog.triggered.connect(self.ui_action_view_log_file)

        # Tools / View Startup Log File menu (for startup log file from GeoProcessorAppSession)
        self.Menu_Tools_ViewStartupLog = QtWidgets.QAction(main_window)
        self.Menu_Tools_ViewStartupLog.setObjectName(qt_util.from_utf8("Menu_Tools_ViewStartupLog"))
        self.Menu_Tools_ViewStartupLog.setText("View Startup Log File")
        self.Menu_Tools.addAction(self.Menu_Tools_ViewStartupLog)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Tools_ViewStartupLog.triggered.connect(self.ui_action_view_startup_log_file)

        # ============================================================================================================
        # Help menu
        # ============================================================================================================

        self.Menu_Help = QtWidgets.QMenu(self.menubar)
        self.Menu_Help.setObjectName(qt_util.from_utf8("Menu_Help"))
        self.Menu_Help.setTitle("Help")

        # Help / About GeoProcessor
        self.Menu_Help_About = QtWidgets.QAction(main_window)
        self.Menu_Help_About.setObjectName(qt_util.from_utf8("Menu_Help_About"))
        self.Menu_Help_About.setText("About GeoProcessor")
        self.Menu_Help.addAction(self.Menu_Help_About)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Help_About.triggered.connect(self.ui_action_help_about)

        # Help / Software/System Information
        self.Menu_Help_SoftwareSystemInformation = QtWidgets.QAction(main_window)
        self.Menu_Help_SoftwareSystemInformation.setObjectName(qt_util.from_utf8("Menu_Help_SoftwareSystemInformation"))
        self.Menu_Help_SoftwareSystemInformation.setText("Software/System Information")
        self.Menu_Help.addAction(self.Menu_Help_SoftwareSystemInformation)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Help_SoftwareSystemInformation.triggered.connect(self.ui_action_help_software_system_information)

        # Help / View Documentation menu
        self.Menu_Help_ViewDocumentation = QtWidgets.QAction(main_window)
        self.Menu_Help_ViewDocumentation.setObjectName(qt_util.from_utf8("Menu_Help_ViewDocumentation"))
        self.Menu_Help_ViewDocumentation.setText("View Documentation")
        icon_path = app_util.get_property("ProgramResourcesPath").replace('\\', '/')
        icon_path = icon_path + "/images/baseline_school_black_18dp.png"
        self.Menu_Help_ViewDocumentation.setIcon(QtGui.QIcon(QtGui.QPixmap(icon_path)))
        self.Menu_Help.addAction(self.Menu_Help_ViewDocumentation)

        # Connect the Help > View Documentation menu tab.
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Help_ViewDocumentation.triggered.connect(self.ui_action_view_documentation)
        # Add Help menu to menubar
        self.menubar.addAction(self.Menu_Help.menuAction())

    def setup_ui_results(self, y_centralwidget: int):
        """
        Set up the Results area of the UI.

        Args:
            y_centralwidget (int):  Row position in the central widget to add this component.

        Returns:
            None
        """
        # Results area is in the bottom of the central widget
        # - Use Tab widget with vertical layout
        # - Alphabetize the tabs
        self.results_GroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.results_GroupBox.setTitle("Results")
        self.results_GroupBox.setObjectName(qt_util.from_utf8("results_GroupBox"))
        self.results_VerticalLayout = QtWidgets.QVBoxLayout(self.results_GroupBox)
        self.results_VerticalLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.results_VerticalLayout.setObjectName(qt_util.from_utf8("verticalLayout"))
        self.results_TabWidget = QtWidgets.QTabWidget(self.results_GroupBox)
        self.results_TabWidget.setObjectName(qt_util.from_utf8("results_TabWidget"))

        # Results GeoLayers tab
        # - Contains a table of GeoLayer
        self.results_GeoLayers_Tab = QtWidgets.QWidget()
        self.results_GeoLayers_Tab.setAcceptDrops(False)
        self.results_GeoLayers_Tab.setObjectName(qt_util.from_utf8("results_GeoLayers_Tab"))
        self.results_GeoLayers_VerticalLayout = QtWidgets.QVBoxLayout(self.results_GeoLayers_Tab)
        self.results_GeoLayers_VerticalLayout.setObjectName(qt_util.from_utf8("results_GeoLayers_VerticalLayout"))
        self.results_GeoLayers_GroupBox = QtWidgets.QGroupBox(self.results_GeoLayers_Tab)
        self.results_GeoLayers_GroupBox.setObjectName(qt_util.from_utf8("results_GeoLayers_GroupBox"))
        self.results_GeoLayers_GroupBox_VerticalLayout = QtWidgets.QVBoxLayout(self.results_GeoLayers_GroupBox)
        self.results_GeoLayers_GroupBox_VerticalLayout.setObjectName(
            qt_util.from_utf8("results_GeoLayers_GroupBox_VerticalLayout"))
        self.results_GeoLayers_Table = QtWidgets.QTableWidget(self.results_GeoLayers_GroupBox)
        self.results_GeoLayers_Table.setObjectName(qt_util.from_utf8("results_GeoLayers_Table"))
        self.results_GeoLayers_Table.setColumnCount(5)
        self.results_GeoLayers_Table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.results_GeoLayers_Table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.results_GeoLayers_Table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.results_GeoLayers_Table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.results_GeoLayers_Table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.results_GeoLayers_Table.setHorizontalHeaderItem(4, item)
        self.results_GeoLayers_Table.horizontalHeader().setCascadingSectionResizes(False)
        self.results_GeoLayers_Table.horizontalHeader().setDefaultSectionSize(200)
        self.results_GeoLayers_Table.setSortingEnabled(True)
        self.results_GeoLayers_Table.horizontalHeader().setSortIndicatorShown(True)
        self.results_GeoLayers_Table.horizontalHeader().setStretchLastSection(True)
        self.results_GeoLayers_GroupBox_VerticalLayout.addWidget(self.results_GeoLayers_Table)
        self.results_GeoLayers_VerticalLayout.addWidget(self.results_GeoLayers_GroupBox)
        self.results_TabWidget.addTab(self.results_GeoLayers_Tab, qt_util.from_utf8(""))
        # Used to be in retranslateUi
        self.results_GeoLayers_GroupBox.setTitle("GeoLayers (0 GeoLayers, 0 selected)")
        self.results_GeoLayers_Table.horizontalHeaderItem(0).setText("GeoLayer ID")
        self.results_GeoLayers_Table.horizontalHeaderItem(0).setToolTip("GeoLayer ID")
        self.results_GeoLayers_Table.horizontalHeaderItem(1).setText("Geometry")
        self.results_GeoLayers_Table.horizontalHeaderItem(1).setToolTip("Geometry")
        self.results_GeoLayers_Table.horizontalHeaderItem(2).setText("Feature Count")
        self.results_GeoLayers_Table.horizontalHeaderItem(2).setToolTip("Feature Count")
        self.results_GeoLayers_Table.horizontalHeaderItem(3).setText("Coordinate Reference System")
        self.results_GeoLayers_Table.horizontalHeaderItem(3).setToolTip("Coordinate Reference System")
        self.results_GeoLayers_Table.horizontalHeaderItem(4).setText("Command Reference")
        self.results_GeoLayers_Table.horizontalHeaderItem(4).setToolTip("Command Reference")
        self.results_GeoLayers_Table.horizontalHeader().setStyleSheet("::section { background-color: #d3d3d3 }")
        self.results_GeoLayers_Table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.results_GeoLayers_Table.customContextMenuRequested.connect(self.ui_action_geolayers_right_click)
        self.results_TabWidget.setTabText(self.results_TabWidget.indexOf(self.results_GeoLayers_Tab), "GeoLayers")

        # Results - Maps tab
        self.results_Maps_Tab = QtWidgets.QWidget()
        self.results_Maps_Tab.setObjectName(qt_util.from_utf8("results_Maps_Tab"))
        self.results_Maps_VerticalLayout = QtWidgets.QVBoxLayout(self.results_Maps_Tab)
        self.results_Maps_VerticalLayout.setObjectName(qt_util.from_utf8("results_Maps_VerticalLayout"))
        self.results_Maps_GroupBox = QtWidgets.QGroupBox(self.results_Maps_Tab)
        self.results_Maps_GroupBox.setObjectName(qt_util.from_utf8("results_Maps_GroupBox"))
        self.results_Maps_GroupBox_VerticalLayout = QtWidgets.QVBoxLayout(self.results_Maps_GroupBox)
        self.results_Maps_GroupBox_VerticalLayout.setObjectName(
            qt_util.from_utf8("results_Maps_GroupBox_VerticalLayout"))
        self.results_Maps_Table = QtWidgets.QTableWidget(self.results_Maps_GroupBox)
        self.results_Maps_Table.setObjectName(qt_util.from_utf8("results_Maps_Table"))
        self.results_Maps_Table.setColumnCount(4)
        self.results_Maps_Table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.results_Maps_Table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.results_Maps_Table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.results_Maps_Table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.results_Maps_Table.setHorizontalHeaderItem(3, item)
        self.results_Maps_Table.horizontalHeader().setDefaultSectionSize(175)
        self.results_Maps_Table.horizontalHeader().setStretchLastSection(True)
        self.results_Maps_GroupBox_VerticalLayout.addWidget(self.results_Maps_Table)
        self.results_Maps_VerticalLayout.addWidget(self.results_Maps_GroupBox)
        self.results_TabWidget.addTab(self.results_Maps_Tab, qt_util.from_utf8(""))
        # Used to be in retranslateUi
        self.results_Maps_GroupBox.setTitle("Maps (0 Maps, 0 selected)")
        self.results_Maps_Table.horizontalHeaderItem(0).setText("Map ID")
        self.results_Maps_Table.horizontalHeaderItem(0).setToolTip("Map ID")
        self.results_Maps_Table.horizontalHeaderItem(1).setText("Included GeoLayers")
        self.results_Maps_Table.horizontalHeaderItem(1).setToolTip("Included GeoLayers")
        self.results_Maps_Table.horizontalHeaderItem(2).setText("Coordinate Reference System")
        self.results_Maps_Table.horizontalHeaderItem(2).setToolTip("Coordinate Reference System")
        self.results_Maps_Table.horizontalHeaderItem(3).setText("Command Reference")
        self.results_Maps_Table.horizontalHeaderItem(3).setToolTip("Command Reference")
        self.results_Maps_Table.horizontalHeader().setStyleSheet("::section { background-color: #d3d3d3 }")
        self.results_TabWidget.setTabText(self.results_TabWidget.indexOf(self.results_Maps_Tab), "Maps")

        # Results - Output Files tab
        self.results_OutputFiles_Tab = QtWidgets.QWidget()
        self.results_OutputFiles_Tab.setObjectName(qt_util.from_utf8("results_OutputFiles_Tab"))
        self.results_OutputFiles_VerticalLayout = QtWidgets.QVBoxLayout(self.results_OutputFiles_Tab)
        self.results_OutputFiles_VerticalLayout.setObjectName(qt_util.from_utf8("results_OutputFiles_VerticalLayout"))
        self.results_OutputFiles_GroupBox = QtWidgets.QGroupBox(self.results_OutputFiles_Tab)
        self.results_OutputFiles_GroupBox.setObjectName(qt_util.from_utf8("results_OutputFiles_GroupBox"))
        self.results_OutputFiles_GroupBox_VerticalLayout = QtWidgets.QVBoxLayout(self.results_OutputFiles_GroupBox)
        self.results_OutputFiles_GroupBox_VerticalLayout.setObjectName(
            qt_util.from_utf8("results_OutputFiles_GroupBox_VerticalLayout"))
        self.results_OutputFiles_Table = QtWidgets.QTableWidget(self.results_OutputFiles_GroupBox)
        self.results_OutputFiles_Table.setObjectName(qt_util.from_utf8("results_OutputFiles_Table"))
        single_column = True  # Like TSTool, only the filename
        if single_column:
            self.results_OutputFiles_Table.setColumnCount(2)
        else:
            self.results_OutputFiles_Table.setColumnCount(3)
        self.results_OutputFiles_Table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        if not single_column:
            item = QtWidgets.QTableWidgetItem()
            self.results_OutputFiles_Table.setHorizontalHeaderItem(1, item)
            item = QtWidgets.QTableWidgetItem()
            self.results_OutputFiles_Table.setHorizontalHeaderItem(2, item)
        self.results_OutputFiles_Table.horizontalHeader().setStretchLastSection(False)
        self.results_OutputFiles_Table.horizontalHeader().hide()
        self.results_OutputFiles_GroupBox_VerticalLayout.addWidget(self.results_OutputFiles_Table)
        self.results_OutputFiles_VerticalLayout.addWidget(self.results_OutputFiles_GroupBox)
        self.results_TabWidget.addTab(self.results_OutputFiles_Tab, qt_util.from_utf8(""))
        # Used to be in retranslateUi
        self.results_OutputFiles_GroupBox.setTitle("Output Files (0 Output Files, 0 selected)")
        if not single_column:
            self.results_OutputFiles_Table.horizontalHeaderItem(1).setText("File Type")
            self.results_OutputFiles_Table.horizontalHeaderItem(2).setText("Command Reference")
        self.results_TabWidget.setTabText(self.results_TabWidget.indexOf(self.results_OutputFiles_Tab), "Output Files")

        # Results - Properties tab
        self.results_Properties_Tab = QtWidgets.QWidget()
        self.results_Properties_Tab.setObjectName(qt_util.from_utf8("results_Properties_Tab"))
        self.results_Properties_Tab_VerticalLayout = QtWidgets.QVBoxLayout(self.results_Properties_Tab)
        self.results_Properties_Tab_VerticalLayout.setObjectName(
            qt_util.from_utf8("results_Properties_Tab_VerticalLayout"))
        self.results_Properties_GroupBox = QtWidgets.QGroupBox(self.results_Properties_Tab)
        self.results_Properties_GroupBox.setObjectName(qt_util.from_utf8("results_Properties_GroupBox"))
        self.results_Properties_GroupBox_VerticalLayout = QtWidgets.QVBoxLayout(self.results_Properties_GroupBox)
        self.results_Properties_GroupBox_VerticalLayout.setObjectName(
            qt_util.from_utf8("results_Properties_GroupBox_VerticalLayout"))
        # Assign a resize event to resize map canvas when dialog window is resized
        self.results_Properties_Table = QtWidgets.QTableWidget(self.results_Properties_GroupBox)
        self.results_Properties_Table.setAlternatingRowColors(True)
        self.results_Properties_Table.setObjectName(qt_util.from_utf8("results_Properties_Table"))
        self.results_Properties_Table.setColumnCount(3)
        self.results_Properties_Table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.results_Properties_Table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.results_Properties_Table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.results_Properties_Table.setHorizontalHeaderItem(2, item)
        self.results_Properties_Table.horizontalHeader().setStretchLastSection(False)
        self.results_Properties_Table.verticalHeader().setStretchLastSection(False)
        self.results_Properties_GroupBox_VerticalLayout.addWidget(self.results_Properties_Table)
        self.results_Properties_Tab_VerticalLayout.addWidget(self.results_Properties_GroupBox)
        self.results_TabWidget.addTab(self.results_Properties_Tab, qt_util.from_utf8(""))
        # Used to be in retranslateUi
        self.results_Properties_GroupBox.setTitle(
            "Processor properties control processing and can be used in some command " +
            "parameters using ${Property} notation (see command documentation). ")
        self.results_Properties_Table.horizontalHeaderItem(0).setText("Property Name")
        self.results_Properties_Table.horizontalHeaderItem(0).setToolTip("Property Name")
        self.results_Properties_Table.horizontalHeaderItem(1).setText("Property Value")
        self.results_Properties_Table.horizontalHeaderItem(1).setToolTip("Property Value")
        self.results_Properties_Table.horizontalHeader().setStyleSheet("::section { background-color: #d3d3d3 }")
        # Hide last column to ensure horizontal scroll
        self.results_Properties_Table.setColumnWidth(2, 0)
        self.results_TabWidget.setTabText(self.results_TabWidget.indexOf(self.results_Properties_Tab), "Properties")

        # Results - Tables tab
        self.results_Tables_Tab = QtWidgets.QWidget()
        self.results_Tables_Tab.setObjectName(qt_util.from_utf8("results_Tables_Tab"))
        self.results_Tables_VerticalLayout = QtWidgets.QVBoxLayout(self.results_Tables_Tab)
        self.results_Tables_VerticalLayout.setObjectName(qt_util.from_utf8("results_Tables_VerticalLayout"))
        self.results_Tables_GroupBox = QtWidgets.QGroupBox(self.results_Tables_Tab)
        self.results_Tables_GroupBox.setObjectName(qt_util.from_utf8("results_Tables_GroupBox"))
        self.results_Tables_GroupBox_VerticalLayout = QtWidgets.QVBoxLayout(self.results_Tables_GroupBox)
        self.results_Tables_GroupBox_VerticalLayout.setObjectName(
            qt_util.from_utf8("results_Tables_GroupBox_VerticalLayout"))
        self.results_Tables_Table = QtWidgets.QTableWidget(self.results_Tables_GroupBox)
        self.results_Tables_Table.setObjectName(qt_util.from_utf8("results_Tables_Table"))
        self.results_Tables_Table.setColumnCount(4)
        self.results_Tables_Table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.results_Tables_Table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.results_Tables_Table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.results_Tables_Table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.results_Tables_Table.setHorizontalHeaderItem(3, item)
        self.results_Tables_Table.setSortingEnabled(True)
        self.results_Tables_Table.horizontalHeader().setSortIndicatorShown(True)
        self.results_Tables_Table.horizontalHeader().setStretchLastSection(True)
        self.results_Tables_GroupBox_VerticalLayout.addWidget(self.results_Tables_Table)
        self.results_Tables_VerticalLayout.addWidget(self.results_Tables_GroupBox)
        self.results_TabWidget.addTab(self.results_Tables_Tab, qt_util.from_utf8(""))
        # Used to be in retranslateUi
        self.results_Tables_GroupBox.setTitle("Tables (0 Tables, 0 selected)")
        self.results_Tables_Table.horizontalHeaderItem(0).setText("Table ID")
        self.results_Tables_Table.horizontalHeaderItem(0).setToolTip("Table ID")
        self.results_Tables_Table.horizontalHeaderItem(1).setText("Column Count")
        self.results_Tables_Table.horizontalHeaderItem(1).setToolTip("Column Count")
        self.results_Tables_Table.horizontalHeaderItem(2).setText("Row Count")
        self.results_Tables_Table.horizontalHeaderItem(2).setToolTip("Row Count")
        self.results_Tables_Table.horizontalHeaderItem(3).setText("Command Reference")
        self.results_Tables_Table.horizontalHeaderItem(3).setToolTip("Command Reference")
        self.results_Tables_Table.horizontalHeader().setStyleSheet("::section { background-color: #d3d3d3 }")
        self.results_TabWidget.setTabText(self.results_TabWidget.indexOf(self.results_Tables_Tab), "Tables")

        # Add the Results tab to the vertical layout
        self.results_VerticalLayout.addWidget(self.results_TabWidget)
        # Now add the Results to the central widget
        self.centralwidget_GridLayout.addWidget(self.results_GroupBox, y_centralwidget, 0, 1, 6)
        # Set the visible tab to the GeoLayers
        self.results_TabWidget.setCurrentIndex(0)

        # Set up event handlers

        # Listen for a change in item selection within the results_GeoLayers_Table widget.
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.results_GeoLayers_Table.itemSelectionChanged.connect(self.update_ui_status)
        # Listen for a change in item selection within the results_Tables_Table widget.
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.results_Tables_Table.itemSelectionChanged.connect(self.update_ui_status)
        # Listen for a change in item selection within the results_Maps_Table widget.
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.results_Maps_Table.itemSelectionChanged.connect(self.update_ui_status)
        # Listen for a change in item selection within the results_OutputFiles_Table widget.
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.results_OutputFiles_Table.itemSelectionChanged.connect(self.update_ui_status)

    # TODO smalers 2018-07-24 evaluate whether the following status components can be moved to status bar area
    def setup_ui_status(self, main_window: GeoProcessorUI, y_centralwidget: int) -> None:
        """
        Set up the Status area of the UI.

        Args:
            main_window: instance of main window
            y_centralwidget (int):  Row position in the central widget to add this component.

        Returns:
            None
        """
        # Set the status bar
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName(qt_util.from_utf8("statusbar"))
        self.statusbar.setStyleSheet("::item { border: none; }")

        self.status_GridLayout = QtWidgets.QGridLayout()

        self.status_CommandWorkflow_StatusBar = QtWidgets.QProgressBar()
        self.status_CommandWorkflow_StatusBar.setObjectName(qt_util.from_utf8("status_CommandWorkflow_StatusBar"))
        self.status_CommandWorkflow_StatusBar.setToolTip("Indicates progress processing the workflow")
        self.status_CommandWorkflow_StatusBar.setProperty("value", 0)
        self.status_CommandWorkflow_StatusBar.setInvertedAppearance(False)

        self.statusbar.addPermanentWidget(self.status_CommandWorkflow_StatusBar)

        self.status_CurrentCommand_StatusBar = QtWidgets.QProgressBar()
        self.status_CurrentCommand_StatusBar.setObjectName(qt_util.from_utf8("status_CurrentCommand_StatusBar"))
        self.status_CurrentCommand_StatusBar.setToolTip("Indicates progress within current command")
        self.status_CurrentCommand_StatusBar.setProperty("value", 0)
        self.status_CurrentCommand_StatusBar.setInvertedAppearance(False)

        self.statusbar.addPermanentWidget(self.status_CurrentCommand_StatusBar)

        self.status_Label = QtWidgets.QLabel()
        self.status_Label.setObjectName(qt_util.from_utf8("status_Label"))
        self.status_Label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.status_Label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.status_Label.setLineWidth(2)
        self.status_Label.setText("Ready")

        self.statusbar.addPermanentWidget(self.status_Label)

        self.status_Label_Hint = QtWidgets.QLabel()
        self.status_Label_Hint.setObjectName(qt_util.from_utf8("status_Label_hint"))
        self.status_Label_Hint.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.status_Label_Hint.setFrameShadow(QtWidgets.QFrame.Plain)
        self.status_Label_Hint.setLineWidth(2)
        self.status_Label_Hint.setText("Use the Run buttons to run the commands.")

        self.statusbar.addWidget(self.status_Label_Hint)

        main_window.setStatusBar(self.statusbar)

    def setup_ui_toolbar(self, main_window: GeoProcessorUI) -> None:
        """
        Setup UI Toolbar

        Args:
            main_window: main window instance

        Returns:
            None
        """

        icon_path = app_util.get_property("ProgramResourcesPath").replace('\\', '/')
        icon_path = icon_path + "/images/baseline_format_indent_increase_black_18dp.png"
        self.increase_indent_button = QtWidgets.QAction(QtGui.QIcon(QtGui.QPixmap(icon_path)), "Increase indent", self)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.increase_indent_button.triggered.connect(
            self.command_CommandListWidget.event_handler_indent_button_clicked)

        icon_path = app_util.get_property("ProgramResourcesPath").replace('\\', '/')
        icon_path = icon_path + "/images/baseline_format_indent_decrease_black_18dp.png"
        self.decrease_indent_button = QtWidgets.QAction(QtGui.QIcon(QtGui.QPixmap(icon_path)), "Decrease indent", self)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.decrease_indent_button.triggered.connect(
            self.command_CommandListWidget.event_handler_decrease_indent_button_clicked)

        self.toolbar = self.addToolBar("Toolbar Actions")
        self.toolbar.addAction(self.decrease_indent_button)
        self.toolbar.addAction(self.increase_indent_button)

        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("background: white;")
        self.toolbar.setStyleSheet("QToolButton {padding-left: 0px}")
        self.toolbar.setMaximumHeight(27)

    def show_command_status(self) -> None:
        """
        Opens a dialog box that shows the command status for the first selected command,
        or if none selected the first command.

        Returns:
            None
        """

        # Get the command that was selected

        # Create command status dialog box
        # TODO smalers 2020-01-19 this can probably be local to this method rather than instance data
        self.command_status_dialog = QtWidgets.QDialog()
        self.command_status_dialog.resize(600, 290)
        self.command_status_dialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        # Add window title
        self.command_status_dialog.setWindowTitle("GeoProcessor - Command Status")
        # Add icon to window
        icon_path = app_util.get_property("ProgramIconPath").replace('\\', '/')
        self.command_status_dialog.setWindowIcon(QtGui.QIcon(icon_path))
        self.command_status_dialog.setObjectName("Command Status Dialog")

        # Create a grid layout for dialog box
        grid_layout = QtWidgets.QGridLayout(self.command_status_dialog)
        grid_layout.setObjectName("Command Status Grid Layout")

        # Add a text browser for the content
        command_status_text_browser = QtWidgets.QTextBrowser(self.command_status_dialog)
        command_status_text_browser.setObjectName("Command Status Text Browser")

        grid_layout.addWidget(command_status_text_browser, 0, 0, 1, 1)

        html_string = ""

        logger = logging.getLogger(__name__)
        gp = self.gp
        if len(gp.commands) == 0:
            # If length of commands is 0, nothing to show.
            return
        # logger.info("In show_command_status, have " + str(len(gp.commands)) + " commands in processor.")
        selected_command = None
        # Get the index of the command list selected and retrieve that command from the geoprocessor
        selected_indices = self.command_CommandListWidget.command_ListView.selectedIndexes()
        if (selected_indices is None) or (len(selected_indices) == 0):
            # Nothing is selected, so use the first command
            selected_command = gp.commands[0]
        else:
            # Something is selected so use the first selected command
            # - the indices are instances of QModelIndex
            row_index = selected_indices[0].row()
            selected_command = gp.commands[row_index]
        if selected_command is None:
            # Should not happen
            html_string = 'No command found to show status.'
        else:
            # Format the information similar to TSTool status
            # - TSTool uses an HTML-formatted status, but for now show as simple text
            # - HTML formatting or other free-form format is preferred because content will fill table cells
            # noinspection PyBroadException
            try:
                command_status = selected_command.command_status

                html_string = (
                    "<style> td.failure{background-color:red} </style>" +
                    "<p><b>Command:<br>" + selected_command.command_string + "</b></p>"
                                                                             
                    "<p><b>Command Status Summary</b> (see below for details if problems exist):</p>" +
                    "<table border='1'>" +
                    "<tr style='background-color:#d0d0ff; font-weight:bold;'>" +
                    "<th> Phase </th>" +
                    "<th> Status/Max Severity </th>" +
                    "</tr>"
                )

                style = ""

                if command_status.initialization_status is CommandStatusType.WARNING:
                    style = "style='background-color:yellow'"
                elif command_status.initialization_status is CommandStatusType.FAILURE:
                    style = "style='background-color:#ffa8a8'"
                elif command_status.initialization_status is CommandStatusType.SUCCESS:
                    style = "style='background-color:#7dba71'"

                html_string += (
                    "<tr>" +
                    "<td> INITIALIZATION </td>" +
                    "<td " + style + ">" + str(command_status.initialization_status) + "</td>" +
                    "</tr>"
                )

                style = ""

                if command_status.discovery_status is CommandStatusType.WARNING:
                    style = "style='background-color:yellow'"
                elif command_status.discovery_status is CommandStatusType.FAILURE:
                    style = "style='background-color:#ffa8a8'"
                elif command_status.discovery_status is CommandStatusType.SUCCESS:
                    style = "style='background-color:green'"

                html_string += (
                    "<tr>" +
                    "<td> DISCOVERY </td>" +
                    "<td " + style + ">" + str(command_status.discovery_status) + "</td>" +
                    "</tr>"
                )

                style = ""

                if command_status.run_status is CommandStatusType.WARNING:
                    style = "style='background-color:yellow'"
                elif command_status.run_status is CommandStatusType.FAILURE:
                    style = "style='background-color:#ffa8a8'"
                else:
                    style = "style='background-color:#7dba71'"

                html_string += (
                    "<tr>" +
                    "<td> RUN </td>" +
                    "<td " + style + ">" + str(command_status.run_status) + "</td>" +
                    "</tr>" +
                    "</table>" +

                    "<p><b>Command Status Details (" +
                    str(command_status.get_log_count(phase=None, severity=CommandStatusType.WARNING)) +
                    " warnings, " +
                    str(command_status.get_log_count(phase=None, severity=CommandStatusType.FAILURE)) +
                    " failures):</p>" +
                    "<table border='1'>" +
                    "<tr style='background-color:#d0d0ff; font-weight:bold;'>" +
                    "<th> # </th>" +
                    "<th> Phase </th>" +
                    "<th> Severity </th>" +
                    "<th> Problem </th>" +
                    "<th> Recommendation </th>" +
                    "</tr>"
                )

                log_count = 0
                for log_record in command_status.initialization_log_list:
                    if log_record.severity is CommandStatusType.WARNING or \
                            log_record.severity is CommandStatusType.FAILURE:
                        
                        style = ""

                        if log_record.severity is CommandStatusType.WARNING:
                            style = "style='background-color:yellow'"
                        elif log_record.severity is CommandStatusType.FAILURE:
                            style = "style='background-color:#ffa8a8'"

                        log_count = log_count + 1
                        html_string += (
                            "<tr>" +
                            "<td>" + str(log_count) + "</td>" +
                            "<td>" + str(CommandPhaseType.INITIALIZATION) + "</td>" +
                            "<td " + style + ">" + str(log_record.severity) + "</td>" +
                            "<td>" + log_record.problem + "</td>" +
                            "<td>" + log_record.recommendation + "</td>" +
                            "</tr>"
                        )
                for log_record in command_status.discovery_log_list:
                    if log_record.severity is CommandStatusType.WARNING or \
                            log_record.severity is CommandStatusType.FAILURE:

                        style = ""

                        if log_record.severity is CommandStatusType.WARNING:
                            style = "style='background-color:yellow'"
                        elif log_record.severity is CommandStatusType.FAILURE:
                            style = "style='background-color:#ffa8a8'"

                        log_count = log_count + 1
                        html_string += (
                            "<tr>" +
                            "<td>" + str(log_count) + "</td>" +
                            "<td>" + str(CommandPhaseType.DISCOVERY) + "</td>" +
                            "<td " + style + ">" + str(log_record.severity) + "</td>" +
                            "<td>" + log_record.problem + "</td>" +
                            "<td>" + log_record.recommendation + "</td>" +
                            "</tr>"
                        )
                print("Have " + str(len(command_status.run_log_list)) + " log records")
                for log_record in command_status.run_log_list:
                    if log_record.severity is CommandStatusType.WARNING or \
                            log_record.severity is CommandStatusType.FAILURE:

                        style = ""

                        if log_record.severity is CommandStatusType.WARNING:
                            style = "style='background-color:yellow'"
                        elif log_record.severity is CommandStatusType.FAILURE:
                            style = "style='background-color:#ffa8a8'"

                        log_count = log_count + 1
                        html_string += (
                            "<tr>" +
                            "<td>" + str(log_count) + "</td>" +
                            "<td>" + str(CommandPhaseType.RUN) + "</td>" +
                            "<td " + style + ">" + str(log_record.severity) + "</td>" +
                            "<td>" + log_record.problem + "</td>" +
                            "<td>" + log_record.recommendation + "</td>" +
                            "</tr>"
                        )
                html_string += (
                                "</table>"
                                )

            except Exception:
                logger.warning("Error formatting status", exc_info=True)

        command_status_text_browser.setHtml(qt_util.translate("Dialog", html_string, None))

        # self.setWindowModality(QtCore.Qt.NonModal)
        # command_status_dialog.setModal(False)
        # print("modality: ")
        # print(command_status_dialog.isModal())
        # print(self.isModal())
        self.command_status_dialog.setModal(False)
        self.command_status_dialog.show()

    def show_command_status_tooltip(self, event) -> None:
        """
        When hovering or clicking on a numbered list item if there is an error or warning
        display a tooltip with the command status. Called in CommandListWidget
        when numbered list item is hovered over or clicked by the user.

        Args:
            event: Hover event over numbered list item.

        Returns:
            None
        """

        gp = self.gp
        logger = logging.getLogger(__name__)

        item = self.command_CommandListWidget.number_ListWidget.itemAt(event.pos())
        row_index = self.command_CommandListWidget.number_ListWidget.row(item)
        # if (row_index >= self.command_CommandListWidget.command_ListWidget.count()) or row_index == -1:
        if (row_index >= len(self.command_CommandListWidget.gp_model.gp.commands)) or row_index == -1:
                return
        selected_command = gp.commands[row_index]

        command_status = selected_command.command_status
        run_status = command_status.run_status
        if run_status is CommandStatusType.WARNING or run_status is CommandStatusType.FAILURE:
            # noinspection PyBroadException
            try:
                html_string = (
                    "<p><b>Command Status Details (" +
                    str(command_status.get_log_count(phase=None, severity=CommandStatusType.WARNING)) +
                    " warnings, " +
                    str(command_status.get_log_count(phase=None, severity=CommandStatusType.FAILURE)) +
                    " failures):</p>" +
                    "<table border='1'>" +
                    "<tr style='background-color:#d0d0ff; font-weight:bold;'>" +
                    "<th> # </th>" +
                    "<th> Phase </th>" +
                    "<th> Severity </th>" +
                    "<th> Problem </th>" +
                    "<th> Recommendation </th>" +
                    "</tr>"
                )

                log_count = 0
                for log_record in command_status.initialization_log_list:
                    if log_record.severity is CommandStatusType.WARNING or \
                            log_record.severity is CommandStatusType.FAILURE:
                        style = ""

                        if log_record.severity is CommandStatusType.WARNING:
                            style = "style='background-color:yellow'"
                        elif log_record.severity is CommandStatusType.FAILURE:
                            style = "style='background-color:#ffa8a8'"
                        log_count = log_count + 1
                        html_string += (
                            "<tr>" +
                            "<td style='white-space:pre'>" + str(log_count) + "</td>" +
                            "<td style='white-space:pre'>" + str(CommandPhaseType.INITIALIZATION) + "</td>" +
                            "<td " + style + ">" + str(log_record.severity) + "</td>" +
                            "<td style='white-space:pre'>" + log_record.problem + "</td>" +
                            "<td style='white-space:pre'>" + log_record.recommendation + "</td>" +
                            "</tr>"
                        )
                for log_record in command_status.discovery_log_list:
                    if log_record.severity is CommandStatusType.WARNING or \
                            log_record.severity is CommandStatusType.FAILURE:

                        style = ""

                        if log_record.severity is CommandStatusType.WARNING:
                            style = "style='background-color:yellow'"
                        elif log_record.severity is CommandStatusType.FAILURE:
                            style = "style='background-color:#ffa8a8'"

                        log_count = log_count + 1
                        html_string += (
                            "<tr>" +
                            "<td style='white-space:pre'>" + str(log_count) + "</td>" +
                            "<td style='white-space:pre'>" + str(CommandPhaseType.DISCOVERY) + "</td>" +
                            "<td " + style + ">" + str(log_record.severity) + "</td>" +
                            "<td style='white-space:pre'>" + log_record.problem + "</td>" +
                            "<td style='white-space:pre'>" + log_record.recommendation + "</td>" +
                            "</tr>"
                        )
                # print("Have " + str(len(command_status.run_log_list)) + " log records")
                for log_record in command_status.run_log_list:
                    if log_record.severity is CommandStatusType.WARNING or \
                            log_record.severity is CommandStatusType.FAILURE:

                        style = ""

                        if log_record.severity is CommandStatusType.WARNING:
                            style = "style='background-color:yellow'"
                        elif log_record.severity is CommandStatusType.FAILURE:
                            style = "style='background-color:#ffa8a8'"

                        log_count = log_count + 1
                        html_string += (
                            "<tr>" +
                            "<td style='white-space:pre'>" + str(log_count) + "</td>" +
                            "<td style='white-space:pre'>" + str(CommandPhaseType.RUN) + "</td>" +
                            "<td " + style + ">" + str(log_record.severity) + "</td>" +
                            "<td style='white-space:pre'>" + log_record.problem + "</td>" +
                            "<td>" + log_record.recommendation + "</td>" +
                            "</tr>"
                        )
                html_string += (
                    "</table>"
                )

                item.setToolTip(qt_util.translate("Tooltip", html_string, None))
            except Exception:
                logger.warning("Error formatting status", exc_info=True)

    def show_results(self) -> None:
        """
        Populates the Results tables of the UI to reflect results of running the GeoProcessor, including
        the existing GeoLayers, Maps, Output Files, Properties, and Tables.

        Returns:
            None
        """

        # Call the specific functions for each output category
        # - Each call will also update the status information in the UI (counts, selected, etc.)
        logger = logging.getLogger(__name__)
        # noinspection PyBroadException
        try:
            self.show_results_geolayers()
        except Exception:
            message = "Error showing GeoLayers in Results"
            logger.warning(message, exc_info=True)
        # noinspection PyBroadException
        try:
            self.show_results_maps()
        except Exception:
            message = "Error showing Maps in Results"
            logger.warning(message, exc_info=True)
        # noinspection PyBroadException
        try:
            self.show_results_output_files()
        except Exception:
            message = "Error showing Output Files in Results"
            logger.warning(message, exc_info=True)
        # noinspection PyBroadException
        try:
            self.show_results_properties()
        except Exception:
            message = "Error showing Properties in Results"
            logger.warning(message, exc_info=True)
        # noinspection PyBroadException
        try:
            self.show_results_tables()
        except Exception:
            message = "Error showing Tables in Results"
            logger.warning(message, exc_info=True)

    def show_results_geolayers(self) -> None:
        """
        Populates the Results / GeoLayers display.

        Returns:
            None
        """
        # Remove items from the Results GeoLayers table (from a previous run).
        self.results_GeoLayers_Table.setRowCount(0)

        for geolayer in self.gp.geolayers:

            # Get the index of the next available row in the table. Add a new row to the table.
            new_row_index = self.results_GeoLayers_Table.rowCount()
            self.results_GeoLayers_Table.insertRow(new_row_index)

            # Retrieve the GeoLayer's GeoLayer ID and set as the attribute for the GeoLayer ID column.
            self.results_GeoLayers_Table.setItem(new_row_index, 0, QtWidgets.QTableWidgetItem(geolayer.id))

            # Retrieve the GeoLayer's geometry and set as the attribute for the Geometry column.
            logger = logging.getLogger(__name__)
            self.results_GeoLayers_Table.setItem(new_row_index, 1,
                                                 QtWidgets.QTableWidgetItem(geolayer.get_geometry()))

            # Retrieve the number of features within the GeoLayer and set as the attribute for the Feature Count column.
            if geolayer.is_vector():
                # Display the feature count
                self.results_GeoLayers_Table.setItem(new_row_index, 2,
                                                     QtWidgets.QTableWidgetItem(str(geolayer.get_feature_count())))
            elif geolayer.is_raster():
                # Display the row, column, and cell count in a formatted string
                self.results_GeoLayers_Table.setItem(new_row_index, 2,
                                                     QtWidgets.QTableWidgetItem(str(geolayer.get_num_rows()) + " x " +
                                                                                str(geolayer.get_num_columns()) +
                                                                                " = " +
                                                                                str(geolayer.get_num_rows() *
                                                                                    geolayer.get_num_columns()) +
                                                                                " cells"))

            # Retrieve the GeoLayer's CRS and set as the attribute for the Coordinate Reference System column.
            self.results_GeoLayers_Table.setItem(new_row_index, 3,
                                                 QtWidgets.QTableWidgetItem(geolayer.get_crs()))

        self.update_ui_status_results_geolayers()

    def show_results_maps(self) -> None:
        """
        Populates the Results / Maps display.

        Returns:
            None
        """
        # Remove items from the Results Maps table (from a previous run).
        self.results_Maps_Table.setRowCount(0)
        # TODO egiles 2018-05-14 Populate the Results / Maps display

        # Remove items from the Results Output Files table (from a previous run).
        self.results_OutputFiles_Table.setRowCount(0)

        self.update_ui_status_results_maps()

    def show_results_output_files(self) -> None:
        """
        Populates the Results / Output Files display.

        Returns:
            None
        """
        # Remove items from the Results Properties table (from a previous run).
        self.results_OutputFiles_Table.setRowCount(0)

        # Populate the Results / Output Files Table
        # Iterate through all of the Output Files in the GeoProcessor.
        single_column = True  # Like TSTool, only the filename
        for output_file in self.gp.output_files:

            # Get the index of the next available row in the table. Add a new row to the table.
            new_row_index = self.results_OutputFiles_Table.rowCount()
            self.results_OutputFiles_Table.insertRow(new_row_index)

            # Retrieve the absolute pathname of the output file and set as the attribute for the Output File column.
            self.results_OutputFiles_Table.setItem(new_row_index, 0, QtWidgets.QTableWidgetItem(output_file))

            if not single_column:
                # Get the extension of the output file.
                output_file_ext = io_util.get_extension(output_file)

                # A dictionary that relates common file extensions to the appropriate file name
                extension_dictionary = {'.xlsx': 'Microsoft Excel Open XML Format Spreadsheet',
                                        '.geojson': 'GeoJSON',
                                        '.xls': 'Microsoft Excel 97-2003 Worksheet'}

                # Retrieve the output file type and set as the attribute for the File Type column. If h
                if output_file_ext in extension_dictionary.keys():
                    self.results_OutputFiles_Table.setItem(
                        new_row_index, 1, QtWidgets.QTableWidgetItem(extension_dictionary[output_file_ext]))
                else:
                    self.results_OutputFiles_Table.setItem(new_row_index, 1, QtWidgets.QTableWidgetItem("Unknown"))
        self.results_OutputFiles_Table.resizeColumnsToContents()
        self.update_ui_status_results_output_files()

    def show_results_properties(self) -> None:
        """
        Populates the Results / Properties Files display.

        Returns:
            None
        """
        # Remove items from the Results Properties table (from a previous run).
        self.results_Properties_Table.setRowCount(0)

        # Populate the Results / Properties Table.
        # Iterate through all of the properties in the GeoProcessor.
        for prop_name, prop_value in self.gp.properties.items():
            # Get the index of the next available row in the table. Add a new row to the table.
            new_row_index = self.results_Properties_Table.rowCount()
            # print("Showing property name=" + str(prop_name) + " value=" + str(prop_value) + " row " +
            #      str(new_row_index))
            self.results_Properties_Table.insertRow(new_row_index)

            # Set the property name as the attribute for the Property Name column.
            self.results_Properties_Table.setItem(new_row_index, 0, QtWidgets.QTableWidgetItem(prop_name))

            # Set the property value as the attribute for the Property Value column.
            # - Have to cast to string because table is configured to display strings
            self.results_Properties_Table.setItem(new_row_index, 1, QtWidgets.QTableWidgetItem(str(prop_value)))

        self.results_Properties_Table.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.results_Properties_Table.resizeColumnsToContents()
        self.update_ui_status_results_properties()

    def show_results_tables(self) -> None:
        """
        Populates the Results / Tables Files display.

        Returns:
            None
        """
        # Remove items from the Results Tables table (from a previous run).
        self.results_Tables_Table.setRowCount(0)

        # Populate the Results / Tables Table.
        # Iterate through all of the Table objects in the GeoProcessor.
        for table in self.gp.tables:

            # Get the index of the next available row in the table. Add a new row to the table.
            new_row_index = self.results_Tables_Table.rowCount()
            self.results_Tables_Table.insertRow(new_row_index)

            # Retrieve the Tables's Table ID and set as the attribute for the Table ID column.
            self.results_Tables_Table.setItem(new_row_index, 0, QtWidgets.QTableWidgetItem(table.id))

            # Retrieve the number of columns in the Table and set as the attribute for the Column Count column.
            self.results_Tables_Table.setItem(new_row_index, 1,
                                              QtWidgets.QTableWidgetItem(str(table.count(returnCol=True))))

            # Retrieve the number of rows in the Table and set as the attribute for the Row Count column.
            self.results_Tables_Table.setItem(new_row_index, 2,
                                              QtWidgets.QTableWidgetItem(str(table.count(returnCol=False))))

        # Sort by Table ID
        # self.results_Tables_Table.sortByColumn(0, QtCore.Qt.AscendingOrder)

        # Update the results count and results' tables' labels to show that the results were populated.
        self.update_ui_status_results_tables()

    def ui_action_command_list_right_click(self, q_pos: int) -> None:
        """
        Open the Command_List widget right-click menu.
        REF: https://stackoverflow.com/questions/31380457/add-right-click-functionality-to-listwidget-in-pyqt4?
        utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

        Arg:
            q_pos (int): The position of the right-click. Updated automatically within interface.
                Do not need to manually pass a value to this variable.
                Used to determine where to display the popup menu.

        Returns:
            None
        """
        # Create the Qt Menu object if it has not previously been created.
        if self.rightClickMenu_Commands is None:
            self.rightClickMenu_Commands = QtWidgets.QMenu()

            # Add the menu options to the right-click menu and connect actions.
            self.menu_item_show_command_status = self.rightClickMenu_Commands.addAction("Show Command Status")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.menu_item_show_command_status.triggered.connect(self.show_command_status)

            self.rightClickMenu_Commands.addSeparator()
            self.menu_item_edit_command = self.rightClickMenu_Commands.addAction("Edit")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.menu_item_edit_command.triggered.connect(self.edit_command_editor)

            self.rightClickMenu_Commands.addSeparator()
            self.menu_item_cut_commands = self.rightClickMenu_Commands.addAction("Cut")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.menu_item_cut_commands.triggered.connect(self.cut_commands_to_clipboard)

            self.menu_item_copy_commands = self.rightClickMenu_Commands.addAction("Copy")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.menu_item_copy_commands.triggered.connect(self.copy_commands_to_clipboard)

            self.menu_item_paste_commands = self.rightClickMenu_Commands.addAction("Paste (after last selected)")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.menu_item_paste_commands.triggered.connect(self.paste_commands_from_clipboard)

            self.rightClickMenu_Commands.addSeparator()
            self.menu_item_delete_commands = self.rightClickMenu_Commands.addAction("Delete Command(s)")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.menu_item_delete_commands.triggered.connect(
                self.command_CommandListWidget.event_handler_button_clear_commands_clicked)

            self.rightClickMenu_Commands.addSeparator()
            self.menu_item_select_all_commands = self.rightClickMenu_Commands.addAction("Select All Commands")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.menu_item_select_all_commands.triggered.connect(self.select_all_commands)

            self.menu_item_deselect_all_commands = self.rightClickMenu_Commands.addAction("Deselect All Commands")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.menu_item_deselect_all_commands.triggered.connect(self.deselect_all_commands)

            self.rightClickMenu_Commands.addSeparator()
            self.menu_item_increase_indent_command = self.rightClickMenu_Commands.addAction("Increase Indent")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.menu_item_increase_indent_command.triggered.connect(
                self.command_CommandListWidget.event_handler_indent_button_clicked)

            self.menu_item_decrease_indent_command = self.rightClickMenu_Commands.addAction("Decrease Indent")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.menu_item_decrease_indent_command.triggered.connect(
                self.command_CommandListWidget.event_handler_decrease_indent_button_clicked)

            self.rightClickMenu_Commands.addSeparator()
            self.menu_item_convert_to_command = self.rightClickMenu_Commands.addAction(
                "Convert selected command(s) to # comments")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.menu_item_convert_to_command.triggered.connect(self.ui_action_command_list_right_click_convert_to_command)
            self.menu_item_convert_from_command = self.rightClickMenu_Commands.addAction(
                "Convert selected command(s) from # comments")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.menu_item_convert_from_command.triggered.connect(self.ui_action_command_list_right_click_convert_from_command)

            # Set the position on the right-click menu to appear at the click point.
            parent_pos = self.command_CommandListWidget.command_ListView.mapToGlobal(QtCore.QPoint(0, 0))
            self.rightClickMenu_Commands.move(parent_pos + q_pos)

        # Update the status of the menu to ensure accuracy
        self.update_ui_status_commands_popup()

        # Show the menu (it will be closed when user selects or escapes)
        self.rightClickMenu_Commands.show()

    def ui_action_command_list_right_click_convert_from_command(self) -> None:
        """
        Convert the selected command list item from a comment in geoprocessor.

        Returns:
            None
        """
        selected_indices = self.command_CommandListWidget.get_selected_indices()

        self.gp.convert_command_line_from_comment(selected_indices)

        #self.gp_model.update_command_list_ui()
        self.command_CommandListWidget.update_ui_status_commands()

    def ui_action_command_list_right_click_convert_to_command(self) -> None:
        """
        Convert the selected command list item to a comment in geoprocessor.

        Returns:
            None
        """
        selected_indices = self.command_CommandListWidget.get_selected_indices()

        self.gp.convert_command_line_to_comment(selected_indices)
        self.command_CommandListWidget.update_ui_status_commands()

        # self.gp_model.update_command_list_ui()

    def ui_action_geolayers_right_click(self, q_pos: int) -> None:
        """
        On right click display a tooltip on GeoLayer selected list item with options to
        open a map window or get the GeoLayer attributes.

        Args:
            q_pos (int): Position of mouse when right clicking on a GeoLayer from
                the output table.

        Returns:
            None
        """

        # Create the right click QMenu
        self.rightClickMenu_GeoLayers = QtWidgets.QMenu()

        # Add possible actions being Open Map or Attributes
        menu_item_map_command = self.rightClickMenu_GeoLayers.addAction("Open Map")
        menu_item_attributes = self.rightClickMenu_GeoLayers.addAction("Attributes")

        # Connect actions to the tooltip options
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        menu_item_map_command.triggered.connect(self.ui_action_open_map_window)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        menu_item_attributes.triggered.connect(self.ui_action_open_attributes)

        # Using the position of the mouse on right click decide where the tooltip should
        # be displayed
        parent_pos = self.results_GeoLayers_Table.mapToGlobal(QtCore.QPoint(0, 0))
        self.rightClickMenu_GeoLayers.move(parent_pos + q_pos)

        # Show the tooltip
        self.rightClickMenu_GeoLayers.show()

    # TODO smalers 2018-07-24 need to make the dialog nicer, including live link to OWF website
    def ui_action_help_about(self) -> None:
        """
        Display the Help / About dialog.

        Returns:
            None
        """
        # noinspection PyBroadException
        try:
            program_name = app_util.get_property('ProgramName')
            version = app_util.get_property('ProgramVersion')
            version_date = app_util.get_property('ProgramVersionDate')
            qt_util.info_message_box(
                program_name + " " + version + " (" + version_date + ")\n" +
                "Developed by the Open Water Foundation.\n" +
                "The GeoProcessor automates geospatial data processing.\n\n" +
                "Copyright 2017-2020 Open Water Foundation.\n" +
                "\n" +
                "License GPLv3+:  GNU GPL version 3 or later\n" +
                "\n" +
                "There is ABSOLUTELY NO WARRANTY; for details see the\n" +
                "'Disclaimer of Warranty' section of the GPLv3 license in the LICENSE file.\n" +
                "This is free software: you are free to change and redistribute it\n" +
                "under the conditions of the GPLv3 license in the LICENSE file.",
                "About GeoProcessor")
        except Exception:
            # Should not happen but does during initial development and UI code swallows exceptions so output to log
            logger = logging.getLogger(__name__)
            message = "Problem showing Help About"
            logger.warning(message, exc_info=True)

    def ui_action_help_software_system_information(self) -> None:
        """
        Display the Software/System information dialog.
        If taken from standard Python modules, also show the module and variable name so the information
        can be cross-checked manually if necessary.

        Returns:
            None
        """

        # noinspection PyBroadException
        try:
            # Local variables for operating system, used in checks below
            is_cygwin = os_util.is_cygwin_os()
            is_linux = os_util.is_linux_os()
            is_mingw = os_util.is_mingw_os()
            is_windows = os_util.is_windows_os()
            os_type = os_util.get_os_type()
            if os_type is None:
                os_type = "unknown"
            os_distro = os_util.get_os_distro()
            if os_distro is None:
                os_distro = "unknown"

            # Format a string with content for Software/System Information:
            TAB = "     "
            properties = ""

            program_name = app_util.get_property('ProgramName')
            version = app_util.get_property('ProgramVersion')
            version_date = app_util.get_property('ProgramVersionDate')
            user_name = os.getlogin()
            current_date = datetime.datetime.now()
            # TODO @jurentie get appropriate timezone if possible
            current_date = current_date.strftime("%c %Z")
            host = platform.uname()[1]
            working_dir = os.getcwd()
            program_home = app_util.get_property('ProgramHome')
            program_resources_path = app_util.get_property('ProgramResourcesPath')

            properties += ("GeoProcessor Application and Session Information:\n" +
                           TAB + "Program Name: " + program_name + " " + version + " " + version_date + "\n" +
                           TAB + "User Name: " + user_name + "\n" +
                           TAB + "Date: " + current_date + "\n" +
                           TAB + "Host: " + host + "\n" +
                           TAB + "Working Directory: " + working_dir + "\n" +
                           TAB + "Command: gpdev.bat --ui\n" +
                           TAB + 'Program Home: ' + program_home + "\n" +
                           TAB + 'Program Resources Path: ' + program_resources_path + "\n" +
                           "\n")

            operating_system = platform.uname()[0] + " " + platform.uname()[2]
            version = platform.uname()[3]
            version = version[0: version.rfind('.')]
            if is_windows:
                try:
                    architecture = os.environ["MSYSTEM_CARCH"]
                except KeyError:
                    # TODO smalers 2018-11-21 Need to fix the above to be portable
                    architecture = "unknown"
            else:
                architecture = "Code not implemented to check on operating system"

            properties += ("Operating System Information:\n" +
                           TAB + "Type: " + os_type + "\n" +
                           TAB + "Distribution: " + os_distro + "\n" +
                           TAB + "Name (platform.uname[0] and [2]): " + operating_system + "\n" +
                           TAB + "Version (platform.uname[3]): " + version + "\n")
            if is_windows:
                properties += (TAB + "System Architecture (os.environ['MSYSTEM_CARCH']): " + architecture + "\n")
            else:
                # Linux variant
                # - TODO smalers 2018-12-31 need to standardize
                properties += (TAB + "System Architecture: " + architecture + "\n")
            properties += "\n"

            # Replace newlines in system version
            system_version = sys.version.replace("\r\n", " ").replace("\n", " ")
            system_path = ''
            for line in sys.path[1:]:
                system_path += str(line) + '\n' + TAB + TAB

            # Python properties

            properties += ("Python Information:\n" +
                           TAB + 'Python Executable (sys.executable): ' + str(sys.executable) + "\n" +
                           TAB + 'Python Version (sys.version): ' + system_version + "\n" +
                           TAB + 'Python Bit Size: ' + str(8*struct.calcsize("P")) + "\n" +
                           TAB + 'Python Path (sys.path):\n' +
                           TAB + TAB + system_path + "\n")

            # Check if QGIS is being used at runtime
            # - may want to provide information about what is installed even if not used at runtime but
            #   that could be confusing and documentation troubleshooting can help figure out issues
            qgis_install_type = "Unknown"
            if app_util.is_qgis_install_standalone():
                qgis_install_type = "Standalone installation"
                qgis_install_folder = app_util.get_qgis_install_folder()
            elif app_util.is_qgis_install_osgeo():
                qgis_install_type = "OSGeo4W installation"
                qgis_install_folder = app_util.get_qgis_install_folder()
            else:
                qgis_install_type = "Unknown"
            qgis_name = "qgis"
            qgis_version = qgis.utils.Qgis.QGIS_VERSION

            # The QGIS environment variables are set by configuration scripts prior to running Python GeoProcessor
            # - output in case they are useful for troubleshooting
            # - use str() to sensure that None values won't cause problems
            if qgis_install_type == "Unknown":
                # QGIS does not appear to be used at runtime so provide minimal information
                properties += (
                            "QGIS Information:\n" +
                            TAB + "QGIS Installation Type: " + str(qgis_install_type) + "\n" +
                            TAB + "The GeoProcessor testing framework is being used without QGIS dependencies.\n" +
                            "\n"
                )
            else:
                qgis_root = ""
                properties += (
                               "QGIS Properties:\n" +
                               TAB + "QGIS Installation Type: " + str(qgis_install_type) + "\n" +
                               TAB + "QGIS Installation Folder: " + str(qgis_install_folder) + "\n" +
                               TAB + "QGIS Version: " + str(qgis_version) + "\n" +
                               TAB + "QGIS Environment Variables (set up by QGIS and GeoProcessor startup scripts):\n" +
                               TAB + TAB + "GDAL_DATA: " + str(os.environ.get('GDAL_DATA')) + "\n" +
                               TAB + TAB + "GDAL_DRIVER_PATH: " + str(os.environ.get('GDAL_DRIVER_PATH')) + "\n" +
                               TAB + TAB + "GDAL_FILENAME_IS_UTF8: " + str(os.environ.get('GDAL_FILENAME_IS_UTF8')) +
                               "\n" +
                               TAB + TAB + "GEOTIFF_CSV: " + str(os.environ.get('GEOTIFF_CSV')) + "\n" +
                               TAB + TAB + "OSGEO4W_ROOT: " + str(os.environ.get('OSGEO4W_ROOT')) + "\n" +
                               TAB + TAB + "O4W_QT_BINARIES: " + str(os.environ.get('O4W_QT_BINARIES')) + "\n" +
                               TAB + TAB + "O4W_QT_DOC: " + str(os.environ.get('O4W_QT_DOC')) + "\n" +
                               TAB + TAB + "O4W_QT_HEADERS: " + str(os.environ.get('O4W_QT_HEADERS')) + "\n" +
                               TAB + TAB + "O4W_QT_LIBRARIES: " + str(os.environ.get('O4W_QT_LIBRARIES')) + "\n" +
                               TAB + TAB + "O4W_QT_PLUGINS: " + str(os.environ.get('O4W_QT_PLUGINS')) + "\n" +
                               TAB + TAB + "O4W_QT_PREFIX: " + str(os.environ.get('O4W_QT_PREFIX')) + "\n" +
                               TAB + TAB + "O4W_QT_TRANSLATIONS: " + str(os.environ.get('O4W_QT_TRANSLATION')) + "\n" +
                               TAB + TAB + "PYTHONHOME: " + str(os.environ.get('PYTHONHOME')) + "\n" +
                               TAB + TAB + "QGIS_PREFIX_PATH: " + str(os.environ.get('QGIS_PREFIX_PATH')) + "\n" +
                               TAB + TAB + "QT_PLUGIN_PATH: " + str(os.environ.get('QT_PLUGIN_PATH')) + "\n" +
                               TAB + TAB + "VSI_CACHE: " + str(os.environ.get('VSI_CACHE')) + "\n" +
                               TAB + TAB + "VSI_CACHE_SIZE: " + str(os.environ.get('VSI_CACHE_SIZE')) + "\n" +
                               "\n")

            # Add information for Qt

            properties += (
                 "Qt Information (used for graphics):\n" +
                 TAB + "Qt Version: " + QtCore.QT_VERSION_STR + "\n" +
                 TAB + "SIP Version: " + SIP_VERSION_STR + "\n" +
                 TAB + "PyQt Version: " + Qt.PYQT_VERSION_STR + "\n" +
                 "\n")

            # Create Software/System Information Dialog Box
            self.sys_info = QtWidgets.QDialog()
            self.sys_info.resize(800, 500)
            self.sys_info.setWindowTitle("Software/System Information")
            self.sys_info.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
            icon_path = app_util.get_property("ProgramIconPath").replace('\\', '/')
            self.sys_info.setWindowIcon(QtGui.QIcon(icon_path))
            self.sys_info_text_browser = QtWidgets.QTextBrowser(self.sys_info)
            self.sys_info_text_browser.setGeometry(QtCore.QRect(25, 20, 750, 550))
            self.sys_info_text_browser.setText(properties)
            self.sys_info_text_browser.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
            # Will implement copy button later once with a better understanding
            # self.push_button = QtWidgets.QPushButton(self.sys_info)
            # self.push_button.setGeometry(QtCore.QRect(300,460,75,23))
            # self.push_button.setText("Copy")
            # self.push_button.clicked.connect(lambda:self.copy_text(properties))
            QtCore.QMetaObject.connectSlotsByName(self.sys_info)
            # Reassign default resizeEvent() to resizeTextBox()
            self.sys_info.resizeEvent = self.ui_action_resize_software_system_information_text_box
            self.sys_info.show()
        except Exception:
            logger = logging.getLogger(__name__)
            message = 'Error getting software/system information.'
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

    def ui_action_map_pan(self) -> None:
        """
        Set GeoLayers map dialog window to allow user to pan with the mouse events.

        Returns:
            None
        """
        self.canvas.setMapTool(self.toolPan)

    def ui_action_map_resize(self, event) -> None:
        """
        Resize the GeoLayers map canvas when the dialog box is resized.

        Args:
            event: Resize event, necessary to add even though it is not being used in order
                for it to be recognized as a slot to respond to the given signal from the event.

        Returns:
            None
        """
        if event is None:
            # Use this to avoid warning about 'event' not being used
            pass
        self.canvas.resize(self.map_window_widget.width(), self.map_window_widget.height())

    def ui_action_map_zoom_in(self) -> None:
        """
        Set the GeoLayers map window to respond to mouse events as zooming in.

        Returns:
            None
        """
        self.canvas.setMapTool(self.toolZoomIn)

    def ui_action_map_zoom_out(self) -> None:
        """
        Set the GeoLayers map window to respond to mouse events as zooming out.

        Returns:
            None
        """
        self.canvas.setMapTool(self.toolZoomOut)

    def ui_action_new_command_file(self) -> None:
        """
        Start a new command file by clearing the current commands list and unsetting the saved command file.
        Users are not required to save the command file until they take another action such as exit, or open.

        Returns:
            None
        """
        # Command file has not been saved
        self.command_file_saved = False
        # Use functions for CloseEvent override to see if user has edited command file and if so
        # prompt user to save...
        self.closeEvent_save_command_file()

        # Set opened file to false since we are now opening a new command file
        self.opened_command_file = False

        # Clear commands from geoprocessor
        self.gp_model.clear_all_commands()

        # Call function to initialize necessary values for new command file
        self.gp_model.new_command_list()

        # Set the title for the main window
        self.ui_set_main_window_title("commands not saved")

    def ui_action_open_attributes(self) -> None:
        """
        Create an attributes window to be opened when user clicks on GeoLayers.

        Returns:
            None
        """
        logger = logging.getLogger(__name__)
        # noinspection PyBroadException
        try:
            # Create attributes window dialog box
            self.attributes_window = QtWidgets.QDialog()
            self.attributes_window.resize(800, 500)
            self.attributes_window.setWindowTitle("Attributes")
            self.attributes_window.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
            # Add icon
            icon_path = app_util.get_property("ProgramIconPath").replace('\\', '/')
            self.attributes_window.setWindowIcon(QtGui.QIcon(icon_path))

            # Create a vertical layout for the map window
            self.attributes_window_layout = QtWidgets.QVBoxLayout(self.attributes_window)
            self.attributes_window_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
            self.attributes_window_layout.setObjectName(qt_util.from_utf8("mapVerticalLayout"))

            # Get GeoLayer from Table
            selected_row_index = self.results_GeoLayers_Table.currentRow()
            selected_geolayer = self.gp.geolayers[selected_row_index]
            selected_vector_layer = selected_geolayer.qgs_layer

            # Get features from vector layer
            features = selected_vector_layer.getFeatures()
            num_features = selected_vector_layer.featureCount()
            # Get attribute field names
            attribute_field_names = selected_geolayer.get_attribute_field_names()

            # Create a table for attributes
            self.attributes_table = QtWidgets.QTableWidget()
            self.attributes_window_layout.addWidget(self.attributes_table)
            self.attributes_table.setColumnCount(len(attribute_field_names))
            self.attributes_table.setRowCount(num_features)

            # Set Column Headers
            for i, attribute_field in enumerate(attribute_field_names):
                item = QtWidgets.QTableWidgetItem()
                self.attributes_table.setHorizontalHeaderItem(i, item)
                self.attributes_table.horizontalHeaderItem(i).setText(str(attribute_field))

            # Customize Header Row
            self.attributes_table.horizontalHeader().setStyleSheet("::section { background-color: #d3d3d3 }")

            # Retrieve attributes per feature and add them to the table
            for i, feature in enumerate(features):
                for j, attribute_field in enumerate(attribute_field_names):
                    attribute = feature[attribute_field]
                    item = QtWidgets.QTableWidgetItem(str(attribute))
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.attributes_table.setItem(i, j, item)

            self.attributes_window.show()
        except Exception:
            message = "Error opening attributes window.  See the log file."
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

    def ui_action_open_command_file(self, filename: str = "") -> bool or None:
        """
        Open a command file. Each line of the command file is a separate item in the Command_List QList Widget.
        If the existing commands have not been saved, the user is prompted to ask if they should be saved
        before reading the indicated filename.

        Args:
            filename (str):
                the absolute path to the command file to open, if blank prompt for the file and otherwise
                open the file

        Returns:
            True if the command file was opened and loaded into command list, False if error or canceled.
        """

        # This command file has previously been saved
        self.command_file_saved = True

        self.closeEvent_save_command_file()

        logger = logging.getLogger(__name__)
        self.opened_command_file = True

        cmd_filepath = ""

        if filename == "":
            # The File / Open / Command File... menu has been selected, in which case the user is
            # browsing for the command file.  Open the dialog by starting in the folder for the most recent
            # file in the history, or otherwise the user's home folder.
            last_opened_folder = ""
            command_file_list = self.app_session.read_history()
            if command_file_list and len(command_file_list) > 0:
                # The history has at least one file so the most recent file can be used to provide
                # the starting folder.
                last_opened_file = command_file_list[0]
                index = last_opened_file.rfind('/')
                last_opened_folder = last_opened_file[:index]
            else:
                # The history did not have any files so default to starting in the user's home folder.
                last_opened_folder = self.app_session.get_user_folder()

            # A browser window will appear to allow the user to browse to the desired command file.
            # The absolute pathname of the command file is added to the cmd_filepath variable.
            cmd_filepath = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", last_opened_folder)[0]
            if not cmd_filepath:
                return False
        else:
            # A command file name has been selected from the history list in File / Open
            logger.info("In ui_action_open_command_file, request to open command file " + filename)
            cmd_filepath = filename

        # Read the command file in GeoProcessor.
        # The previous command file lines in the UI are discarded.
        try:
            # Read using the GeoProcessorModel that is managed by the command list
            self.command_CommandListWidget.gp_model.read_command_file(cmd_filepath)
        except FileNotFoundError:
            # The file should exist but may have been deleted outside of the UI
            # - TODO smalers 2019-01-19 may automatically remove such files,
            #   or leave assuming the user will rename, move the file back again.
            message = 'Selected command file does not exist (maybe deleted or renamed?):\n"' + cmd_filepath + '"'
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
            # Return so history is not changed to include a file that does not exist
            return False

        # Push new command onto history
        self.app_session.push_history(cmd_filepath)

        # Set this file path as the path to save if the user click "Save Commands ..."
        self.saved_file = cmd_filepath

        # Set the title for the main window
        self.ui_set_main_window_title('"' + cmd_filepath + '"')

        # Update recently opened files in file menu
        self.ui_init_file_open_recent_files()

        # Return True meaning a command file was opened
        logger.info("Model size after reading command file=" + str(self.gp_model.rowCount(QtCore.QModelIndex())))
        return True

    def ui_action_open_map_window(self) -> None:
        """
        Open a map window dialog box that displays the map layers from the selected GeoLayers.

        Returns:
            None
        """
        logger = logging.getLogger(__name__)

        # noinspection PyBroadException
        try:
            # Create map window dialog box
            self.map_window = QtWidgets.QDialog()
            self.map_window.resize(800, 500)
            self.map_window.setWindowTitle("Map")
            self.map_window.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
            # Add icon
            icon_path = app_util.get_property("ProgramIconPath").replace('\\', '/')
            self.map_window.setWindowIcon(QtGui.QIcon(icon_path))

            # Create a vertical layout for the map window
            self.map_window_layout = QtWidgets.QVBoxLayout(self.map_window)
            self.map_window_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
            self.map_window_layout.setObjectName(qt_util.from_utf8("mapVerticalLayout"))

            # Add toolbar to map window
            self.map_toolbar = QtWidgets.QToolBar()
            self.map_window_layout.addWidget(self.map_toolbar)

            # Create a widget for the canvas and add it to map_window in the map_window_layout
            self.map_window_widget = QtWidgets.QWidget()
            self.map_window_layout.addWidget(self.map_window_widget)
            self.map_window_widget.setGeometry(QtCore.QRect(25, 20, 750, 450))
            # Create canvas and add it to the previously widget
            self.canvas = qgis.gui.QgsMapCanvas(self.map_window_widget)
            self.canvas.setCanvasColor(QtCore.Qt.white)
            self.canvas.resize(750, 400)

            # Retrieve QgsVectorLayers from selected geolayers
            # - this retrieves selected indices
            # selected_rows = self.results_GeoLayers_Table.selectedIndexes()
            selected_rows = qt_util.get_table_rows_from_indexes(self.results_GeoLayers_Table.selectedIndexes())
            selected_geolayers = []
            for row in selected_rows:
                geolayer = self.gp.geolayers[row]
                if geolayer.is_vector():
                    logger.info("Appending vector layer \"" + geolayer.id + "\" [" + str(row) + "] for map ")
                elif geolayer.is_raster():
                    logger.info("Appending raster layer \"" + geolayer.id + "\" [" + str(row) + "] for map ")
                selected_geolayers.append(geolayer.qgs_layer)

            # Get the extent for all the layers by calling qgis_util
            logger.info("Have " + str(len(selected_geolayers)) + " selected layers")
            extent = qgis_util.get_extent_from_geolayers(selected_geolayers)
            self.canvas.setExtent(extent)
            self.canvas.setLayers(selected_geolayers)

            # Add tools for map canvas
            self.actionZoomIn = QtWidgets.QAction("Zoom in", self)
            self.actionZoomIn.setToolTip("Zoom in by clicking on a location to center on.")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.actionZoomIn.triggered.connect(self.ui_action_map_zoom_in)
            self.actionZoomIn.setCheckable(True)
            self.map_toolbar.addAction(self.actionZoomIn)

            self.actionZoomOut = QtWidgets.QAction("Zoom out", self)
            self.actionZoomOut.setToolTip("Zoom out by clicking on a location to center on.")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.actionZoomOut.triggered.connect(self.ui_action_map_zoom_out)
            self.actionZoomOut.setCheckable(True)
            self.map_toolbar.addAction(self.actionZoomOut)

            self.actionPan = QtWidgets.QAction("Pan", self)
            self.actionPan.setToolTip("Use mouse to drag the viewing area.")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.actionPan.triggered.connect(self.ui_action_map_pan)
            self.actionPan.setCheckable(True)
            self.map_toolbar.addAction(self.actionPan)

            # # Add tools to canvas
            self.toolPan = qgis.gui.QgsMapToolPan(self.canvas)
            self.toolPan.setAction(self.actionPan)
            self.toolZoomIn = qgis.gui.QgsMapToolZoom(self.canvas, False)  # false = in
            self.toolZoomIn.setAction(self.actionZoomIn)
            self.toolZoomOut = qgis.gui.QgsMapToolZoom(self.canvas, True)  # true = out
            self.toolZoomOut.setAction(self.actionZoomOut)

            QtCore.QMetaObject.connectSlotsByName(self.map_window)
            # Assign a resize event to resize map canvas when dialog window is resized
            self.map_window_widget.resizeEvent = self.ui_action_map_resize
            self.map_window.show()
        except Exception:
            message = "Error opening map window.  See the log file."
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

    def ui_action_print_commands(self) -> None:
        """
        Print the command file.
        This is currently not enabled other than to print a dialog.

        Returns:
            None
        """
        # Set the title for the main window
        qt_util.info_message_box("Printing features have not yet been implemented.")

    def ui_action_resize_software_system_information_text_box(self, event) -> None:
        """
        Resize the text box for the Software/System Information dialog window.

        Args:
            event: Resize Event

        Returns:
            None
        """
        self.sys_info_text_browser.resize(self.sys_info.width()-50, self.sys_info.height()-50)

    def ui_action_save_commands(self) -> None:
        """
        Saves the commands to a previously saved file location (overwrite).

        Returns:
            None
        """

        # Record the new saved command file in the command list backup class
        self.gp_model.update_command_list_backup()

        # If there is not a previously saved file location, save the file with the save_command_as function.
        if self.saved_file is None:
            self.ui_action_save_commands_as()

        # If there is a previously saved file location, continue.
        else:

            # A list to hold each command as a separate string.
            list_of_cmds = []

            # Iterate over the items in the command_ListWidget widget.
            for i in range(self.command_CommandListWidget.command_ListView.count()):

                # Add the command string text ot the list_of_cmds list.
                list_of_cmds.append(self.command_CommandListWidget.command_ListView.item(i).text())

            # Join all of the command strings together (separated by a line break).
            all_commands_string = '\n'.join(list_of_cmds)

            # Write the commands to the previously saved file location (overwrite).
            file = open(self.saved_file, 'w')
            file.write(all_commands_string)
            file.close()

            # Update command file history list in GUI
            self.ui_init_file_open_recent_files()

    def ui_action_save_commands_as(self) -> None:
        """
        Saves the commands to a file.

        Returns:
            None if no file name specified.
        """

        # Record the new saved command file in the command list backup class
        self.gp_model.update_command_list_backup()

        # TODO egiles 2018-16-05 Discuss with Steve about line breaks for Linux/Windows OS

        # A list to hold each command as a separate string.
        list_of_cmds = []

        # Iterate over the items in the command_ListWidget widget.
        for i in range(self.command_CommandListWidget.command_ListView.count()):

            # Add the command string text ot the list_of_cmds list.
            list_of_cmds.append(self.command_CommandListWidget.command_ListView.item(i).text())

        # Join all of the command strings together (separated by a line break).
        all_commands_string = '\n'.join(list_of_cmds)

        # Create a QDialog window instance.
        d = QtWidgets.QDialog()

        # Try to get the last opened folder
        last_opened_folder = ""
        command_file_list = self.app_session.read_history()
        if command_file_list and len(command_file_list) > 0:
            # The history has at least one file so the most recent file can be used to provide
            # the starting folder.
            last_opened_file = command_file_list[0]
            index = last_opened_file.rfind('/')
            last_opened_folder = last_opened_file[:index]
        else:
            # The history did not have any files so default to starting in the user's home folder.
            last_opened_folder = self.app_session.get_user_folder()

        # Open a browser for the user to select a location and filename to save the command file. Set the most recent
        # file save location.
        self.saved_file = QtWidgets.QFileDialog.getSaveFileName(d, 'Save Command File As', last_opened_folder)[0]

        if self.saved_file == "":
            return

        # Write the commands to the file.
        file = open(self.saved_file, 'w')
        file.write(all_commands_string)
        file.close()

        # This command file has now been saved
        self.command_file_saved = True

        # Save the command file name in the command file history
        self.app_session.push_history(self.saved_file)

        # Update the recent files in the File... Open menu, for the next menu access
        self.ui_init_file_open_recent_files()

    @classmethod
    def ui_action_view_documentation(cls) -> None:
        """
        Opens the GeoProcessor user documentation in the user's default browser.

        Returns:
            None
        """

        # Open the GeoProcessor user documentation in the default browser (new window).
        logger = logging.getLogger(__name__)
        user_doc_url = None
        try:
            user_doc_url = app_util.get_property('ProgramUserDocumentationUrl')
            message = "Displaying documentation using URL: " + user_doc_url
            logger.info(message)
            webbrowser.open_new_tab(user_doc_url)
        # noinspection PyBroadException
        except Exception:
            message = 'Error viewing documentation for url "' + user_doc_url + '"'
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

    def ui_action_view_log_file(self) -> None:
        """
        Opens the current log file in the default text editor for operating system.

        Returns:
            None
        """
        logger = logging.getLogger(__name__)
        logfile_name = log_util.get_logfile_name()
        if logfile_name is None:
            # This should not happen because the startup logfile should be the current logfile at startup,
            # and then the StartLog command will open a new log file as the current log file.
            message = 'The logfile is not available.  Try viewing the startup log file.'
            qt_util.warning_message_box(message)
            return

        # Normal case is that a log file will always be available
        try:
            # TODO smalers 2018-11-21 the following works on Windows - need to support other operating systems
            if os_util.is_windows_os():
                os.startfile(logfile_name)
            elif os_util.is_cygwin_os():
                message = 'The log file viewer for Cygwin has not been implemented'
                qt_util.warning_message_box(message)
            elif os_util.is_linux_os():
                try:
                    subprocess.call('xdg-open', logfile_name)
                except (AttributeError, FileNotFoundError, NotImplementedError):
                    # Log the message to help with development
                    message = 'Error viewing log file using xdg-open ' + logfile_name
                    logger.warning(message, exc_info=True)
                    # Try to use nano as a default visual editor
                    # - TODO smalers 2018-12-28 need to figure out what is installed rather than hard-code nano
                    try:
                        subprocess.call('nano', logfile_name)
                    except (AttributeError, FileNotFoundError, NotImplementedError):
                        message = 'Error viewing log file - no application available for log file and' + \
                                  'also tried nano editor for log file "' + logfile_name + '"'
                        qt_util.warning_message_box(message)
        except (AttributeError, FileNotFoundError, NotImplementedError):
            message = 'Error viewing log file - no application available for log file "' + logfile_name + '"'
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

    def ui_action_view_startup_log_file(self) -> None:
        """
        Opens the startup log file in the default text editor for operating system.

        Returns:
            None
        """
        logger = logging.getLogger(__name__)
        logfile_name = self.app_session.get_user_log_file()
        if logfile_name is None:
            # This should not happen because the startup logfile should always exist, unless there is a file
            # permissions problem.
            message = 'The logfile is not available.'
            qt_util.warning_message_box(message)
            return

        try:
            # TODO smalers 2018-11-21 the following works on Windows - need to support other operating systems
            if os_util.is_windows_os():
                os.startfile(logfile_name)
            elif os_util.is_cygwin_os():
                message = 'The log file viewer for Cygwin has not been implemented'
                qt_util.warning_message_box(message)
            elif os_util.is_linux_os():
                try:
                    subprocess.call('xdg-open', logfile_name)
                except (AttributeError, FileNotFoundError, NotImplementedError):
                    # Log the message to help with development
                    message = 'Error viewing log file using xdg-open ' + logfile_name
                    logger.warning(message, exc_info=True)
                    # Try to use nano as a default visual editor
                    # - TODO smalers 2018-12-28 need to figure out what is installed rather than hard-code nano
                    try:
                        subprocess.call('nano', logfile_name)
                    except (AttributeError, FileNotFoundError, NotImplementedError):
                        message = 'Error viewing log file - no application available for log file and' + \
                                  'also tried nano editor for log file "' + logfile_name + '"'
                        qt_util.warning_message_box(message)
        except (AttributeError, FileNotFoundError, NotImplementedError):
            message = 'Error viewing log file - no application available for log file "' + logfile_name + '"'
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

    def ui_init_file_open_recent_files(self) -> None:
        """
        Update the File / Open / Command File... menu items to list the most recently opened command files.
        The menu will then be properly updated when opening a new command file.
        This function should be called whenever the command file history is written so that the history file and
        menu are synchronized.

        Returns:
            None
        """
        logger = logging.getLogger(__name__)
        # Set the maximum amount of recent command files to open.
        # If there are less than 20 cached commands in the command file history then set the maximum to be the
        # number of recently opened files.
        # If there are more than 20 cached commands in the command file history set the maximum to 20.
        max_files = self.command_file_menu_max  # Default size of command file history in menu
        # Read the list of command files
        command_file_list = self.app_session.read_history()
        command_file_list_len = len(command_file_list)
        if command_file_list_len < max_files:
            # There are less than the maximum number of files in the history so reset the maximum
            max_files = command_file_list_len
        # Always iterate through the maximum of command files in the menu to ensure that old event handlers
        # are disconnected.
        for i in range(0, self.command_file_menu_max):
            # TODO smalers 2018-12-29 why is the following needed?
            # - it seems like the File / Open / Command File... menu has exactly the right number of items
            #   and does not need any blank placeholders?
            # - or the placeholders needed to make sure that event handling is always handled up to max items?
            if i >= command_file_list_len:
                command_file = ""
            else:
                command_file = command_file_list[i]
            # First disconnect the event handler that was initially set up
            self.Menu_File_Open_CommandFileHistory_List[i].triggered.disconnect()
            self.Menu_File_Open_CommandFileHistory_List[i].setText(command_file)
            self.Menu_File_Open_CommandFileHistory_List[i].setObjectName(
                qt_util.from_utf8("Menu_File_Open_CommandFileHistory_Command_" + str(i)))
            self.Menu_File_Open_CommandFileHistory_List[i].triggered.connect(
                lambda checked, filename=command_file: self.ui_action_open_command_file(filename))
            self.Menu_File_Open.addAction(self.Menu_File_Open_CommandFileHistory_List[i])

    def ui_set_main_window_title(self, title: str) -> None:
        """
        Set the main window title.
        This is called to indicate the status of the command file.

        Args:
            title (str): Title for main window.

        Returns:
            None
        """
        self.setWindowTitle("GeoProcessor - " + title)  # Initial title

    def update_ui_main_window_title(self) -> None:
        """
        Update the main window title to reflect that the command file has been modified.

        Returns:
            None
        """

        # Get the current window title
        window_title = self.windowTitle()
        window_title_end = window_title[-10:]
        # First check to see if the command file has been modified
        if self.command_CommandListWidget.command_list_modified():
            if window_title_end != "(modified)" and window_title != "GeoProcessor - commands not saved":
                window_title_modified = window_title + " (modified)"
                self.setWindowTitle(window_title_modified)
        # If not modified it must have been returned to the original state so remove the modified indication
        else:
            if window_title_end == "(modified)":
                length = len(window_title)
                self.setWindowTitle(window_title[:length-10])

    def update_ui_commands_list(self) -> None:
        """
        Once commands have been run. Loop through and check for any errors or warnings.

        Returns:
            None
        """
        gp = self.gp
        for i in range(0, self.command_ListView.count()):
            # TODO jurentie may update to handle Discovery errors once implemented in GeoProcessor
            command_status = gp.commands[i].command_status.run_status
            if command_status is CommandStatusType.FAILURE:
                self.numbered_list_error_at_row(i)
                self.gutter_error_at_row(i)
            elif command_status is CommandStatusType.WARNING:
                self.numbered_list_warning_at_row(i)
                self.gutter_warning_at_row(i)

    def update_ui_status(self) -> None:
        """
        Update the UI status by checking data and setting various status information.

        Returns:
            None
        """
        self.update_ui_status_commands_popup()
        self.update_ui_status_results_geolayers()
        self.update_ui_status_results_maps()
        self.update_ui_status_results_output_files()
        self.update_ui_status_results_properties()
        self.update_ui_status_results_tables()

    def update_ui_status_commands_popup(self) -> None:
        """
        Update the status of the command popup menu.

        Returns:

        """
        # Adjust whether menus are enabled or disabled based on the state of the data
        num_commands = len(self.gp)
        selected_indices = self.command_CommandListWidget.get_selected_indices()
        num_selected = len(selected_indices)
        if num_selected > 0:
            self.menu_item_show_command_status.setEnabled(True)
            self.menu_item_edit_command.setEnabled(True)
            self.menu_item_cut_commands.setEnabled(False)  # TODO smalers 2020-01-20 need to enable
            self.menu_item_copy_commands.setEnabled(False)
            self.menu_item_paste_commands.setEnabled(False)
            self.menu_item_deselect_all_commands.setEnabled(True)
            self.menu_item_increase_indent_command.setEnabled(True)
            self.menu_item_decrease_indent_command.setEnabled(True)
            self.menu_item_convert_from_command.setEnabled(True)
            self.menu_item_convert_to_command.setEnabled(True)

            self.increase_indent_button.setEnabled(True)
            self.decrease_indent_button.setEnabled(True)
        else:
            self.menu_item_show_command_status.setEnabled(False)
            self.menu_item_edit_command.setEnabled(False)
            self.menu_item_cut_commands.setEnabled(False)  # TODO smalers 2020-01-20 need to enable
            self.menu_item_copy_commands.setEnabled(False)
            self.menu_item_paste_commands.setEnabled(False)
            self.menu_item_deselect_all_commands.setEnabled(False)
            self.menu_item_increase_indent_command.setEnabled(False)
            self.menu_item_decrease_indent_command.setEnabled(False)
            self.menu_item_convert_from_command.setEnabled(False)
            self.menu_item_convert_to_command.setEnabled(False)

            self.increase_indent_button.setEnabled(False)
            self.decrease_indent_button.setEnabled(False)

        if num_commands == num_selected:
            self.menu_item_select_all_commands.setEnabled(False)
        else:
            self.menu_item_select_all_commands.setEnabled(True)

        if num_commands > 0:
            self.menu_item_delete_commands.setEnabled(True)
        else:
            self.menu_item_delete_commands.setEnabled(False)

    def update_ui_status_results_geolayers(self) -> None:
        """
        Update the UI status for Results / GeoLayers area.

        Returns:
            None
        """
        # Count the total and selected number of rows within the GeoLayers table. Update the label to reflect counts.
        row_num = str(self.results_GeoLayers_Table.rowCount())
        selected_rows = qt_util.get_table_rows_from_indexes(self.results_GeoLayers_Table.selectedIndexes())
        self.results_GeoLayers_GroupBox.setTitle(
            "GeoLayers ({} GeoLayers, {} selected)".format(row_num, len(selected_rows)))

    def update_ui_status_results_maps(self) -> None:
        """
        Update the UI status for Results / Maps area.

        Returns:
            None
        """
        # Count the total and selected number of rows within the Maps table. Update the label to reflect counts.
        row_num = str(self.results_Maps_Table.rowCount())
        # slct_row_num = str(len(set(index.row() for index in self.results_Maps_Table.selectedIndexes())))
        slct_row_num = str(len(self.results_Maps_Table.selectedIndexes()))
        self.results_Maps_GroupBox.setTitle("Maps ({} Maps, {} selected)".format(row_num, slct_row_num))

    def update_ui_status_results_output_files(self) -> None:
        """
        Update the UI status for Results / Output Files area.

        Returns:
            None
        """
        # Count the total and selected number of rows within the Output Files table. Update the label to reflect counts.
        row_num = str(self.results_OutputFiles_Table.rowCount())
        # slct_row_num = str(len(set(index.row() for index in self.results_OutputFiles_Table.selectedIndexes())))
        slct_row_num = str(len(self.results_OutputFiles_Table.selectedIndexes()))
        self.results_OutputFiles_GroupBox.setTitle(
            "Output Files ({} Output Files, {} selected)".format(row_num, slct_row_num))

        # Hide last column to ensure horizontal scroll
        self.results_OutputFiles_Table.setColumnWidth(1, 0)

    def update_ui_status_results_properties(self) -> None:
        """
        Update the UI status for Results / GeoLayers area.

        Returns:
            None
        """

        # Count the total and selected number of rows within the Properties table. Update the label to reflect counts.
        row_num = str(self.results_Properties_Table.rowCount())
        # slct_row_num = str(len(set(index.row() for index in self.results_GeoLayers_Table.selectedIndexes())))
        slct_row_num = str(len(self.results_Properties_Table.selectedIndexes()))
        self.results_Properties_GroupBox.setTitle(
            "Properties ({} Properties, {} selected)".format(row_num, slct_row_num))

        self.results_Properties_Table.setColumnWidth(2, 0)

    def update_ui_status_results_tables(self) -> None:
        """
        Update the UI status for Results / Tables area.

        Returns:
            None
        """
        # Count the total and selected number of rows within the Tables table. Update the label to reflect counts.
        row_num = str(self.results_Tables_Table.rowCount())
        slct_row_num = str(len(set(index.row() for index in self.results_Tables_Table.selectedIndexes())))
        self.results_Tables_GroupBox.setTitle("Tables ({} Tables, {} selected)".format(row_num, slct_row_num))
