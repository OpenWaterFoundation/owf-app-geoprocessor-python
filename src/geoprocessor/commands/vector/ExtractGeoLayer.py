# ExtractGeoLayer - command to extract GeoLayer features from a layer
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
from geoprocessor.core.GeoLayer import GeoLayer
from geoprocessor.core.QGISAlgorithmProcessingFeedbackHandler import QgisAlgorithmProcessingFeedbackHandler
from geoprocessor.core.VectorGeoLayer import VectorGeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.validator_util as validator_util

from geoprocessor.commands.vector.ExtractGeoLayerSelectionConditionType import ExtractGeoLayerSelectionConditionType

import logging
import os

# from plugins.processing.tools import general


class ExtractGeoLayer(AbstractCommand):
    """
    Extract features from a GeoLayer using another layer.
    This uses the 'qgis:extractbylocation' algorithm.
    See: https://docs.qgis.org/latest/en/docs/user_manual/processing_algs/qgis/vectorselection.html#extract-by-location
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("IntersectGeoLayerID", type("")),       
        CommandParameterMetadata("SelectionCondition", type("")),
        CommandParameterMetadata("OutputGeoLayerID", type("")),
        CommandParameterMetadata("Name", type("")),
        CommandParameterMetadata("Description", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    __command_metadata = dict()
    __command_metadata['Description'] = (
        "Extract the features in the input GeoLayer that match the selection condition of the intersect GeoLayer.\n"
        "See the documentation for an explanation of the selection criteria, which controls the extraction."
    )
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "the ID of the input GeoLayer"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerId.Tooltip'] = "The ID of the input GeoLayer that will be intersected."
    # IntersectGeoLayerID
    __parameter_input_metadata['IntersectGeoLayerID.Description'] = "the ID of the intersect GeoLayer"
    __parameter_input_metadata['IntersectGeoLayerID.Label'] = "Intersect GeoLayerID"
    __parameter_input_metadata['IntersectGeoLayerID.Required'] = True
    __parameter_input_metadata['IntersectGeoLayerID.Tooltip'] = "The ID of the intersect GeoLayer."
    # SelectionCondition
    # TODO smalers 2022-08-18 currently only allow one to be picked but could allow multiple as OR.
    __parameter_input_metadata['SelectionCondition.Description'] = "how to select features to extract"
    __parameter_input_metadata['SelectionCondition.Label'] = "Selection criteria"
    __parameter_input_metadata['SelectionCondition.Tooltip'] = (
        "Criteria by which input layers features are selected, when compared to the intersection layer.")
    # Allow a blank to indicate the default.
    __parameter_input_metadata['SelectionCondition.Values'] = ExtractGeoLayerSelectionConditionType.names(sort=True)
    __parameter_input_metadata['SelectionCondition.Values'].insert(0, "")
    __parameter_input_metadata['SelectionCondition.Value.Default'] = "Intersect"
    # OutputGeoLayerID
    __parameter_input_metadata['OutputGeoLayerID.Description'] = "the ID of the extracted GeoLayer"
    __parameter_input_metadata['OutputGeoLayerID.Label'] = "Output GeoLayerID"
    __parameter_input_metadata['OutputGeoLayerID.Tooltip'] = "The ID of the extracted GeoLayer."
    __parameter_input_metadata['OutputGeoLayerID.Value.Default.Description'] = \
        "GeoLayerId_extractedFrom_IntersectGeoLayerID."
    # Name
    __parameter_input_metadata['Name.Description'] = "extracted GeoLayer name"
    __parameter_input_metadata['Name.Label'] = "Name"
    __parameter_input_metadata['Name.Required'] = False
    __parameter_input_metadata['Name.Tooltip'] = "The extracted GeoLayer name, can use ${Property}."
    __parameter_input_metadata['Name.Value.Default.Description'] = "OutputGeoLayerID"
    # Description
    __parameter_input_metadata['Description.Description'] = "extracted GeoLayer description"
    __parameter_input_metadata['Description.Label'] = "Description"
    __parameter_input_metadata['Description.Required'] = False
    __parameter_input_metadata['Description.Tooltip'] = "The extracted GeoLayer description, can use ${Property}."
    __parameter_input_metadata['Description.Value.Default'] = ''
    # IfGeoLayerIDExists
    __parameter_input_metadata['IfGeoLayerIDExists.Description'] = "action if output layer exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = (
        "The action that occurs if the OutputGeoLayerID already exists within the GeoProcessor.\n"
        "Replace : The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer. "
        "No warning is logged.\n"
        "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer."
        "A warning is logged.\n"
        "Warn : The new GeoLayer is not created. A warning is logged.\n"
        "Fail : The new GeoLayer is not created. A fail message is logged.")
    __parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
    __parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "ExtractGeoLayer"
        self.command_parameter_metadata = self.__command_parameter_metadata

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

        Returns:
            None

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

        # Check that opt parameter SelectionCondition is valid enumeration value.
        # noinspection PyPep8Naming
        pv_SelectionCondition = self.get_parameter_value(parameter_name="SelectionCondition",
                                                         command_parameters=command_parameters)
        acceptable_values = ExtractGeoLayer.__parameter_input_metadata['SelectionCondition.Values']
        if not validator_util.validate_string_in_list(pv_SelectionCondition, acceptable_values, none_allowed=True,
                                                      empty_string_allowed=True, ignore_case=True):
            message = "SelectionCondition parameter value ({}) is not recognized.".format(pv_SelectionCondition)
            recommendation = "Specify one of the acceptable values ({}) for the SelectionCondition parameter.".format(
                acceptable_values)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
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

    def check_runtime_data(self, input_geolayer_id: str, intersect_geolayer_id: str, output_geolayer_id: str) -> bool:
        """
        Checks the following:
        * the ID of the input GeoLayer is an existing GeoLayer ID
        * the ID of the intersect GeoLayer is an existing GeoLayer ID
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)
        * the input GeoLayer and the intersect GeoLayer are in the same CRS (warning but no failure)
        * the intersect GeoLayer is a POLYGON if the input GeoLayer is a POLYGON
        * the intersect GeoLayer is either a POLYGON or a LINE if the input GeoLayer is a LINE

        Args:
            input_geolayer_id: the ID of the input GeoLayer
            intersect_geolayer_id: the ID of the intersect GeoLayer
            output_geolayer_id: the ID of the output, clipped GeoLayer

        Returns:
             Boolean. If TRUE, the GeoLayer should be intersected. If FALSE, at least one check failed and the GeoLayer
                should not be intersected.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests.
        # If TRUE, the test confirms that the command should be run.
        should_run_command = list()

        # If the input GeoLayerID is not an existing GeoLayerID, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIDExisting", "GeoLayerID",
                                                           input_geolayer_id, "FAIL"))

        # If the intersect GeoLayer ID is not an existing GeoLayer ID, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIDExisting", "IntersectGeoLayerID",
                                                           intersect_geolayer_id, "FAIL"))

        # If the input GeoLayer and the intersect GeoLayer both exist, continue with the checks.
        if False not in should_run_command:

            # If the input GeoLayer and the clipping GeoLayer do not have the same CRS, raise a WARNING.
            should_run_command.append(validator_util.run_check(self, "DoGeoLayerIDsHaveMatchingCRS", "GeoLayerID",
                                                               input_geolayer_id, "WARN",
                                                               other_values=["IntersectGeoLayerID",
                                                                             intersect_geolayer_id]))

            # Get the geometry of the Input GeoLayer.
            input_geolayer = self.command_processor.get_geolayer(input_geolayer_id)
            input_geolayer_geom_qgis = input_geolayer.get_geometry()

            # If the InputGeoLayer is a polygon and the IntersectGeoLayer is a line or point, raise a FAILURE.
            if input_geolayer_geom_qgis == "Polygon":

                should_run_command.append(validator_util.run_check(self, "DoesGeoLayerIdHaveCorrectGeometry",
                                                                   "IntersectGeoLayerID", intersect_geolayer_id,
                                                                   "FAIL", other_values=[["Polygon"]]))

            # If the InputGeoLayer is a line and the IntersectGeoLayer is a point, raise a FAILURE.
            if input_geolayer_geom_qgis == "LineString":
                should_run_command.append(validator_util.run_check(self, "DoesGeoLayerIdHaveCorrectGeometry",
                                                                   "IntersectGeoLayerID", intersect_geolayer_id,
                                                                   "FAIL", other_values=[["LineString", "Polygon"]]))

        # If the OutputGeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE
        # (depends on the value of the IfGeoLayerIDExists parameter.)
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIdUnique", "OutputGeoLayerID",
                                                           output_geolayer_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Extract features from the input GeoLayer using the intersect GeoLayer.
        Create a new GeoLayer with the extracted features in the output layer.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        # noinspection PyPep8Naming
        pv_IntersectGeoLayerID = self.get_parameter_value("IntersectGeoLayerID")
        # noinspection PyPep8Naming
        pv_SelectionCondition = self.get_parameter_value("SelectionCondition")
        # noinspection PyPep8Naming
        pv_OutputGeoLayerID = self.get_parameter_value("OutputGeoLayerID", default_value="{}_intersectedBy_{}".format(
            pv_GeoLayerID, pv_IntersectGeoLayerID))
        # noinspection PyPep8Naming
        pv_Name = self.get_parameter_value("Name", default_value=pv_OutputGeoLayerID)
        # noinspection PyPep8Naming
        pv_Description = \
            self.get_parameter_value("Description",
                                     default_value=self.parameter_input_metadata['Description.Value.Default'])

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.command_processor.expand_parameter_value(pv_GeoLayerID, self)
        # noinspection PyPep8Naming
        pv_IntersectGeoLayerID = self.command_processor.expand_parameter_value(pv_IntersectGeoLayerID, self)
        # noinspection PyPep8Naming
        pv_SelectionCondition = self.command_processor.expand_parameter_value(pv_SelectionCondition, self)
        # TODO smalers 2022-08-19 Currently can only handle one condition.
        selection_condition = ExtractGeoLayerSelectionConditionType.Intersects.name  # Default.
        if pv_SelectionCondition is not None:
            selection_condition = pv_SelectionCondition
        # Convert to list of integer values.
        selection_conditions = [
            ExtractGeoLayerSelectionConditionType.value_of(selection_condition).value
        ]
        # noinspection PyPep8Naming
        pv_OutputGeoLayerID = self.command_processor.expand_parameter_value(pv_OutputGeoLayerID, self)
        # noinspection PyPep8Naming
        pv_Name = self.command_processor.expand_parameter_value(pv_Name, self)
        # noinspection PyPep8Naming
        pv_Description = self.command_processor.expand_parameter_value(pv_Description, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(pv_GeoLayerID, pv_IntersectGeoLayerID, pv_OutputGeoLayerID):
            # noinspection PyBroadException
            try:
                # Get the Input GeoLayer and the Intersect GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)
                intersect_geolayer = self.command_processor.get_geolayer(pv_IntersectGeoLayerID)

                # Make a copy of the intersect GeoLayer - manipulations will occur on this layer and the original
                # should not be affected.
                intersect_geolayer_copy = intersect_geolayer.deepcopy("intersect_geolayer_copy")

                if input_geolayer.input_path_full is None or input_geolayer.input_path_full.upper() in\
                        ["", GeoLayer.SOURCE_MEMORY]:
                    # If the input GeoLayer is an in-memory GeoLayer, make it an on-disk GeoLayer.

                    # Get the absolute path of the GeoLayer to write to disk.
                    geolayer_disk_abs_path = os.path.join(self.command_processor.get_property('TempDir'),
                                                          input_geolayer.id)

                    # Write the GeoLayer to disk.
                    # Overwrite the (memory) GeoLayer in the geoprocessor with the on-disk GeoLayer.
                    input_geolayer = input_geolayer.write_to_disk(geolayer_disk_abs_path)
                    self.command_processor.add_geolayer(input_geolayer)

                if intersect_geolayer_copy.input_path_full is None or\
                    intersect_geolayer_copy.input_path_full.upper() in \
                        ["", GeoLayer.SOURCE_MEMORY]:
                    # If the intersect GeoLayer is an in-memory GeoLayer, make it an on-disk GeoLayer.
                    # Get the absolute path of the GeoLayer to write to disk.
                    geolayer_disk_abs_path = os.path.join(self.command_processor.get_property('TempDir'),
                                                          intersect_geolayer_copy.id)

                    # Write the GeoLayer to disk.
                    # Overwrite the (memory) GeoLayer in the geoprocessor with the on-disk GeoLayer.
                    intersect_geolayer_copy = intersect_geolayer_copy.write_to_disk(geolayer_disk_abs_path)
                    self.command_processor.add_geolayer(intersect_geolayer_copy)

                # Perform the QGIS extract by location function.
                # Refer to the reference below for parameter descriptions.
                # REF: https://docs.qgis.org/latest/en/docs/user_manual/processing_algs/qgis/
                # vectorselection.html#extract-by-location
                alg_parameters = {
                    "INPUT": input_geolayer.qgs_layer,
                    "INTERSECT": intersect_geolayer_copy.qgs_layer,
                    "PREDICATE": selection_conditions,
                    "OUTPUT": "memory:"
                }
                feedback_handler = QgisAlgorithmProcessingFeedbackHandler(self)
                intersected_output = qgis_util.run_processing(processor=self.command_processor.qgis_processor,
                                                              algorithm="qgis:extractbylocation",
                                                              algorithm_parameters=alg_parameters,
                                                              feedback_handler=feedback_handler)
                self.warning_count += feedback_handler.get_warning_count()

                # Create a new GeoLayer and add it to the GeoProcessor's geolayers list.
                # in QGIS3, intersected_output["OUTPUT"] returns the returns the QGS vector layer object
                # see ClipGeoLayer.py for information about value in QGIS2 environment.
                new_geolayer = VectorGeoLayer(geolayer_id=pv_OutputGeoLayerID,
                                              qgs_vector_layer=intersected_output["OUTPUT"],
                                              name=pv_Name,
                                              description=pv_Description,
                                              input_path_full=GeoLayer.SOURCE_MEMORY,
                                              input_path=GeoLayer.SOURCE_MEMORY)
                self.command_processor.add_geolayer(new_geolayer)

                # Remove the copied intersect GeoLayer from the GeoProcessor's geolayers list. Delete the GeoLayer.
                index = self.command_processor.geolayers.index(intersect_geolayer_copy)
                del self.command_processor.geolayers[index]
                del intersect_geolayer_copy

            except Exception:
                # Raise an exception if an unexpected error occurs during the process.
                self.warning_count += 1
                message = "Unexpected error extracting GeoLayer {} using intersection GeoLayer {}.".format(
                    pv_GeoLayerID, pv_IntersectGeoLayerID)
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
