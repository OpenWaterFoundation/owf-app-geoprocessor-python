# SplitGeoLayerByAttribute - command to split a GeoLayer into multiple GeoLayers based on an attribute's values
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

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType
from geoprocessor.core.VectorGeoLayer import VectorGeoLayer
from processing.core.Processing import Processing
from qgis.core import QgsVectorLayer, QgsProject

import glob
import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validators
import geoprocessor.util.qgis_util as qgis_util
import logging
import os
import tempfile


class SplitGeoLayerByAttribute(AbstractCommand):
    """
    Splits a VectorGeoLayer into multiple VectorGeoLayer based on the VectorGeoLayer's attribute values.
    This command takes a VectorGeoLayer and an attribute and generates a set of VectorGeoLayers.
    Each new VectorGeoLayer contains all features from the input VectorGeoLayer with the
    same value for the specified attribute.  The number of VectorGeoLayer generated is equal to the number of
    unique values found for the specified attribute.
    Command Parameters
    * InputGeoLayerID (str, required): the ID of the input VectorGeoLayer, the layer to be split.
    * AttributeName (str, required): the name of the attribute to split on. Must be a unique attribute
         name of the VectorGeoLayer.
    * OutputGeoLayerIDs (str, optional): the IDs of the VectorGeoLayer created as the output split layers.
        By default the GeoLayerID of the output layers will be {}_splitBy_{} where the first
        variable is the InputGeoLayerID and the second variable is the AttributeName value.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the OutputGeoLayerIDs
        already exist within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("InputGeoLayerID", type("")),
        CommandParameterMetadata("AttributeName", type("")),
        CommandParameterMetadata("OutputGeoLayerIDs", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type("")),
        CommandParameterMetadata("TemporaryFolder", type(""))]
        #CommandParameterMetadata("RemoveTemporaryFiles", type(""))]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "SplitGeoLayerByAttribute"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = \
            "Split an input GeoLayer into one or more new GeoLayers by unique attribute value.\n" \
            'For example, if the specified attribute name has unique values "a", "b", and "c", three layers will ' \
            "be created."
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # InputGeoLayerID
        self.parameter_input_metadata['InputGeoLayerID.Description'] = 'input GeoLayer identifier'
        self.parameter_input_metadata['InputGeoLayerID.Label'] = "Input GeoLayerID"
        self.parameter_input_metadata['InputGeoLayerID.Required'] = True
        self.parameter_input_metadata['InputGeoLayerID.Tooltip'] = "Input GeoLayer identifier."
        # AttributeName
        self.parameter_input_metadata['AttributeName.Description'] = "attribute name to split by"
        self.parameter_input_metadata['AttributeName.Label'] = "Attribute name"
        self.parameter_input_metadata['AttributeName.Required'] = True
        self.parameter_input_metadata['AttributeName.Tooltip'] = "The attribute name that will be used to " \
            "split the input GeoLayer."
        # OutputGeoLayerIDs
        self.parameter_input_metadata['OutputGeoLayerIDs.Description'] = "the identifiers of the output GeoLayers"
        self.parameter_input_metadata['OutputGeoLayerIDs.Label'] = "Output GeoLayerIDs"
        self.parameter_input_metadata['OutputGeoLayerIDs.Tooltip'] = "The identifiers of the output GeoLayers."
        self.parameter_input_metadata['OutputGeoLayerIDs.Value.Default'] = \
            "The default Output GeoLayerID will be of the format 'InputGeoLayerID-AttributeValue'.\nThe attribute " \
            "value being the resulting value identified from the AttributeName."
        # IfGeoLayerIDExists
        self.parameter_input_metadata['IfGeoLayerIDExists.Description'] = "action if output layer exists"
        self.parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID exists"
        self.parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = (
            "The action that occurs if the GeoLayerID already exists within the GeoProcessor.\n"
            "Replace : The existing GeoLayer within the GeoProcessor is overwritten with the new"
            "GeoLayer. No warning is logged.\n"
            "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new "
            "GeoLayer. A warning is logged. \n"
            "Warn : The new GeoLayer is not created. A warning is logged. \n"
            "Fail : The new GeoLayer is not created. A fail message is logged.")
        self.parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
        self.parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"
        # TemporaryFolder
        self.parameter_input_metadata['TemporaryFolder.Description'] = "temporary location for output files"
        self.parameter_input_metadata['TemporaryFolder.Label'] = "Temporary files folder"
        self.parameter_input_metadata['TemporaryFolder.Tooltip'] = \
            "Specify the folder for temporary files, useful for troubleshooting. See the documentation."
        self.parameter_input_metadata['TemporaryFolder.Value.Default'] = "default temporary folder directory"
        self.parameter_input_metadata['TemporaryFolder.FileSelector.Title'] = \
            "Select the folder for temporary files"
        self.parameter_input_metadata['TemporaryFolder.FileSelector.SelectFolder'] = True
        self.parameter_input_metadata['TemporaryFolder.FileSelector.Type'] = "Write"
        # RemoveTemporaryFiles
        # self.parameter_input_metadata['RemoveTemporaryFiles.Description'] = "remove temporary files"
        # self.parameter_input_metadata['RemoveTemporaryFiles.Label'] = "Remove temporary files"
        # self.parameter_input_metadata['RemoveTemporaryFiles.Tooltip'] = \
        #     "True (default): remove the temporary files created behind the scenes.\n" \
        #     "False: leave the files so that they can be reviewed."
        # self.parameter_input_metadata['RemoveTemporaryFiles.Value.Default'] = "True"
        # self.parameter_input_metadata['RemoveTemporaryFiles.Values'] = ["", "True", "False"]

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters: dict) -> None:
        """
        Check the command parameters for validity.
        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)
        Returns:
            None.
        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning = ""

        # Check that parameter InputGeoLayerID is a non-empty, non-None string.
        pv_InputGeoLayerID = self.get_parameter_value(parameter_name='InputGeoLayerID',
                                                      command_parameters=command_parameters)

        if not validators.validate_string(pv_InputGeoLayerID, False, False):
            message = "InputGeoLayerID parameter has no value."
            recommendation = "Specify the InputGeoLayerID parameter to indicate the input GeoLayer."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that parameter AttributeName is a non-empty, non-None string.
        pv_AttributeName = self.get_parameter_value(parameter_name='AttributeName',
                                                    command_parameters=command_parameters)

        if not validators.validate_string(pv_AttributeName, False, False):

            message = "AttributeName parameter has no value."
            recommendation = "Specify the AttributeName parameter to indicate the attribute to split on."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional parameter IfGeoLayerIDExists is either `Replace`, `Warn`, `Fail` or None.
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        acceptable_values = ["Replace", "Warn", "Fail", "ReplaceAndWarn"]
        if not validators.validate_string_in_list(pv_IfGeoLayerIDExists, acceptable_values, none_allowed=True,
                                                  empty_string_allowed=True, ignore_case=True):
            message = "IfGeoLayerIDExists parameter value ({}) is not recognized.".format(pv_IfGeoLayerIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfGeoLayerIDExists parameter.".format(
                acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_command_input(self, input_geolayer_id: str, attribute_name: str, output_geolayer_ids: [str]) -> bool:
        """
        Checks the following:
        * the ID of the input GeoLayer is an existing GeoLayer ID
        * the attribute name is a valid name for the GeoLayer (if not, log an error message & do not continue.)
        * the IDs of the output GeoLayers are unique (not an existing GeoLayer ID)
        Args:
            input_geolayer_id: the ID of the input GeoLayer
            attribute_name (str): the name of the attribute in which to split the GeoLayer
            output_geolayer_ids: the IDs of the output GeoLayers
        Returns:
             Boolean. If TRUE, the GeoLayer should be split. If FALSE, at least one check failed and the GeoLayer
                should not be split.
        """

        logger = logging.getLogger(__name__)
        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []


        # If the input GeoLayerID is not an existing GeoLayerID, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsGeoLayerIDExisting", "InputGeoLayerID",
                                                       input_geolayer_id, "FAIL"))

        # If the input GeoLayer exists, continue with the checks.
        if False not in should_run_command:

            # Get the input GeoLayer object.
            input_geolayer = self.command_processor.get_geolayer(input_geolayer_id)

            # Get the attribute names of the input GeoLayer.
            list_of_attributes = input_geolayer.get_attribute_field_names()
            for i_attribute_name in list_of_attributes:
                logger.info('Input layer has attribute "' + str(i_attribute_name) + '"')

            # If the attribute name is not valid, raise a FAILURE.
            if attribute_name not in list_of_attributes:
                self.warning_count += 1
                message = 'The attribute name ({}) is not valid.'.format(attribute_name)
                recommendation = 'Specify a valid attribute name. Valid attributes for this layer are as follows: ' \
                                 '{}'.format(list_of_attributes)
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
            logger.info('Found attribute "' + attribute_name + '" in input layer attributes')

            # If the OutputGeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE (depends
            # on the value of the IfGeoLayerIDExists parameter.)
            should_run_command.append(validators.run_check(self, "IsGeoLayerIdUnique", "OutputGeoLayerID",
                                                           output_geolayer_ids, None))

            # Return the Boolean to determine if the process should be run.
            if False in should_run_command:
                return False
            else:
                return True
        else:
            return True
            logger.info('Process can be run')

    def run_command(self) -> None:
        """
        Run the command. Split the input GeoLayer by the selected Attribute. Create new GeoLayers based on
        unique attribute values.
        Returns:
            None.
        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.

        # @jurentie
        # 1. Parameter values are passed into the SplitGeoLayerByAttribute command editor -> GenericCommandEditor
        # 2. The SplitGEoLayerByAttribute command is updated when user changes input to parameter
        #    and parsed by AbstractCommand into parameter values and saved as command_parameters.
        # 3. Obtain parameter value by calling parent function get_parameter_value from AbstractCommand

        # Get the 'Input GeoLayerID' parameter
        pv_InputGeoLayerID = self.get_parameter_value("InputGeoLayerID")
        pv_AttributeName = self.get_parameter_value("AttributeName")

        # TODO jurentie 01/26/2019 Need to figure out how default should work in this case
        # @jurentie
        # I've commented out the below, this is specific to ClipGeoLayer, creating a default
        # value that makes sense for 'Value_splityBy_value' but we are looking for Output GeoLayerID's for this
        # specific command. Default might just need to be the name of the file's automatically output by
        # runAlgorithm("qgis:splitvectorlayer", alg_parameters) which can be handled down below...

        # pv_OutputGeoLayerIDs = self.get_parameter_value("OutputGeoLayerIDs", default_value="{}_splitBy_{}".format(
        #     pv_InputGeoLayerID, pv_AttributeName))

        # Get OutputGeoLayerID's and split on ',' to create an array of Output GeoLayerId's
        # ex OutputGeoLayerIDs = 'ouput1, output1, output3'
        # pv_OutputGeoLayerIDs = ['output1', 'output2', 'output3']
        try:
            pv_OutputGeoLayerIDs = self.get_parameter_value("OutputGeoLayerIDs").split(',')
        except:
            # Get the list of features from the GeoLayer. This returns all attributes for each feature listed.
            pv_OutputGeoLayerIDs = None

        # Create logger
        logger = logging.getLogger(__name__)

        # Run the checks on the parameter values. Only continue if the checks passed.

        # @jurentie
        # The following line is currently commented out but needs to be added back in once
        # __should_split_geolayer is functioning properly...

        if self.check_command_input(pv_InputGeoLayerID, pv_AttributeName, pv_OutputGeoLayerIDs):

            try:

                # Get the Input GeoLayer.

                # Get the GeoLayer which will be QgsVectorLayer
                # https://qgis.org/api/classQgsVectorLayer.html
                # Passes a GeoLayerID to GeoProcessor to return the GeoLayer that matches the ID
                input_geolayer = self.command_processor.get_geolayer(pv_InputGeoLayerID)

                logger.info('Input GeoLayer [GeoLayerID: ' + pv_InputGeoLayerID + '] has been read in successfully')

                # TODO jurentie 01/26/2019 still need to figure out what the code below is for...
                # If the input GeoLayer is an in-memory GeoLayer, make it an on-disk GeoLayer.
                if input_geolayer.source_path is None or input_geolayer.source_path.upper() in ["", "MEMORY"]:

                    # Get the absolute path of the GeoLayer to write to disk.
                    geolayer_disk_abs_path = os.path.join(self.command_processor.get_property('TempDir'), input_geolayer.id)
                    logger.info('GeoLayer path ' + geolayer_disk_abs_path)
                    # Write the GeoLayer to disk. Overwrite the (memory) GeoLayer in the geoprocessor with the
                    # on-disk GeoLayer.
                    input_geolayer = input_geolayer.write_to_disk(geolayer_disk_abs_path)
                    self.command_processor.add_geolayer(input_geolayer)

                # Select the Attribute
                # NEED TO CREATE A 'input_geolayer.select_attribute' FUNCTION IN GEOLAYER.PY??
                # SOMETHING LIKE:  attribute_name = input_geolayer.select_attribute(pv_AttributeName)
                # OR SHOULD THE FOLLOWING JUST WORK?
                attribute_name = pv_AttributeName
                working_dir = self.command_processor.properties['WorkingDir']


                # @jurentie
                # TODO @jurentie 01/31/2019 How to handle absolute path
                # Assuming relative path for the moment....

                # Perform the QGIS split vector layer function. Refer to the reference below for parameter descriptions.
                # REF: https://docs.qgis.org/2.8/en/docs/user_manual/processing_algs/qgis/vector_general_tools.html#split-vector-layer

                # @jurentie
                # Check to see if parameter temporary folder has been specified, otherwise use the
                # default environment temp folder directory.

                #boolean to see if working with custom temp folder
                temp_directory_custom = False
                try:
                    # Append specified temporary folder to working directory to create temp files in current
                    # command file location.
                    temp_directory = working_dir + "/" + self.get_parameter_value("TemporaryFolder")
                    temp_directory_custom = True
                except:
                    # If using the default temp directory from environment variables create a temp folder to
                    # easily remove all files
                    temp_directory = tempfile.gettempdir()
                    temp_directory += "/qgissplitvectorlayer-outputfiles"
                # @jurentie
                # Assign parameter to pass into runAlgorithm for splitting the GeoLayer
                # Input = input GeoLayer (QgsVectorLayer)
                # Field = Attribute name to split by
                # Output = path to write output GeoLayers to this creates a list of files following the naming
                #          convention attributeName_attribute.extension
                #          ex: GNIS_ID_00030007.shp
                #          file types generated = .dbf, .prj, .qpj, .shp, .shx
                alg_parameters = {"INPUT": input_geolayer.qgs_layer,
                                  "FIELD": attribute_name,
                                  "OUTPUT": temp_directory}
                # @jurentie
                # call runAlgorithm with the parameter "qgis:splitvectorlayer" (a list of possible parameters
                # that can be passed here can be found here
                # https://gist.github.com/jurentie/7b6c53d5a592991b6bb2491fcc5f01eb)
                # pass in the parameters defined above
                # This should result in separate GeoLayer shapefiles being written to the OUTPUT directory
                split_output = self.command_processor.qgis_processor.runAlgorithm("qgis:splitvectorlayer", alg_parameters)

                # Create new GeoLayers and add them to the GeoProcessor's geolayers list.

                # @jurentie
                # TODO jurentie 01/26/2019 There probably needs to be some error handling happening below
                # Get the list of features from the GeoLayer. This returns all attributes for each feature listed.
                features = input_geolayer.qgs_layer.getFeatures()
                # Set the extension for the filename's to get the geolayer from
                filename_extension = ".shp"
                # Parse through the list of features and also enumerate to get the index which
                # is used for accessing which OutputGeoLayerIDs to name each GeoLayer.
                # TODO jurentie 01/26/2019 need to decide what to do with a default OutputGeoLayerIDs
                # 1. Get the attribute of interest from each feature
                # TODO jurentie 01/26/2019 need to handle parsing out unique attributes only...
                # 2. Create the path name using the output folder specified in alg_parameters and passed in to
                #    split_output, and the naming convention defaults for qgis:splitvectorlayer
                # 3. Construct a QgsVectorLayer()
                #    Parameters:
                #       path: The path or url of the parameter. Typically this encodes parameters used by the data
                #       provider as url query items.
                #       baseName: The name used to represent the layer in the legend
                #       providerLib: The name of the data provider, e.g., "memory", "postgres"
                #       options: layer load options
                #    For more info see:
                #       https://qgis.org/api/classQgsVectorLayer.html#a1e7827a9d7bd33549babdc3bd7a279fd
                # 4. Construct a new GeoLayer from the QgsVectorLayer()
                #    Parameters:
                #       geolayer_id (str): String that is the GeoLayer's reference ID. This ID is used to access the
                #       GeoLayer from the GeoProcessor for manipulation.
                #       geolayer_qgs_vector_layer (QGSVectorLayer): Object created by the QGIS processor.
                #       All GeoLayer spatial manipulations are performed on the GeoLayer's qgs_vector_layer.
                #       geolayer_source_path (str): The full pathname to the original spatial data file on the
                #       user's local computer. If the geolayer was made in memory from the GeoProcessor, this value
                #       is set to `MEMORY`.
                # 5. Add the new GeoLayer to the GeoProcessor
                for i, feature in enumerate(features):
                    attribute = feature[attribute_name]
                    path = temp_directory + "/" + attribute_name + "_" + str(attribute) + filename_extension
                    layer = QgsVectorLayer(path, "layer" + str(attribute), "ogr")
                    try:
                        new_geolayer = VectorGeoLayer(geolayer_id=pv_OutputGeoLayerIDs[i],
                                                      geolayer_qgs_vector_layer=layer,
                                                      geolayer_source_path=path)
                    except:
                        # Default Output GeoLayerID's will be default title of output files from .runAlgorithm above
                        new_geolayer = VectorGeoLayer(geolayer_id=pv_InputGeoLayerID + "-" + str(attribute),
                                                      geolayer_qps_vector_layer=layer,
                                                      geolayer_source_path=path)
                    self.command_processor.add_geolayer(new_geolayer)

                # @jurentie
                # remove files if specified in parameters
                # TODO @jurentie figure out how to delete files after using them...
                # remove_files = self.get_parameter_value("RemoveTemporaryFiles")
                # files = glob.glob(temp_directory + "/*")
                # print(files)
                # if remove_files == None:
                #     # Remove all files from directory
                #     for f in files:
                #         os.remove(f)
                #     os.rmdir(temp_directory)

                # In QGIS 2 the clipped_output["OUTPUT"] returned the full file pathname of the memory output layer
                # (saved in a QGIS temporary folder)
                # qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_file(clipped_output["OUTPUT"])
                # new_geolayer = VectorGeoLayer(pv_OutputGeoLayerID, qgs_vector_layer, "MEMORY")
                # Get this list of ID's, name can be changed later to make more sense
                # in a dynamic fashion

                # In QGIS 3 the clipped_output["OUTPUT"] returns the QGS vector layer object
                # new_geolayer = VectorGeoLayer(pv_OutputGeoLayerIDs, split_output["OUTPUT"], "MEMORY")
                # self.command_processor.add_geolayer(new_geolayer)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error splitting GeoLayer {}.".format(
                    pv_InputGeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
