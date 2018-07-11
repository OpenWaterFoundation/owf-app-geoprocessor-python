from PyQt5 import QtWidgets

from geoprocessor.commands.layers.ReadGeoLayerFromGeoJSON import ReadGeoLayerFromGeoJSON
from geoprocessor.ui.util.AbstractCommand_Editor import UI_AbstractDialog
from geoprocessor.ui.util.command_parameter import CommandParameter
from geoprocessor.core.CommandParameterMetadata import get_parameter_names

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


class UiDialog(UI_AbstractDialog):

    # CLASS VARIABLES: static across all classes

    # The GeoProcessor ReadGeoLayerFromGeoJSON object.
    command_obj = ReadGeoLayerFromGeoJSON()

    # The name of the command. Read from the GeoProcessor command object.
    command_name = command_obj.command_name

    # A list of the command parameters. Read from the GeoProcessor command object.
    command_parameters = get_parameter_names(command_obj.command_parameter_metadata)

    # A brief description of the command. This is displayed in the UI dialog box at the top to give the user context.
    command_description = "The ReadGeoLayerFromGeoJSON command reads a GeoLayer from a .geojson file. \n\n Specify " \
                          "the GeoJSON file to read into the GeoProcessor."

    # The number of parameters within the command. Indirectly, read from the GeoProcessor command object.
    parameter_count = len(command_parameters)

    # UI label objects are to be assigned within the setupUI function
    # These label objects are non-changing and are present in each ReadGeoLayerFromGeoJSON dialog box.
    #   SpatialDataFile_Label: labels the SpatialDataFile input text field. Note that the SpatialDataFile parameter
    #   does not need a description label object because the parameter description is written in the text field as
    #   placeholder text.
    #   GeoLayerID_Label: labels the GeoLayerID input text field
    #   GeoLayerID_Description_Label: describes the GeoLayerID parameter
    #   IfGeoLayerIDExists_Label: labels the IfGeoLayerIDExists input text field
    #   IfGeoLayerIDExists_Description_Label: describes the IfGeoLayerIDExists parameter
    SpatialDataFile_Label = None
    GeoLayerID_Label = None
    GeoLayerID_Description_Label = None
    IfGeoLayerIDExists_Label = None
    IfGeoLayerIDExists_Description_Label = None

    # Command parameter descriptions for the SpatialDataFile parameter.
    cp_SpatialDataFile = CommandParameter(name="SpatialDataFile",
                                          description="absolute or relative path to the input GeoJSON file",
                                          optional=False,
                                          tooltip="The GeoJSON file to read (relative or absolute path).\n${Property} "
                                                  "syntax is recognized.",
                                          default_value_description=None)

    # Command parameter descriptions for the GeoLayerID parameter.
    cp_GeoLayerID = CommandParameter(name="GeoLayerID",
                                     description="GeoLayer identifier",
                                     optional=True,
                                     tooltip="A GeoLayer identifier.\n Formatting characters and ${Property} syntax "
                                             "are recognized.",
                                     default_value_description="filename of the input Spatial Data File")

    # Command parameter descriptions for the IfGeoLayerIDExists parameter.
    cp_IfGeoLayerIDExists = CommandParameter(name="IfGeoLayerIDExists",
                                             description="action that occurs if GeoLayer ID is not unique",
                                             optional=True,
                                             tooltip="The action that occurs if the GeoLayerID already exists "
                                                     "within the GeoProcessor. \n\nReplace: The existing GeoLayer "
                                                     "within the GeoProcessor is overwritten with the new GeoLayer. "
                                                     "No warning is logged.\n\nReplaceAndWarn: The existing GeoLayer "
                                                     "within the GeoProcessor is overwritten with the new GeoLayer. A "
                                                     "warning is logged. \n\nWarn: The new GeoLayer is not created. "
                                                     "A warning is logged. \n\nFail: The new GeoLayer is not created. "
                                                     "A fail message is logged.",
                                             default_value_description="Replace")

    def __init__(self):
        """
        Initialize the ReadGeoLayerFromGeoJSON dialog box.
        Assign the INSTANCE VARIABLES: values specific to each instance.
        """

        # Command_parameter_values is a dictionary that holds the entered command parameter values.
        # Key: the name of the command parameter
        # Value: the entered value of the command parameter
        self.command_parameter_values = {}

        # Add all of the command parameters to the command_parameter_values dictionary. By default, set all
        # parameter values to an empty string. The values are populated later as the user enters text in the dialog box.
        for command_parameter_name in UiDialog.command_parameters:
            self.command_parameter_values[command_parameter_name] = ""

        # UI input field objects are to be assigned within the setupUI function
        # The values of these input field objects are dynamic and unique to the instance. They are, however, all
        # present in each ReadGeoLayerFromGeoJSON dialog box.
        #   SpatialDataFile_LineEdit: the input field (PyQt5 LineEdit obj) for the SpatialDataFile parameter
        #   SpatialDataFile_ToolButton: the button (PyQt5 ToolButton obj) to select a file for the SpatialDataFile
        #   parameter
        #   GeoLayerID_LineEdit: the input field (PyQt5 LineEdit obj) for the GeoLayerID parameter
        #   IfGeoLayerIDExists_ComboBox: the input field (PyQt5 ComboBox obj) for the IfGeoLayerIDExists parameter
        self.SpatialDataFile_LineEdit = None
        self.SpatialDataFile_ToolButton = None
        self.GeoLayerID_LineEdit = None
        self.IfGeoLayerIDExists_ComboBox = None

        # Initialize the parent Abstract Dialog class.
        UI_AbstractDialog.__init__(self, UiDialog.command_name, UiDialog.command_description, UiDialog.parameter_count,
                                   UiDialog.command_parameters, self.command_parameter_values)

    def setupUi(self, Dialog):

        # Configure the Dialog window with the features that are consistent across all GeoProcessor command dialog
        # windows.
        self.setupUi_Abstract(Dialog)

        # SpatialDataFile ##
        # Initialize a Qt QLabel object for the SpatialDataFile label.
        UiDialog.SpatialDataFile_Label = QtWidgets.QLabel(Dialog)

        # Configure the label to display the parameter name and align with the left side of the dialog window.
        self.configureLabel(UiDialog.SpatialDataFile_Label, UiDialog.cp_SpatialDataFile.name)

        # Initialize a Qt QLineEdit object for the SpatialDataFile input field.
        self.SpatialDataFile_LineEdit = QtWidgets.QLineEdit(Dialog)

        # Configure the input field to be extra long, display the placeholder description and include tooltip help.
        self.configureLineEdit(self.SpatialDataFile_LineEdit, UiDialog.cp_SpatialDataFile.name, long=True,
                               placeholder_text=UiDialog.cp_SpatialDataFile.description,
                               tooltip=UiDialog.cp_SpatialDataFile.tooltip)

        # Initialize a Qt QToolButton to open a browser to select a file for the SpatialDataFile parameter.
        self.SpatialDataFile_ToolButton = QtWidgets.QToolButton(Dialog)

        # Configure the button to link the selection to the SpatialDataFile_LineEdit input field.
        self.configureToolButton(self.SpatialDataFile_ToolButton, UiDialog.cp_SpatialDataFile.name,
                                 self.SpatialDataFile_LineEdit)

        # GeoLayerID ##
        # Initialize a Qt QLabel object for the GeoLayerID label.
        UiDialog.GeoLayerID_Label = QtWidgets.QLabel(Dialog)

        # Configure the label to display the parameter name and align with the left side of the dialog window.
        self.configureLabel(UiDialog.GeoLayerID_Label, UiDialog.cp_GeoLayerID.name)

        # Initialize a Qt QLineEdit object for the GeoLayerID input field.
        self.GeoLayerID_LineEdit = QtWidgets.QLineEdit(Dialog)

        # Configure the input field to include tooltip help.
        self.configureLineEdit(self.GeoLayerID_LineEdit, UiDialog.cp_GeoLayerID.name,
                               tooltip=UiDialog.cp_GeoLayerID.tooltip)

        # Initialize a Qt QLabel object for the GeoLayerID description.
        UiDialog.GeoLayerID_Description_Label = QtWidgets.QLabel(Dialog)

        # Configure the label to display the GeoLayerID parameter description.
        self.configureDescriptionLabel(UiDialog.GeoLayerID_Description_Label, UiDialog.cp_GeoLayerID.name,
                                       UiDialog.cp_GeoLayerID.description)

        # IfGeoLayerIDExists ##
        # Initialize a Qt QLabel object for the IfGeoLayerIDExists label.
        UiDialog.IfGeoLayerIDExists_Label = QtWidgets.QLabel(Dialog)

        # Configure the label to display the parameter name and align with the left side of the dialog window.
        self.configureLabel(UiDialog.IfGeoLayerIDExists_Label, UiDialog.cp_IfGeoLayerIDExists.name)

        # Initialize a Qt QComboBox object for the IfGeoLayerIDExists input field.
        self.IfGeoLayerIDExists_ComboBox = QtWidgets.QComboBox(Dialog)

        # Configure the input combo box to be populated with the available choices for the IfGeoLayerIDExists parameter.
        self.configureComboBox(self.IfGeoLayerIDExists_ComboBox, UiDialog.cp_IfGeoLayerIDExists.name,
                               UiDialog.command_obj.choices_IfGeoLayerIDExists,
                               tooltip=UiDialog.cp_IfGeoLayerIDExists.tooltip)

        # Initialize a Qt QLabel object for the IfGeoLayerIDExists description.
        UiDialog.IfGeoLayerIDExists_Description_Label = QtWidgets.QLabel(Dialog)

        # Configure the label to display the IfGeoLayerIDExists parameter description.
        self.configureDescriptionLabel(UiDialog.IfGeoLayerIDExists_Description_Label,
                                       UiDialog.cp_IfGeoLayerIDExists.name,
                                       UiDialog.cp_IfGeoLayerIDExists.description)

    def refresh(self):
        """
        This updates the dialog box with the previously defined parameter values when editing a command within the UI.
        """

        # Get the values of the previously-defined command dialog box. Assign to static variables before updating
        # the command dialog window. As the command dialog window is updated, the command_parameter_values
        # dictionary is altered.
        spatialdatafile_value = self.command_parameter_values["SpatialDataFile"]
        geolayerid_value = self.command_parameter_values["GeoLayerID"]
        ifgeolayeridexists_value = self.command_parameter_values["IfGeoLayerIDExists"]

        # Set the text of the SpatialDataFile input field to the predefined value of the SpatialDataFile parameter.
        self.GeoLayerID_LineEdit.setText(spatialdatafile_value)

        # Set the text of the SpatialDataFile input field to the predefined value of the SpatialDataFile parameter.
        self.GeoLayerID_LineEdit.setText(geolayerid_value)

        # If the predefined IfGeoLayerIDExists parameter value is within one of the available options, the index of
        # the value in the ComboBox object is the index of the value in the options list plus one. The one accounts
        #  for the blank option that is available in the ComboBox but is not in the available options list.
        if ifgeolayeridexists_value in UiDialog.command_obj.choices_IfGeoLayerIDExists:
            index = UiDialog.command_obj.choices_IfGeoLayerIDExists.index(ifgeolayeridexists_value) + 1

        # If the predefined IfGeoLayerIDExists parameter value is NOT within one of the available options, set the
        # index to the location of the blank option.
        else:
            index = 0

        # Set the value of the IfGeoLayerIDExists combo box to the predefined value of the IfGeoLayerIDExists parameter.
        # Combo boxes are set by indexes rather than by text.
        self.IfGeoLayerIDExists_ComboBox.setCurrentIndex(index)
