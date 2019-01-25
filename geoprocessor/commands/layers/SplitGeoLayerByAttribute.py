# SplitGeoLayerByAttribute - command to split a GeoLayer into multiple GeoLayers based on an attribute's values
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2019 Open Water Foundation
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
from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validators
import geoprocessor.util.qgis_util as qgis_util

import logging

import os

from processing.core.Processing import Processing


class SplitGeoLayerByAttribute(AbstractCommand):

    """
    Splits a GeoLayer into multiple GeoLayers based on the GeoLayer's attribute values.

    This command takes a GeoLayer and an attribute and generates a set of GeoLayers.
    Each new GeoLayer contains all features from the input GeoLayer with the
    same value for the specified attribute.  The number of GeoLayers generated is equal to the number of
    unique values found for the specified attribute.

    Command Parameters

    * InputGeoLayerID (str, required): the ID of the input GeoLayer, the layer to be split.
    * AttributeName (str, required): the name of the attribute to split on. Must be a unique attribute name of the GeoLayer.
    * OutputGeoLayerIDs (str, optional): the IDs of the GeoLayers created as the output split layers. By default the
        GeoLayerID of the output layers will be {}_splitBy_{} where the first variable is the InputGeoLayerID and the
        second variable is the AttributeName value.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the OutputGeoLayerIDs
        already exist within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("InputGeoLayerID", type("")),
        CommandParameterMetadata("AttributeName", type("")),
        CommandParameterMetadata("OutputGeoLayerIDs", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "SplitGeoLayerByAttribute"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = {}
        self.command_metadata['Description'] = ('This command splits an input GeoLayer by unique values '
                                                'of an attribute.')
        self.command_metadata['EditorType'] = 'Generic'

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters):
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

    def __should_split_geolayer(self, input_geolayer_id, attribute_name, output_geolayer_ids):
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
                self.logger.error(message)
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
            logger.info('Process can be run')

    def run_command(self):
        """
        Run the command. Split the input GeoLayer by the selected Attribute. Create new GeoLayers based on
        unique attribute values.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_InputGeoLayerID = self.get_parameter_value("InputGeoLayerID")
        pv_AttributeName = self.get_parameter_value("AttributeName")
        pv_OutputGeoLayerIDs = self.get_parameter_value("OutputGeoLayerIDs", default_value="{}_splitBy_{}".format(
            pv_InputGeoLayerID, pv_AttributeName))

        logger = logging.getLogger(__name__)

        # Run the checks on the parameter values. Only continue if the checks passed.
        #if self.__should_split_geolayer(pv_InputGeoLayerID, pv_AttributeName, pv_OutputGeoLayerIDs):
        run=True
        if run:

            try:

                # Get the Input GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_InputGeoLayerID)

                logger.info('Input GeoLayer has been read in')

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

                # Perform the QGIS split vector layer function. Refer to the reference below for parameter descriptions.
                # REF: https://docs.qgis.org/2.8/en/docs/user_manual/processing_algs/qgis/vector_general_tools.html#split-vector-layer
                alg_parameters = {"INPUT": input_geolayer.qgs_vector_layer,
                                  "FIELD": attribute_name,
                                  "OUTPUT": ""}
                split_output = self.command_processor.qgis_processor.runAlgorithm("qgis:splitvectorlayer", alg_parameters)

                # Create new GeoLayers and add them to the GeoProcessor's geolayers list.

                # In QGIS 2 the clipped_output["OUTPUT"] returned the full file pathname of the memory output layer
                # (saved in a QGIS temporary folder)
                # qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_file(clipped_output["OUTPUT"])
                # new_geolayer = GeoLayer(pv_OutputGeoLayerID, qgs_vector_layer, "MEMORY")

                # In QGIS 3 the clipped_output["OUTPUT"] returns the QGS vector layer object
                new_geolayer = GeoLayer(pv_OutputGeoLayerIDs, split_output["OUTPUT"], "MEMORY")
                self.command_processor.add_geolayer(new_geolayer)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error splitting GeoLayer {}.".format(
                    pv_InputGeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.error(message, exc_info=True)
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
