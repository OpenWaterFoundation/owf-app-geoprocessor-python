# -*- coding: utf-8 -*-
# GeoProcessorUI_Design - used with Qt Designer
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

# THIS CLASS IS NOT CURRENTLY USED BECAUSE UI COMPONENTS ARE MANUALLY CODED.
# - Qt Designer is useful for some things but not complex GeoProcessor code.

# Form implementation generated from reading ui file 'main-window-draft2.ui'
#
# Created: Tue May 08 10:21:50 2018
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

try:
    # _fromUtf8 = QtCore.QString.fromUtf8
    _fromUtf8 = lambda s: s
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1038, 834)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("MS Shell Dlg 2"))
        MainWindow.setFont(font)
        MainWindow.setWindowOpacity(1.0)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.Commands_GroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.Commands_GroupBox.setObjectName(_fromUtf8("Commands_GroupBox"))
        self.gridLayout = QtWidgets.QGridLayout(self.Commands_GroupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.Commands_RunAll_Button = QtWidgets.QPushButton(self.Commands_GroupBox)
        self.Commands_RunAll_Button.setEnabled(False)
        self.Commands_RunAll_Button.setObjectName(_fromUtf8("Commands_RunAll_Button"))
        self.gridLayout.addWidget(self.Commands_RunAll_Button, 1, 1, 1, 1)
        self.Commands_Clear_Button = QtWidgets.QPushButton(self.Commands_GroupBox)
        self.Commands_Clear_Button.setEnabled(False)
        self.Commands_Clear_Button.setObjectName(_fromUtf8("Commands_Clear_Button"))
        self.gridLayout.addWidget(self.Commands_Clear_Button, 1, 3, 1, 1)
        self.Commands_RunSelected_Button = QtWidgets.QPushButton(self.Commands_GroupBox)
        self.Commands_RunSelected_Button.setEnabled(False)
        self.Commands_RunSelected_Button.setDefault(False)
        self.Commands_RunSelected_Button.setFlat(False)
        self.Commands_RunSelected_Button.setObjectName(_fromUtf8("Commands_RunSelected_Button"))
        self.gridLayout.addWidget(self.Commands_RunSelected_Button, 1, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.Commands_List = QtWidgets.QListWidget(self.Commands_GroupBox)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("MS Shell Dlg 2"))
        self.Commands_List.setFont(font)
        self.Commands_List.setAutoScroll(True)
        self.Commands_List.setDragDropOverwriteMode(False)
        self.Commands_List.setAlternatingRowColors(True)
        self.Commands_List.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.Commands_List.setProperty("isWrapping", False)
        self.Commands_List.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.Commands_List.setWordWrap(True)
        self.Commands_List.setSelectionRectVisible(False)
        self.Commands_List.setObjectName(_fromUtf8("Commands_List"))
        self.Commands_List.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.gridLayout.addWidget(self.Commands_List, 0, 0, 1, 4)
        self.gridLayout_2.addWidget(self.Commands_GroupBox, 1, 0, 1, 6)
        self.Results_GroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.Results_GroupBox.setObjectName(_fromUtf8("Results_GroupBox"))
        self.verticalLayout = QtWidgets.QVBoxLayout(self.Results_GroupBox)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.Results_Tab_Widget = QtWidgets.QTabWidget(self.Results_GroupBox)
        self.Results_Tab_Widget.setObjectName(_fromUtf8("Results_Tab_Widget"))
        self.Results_GeoLayers_Tab = QtWidgets.QWidget()
        self.Results_GeoLayers_Tab.setAcceptDrops(False)
        self.Results_GeoLayers_Tab.setObjectName(_fromUtf8("Results_GeoLayers_Tab"))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.Results_GeoLayers_Tab)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.Results_GeoLayers_GroupBox = QtWidgets.QGroupBox(self.Results_GeoLayers_Tab)
        self.Results_GeoLayers_GroupBox.setObjectName(_fromUtf8("Results_GeoLayers_GroupBox"))
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.Results_GeoLayers_GroupBox)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.Results_GeoLayers_Table = QtWidgets.QTableWidget(self.Results_GeoLayers_GroupBox)
        self.Results_GeoLayers_Table.setObjectName(_fromUtf8("Results_GeoLayers_Table"))
        self.Results_GeoLayers_Table.setColumnCount(5)
        self.Results_GeoLayers_Table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.Results_GeoLayers_Table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.Results_GeoLayers_Table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.Results_GeoLayers_Table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.Results_GeoLayers_Table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.Results_GeoLayers_Table.setHorizontalHeaderItem(4, item)
        self.Results_GeoLayers_Table.horizontalHeader().setCascadingSectionResizes(False)
        self.Results_GeoLayers_Table.horizontalHeader().setDefaultSectionSize(200)
        self.Results_GeoLayers_Table.horizontalHeader().setSortIndicatorShown(True)
        self.Results_GeoLayers_Table.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_5.addWidget(self.Results_GeoLayers_Table)
        self.verticalLayout_2.addWidget(self.Results_GeoLayers_GroupBox)
        self.Results_Tab_Widget.addTab(self.Results_GeoLayers_Tab, _fromUtf8(""))
        self.Results_Tables_Tab = QtWidgets.QWidget()
        self.Results_Tables_Tab.setObjectName(_fromUtf8("Results_Tables_Tab"))
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.Results_Tables_Tab)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.Results_Tables_GroupBox = QtWidgets.QGroupBox(self.Results_Tables_Tab)
        self.Results_Tables_GroupBox.setObjectName(_fromUtf8("Results_Tables_GroupBox"))
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.Results_Tables_GroupBox)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.Results_Tables_Table = QtWidgets.QTableWidget(self.Results_Tables_GroupBox)
        self.Results_Tables_Table.setObjectName(_fromUtf8("Results_Tables_Table"))
        self.Results_Tables_Table.setColumnCount(4)
        self.Results_Tables_Table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.Results_Tables_Table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.Results_Tables_Table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.Results_Tables_Table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.Results_Tables_Table.setHorizontalHeaderItem(3, item)
        self.Results_Tables_Table.horizontalHeader().setDefaultSectionSize(175)
        self.verticalLayout_7.addWidget(self.Results_Tables_Table)
        self.verticalLayout_6.addWidget(self.Results_Tables_GroupBox)
        self.Results_Tab_Widget.addTab(self.Results_Tables_Tab, _fromUtf8(""))
        self.Results_Maps_Tab = QtWidgets.QWidget()
        self.Results_Maps_Tab.setObjectName(_fromUtf8("Results_Maps_Tab"))
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.Results_Maps_Tab)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.Results_Maps_GroupBox = QtWidgets.QGroupBox(self.Results_Maps_Tab)
        self.Results_Maps_GroupBox.setObjectName(_fromUtf8("Results_Maps_GroupBox"))
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.Results_Maps_GroupBox)
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.Results_Maps_Table = QtWidgets.QTableWidget(self.Results_Maps_GroupBox)
        self.Results_Maps_Table.setObjectName(_fromUtf8("Results_Maps_Table"))
        self.Results_Maps_Table.setColumnCount(4)
        self.Results_Maps_Table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.Results_Maps_Table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.Results_Maps_Table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.Results_Maps_Table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.Results_Maps_Table.setHorizontalHeaderItem(3, item)
        self.Results_Maps_Table.horizontalHeader().setDefaultSectionSize(175)
        self.Results_Maps_Table.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_9.addWidget(self.Results_Maps_Table)
        self.verticalLayout_8.addWidget(self.Results_Maps_GroupBox)
        self.Results_Tab_Widget.addTab(self.Results_Maps_Tab, _fromUtf8(""))
        self.Results_OutputFiles_Tab = QtWidgets.QWidget()
        self.Results_OutputFiles_Tab.setObjectName(_fromUtf8("Results_OutputFiles_Tab"))
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.Results_OutputFiles_Tab)
        self.verticalLayout_10.setObjectName(_fromUtf8("verticalLayout_10"))
        self.Results_OutputFiles_GroupBox = QtWidgets.QGroupBox(self.Results_OutputFiles_Tab)
        self.Results_OutputFiles_GroupBox.setObjectName(_fromUtf8("Results_OutputFiles_GroupBox"))
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.Results_OutputFiles_GroupBox)
        self.verticalLayout_11.setObjectName(_fromUtf8("verticalLayout_11"))
        self.Results_OutputFiles_Table = QtWidgets.QTableWidget(self.Results_OutputFiles_GroupBox)
        self.Results_OutputFiles_Table.setObjectName(_fromUtf8("Results_OutputFiles_Table"))
        self.Results_OutputFiles_Table.setColumnCount(3)
        self.Results_OutputFiles_Table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.Results_OutputFiles_Table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.Results_OutputFiles_Table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.Results_OutputFiles_Table.setHorizontalHeaderItem(2, item)
        self.Results_OutputFiles_Table.horizontalHeader().setDefaultSectionSize(150)
        self.Results_OutputFiles_Table.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_11.addWidget(self.Results_OutputFiles_Table)
        self.verticalLayout_10.addWidget(self.Results_OutputFiles_GroupBox)
        self.Results_Tab_Widget.addTab(self.Results_OutputFiles_Tab, _fromUtf8(""))
        self.Results_Properties_Tab = QtWidgets.QWidget()
        self.Results_Properties_Tab.setObjectName(_fromUtf8("Results_Properties_Tab"))
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.Results_Properties_Tab)
        self.verticalLayout_12.setObjectName(_fromUtf8("verticalLayout_12"))
        self.Results_Properties_GroupBox = QtWidgets.QGroupBox(self.Results_Properties_Tab)
        self.Results_Properties_GroupBox.setObjectName(_fromUtf8("Results_Properties_GroupBox"))
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.Results_Properties_GroupBox)
        self.verticalLayout_13.setObjectName(_fromUtf8("verticalLayout_13"))
        self.Results_Properties_Table = QtWidgets.QTableWidget(self.Results_Properties_GroupBox)
        self.Results_Properties_Table.setAlternatingRowColors(True)
        self.Results_Properties_Table.setObjectName(_fromUtf8("Results_Properties_Table"))
        self.Results_Properties_Table.setColumnCount(2)
        self.Results_Properties_Table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.Results_Properties_Table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.Results_Properties_Table.setHorizontalHeaderItem(1, item)
        self.Results_Properties_Table.horizontalHeader().setStretchLastSection(True)
        self.Results_Properties_Table.verticalHeader().setStretchLastSection(False)
        self.verticalLayout_13.addWidget(self.Results_Properties_Table)
        self.verticalLayout_12.addWidget(self.Results_Properties_GroupBox)
        self.Results_Tab_Widget.addTab(self.Results_Properties_Tab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.Results_Tab_Widget)
        self.gridLayout_2.addWidget(self.Results_GroupBox, 2, 0, 1, 6)
        self.Status_Current_Command_Status_Label = QtWidgets.QLabel(self.centralwidget)
        self.Status_Current_Command_Status_Label.setObjectName(_fromUtf8("Status_Current_Command_Status_Label"))
        self.gridLayout_2.addWidget(self.Status_Current_Command_Status_Label, 3, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 5, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 5, 2, 1, 1)
        self.Status_Command_Workflow_Status_Label = QtWidgets.QLabel(self.centralwidget)
        self.Status_Command_Workflow_Status_Label.setObjectName(_fromUtf8("Status_Command_Workflow_Status_Label"))
        self.gridLayout_2.addWidget(self.Status_Command_Workflow_Status_Label, 3, 4, 1, 1)
        self.Status_Label = QtWidgets.QLabel(self.centralwidget)
        self.Status_Label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.Status_Label.setFrameShadow(QtWidgets.QFrame.Plain)
        self.Status_Label.setLineWidth(2)
        self.Status_Label.setObjectName(_fromUtf8("Status_Label"))
        self.gridLayout_2.addWidget(self.Status_Label, 5, 5, 1, 1)
        self.StatusCommand_Workflow_Status_Bar = QtWidgets.QProgressBar(self.centralwidget)
        self.StatusCommand_Workflow_Status_Bar.setProperty("value", 0)
        self.StatusCommand_Workflow_Status_Bar.setInvertedAppearance(False)
        self.StatusCommand_Workflow_Status_Bar.setObjectName(_fromUtf8("StatusCommand_Workflow_Status_Bar"))
        self.gridLayout_2.addWidget(self.StatusCommand_Workflow_Status_Bar, 5, 4, 1, 1)
        self.Status_Current_Command_Status_Bar = QtWidgets.QProgressBar(self.centralwidget)
        self.Status_Current_Command_Status_Bar.setProperty("value", 0)
        self.Status_Current_Command_Status_Bar.setInvertedAppearance(False)
        self.Status_Current_Command_Status_Bar.setObjectName(_fromUtf8("Status_Current_Command_Status_Bar"))
        self.gridLayout_2.addWidget(self.Status_Current_Command_Status_Bar, 5, 3, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout_3.addWidget(self.pushButton, 0, 1, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout_3.addWidget(self.lineEdit, 0, 0, 1, 1)
        self.listWidget = QtWidgets.QListWidget(self.groupBox)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.gridLayout_3.addWidget(self.listWidget, 1, 0, 1, 2)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 6)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1038, 20))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.Menu_File = QtWidgets.QMenu(self.menubar)
        self.Menu_File.setObjectName(_fromUtf8("Menu_File"))
        self.Menu_File_New = QtWidgets.QMenu(self.Menu_File)
        self.Menu_File_New.setObjectName(_fromUtf8("Menu_File_New"))
        self.Menu_File_Open = QtWidgets.QMenu(self.Menu_File)
        self.Menu_File_Open.setObjectName(_fromUtf8("Menu_File_Open"))
        self.Menu_File_Save = QtWidgets.QMenu(self.Menu_File)
        self.Menu_File_Save.setObjectName(_fromUtf8("Menu_File_Save"))
        self.Menu_Commands = QtWidgets.QMenu(self.menubar)
        self.Menu_Commands.setObjectName(_fromUtf8("Menu_Commands"))
        self.Menu_Commands_Tables = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Tables.setObjectName(_fromUtf8("Menu_Commands_Tables"))
        self.Menu_Commands_GeoLayers = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_GeoLayers.setObjectName(_fromUtf8("Menu_Commands_GeoLayers"))
        self.Commands_GeoLayers_Read_2 = QtWidgets.QMenu(self.Menu_Commands_GeoLayers)
        self.Commands_GeoLayers_Read_2.setObjectName(_fromUtf8("Commands_GeoLayers_Read_2"))
        self.Menu_Commands_Comments = QtWidgets.QMenu(self.Menu_Commands)
        self.Menu_Commands_Comments.setObjectName(_fromUtf8("Menu_Commands_Comments"))
        self.Menu_Help = QtWidgets.QMenu(self.menubar)
        self.Menu_Help.setObjectName(_fromUtf8("Menu_Help"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.Menu_Print = QtWidgets.QAction(MainWindow)
        self.Menu_Print.setObjectName(_fromUtf8("Menu_Print"))
        self.Menu_Properties = QtWidgets.QAction(MainWindow)
        self.Menu_Properties.setObjectName(_fromUtf8("Menu_Properties"))
        self.File_SetWorkingDirectory = QtWidgets.QAction(MainWindow)
        self.File_SetWorkingDirectory.setObjectName(_fromUtf8("File_SetWorkingDirectory"))
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.File_New_CommandFile = QtWidgets.QAction(MainWindow)
        self.File_New_CommandFile.setObjectName(_fromUtf8("File_New_CommandFile"))
        self.File_Open_CommandFile = QtWidgets.QAction(MainWindow)
        self.File_Open_CommandFile.setObjectName(_fromUtf8("File_Open_CommandFile"))
        self.File_Save_Commands = QtWidgets.QAction(MainWindow)
        self.File_Save_Commands.setObjectName(_fromUtf8("File_Save_Commands"))
        self.File_Save_CommandsAs = QtWidgets.QAction(MainWindow)
        self.File_Save_CommandsAs.setObjectName(_fromUtf8("File_Save_CommandsAs"))
        self.actionRead = QtWidgets.QAction(MainWindow)
        self.actionRead.setObjectName(_fromUtf8("actionRead"))
        self.actionWrite = QtWidgets.QAction(MainWindow)
        self.actionWrite.setObjectName(_fromUtf8("actionWrite"))
        self.Commands_Tables_Read = QtWidgets.QAction(MainWindow)
        self.Commands_Tables_Read.setObjectName(_fromUtf8("Commands_Tables_Read"))
        self.Commands_Tables_Process = QtWidgets.QAction(MainWindow)
        self.Commands_Tables_Process.setObjectName(_fromUtf8("Commands_Tables_Process"))
        self.Commands_Tables_Write = QtWidgets.QAction(MainWindow)
        self.Commands_Tables_Write.setObjectName(_fromUtf8("Commands_Tables_Write"))
        self.Commands_GeoLayers_Process = QtWidgets.QAction(MainWindow)
        self.Commands_GeoLayers_Process.setObjectName(_fromUtf8("Commands_GeoLayers_Process"))
        self.Commands_GeoLayers_Write = QtWidgets.QAction(MainWindow)
        self.Commands_GeoLayers_Write.setObjectName(_fromUtf8("Commands_GeoLayers_Write"))
        self.Commands_Comments_Single = QtWidgets.QAction(MainWindow)
        self.Commands_Comments_Single.setObjectName(_fromUtf8("Commands_Comments_Single"))
        self.Commands_Comments_MultipleStart = QtWidgets.QAction(MainWindow)
        self.Commands_Comments_MultipleStart.setObjectName(_fromUtf8("Commands_Comments_MultipleStart"))
        self.Commands_Comments_MultipleEnd = QtWidgets.QAction(MainWindow)
        self.Commands_Comments_MultipleEnd.setObjectName(_fromUtf8("Commands_Comments_MultipleEnd"))
        self.Commands_Comments_DisableTest = QtWidgets.QAction(MainWindow)
        self.Commands_Comments_DisableTest.setObjectName(_fromUtf8("Commands_Comments_DisableTest"))
        self.Commands_Comments_ExpectedStatusFail = QtWidgets.QAction(MainWindow)
        self.Commands_Comments_ExpectedStatusFail.setObjectName(_fromUtf8("Commands_Comments_ExpectedStatusFail"))
        self.Commands_Comments_ExpectedStatusWarn = QtWidgets.QAction(MainWindow)
        self.Commands_Comments_ExpectedStatusWarn.setObjectName(_fromUtf8("Commands_Comments_ExpectedStatusWarn"))
        self.GeoLayers_Read_ReadGeoLayerFromGeoJSON = QtWidgets.QAction(MainWindow)
        self.GeoLayers_Read_ReadGeoLayerFromGeoJSON.setObjectName(_fromUtf8("GeoLayers_Read_ReadGeoLayerFromGeoJSON"))
        self.GeoLayers_Read_ReadGeoLayerFromShapefile = QtWidgets.QAction(MainWindow)
        self.GeoLayers_Read_ReadGeoLayerFromShapefile.setObjectName(_fromUtf8("GeoLayers_Read_ReadGeoLayerFromShapefile"))
        self.GeoLayers_Read_ReadGeoLayersFromFGDB = QtWidgets.QAction(MainWindow)
        self.GeoLayers_Read_ReadGeoLayersFromFGDB.setObjectName(_fromUtf8("GeoLayers_Read_ReadGeoLayersFromFGDB"))
        self.GeoLayers_Read_ReadGeoLayersFromFolder = QtWidgets.QAction(MainWindow)
        self.GeoLayers_Read_ReadGeoLayersFromFolder.setObjectName(_fromUtf8("GeoLayers_Read_ReadGeoLayersFromFolder"))
        self.Menu_Help_About = QtWidgets.QAction(MainWindow)
        self.Menu_Help_About.setObjectName(_fromUtf8("Menu_Help_About"))
        self.Help_ViewDocumentation = QtWidgets.QAction(MainWindow)
        self.Help_ViewDocumentation.setObjectName(_fromUtf8("Help_ViewDocumentation"))
        self.Menu_File_New.addAction(self.File_New_CommandFile)
        self.Menu_File_Open.addAction(self.File_Open_CommandFile)
        self.Menu_File_Save.addAction(self.File_Save_Commands)
        self.Menu_File_Save.addAction(self.File_Save_CommandsAs)
        self.Menu_File.addAction(self.Menu_File_New.menuAction())
        self.Menu_File.addAction(self.Menu_File_Open.menuAction())
        self.Menu_File.addAction(self.Menu_File_Save.menuAction())
        self.Menu_File.addAction(self.Menu_Print)
        self.Menu_File.addSeparator()
        self.Menu_File.addAction(self.Menu_Properties)
        self.Menu_File.addSeparator()
        self.Menu_File.addAction(self.File_SetWorkingDirectory)
        self.Menu_File.addSeparator()
        self.Menu_File.addAction(self.actionExit)
        self.Menu_Commands_Tables.addAction(self.Commands_Tables_Read)
        self.Menu_Commands_Tables.addAction(self.Commands_Tables_Process)
        self.Menu_Commands_Tables.addAction(self.Commands_Tables_Write)
        self.Commands_GeoLayers_Read_2.addAction(self.GeoLayers_Read_ReadGeoLayerFromGeoJSON)
        self.Commands_GeoLayers_Read_2.addAction(self.GeoLayers_Read_ReadGeoLayerFromShapefile)
        self.Commands_GeoLayers_Read_2.addAction(self.GeoLayers_Read_ReadGeoLayersFromFGDB)
        self.Commands_GeoLayers_Read_2.addAction(self.GeoLayers_Read_ReadGeoLayersFromFolder)
        self.Menu_Commands_GeoLayers.addAction(self.Commands_GeoLayers_Read_2.menuAction())
        self.Menu_Commands_GeoLayers.addAction(self.Commands_GeoLayers_Process)
        self.Menu_Commands_GeoLayers.addAction(self.Commands_GeoLayers_Write)
        self.Menu_Commands_Comments.addAction(self.Commands_Comments_Single)
        self.Menu_Commands_Comments.addAction(self.Commands_Comments_MultipleStart)
        self.Menu_Commands_Comments.addAction(self.Commands_Comments_MultipleEnd)
        self.Menu_Commands_Comments.addSeparator()
        self.Menu_Commands_Comments.addAction(self.Commands_Comments_DisableTest)
        self.Menu_Commands_Comments.addAction(self.Commands_Comments_ExpectedStatusFail)
        self.Menu_Commands_Comments.addAction(self.Commands_Comments_ExpectedStatusWarn)
        self.Menu_Commands.addAction(self.Menu_Commands_GeoLayers.menuAction())
        self.Menu_Commands.addAction(self.Menu_Commands_Tables.menuAction())
        self.Menu_Commands.addSeparator()
        self.Menu_Commands.addAction(self.Menu_Commands_Comments.menuAction())
        self.Menu_Help.addAction(self.Menu_Help_About)
        self.Menu_Help.addAction(self.Help_ViewDocumentation)
        self.menubar.addAction(self.Menu_File.menuAction())
        self.menubar.addAction(self.Menu_Commands.menuAction())
        self.menubar.addAction(self.Menu_Help.menuAction())


        self.retranslateUi(MainWindow)
        self.Results_Tab_Widget.setCurrentIndex(0)
        self.actionExit.triggered.connect(MainWindow.close)
        # QtCore.QObject.connect(self.actionExit, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)



    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "GeoProcessor", None))
        self.Commands_GroupBox.setTitle(_translate("MainWindow", "Commands (0 commands, 0  selected, 0 with failures, 0 with warnings)", None))
        self.Commands_RunAll_Button.setText(_translate("MainWindow", "  Run All Commands  ", None))
        self.Commands_Clear_Button.setText(_translate("MainWindow", "  Clear Commands  ", None))
        self.Commands_RunSelected_Button.setText(_translate("MainWindow", "  Run Selected Commands  ", None))
        self.Results_GroupBox.setTitle(_translate("MainWindow", "Results", None))
        self.Results_GeoLayers_GroupBox.setTitle(_translate("MainWindow", "GeoLayers (0 GeoLayers, 0 selected)", None))
        item = self.Results_GeoLayers_Table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "GeoLayer ID", None))
        item = self.Results_GeoLayers_Table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Geometry", None))
        item = self.Results_GeoLayers_Table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Feature Count", None))
        item = self.Results_GeoLayers_Table.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Coordinate Reference System", None))
        item = self.Results_GeoLayers_Table.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Command Reference", None))
        self.Results_Tab_Widget.setTabText(self.Results_Tab_Widget.indexOf(self.Results_GeoLayers_Tab), _translate("MainWindow", "GeoLayers", None))
        self.Results_Tables_GroupBox.setTitle(_translate("MainWindow", "Tables (0 Tables, 0 selected)", None))
        item = self.Results_Tables_Table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Table ID", None))
        item = self.Results_Tables_Table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Column Count", None))
        item = self.Results_Tables_Table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Row Count", None))
        item = self.Results_Tables_Table.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Command Reference", None))
        self.Results_Tab_Widget.setTabText(self.Results_Tab_Widget.indexOf(self.Results_Tables_Tab), _translate("MainWindow", "Tables", None))
        self.Results_Maps_GroupBox.setTitle(_translate("MainWindow", "Maps (0 Maps, 0 selected)", None))
        item = self.Results_Maps_Table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Map ID", None))
        item = self.Results_Maps_Table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Included GeoLayers", None))
        item = self.Results_Maps_Table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Coordinate Reference System", None))
        item = self.Results_Maps_Table.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Command Reference", None))
        self.Results_Tab_Widget.setTabText(self.Results_Tab_Widget.indexOf(self.Results_Maps_Tab), _translate("MainWindow", "Maps", None))
        self.Results_OutputFiles_GroupBox.setTitle(_translate("MainWindow", "Output Files (0 Output Files, 0 selected)", None))
        item = self.Results_OutputFiles_Table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Output File ", None))
        item = self.Results_OutputFiles_Table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "File Type", None))
        item = self.Results_OutputFiles_Table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Command Reference", None))
        self.Results_Tab_Widget.setTabText(self.Results_Tab_Widget.indexOf(self.Results_OutputFiles_Tab), _translate("MainWindow", "Output Files", None))
        self.Results_Properties_GroupBox.setTitle(_translate("MainWindow", "Processor properties control processing and can be used in some command parameters using ${Property} notation (see command documentation). ", None))
        item = self.Results_Properties_Table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Property Name", None))
        item = self.Results_Properties_Table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Property Value", None))
        self.Results_Tab_Widget.setTabText(self.Results_Tab_Widget.indexOf(self.Results_Properties_Tab), _translate("MainWindow", "Properties", None))
        self.Status_Current_Command_Status_Label.setText(_translate("MainWindow", "Current Command Status", None))
        self.Status_Command_Workflow_Status_Label.setText(_translate("MainWindow", "Command Workflow Status", None))
        self.Status_Label.setText(_translate("MainWindow", "Ready", None))
        self.groupBox.setTitle(_translate("MainWindow", "Catalog", None))
        self.pushButton.setText(_translate("MainWindow", "Add To Catalog", None))
        self.Menu_File.setTitle(_translate("MainWindow", "File", None))
        self.Menu_File_New.setTitle(_translate("MainWindow", "New", None))
        self.Menu_File_Open.setTitle(_translate("MainWindow", "Open", None))
        self.Menu_File_Save.setTitle(_translate("MainWindow", "Save", None))
        self.Menu_Commands.setTitle(_translate("MainWindow", "Commands", None))
        self.Menu_Commands_Tables.setTitle(_translate("MainWindow", "Tables", None))
        self.Menu_Commands_GeoLayers.setTitle(_translate("MainWindow", "GeoLayers", None))
        self.Commands_GeoLayers_Read_2.setTitle(_translate("MainWindow", "Read", None))
        self.Menu_Commands_Comments.setTitle(_translate("MainWindow", "General - Comments", None))
        self.Menu_Help.setTitle(_translate("MainWindow", "Help", None))
        self.Menu_Print.setText(_translate("MainWindow", "Print", None))
        self.Menu_Properties.setText(_translate("MainWindow", "Properties", None))
        self.File_SetWorkingDirectory.setText(_translate("MainWindow", "Set Working Directory ...", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))
        self.File_New_CommandFile.setText(_translate("MainWindow", "Command File", None))
        self.File_Open_CommandFile.setText(_translate("MainWindow", "Command File ...", None))
        self.File_Save_Commands.setText(_translate("MainWindow", "Commands ...", None))
        self.File_Save_CommandsAs.setText(_translate("MainWindow", "Commands as ...", None))
        self.actionRead.setText(_translate("MainWindow", "Read", None))
        self.actionWrite.setText(_translate("MainWindow", "Write", None))
        self.Commands_Tables_Read.setText(_translate("MainWindow", "Read", None))
        self.Commands_Tables_Process.setText(_translate("MainWindow", "Process", None))
        self.Commands_Tables_Write.setText(_translate("MainWindow", "Write", None))
        self.Commands_GeoLayers_Process.setText(_translate("MainWindow", "Process", None))
        self.Commands_GeoLayers_Write.setText(_translate("MainWindow", "Write", None))
        self.Commands_Comments_Single.setText(_translate("MainWindow", "# comments <enter 1+ comments each starting with #>", None))
        self.Commands_Comments_MultipleStart.setText(_translate("MainWindow", "/* <start multi-line comment section> ", None))
        self.Commands_Comments_MultipleEnd.setText(_translate("MainWindow", "*/ <end multi-line comment section>", None))
        self.Commands_Comments_DisableTest.setText(_translate("MainWindow", "#@enabled False <disables the test>", None))
        self.Commands_Comments_ExpectedStatusFail.setText(_translate("MainWindow", "#@expectedStatus Failure <used to test commands>", None))
        self.Commands_Comments_ExpectedStatusWarn.setText(_translate("MainWindow", "#@expectedStatus Warning <used to test commands>", None))
        self.GeoLayers_Read_ReadGeoLayerFromGeoJSON.setText(_translate("MainWindow", "ReadGeoLayerFromGeoJSON <reads a GeoLayer from a .geojson file>", None))
        self.GeoLayers_Read_ReadGeoLayerFromShapefile.setText(_translate("MainWindow", "ReadGeoLayerFromShapefile <reads a GeoLayer from a shapefile>", None))
        self.GeoLayers_Read_ReadGeoLayersFromFGDB.setText(_translate("MainWindow", "ReadGeoLayersFromFGDB <reads 1+ GeoLayer(s) from the feature classes of a file geodatabase>", None))
        self.GeoLayers_Read_ReadGeoLayersFromFolder.setText(_translate("MainWindow", "ReadGeoLayersFromFolder <reads 1+ GeoLayer(s) from a local folder>", None))
        self.Menu_Help_About.setText(_translate("MainWindow", "About GeoProcessor", None))
        self.Help_ViewDocumentation.setText(_translate("MainWindow", "View Documentation", None))

