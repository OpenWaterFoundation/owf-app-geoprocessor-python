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

# The following is needed to allow type hinting -> GeoLayer, and requires Python 3.7+
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
import geoprocessor.util.string_util as string_util
from geoprocessor.ui.app.CommandListWidget import CommandListWidget  # previously command_list_view
from geoprocessor.ui.app.GeoLayerAttributesQDialog import GeoLayerAttributesQDialog
from geoprocessor.ui.app.GeoLayerMapQDialog import GeoLayerMapQDialog
from geoprocessor.ui.app.TableQDialog import TableQDialog
# from geoprocessor.ui.core.GeoProcessorListModel import GeoProcessorListModel  # previously gp_list_model
from geoprocessor.ui.core.GeoProcessorListModel import GeoProcessorListModel
from geoprocessor.ui.util.CommandListBackup import CommandListBackup  # previously command_list_backup
import geoprocessor.ui.util.qt_util as qt_util

import datetime
import functools
import logging
import os
from pathlib import Path
import platform
import qgis.utils
import qgis.gui
import shlex  # used to parse command line with spaces and quotes
import struct
import subprocess
import sys
import tempfile
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

        # GeoProcessorListModel that manages the commands, initialized when UI is created
        self.gp_model = None

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
        # - TODO smalers 2020-01-15 catalog area has not yet been implemented
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
        self.menu_item_show_command_status: QtWidgets.QAction or None = None
        self.menu_item_edit_command: QtWidgets.QAction or None = None
        self.menu_item_cut_commands: QtWidgets.QAction or None = None
        self.menu_item_copy_commands: QtWidgets.QAction or None = None
        self.menu_item_paste_commands: QtWidgets.QAction or None = None
        self.menu_item_delete_commands: QtWidgets.QAction or None = None
        self.menu_item_increase_indent_command: QtWidgets.QAction or None = None
        self.menu_item_decrease_indent_command: QtWidgets.QAction or None = None
        self.menu_item_convert_from_command: QtWidgets.QAction or None = None
        self.menu_item_convert_to_command: QtWidgets.QAction or None = None
        self.menu_item_select_all_commands: QtWidgets.QAction or None = None
        self.menu_item_deselect_all_commands: QtWidgets.QAction or None = None

        self.commands_cut_buffer: [AbstractCommand] = []  # List of commands for cut/copy/paste

        # Dialog for command status
        # - apparently cannot make 'command_status_dialog' - must be a class member or goes out of scope in function?
        self.command_status_dialog: QtWidgets.QDialog or None = None

        # Dialogs that must be global.
        # - otherwise they go out of scope in function and are closed automatically and immediately after opening
        # - use open_dialog() to open an instance and add to this list
        # - TODO smalers 2020-11-15 need to add a close_dialog() function to remove from the list
        self.dialogs: {QtWidgets.QDialog} = {}

        # Results area
        self.results_GroupBox: QtWidgets.QGroupBox or None = None
        self.results_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_TabWidget: QtWidgets.QTabWidget or None = None

        # Results / GeoLayers
        self.rightClickMenu_Results_GeoLayers: QtWidgets.QMenu or None = None
        self.results_GeoLayers_Tab: QtWidgets.QWidget or None = None
        self.results_GeoLayers_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_GeoLayers_GroupBox: QtWidgets.QGroupBox or None = None
        self.results_GeoLayers_GroupBox_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_GeoLayers_Table: QtWidgets.QTableWidget or None = None

        # Results / GeoMaps
        self.results_GeoMaps_Tab: QtWidgets.QWidget or None = None
        self.results_GeoMaps_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_GeoMaps_GroupBox: QtWidgets.QGroupBox or None = None
        self.results_GeoMaps_GroupBox_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_GeoMaps_Table: QtWidgets.QTableWidget or None = None

        # Results / GeoMapProjects
        self.results_GeoMapProjects_Tab: QtWidgets.QWidget or None = None
        self.results_GeoMapProjects_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_GeoMapProjects_GroupBox: QtWidgets.QGroupBox or None = None
        self.results_GeoMapProjects_GroupBox_VerticalLayout: QtWidgets.QVBoxLayout or None = None
        self.results_GeoMapProjects_Table: QtWidgets.QTableWidget or None = None

        # Results / Output Files
        self.rightClickMenu_Results_OutputFiles: QtWidgets.QMenu or None = None
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
        self.rightClickMenu_Results_Tables: QtWidgets.QMenu or None = None

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

        # View menu
        self.Menu_View: QtWidgets.QMenu or None = None
        self.Menu_View_CommandFileDiff: QtWidgets.QAction or None = None

        # Commands menu
        self.Menu_Commands: QtWidgets.QMenu or None = None
        # Commands / Select, Free GeoLayer menu
        self.Menu_Commands_Select_Free_GeoLayers: QtWidgets.QMenu or None = None
        self.Menu_Commands_Select_Free_FreeGeoLayers: QtWidgets.QAction or None = None

        # Commands / Create GeoLayer menu
        self.Menu_Commands_Create_GeoLayer: QtWidgets.QMenu or None = None
        self.Menu_Commands_Create_CopyGeoLayer: QtWidgets.QAction or None = None
        self.Menu_Commands_Create_CreateGeoLayerFromGeometry: QtWidgets.QAction or None = None

        # Commands / Read GeoLayer
        self.Menu_Commands_Read_GeoLayer: QtWidgets.QMenu or None = None
        self.Menu_Commands_Read_ReadGeoLayerFromDelimitedFile: QtWidgets.QAction or None = None
        self.Menu_Commands_Read_ReadGeoLayerFromGeoJSON: QtWidgets.QAction or None = None
        self.Menu_Commands_Read_ReadGeoLayerFromKML: QtWidgets.QAction or None = None
        self.Menu_Commands_Read_ReadGeoLayerFromShapefile: QtWidgets.QAction or None = None
        self.Menu_Commands_Read_ReadGeoLayerFromWebFeatureService: QtWidgets.QAction or None = None
        self.Menu_Commands_Read_ReadGeoLayersFromFolder: QtWidgets.QAction or None = None
        self.Menu_Commands_Read_ReadGeoLayersFromFGDB: QtWidgets.QAction or None = None
        self.Menu_Commands_Read_ReadGeoLayersFromGeoPackage: QtWidgets.QAction or None = None
        self.Menu_Commands_Read_ReadGeoLayerFromTileMapService: QtWidgets.QAction or None = None
        self.Menu_Commands_Read_ReadGeoLayerFromWebMapService: QtWidgets.QAction or None = None

        # Commands / Fill GeoLayer
        self.Menu_Commands_FillGeoLayerMissingData: QtWidgets.QMenu or None = None

        # Commands / Set GeoLayer
        self.Menu_Commands_SetGeoLayer_Contents: QtWidgets.QMenu or None = None
        self.Menu_Commands_SetContents_AddGeoLayerAttribute: QtWidgets.QAction or None = None
        self.Menu_Commands_SetContents_SetGeoLayerAttribute: QtWidgets.QAction or None = None
        self.Menu_Commands_SetContents_RemoveGeoLayerAttributes: QtWidgets.QAction or None = None
        self.Menu_Commands_SetContents_RenameGeoLayerAttribute: QtWidgets.QAction or None = None
        self.Menu_Commands_SetContents_SetGeoLayerCRS: QtWidgets.QAction or None = None
        self.Menu_Commands_SetContents_SetGeoLayerProperty: QtWidgets.QAction or None = None

        # Commands / Manipulate GeoLayer
        self.Menu_Commands_Manipulate_GeoLayer: QtWidgets.QMenu or None = None
        self.Menu_Commands_Manipulate_ChangeGeoLayerGeometry: QtWidgets.QAction or None = None
        self.Menu_Commands_Manipulate_ClipGeoLayer: QtWidgets.QAction or None = None
        self.Menu_Commands_Manipulate_IntersectGeoLayer: QtWidgets.QAction or None = None
        self.Menu_Commands_Manipulate_MergeGeoLayers: QtWidgets.QAction or None = None
        self.Menu_Commands_Manipulate_RemoveGeoLayerFeatures: QtWidgets.QAction or None = None
        self.Menu_Commands_Manipulate_SimplifyGeoLayerGeometry: QtWidgets.QAction or None = None
        self.Menu_Commands_Manipulate_SplitGeoLayerByAttribute: QtWidgets.QAction or None = None

        # Commands / Analyze GeoLayer
        self.Menu_Commands_Analyze_GeoLayer: QtWidgets.QMenu or None = None

        # Commands / Check GeoLayer
        self.Menu_Commands_Check_GeoLayer: QtWidgets.QMenu or None = None

        # Commands / Write GeoLayer
        self.Menu_Commands_Write_GeoLayer: QtWidgets.QMenu or None = None
        self.Menu_Commands_Write_WriteGeoLayerToDelimitedFile: QtWidgets.QAction or None = None
        self.Menu_Commands_Write_WriteGeoLayerToGeoJSON: QtWidgets.QAction or None = None
        self.Menu_Commands_Write_WriteGeoLayerToKML: QtWidgets.QAction or None = None
        self.Menu_Commands_Write_WriteGeoLayerToShapefile: QtWidgets.QAction or None = None

        # Commands / Datastore Processing
        self.Menu_Commands_DatastoreProcessing: QtWidgets.QMenu or None = None
        self.Menu_Commands_DatastoreProcessing_OpenDataStore: QtWidgets.QAction or None = None
        self.Menu_Commands_DatastoreProcessing_ReadTableFromDataStore: QtWidgets.QAction or None = None

        # Commands / Map Processing
        self.Menu_Commands_MapProcessing: QtWidgets.QMenu or None = None
        self.Menu_Commands_MapProcessing_CreateGeoMap: QtWidgets.QAction or None = None
        self.Menu_Commands_MapProcessing_AddGeoLayerViewGroupToGeoMap: QtWidgets.QAction or None = None
        self.Menu_Commands_MapProcessing_AddGeoLayerViewToGeoMap: QtWidgets.QAction or None = None
        self.Menu_Commands_MapProcessing_SetGeoLayerViewCategorizedSymbol: QtWidgets.QAction or None = None
        self.Menu_Commands_MapProcessing_SetGeoLayerViewGraduatedSymbol: QtWidgets.QAction or None = None
        self.Menu_Commands_MapProcessing_SetGeoLayerViewSingleSymbol: QtWidgets.QAction or None = None
        self.Menu_Commands_MapProcessing_SetGeoLayerViewEventHandler: QtWidgets.QAction or None = None
        self.Menu_Commands_MapProcessing_CreateGeoMapProject: QtWidgets.QAction or None = None
        self.Menu_Commands_MapProcessing_AddGeoMapToGeoMapProject: QtWidgets.QAction or None = None
        self.Menu_Commands_MapProcessing_WriteGeoMapProjectToJSON: QtWidgets.QAction or None = None

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
        self.Menu_Commands_General_FileHandling_FTPGet: QtWidgets.QAction or None = None
        self.Menu_Commands_General_FileHandling_WebGet: QtWidgets.QAction or None = None
        self.Menu_Commands_General_FileHandling_CreateFolder: QtWidgets.QAction or None = None
        self.Menu_Commands_General_FileHandling_CopyFile: QtWidgets.QAction or None = None
        self.Menu_Commands_General_FileHandling_ListFiles: QtWidgets.QAction or None = None
        self.Menu_Commands_General_FileHandling_RemoveFile: QtWidgets.QAction or None = None
        self.Menu_Commands_General_FileHandling_UnzipFile: QtWidgets.QAction or None = None

        # Commands / General - Logging and Messaging
        self.Menu_Commands_General_LoggingMessaging: QtWidgets.QMenu or None = None
        self.Menu_Commands_General_LoggingMessaging_StartLog: QtWidgets.QAction or None = None
        self.Menu_Commands_General_LoggingMessaging_Message: QtWidgets.QAction or None = None

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
        self.Menu_Commands_General_RunningProperties_Exit: QtWidgets.QAction or None = None
        self.Menu_Commands_General_RunningProperties_QgisAlgorithmHelp: QtWidgets.QAction or None = None

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
        self.Menu_Commands_Raster_Create_RasterGeoLayer: QtWidgets.QMenu or None = None
        self.Menu_Commands_Raster_Create_CreateRasterGeoLayer: QtWidgets.QAction or None = None
        self.Menu_Commands_Raster_Create_RasterizeGeoLayer: QtWidgets.QAction or None = None

        # Commands(Raster) / Read GeoLayer
        self.Menu_Commands_Raster_Read_RasterGeoLayer: QtWidgets.QMenu or None = None
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromFile: QtWidgets.QAction or None = None
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromTileService: QtWidgets.QAction or None = None
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromWebMapService: QtWidgets.QAction or None = None

        # Commands(Raster) / Write GeoLayer
        self.Menu_Commands_Raster_Write_RasterGeoLayer: QtWidgets.QMenu or None = None
        self.Menu_Commands_Raster_Write_WriteRasterGeoLayerFromFile: QtWidgets.QAction or None = None

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
        # The backup list should be recreated every time a command file is read or written.
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

        # Tell the processor that the UI will listing to command processor progress,
        # including when commands are started, finish, etc., so the UI can update its state.
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
        command_list_modified = self.command_list_backup.command_list_modified(self.gp.commands)

        # If modified, open dialog box to ask if user wants to save file
        if command_list_modified:
            save_command_dialog =\
                QtWidgets.QMessageBox.question(self, 'GeoProcessor',
                                               'Do you want to save the changes you made?\n\n' +
                                               'To view differences, Cancel and use View / Command File Diff.',
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
        This function is called from GeoProcessor.notify_command_processor_listeners_of_command_completed().
        See also 'command_exception', which has similar logic,
        especially to handle case when the last command run has an exception.

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

        debug = True
        logger = logging.getLogger(__name__)
        if command is None:
            # Not really needed but prevents a warning
            return

        # Get the class name
        command_class = command.__class__.__name__

        # Update the progress to indicate progress (0 to number of commands... completed).
        # - icommand starts at 0 so need to update add 2, one for zero value and 1 for zero offset index
        self.status_CommandWorkflow_StatusBar.setValue(icommand + 2)
        self.status_CurrentCommand_StatusBar.setValue(100)

        # Set the tooltip text for the progress bar to indicate the numbers
        hint = ("Completed command " + str(icommand + 1) + " of " + str(ncommand))
        self.status_CommandWorkflow_StatusBar.setToolTip(hint)

        # Last command has complete or Exit() command.
        detected_end = False
        if (icommand + 1) == ncommand:
            # Last command has completed (or Exit() command) so refresh the command status.
            logger.info("Detected (from listener) completed running the last command ({})...updating UI status.".format(
                (icommand + 1)))
            detected_end = True
        elif command_class == "Exit":
            # Last command has completed (or Exit() command) so refresh the command status.
            logger.info("Detected (from listener) running Exit command...updating UI status.")
            detected_end = True
        else:
            if debug:
                logger.debug("Completed command {}.".format((icommand + 1)))

        if detected_end:
            # Last command being run has completed.
            self.status_Label.setText("Ready")
            self.status_Label_Hint.setText("Completed running commands. Use Results and Tools menus.")
            # The following updates the command status and displays warning/fail icons
            self.command_CommandListWidget.update_ui_command_list_errors()
            # TODO smalers 2020-03-13 old logic
            # self.update_ui_commands_list()
            # Cause the labels to be updated
            self.command_CommandListWidget.update_ui_status_commands()

    def command_exception(self, icommand: int, ncommand: int, command: AbstractCommand,
                          percent_completed: float, message: str) -> None:
        """
        Indicate that a command had an exception.
        This function is called from GeoProcessor.notify_command_processor_listeners_of_command_exception().
        See also 'command_completed', which has similar logic for normal (non-exception) case.

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

        debug = True
        logger = logging.getLogger(__name__)
        if command is None:
            # Not really needed but prevents a warning
            return

        # Get the class name
        command_class = command.__class__.__name__

        # Update the progress to indicate progress (0 to number of commands... completed).
        # - icommand starts at 0 so need to update add 2, one for zero value and 1 for zero offset index
        self.status_CommandWorkflow_StatusBar.setValue(icommand + 2)
        self.status_CurrentCommand_StatusBar.setValue(100)

        # Set the tooltip text for the progress bar to indicate the numbers
        hint = ("Exception for command " + str(icommand + 1) + " of " + str(ncommand))
        self.status_CommandWorkflow_StatusBar.setToolTip(hint)

        # Last command has complete or Exit() command.
        detected_end = False
        if (icommand + 1) == ncommand:
            # Last command has completed (or Exit() command) so refresh the command status.
            logger.info("Detected (from listener) exception running the last command ({})...updating UI status.".format(
                (icommand + 1)))
            detected_end = True
        elif command_class == "Exit":
            # Last command has completed (or Exit() command) so refresh the command status.
            # - should not get an exception but put in code for consistency with 'command_completed'
            logger.info("Detected (from listener) exception running Exit command...updating UI status.")
            detected_end = True
        else:
            if debug:
                logger.debug("Exception for command {}.".format((icommand + 1)))

        if detected_end:
            # Last command being run has completed.
            self.status_Label.setText("Ready")
            self.status_Label_Hint.setText("Completed running commands. Use Results and Tools menus.")
            # The following updates the command status and displays warning/fail icons
            self.command_CommandListWidget.update_ui_command_list_errors()
            # TODO smalers 2020-03-13 old logic
            # self.update_ui_commands_list()
            # Cause the labels to be updated
            self.command_CommandListWidget.update_ui_status_commands()

    def command_started(self, icommand: int, ncommand: int, command: AbstractCommand,
                        percent_completed: float, message: str) -> None:
        """
        Indicate that a command has started running.
        This function is called from GeoProcessor.notify_command_processor_listeners_of_command_started().

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
        size = 0
        if selected_indices is not None:
            size = len(selected_indices)
        if size == 0:
            return

        # Clear what may previously have been in the cut buffer...
        self.commands_cut_buffer.clear()

        # Transfer Command instances to the cut buffer...
        command = None  # Command instance to process
        for i in range(size):
            command = self.gp_model.gp.commands[selected_indices[i]]
            # It is OK ot store the original commands in the cut buffer because their command strings will be used
            # to create new commands if necessary for copy.
            self.commands_cut_buffer.append(command)

    def cut_commands_to_clipboard(self) -> None:
        """
        Cut commands in the command list (to be used with paste) and also remove the commands.

        Returns:
            None
        """
        # The top of this function is the same as cut_commands_to_clipboard().
        selected_indices = self.command_CommandListWidget.get_selected_indices()
        size = 0
        if selected_indices is not None:
            size = len(selected_indices)
        if size == 0:
            return

        # Clear what may previously have been in the cut buffer...
        self.commands_cut_buffer.clear()

        # Transfer Command instances to the cut buffer...
        command = None  # Command instance to process
        for i in range(size):
            command = self.gp_model.gp.commands[selected_indices[i]]
            # It is OK ot store the original commands in the cut buffer because their command strings will be used
            # to create new commands if necessary for paste.
            self.commands_cut_buffer.append(command)

        # Remove the selected commands - same as pressing the clear button
        # - commands will be removed from the list, with prompt if all commands are removed
        self.command_CommandListWidget.command_list_clear()

    def deselect_all_commands(self) -> None:
        """
        Connected to command list popup "Deselect All Commands" menu.
        Deselect all commands in the command list.

        Returns:
            None
        """
        self.command_CommandListWidget.command_list_deselect_all()

    def edit_existing_command(self) -> None:
        """
        Opens a dialog box to edit an existing command.
        The edit depends on what is selected, either the first selected:

        1. first selected command
        2. first consecutive sequence of #-comment commands.

        Returns:
            None
        """

        logger = logging.getLogger(__name__)

        # Get the list of selected indices.
        # -the following returns a list of PyQt5.QtCore.QModelIndex, an empty list if none are selected.

        selected_indices = self.command_CommandListWidget.get_selected_indices()
        num_selected = len(selected_indices)
        if num_selected == 0:
            # This should not happen because edit menus are enabled only when some commands are selected,
            # but add a check just to be sure and to deal with logic problems.
            qt_util.warning_message_box('No commands are selected - cannot edit - the code has a logic problem.')
            return

        # Ensure that if the first selected command is a comments that they are contiguous.
        # - ignore remaining selections that are not contiguous
        is_hash_comment_block = False
        comment_commands = []
        selected_indices_edited = []  # List of rows (0+) that are actually edited, may be less than all selections
        if self.gp.commands[selected_indices[0]].command_string.strip().startswith('#'):
            # Have a # comment
            is_hash_comment_block = True

            # Get the first contiguous selected block of comment commands
            # - remaining selected commands won't be edited
            comment_count = 0
            index_prev = -1
            for index in selected_indices:
                # Check whether still in contiguous block of selected commands
                if index_prev >= 0:
                    # Processing 2nd+ selected index
                    if (index - index_prev) > 1:
                        # No longer in contiguous block
                        break
                # Always set the previous index for the next iteration
                index_prev = index
                if self.gp.commands[index].command_string.strip().startswith('#'):
                    # Still processing contiguous comments.
                    comment_commands.append(self.gp.commands[index])
                    selected_indices_edited.append(index)
                else:
                    # Done processing contiguous comments.
                    break
            logger.debug("Editing " + str(len(comment_commands)) + " #-comments.")

        else:
            # Editing a one-line command.
            # - get the index of the first selected command
            command_object = self.gp.commands[selected_indices[0]]
            logger.debug("Editing a single command.")

        # Create a copy of the command to edit.
        # - this matches TSTool logic
        # - this allows the new command edit to be discarded if Cancel is pressed in the edit
        # - otherwise, there is danger that the editor will change underlying data prior to Cancel
        # - a "deep" copy is probably needed because lists of metadata, etc. are needed; however, deepcopy() fails,
        #   and not sure how well copy() does.  Therefore, create a new instance of the command using the command string

        create_unknown_command_if_not_recognized = True  # Similar to an original load from a command file
        command_factory = GeoProcessorCommandFactory()
        command_object_original = None
        if is_hash_comment_block:
            # Copy the first comment command object
            # - multiple lines are handled below by setting text in the editor
            command_object_original = comment_commands[0]
        else:
            # Copy the single command object
            command_object_original = command_object

        command_object_to_edit = command_factory.new_command(
            command_object_original.command_string,
            create_unknown_command_if_not_recognized)
        # logger.debug("New command for editing is type " + str(type(command_object)))
        # logger.debug("Description =" + command_object.command_metadata['Description'])

        # Initialize additional command object data.
        # - work is done in the AbstractCommand class
        # - the processor is set in the command
        # - full_initialization parses the command string
        full_initialization = True
        command_object_to_edit.initialize_command(command_object_original.command_string, self.gp_model.gp,
                                                  full_initialization)
        command_object_to_edit.initialize_geoprocessor_ui(self)

        # The following code is used for all commands, including # comments:
        # - create a command editor using the factory
        # noinspection PyBroadException
        try:
            # Create the editor for the command
            # - initialization occurs in the dialog
            command_editor_factory = GeoProcessorCommandEditorFactory()
            command_editor = command_editor_factory.new_command_editor(command_object_to_edit, self.app_session)
            if is_hash_comment_block:
                # Comment block editor is for 1+ comment lines separated by newline as formed above
                comment_block_text = ""
                for i in range(len(comment_commands)):
                    command = comment_commands[i]
                    if i > 0:
                        comment_block_text += "\n"
                    comment_block_text += command.command_string
                command_editor.set_text(comment_block_text)
        except Exception:
            message = "Error creating editor for existing command."
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
            return

        # Edit the command copy in the editor.
        # noinspection PyBroadException
        try:
            # If the "OK" button is clicked within the dialog window, continue.
            # Else, if the "Cancel" button is clicked, do nothing (original command list will remain).
            button_clicked = command_editor.exec_()
            if button_clicked == QtWidgets.QDialog.Accepted:
                # OK button was clicked in the editor and validation passed so OK to use the changes.

                # Get the command string from the dialog window.
                command_string = command_editor.CommandDisplay_View_TextBrowser.toPlainText()

                # Update command in GeoProcessor list of commands
                if is_hash_comment_block:
                    # The editor will result in 0+ newline-separated comments
                    # - let the command editor deal with formatting
                    # - the get_text() function is similar to TSTool Command_JDialog.getText().
                    command_string_list = command_editor.get_command_string_list()
                    # Update or insert into the GeoProcessor
                    # - the number of comments as per num_selected_are_comments may be different from the
                    #   number of comments returned from the editor

                    # First, remove the selected comments from before that were edited
                    # - remove at the same index for the number of original comments since contiguous
                    # - callbacks will update UI status
                    self.gp_model.clear_selected_commands(selected_indices_edited)
                    # Second, add the new comments starting at the same position as before.
                    # - use the data model to change the command list
                    comment_commands_new = []
                    for command_string in command_string_list:
                        # Create a new comment command using the factory.
                        comment_command_new = command_factory.new_command(
                            command_string,
                            create_unknown_command_if_not_recognized)
                        full_initialization = True
                        # Initialize the comment string
                        comment_command_new.initialize_command(command_string, self.gp_model.gp, full_initialization)
                        comment_command_new.initialize_geoprocessor_ui(self)
                        comment_commands_new.append(comment_command_new)
                    # Insert the commands in bulk into the model
                    self.gp_model.insert_commands_at_index(comment_commands_new, selected_indices_edited[0])
                else:
                    # Update the string in the original command
                    # - just reinitialize the command using the string from the edited command copy
                    full_initialization = True
                    command_object.initialize_command(command_object_to_edit.command_string, self.gp_model.gp,
                                                      full_initialization)
                    command_object.initialize_geoprocessor_ui(self)

                # Manually set the run all commands and clear commands buttons to enabled
                # - TODO smalers 2020-03-13 hopefully don't need this since status us checked below
                # self.command_CommandListWidget.commands_RunAllCommands_PushButton.setEnabled(True)
                # self.command_CommandListWidget.commands_ClearCommands_PushButton.setEnabled(True)

                # update the window title in case command file has been modified
                self.update_ui_status()
                self.update_ui_main_window_title()

            else:
                # Cancel was clicked so don't do anything
                pass

        except Exception:
            message = "Error editing existing command."
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
            return

    def edit_new_command(self, command_string: str) -> None:
        """
        Opens the dialog window for the selected command, editing a new command.
        This function is called when the user selects a Command menu item.
        If the users clicks "OK" within the dialog window, the command is added to the Command_List view
        within the Main Window user interface.
        Other UI components are also updated - including the total and selected command count, the
        Command_List Widget Label, and the GeoProcessor's list of commands.

        Args:
            command_string (str): the command string with empty parameters:  CommandName()
            If a #-comment, /*, or */, or empty line, then no () are used.

        Returns:
            None (results of the function are propagated to the command list)
        """
        logger = logging.getLogger(__name__)
        logger.debug("Editing new command string:  '" + command_string + "'")

        # Trim the command string string, just in case, but

        # Detect comment block, which is handled separately because it can edit more than one line
        is_hash_comment_block = False
        if command_string.strip().startswith("#"):
            is_hash_comment_block = True

        # Create a new command object for the command name using the command factory.
        # - the command object will be retained as is if a one-line command
        # - if a # comment block, the returned command object string will be split
        #   into 1+ comment commands and added separately for each line
        # noinspection PyBroadException
        try:
            command_factory = GeoProcessorCommandFactory()

            # Initialize the command object (without parameters).
            # - Work is done in the GeoProcessorCommandFactory class.
            # - Do not allow unrecognized commands because this function should only be called with valid commands.
            # - # comments at this point will only be one line (may be more than one line after editing).
            create_unknown_command_if_not_recognized = False
            command_object = command_factory.new_command(
                command_string,
                create_unknown_command_if_not_recognized)
            logger.debug("New command for editing is type " + str(type(command_object)))
            # logger.debug("Description =" + command_object.command_metadata['Description'])

            # Initialize additional command object data.
            # - work is done in the AbstractCommand class
            # - the processor is set in the command
            # - full_initialization parses the command string, which won't do much here since new and no parameters
            full_initialization = True
            command_object.initialize_command(command_string, self.gp_model.gp, full_initialization)
            command_object.initialize_geoprocessor_ui(self)
        except Exception:
            message = "Error creating new command, unable to edit command string: " + command_string
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
            return

        # If here, a new command instance was successfully created above.
        # - Currently don't allow UnknownCommand instance, but might allow in the future.
        # Use the command object to create a corresponding editor based on the command's
        # command_metadata[`EditorType`] value.

        # noinspection PyBroadException
        try:
            # Create the editor for the command
            # - initialization occurs in the dialog
            command_editor_factory = GeoProcessorCommandEditorFactory()
            command_editor = command_editor_factory.new_command_editor(command_object, self.app_session)
            logger.debug("New command editor for editing is type " + str(type(command_editor)) +
                         " for command type " + str(type(command_editor.command)))
            # logger.debug("Description =" + command_object.command_metadata['Description'])
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

            if button_clicked == QtWidgets.QDialog.Accepted:
                # The editor will have edited the command string.
                # - in most cases the string will not contain newlines
                # - if a #-block of comments, multiple # lines will be separated by newline
                if is_hash_comment_block:
                    logger.debug("Command string after editing (may include line breaks):  '" +
                                 str(command_object.command_string) + "'")
                else:
                    logger.debug("Command string after editing:  '" + str(command_object.command_string) + "'")

                comment_commands = []
                if is_hash_comment_block:
                    # If working with a comment block with potential multiple lines,
                    # must add those lines individually to the GeoProcessor.
                    # The lines that are returned may or may not have # in front - if not, add.
                    # Also allow spaces in front of the comments - preserve the spaces when adding the comments.
                    comment_lines = command_object.command_string.splitlines()
                    logger.debug("# comment block has " + str(len(comment_lines)) + " lines.")
                    for i in range(len(comment_lines)):
                        # Make sure that the lines start with the comment character
                        if not comment_lines[i].strip().startswith("#"):
                            # Need to add # in front of command, but need to check for leading spaces
                            if not comment_lines[i].startswith("") and not comment_lines[i].startswith("\t"):
                                # String does not start with space or tab so add "# " at the start
                                comment_lines[i] = "# " + comment_lines[i]
                            else:
                                # More than one space or tab so get the leading string
                                # - then insert the "# " in the middle of the string
                                white = string_util.get_leading_whitespace(comment_lines[i])
                                comment_lines[i] = white + "# " + comment_lines[i][len(white):]
                        logger.debug("New comment line [" + str(i) + "] after confirming #: '" + comment_lines[i] + "'")
                        # Create a new comment line command using the factory.
                        command_object = command_factory.new_command(
                            comment_lines[i],
                            create_unknown_command_if_not_recognized)
                        # The above just creates an instance of the command but does not initialize it
                        full_initialization = True
                        command_object.initialize_command(comment_lines[i], self.gp_model.gp, full_initialization)
                        logger.debug("New comment line after creating command: '" + command_object.command_string + "'")
                        # Add the comment command to the temporary list
                        comment_commands.append(command_object)

                # Add the command to the GeoProcessor commands.
                # If there are already commands in the command list, see if any are selected.
                insert_row = -1  # used to update the UI command list data model
                if len(self.gp.commands) == 0:
                    # Will insert at first row
                    insert_row = 0
                else:
                    # Default insert row is at end (next index after the last row = length)
                    # - end row is calculated below depending on whether one or more rows are inserted.
                    insert_row = len(self.gp_model)

                # Check whether any commands are selected and if so reset the insert row.
                selected_indices = self.command_CommandListWidget.command_ListView.selectedIndexes()
                if (selected_indices is not None) and (len(selected_indices) > 0):
                    # Have selected commands
                    # - selected_indices are QModelIndex so get the integer row
                    # - reset the insert row to the first selected
                    insert_row = selected_indices[0].row()

                # Now actually insert the commands into rows of the data model.
                if is_hash_comment_block:
                    # Add all the comment commands starting at the indicated index.
                    self.gp_model.insert_commands_at_index(comment_commands, insert_row)
                else:
                    # Insert the single row in the data model
                    self.gp_model.insert_command_at_index(command_object, insert_row)

                # If rows were selected prior to the insert, select the same rows again by shifting by the
                # number of commands that were inserted
                # TODO smalers 2020-03-13 This needs to be implemented
                new_selected_indices = [len(selected_indices)]  # array of integer rows (not QModelIndex)
                if (selected_indices is not None) and (len(selected_indices) > 0):
                    if is_hash_comment_block:
                        pass
                    else:
                        # Inserted a single row
                        for i in range(len(selected_indices)):
                            if selected_indices[i].row() >= insert_row:
                                # Shift by one row
                                new_selected_indices[i] = selected_indices[i].row() + 1
                    # Reselect the rows
                    self.command_CommandListWidget.command_list_select_rows(new_selected_indices)

                # The item has been added to the GeoProcessor command list but the Widget needs to be informed.
                # Synchronize the other lists with the main command list.
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
            message = "Error editing new command."
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

    def open_dialog(self, existing_dialog: QtWidgets.QDialog = None, id: str = None) -> QtWidgets.QDialog:
        """
        Open a new dialog.
        This is used to ensure that data-viewing dialogs are set in global scope so that they don't automatically
        close when the UI function returns.

        Args:
            existing_dialog (QtWidgets.QDialog): dialog that was already created - just add to the global list
            id (str): dialog identifier

        Returns:
            The new dialog instance.
        """
        if existing_dialog is None:
            # Create a new dialog
            dialog = QtWidgets.QDialog()
        else:
            dialog = existing_dialog
        if id is None:
            # Default identifier is "dialogN" where N is the count of dialogs
            id = "dialog{}".format((len(self.dialogs) + 1))
        self.dialogs[id] = dialog
        return dialog

    def paste_commands_from_clipboard(self) -> None:
        """
        Paste commands in the command list (used with copy and cut).
        Commands in the self.commands_cut_buffer list are inserted after the last selected command (or at end).
        The logic is similar to inserting new commands except there is no edit involved.

        Returns:
            None
        """
        if len(self.commands_cut_buffer) == 0:
            # No commands in the buffer so nothing to do - should not have been called but check anyway
            return

        logger = logging.getLogger(__name__)

        # noinspection PyBroadException
        try:
            # Loop through the commands in the buffer and create new commands based on the command strings.
            new_commands = []
            command_factory = GeoProcessorCommandFactory()
            for command in self.commands_cut_buffer:
                # Initialize the command object (without parameters).
                # - Work is done in the GeoProcessorCommandFactory class.
                # - Do not allow unrecognized commands because this function should only be called with valid commands.
                # - # comments at this point will only be one line (may be more than one line after editing).
                create_unknown_command_if_not_recognized = False
                command_object = command_factory.new_command(
                    command.command_string,
                    create_unknown_command_if_not_recognized)
                # logger.debug("New command for paste " + str(type(command_object)))
                new_commands.append(command_object)
                # logger.debug("Description =" + command_object.command_metadata['Description'])

                # Initialize additional command object data.
                # - work is done in the AbstractCommand class
                # - the processor is set in the command
                # - full_initialization parses the command string, which won't do much here since new and no parameters
                full_initialization = True
                command_object.initialize_command(command.command_string, self.gp_model.gp, full_initialization)

            # Check whether any commands are selected and if so reset the insert row.
            selected_indices = self.command_CommandListWidget.command_ListView.selectedIndexes()
            if (selected_indices is not None) and (len(selected_indices) > 0):
                # Have selected commands
                # - selected_indices are QModelIndex so get the integer row
                # - reset the insert row to the row after the last selected row
                insert_row = selected_indices[len(selected_indices) - 1].row() + 1
            else:
                # Insert after all commands
                insert_row = len(self.gp_model)

            self.gp_model.insert_commands_at_index(new_commands, insert_row)

            # The item has been added to the GeoProcessor command list but the Widget needs to be informed.
            # Synchronize the other lists with the main command list.
            self.command_CommandListWidget.number_list_sync_with_commands()
            self.command_CommandListWidget.gutter_list_sync_with_commands()
            self.command_CommandListWidget.update_ui_status_commands()
        except Exception:
            # Unexpected error.
            message = "Error pasting command(s)."
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

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

        # The widget is a complex object that is comprised of several components.
        # Command-related events from the widget are passed back to this class to be handled.
        self.command_CommandListWidget = CommandListWidget(self.commands_GroupBox)

        # Model to map GeoProcessor commands to the CommandListWidget
        # self.gp_model = GeoProcessorListModel(self.gp, self.command_CommandListWidget)
        self.gp_model = GeoProcessorListModel(self.gp)
        # self.command_CommandListWidget.command_ListWidget.set_gp_model(self.gp_model)
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
        # Use the following because connect() is shown as unresolved reference in PyCharm
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
        self.Menu_File_Save_Commands.setText("Commands")
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
        self.Menu_Edit_Format.setObjectName(qt_util.from_utf8("Menu_Edit_Format"))
        self.Menu_Edit_Format.setText("Format")
        self.Menu_Edit.addAction(self.Menu_Edit_Format)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Edit_Format.triggered.connect(self.ui_action_edit_format)

        self.menubar.addAction(self.Menu_Edit.menuAction())

        # ============================================================================================================
        # View menu
        # ============================================================================================================

        self.Menu_View = QtWidgets.QMenu(self.menubar)
        self.Menu_View.setObjectName(qt_util.from_utf8("Menu_View"))
        self.Menu_View.setTitle("View")

        # View / Command File Diff
        self.Menu_View_CommandFileDiff = QtWidgets.QAction(main_window)
        self.Menu_View_CommandFileDiff.setObjectName(qt_util.from_utf8("Menu_View_CommandFileDiff"))
        self.Menu_View_CommandFileDiff.setText("Command File Diff")
        self.Menu_View.addAction(self.Menu_View_CommandFileDiff)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_View_CommandFileDiff.triggered.connect(self.ui_action_view_command_file_diff)

        self.menubar.addAction(self.Menu_View.menuAction())

        # ============================================================================================================
        # Commands menu
        # ============================================================================================================

        self.Menu_Commands = QtWidgets.QMenu(self.menubar)
        self.Menu_Commands.setObjectName(qt_util.from_utf8("Menu_Commands"))
        self.Menu_Commands.setTitle("Commands")

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Select, Free - GeoLayers menu
        # ------------------------------------------------------------------------------------------------------------
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
            functools.partial(self.edit_new_command, "FreeGeoLayers()"))
        self.Menu_Commands_Select_Free_GeoLayers.addAction(self.Menu_Commands_Select_Free_FreeGeoLayers)

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Create - GeoLayers menu
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_Create_GeoLayer = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Create_GeoLayer.setObjectName(qt_util.from_utf8("Menu_Commands_Create_GeoLayer"))
        self.Menu_Commands_Create_GeoLayer.setTitle("Create GeoLayer")
        self.Menu_Commands.addAction(self.Menu_Commands_Create_GeoLayer.menuAction())

        # CopyGeoLayer
        self.Menu_Commands_Create_CopyGeoLayer = QtWidgets.QAction(main_window)
        self.Menu_Commands_Create_CopyGeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_Create_CopyGeoLayer"))
        self.Menu_Commands_Create_CopyGeoLayer.setText(
            "CopyGeoLayer()... <copy a GeoLayer to a new GeoLayer>")
        self.Menu_Commands_Create_GeoLayer.addAction(self.Menu_Commands_Create_CopyGeoLayer)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Create_CopyGeoLayer.triggered.connect(
            functools.partial(self.edit_new_command, "CopyGeoLayer()"))

        # CreateGeoLayerFromGeometry
        self.Menu_Commands_Create_CreateGeoLayerFromGeometry = QtWidgets.QAction(main_window)
        self.Menu_Commands_Create_CreateGeoLayerFromGeometry.setObjectName(
            qt_util.from_utf8("Menu_Commands_Create_CreateGeoLayerFromGeomtery"))
        self.Menu_Commands_Create_CreateGeoLayerFromGeometry.setText(
            "CreateGeoLayerFromGeometry()... <create a GeoLayer from input geometry data>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Create_CreateGeoLayerFromGeometry.triggered.connect(
            functools.partial(self.edit_new_command, "CreateGeoLayerFromGeometry()"))
        self.Menu_Commands_Create_GeoLayer.addAction(self.Menu_Commands_Create_CreateGeoLayerFromGeometry)

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Read - GeoLayers menu
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_Read_GeoLayer = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Read_GeoLayer.setObjectName(qt_util.from_utf8("Menu_Commands_Read_GeoLayer"))
        self.Menu_Commands_Read_GeoLayer.setTitle("Read GeoLayer")
        self.Menu_Commands.addAction(self.Menu_Commands_Read_GeoLayer.menuAction())

        # ReadGeoLayerFromDelimitedFile
        self.Menu_Commands_Read_ReadGeoLayerFromDelimitedFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_Read_ReadGeoLayerFromDelimitedFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_GeoLayer_Read_ReadGeoLayerFromDelimitedFile"))
        self.Menu_Commands_Read_ReadGeoLayerFromDelimitedFile.setText(
            "ReadGeoLayerFromDelimitedFile()... <read a GeoLayer from a file in delimited file format>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Read_ReadGeoLayerFromDelimitedFile.triggered.connect(
            functools.partial(self.edit_new_command, "ReadGeoLayerFromDelimitedFile()"))
        self.Menu_Commands_Read_GeoLayer.addAction(self.Menu_Commands_Read_ReadGeoLayerFromDelimitedFile)

        # ReadGeoLayerFromGeoJSON
        self.Menu_Commands_Read_ReadGeoLayerFromGeoJSON = QtWidgets.QAction(main_window)
        self.Menu_Commands_Read_ReadGeoLayerFromGeoJSON.setObjectName(
            qt_util.from_utf8("Menu_Commands_GeoLayers_Read_ReadGeoLayerFromGeoJSON"))
        self.Menu_Commands_Read_ReadGeoLayerFromGeoJSON.setText(
            "ReadGeoLayerFromGeoJSON()... <reads a GeoLayer from a GeoJSON file or URL>")
        self.Menu_Commands_Read_GeoLayer.addAction(self.Menu_Commands_Read_ReadGeoLayerFromGeoJSON)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Read_ReadGeoLayerFromGeoJSON.triggered.connect(
            functools.partial(self.edit_new_command, "ReadGeoLayerFromGeoJSON()"))

        # ReadGeoLayerFromKML
        self.Menu_Commands_Read_ReadGeoLayerFromKML = QtWidgets.QAction(main_window)
        self.Menu_Commands_Read_ReadGeoLayerFromKML.setObjectName(
            qt_util.from_utf8("Menu_Commands_GeoLayers_Read_ReadGeoLayerFromKML"))
        self.Menu_Commands_Read_ReadGeoLayerFromKML.setText(
            "ReadGeoLayerFromKML()... <reads a GeoLayer from a KML file or URL>")
        self.Menu_Commands_Read_GeoLayer.addAction(self.Menu_Commands_Read_ReadGeoLayerFromKML)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Read_ReadGeoLayerFromKML.triggered.connect(
            functools.partial(self.edit_new_command, "ReadGeoLayerFromKML()"))

        # ReadGeoLayerFromShapefile
        self.Menu_Commands_Read_ReadGeoLayerFromShapefile = QtWidgets.QAction(main_window)
        self.Menu_Commands_Read_ReadGeoLayerFromShapefile.setObjectName(
            qt_util.from_utf8("GeoLayers_Read_ReadGeoLayerFromShapefile"))
        self.Menu_Commands_Read_ReadGeoLayerFromShapefile.setText(
            "ReadGeoLayerFromShapefile()... <reads a GeoLayer from a shapefile>")
        self.Menu_Commands_Read_GeoLayer.addAction(self.Menu_Commands_Read_ReadGeoLayerFromShapefile)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Read_ReadGeoLayerFromShapefile.triggered.connect(
            functools.partial(self.edit_new_command, "ReadGeoLayerFromShapefile()"))

        # ReadGeoLayerFromWebFeatureService
        self.Menu_Commands_Read_ReadGeoLayerFromWebFeatureService = QtWidgets.QAction(main_window)
        self.Menu_Commands_Read_ReadGeoLayerFromWebFeatureService.setObjectName(
            qt_util.from_utf8("Menu_Commands_GeoLayer_Read_ReadGeoLayerFromWebFeatureService"))
        self.Menu_Commands_Read_ReadGeoLayerFromWebFeatureService.setText(
            "ReadGeoLayerFromWebFeatureService()... <read a GeoLayer from a Web Feature Service>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Read_ReadGeoLayerFromWebFeatureService.triggered.connect(
            functools.partial(self.edit_new_command, "ReadGeoLayerFromWebFeatureService()"))
        self.Menu_Commands_Read_GeoLayer.addAction(self.Menu_Commands_Read_ReadGeoLayerFromWebFeatureService)

        self.Menu_Commands_Read_GeoLayer.addSeparator()

        # ReadGeoLayersFromFGDB
        self.Menu_Commands_Read_ReadGeoLayersFromFGDB = QtWidgets.QAction(main_window)
        self.Menu_Commands_Read_ReadGeoLayersFromFGDB.setObjectName(
            qt_util.from_utf8("GeoLayers_Read_ReadGeoLayersFromFGDB"))
        self.Menu_Commands_Read_ReadGeoLayersFromFGDB.setText(
            "ReadGeoLayersFromFGDB()... <reads 1+ GeoLayer(s) from the feature classes of a file geodatabase>")
        self.Menu_Commands_Read_GeoLayer.addAction(self.Menu_Commands_Read_ReadGeoLayersFromFGDB)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Read_ReadGeoLayersFromFGDB.triggered.connect(
            functools.partial(self.edit_new_command, "ReadGeoLayersFromFGDB()"))

        # ReadGeoLayersFromFolder
        self.Menu_Commands_Read_ReadGeoLayersFromFolder = QtWidgets.QAction(main_window)
        self.Menu_Commands_Read_ReadGeoLayersFromFolder.setObjectName(
            qt_util.from_utf8("GeoLayers_Read_ReadGeoLayersFromFolder"))
        self.Menu_Commands_Read_ReadGeoLayersFromFolder.setText(
            "ReadGeoLayersFromFolder()... <reads 1+ GeoLayer(s) from a local folder>")
        self.Menu_Commands_Read_GeoLayer.addAction(self.Menu_Commands_Read_ReadGeoLayersFromFolder)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Read_ReadGeoLayersFromFolder.triggered.connect(
            functools.partial(self.edit_new_command, "ReadGeoLayersFromFolder()"))

        # ReadGeoLayersFromGeoPackage
        self.Menu_Commands_Read_ReadGeoLayersFromGeoPackage = QtWidgets.QAction(main_window)
        self.Menu_Commands_Read_ReadGeoLayersFromGeoPackage.setObjectName(
            qt_util.from_utf8("GeoLayers_Read_ReadGeoLayersFromGeoPackage"))
        self.Menu_Commands_Read_ReadGeoLayersFromGeoPackage.setText(
            "ReadGeoLayersFromGeoPackage()... <reads 1+ GeoLayer(s) from a GeoPackage file>")
        self.Menu_Commands_Read_GeoLayer.addAction(self.Menu_Commands_Read_ReadGeoLayersFromGeoPackage)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Read_ReadGeoLayersFromGeoPackage.triggered.connect(
            functools.partial(self.edit_new_command, "ReadGeoLayersFromGeoPackage()"))

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Fill GeoLayer Missing Data menu (disabled)
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_FillGeoLayerMissingData = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_FillGeoLayerMissingData.setObjectName(
            qt_util.from_utf8("Menu_Commands_FillGeoLayerMissingData"))
        self.Menu_Commands_FillGeoLayerMissingData.setTitle("Fill GeoLayer Missing Data")
        self.Menu_Commands_FillGeoLayerMissingData.setEnabled(False)
        self.Menu_Commands.addAction(self.Menu_Commands_FillGeoLayerMissingData.menuAction())

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Set Contents - GeoLayers menu
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_SetGeoLayer_Contents = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_SetGeoLayer_Contents.setObjectName(
            qt_util.from_utf8("Menu_Commands_SetContents_GeoLayer"))
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
            functools.partial(self.edit_new_command, "AddGeoLayerAttribute()"))
        self.Menu_Commands_SetGeoLayer_Contents.addAction(self.Menu_Commands_SetContents_AddGeoLayerAttribute)

        # SetGeoLayerAttribute
        self.Menu_Commands_SetContents_SetGeoLayerAttribute = QtWidgets.QAction(main_window)
        self.Menu_Commands_SetContents_SetGeoLayerAttribute.setObjectName(
            qt_util.from_utf8("Menu_Commands_SetContents_SetGeoLayerAttribute"))
        self.Menu_Commands_SetContents_SetGeoLayerAttribute.setText(
            "SetGeoLayerAttribute()... <set an attribute for a GeoLayer>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_SetContents_SetGeoLayerAttribute.triggered.connect(
            functools.partial(self.edit_new_command, "SetGeoLayerAttribute()"))
        self.Menu_Commands_SetGeoLayer_Contents.addAction(self.Menu_Commands_SetContents_SetGeoLayerAttribute)

        # RemoveGeoLayerAttributes
        self.Menu_Commands_SetContents_RemoveGeoLayerAttributes = QtWidgets.QAction(main_window)
        self.Menu_Commands_SetContents_RemoveGeoLayerAttributes.setObjectName(
            qt_util.from_utf8("Menu_Commnads_SetContents_RemoveGeoLayerAttributes"))
        self.Menu_Commands_SetContents_RemoveGeoLayerAttributes.setText(
            "RemoveGeoLayerAttributes()... <remove one or more attributes from GeoLayer>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_SetContents_RemoveGeoLayerAttributes.triggered.connect(
            functools.partial(self.edit_new_command, "RemoveGeoLayerAttributes()"))
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
            functools.partial(self.edit_new_command, "RenameGeoLayerAttribute()"))
        self.Menu_Commands_SetGeoLayer_Contents.addAction(self.Menu_Commands_SetContents_RenameGeoLayerAttribute)

        self.Menu_Commands_SetGeoLayer_Contents.addSeparator()

        # SetGeoLayerCRS
        self.Menu_Commands_SetContents_SetGeoLayerCRS = QtWidgets.QAction(main_window)
        self.Menu_Commands_SetContents_SetGeoLayerCRS.setObjectName(
            qt_util.from_utf8("Menu_Commands_SetContents_SetGeoLayerCRS"))
        self.Menu_Commands_SetContents_SetGeoLayerCRS.setText(
            "SetGeoLayerCRS()... <sets a GeoLayer's coordinate reference system>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_SetContents_SetGeoLayerCRS.triggered.connect(
            functools.partial(self.edit_new_command, "SetGeoLayerCRS()"))
        self.Menu_Commands_SetGeoLayer_Contents.addAction(self.Menu_Commands_SetContents_SetGeoLayerCRS)

        self.Menu_Commands_SetGeoLayer_Contents.addSeparator()

        # SetGeoLayerProperty
        self.Menu_Commands_SetContents_SetGeoLayerProperty = QtWidgets.QAction(main_window)
        self.Menu_Commands_SetContents_SetGeoLayerProperty.setObjectName(
            qt_util.from_utf8("Menu_Commands_SetContents_SetGeoLayerProperty"))
        self.Menu_Commands_SetContents_SetGeoLayerProperty.setText(
            "SetGeoLayerProperty()... <set a GeoLayer property>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_SetContents_SetGeoLayerProperty.triggered.connect(
            functools.partial(self.edit_new_command, "SetGeoLayerProperty()"))
        self.Menu_Commands_SetGeoLayer_Contents.addAction(self.Menu_Commands_SetContents_SetGeoLayerProperty)

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Manipulate GeoLayer menu
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_Manipulate_GeoLayer = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Manipulate_GeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_Manipulate_GeoLayer"))
        self.Menu_Commands_Manipulate_GeoLayer.setTitle("Manipulate GeoLayer")
        self.Menu_Commands.addAction(self.Menu_Commands_Manipulate_GeoLayer.menuAction())

        # ChangeGeoLayerGeometry
        self.Menu_Commands_Manipulate_ChangeGeoLayerGeometry = QtWidgets.QAction(main_window)
        self.Menu_Commands_Manipulate_ChangeGeoLayerGeometry.setObjectName(
            qt_util.from_utf8("Menu_Commands_Manipulate_ChangeGeoLayerGeometry"))
        self.Menu_Commands_Manipulate_ChangeGeoLayerGeometry.setText(
            "ChangeGeoLayerGeometry()... <change a GeoLayer to new geometry>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Manipulate_ChangeGeoLayerGeometry.triggered.connect(
            functools.partial(self.edit_new_command, "ChangeGeoLayerGeometry()"))
        self.Menu_Commands_Manipulate_GeoLayer.addAction(self.Menu_Commands_Manipulate_ChangeGeoLayerGeometry)

        # ClipGeoLayer
        self.Menu_Commands_Manipulate_ClipGeoLayer = QtWidgets.QAction(main_window)
        self.Menu_Commands_Manipulate_ClipGeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_Manipulate_ClipGeoLayer"))
        self.Menu_Commands_Manipulate_ClipGeoLayer.setText(
            "ClipGeoLayer()... <clip a GeoLayer by the boundary of another GeoLayer>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Manipulate_ClipGeoLayer.triggered.connect(
            functools.partial(self.edit_new_command, "ClipGeoLayer()"))
        self.Menu_Commands_Manipulate_GeoLayer.addAction(self.Menu_Commands_Manipulate_ClipGeoLayer)

        # IntersectGeoLayer
        self.Menu_Commands_Manipulate_IntersectGeoLayer = QtWidgets.QAction(main_window)
        self.Menu_Commands_Manipulate_IntersectGeoLayer.setObjectName(
            qt_util.from_utf8("Menu_commands_Manipulate_IntersectGeoLayer"))
        self.Menu_Commands_Manipulate_IntersectGeoLayer.setText(
            "IntersectGeoLayer()... <intersects a GeoLayer by another GeoLayer>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Manipulate_IntersectGeoLayer.triggered.connect(
            functools.partial(self.edit_new_command, "IntersectGeoLayer()"))
        self.Menu_Commands_Manipulate_GeoLayer.addAction(
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
            functools.partial(self.edit_new_command, "MergeGeoLayers()"))
        self.Menu_Commands_Manipulate_GeoLayer.addAction(self.Menu_Commands_Manipulate_MergeGeoLayers)

        # RemoveGeoLayerFeatures
        self.Menu_Commands_Manipulate_RemoveGeoLayerFeatures = QtWidgets.QAction(main_window)
        self.Menu_Commands_Manipulate_RemoveGeoLayerFeatures.setObjectName(
            qt_util.from_utf8("Menu_Commands_Manipulate_RemoveGeoLayerFeatures"))
        self.Menu_Commands_Manipulate_RemoveGeoLayerFeatures.setText(
            "RemoveGeoLayerFeatures()... <remove GeoLayer features>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Manipulate_RemoveGeoLayerFeatures.triggered.connect(
            functools.partial(self.edit_new_command, "RemoveGeoLayerFeatures()"))
        self.Menu_Commands_Manipulate_GeoLayer.addAction(self.Menu_Commands_Manipulate_RemoveGeoLayerFeatures)

        # SimplifyGeoLayerGeometry
        self.Menu_Commands_Manipulate_SimplifyGeoLayerGeometry = QtWidgets.QAction(main_window)
        self.Menu_Commands_Manipulate_SimplifyGeoLayerGeometry.setObjectName(
            qt_util.from_utf8("Menu_Commands_Manipulate_SimplifyGeoLayerGeometry"))
        self.Menu_Commands_Manipulate_SimplifyGeoLayerGeometry.setText(
            "SimplifyGeoLayerGeometry()... <decreases the vertices in a polygon or line GeoLayer>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Manipulate_SimplifyGeoLayerGeometry.triggered.connect(
            functools.partial(self.edit_new_command, "SimplifyGeoLayerGeometry()"))
        self.Menu_Commands_Manipulate_GeoLayer.addAction(
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
            functools.partial(self.edit_new_command, "SplitGeoLayerByAttribute()"))
        self.Menu_Commands_Manipulate_GeoLayer.addAction(
            self.Menu_Commands_Manipulate_SplitGeoLayerByAttribute)

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Analyze GeoLayer menu (disabled)
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_Analyze_GeoLayer = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Analyze_GeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_Analyze_GeoLayer"))
        self.Menu_Commands_Analyze_GeoLayer.setTitle("Analyze GeoLayer")
        self.Menu_Commands_Analyze_GeoLayer.setEnabled(False)
        self.Menu_Commands.addAction(self.Menu_Commands_Analyze_GeoLayer.menuAction())

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Check GeoLayer menu (disabled)
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_Check_GeoLayer = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Check_GeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_Check_GeoLayer"))
        self.Menu_Commands_Check_GeoLayer.setTitle("Check GeoLayer")
        self.Menu_Commands_Check_GeoLayer.setEnabled(False)
        self.Menu_Commands.addAction(self.Menu_Commands_Check_GeoLayer.menuAction())

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Write GeoLayer menu
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_Write_GeoLayer = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Write_GeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_Write_GeoLayer"))
        self.Menu_Commands_Write_GeoLayer.setTitle("Write GeoLayer")
        self.Menu_Commands.addAction(self.Menu_Commands_Write_GeoLayer.menuAction())

        # WriteGeoLayerToDelimitedFile
        self.Menu_Commands_Write_WriteGeoLayerToDelimitedFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_Write_WriteGeoLayerToDelimitedFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_Write_WriteGeoLayerToDelimitedFile"))
        self.Menu_Commands_Write_WriteGeoLayerToDelimitedFile.setText(
            "WriteGeoLayerToDelimitedFile()... write GeoLayer to a file in delimited file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Write_WriteGeoLayerToDelimitedFile.triggered.connect(
            functools.partial(self.edit_new_command, "WriteGeoLayerToDelimitedFile()"))
        self.Menu_Commands_Write_GeoLayer.addAction(self.Menu_Commands_Write_WriteGeoLayerToDelimitedFile)

        # WriteGeoLayerToGeoJSON
        self.Menu_Commands_Write_WriteGeoLayerToGeoJSON = QtWidgets.QAction(main_window)
        self.Menu_Commands_Write_WriteGeoLayerToGeoJSON.setObjectName(
            qt_util.from_utf8("Menu_Commands_Write_WriteGeoLayerToGeoJSON"))
        self.Menu_Commands_Write_WriteGeoLayerToGeoJSON.setText(
            "WriteGeoLayerToGeoJSON()... <write GeoLayer to a file in GeoJSON format>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Write_WriteGeoLayerToGeoJSON.triggered.connect(
            functools.partial(self.edit_new_command, "WriteGeoLayerToGeoJSON()"))
        self.Menu_Commands_Write_GeoLayer.addAction(self.Menu_Commands_Write_WriteGeoLayerToGeoJSON)

        # WriteGeoLayerToKML
        self.Menu_Commands_Write_WriteGeoLayerToKML = QtWidgets.QAction(main_window)
        self.Menu_Commands_Write_WriteGeoLayerToKML.setObjectName(
            qt_util.from_utf8("Menu_Commands_Write_WriteGeoLayerToKML"))
        self.Menu_Commands_Write_WriteGeoLayerToKML.setText(
            "WriteGeoLayerToKML()... <write GeoLayer to a file in KML format>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Write_WriteGeoLayerToKML.triggered.connect(
            functools.partial(self.edit_new_command, "WriteGeoLayerToKML()"))
        self.Menu_Commands_Write_GeoLayer.addAction(self.Menu_Commands_Write_WriteGeoLayerToKML)

        # WriteGeoLayerToShapefile
        self.Menu_Commands_Write_WriteGeoLayerToShapefile = QtWidgets.QAction(main_window)
        self.Menu_Commands_Write_WriteGeoLayerToShapefile.setObjectName(
            qt_util.from_utf8("Menu_Commands_Write_WriteGeoLayerToShapefile"))
        self.Menu_Commands_Write_WriteGeoLayerToShapefile.setText(
            "WriteGeoLayerToShapefile()... <write GeoLayer to a file shapefile format>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Write_WriteGeoLayerToShapefile.triggered.connect(
            functools.partial(self.edit_new_command, "WriteGeoLayerToShapefile()"))
        self.Menu_Commands_Write_GeoLayer.addAction(self.Menu_Commands_Write_WriteGeoLayerToShapefile)

        self.Menu_Commands.addSeparator()

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Datastore Processing menu
        # ------------------------------------------------------------------------------------------------------------
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
            functools.partial(self.edit_new_command, "OpenDataStore()"))
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
            functools.partial(self.edit_new_command, "ReadTableFromDataStore()"))
        self.Menu_Commands_DatastoreProcessing.addAction(self.Menu_Commands_DatastoreProcessing_ReadTableFromDataStore)

        # ------------------------------------------------------------------------------------------------------------
        # Commands / GeoMap Processing menu
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_MapProcessing = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_MapProcessing.setObjectName(
            qt_util.from_utf8("Menu_Commands_MapProcessing"))
        self.Menu_Commands_MapProcessing.setTitle("Map Processing")
        self.Menu_Commands.addAction(self.Menu_Commands_MapProcessing.menuAction())

        # CreateGeoMap
        self.Menu_Commands_MapProcessing_CreateGeoMap = QtWidgets.QAction(main_window)
        self.Menu_Commands_MapProcessing_CreateGeoMap.setObjectName(
            qt_util.from_utf8("Menu_Commands_MapProcessing_CreateGeoMap"))
        self.Menu_Commands_MapProcessing_CreateGeoMap.setText(
            "CreateGeoMap()... <create a new GeoMap>")
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_MapProcessing_CreateGeoMap.triggered.connect(
            functools.partial(self.edit_new_command, "CreateGeoMap()"))
        self.Menu_Commands_MapProcessing.addAction(self.Menu_Commands_MapProcessing_CreateGeoMap)

        self.Menu_Commands_MapProcessing.addSeparator()

        # AddGeoLayerViewGroupToGeoMap
        self.Menu_Commands_MapProcessing_AddGeoLayerViewGroupToGeoMap = QtWidgets.QAction(main_window)
        self.Menu_Commands_MapProcessing_AddGeoLayerViewGroupToGeoMap.setObjectName(
            qt_util.from_utf8("Menu_Commands_MapProcessing_AddGeoLayerViewGroupToGeoMap"))
        self.Menu_Commands_MapProcessing_AddGeoLayerViewGroupToGeoMap.setText(
            "AddGeoLayerViewGroupToGeoMap()... <add a GeoLayerViewGroup to a GeoMap>")
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_MapProcessing_AddGeoLayerViewGroupToGeoMap.triggered.connect(
            functools.partial(self.edit_new_command, "AddGeoLayerViewGroupToGeoMap()"))
        self.Menu_Commands_MapProcessing.addAction(self.Menu_Commands_MapProcessing_AddGeoLayerViewGroupToGeoMap)

        # AddGeoLayerViewToGeoMap
        self.Menu_Commands_MapProcessing_AddGeoLayerViewToGeoMap = QtWidgets.QAction(main_window)
        self.Menu_Commands_MapProcessing_AddGeoLayerViewToGeoMap.setObjectName(
            qt_util.from_utf8("Menu_Commands_MapProcessing_AddGeoLayerViewToGeoMap"))
        self.Menu_Commands_MapProcessing_AddGeoLayerViewToGeoMap.setText(
            "AddGeoLayerViewToGeoMap()... <add a GeoLayerView to a GeoMap>")
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_MapProcessing_AddGeoLayerViewToGeoMap.triggered.connect(
            functools.partial(self.edit_new_command, "AddGeoLayerViewToGeoMap()"))
        self.Menu_Commands_MapProcessing.addAction(self.Menu_Commands_MapProcessing_AddGeoLayerViewToGeoMap)

        self.Menu_Commands_MapProcessing.addSeparator()

        # SetGeoLayerViewCategorizedSymbol
        self.Menu_Commands_MapProcessing_SetGeoLayerViewCategorizedSymbol = QtWidgets.QAction(main_window)
        self.Menu_Commands_MapProcessing_SetGeoLayerViewCategorizedSymbol.setObjectName(
            qt_util.from_utf8("Menu_Commands_MapProcessing_SetGeoLayerViewCategorizedSymbol"))
        self.Menu_Commands_MapProcessing_SetGeoLayerViewCategorizedSymbol.setText(
            "SetGeoLayerViewCategorizedSymbol()... <set a GeoLayerView to use categorized symbol>")
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_MapProcessing_SetGeoLayerViewCategorizedSymbol.triggered.connect(
            functools.partial(self.edit_new_command, "SetGeoLayerViewCategorizedSymbol()"))
        self.Menu_Commands_MapProcessing.addAction(self.Menu_Commands_MapProcessing_SetGeoLayerViewCategorizedSymbol)

        # SetGeoLayerViewGraduatedSymbol
        self.Menu_Commands_MapProcessing_SetGeoLayerViewGraduatedSymbol = QtWidgets.QAction(main_window)
        self.Menu_Commands_MapProcessing_SetGeoLayerViewGraduatedSymbol.setObjectName(
            qt_util.from_utf8("Menu_Commands_MapProcessing_SetGeoLayerViewGraduatedSymbol"))
        self.Menu_Commands_MapProcessing_SetGeoLayerViewGraduatedSymbol.setText(
            "SetGeoLayerViewGraduatedSymbol()... <set a GeoLayerView to use graduated symbol>")
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_MapProcessing_SetGeoLayerViewGraduatedSymbol.triggered.connect(
            functools.partial(self.edit_new_command, "SetGeoLayerViewGraduatedSymbol()"))
        self.Menu_Commands_MapProcessing.addAction(self.Menu_Commands_MapProcessing_SetGeoLayerViewGraduatedSymbol)

        # SetGeoLayerViewSingleSymbol
        self.Menu_Commands_MapProcessing_SetGeoLayerViewSingleSymbol = QtWidgets.QAction(main_window)
        self.Menu_Commands_MapProcessing_SetGeoLayerViewSingleSymbol.setObjectName(
            qt_util.from_utf8("Menu_Commands_MapProcessing_SetGeoLayerViewSingleSymbol"))
        self.Menu_Commands_MapProcessing_SetGeoLayerViewSingleSymbol.setText(
            "SetGeoLayerViewSingleSymbol()... <set a GeoLayerView to use a single symbol>")
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_MapProcessing_SetGeoLayerViewSingleSymbol.triggered.connect(
            functools.partial(self.edit_new_command, "SetGeoLayerViewSingleSymbol()"))
        self.Menu_Commands_MapProcessing.addAction(self.Menu_Commands_MapProcessing_SetGeoLayerViewSingleSymbol)

        self.Menu_Commands_MapProcessing.addSeparator()

        # SetGeoLayerViewEventHandler
        self.Menu_Commands_MapProcessing_SetGeoLayerViewEventHandler = QtWidgets.QAction(main_window)
        self.Menu_Commands_MapProcessing_SetGeoLayerViewEventHandler.setObjectName(
            qt_util.from_utf8("Menu_Commands_MapProcessing_SetGeoLayerViewEventHandler"))
        self.Menu_Commands_MapProcessing_SetGeoLayerViewEventHandler.setText(
            "SetGeoLayerViewEventHandler()... <set a GeoLayerView event handler>")
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_MapProcessing_SetGeoLayerViewEventHandler.triggered.connect(
            functools.partial(self.edit_new_command, "SetGeoLayerViewEventHandler()"))
        self.Menu_Commands_MapProcessing.addAction(self.Menu_Commands_MapProcessing_SetGeoLayerViewEventHandler)

        self.Menu_Commands_MapProcessing.addSeparator()

        # CreateGeoMapProject
        self.Menu_Commands_MapProcessing_CreateGeoMapProject = QtWidgets.QAction(main_window)
        self.Menu_Commands_MapProcessing_CreateGeoMapProject.setObjectName(
            qt_util.from_utf8("Menu_Commands_MapProcessing_CreateGeoMapProject"))
        self.Menu_Commands_MapProcessing_CreateGeoMapProject.setText(
            "CreateGeoMapProject()... <create a new GeoMapProject>")
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_MapProcessing_CreateGeoMapProject.triggered.connect(
            functools.partial(self.edit_new_command, "CreateGeoMapProject()"))
        self.Menu_Commands_MapProcessing.addAction(self.Menu_Commands_MapProcessing_CreateGeoMapProject)

        # AddGeoMapToGeoMapProject
        self.Menu_Commands_MapProcessing_AddGeoMapToGeoMapProject = QtWidgets.QAction(main_window)
        self.Menu_Commands_MapProcessing_AddGeoMapToGeoMapProject.setObjectName(
            qt_util.from_utf8("Menu_Commands_MapProcessing_AddGeoMapToGeoMapProject"))
        self.Menu_Commands_MapProcessing_AddGeoMapToGeoMapProject.setText(
            "AddGeoMapToGeoMapProject()... <add a GeoMap to a GeoMapProject>")
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_MapProcessing_AddGeoMapToGeoMapProject.triggered.connect(
            functools.partial(self.edit_new_command, "AddGeoMapToGeoMapProject()"))
        self.Menu_Commands_MapProcessing.addAction(self.Menu_Commands_MapProcessing_AddGeoMapToGeoMapProject)

        # WriteGeoMapProjectToJSON
        self.Menu_Commands_MapProcessing_WriteGeoMapProjectToJSON = QtWidgets.QAction(main_window)
        self.Menu_Commands_MapProcessing_WriteGeoMapProjectToJSON.setObjectName(
            qt_util.from_utf8("Menu_Commands_MapProcessing_WriteGeoMapProjectToJSON"))
        self.Menu_Commands_MapProcessing_WriteGeoMapProjectToJSON.setText(
            "WriteGeoMapProjectToJSON()... <write a GeoMapProject to JSON file>")
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_MapProcessing_WriteGeoMapProjectToJSON.triggered.connect(
            functools.partial(self.edit_new_command, "WriteGeoMapProjectToJSON()"))
        self.Menu_Commands_MapProcessing.addAction(self.Menu_Commands_MapProcessing_WriteGeoMapProjectToJSON)

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Network Processing menu (disabled)
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_NetworkProcessing = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_NetworkProcessing.setObjectName(
            qt_util.from_utf8("Menu_Commands_NetworkProcessing"))
        self.Menu_Commands_NetworkProcessing.setTitle("Network Processing")
        self.Menu_Commands_NetworkProcessing.setEnabled(False)
        self.Menu_Commands.addAction(self.Menu_Commands_NetworkProcessing.menuAction())

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Spreadsheet Processing menu (disabled)
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_SpreadsheetProcessing = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_SpreadsheetProcessing.setObjectName(
            qt_util.from_utf8("Menu_Commands_SpreadsheetProcessing"))
        self.Menu_Commands_SpreadsheetProcessing.setTitle("Spreadsheet Processing")
        self.Menu_Commands_SpreadsheetProcessing.setEnabled(False)
        self.Menu_Commands.addAction(self.Menu_Commands_SpreadsheetProcessing.menuAction())

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Template Processing menu (disabled)
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_TemplateProcessing = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_TemplateProcessing.setObjectName(
            qt_util.from_utf8("Menu_Commands_TemplateProcessing"))
        self.Menu_Commands_TemplateProcessing.setTitle("Template Processing")
        self.Menu_Commands_TemplateProcessing.setEnabled(False)
        self.Menu_Commands.addAction(self.Menu_Commands_TemplateProcessing.menuAction())

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Visualization Processing (disabled)
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_VisualizationProcessing = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_VisualizationProcessing.setObjectName(
            qt_util.from_utf8("Menu_Commands_VisualizationProcessing"))
        self.Menu_Commands_VisualizationProcessing.setTitle("Visualization Processing")
        self.Menu_Commands_VisualizationProcessing.setEnabled(False)
        self.Menu_Commands.addAction(self.Menu_Commands_VisualizationProcessing.menuAction())

        # ------------------------------------------------------------------------------------------------------------
        # Commands / General - Comments menu
        # ------------------------------------------------------------------------------------------------------------
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
            functools.partial(self.edit_new_command, "# "))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_Single)

        # Comments / General - Comments / Multi-line menus
        self.Menu_Commands_General_Comments_MultipleStart = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_Comments_MultipleStart.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_Comments_MultipleStart"))
        self.Menu_Commands_General_Comments_MultipleStart.setText("/* <start multi-line comment section> ")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_Comments_MultipleStart.triggered.connect(
            functools.partial(self.edit_new_command, "/*"))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_MultipleStart)

        # MultipleEnd
        self.Menu_Commands_General_Comments_MultipleEnd = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_Comments_MultipleEnd.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_Comments_MultipleEnd"))
        self.Menu_Commands_General_Comments_MultipleEnd.setText("*/ <end multi-line comment section>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_Comments_MultipleEnd.triggered.connect(
            functools.partial(self.edit_new_command, "*/"))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_MultipleEnd)

        self.Menu_Commands_General_Comments.addSeparator()

        # Comments / General - Comments / #@docExample
        self.Menu_Commands_General_Comments_DocExample = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_Comments_DocExample.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_Comments_DocExample"))
        self.Menu_Commands_General_Comments_DocExample.setText(
            "#@docExample <command file is documentation example>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_Comments_DocExample.triggered.connect(
            functools.partial(self.edit_new_command, "#@docExample"))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_DocExample)

        # Comments / General - Comments / Enabled menu
        self.Menu_Commands_General_Comments_EnabledFalse = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_Comments_EnabledFalse.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_Comments_Enabled"))
        self.Menu_Commands_General_Comments_EnabledFalse.setText("#@enabled False <disables the command file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_Comments_EnabledFalse.triggered.connect(
            functools.partial(self.edit_new_command, "#@enabled False"))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_EnabledFalse)

        # Comments / General - Comments / special comments for testing fail/warn

        # Comments / General - Comments / #@expectedStatus Failure
        self.Menu_Commands_General_Comments_ExpectedStatusFail = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_Comments_ExpectedStatusFail.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_Comments_ExpectedStatusFail"))
        self.Menu_Commands_General_Comments_ExpectedStatusFail.setText(
            "#@expectedStatus Failure <used to test commands>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_Comments_ExpectedStatusFail.triggered.connect(
            functools.partial(self.edit_new_command, "#@expectedStatus Failure"))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_ExpectedStatusFail)

        # Comments / General - Comments / #@expectedStatus Warning
        self.Menu_Commands_General_Comments_ExpectedStatusWarn = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_Comments_ExpectedStatusWarn.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_Comments_ExpectedStatusWarn"))
        self.Menu_Commands_General_Comments_ExpectedStatusWarn.setText(
            "#@expectedStatus Warning <used to test commands>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_Comments_ExpectedStatusWarn.triggered.connect(
            functools.partial(self.edit_new_command, "#@expectedStatus Warning"))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_ExpectedStatusWarn)
        # Add to menu bar
        self.menubar.addAction(self.Menu_Commands.menuAction())

        self.Menu_Commands_General_Comments.addSeparator()

        # Blank
        self.Menu_Commands_General_Comments_Blank = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_Comments_Blank.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_Comments_Blank"))
        self.Menu_Commands_General_Comments_Blank.setText("<empty line>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_Comments_Blank.triggered.connect(
            functools.partial(self.edit_new_command, ""))
        self.Menu_Commands_General_Comments.addAction(self.Menu_Commands_General_Comments_Blank)

        # ------------------------------------------------------------------------------------------------------------
        # Commands / General - File Handling
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_General_FileHandling = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_General_FileHandling.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_FileHandling"))
        self.Menu_Commands_General_FileHandling.setTitle("General - File Handling")
        self.Menu_Commands.addAction(self.Menu_Commands_General_FileHandling.menuAction())

        # FTPGet
        self.Menu_Commands_General_FileHandling_FTPGet = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_FileHandling_FTPGet.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_FileHandling_FTPGet"))
        self.Menu_Commands_General_FileHandling_FTPGet.setText(
            "FTPGet()... <download 1+ files from an FTP site>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_FileHandling_FTPGet.triggered.connect(
            functools.partial(self.edit_new_command, "FTPGet()"))
        self.Menu_Commands_General_FileHandling.addAction(self.Menu_Commands_General_FileHandling_FTPGet)

        # WebGet
        self.Menu_Commands_General_FileHandling_WebGet = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_FileHandling_WebGet.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_FileHandling_WebGet"))
        self.Menu_Commands_General_FileHandling_WebGet.setText(
            "WebGet()... <download a file from website using URL>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_FileHandling_WebGet.triggered.connect(
            functools.partial(self.edit_new_command, "WebGet()"))
        self.Menu_Commands_General_FileHandling.addAction(self.Menu_Commands_General_FileHandling_WebGet)

        self.Menu_Commands_General_FileHandling.addSeparator()

        # CreateFolder
        self.Menu_Commands_General_FileHandling_CreateFolder = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_FileHandling_CreateFolder.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_FileHandling_CreateFolder"))
        self.Menu_Commands_General_FileHandling_CreateFolder.setText(
            "CreateFolder()... <create a folder>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_FileHandling_CreateFolder.triggered.connect(
            functools.partial(self.edit_new_command, "CreateFolder()"))
        self.Menu_Commands_General_FileHandling.addAction(self.Menu_Commands_General_FileHandling_CreateFolder)

        self.Menu_Commands_General_FileHandling.addSeparator()

        # CopyFile
        self.Menu_Commands_General_FileHandling_CopyFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_FileHandling_CopyFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_FileHandling_CopyFile"))
        self.Menu_Commands_General_FileHandling_CopyFile.setText(
            "CopyFile()... <copy a file to a new file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_FileHandling_CopyFile.triggered.connect(
            functools.partial(self.edit_new_command, "CopyFile()"))
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
            functools.partial(self.edit_new_command, "ListFiles()"))
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
            functools.partial(self.edit_new_command, "RemoveFile()"))
        self.Menu_Commands_General_FileHandling.addAction(self.Menu_Commands_General_FileHandling_RemoveFile)

        self.Menu_Commands_General_FileHandling.addSeparator()

        # UnzipFile
        self.Menu_Commands_General_FileHandling_UnzipFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_FileHandling_UnzipFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_FileHandling_UnzipFile"))
        self.Menu_Commands_General_FileHandling_UnzipFile.setText(
            "UnzipFile()... <unzip a file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_FileHandling_UnzipFile.triggered.connect(
            functools.partial(self.edit_new_command, "UnzipFile()"))
        self.Menu_Commands_General_FileHandling.addAction(self.Menu_Commands_General_FileHandling_UnzipFile)

        # ------------------------------------------------------------------------------------------------------------
        # Commands / General - Logging and Messaging menu
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_General_LoggingMessaging = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_General_LoggingMessaging.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_LoggingMessaging"))
        self.Menu_Commands_General_LoggingMessaging.setTitle("General - Logging and Messaging")
        self.Menu_Commands.addAction(self.Menu_Commands_General_LoggingMessaging.menuAction())

        # StartLog
        self.Menu_Commands_General_LoggingMessaging_StartLog = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_LoggingMessaging_StartLog.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_LoggingMessaging_StartLog"))
        self.Menu_Commands_General_LoggingMessaging_StartLog.setText(
            "StartLog()... <start a new log file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_LoggingMessaging_StartLog.triggered.connect(
            functools.partial(self.edit_new_command, "StartLog()"))
        self.Menu_Commands_General_LoggingMessaging.addAction(self.Menu_Commands_General_LoggingMessaging_StartLog)

        # Message
        self.Menu_Commands_General_LoggingMessaging_Message = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_LoggingMessaging_Message.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_LoggingMessaging_Message"))
        self.Menu_Commands_General_LoggingMessaging_Message.setText(
            "Message()... <print a message to the log file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_LoggingMessaging_Message.triggered.connect(
            functools.partial(self.edit_new_command, "Message()"))
        self.Menu_Commands_General_LoggingMessaging.addAction(self.Menu_Commands_General_LoggingMessaging_Message)

        # ------------------------------------------------------------------------------------------------------------
        # Commands / General - Running and Properties menu
        # ------------------------------------------------------------------------------------------------------------
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
            functools.partial(self.edit_new_command, "If()"))
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
            functools.partial(self.edit_new_command, "EndIf()"))
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
            functools.partial(self.edit_new_command, "For()"))
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
            functools.partial(self.edit_new_command, "EndFor()"))
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
            functools.partial(self.edit_new_command, "RunCommands()"))
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
            functools.partial(self.edit_new_command, "RunGdalProgram()"))
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
            functools.partial(self.edit_new_command, "RunOgrProgram()"))
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
            functools.partial(self.edit_new_command, "RunProgram()"))
        self.Menu_Commands_General_RunningProperties.addAction(self.Menu_Commands_General_RunningProperties_RunProgram)

        self.Menu_Commands_General_RunningProperties.addSeparator()

        # SetProperty
        self.Menu_Commands_General_RunningProperties_SetProperty = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_RunningProperties_SetProperty.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties_SetProperty"))
        self.Menu_Commands_General_RunningProperties_SetProperty.setText(
            "SetProperty()... <set a GeoProcessor property>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_RunningProperties_SetProperty.triggered.connect(
            functools.partial(self.edit_new_command, "SetProperty()"))
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
            functools.partial(self.edit_new_command, "SetPropertyFromGeoLayer()"))
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
            functools.partial(self.edit_new_command, "WritePropertiesToFile()"))
        self.Menu_Commands_General_RunningProperties.addAction(
            self.Menu_Commands_General_RunningProperties_WritePropertiesToFile)

        self.Menu_Commands_General_RunningProperties.addSeparator()

        # Exit
        self.Menu_Commands_General_RunningProperties_Exit = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_RunningProperties_Exit.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties_Exit"))
        self.Menu_Commands_General_RunningProperties_Exit.setText(
            "Exit()... <end processing>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_RunningProperties_Exit.triggered.connect(
            functools.partial(self.edit_new_command, "Exit()"))
        self.Menu_Commands_General_RunningProperties.addAction(self.Menu_Commands_General_RunningProperties_Exit)

        self.Menu_Commands_General_RunningProperties.addSeparator()

        # QgisAlgorithmHelp
        self.Menu_Commands_General_RunningProperties_QgisAlgorithmHelp = QtWidgets.QAction(main_window)
        self.Menu_Commands_General_RunningProperties_QgisAlgorithmHelp.setObjectName(
            qt_util.from_utf8("Menu_Commands_General_RunningProperties_QgisAlgorithmHelp"))
        self.Menu_Commands_General_RunningProperties_QgisAlgorithmHelp.setText(
            "QgisAlgorithmHelp()... <print algorithm help>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_General_RunningProperties_QgisAlgorithmHelp.triggered.connect(
            functools.partial(self.edit_new_command, "QgisAlgorithmHelp()"))
        self.Menu_Commands_General_RunningProperties.addAction(
            self.Menu_Commands_General_RunningProperties_QgisAlgorithmHelp)

        # ------------------------------------------------------------------------------------------------------------
        # Commands / General - Test Processing menu
        # ------------------------------------------------------------------------------------------------------------
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
            functools.partial(self.edit_new_command, "CompareFiles()"))
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
            functools.partial(self.edit_new_command, "CreateRegressionTestCommandFile()"))
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
            functools.partial(self.edit_new_command, "StartRegressionTestResultsReport()"))
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
            functools.partial(self.edit_new_command, "WriteCommandSummaryToFile()"))
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
            functools.partial(self.edit_new_command, "WriteGeoLayerPropertiesToFile()"))
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

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Create - Raster GeoLayer menu
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_Raster_Create_RasterGeoLayer = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Raster_Create_RasterGeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_Raster_Create_RasterGeoLayer"))
        self.Menu_Commands_Raster_Create_RasterGeoLayer.setTitle("Create Raster GeoLayer")
        self.Menu_Commands_Raster.addAction(self.Menu_Commands_Raster_Create_RasterGeoLayer.menuAction())

        # CreateRasterGeoLayer
        self.Menu_Commands_Raster_Create_CreateRasterGeoLayer = QtWidgets.QAction(main_window)
        self.Menu_Commands_Raster_Create_CreateRasterGeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_Raster_Create_CreateRasterGeoLayer"))
        self.Menu_Commands_Raster_Create_CreateRasterGeoLayer.setText(
            "CreateRasterGeoLayer()... <create a Raster GeoLayer>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Raster_Create_CreateRasterGeoLayer.triggered.connect(
            functools.partial(self.edit_new_command, "CreateRasterGeoLayer()"))
        self.Menu_Commands_Raster_Create_RasterGeoLayer.addAction(
            self.Menu_Commands_Raster_Create_CreateRasterGeoLayer)

        # RasterizeGeoLayer
        self.Menu_Commands_Raster_Create_RasterizeGeoLayer = QtWidgets.QAction(main_window)
        self.Menu_Commands_Raster_Create_RasterizeGeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_Raster_Create_RasterizeGeoLayer"))
        self.Menu_Commands_Raster_Create_RasterizeGeoLayer.setText(
            "RasterizeGeoLayer()... <Create a raster GeoLayer from a vector GeoLayer>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Raster_Create_RasterizeGeoLayer.triggered.connect(
            functools.partial(self.edit_new_command, "RasterizeGeoLayer()"))
        self.Menu_Commands_Raster_Create_RasterGeoLayer.addAction(
            self.Menu_Commands_Raster_Create_RasterizeGeoLayer)

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Read - Raster GeoLayer menu
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_Raster_Read_RasterGeoLayer = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Raster_Read_RasterGeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_Raster_Read_Raster_GeoLayer"))
        self.Menu_Commands_Raster_Read_RasterGeoLayer.setTitle("Read Raster GeoLayer")
        self.Menu_Commands_Raster.addAction(self.Menu_Commands_Raster_Read_RasterGeoLayer.menuAction())

        # ReadRasterGeoLayerFromFile
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_Raster_Read_ReadRasterGeoLayerFromFile"))
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromFile.setText(
            "ReadRasterGeoLayerFromFile()... <read a Raster GeoLayer from a file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromFile.triggered.connect(
            functools.partial(self.edit_new_command, "ReadRasterGeoLayerFromFile()"))
        self.Menu_Commands_Raster_Read_RasterGeoLayer.addAction(
            self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromFile)

        self.Menu_Commands_Raster_Read_RasterGeoLayer.addSeparator()

        # ReadRasterGeoLayerFromTileMapService
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromTileMapService = QtWidgets.QAction(main_window)
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromTileMapService.setObjectName(
            qt_util.from_utf8("Menu_Commands_Raster_Read_ReadRasterGeoLayerFromTileMapService"))
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromTileMapService.setText(
            "ReadRasterGeoLayerFromTileMapService()... <read a Raster GeoLayer from a file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromTileMapService.triggered.connect(
            functools.partial(self.edit_new_command, "ReadRasterGeoLayerFromTileMapService()"))
        self.Menu_Commands_Raster_Read_RasterGeoLayer.addAction(
            self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromTileMapService)

        # ReadRasterGeoLayerFromWebMapService
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromWebMapService = QtWidgets.QAction(main_window)
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromWebMapService.setObjectName(
            qt_util.from_utf8("Menu_Commands_Raster_Read_ReadRasterGeoLayerFromWebMapService"))
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromWebMapService.setText(
            "ReadRasterGeoLayerFromWebMapService()... <read a Raster GeoLayer from a file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromWebMapService.triggered.connect(
            functools.partial(self.edit_new_command, "ReadRasterGeoLayerFromWebMapService()"))
        self.Menu_Commands_Raster_Read_RasterGeoLayer.addAction(
            self.Menu_Commands_Raster_Read_ReadRasterGeoLayerFromWebMapService)

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Write - Raster GeoLayer menu
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_Raster_Write_RasterGeoLayer = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Raster_Write_RasterGeoLayer.setObjectName(
            qt_util.from_utf8("Menu_Commands_Raster_Write_Raster_GeoLayer"))
        self.Menu_Commands_Raster_Write_RasterGeoLayer.setTitle("Write Raster GeoLayer")
        self.Menu_Commands_Raster.addAction(self.Menu_Commands_Raster_Write_RasterGeoLayer.menuAction())

        # WriteRasterGeoLayerToFile
        self.Menu_Commands_Raster_Write_WriteRasterGeoLayerToFile = QtWidgets.QAction(main_window)
        self.Menu_Commands_Raster_Write_WriteRasterGeoLayerToFile.setObjectName(
            qt_util.from_utf8("Menu_Commands_Raster_Write_WriteRasterGeoLayerToFile"))
        self.Menu_Commands_Raster_Write_WriteRasterGeoLayerToFile.setText(
            "WriteRasterGeoLayerToFile()... <write a Raster GeoLayer to a file>")
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.Menu_Commands_Raster_Write_WriteRasterGeoLayerToFile.triggered.connect(
            functools.partial(self.edit_new_command, "WriteRasterGeoLayerToFile()"))
        self.Menu_Commands_Raster_Write_RasterGeoLayer.addAction(
            self.Menu_Commands_Raster_Write_WriteRasterGeoLayerToFile)

        # ============================================================================================================
        # Commands(Table) menu
        # ============================================================================================================

        self.Menu_Commands_Table = QtWidgets.QMenu(self.menubar)
        self.Menu_Commands_Table.setObjectName(qt_util.from_utf8("Menu_Commands_Table"))
        self.Menu_Commands_Table.setTitle("Commands(Table)")

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Tables / Read menu
        # ------------------------------------------------------------------------------------------------------------
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
            functools.partial(self.edit_new_command, "ReadTableFromDataStore()"))
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
            functools.partial(self.edit_new_command, "ReadTableFromDelimitedFile()"))
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
            functools.partial(self.edit_new_command, "ReadTableFromExcel()"))
        self.Menu_Commands_Tables_Read.addAction(self.Menu_Commands_Table_ReadTableFromExcel)

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Tables / Process menu
        # ------------------------------------------------------------------------------------------------------------
        self.Menu_Commands_Tables_Process = QtWidgets.QMenu(self.Menu_Commands_Table)
        self.Menu_Commands_Tables_Process.setObjectName(qt_util.from_utf8("Menu_Commands_Tables_Process"))
        self.Menu_Commands_Tables_Process.setTitle("Process Table")
        self.Menu_Commands_Tables_Process.setEnabled(False)
        self.Menu_Commands_Table.addAction(self.Menu_Commands_Tables_Process.menuAction())

        # ------------------------------------------------------------------------------------------------------------
        # Commands / Tables / Write menu
        # ------------------------------------------------------------------------------------------------------------
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
            functools.partial(self.edit_new_command, "WriteTableToDataStore()"))
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
            functools.partial(self.edit_new_command, "WriteTableToDelimitedFile()"))
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
            functools.partial(self.edit_new_command, "WriteTableToExcel()"))
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
        self.results_GeoLayers_Table.setColumnCount(7)
        self.results_GeoLayers_Table.setRowCount(0)
        self.results_GeoLayers_Table.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem())
        self.results_GeoLayers_Table.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem())
        self.results_GeoLayers_Table.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem())
        self.results_GeoLayers_Table.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem())
        self.results_GeoLayers_Table.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem())
        self.results_GeoLayers_Table.setHorizontalHeaderItem(5, QtWidgets.QTableWidgetItem())
        self.results_GeoLayers_Table.setHorizontalHeaderItem(6, QtWidgets.QTableWidgetItem())
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
        self.results_GeoLayers_Table.horizontalHeaderItem(0).setText("GeoLayerID")
        self.results_GeoLayers_Table.horizontalHeaderItem(0).setToolTip("GeoLayerID - unique identifier for GeoLayer")
        self.results_GeoLayers_Table.horizontalHeaderItem(1).setText("Name")
        self.results_GeoLayers_Table.horizontalHeaderItem(1).setToolTip("GeoLayer name")
        self.results_GeoLayers_Table.horizontalHeaderItem(2).setText("Geometry")
        self.results_GeoLayers_Table.horizontalHeaderItem(2).setToolTip("Geometry")
        self.results_GeoLayers_Table.horizontalHeaderItem(3).setText("Feature Count")
        self.results_GeoLayers_Table.horizontalHeaderItem(3).setToolTip("Feature Count")
        self.results_GeoLayers_Table.horizontalHeaderItem(4).setText("Coordinate Reference System (CRS)")
        self.results_GeoLayers_Table.horizontalHeaderItem(4).setToolTip("Coordinate Reference System (CRS)")
        self.results_GeoLayers_Table.horizontalHeaderItem(5).setText("Input Format")
        self.results_GeoLayers_Table.horizontalHeaderItem(5).setToolTip("Input format (GDAL driver type)")
        self.results_GeoLayers_Table.horizontalHeaderItem(6).setText("Input path")
        self.results_GeoLayers_Table.horizontalHeaderItem(6).setToolTip("Path to input file/database/service")
        self.results_GeoLayers_Table.horizontalHeader().setStyleSheet("::section { background-color: #d3d3d3 }")
        self.results_GeoLayers_Table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.results_GeoLayers_Table.customContextMenuRequested.connect(self.ui_action_results_geolayers_right_click)
        self.results_TabWidget.setTabText(self.results_TabWidget.indexOf(self.results_GeoLayers_Tab), "GeoLayers")

        # Results - GeoMaps tab
        self.results_GeoMaps_Tab = QtWidgets.QWidget()
        self.results_GeoMaps_Tab.setObjectName(qt_util.from_utf8("results_GeoMaps_Tab"))
        self.results_GeoMaps_VerticalLayout = QtWidgets.QVBoxLayout(self.results_GeoMaps_Tab)
        self.results_GeoMaps_VerticalLayout.setObjectName(qt_util.from_utf8("results_GeoMaps_VerticalLayout"))
        self.results_GeoMaps_GroupBox = QtWidgets.QGroupBox(self.results_GeoMaps_Tab)
        self.results_GeoMaps_GroupBox.setObjectName(qt_util.from_utf8("results_GeoMaps_GroupBox"))
        self.results_GeoMaps_GroupBox_VerticalLayout = QtWidgets.QVBoxLayout(self.results_GeoMaps_GroupBox)
        self.results_GeoMaps_GroupBox_VerticalLayout.setObjectName(
            qt_util.from_utf8("results_GeoMaps_GroupBox_VerticalLayout"))
        self.results_GeoMaps_Table = QtWidgets.QTableWidget(self.results_GeoMaps_GroupBox)
        self.results_GeoMaps_Table.setObjectName(qt_util.from_utf8("results_GeoMaps_Table"))
        self.results_GeoMaps_Table.setColumnCount(5)
        self.results_GeoMaps_Table.setRowCount(0)
        self.results_GeoMaps_Table.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem())
        self.results_GeoMaps_Table.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem())
        self.results_GeoMaps_Table.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem())
        self.results_GeoMaps_Table.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem())
        self.results_GeoMaps_Table.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem())
        self.results_GeoMaps_Table.horizontalHeader().setDefaultSectionSize(175)
        self.results_GeoMaps_Table.horizontalHeader().setStretchLastSection(True)
        self.results_GeoMaps_GroupBox_VerticalLayout.addWidget(self.results_GeoMaps_Table)
        self.results_GeoMaps_VerticalLayout.addWidget(self.results_GeoMaps_GroupBox)
        self.results_TabWidget.addTab(self.results_GeoMaps_Tab, qt_util.from_utf8(""))
        # Used to be in retranslateUi
        self.results_GeoMaps_GroupBox.setTitle("GeoMaps (0 GeoMaps, 0 selected)")
        self.results_GeoMaps_Table.horizontalHeaderItem(0).setText("GeoMapID")
        self.results_GeoMaps_Table.horizontalHeaderItem(0).setToolTip("GeoMapID - uniquely identifies the GeoMap")
        self.results_GeoMaps_Table.horizontalHeaderItem(1).setText("Name")
        self.results_GeoMaps_Table.horizontalHeaderItem(1).setToolTip("GeoMap Name")
        self.results_GeoMaps_Table.horizontalHeaderItem(2).setText("GeoLayerViewGroups")
        self.results_GeoMaps_Table.horizontalHeaderItem(2).setToolTip("How many GeoLayerViewGroups in the GeoMap")
        self.results_GeoMaps_Table.horizontalHeaderItem(3).setText("GeoLayers")
        self.results_GeoMaps_Table.horizontalHeaderItem(3).setToolTip("How many GeoLayers in the GeoMap")
        self.results_GeoMaps_Table.horizontalHeaderItem(4).setText("Coordinate Reference System (CRS)")
        self.results_GeoMaps_Table.horizontalHeaderItem(4).setToolTip("Coordinate Reference System (CRS)")
        self.results_GeoMaps_Table.horizontalHeader().setStyleSheet("::section { background-color: #d3d3d3 }")
        self.results_TabWidget.setTabText(self.results_TabWidget.indexOf(self.results_GeoMaps_Tab), "GeoMaps")

        # Results - GeoMapProjects tab
        self.results_GeoMapProjects_Tab = QtWidgets.QWidget()
        self.results_GeoMapProjects_Tab.setObjectName(qt_util.from_utf8("results_GeoMapProjects_Tab"))
        self.results_GeoMapProjects_VerticalLayout = QtWidgets.QVBoxLayout(self.results_GeoMapProjects_Tab)
        self.results_GeoMapProjects_VerticalLayout.setObjectName(
            qt_util.from_utf8("results_GeoMapProjects_VerticalLayout"))
        self.results_GeoMapProjects_GroupBox = QtWidgets.QGroupBox(self.results_GeoMapProjects_Tab)
        self.results_GeoMapProjects_GroupBox.setObjectName(qt_util.from_utf8("results_GeoMapProjects_GroupBox"))
        self.results_GeoMapProjects_GroupBox_VerticalLayout =\
            QtWidgets.QVBoxLayout(self.results_GeoMapProjects_GroupBox)
        self.results_GeoMapProjects_GroupBox_VerticalLayout.setObjectName(
            qt_util.from_utf8("results_GeoMapProjects_GroupBox_VerticalLayout"))
        self.results_GeoMapProjects_Table = QtWidgets.QTableWidget(self.results_GeoMapProjects_GroupBox)
        self.results_GeoMapProjects_Table.setObjectName(qt_util.from_utf8("results_GeoMapProjects_Table"))
        self.results_GeoMapProjects_Table.setColumnCount(4)
        self.results_GeoMapProjects_Table.setRowCount(0)
        self.results_GeoMapProjects_Table.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem())
        self.results_GeoMapProjects_Table.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem())
        self.results_GeoMapProjects_Table.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem())
        self.results_GeoMapProjects_Table.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem())
        self.results_GeoMapProjects_Table.horizontalHeader().setDefaultSectionSize(175)
        self.results_GeoMapProjects_Table.horizontalHeader().setStretchLastSection(True)
        self.results_GeoMapProjects_GroupBox_VerticalLayout.addWidget(self.results_GeoMapProjects_Table)
        self.results_GeoMapProjects_VerticalLayout.addWidget(self.results_GeoMapProjects_GroupBox)
        self.results_TabWidget.addTab(self.results_GeoMapProjects_Tab, qt_util.from_utf8(""))
        # Used to be in retranslateUi
        self.results_GeoMapProjects_GroupBox.setTitle("GeoMapProjects (0 GeoMapProjects, 0 selected)")
        self.results_GeoMapProjects_Table.horizontalHeaderItem(0).setText("GeoMapProjectID")
        self.results_GeoMapProjects_Table.horizontalHeaderItem(0).setToolTip(
            "GeoMapProjectID - uniquely identifies the GeoMapProject")
        self.results_GeoMapProjects_Table.horizontalHeaderItem(1).setText("Name")
        self.results_GeoMapProjects_Table.horizontalHeaderItem(1).setToolTip("GeoMapProject Name")
        self.results_GeoMapProjects_Table.horizontalHeaderItem(2).setText("GeoMaps")
        self.results_GeoMapProjects_Table.horizontalHeaderItem(2).setToolTip("How many GeoMaps in the GeoMapProject")
        self.results_GeoMapProjects_Table.horizontalHeaderItem(3).setText("Description")
        self.results_GeoMapProjects_Table.horizontalHeaderItem(3).setToolTip("GeoMapProject Description")
        self.results_GeoMapProjects_Table.horizontalHeader().setStyleSheet("::section { background-color: #d3d3d3 }")
        self.results_TabWidget.setTabText(self.results_TabWidget.indexOf(
            self.results_GeoMapProjects_Tab), "GeoMapProjects")

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
        # Use the following because connect() is shown as unresolved reference in PyCharm
        self.results_OutputFiles_Table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.results_OutputFiles_Table.customContextMenuRequested.connect(
            self.ui_action_results_outputfiles_right_click)
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
        self.results_Tables_Table.horizontalHeaderItem(3).setText("Description")
        self.results_Tables_Table.horizontalHeaderItem(3).setToolTip("Description")
        self.results_Tables_Table.horizontalHeader().setStyleSheet("::section { background-color: #d3d3d3 }")
        self.results_Tables_Table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.results_Tables_Table.customContextMenuRequested.connect(self.ui_action_results_tables_right_click)
        self.results_TabWidget.setTabText(self.results_TabWidget.indexOf(self.results_Tables_Tab), "Tables")

        # Add the Results tab to the vertical layout
        self.results_VerticalLayout.addWidget(self.results_TabWidget)
        # Now add the Results to the central widget
        self.centralwidget_GridLayout.addWidget(self.results_GroupBox, y_centralwidget, 0, 1, 6)
        # Set the visible tab to the GeoLayers
        self.results_TabWidget.setCurrentIndex(0)

        # Set up event handlers

        # GeoLayers
        # Listen for a change in item selection within the results_GeoLayers_Table widget.
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.results_GeoLayers_Table.itemSelectionChanged.connect(self.update_ui_status)
        # GeoMaps
        # Listen for a change in item selection within the results_GeoMaps_Table widget.
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.results_GeoMaps_Table.itemSelectionChanged.connect(self.update_ui_status)
        # GeoMapProjects
        # Listen for a change in item selection within the results_GeoMaps_Table widget.
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.results_GeoMapProjects_Table.itemSelectionChanged.connect(self.update_ui_status)
        # Output Files
        # Listen for a change in item selection within the results_OutputFiles_Table widget.
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.results_OutputFiles_Table.itemSelectionChanged.connect(self.update_ui_status)
        # Properties
        # Listen for a change in item selection within the results_Properties_Table widget.
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.results_Properties_Table.itemSelectionChanged.connect(self.update_ui_status)
        # Tables
        # Listen for a change in item selection within the results_Tables_Table widget.
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.results_Tables_Table.itemSelectionChanged.connect(self.update_ui_status)

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
            self.command_CommandListWidget.event_handler_increase_indent_button_clicked)

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
        # Create command status dialog box
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

        # Set colors for different status levels
        color_warning = 'yellow'
        color_failure = '#ffa8a8'  # Red (dull so does not overwhelm text)
        color_success = '#7dba71'  # Green (dull so does not overwhelm text)
        color_unknown = 'white'

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
            # - HTML formatting or other free-form format is preferred because content will fill table cells
            show_all_log_messages = True   # False only shows warning and failure messages
            # noinspection PyBroadException
            try:
                command_status = selected_command.command_status

                html_string = (
                    "<style> td.failure{background-color:red} </style>" +
                    "<p><b>Command {}:<br>{}</b></p>".format(row_index + 1, selected_command.command_string) +

                    "<p><b>Command Status Summary</b> (see below for details if problems exist):</p>" +
                    "<table border='1'>" +
                    "<tr style='background-color:#d0d0ff; font-weight:bold;'>" +
                    "<th> Phase </th>" +
                    "<th> Status/Max Severity </th>" +
                    "</tr>"
                )

                if command_status.initialization_status is CommandStatusType.WARNING:
                    style = "style='background-color:{}'".format(color_warning)
                elif command_status.initialization_status is CommandStatusType.FAILURE:
                    style = "style='background-color:{}'".format(color_failure)
                elif command_status.initialization_status is CommandStatusType.SUCCESS:
                    style = "style='background-color:{}'".format(color_success)
                else:
                    # Typically UNKNOWN
                    style = "style='background-color:{}'".format(color_unknown)

                html_string += (
                    "<tr>" +
                    "<td> INITIALIZATION </td>" +
                    "<td " + style + ">" + str(command_status.initialization_status) + "</td>" +
                    "</tr>"
                )

                if command_status.discovery_status is CommandStatusType.WARNING:
                    style = "style='background-color:{}'".format(color_warning)
                elif command_status.discovery_status is CommandStatusType.FAILURE:
                    style = "style='background-color:{}'".format(color_failure)
                elif command_status.discovery_status is CommandStatusType.SUCCESS:
                    style = "style='background-color:{}'".format(color_success)
                else:
                    # Typically UNKNOWN
                    style = "style='background-color:{}'".format(color_unknown)

                html_string += (
                    "<tr>" +
                    "<td> DISCOVERY </td>" +
                    "<td " + style + ">" + str(command_status.discovery_status) + "</td>" +
                    "</tr>"
                )

                if command_status.run_status is CommandStatusType.WARNING:
                    style = "style='background-color:{}'".format(color_warning)
                elif command_status.run_status is CommandStatusType.FAILURE:
                    style = "style='background-color:{}'".format(color_failure)
                elif command_status.run_status is CommandStatusType.SUCCESS:
                    style = "style='background-color:{}'".format(color_success)
                else:
                    # Typically UNKNOWN
                    style = "style='background-color:{}'".format(color_unknown)

                html_string += (
                    "<tr>" +
                    "<td> RUN </td>" +
                    "<td " + style + ">" + str(command_status.run_status) + "</td>" +
                    "</tr>" +
                    "</table>" +

                    "<p><b>Command Status Details (" +
                    str(command_status.get_log_count(phase=None, severity=CommandStatusType.WARNING)) + " warnings, " +
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
                            log_record.severity is CommandStatusType.FAILURE or show_all_log_messages:

                        if log_record.severity is CommandStatusType.WARNING:
                            style = "style='background-color:{}'".format(color_warning)
                        elif log_record.severity is CommandStatusType.FAILURE:
                            style = "style='background-color:{}'".format(color_failure)
                        elif log_record.severity is CommandStatusType.SUCCESS:
                            style = "style='background-color:{}'".format(color_success)
                        else:
                            style = "style='background-color:{}'".format(color_unknown)

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
                            log_record.severity is CommandStatusType.FAILURE or show_all_log_messages:

                        if log_record.severity is CommandStatusType.WARNING:
                            style = "style='background-color:{}'".format(color_warning)
                        elif log_record.severity is CommandStatusType.FAILURE:
                            style = "style='background-color:{}'".format(color_failure)
                        elif log_record.severity is CommandStatusType.SUCCESS:
                            style = "style='background-color:{}'".format(color_success)
                        else:
                            style = "style='background-color:{}'".format(color_unknown)

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
                # print("Have " + str(len(command_status.run_log_list)) + " log records")
                for log_record in command_status.run_log_list:
                    if log_record.severity is CommandStatusType.WARNING or \
                            log_record.severity is CommandStatusType.FAILURE or show_all_log_messages:

                        if log_record.severity is CommandStatusType.WARNING:
                            style = "style='background-color:{}'".format(color_warning)
                        elif log_record.severity is CommandStatusType.FAILURE:
                            style = "style='background-color:{}'".format(color_failure)
                        elif log_record.severity is CommandStatusType.SUCCESS:
                            style = "style='background-color:{}'".format(color_success)
                        else:
                            style = "style='background-color:{}'".format(color_unknown)

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

        # Make non-modal so the status window can be viewed at the same time as the main application.
        # - this allows errors to be fixed
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
        the existing GeoLayers, GeoMaps, Output Files, Properties, and Tables.

        Returns:
            None
        """

        # Call the specific functions for each output category
        # - Each call will also update the status information in the UI (counts, selected, etc.)
        logger = logging.getLogger(__name__)
        # GeoLayers
        # noinspection PyBroadException
        try:
            self.show_results_geolayers()
        except Exception:
            message = "Error showing GeoLayers in Results"
            logger.warning(message, exc_info=True)

        # GeoMaps
        # noinspection PyBroadException
        try:
            self.show_results_geomaps()
        except Exception:
            message = "Error showing GeoMaps in Results"
            logger.warning(message, exc_info=True)

        # GeoMapProjects
        # noinspection PyBroadException
        try:
            self.show_results_geomapprojects()
        except Exception:
            message = "Error showing GeoMapProjects in Results"
            logger.warning(message, exc_info=True)

        # Output Files
        # noinspection PyBroadException
        try:
            self.show_results_output_files()
        except Exception:
            message = "Error showing Output Files in Results"
            logger.warning(message, exc_info=True)

        # Properties
        # noinspection PyBroadException
        try:
            self.show_results_properties()
        except Exception:
            message = "Error showing Properties in Results"
            logger.warning(message, exc_info=True)

        # Tables
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

        # Display the GeoLayers from the run
        for geolayer in self.gp.geolayers:
            # Get the index of the next available row in the table. Add a new row to the table.
            new_row_index = self.results_GeoLayers_Table.rowCount()
            self.results_GeoLayers_Table.insertRow(new_row_index)

            col = -1
            # GeoLayerID
            # - should not be null
            col += 1
            self.results_GeoLayers_Table.setItem(new_row_index, col, QtWidgets.QTableWidgetItem(str(geolayer.id)))

            # Name
            # - should not be null
            col += 1
            self.results_GeoLayers_Table.setItem(new_row_index, col, QtWidgets.QTableWidgetItem(str(geolayer.name)))

            # Geometry
            # - should not be null
            col += 1
            geometry_type = None
            if geolayer.get_geometry() is not None:
                geometry_type = str(geolayer.get_geometry())
            else:
                geometry_type = "Unknown"
            self.results_GeoLayers_Table.setItem(new_row_index, col, QtWidgets.QTableWidgetItem(geometry_type))

            # Feature Count
            if geolayer.is_vector():
                # Display the feature count
                col += 1
                self.results_GeoLayers_Table.setItem(new_row_index, col,
                                                     QtWidgets.QTableWidgetItem(str(geolayer.get_feature_count())))
            elif geolayer.is_raster():
                # Display the row, column, and cell count in a formatted string
                col += 1
                self.results_GeoLayers_Table.setItem(new_row_index, col,
                                                     QtWidgets.QTableWidgetItem(str(geolayer.get_num_rows()) +
                                                                                " rows x " +
                                                                                str(geolayer.get_num_columns()) +
                                                                                " columns = " +
                                                                                str(geolayer.get_num_rows() *
                                                                                    geolayer.get_num_columns()) +
                                                                                " cells"))

            # CRS
            col += 1
            self.results_GeoLayers_Table.setItem(new_row_index, col,
                                                 QtWidgets.QTableWidgetItem(geolayer.get_crs_code()))

            # Source Format
            # - should not be null
            col += 1
            input_format = None
            if geolayer.input_format is None:
                input_format = "Unknown"
            else:
                input_format = geolayer.input_format
            self.results_GeoLayers_Table.setItem(new_row_index, col, QtWidgets.QTableWidgetItem(input_format))

            # Source Path
            # - should not be null
            col += 1
            input_path = None
            if geolayer.input_path is None:
                input_path = ""
            else:
                input_path = geolayer.input_path
            self.results_GeoLayers_Table.setItem(new_row_index, col, QtWidgets.QTableWidgetItem(input_path))

        self.results_GeoLayers_Table.resizeColumnsToContents()
        self.update_ui_status_results_geolayers()

    def show_results_geomaps(self) -> None:
        """
        Populates the Results / GeoMaps display.

        Returns:
            None
        """
        # Remove items from the Results GeoMaps table (from a previous run).
        self.results_GeoMaps_Table.setRowCount(0)

        # Display the GeoMaps from the run
        for geomap in self.gp.geomaps:
            # Get the index of the next available row in the table. Add a new row to the table.
            new_row_index = self.results_GeoMaps_Table.rowCount()
            self.results_GeoMaps_Table.insertRow(new_row_index)

            col = -1
            # GeoMapID
            col += 1
            self.results_GeoMaps_Table.setItem(new_row_index, col, QtWidgets.QTableWidgetItem(geomap.id))

            # Name
            col += 1
            self.results_GeoMaps_Table.setItem(new_row_index, col,
                                               QtWidgets.QTableWidgetItem(str(geomap.name)))

            # GeoLayerViewGroups (count)
            col += 1
            self.results_GeoMaps_Table.setItem(new_row_index, col,
                                               QtWidgets.QTableWidgetItem(str(len(geomap.geolayerviewgroups))))

            # GeoLayers (count)
            col += 1
            self.results_GeoMaps_Table.setItem(new_row_index, col,
                                               QtWidgets.QTableWidgetItem(str(len(geomap.geolayers))))

            # CRS
            col += 1
            # - the CRS might be null, but should not be
            self.results_GeoMaps_Table.setItem(new_row_index, col,
                                               QtWidgets.QTableWidgetItem(str(geomap.get_crs_code())))

        self.results_GeoMaps_Table.resizeColumnsToContents()
        self.update_ui_status_results_geomaps()

    def show_results_geomapprojects(self) -> None:
        """
        Populates the Results / GeoMapProjects display.

        Returns:
            None
        """
        # Remove items from the Results GeoMapProjects table (from a previous run).
        self.results_GeoMapProjects_Table.setRowCount(0)

        # Display the GeoMapProjects from the run
        for geomapproject in self.gp.geomapprojects:
            # Get the index of the next available row in the table. Add a new row to the table.
            new_row_index = self.results_GeoMapProjects_Table.rowCount()
            self.results_GeoMapProjects_Table.insertRow(new_row_index)

            col = -1
            # GeoMapProject
            col += 1
            self.results_GeoMapProjects_Table.setItem(new_row_index, col, QtWidgets.QTableWidgetItem(geomapproject.id))

            # Name
            col += 1
            self.results_GeoMapProjects_Table.setItem(new_row_index, col,
                                                      QtWidgets.QTableWidgetItem(str(geomapproject.name)))

            # GeoMap (count)
            col += 1
            self.results_GeoMapProjects_Table.setItem(new_row_index, col,
                                                      QtWidgets.QTableWidgetItem(str(len(geomapproject.geomaps))))

            # Description
            col += 1
            self.results_GeoMapProjects_Table.setItem(new_row_index, col,
                                                      QtWidgets.QTableWidgetItem(str(geomapproject.description)))

        self.results_GeoMapProjects_Table.resizeColumnsToContents()
        self.update_ui_status_results_geomapprojects()

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

                # Retrieve the output file type and set as the attribute for the File Type column.
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

            # Property Name
            self.results_Properties_Table.setItem(new_row_index, 0, QtWidgets.QTableWidgetItem(prop_name))

            # Property Value
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
            # TODO smalers 2020-11-14 is the following from Pandas?
            #self.results_Tables_Table.setItem(new_row_index, 1, QtWidgets.QTableWidgetItem(str(table.count_columns())))
            self.results_Tables_Table.setItem(new_row_index, 1, QtWidgets.QTableWidgetItem(
                str(table.get_number_of_columns())))

            # Retrieve the number of rows in the Table and set as the attribute for the Row Count column.
            # TODO smalers 2020-11-14 is the following from Pandas?
            #self.results_Tables_Table.setItem(new_row_index, 2, QtWidgets.QTableWidgetItem(str(table.count_rows())))
            self.results_Tables_Table.setItem(new_row_index, 2, QtWidgets.QTableWidgetItem(
                str(table.get_number_of_rows())))

        # Sort by Table ID
        # self.results_Tables_Table.sortByColumn(0, QtCore.Qt.AscendingOrder)

        # Update the results count and results' tables' labels to show that the results were populated.
        self.update_ui_status_results_tables()

    def ui_action_command_list_double_click(self, row: int) -> None:
        """
        Handle a double click on the command list.
        This is the same as right-click Edit.

        Arg:
            row (int): Command list row (0+).

        Returns:
            None
        """
        self.edit_existing_command()

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
            self.menu_item_edit_command.triggered.connect(self.edit_existing_command)

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
                self.command_CommandListWidget.event_handler_increase_indent_button_clicked)

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
            self.menu_item_convert_to_command.triggered.connect(
                self.ui_action_command_list_right_click_convert_to_command)
            self.menu_item_convert_from_command = self.rightClickMenu_Commands.addAction(
                "Convert selected command(s) from # comments")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
            # noinspection PyUnresolvedReferences
            self.menu_item_convert_from_command.triggered.connect(
                self.ui_action_command_list_right_click_convert_from_command)

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

        # self.gp_model.update_command_list_ui()
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

    def ui_action_edit_format(self) -> None:
        """
        Format the commands to auto-indent based on If and For blocks.

        Returns:
            None
        """
        pass

        message = "The format tool is not yet enabled.  When enabled, it will auto-indent the commands."
        qt_util.warning_message_box(message)
        return

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
            tab = "    "
            tab2 = tab + tab
            properties = ""

            program_name = app_util.get_property('ProgramName')
            version = app_util.get_property('ProgramVersion')
            version_date = app_util.get_property('ProgramVersionDate')
            user_name = os.getlogin()
            current_date = datetime.datetime.now()
            # TODO @jurentie get appropriate timezone if possible
            current_date = current_date.strftime("%c %Z")
            host = platform.uname()[1]
            working_dir_start = os.getcwd()
            program_home = app_util.get_property('ProgramHome')
            program_resources_path = app_util.get_property('ProgramResourcesPath')
            command_line = ""
            for i in range(len(sys.argv)):
                if i > 0:
                    command_line += " "
                command_line += sys.argv[i]

            properties += ("GeoProcessor Application and Session Information:\n" +
                           tab + "Program Name: {} {} {}\n".format(program_name, version, version_date) +
                           tab + "User Name: {}\n".format(user_name) +
                           tab + "Date: {}\n".format(current_date) +
                           tab + "Host: {}\n".format(host) +
                           tab + "Working Directory (from software start): {}\n".format(working_dir_start) +
                           tab + "Last Saved Command File: {}\n".format(self.saved_file) +
                           tab + "Working Directory (from processor): {}\n".format(self.gp.get_property('WorkingDir')) +
                           tab + "Working Directory, native (from processor): {}\n".
                           format(self.gp.get_property('WorkingDirNative')) +
                           tab + "Command: {}\n".format(command_line) +
                           tab + 'Program Home: {}\n'.format(program_home) +
                           tab + 'Program Resources Path: {}\n'.format(program_resources_path) +
                           tab + "Process ID: {}\n".format(os.getpid()) +
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
                           tab + "Type: {}\n".format(os_type) +
                           tab + "Distribution: {}\n".format(os_distro) +
                           tab + "Name (platform.uname[0] and [2]): {}\n".format(operating_system) +
                           tab + "Version (platform.uname[3]): {}\n".format(version) )
            if is_windows:
                properties += (tab + "System Architecture (os.environ['MSYSTEM_CARCH']): {}\n".format(architecture))
            else:
                # Linux variant
                # - TODO smalers 2018-12-31 need to standardize
                properties += (tab + "System Architecture: {}\n".format(architecture))

            properties += tab + "\n" + tab + "Environment Variables (os.environ):\n"
            for env_var in os.environ.keys():
                properties += "{}{}={}\n".format(tab2, env_var, os.environ[env_var])

            # Add unsorted path, each part on a separate line
            path = ''
            for path_item in os.environ['PATH'].split(os.pathsep):
                path += "{}{}\n".format(tab2, path_item)

            # Add sorted path, each part on a separate line
            path_sorted = ''
            for path_item in os.environ['PATH'].split(os.pathsep):
                path_sorted += "{}{}\n".format(tab2, path_item)

            properties += (
                tab + "\n" + tab +
                "PATH Environment Variable, unsorted, indicates order of finding a program:\n" + path +
                tab + "\n" + tab + "PATH Environment Variable, sorted, useful for troubleshooting:\n" + path_sorted)

            properties += "\n"

            # Replace newlines in system version
            system_version = sys.version.replace("\r\n", " ").replace("\n", " ")
            system_path = ''
            system_path_sorted = ''
            for path_item in sys.path:
                system_path += str(path_item) + '\n' + tab2
            for path_item in sorted(sys.path):
                system_path_sorted += str(path_item) + '\n' + tab2

            # Python properties

            try:
                python_home = os.environ['PYTHONHOME']
            except KeyError:
                python_home = "not set"

            properties += ("Python Information:\n" +
                           tab + 'Python Executable (sys.executable): {}\n'.format(sys.executable) +
                           tab + 'Python Version (sys.version): {}\n'.format(system_version) +
                           tab + 'Python Bit Size: {}\n'.format(8*struct.calcsize("P")) +
                           tab + 'PYTHONHOME Environment Variable: {}\n'.format(python_home) +
                           tab + 'Python Path (sys.path), unsorted, which indicates import search order:\n' +
                           tab2 + system_path + "\n" +
                           tab + 'Python Path (sys.path), sorted, useful for troubleshooting:\n' +
                           tab2 + system_path_sorted + "\n")

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
            # - use str() to ensure that None values won't cause problems
            if qgis_install_type == "Unknown":
                # QGIS does not appear to be used at runtime so provide minimal information
                properties += (
                            "QGIS Information:\n" +
                            tab + "QGIS Installation Type: {}\n".format(qgis_install_type) +
                            tab + "The GeoProcessor testing framework is being used without QGIS dependencies.\n" +
                            "\n"
                )
            else:
                qgis_root = ""
                properties += (
                               "QGIS Information:\n" +
                               tab + "QGIS Installation Type: {}\n".format(qgis_install_type) +
                               tab + "QGIS Installation Folder: {}\n".format(qgis_install_folder) +
                               tab + "QGIS Version: {}\n".format(qgis_version) +
                               tab + "QGIS Environment Variables (set up by QGIS and GeoProcessor startup scripts):\n" +
                               tab2 + "GDAL_DATA: {}\n".format(os.environ.get('GDAL_DATA')) +
                               tab2 + "GDAL_DRIVER_PATH: {}\n".format(os.environ.get('GDAL_DRIVER_PATH')) +
                               tab2 + "GDAL_FILENAME_IS_UTF8: {}\n".format(os.environ.get('GDAL_FILENAME_IS_UTF8')) +
                               tab2 + "GEOTIFF_CSV: {}\n".format(os.environ.get('GEOTIFF_CSV')) +
                               tab2 + "OSGEO4W_ROOT: {}\n".format(os.environ.get('OSGEO4W_ROOT')) +
                               tab2 + "O4W_QT_BINARIES: {}\n".format(os.environ.get('O4W_QT_BINARIES')) +
                               tab2 + "O4W_QT_DOC: {}\n".format(os.environ.get('O4W_QT_DOC')) +
                               tab2 + "O4W_QT_HEADERS: {}\n".format(os.environ.get('O4W_QT_HEADERS')) +
                               tab2 + "O4W_QT_LIBRARIES: {}\n".format(os.environ.get('O4W_QT_LIBRARIES')) +
                               tab2 + "O4W_QT_PLUGINS: {}\n".format(os.environ.get('O4W_QT_PLUGINS')) +
                               tab2 + "O4W_QT_PREFIX: {}\n".format(os.environ.get('O4W_QT_PREFIX')) +
                               tab2 + "O4W_QT_TRANSLATIONS: {}\n".format(os.environ.get('O4W_QT_TRANSLATION')) +
                               tab2 + "PYTHONHOME: {}\n".format(os.environ.get('PYTHONHOME')) +
                               tab2 + "QGIS_PREFIX_PATH: {}\n".format(os.environ.get('QGIS_PREFIX_PATH')) +
                               tab2 + "QT_PLUGIN_PATH: {}\n".format(os.environ.get('QT_PLUGIN_PATH')) +
                               tab2 + "VSI_CACHE: {}\n".format(os.environ.get('VSI_CACHE')) +
                               tab2 + "VSI_CACHE_SIZE: {}\n".format(os.environ.get('VSI_CACHE_SIZE')) +
                               "\n")

            # Add information for Qt

            properties += (
                 "Qt Information (used for user interface):\n" +
                 tab + "Qt Version: {}\n".format(QtCore.QT_VERSION_STR) +
                 tab + "SIP Version: {}\n".format(SIP_VERSION_STR) +
                 tab + "PyQt Version: {}\n".format(Qt.PYQT_VERSION_STR) +
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

        # Set opened file to false since opening a new command file
        self.opened_command_file = False

        # Clear commands from geoprocessor
        # - this retains the command file name
        self.gp_model.clear_all_commands()

        # Save a new backup of commands (will be empty list)
        self.command_list_backup.update_command_list(self.gp.commands)

        # Set the title for the main window
        self.ui_set_main_window_title("commands not saved")

    def ui_action_results_geolayers_open_attributes(self) -> None:
        """
        Create an attributes window to be opened when user clicks on GeoLayers.

        Returns:
            None
        """
        logger = logging.getLogger(__name__)
        # noinspection PyBroadException
        try:
            # Get GeoLayer from Table
            selected_row_index = self.results_GeoLayers_Table.currentRow()
            selected_geolayer = self.gp.geolayers[selected_row_index]

            # Create attributes window dialog
            self.open_dialog(existing_dialog=GeoLayerAttributesQDialog(selected_geolayer))
        except Exception:
            message = "Error opening attributes window.  See the log file."
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

    def ui_action_results_tables_view_table(self) -> None:
        """
        Create a window to view a table.

        Returns:
            None
        """
        logger = logging.getLogger(__name__)
        # noinspection PyBroadException
        try:
            # Get the first selected table
            selected_row_index = self.results_Tables_Table.selectedIndexes()[0].row()
            logger.info("Selected table index = {}".format(selected_row_index))
            selected_table = self.gp.tables[selected_row_index]

            # Create attributes window dialog
            self.open_dialog(existing_dialog=TableQDialog(selected_table))
            return
        except Exception:
            message = "Error opening table window.  See the log file."
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
            # cmd_filepath = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", last_opened_folder)[0]
            title = "Open GeoProcessor Command File"
            # Can't use full GeoProcessor below or choice is not fully visible
            filters = "GP command files (*.gp);;All files (*)"
            cmd_filepath = QtWidgets.QFileDialog.getOpenFileName(self, title, last_opened_folder, filters)[0]
            if not cmd_filepath:
                return False
        else:
            # A command file name has been selected from the history list in File / Open
            logger.info("In ui_action_open_command_file, request to open command file " + filename)
            cmd_filepath = filename

        # Read the command file in GeoProcessor.
        # The previous command file lines in the UI are discarded.
        try:
            # Read using the GeoProcessorModel that is managed by the command list.
            self.command_CommandListWidget.gp_model.read_command_file(cmd_filepath)
            # Create a backup of the commands as text to allow checking for modifications.
            self.command_list_backup.update_command_list(self.gp.commands)
        except FileNotFoundError:
            # The file should exist but may have been deleted outside of the UI
            # - TODO smalers 2019-01-19 may automatically remove such files,
            #   or leave assuming the user will rename, move the file back again.
            message = 'Selected command file does not exist (maybe deleted or renamed?):\n"' + cmd_filepath + '"'
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
            # Return so history is not changed to include a file that does not exist
            return False

        # Update the error status for initialization run mode
        self.command_CommandListWidget.update_ui_command_list_errors(command_phase_type=CommandPhaseType.INITIALIZATION)
        # And refresh display of the messages
        self.command_CommandListWidget.update_ui_status_commands()

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

    def ui_action_results_geolayers_open_map_window(self) -> None:
        """
        Open a map window dialog box that displays the map layers from the selected GeoLayers.

        Returns:
            None
        """
        logger = logging.getLogger(__name__)

        # noinspection PyBroadException
        try:
            # Retrieve QgsVectorLayers from selected geolayers
            # - this retrieves selected indices
            # selected_rows = self.results_GeoLayers_Table.selectedIndexes()
            selected_rows = qt_util.get_table_rows_from_indexes(self.results_GeoLayers_Table.selectedIndexes())
            selected_geolayers = []
            for row in selected_rows:
                geolayer = self.gp.geolayers[row]
                if geolayer.is_vector():
                    logger.info("Appending vector layer \"{}\" [{}] for map ".format(geolayer.id, row))
                elif geolayer.is_raster():
                    logger.info("Appending raster layer \"{}\" [{}] for map ".format(geolayer.id, row))
                selected_geolayers.append(geolayer.qgs_layer)

            # Create attributes window dialog
            self.open_dialog(existing_dialog=GeoLayerMapQDialog(selected_geolayers))
            return
        except Exception:
            message = "Error opening map window.  See the log file."
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

    def ui_action_results_geolayers_right_click(self, q_pos: int) -> None:
        """
        On right click display a popup menu that allows viewing the layers in a map or view attributes.
        Upon selecting an item in the map, a corresponding popup window will be displayed.

        Args:
            q_pos (int): Position of mouse when right clicking on a GeoLayer from the output table.

        Returns:
            None
        """

        # Create the right click QMenu
        self.rightClickMenu_Results_GeoLayers = QtWidgets.QMenu()

        # Add possible actions being Open Map or Attributes
        menu_item_map_command = self.rightClickMenu_Results_GeoLayers.addAction("Open Map")
        menu_item_attributes = self.rightClickMenu_Results_GeoLayers.addAction("Attributes")

        # Connect actions to the tooltip options
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        menu_item_map_command.triggered.connect(self.ui_action_results_geolayers_open_map_window)
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        menu_item_attributes.triggered.connect(self.ui_action_results_geolayers_open_attributes)

        # Using the position of the mouse on right click decide where the tooltip should
        # be displayed
        parent_pos = self.results_GeoLayers_Table.mapToGlobal(QtCore.QPoint(0, 0))
        self.rightClickMenu_Results_GeoLayers.move(parent_pos + q_pos)

        # Show the tooltip
        self.rightClickMenu_Results_GeoLayers.show()

    def ui_action_results_outputfiles_open_app(self, as_text: bool = False) -> None:
        """
        Open the output file by running the default application for the file extension.

        Returns:
            None
        """
        logger = logging.getLogger(__name__)

        # noinspection PyBroadException
        try:
            # Get the first selected file
            # - this retrieves selected indices
            # selected_rows = self.results_GeoLayers_Table.selectedIndexes()
            selected_rows = qt_util.get_table_rows_from_indexes(self.results_OutputFiles_Table.selectedIndexes())
            for row in selected_rows:
                # Get the output file
                output_file_path = self.results_OutputFiles_Table.itemAt(row, 0).text()
                logger.info("Output file item from table: {}".format(output_file_path))
                os_util.run_default_app(output_file_path, as_text=as_text)
                # Only show the first selected row
                # - TODO smalers 2020-07-22 evaluate whether multiple files should be provided to one application
                break

        except Exception:
            message = "Error opening output file {}.  The file extension may not be associated with a program. "\
                "See the log file.".format(output_file_path)
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

    def ui_action_results_outputfiles_openastext_app(self) -> None:
        """
        Open the output file as text by running the default application for the file extension.

        Returns:
            None
        """
        self.ui_action_results_outputfiles_open_app(as_text=True)

    def ui_action_results_outputfiles_right_click(self, q_pos: int) -> None:
        """
        On right click display a menu to view the output file.
        Then start the appropriate application.

        Args:
            q_pos (int): Position of mouse when right clicking on a GeoLayer from
                the output table.

        Returns:
            None
        """

        # Create the right click QMenu
        self.rightClickMenu_Results_OutputFiles = QtWidgets.QMenu()

        # Add possible actions
        outputfiles_item_open = self.rightClickMenu_Results_OutputFiles.addAction("Open")
        outputfiles_item_openastext = self.rightClickMenu_Results_OutputFiles.addAction("Open as text")

        # Connect actions to the tooltip options
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        outputfiles_item_open.triggered.connect(self.ui_action_results_outputfiles_open_app)
        # noinspection PyUnresolvedReferences
        outputfiles_item_openastext.triggered.connect(self.ui_action_results_outputfiles_openastext_app)

        # Using the position of the mouse on right click decide where the tooltip should
        # be displayed
        parent_pos = self.results_OutputFiles_Table.mapToGlobal(QtCore.QPoint(0, 0))
        self.rightClickMenu_Results_OutputFiles.move(parent_pos + q_pos)

        # Show the tooltip
        self.rightClickMenu_Results_OutputFiles.show()

    def ui_action_results_tables_right_click(self, q_pos: int) -> None:
        """
        On right click display a popup menu that allows viewing the table.
        Upon selecting an item in the map, a corresponding popup window will be displayed.

        Args:
            q_pos (int): Position of mouse when right clicking on a GeoLayer from the output table.

        Returns:
            None
        """

        # Create the right click QMenu
        self.rightClickMenu_Results_Tables = QtWidgets.QMenu()

        # Add possible actions being Open Map or Attributes
        menu_item_attributes = self.rightClickMenu_Results_Tables.addAction("View")

        # Connect actions to the tooltip options
        # Use the following because triggered.connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        menu_item_attributes.triggered.connect(self.ui_action_results_tables_view_table)

        # Using the position of the mouse on right click decide where the tooltip should
        # be displayed
        parent_pos = self.results_Tables_Tab.mapToGlobal(QtCore.QPoint(0, 0))
        self.rightClickMenu_Results_Tables.move(parent_pos + q_pos)

        # Show the tooltip
        self.rightClickMenu_Results_Tables.show()

    def ui_action_save_commands(self) -> None:
        """
        Saves the commands to a previously saved file location (overwrite).

        Returns:
            None
        """

        if self.saved_file is None:
            # If there is not a previously saved file location, save the file with the ui_action_save_command_as
            # function, which will prompt for the file name.
            self.ui_action_save_commands_as()

        else:
            # There is a previously saved file location, continue.

            # A list to hold each command as a separate string.
            list_of_cmds = []

            # Get the command list as strings
            for i in range(len(self.gp.commands)):
                # Add the command string text ot the list_of_cmds list.
                list_of_cmds.append(self.gp.commands[i].command_string)

            # Join all of the command strings together (separated by a line break).
            all_commands_string = '\n'.join(list_of_cmds)

            # Write the commands to the previously saved file location (overwrite).
            file = open(self.saved_file, 'w')
            file.write(all_commands_string)
            file.close()

            # Update command file history list in GUI
            self.ui_init_file_open_recent_files()

        # Successfully saved so record the new saved command file in the command list backup.
        self.command_list_backup.update_command_list(self.gp.commands)

        # Update the title so that "modified" is not shown
        self.update_ui_main_window_title()

    def ui_action_save_commands_as(self) -> None:
        """
        Saves the commands to a file.

        Returns:
            None if no file name specified.
        """

        # A list to hold each command as a separate string.
        list_of_cmds = []

        # Get the command list as strings
        for i in range(len(self.gp.commands)):
            # Add the command string text ot the list_of_cmds list.
            list_of_cmds.append(self.gp.commands[i].command_string)

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

        # Open a browser for the user to select a location and filename to save the command file.
        # Set the most recent file save location.
        new_saved_file = QtWidgets.QFileDialog.getSaveFileName(d, 'Save Command File As', last_opened_folder)[0]

        if new_saved_file == "":
            # Canceled out of save.  Don't do anything.
            return

        # Write the commands to the file.
        file = open(new_saved_file, 'w')
        file.write(all_commands_string)
        file.close()

        # Reset the command file name after successful write.
        self.saved_file = new_saved_file

        # The command file has now been saved.
        self.command_file_saved = True

        # Save the command file name in the command file history.
        self.app_session.push_history(self.saved_file)

        # Update the recent files in the File... Open menu, for the next menu access.
        self.ui_init_file_open_recent_files()

        # Successfully saved so record the new saved command file in the command list backup.
        self.command_list_backup.update_command_list(self.gp.commands)

        # Update the title so that "modified" is not shown
        self.update_ui_main_window_title()

    def ui_action_view_command_file_diff(self) -> None:
        """
        Show the difference between the current commands and the saved on disk command file.

        Returns:
            None
        """
        pass

        logger = logging.getLogger(__name__)

        # If the diff tool is not configured, provide information.
        # Prop prop = IOUtil.getProp("DiffProgram")
        prop = "xxx"
        # TODO smalers 2020-03-10 for now hard-code the path to KDiff3 - a repo issue has been added to
        # - dummy in code below to mimic what would happen
        # implement an application configuration file.
        diff_program = None
        if prop is not None:
            # diff_program = "/C/Program Files/KDiff3/kdiff3.exe"
            diff_program = Path("C:/Program Files/KDiff3/kdiff3.exe")
        else:
            message = "The visual diff program has not been configured in the TSTool configuration file.\n" \
                "Define the \"DiffProgram\" property as the path to a visual diff program, for example kdiff3\n" \
                "Cannot show the command file difference."
            qt_util.warning_message_box(message)
            return

        p = Path(diff_program)
        if p.exists():
            # Diff program exists so save a temporary file with UI commands and then compare with file version.
            # Run the diff program on the input and output files
            # (they should have existed because the button will have been disabled if not)
            file1_path = None
            if self.saved_file is not None:
                file1_path = Path(self.saved_file)
            if file1_path is None:
                message = "No command file was previously read or saved.  The commands being edited are new."
                qt_util.warning_message_box(message)
                return
            # Write the commands to a temporary file.
            # First construct a temporary filename that makes sense to users.
            temp_folder = tempfile.gettempdir()
            file2_path = Path(temp_folder) / "gp-commands.gp"
            list_of_cmds = []
            try:
                # Get the command list as strings
                for i in range(len(self.gp.commands)):
                    # Add the command string text ot the list_of_cmds list.
                    list_of_cmds.append(self.gp.commands[i].command_string)

                # Join all of the command strings together (separated by a line break).
                all_commands_string = '\n'.join(list_of_cmds)

                # Write the commands to the previously saved file location (overwrite).
                file = open(file2_path, 'w')
                file.write(all_commands_string)
                file.close()
            except Exception:
                message = "Error saving commands to temporary file for diff."
                logger.warning(message, exc_info=True)
                qt_util.warning_message_box(message)
                return

            # Run the diff program
            # noinspection PyBroadException
            try:
                # Files must be Platform-specific to work with with called program
                # TODO smalers 2020-03-10 the following did not work
                logger.info("diff_program=" + str(diff_program))
                logger.info("file1_path=" + str(file1_path))
                logger.info("file2_path=" + str(file2_path))
                # args = [diff_program, file1_path, file2_path]
                command_line = '"' + str(diff_program) + '" "' + str(file1_path) + '" "' + str(file2_path) + '"'
                args = shlex.split(command_line)
                # use_command_shell = True   # Use shell to handle spaces in paths
                use_command_shell = False  # Seems to work OK with command line parsed above
                # env_dict = None
                # capture_output = None
                # stdout = None
                # stderr = None
                # timeout = 0
                do_thread = True
                if do_thread:
                    # The following runs the diff tool as a separate thread
                    subprocess.Popen(args, shell=use_command_shell)
                else:
                    # completed_process = subprocess.run(args, shell=use_command_shell, env=env_dict, timeout=timeout,
                    #                                   capture_output=capture_output, stdout=stdout, stderr=stderr)
                    # The following runs but not threaded so it hangs the UI until the diff tool exits
                    completed_process = subprocess.run(args, shell=use_command_shell)
            except Exception:
                message = "Error running diff program."
                logger.warning(message, exc_info=True)
                qt_util.warning_message_box(message)
        else:
            message = "Visual diff program does not exist:  " + diff_program
            qt_util.warning_message_box(message)

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
        # noinspection PyBroadException
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
        # logger = logging.getLogger(__name__)
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

    def update_command_list_backup(self) -> None:
        """
        Update the internal backup of the previous commands strings that were saved or read,
        from the data model command list.

        Returns:
            None
        """
        self.command_list_backup.update_command_list(self.gp.commands)

    def update_ui_main_window_title(self) -> None:
        """
        Update the main window title to reflect that the command file has been modified.

        Returns:
            None
        """
        if self.saved_file is None:
            # New command file has not been saved so no file name to display.
            window_title = "GeoProcessor - commands not saved"
        else:
            # Command file has a name and may or may not have been modified.
            if self.command_list_backup.command_list_modified(self.gp.commands):
                # The command file has been modified
                window_title = "GeoProcessor - " + self.saved_file + " (modified)"
            else:
                # The command file has not been modified.
                window_title = "GeoProcessor - " + self.saved_file

        # Set the window title
        self.setWindowTitle(window_title)

    def update_ui_status(self) -> None:
        """
        Update the UI status by checking data and setting various status information.
        This does not update the UI window title.

        Returns:
            None
        """
        self.update_ui_status_commands_popup()
        self.update_ui_status_results_geolayers()
        self.update_ui_status_results_geomaps()
        self.update_ui_status_results_geomapprojects()
        self.update_ui_status_results_output_files()
        self.update_ui_status_results_properties()
        self.update_ui_status_results_tables()

    def update_ui_status_commands_popup(self) -> None:
        """
        Update the status of the command popup menu and tool buttons (indent, etc.).

        Returns:

        """
        # Adjust whether menus are enabled or disabled based on the state of the data
        num_commands = len(self.gp)
        selected_indices = self.command_CommandListWidget.get_selected_indices()
        num_selected = len(selected_indices)

        # The popup menu will not be populated until one right-click has occurred, so check for None once
        if num_selected > 0:
            # Some commands are selected
            if self.menu_item_show_command_status is not None:
                self.menu_item_show_command_status.setEnabled(True)
                self.menu_item_edit_command.setEnabled(True)
                self.menu_item_cut_commands.setEnabled(True)
                self.menu_item_copy_commands.setEnabled(True)
                self.menu_item_deselect_all_commands.setEnabled(True)
                self.menu_item_increase_indent_command.setEnabled(True)
                self.menu_item_decrease_indent_command.setEnabled(True)
                self.menu_item_convert_from_command.setEnabled(True)
                self.menu_item_convert_to_command.setEnabled(True)

            self.increase_indent_button.setEnabled(True)
            self.decrease_indent_button.setEnabled(True)
        else:
            # No commands are selected
            if self.menu_item_show_command_status is not None:
                self.menu_item_show_command_status.setEnabled(False)
                self.menu_item_edit_command.setEnabled(False)
                self.menu_item_cut_commands.setEnabled(False)
                self.menu_item_copy_commands.setEnabled(False)
                self.menu_item_deselect_all_commands.setEnabled(False)
                self.menu_item_increase_indent_command.setEnabled(False)
                self.menu_item_decrease_indent_command.setEnabled(False)
                self.menu_item_convert_from_command.setEnabled(False)
                self.menu_item_convert_to_command.setEnabled(False)

            self.increase_indent_button.setEnabled(False)
            self.decrease_indent_button.setEnabled(False)

        if self.menu_item_paste_commands is not None:
            if len(self.commands_cut_buffer) > 0:
                # The cut/copy/paste command list has some commands
                self.menu_item_paste_commands.setEnabled(True)
            else:
                # Nothing available to cut/copy/paste
                self.menu_item_paste_commands.setEnabled(False)

        if self.menu_item_select_all_commands is not None:
            if num_commands == num_selected:
                self.menu_item_select_all_commands.setEnabled(False)
            else:
                self.menu_item_select_all_commands.setEnabled(True)

        if self.menu_item_delete_commands is not None:
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

    def update_ui_status_results_geomaps(self) -> None:
        """
        Update the UI status for Results / GeoMaps area.

        Returns:
            None
        """
        # Count the total and selected number of rows within the GeoMaps table. Update the label to reflect counts.
        row_num = str(self.results_GeoMaps_Table.rowCount())
        selected_rows = str(len(self.results_GeoMaps_Table.selectedIndexes()))
        self.results_GeoMaps_GroupBox.setTitle("GeoMaps ({} GeoMaps, {} selected)".format(row_num, selected_rows))

    def update_ui_status_results_geomapprojects(self) -> None:
        """
        Update the UI status for Results / GeoMapProjects area.

        Returns:
            None
        """
        # Count the total and selected number of rows within the GeoMapProjets table.
        # Update the label to reflect counts.
        row_num = str(self.results_GeoMapProjects_Table.rowCount())
        selected_rows = str(len(self.results_GeoMapProjects_Table.selectedIndexes()))
        self.results_GeoMapProjects_GroupBox.setTitle("GeoMapProjects ({} GeoMapProjects, {} selected)".format(
            row_num, selected_rows))

    def update_ui_status_results_output_files(self) -> None:
        """
        Update the UI status for Results / Output Files area.

        Returns:
            None
        """
        # Count the total and selected number of rows within the Output Files table. Update the label to reflect counts.
        row_num = str(self.results_OutputFiles_Table.rowCount())
        selected_rows = str(len(self.results_OutputFiles_Table.selectedIndexes()))
        self.results_OutputFiles_GroupBox.setTitle(
            "Output Files ({} Output Files, {} selected)".format(row_num, selected_rows))

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
        selected_rows = str(len(self.results_Properties_Table.selectedIndexes()))
        self.results_Properties_GroupBox.setTitle(
            "Properties ({} Properties, {} selected)".format(row_num, selected_rows))

        self.results_Properties_Table.setColumnWidth(2, 0)

    def update_ui_status_results_tables(self) -> None:
        """
        Update the UI status for Results / Tables area.

        Returns:
            None
        """
        # Count the total and selected number of rows within the Tables table. Update the label to reflect counts.
        row_num = str(self.results_Tables_Table.rowCount())
        selected_rows = str(len(set(index.row() for index in self.results_Tables_Table.selectedIndexes())))
        if selected_rows != 1:
            self.results_Tables_GroupBox.setTitle("Tables ({} Tables, {} selected)".format(row_num, selected_rows))
        else:
            self.results_Tables_GroupBox.setTitle("Tables ({} Table, {} selected)".format(row_num, selected_rows))

    # TODO smalers 2020-01-18 does not seem to be called by anything - this has been moved to CommandListWidget
    def x_delete_numbered_list_item(self, index: int) -> None:
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

    # TODO smalers 2020-03-13 a similar method exists in CommandListWidget and should be used directly
    def x_update_ui_commands_list(self) -> None:
        """
        Once commands have been run. Loop through and check for any errors or warnings.

        Returns:
            None
        """
        self.command_CommandListWidget.update_ui_command_list_errors()

        old_logic = False
        if old_logic:
            gp = self.gp
            count = len(self.command_CommandListWidget)
            for i in range(0, count):
                # TODO jurentie may update to handle Discovery errors once implemented in GeoProcessor
                command_status = gp.commands[i].command_status.run_status
                if command_status is CommandStatusType.FAILURE:
                    self.command_CommandListWidget.numbered_list_error_at_row(i)
                    self.command_CommandListWidget.gutter_error_at_row(i)
                elif command_status is CommandStatusType.WARNING:
                    self.command_CommandListWidget.numbered_list_warning_at_row(i)
                    self.command_CommandListWidget.gutter_warning_at_row(i)
