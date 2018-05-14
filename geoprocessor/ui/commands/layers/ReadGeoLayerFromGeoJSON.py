# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'readgeolayerfromgeojson-draft2.ui'
#
# Created: Tue May 08 10:41:20 2018
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(684, 404)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.Command_Description = QtGui.QFrame(Dialog)
        self.Command_Description.setFrameShape(QtGui.QFrame.StyledPanel)
        self.Command_Description.setFrameShadow(QtGui.QFrame.Raised)
        self.Command_Description.setObjectName(_fromUtf8("Command_Description"))
        self.gridLayout_2 = QtGui.QGridLayout(self.Command_Description)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 2, 0, 1, 1)
        self.View_Documentation_Button = QtGui.QPushButton(self.Command_Description)
        self.View_Documentation_Button.setObjectName(_fromUtf8("View_Documentation_Button"))
        self.gridLayout_2.addWidget(self.View_Documentation_Button, 2, 1, 1, 1)
        self.Command_Description_Label = QtGui.QLabel(self.Command_Description)
        self.Command_Description_Label.setObjectName(_fromUtf8("Command_Description_Label"))
        self.gridLayout_2.addWidget(self.Command_Description_Label, 0, 0, 1, 2)
        self.gridLayout.addWidget(self.Command_Description, 0, 0, 1, 8)
        self.GeoLayerID_Label = QtGui.QLabel(Dialog)
        self.GeoLayerID_Label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.GeoLayerID_Label.setObjectName(_fromUtf8("GeoLayerID_Label"))
        self.gridLayout.addWidget(self.GeoLayerID_Label, 3, 0, 1, 1)
        self.SpatialDataFile_Label = QtGui.QLabel(Dialog)
        self.SpatialDataFile_Label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.SpatialDataFile_Label.setObjectName(_fromUtf8("SpatialDataFile_Label"))
        self.gridLayout.addWidget(self.SpatialDataFile_Label, 2, 0, 1, 1)
        self.IfGeoLayerIDExists_Label = QtGui.QLabel(Dialog)
        self.IfGeoLayerIDExists_Label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.IfGeoLayerIDExists_Label.setObjectName(_fromUtf8("IfGeoLayerIDExists_Label"))
        self.gridLayout.addWidget(self.IfGeoLayerIDExists_Label, 4, 0, 1, 1)
        self.Separator = QtGui.QFrame(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Separator.sizePolicy().hasHeightForWidth())
        self.Separator.setSizePolicy(sizePolicy)
        self.Separator.setFrameShape(QtGui.QFrame.HLine)
        self.Separator.setFrameShadow(QtGui.QFrame.Sunken)
        self.Separator.setObjectName(_fromUtf8("Separator"))
        self.gridLayout.addWidget(self.Separator, 1, 0, 1, 8)
        self.GeoLayerID_Input_LineEdit = QtGui.QLineEdit(Dialog)
        self.GeoLayerID_Input_LineEdit.setPlaceholderText(_fromUtf8(""))
        self.GeoLayerID_Input_LineEdit.setObjectName(_fromUtf8("GeoLayerID_Input_LineEdit"))
        self.gridLayout.addWidget(self.GeoLayerID_Input_LineEdit, 3, 1, 1, 3)
        self.IfGeoLayerIDExists_ComboBox = QtGui.QComboBox(Dialog)
        self.IfGeoLayerIDExists_ComboBox.setObjectName(_fromUtf8("IfGeoLayerIDExists_ComboBox"))
        self.IfGeoLayerIDExists_ComboBox.addItem(_fromUtf8(""))
        self.IfGeoLayerIDExists_ComboBox.setItemText(0, _fromUtf8(""))
        self.IfGeoLayerIDExists_ComboBox.addItem(_fromUtf8(""))
        self.IfGeoLayerIDExists_ComboBox.addItem(_fromUtf8(""))
        self.IfGeoLayerIDExists_ComboBox.addItem(_fromUtf8(""))
        self.IfGeoLayerIDExists_ComboBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.IfGeoLayerIDExists_ComboBox, 4, 1, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 5, 3, 1, 1)
        self.GeoLayerID_Description_Label = QtGui.QLabel(Dialog)
        self.GeoLayerID_Description_Label.setObjectName(_fromUtf8("GeoLayerID_Description_Label"))
        self.gridLayout.addWidget(self.GeoLayerID_Description_Label, 3, 5, 1, 3)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 5, 0, 1, 1)
        self.SpatialDataFile_Browse_ToolButton = QtGui.QToolButton(Dialog)
        self.SpatialDataFile_Browse_ToolButton.setObjectName(_fromUtf8("SpatialDataFile_Browse_ToolButton"))
        self.SpatialDataFile_Browse_ToolButton.clicked.connect(self.selectFile)
        self.gridLayout.addWidget(self.SpatialDataFile_Browse_ToolButton, 2, 7, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 5, 2, 1, 1)
        self.CommandDisplay_View_TextBrowser = QtGui.QTextEdit(Dialog)
        self.CommandDisplay_View_TextBrowser.setMinimumSize(QtCore.QSize(0, 100))
        self.CommandDisplay_View_TextBrowser.setMaximumSize(QtCore.QSize(16777215, 100))
        self.CommandDisplay_View_TextBrowser.setObjectName(_fromUtf8("CommandDisplay_View_TextBrowser"))
        self.gridLayout.addWidget(self.CommandDisplay_View_TextBrowser, 6, 2, 1, 6)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 5, 7, 1, 1)
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem5, 5, 5, 1, 1)
        self.CommandDisplay_Label = QtGui.QLabel(Dialog)
        self.CommandDisplay_Label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.CommandDisplay_Label.setObjectName(_fromUtf8("CommandDisplay_Label"))
        self.gridLayout.addWidget(self.CommandDisplay_Label, 6, 0, 1, 1)
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem6, 5, 6, 1, 1)
        self.IfGeoLayerIDExists_Description_Label = QtGui.QLabel(Dialog)
        self.IfGeoLayerIDExists_Description_Label.setObjectName(_fromUtf8("IfGeoLayerIDExists_Description_Label"))
        self.gridLayout.addWidget(self.IfGeoLayerIDExists_Description_Label, 4, 5, 1, 3)
        self.OK_Cancel_Buttons = QtGui.QDialogButtonBox(Dialog)
        self.OK_Cancel_Buttons.setOrientation(QtCore.Qt.Horizontal)
        self.OK_Cancel_Buttons.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.OK_Cancel_Buttons.setObjectName(_fromUtf8("OK_Cancel_Buttons"))
        self.gridLayout.addWidget(self.OK_Cancel_Buttons, 7, 6, 1, 2)
        spacerItem7 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem7, 5, 4, 1, 1)
        self.SpatialDataFile_Input_LineEdit = QtGui.QLineEdit(Dialog)
        self.SpatialDataFile_Input_LineEdit.setObjectName(_fromUtf8("SpatialDataFile_Input_LineEdit"))
        self.gridLayout.addWidget(self.SpatialDataFile_Input_LineEdit, 2, 1, 1, 6)

        self.SpatialDataFile_Input_LineEdit.textChanged.connect(self.sync_lineEdit)
        self.GeoLayerID_Input_LineEdit.textChanged.connect(self.sync_lineEdit)
        self.IfGeoLayerIDExists_ComboBox.currentIndexChanged.connect(self.sync_lineEdit)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.OK_Cancel_Buttons, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.OK_Cancel_Buttons, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)


    def selectFile(self):
        self.SpatialDataFile_Input_LineEdit.setText(QtGui.QFileDialog.getOpenFileName())

    def sync_lineEdit(self):

        updated_text_paramters = ""
        if self.SpatialDataFile_Input_LineEdit.text() != "" or None:
            updated_text_paramters += ('SpatialDataFile="{}", '.format(self.SpatialDataFile_Input_LineEdit.text()))
        if self.GeoLayerID_Input_LineEdit.text() != "" or None:
            updated_text_paramters += ('GeoLayerID="{}", '.format(self.GeoLayerID_Input_LineEdit.text()))
        if self.IfGeoLayerIDExists_ComboBox.currentText() != "" or None:
            updated_text_paramters += ('IfGeoLayerIDExists="{}", '.format(self.IfGeoLayerIDExists_ComboBox.currentText()))

        updated_text_paramters = updated_text_paramters.rsplit(", ", 1)[0]

        updatedText = "ReadGeoLayerFromGeoJSON({})".format(updated_text_paramters)
        self.CommandDisplay_View_TextBrowser.setText(updatedText)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "ReadGeoLayerFromGeoJSON", None))
        self.View_Documentation_Button.setText(_translate("Dialog", "  View Documentation  ", None))
        self.Command_Description_Label.setText(_translate("Dialog", "The ReadGeoLayerFromGeoJSON command reads a GeoLayer from a .geojson file. \n"
"\n"
" Specify the GeoJSON file to read into the GeoProcessor.", None))
        self.GeoLayerID_Label.setText(_translate("Dialog", "GeoLayer ID: ", None))
        self.SpatialDataFile_Label.setText(_translate("Dialog", "Spatial Data File:", None))
        self.IfGeoLayerIDExists_Label.setText(_translate("Dialog", "If GeoLayer ID Exists: ", None))
        self.GeoLayerID_Input_LineEdit.setToolTip(_translate("Dialog", "A GeoLayer identifier.\n"
" Formatting characters and ${Property} syntax are recognized. ", None))
        self.IfGeoLayerIDExists_ComboBox.setToolTip(_translate("Dialog", "The action that occurs if the GeoLayerID already exists within the GeoProcessor. \n"
"\n"
"Replace : The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer. No warning is logged.\n"
"\n"
"ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer. A warning is logged. \n"
"\n"
"Warn : The new GeoLayer is not created. A warning is logged. \n"
"\n"
"Fail : The new GeoLayer is not created. A fail message is logged.", None))
        self.IfGeoLayerIDExists_ComboBox.setItemText(1, _translate("Dialog", "Replace", None))
        self.IfGeoLayerIDExists_ComboBox.setItemText(2, _translate("Dialog", "ReplaceAndWarn", None))
        self.IfGeoLayerIDExists_ComboBox.setItemText(3, _translate("Dialog", "Warn", None))
        self.IfGeoLayerIDExists_ComboBox.setItemText(4, _translate("Dialog", "Fail", None))
        self.GeoLayerID_Description_Label.setText(_translate("Dialog", "Optional - GeoLayer identifier\n"
"(default: filename of the input Spatial Data File)", None))
        self.SpatialDataFile_Browse_ToolButton.setText(_translate("Dialog", "...", None))
        self.CommandDisplay_View_TextBrowser.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">ReadGeoLayerFromGeoJSON()</span></p></body></html>", None))
        self.CommandDisplay_Label.setText(_translate("Dialog", "Command: ", None))
        self.IfGeoLayerIDExists_Description_Label.setText(_translate("Dialog", "Optional - action that occurs if GeoLayer ID is not unique \n"
"(default = Replace)", None))
        self.SpatialDataFile_Input_LineEdit.setToolTip(_translate("Dialog", "The GeoJSON file to read (relative or absolute path).\n"
" ${Property} syntax is recognized.", None))
        self.SpatialDataFile_Input_LineEdit.setPlaceholderText(_translate("Dialog", "Required - absolute or relative path to the input GeoJSON file.", None))

