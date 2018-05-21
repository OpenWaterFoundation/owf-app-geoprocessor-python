from PyQt4 import QtCore, QtGui
from geoprocessor.commands.layers.ReadGeoLayerFromGeoJSON import ReadGeoLayerFromGeoJSON
from geoprocessor.ui.util.AbstractCommand_Editor import UI_AbstractDialog
from geoprocessor.core.CommandParameterMetadata import get_parameter_names

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

class Ui_Dialog(UI_AbstractDialog):

    def __init__(self):
        self.command_obj = ReadGeoLayerFromGeoJSON()
        self.command_name = self.command_obj.command_name
        self.command_parameters = get_parameter_names(self.command_obj.command_parameter_metadata)
        self.command_description = "The ReadGeoLayerFromGeoJSON command reads a GeoLayer from a .geojson file. \n\n" \
                                   "Specify the GeoJSON file to read into the GeoProcessor."
        self.parameter_count = len(self.command_parameters)
        self.command_parameter_values = {"SpatialDataFile": "",
                                         "GeoLayerID": "",
                                         "IfGeoLayerIDExists": ""}

        UI_AbstractDialog.__init__(self, self.command_name, self.command_description, self.parameter_count,
                                self.command_parameters, self.command_parameter_values)

    def setupUi(self, Dialog):

        # Configure the Dialog window with the features that are consistent across all command dialog windows.
        self.setupUi_Abstract(Dialog)

        # SpatialDataFile
        parameter_name = "SpatialDataFile"
        description = self.create_full_description("absolute or relative path to the input GeoJSON file", optional=False)
        tooltip = "The GeoJSON file to read (relative or absolute path).\n${Property} syntax is recognized."
        self.SpatialDataFile_Label = QtGui.QLabel(Dialog)
        self.configureLabel(self.SpatialDataFile_Label, parameter_name)
        self.SpatialDataFile_LineEdit = QtGui.QLineEdit(Dialog)
        self.configureLineEdit(self.SpatialDataFile_LineEdit, parameter_name, long=True, placeholder_text=description,
                            tooltip=tooltip)
        self.SpatialDataFile_ToolButton = QtGui.QToolButton(Dialog)
        self.configureToolButton(self.SpatialDataFile_ToolButton, parameter_name, self.SpatialDataFile_LineEdit)

        # GeoLayerID
        parameter_name = "GeoLayerID"
        description = self.create_full_description("GeoLayer identifier", optional=True,
                                                  default_value="filename of the input Spatial Data File")
        tooltip = "A GeoLayer identifier.\n Formatting characters and ${Property} syntax are recognized."
        self.GeoLayerID_Label = QtGui.QLabel(Dialog)
        self.configureLabel(self.GeoLayerID_Label, parameter_name)
        self.GeoLayerID_LineEdit = QtGui.QLineEdit(Dialog)
        self.configureLineEdit(self.GeoLayerID_LineEdit, parameter_name, tooltip=tooltip)
        self.GeoLayerID_Description_Label = QtGui.QLabel(Dialog)
        self.configureDescriptionLabel(self.GeoLayerID_Description_Label, parameter_name, description)

        # IfGeoLayerIDExists
        parameter_name = "IfGeoLayerIDExists"
        description = self.create_full_description("action that occurs if GeoLayer ID is not unique", optional=True,
                                                  default_value="Replace")
        tooltip = "The action that occurs if the GeoLayerID already exists within the GeoProcessor. \n\nReplace: " \
                  "The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer. No warning " \
                  "is logged.\n\nReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with " \
                  "the new GeoLayer. A warning is logged. \n\nWarn: The new GeoLayer is not created. A warning " \
                  "is logged. \n\nFail: The new GeoLayer is not created. A fail message is logged."
        self.IfGeoLayerIDExists_Label = QtGui.QLabel(Dialog)
        self.configureLabel(self.IfGeoLayerIDExists_Label, parameter_name)
        self.IfGeoLayerIDExists_ComboBox = QtGui.QComboBox(Dialog)
        self.configureComboBox(self.IfGeoLayerIDExists_ComboBox, parameter_name,
                            self.command_obj.choices_IfGeoLayerIDExists, tooltip=tooltip)
        self.IfGeoLayerIDExists_Description_Label = QtGui.QLabel(Dialog)
        self.configureDescriptionLabel(self.IfGeoLayerIDExists_Description_Label, parameter_name, description)

    def refresh(self):
        """THIS UPDATE THE DIALOG BOX WITH THE PREVIOUSLY DEFINED PARAMETER VALUES WHEN EDITING A COMMAND WITHIN THE UI.
        """
        self.SpatialDataFile_LineEdit.setText(self.command_parameter_values["SpatialDataFile"])
        self.GeoLayerID_LineEdit.setText(self.command_parameter_values["GeoLayerID"])
        try:
            index = self.command_obj.choices_IfGeoLayerIDExists.index(self.command_parameter_values["IfGeoLayerIDExists"])
        except:
            index = 0
        self.IfGeoLayerIDExists_ComboBox.setCurrentIndex(index)
