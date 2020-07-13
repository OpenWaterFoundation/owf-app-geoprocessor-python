# ReadGeoLayersFromGeoPackage - command to read GeoLayers from a GeoPackage file
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
from qgis._core import QgsVectorLayer

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandError import CommandError
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType
from geoprocessor.core.VectorGeoLayer import VectorGeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util
import geoprocessor.util.qgis_util as qgis_util

import os
import logging
# import re
import ogr


class ReadGeoLayersFromGeoPackage(AbstractCommand):
    """
    This command reads 1+ GeoLayers from a GeoPackage file (.gpkg) and creates GeoLayer objects within the
    geoprocessor. The GeoLayers can then be accessed in the geoprocessor by their identifier and further processed.

    Command Parameters
    * InputFile (str, required): the path to the GeoPackage file containing spatial data.
    * ReadOneLayer (str, required): a string that can be converted to a valid boolean value. If TRUE, only
         one specific feature class is read in as a GeoLayer. If FALSE, multiple feature classes are read in as
         different GeoLayers.
    * LayerName (str, required if ReadOneLayer is TRUE): the name of the GeoPackage layer to read.
    * GeoLayerID (str, required if ReadOneLayer is TRUE): the GeoLayer identifier.
    * GeoLayerID_prefix (str, optional, only used if ReadOneLayer is FALSE): the GeoLayer identifier will,
        by default, use the name of the feature class that is being read. However, if a value is set for this parameter,
         the GeoLayerID will follow this format: [GeoLayerID_prefix]_[name_of_feature_class].
    * Subset_Pattern (str, optional, only used if ReadOneLayer is FALSE): the glob-style pattern of the
        feature class name to determine which feature classes within the file geodatabase are to be processed. More
        information on creating a glob pattern can be found at https://docs.python.org/2/library/glob.html.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the GeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`. Used if
        ReadOneLayer is TRUE or FALSE.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("InputFile", type("")),
        CommandParameterMetadata("ReadOneLayer", type("")),
        CommandParameterMetadata("LayerName", type("")),
        CommandParameterMetadata("GeoLayerID", type("")),
        # CommandParameterMetadata("GeoLayerID_prefix", type("")),
        # CommandParameterMetadata("Subset_Pattern", type("")),
        CommandParameterMetadata("Name", type("")),
        CommandParameterMetadata("Description", type("")),
        CommandParameterMetadata("Properties", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Read one or more GeoLayers from a GeoPackage file.\n" \
        "Currently only a single (sub)layer can be read from a GeoPackage file."

    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()

    # InputFile
    __parameter_input_metadata['InputFile.Description'] = "GeoPackage file to read"
    __parameter_input_metadata['InputFile.Label'] = "GeoPackage file"
    __parameter_input_metadata['InputFile.Required'] = True
    __parameter_input_metadata['InputFile.Tooltip'] = "The GeoPackage file to read (must end in .gpkg)."
    __parameter_input_metadata['InputFile.FileSelector.Type'] = "Read"
    __parameter_input_metadata['InputFile.FileSelector.Title'] = "Select the file GeoPackage file"
    # Filters only seem to work on files, not folders
    # __parameter_input_metadata['InputFolder.FileSelector.Filters'] = \
    #    ["Geodatabase (*.gdb)", "All folders (*.*)"]

    # ReadOneLayer
    __parameter_input_metadata['ReadOneLayer.Description'] = "whether to read one layer"
    __parameter_input_metadata['ReadOneLayer.Label'] = "Read a single layer?"
    __parameter_input_metadata['ReadOneLayer.Required'] = True
    __parameter_input_metadata['ReadOneLayer.Tooltip'] = (
        "If True, only one layer will be read as a GeoLayer. Must specify a valid layer name.\n"
        "If False, one or more layers will be read as GeoLayers. "
        "Can specify the Subset_Pattern to select which layers to read.")
    __parameter_input_metadata['ReadOneLayer.Values'] = ["", "False", "True"]

    # LayerName
    __parameter_input_metadata['LayerName.Description'] = "name of layer to read"
    __parameter_input_metadata['LayerName.Label'] = "Layer name"
    __parameter_input_metadata['LayerName.Required'] = False
    __parameter_input_metadata['LayerName.Tooltip'] = \
        "The layer name within the GeoPackage file to read. ${Property} syntax is recognized."

    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "output GeoLayer identifier"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = \
        "A GeoLayer identifier. Formatting characters and ${Property} syntax are recognized."

    # GeoLayerID_prefix
    # __parameter_input_metadata['GeoLayerID_prefix.Description'] = "a GeoLayer identifier prefix"
    # __parameter_input_metadata['GeoLayerID_prefix.Label'] = "GeoLayerID prefix"
    # __parameter_input_metadata['GeoLayerID_prefix.Tooltip'] = \
    #     "GeoLayers read from a GeoPackage file have an identifier in the GeoLayerID_prefix_FeatureClass format."
    # __parameter_input_metadata['GeoLayerID_prefix.Value.Default'] = \
    #     "No prefix is used. The GeoLayerID is the GeoPackage layer name."

    # Subset_Pattern
    # __parameter_input_metadata['Subset_Pattern.Description'] = "globstyle pattern of layers to read"
    # __parameter_input_metadata['Subset_Pattern.Label'] = "Subset pattern"
    # __parameter_input_metadata['Subset_Pattern.Tooltip'] = \
    #     "The glob-style pattern (e.g., CO_* or *_[MC]O) of GeoPackage layer names to read."
    # __parameter_input_metadata['Subset_Pattern.Value.Default'] = \
    #     "No pattern is used. All GeoPackage layers are read."

    # Name
    __parameter_input_metadata['Name.Description'] = "GeoLayer name"
    __parameter_input_metadata['Name.Label'] = "Name"
    __parameter_input_metadata['Name.Required'] = False
    __parameter_input_metadata['Name.Tooltip'] = "The GeoLayer name, can use ${Property}."
    __parameter_input_metadata['Name.Value.Default.Description'] = "Layer name"

    # Description
    __parameter_input_metadata['Description.Description'] = "GeoLayer description"
    __parameter_input_metadata['Description.Label'] = "Description"
    __parameter_input_metadata['Description.Required'] = False
    __parameter_input_metadata['Description.Tooltip'] = "The GeoLayer description, can use ${Property}."
    __parameter_input_metadata['Description.Value.Default'] = ''

    # Properties
    __parameter_input_metadata['Properties.Description'] = "properties for the new GeoLayer"
    __parameter_input_metadata['Properties.Label'] = "Properties"
    __parameter_input_metadata['Properties.Required'] = False
    __parameter_input_metadata['Properties.Tooltip'] = \
        "Properties for the new GeoLayer using syntax:  property:value,property:'value'"

    # IfGeoLayerIDExists
    __parameter_input_metadata['IfGeoLayerIDExists.Description'] = "action if output exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = (
        "The action that occurs if the GeoLayerID already exists within the GeoProcessor.\n"
        "Replace : The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer.  "
        "No warning is logged.\n"
        "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new "
        "GeoLayer. A warning is logged.\n"
        "Warn : The new GeoLayer is not created. A warning is logged.\n"
        "Fail : The new GeoLayer is not created. A fail message is logged.")
    __parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
    __parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"

    def __init__(self) -> None:
        """
        Initialize the command
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "ReadGeoLayersFromGeoPackage"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata
        self.parameter_input_metadata = self.__parameter_input_metadata

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters: dict) -> None:
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns: None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning_message = ""

        # Check that required parameters are non-empty, non-None strings.
        required_parameters = command_util.get_required_parameter_names(self)
        for parameter in required_parameters:
            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)
            if not validator_util.validate_string(parameter_value, False, False):
                message = "Required {} parameter has no value.".format(parameter)
                recommendation = "Specify the {} parameter.".format(parameter)
                warning_message += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional parameter IfGeoLayerIDExists is either `Replace`, `ReplaceAndWarn`, `Warn`, `Fail`, None.
        # noinspection PyPep8Naming
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        acceptable_values = ["Replace", "ReplaceAndWarn", "Warn", "Fail"]
        if not validator_util.validate_string_in_list(pv_IfGeoLayerIDExists, acceptable_values, none_allowed=True,
                                                      empty_string_allowed=True, ignore_case=True):
            message = "IfGeoLayerIDExists parameter value ({}) is not recognized.".format(pv_IfGeoLayerIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfGeoLayerIDExists parameter.".format(
                acceptable_values)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that the optional parameter ReadOneLayer is a valid Boolean.
        # noinspection PyPep8Naming
        pv_ReadOneLayer = self.get_parameter_value(parameter_name="ReadOneLayer", command_parameters=command_parameters)
        if not validator_util.validate_bool(pv_ReadOneLayer, True, False):
            message = "ReadOneLayer is not a valid boolean value."
            recommendation = "Specify a valid boolean value for the ReadOneLayer parameter."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Continue with checks if the ReadOneLayer is a valid TRUE Boolean.
        elif string_util.str_to_bool(pv_ReadOneLayer):
            # Check that parameter GeoLayerID is a non-empty, non-None string.
            # noinspection PyPep8Naming
            pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID', command_parameters=command_parameters)

            if not validator_util.validate_string(pv_GeoLayerID, False, False):
                message = "GeoLayerID parameter has no value."
                recommendation = "Specify the GeoLayerID parameter."
                warning_message += "\n" + message
                self.command_status.add_to_log(
                    CommandPhaseType.INITIALIZATION,
                    CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Properties - verify that the properties can be parsed
        # noinspection PyPep8Naming
        pv_Properties = self.get_parameter_value(parameter_name="Properties", command_parameters=command_parameters)
        try:
            command_util.parse_properties_from_parameter_string(pv_Properties)
        except ValueError as e:
            # Use the exception
            message = str(e)
            recommendation = "Check the Properties string format."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            self.logger.warning(warning_message)
            raise CommandParameterError(warning_message)

        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    @classmethod
    def __return_a_list_of_fc(cls, fgdb_full_path: str) -> []:

        # The file geodatabase will be read and each feature class will be added to the feature_class_list.
        feature_class_list = []

        # Append each feature class in the Esri File Geodatabase to the feature_class_list.
        # REF: https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html|
        # "Get all layers in an Esri File GeoDataBase"
        ogr.UseExceptions()
        driver = ogr.GetDriverByName("OpenFileGDB")
        gdb = driver.Open(fgdb_full_path)
        for feature_class_idx in range(gdb.GetLayerCount()):
            feature_class = gdb.GetLayerByIndex(feature_class_idx)
            feature_class_list.append(feature_class.GetName())

        return feature_class_list

    def check_runtime_data_geopackage(self, input_file_absolute: str) -> bool:
        """
        Checks the following:
        * the InputFile (absolute) is a valid file
        * the InputFile (absolute) is a valid File GeoPackage

        Args:
            input_file_absolute (str): the full pathname to the GeoPackage file

        Returns:
             Boolean. If TRUE, the GeoPackage should be read. If FALSE, at least one check failed and the GeoPackage
             fle should not be read.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the input file is not a valid file path, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsFilePathValid", "InputFile",
                                                           input_file_absolute, "FAIL"))

        # TODO smalers 2020-07-12 need to enable
        #if False not in should_run_command:
        #    # If the input spatial data folder is not a geopackage file, raise a FAILURE.
        #    should_run_command.append(validator_util.run_check(self, "IsFolderAfGDB", "InputFolder",
        #                                                       input_file_absolute, "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def check_runtime_data_geolayer(self, geolayer_id: str, one_geolayer_bool: bool, layer_name: str = None,
                                    input_file_absolute: str = None) -> bool:
        """
        Checks the following:
        * if only one geolayer is being read, the FeatureClass is an existing feature class within the File GeoDatabase
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)

        Args:
            geolayer_id (str): the ID of the output GeoLayer
            one_geolayer_bool (bool): if True, the command is only reading one FC from the FGDB
            layer_name (str): the name of the layer being read.  Only used if one_geolayer_bool is True. Default = None
            input_file_absolute (str): the full pathname to the input GeoPackage file,
                only used if one_geolayer_bool is True. Default = None

        Returns:
            Boolean. If TRUE, the GeoLayer should be read. If FALSE, at least one check failed and the GeoLayer
                should not be read.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the GeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE (depends
        # on the value of the IfGeoLayerIDExists parameter.)
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIdUnique", "GeoLayerID", geolayer_id, None))

        # If only one geolayer is being read from the geopackage file, continue.
        # - TODO smalers 2020-07-12 need to enable similar check
        #if one_geolayer_bool:
        #    # If the requested layer is not in the GeoPackage raise a FAILURE.
        #    should_run_command.append(validator_util.run_check(self, "IsFeatureClassInFGDB", "FeatureClass", fc_name,
        #                                                       "FAIL", other_values=[input_folder_absolute]))

        # TODO smalers 2020-07-12 the following does not seem to work, even though layer CAN be read later in code
        one = 2
        if one == 1:
            # List the layers in a GeoPackage, which are "sublayers":
            # - TODO smalers 2020-07-12 need to enable something like this
            # - do this for troubleshooting and initial command development
            # - see: https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/cheat_sheet.html#layers
            # - TODO smalers 2020-07-12 need to isolate this specific code in the qgis_util once figure out
            layer = QgsVectorLayer(input_file_absolute, "list", "org")
            if layer is None:
                self.logger.info("Unable to create GeoPackage layer.")
            else:
                if layer.isValid():
                    self.logger.info("Layer is valid")
                    sub_layers = layer.dataProvider().subLayers()
                    self.logger.info('GeoPackage sub_layers={}'.format(sub_layers))
                    for sub_layer in sub_layers:
                        sub_layer_name = sub_layer.split('!!::!!')[1]
                        sub_layer_uri = "{}|layername={}".format(input_file_absolute, sub_layer_name)
                        self.logger.info('GeoPackage sub_layer URI={}'.format(sub_layer_uri))
                else:
                    self.logger.info("Layer is invalid")

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Read the layer(s) from a GeoPackage file. For each desired layer,
        GeoLayer object, and add to the GeoProcessor's geolayer list.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the required and optional parameter values
        # noinspection PyPep8Naming
        pv_InputFile = self.get_parameter_value("InputFile")
        # noinspection PyPep8Naming
        pv_ReadOneLayer = self.get_parameter_value("ReadOneLayer")
        # noinspection PyPep8Naming
        pv_LayerName = self.get_parameter_value("LayerName")
        # noinspection PyPep8Naming
        pv_Subset_Pattern = self.get_parameter_value("Subset_Pattern")
        # noinspection PyPep8Naming
        pv_GeoLayerID_prefix = self.get_parameter_value("GeoLayerID_prefix")
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        # noinspection PyPep8Naming
        pv_FeatureClass = self.get_parameter_value("FeatureClass")
        # noinspection PyPep8Naming
        pv_Name = self.get_parameter_value("Name")
        # noinspection PyPep8Naming
        pv_Description = \
            self.get_parameter_value("Description",
                                     default_value=self.parameter_input_metadata['Description.Value.Default'])
        # noinspection PyPep8Naming
        pv_Properties = self.get_parameter_value("Properties")

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.command_processor.expand_parameter_value(pv_GeoLayerID, self)
        # noinspection PyPep8Naming
        pv_Name = self.command_processor.expand_parameter_value(pv_Name, self)
        # noinspection PyPep8Naming
        pv_Description = self.command_processor.expand_parameter_value(pv_Description, self)
        if pv_Description is None or pv_Description == "":
            pv_Description = pv_Name
        # noinspection PyPep8Naming
        pv_Properties = self.command_processor.expand_parameter_value(pv_Properties, self)

        # Convert the ReadOneLayer from a string value to a Boolean value.
        # noinspection PyPep8Naming
        pv_ReadOneLayer = string_util.str_to_bool(pv_ReadOneLayer)

        # Convert the InputFile parameter to an absolute path
        input_file_abs = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_InputFile, self)))
        self.logger.info("Reading GeoPackage file = {}".format(input_file_abs))

        # Run the initial checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data_geopackage(input_file_abs):
            # If configured to only read one Feature Class into one GeoLayer.
            if pv_ReadOneLayer:
                # Run the check to see if the GeoLayer should be read.
                if self.check_runtime_data_geolayer(pv_GeoLayerID, True, pv_LayerName, input_file_abs):
                    # noinspection PyBroadException
                    try:
                        # Create a QgsVectorLayer object for the layer and sub-layer.
                        qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_geopackage(input_file_abs,
                                                                                         pv_LayerName,
                                                                                         pv_Description)

                        # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
                        new_geolayer = VectorGeoLayer(geolayer_id=pv_GeoLayerID,
                                                      qgs_vector_layer=qgs_vector_layer,
                                                      name=pv_Name,
                                                      description=pv_Description,
                                                      input_path_full=input_file_abs,
                                                      input_path=pv_InputFile)

                        # Set the properties
                        properties = command_util.parse_properties_from_parameter_string(pv_Properties)
                        # Set the properties as additional properties (don't just reset the properties dictionary)
                        new_geolayer.set_properties(properties)

                        self.command_processor.add_geolayer(new_geolayer)

                    except Exception:
                        # Raise an exception if an unexpected error occurs during the process
                        self.warning_count += 1
                        message = "Unexpected error reading layer ({}) from GeoPackage file ({}).".format(
                            pv_LayerName, input_file_abs)
                        recommendation = "Check the log file for details."
                        self.logger.warning(message, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                        recommendation))

            else:
                # If configured to read multiple Feature Classes into multiple GeoLayers.
                # TODO smalers 2020-07-12 currently not supported, need to convert to GeoPackage

                self.warning_count += 1
                message = "Reading multiple layers from a GeoPackage file is currently not supported"
                recommendation = "Read individual layers."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                recommendation))
                raise CommandError(message)

                # Get a list of all of the feature classes in the file geodatabase.
                fc_list = ReadGeoLayersFromGeoPackage.__return_a_list_of_fc(sd_folder_abs)

                # Filter the fc_list to only include feature classes that meet the Subset Pattern configuration.
                # If the Subset Pattern configuration is None, all feature classes will remain in the fc_list.
                fc_list = string_util.filter_list_of_strings(fc_list, [pv_Subset_Pattern])

                # Iterate over the feature classes in the fc_list.
                for feature_class in fc_list:
                    # Determine the GeoLayerID.
                    if pv_GeoLayerID_prefix:
                        geolayer_id = "{}_{}".format(pv_GeoLayerID_prefix, feature_class)
                    else:
                        geolayer_id = feature_class

                    # Run the secondary checks on the parameter values. Only continue if the checks passed.
                    if self.check_runtime_data_geolayer(geolayer_id, False):
                        # noinspection PyBroadException
                        try:
                            # Get the full pathname to the feature class
                            # TODO egiles 2018-01-04 Need to research how to properly document feature class source path
                            input_file_absolute = os.path.join(sd_folder_abs, str(feature_class))

                            # Create a QgsVectorLayer object from the feature class.
                            qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_feature_class(sd_folder_abs,
                                                                                                feature_class)

                            # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
                            geolayer_obj = VectorGeoLayer(geolayer_id=geolayer_id,
                                                          qgs_vector_layer=qgs_vector_layer,
                                                          name=pv_Name,
                                                          description=pv_Description,
                                                          input_path_full=input_file_absolute,
                                                          input_path=pv_InputFolder)
                            self.command_processor.add_geolayer(geolayer_obj)

                        except Exception:
                            # Raise an exception if an unexpected error occurs during the process

                            self.warning_count += 1
                            message = "Unexpected error reading feature class ({}) from file geodatabase ({}).".format(
                                feature_class, sd_folder_abs)
                            recommendation = "Check the log file for details."
                            self.logger.warning(message, exc_info=True)
                            self.command_status.add_to_log(CommandPhaseType.RUN,
                                                           CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                            recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
