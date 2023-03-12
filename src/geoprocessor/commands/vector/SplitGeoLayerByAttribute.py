# SplitGeoLayerByAttribute - command to split a GeoLayer into multiple GeoLayers based on an attribute's values
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2023 Open Water Foundation
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

from geoprocessor.core.CommandError import CommandError
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType
from geoprocessor.core.QGISAlgorithmProcessingFeedbackHandler import QgisAlgorithmProcessingFeedbackHandler
from geoprocessor.core.VectorGeoLayer import VectorGeoLayer
# from processing.core.Processing import Processing
from qgis.core import QgsVectorLayer

# import glob
import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.validator_util as validator_util
import logging
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
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("InputGeoLayerID", type("")),
        CommandParameterMetadata("AttributeName", type("")),
        CommandParameterMetadata("IncludeAttributeValues", type("")),
        CommandParameterMetadata("ExcludeAttributeValues", type("")),
        CommandParameterMetadata("OutputGeoLayerID", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type("")),
        CommandParameterMetadata("TemporaryFolder", type(""))]
    # CommandParameterMetadata("RemoveTemporaryFiles", type(""))]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = \
        "Split an input GeoLayer into one or more new GeoLayers by unique attribute value.\n" \
        'For example, if the specified attribute name has unique values "a", "b", and "c", three layers will ' \
        'be created.\n'  \
        'The attribute values being processed can be filtered to limit the number of output layers.'
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()

    # InputGeoLayerID
    __parameter_input_metadata['InputGeoLayerID.Description'] = 'input GeoLayer identifier'
    __parameter_input_metadata['InputGeoLayerID.Label'] = "Input GeoLayerID"
    __parameter_input_metadata['InputGeoLayerID.Required'] = True
    __parameter_input_metadata['InputGeoLayerID.Tooltip'] = "Input GeoLayer identifier."

    # AttributeName
    __parameter_input_metadata['AttributeName.Description'] = "attribute name to split by"
    __parameter_input_metadata['AttributeName.Label'] = "Attribute name"
    __parameter_input_metadata['AttributeName.Required'] = True
    __parameter_input_metadata['AttributeName.Tooltip'] = "The attribute name that will be used to " \
                                                          "split the input GeoLayer."

    # IncludeAttributeValues
    __parameter_input_metadata['IncludeAttributeValues.Description'] = "attribute values to include"
    __parameter_input_metadata['IncludeAttributeValues.Label'] = "Include attribute values"
    __parameter_input_metadata['IncludeAttributeValues.Required'] = False
    __parameter_input_metadata['IncludeAttributeValues.Tooltip'] = "Attribute values to include, separated by commas."
    __parameter_input_metadata['IncludeAttributeValues.Value.Default'] = '*'

    # ExcludeAttributeValues
    __parameter_input_metadata['ExcludeAttributeValues.Description'] = "attribute values to exclude"
    __parameter_input_metadata['ExcludeAttributeValues.Label'] = "Exclude attribute values"
    __parameter_input_metadata['ExcludeAttributeValues.Required'] = False
    __parameter_input_metadata['ExcludeAttributeValues.Tooltip'] =\
        "Attribute values to exclude (after processing included attributes), separated by commas."

    # OutputGeoLayerID
    __parameter_input_metadata['OutputGeoLayerID.Description'] = "the output GeoLayerID pattern (currently ignored)"
    __parameter_input_metadata['OutputGeoLayerID.Label'] = "Output GeoLayerID"
    __parameter_input_metadata['OutputGeoLayerID.Tooltip'] = "The output GeoLayerID." \
        "The default output GeoLayerID will be of the format 'InputGeoLayerID_AttributeName_AttributeValue'."
    __parameter_input_metadata['OutputGeoLayerID.Value.Default'] = "see tooltip"

    # IfGeoLayerIDExists
    __parameter_input_metadata['IfGeoLayerIDExists.Description'] = "action if output layer exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = (
        "The action that occurs if the GeoLayerID already exists within the GeoProcessor.\n"
        "Replace : The existing GeoLayer within the GeoProcessor is overwritten with the new"
        "GeoLayer. No warning is logged.\n"
        "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new "
        "GeoLayer. A warning is logged. \n"
        "Warn : The new GeoLayer is not created. A warning is logged. \n"
        "Fail : The new GeoLayer is not created. A fail message is logged.")
    __parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
    __parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"

    # TemporaryFolder
    __parameter_input_metadata['TemporaryFolder.Description'] = "temporary location for output files"
    __parameter_input_metadata['TemporaryFolder.Label'] = "Temporary files folder"
    __parameter_input_metadata['TemporaryFolder.Tooltip'] = \
        "Folder for temporary output layer files, useful for troubleshooting. See the documentation."
    __parameter_input_metadata['TemporaryFolder.Value.Default'] = "default temporary folder directory"
    __parameter_input_metadata['TemporaryFolder.FileSelector.Title'] = \
        "Select the folder for temporary files"
    __parameter_input_metadata['TemporaryFolder.FileSelector.SelectFolder'] = True
    __parameter_input_metadata['TemporaryFolder.FileSelector.Type'] = "Write"

    # TODO smalers 2020-07-07 evaluate whether to enable the parameter:
    #  - by default leave temporary files so they can be reviewed.
    # RemoveTemporaryFiles
    # self.parameter_input_metadata['RemoveTemporaryFiles.Description'] = "remove temporary files"
    # self.parameter_input_metadata['RemoveTemporaryFiles.Label'] = "Remove temporary files"
    # self.parameter_input_metadata['RemoveTemporaryFiles.Tooltip'] = \
    #     "True (default): remove the temporary files created behind the scenes.\n" \
    #     "False: leave the files so that they can be reviewed."
    # self.parameter_input_metadata['RemoveTemporaryFiles.Value.Default'] = "True"
    # self.parameter_input_metadata['RemoveTemporaryFiles.Values'] = ["", "True", "False"]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data.
        super().__init__()
        self.command_name = "SplitGeoLayerByAttribute"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display.
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata.
        self.parameter_input_metadata = self.__parameter_input_metadata

        # Class data.
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

        # Check that optional parameter IfGeoLayerIDExists is either `Replace`, `Warn`, `Fail` or None.
        # noinspection PyPep8Naming
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        acceptable_values = ["Replace", "Warn", "Fail", "ReplaceAndWarn"]
        if not validator_util.validate_string_in_list(pv_IfGeoLayerIDExists, acceptable_values, none_allowed=True,
                                                      empty_string_allowed=True, ignore_case=True):
            message = "IfGeoLayerIDExists parameter value ({}) is not recognized.".format(pv_IfGeoLayerIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfGeoLayerIDExists parameter.".format(
                acceptable_values)
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
            # Refresh the phase severity.
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, input_geolayer_id: str, attribute_name: str, output_geolayer_ids: [str]) -> bool:
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
        # List of Boolean values. The Boolean values correspond to the results of the following tests.
        # If TRUE, the test confirms that the command should be run.
        should_run_command = list()

        # If the input GeoLayerID is not an existing GeoLayerID, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIDExisting", "InputGeoLayerID",
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

            # If the OutputGeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE
            # (depends on the value of the IfGeoLayerIDExists parameter).
            should_run_command.append(validator_util.run_check(self, "IsGeoLayerIdUnique", "OutputGeoLayerID",
                                                               output_geolayer_ids, None))

            # Return the Boolean to determine if the process should be run.
            if False in should_run_command:
                return False
            else:
                return True
        else:
            logger.info('Process can be run')
            return True

    def is_attribute_included(self, attribute_value: str,
                              include_attribute_values: [str],
                              exclude_attribute_values: [str]) -> bool:
        """
        Determine whether to include an attribute based on the include and exclude lists.

        Args:
            attribute_value (str) - the attribute value to check, as a string
            include_attribute_values ([str]) - the list of attribute values to include
            exclude_attribute_values ([str]) - the list of attribute values to exclude
        """
        include = False
        # First see if in the include list.
        if len(include_attribute_values) == 0:
            # Default is to include all.
            include = True
        else:
            # Specific attributes are included.
            for include_attribute_value in include_attribute_values:
                if attribute_value == include_attribute_value:
                    include = True
                    break
        # Next see if in the exclude list.
        for exclude_attribute_value in exclude_attribute_values:
            if attribute_value == exclude_attribute_value:
                include = False
                break
        return include

    def run_command(self) -> None:
        """
        Run the command. Split the input GeoLayer by the selected Attribute.
        Create new GeoLayers based on unique attribute values.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.

        # Get the 'Input GeoLayerID' parameter.
        # noinspection PyPep8Naming
        pv_InputGeoLayerID = self.get_parameter_value("InputGeoLayerID")
        # noinspection PyPep8Naming
        pv_AttributeName = self.get_parameter_value("AttributeName")
        # noinspection PyPep8Naming
        pv_IncludeAttributeValues = self.get_parameter_value("IncludeAttributeValues")
        include_attribute_values = []
        if pv_IncludeAttributeValues is not None and pv_IncludeAttributeValues != "":
            include_attribute_values = pv_IncludeAttributeValues.split(',')
            for i in range(len(include_attribute_values)):
                include_attribute_values[i] = include_attribute_values[i].strip()
        # noinspection PyPep8Naming
        pv_ExcludeAttributeValues = self.get_parameter_value("ExcludeAttributeValues")
        exclude_attribute_values = []
        if pv_ExcludeAttributeValues is not None and pv_ExcludeAttributeValues != "":
            exclude_attribute_values = pv_ExcludeAttributeValues.split(',')
            for i in range(len(include_attribute_values)):
                exclude_attribute_values[i] = exclude_attribute_values[i].strip()
        # noinspection PyPep8Naming
        pv_TemporaryFolder = self.get_parameter_value("TemporaryFolder")

        # Get the temporary folder based on TemporaryFolder parameter.
        if pv_TemporaryFolder is not None and pv_TemporaryFolder != "":
            # Convert the TemporaryFolder parameter value to an absolute path and expand for ${Property} syntax.
            temp_folder_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                         self.command_processor.expand_parameter_value(
                                             pv_TemporaryFolder, self)))
        else:
            # If using the default temp directory from environment variables create a temp folder.
            temp_folder_absolute = tempfile.gettempdir()
            temp_folder_absolute += "/qgissplitvectorlayer-outputfiles"

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
        # noinspection PyBroadException
        try:
            # noinspection PyPep8Naming
            pv_OutputGeoLayerIDs = self.get_parameter_value("OutputGeoLayerIDs").split(',')
        except Exception:
            # Get the list of features from the GeoLayer. This returns all attributes for each feature listed.
            # noinspection PyPep8Naming
            pv_OutputGeoLayerIDs = None

        # Create logger.
        logger = logging.getLogger(__name__)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(pv_InputGeoLayerID, pv_AttributeName, pv_OutputGeoLayerIDs):
            # noinspection PyBroadException
            try:
                # Get the Input GeoLayer.

                # Get the GeoLayer which will be QgsVectorLayer.
                # https://qgis.org/api/classQgsVectorLayer.html
                # Passes a GeoLayerID to GeoProcessor to return the GeoLayer that matches the ID.
                input_geolayer = self.command_processor.get_geolayer(pv_InputGeoLayerID)

                logger.info('Input GeoLayer [GeoLayerID: ' + pv_InputGeoLayerID + '] has been found.')

                attribute_name = pv_AttributeName

                # Perform the QGIS split vector layer function. Refer to the reference below for parameter descriptions.
                # REF: https://docs.qgis.org/
                # 2.8/en/docs/user_manual/processing_algs/qgis/vector_general_tools.html#split-vector-layer
                # TODO smalers 2020-07-07 the QGIS documentation is bad.

                # Assign parameter to pass into runAlgorithm for splitting the GeoLayer:
                # INPUT = input GeoLayer (QgsVectorLayer)
                # FIELD = Attribute name to split by
                # OUTPUT = path to write output GeoLayers to this creates a list of files following the naming
                #          convention attributeName_attributeValue.extension
                #          ex: GNIS_ID_00030007.shp
                #          The default format for QGIS 3.10 is GeoPackage with .gpkg extension.
                #          There is discussion that the format (via extension) should be able to be specified,
                #          but go with GeoPackage.
                alg_parameters = {"INPUT": input_geolayer.qgs_layer,
                                  "FIELD": attribute_name,
                                  "OUTPUT": temp_folder_absolute}
                # Call runAlgorithm with the parameter "qgis:splitvectorlayer" pass in the parameters defined above.
                # This should result in separate GeoLayer files written to the OUTPUT directory.
                # Unfortunately, there is no way to limit which attributes are processed until after the split occurs,
                # so additional work will be done and unneeded files will be created.
                feedback_handler = QgisAlgorithmProcessingFeedbackHandler(self)
                split_output = qgis_util.run_processing(processor=self.command_processor.qgis_processor,
                                                        algorithm="qgis:splitvectorlayer",
                                                        algorithm_parameters=alg_parameters,
                                                        feedback_handler=feedback_handler)
                self.warning_count += feedback_handler.get_warning_count()

                # Get the list of features from the input GeoLayer. This returns all attributes for each feature listed:
                # - this is used to determine the attribute values used below to create layers
                # - returns a QgsFeatureIterator
                features = input_geolayer.qgs_layer.getFeatures()
                num_features = input_geolayer.qgs_layer.featureCount()
                # TODO smalers 2020-07-07 Make sure that the number of output GeoLayerID match the features to include.
                # for i, feature in enumerate(features):
                #    #attribute = feature[attribute_name]

                # Create new GeoLayers and add them to the GeoProcessor's geolayers list.
                # Set the extension for the filenames for created layers, which will indicate the layer format.
                filename_extension = ".gpkg"

                # Parse through the list of features in the input layer and also enumerate to get the index which
                # is used for accessing which OutputGeoLayerIDs to name each GeoLayer.
                # TODO jurentie 01/26/2019 need to decide what to do with a default OutputGeoLayerIDs:
                # 1. Get the attribute of interest from each feature
                # TODO jurentie 01/26/2019 need to handle parsing out unique attributes only:
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

                # Get the list of attributes to process:
                # - sort the attributes so that when added as GeoLayer they are easier to review
                attributes_to_process = []
                for i, feature in enumerate(features):
                    attribute = feature[attribute_name]
                    attribute_str = str(attribute)
                    # logger.info("Checking attribute \"" + attribute_name + "\" value \"" + attribute_str + "\"")
                    if self.is_attribute_included(attribute_str, include_attribute_values, exclude_attribute_values):
                        # logger.info("Attribute is included for split processing.")
                        # The attribute is OK to be processed.
                        # Make sure to only process the layer once for its matching attribute.
                        found = False
                        for attribute_to_process in attributes_to_process:
                            if attribute_str == attribute_to_process:
                                found = True
                                break
                        # Indicate that attribute has been processed.
                        if not found:
                            # Have a new attribute to process.
                            attributes_to_process.append(attribute_str)

                # Sort the attributes.
                attributes_to_process.sort()

                # Now process the attributes that are to be included.
                for attribute_str in attributes_to_process:
                    # The attribute was not previously processed so create the layer from the file.
                    logger.info("Attribute has not previously been processed... so read the split file.")
                    split_file_path = temp_folder_absolute + "/" + attribute_name + "_" + attribute_str +\
                       filename_extension
                    logger.info("Reading temporary split output file into GeoLayer: " + split_file_path)
                    layer = QgsVectorLayer(split_file_path, "layer" + attribute_str, "ogr")
                    geolayer_id = input_geolayer.id + "_" + attribute_name + "_" + attribute_str
                    logger.info("Creating GeoLayerID: " + geolayer_id)
                    # noinspection PyBroadException
                    # Use the ID for the name until more control is added.
                    # Currently only support default output GeoLayerID.
                    new_geolayer = VectorGeoLayer(geolayer_id=geolayer_id,
                                                  name=geolayer_id,
                                                  qgs_vector_layer=layer,
                                                  input_path_full=split_file_path,
                                                  input_path=split_file_path)
                    self.command_processor.add_geolayer(new_geolayer)

                # TODO smalers 2020-07-12 need to enable removing the temporary split files,
                # but workflow will neeed to copy or read/write to another location.
                # @jurentie
                # Remove files if specified in parameters.
                # TODO @jurentie figure out how to delete files after using them.
                # remove_files = self.get_parameter_value("RemoveTemporaryFiles")
                # files = glob.glob(temp_directory + "/*")
                # print(files)
                # if remove_files == None:
                #     # Remove all files from directory.
                #     for f in files:
                #         os.remove(f)
                #     os.rmdir(temp_directory)

                # In QGIS 2 the clipped_output["OUTPUT"] returned the full file pathname of the memory output layer
                # (saved in a QGIS temporary folder).
                # qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_file(clipped_output["OUTPUT"])
                # new_geolayer = VectorGeoLayer(pv_OutputGeoLayerID, qgs_vector_layer, GeoLayer.SOURCE_MEMORY)
                # Get this list of ID's, name can be changed later to make more sense in a dynamic fashion.

                # In QGIS 3 the clipped_output["OUTPUT"] returns the QGS vector layer object.
                # new_geolayer = VectorGeoLayer(pv_OutputGeoLayerIDs, split_output["OUTPUT"], GeoLayer.SOURCE_MEMORY)
                # self.command_processor.add_geolayer(new_geolayer)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process.
                self.warning_count += 1
                message = "Unexpected error splitting GeoLayer {}.".format(pv_InputGeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred.
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
