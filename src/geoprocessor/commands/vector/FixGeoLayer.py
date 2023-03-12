# FixGeoLayer - command to fix a GeoLayer's geometry
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

import logging
import os
# from plugins.processing.tools import general


class FixGeoLayer(AbstractCommand):
    """
    Fixes the geometry of a layer.
    A new GeoLayer is optionally created with the fixed geometry (default is to replace the old layer).

    Command Parameters:

    * GeoLayerID (str, required): the ID of the input GeoLayer, the layer to be clipped
    * FixedGeoLaterID (str, optional): the ID of the fixed GeoLayer.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the OutputGeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("OutputGeoLayerID", type("")),
        CommandParameterMetadata("Name", type("")),
        CommandParameterMetadata("Description", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = (
        "Fix the geometry for each feature of a GeoLayer.")
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "GeoLayer identifier"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = "The ID of the GeoLayer to be fixed."
    # OutputGeoLayerID
    __parameter_input_metadata['OutputGeoLayerID.Description'] = "output GeoLayer identifier"
    __parameter_input_metadata['OutputGeoLayerID.Label'] = "Fixed GeoLayerID"
    __parameter_input_metadata['OutputGeoLayerID.Tooltip'] = \
        "A GeoLayer identifier for the output fixed GeoLayer."
    __parameter_input_metadata['OutputGeoLayerID.Value.Default.Description'] = "GeoLayerID for fixed layer"
    # Name
    __parameter_input_metadata['Name.Description'] = "fixed GeoLayer name"
    __parameter_input_metadata['Name.Label'] = "Name"
    __parameter_input_metadata['Name.Required'] = False
    __parameter_input_metadata['Name.Tooltip'] = "The fixed GeoLayer name, can use ${Property}."
    __parameter_input_metadata['Name.Value.Default.Description'] = "OutputGeoLayerID"
    # Description
    __parameter_input_metadata['Description.Description'] = "fixed GeoLayer description"
    __parameter_input_metadata['Description.Label'] = "Description"
    __parameter_input_metadata['Description.Required'] = False
    __parameter_input_metadata['Description.Tooltip'] = "The fixed GeoLayer description, can use ${Property}."
    __parameter_input_metadata['Description.Value.Default'] = ''
    # IfGeoLayerIDExists
    __parameter_input_metadata['IfGeoLayerIDExists.Description'] = "action if OutputGeoLayerID exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = (
        "The action that occurs if the OutputGeoLayerID already exists within the GeoProcessor. \n"
        "Replace : The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer. "
        "No warning is logged.\n"
        "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer. "
        "A warning is logged.\n"
        "Warn : The new GeoLayer is not created. A warning is logged. \n"
        "Fail : The new GeoLayer is not created. A fail message is logged.")
    __parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
    __parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data.
        super().__init__()
        self.command_name = "FixGeoLayer"
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
        warning = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise CommandParameterError(warning)
        else:
            # Refresh the phase severity.
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, geolayer_id: str, fixed_geolayer_id: str) -> bool:
        """
        Checks the following:
        * the ID of the GeoLayer is an existing GeoLayer ID
        * the ID of the OutputGeoLayerID is unique (not an existing GeoLayer ID)

        Args:
            geolayer_id: the ID of the GeoLayer to be simplified
            fixed_geolayer_id: the ID of the fixed GeoLayer

        Returns:
             Boolean. If TRUE, the GeoLayer should be fixed. If FALSE, at least one check failed and the GeoLayer
                should not be fixed.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests.
        # If TRUE, the test confirms that the command should be run.
        should_run_command = list()

        # If the GeoLayerID is not an existing GeoLayerID, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIDExisting", "GeoLayerID", geolayer_id,
                                                           "FAIL"))

        # If the OutputGeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE
        # (depends on the value of the IfGeoLayerIDExists parameter.)
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIdUnique", "OutputGeoLayerID",
                                                           fixed_geolayer_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Simplify the GeoLayer by the tolerance.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        default_fixed_id = "{}_fixed".format(pv_GeoLayerID)
        # noinspection PyPep8Naming
        pv_OutputGeoLayerID = self.get_parameter_value("OutputGeoLayerID", default_value=default_fixed_id)
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
        pv_OutputGeoLayerID = self.command_processor.expand_parameter_value(pv_OutputGeoLayerID, self)
        # noinspection PyPep8Naming
        pv_Name = self.command_processor.expand_parameter_value(pv_Name, self)
        # noinspection PyPep8Naming
        pv_Description = self.command_processor.expand_parameter_value(pv_Description, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(pv_GeoLayerID, pv_OutputGeoLayerID):
            # noinspection PyBroadException
            try:
                # Get the GeoLayer.
                geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # If the GeoLayer is an in-memory GeoLayer, make it an on-disk GeoLayer.
                if geolayer.input_path_full is None or geolayer.input_path_full.upper() in ["", GeoLayer.SOURCE_MEMORY]:

                    # Get the absolute path of the GeoLayer to write to disk.
                    geolayer_disk_abs_path = os.path.join(self.command_processor.get_property('TempDir'), geolayer.id)

                    # Write the GeoLayer to disk.
                    # Overwrite the (memory) GeoLayer in the geoprocessor with the on-disk GeoLayer.
                    geolayer = geolayer.write_to_disk(geolayer_disk_abs_path)
                    self.command_processor.add_geolayer(geolayer)

                do_fix = True
                if do_fix:
                    # Perform the QGIS fix geometries function. Refer to the REF below for parameter descriptions.
                    # TODO smalers the following link is broken, need to find the correct documentation.
                    # REF: https://docs.qgis.org/2.8/en/docs/user_manual/processing_algs/qgis/
                    #       vector_geometry_tools/fixgeometries.html
                    alg_parameters = {
                        "INPUT": geolayer.qgs_layer,
                        "OUTPUT": "memory:"
                    }
                    feedback_handler = QgisAlgorithmProcessingFeedbackHandler(self)
                    simple_output = qgis_util.run_processing(processor=self.command_processor.qgis_processor,
                                                             algorithm="native:fixgeometries",
                                                             algorithm_parameters=alg_parameters,
                                                             feedback_handler=feedback_handler)
                    self.warning_count += feedback_handler.get_warning_count()

                    # Create a new GeoLayer and add it to the GeoProcessor's geolayers list.
                    # In QGIS3, simple_output["OUTPUT"] returns the QGS vector layer object
                    # see ClipGeoLayer.py for information about value in QGIS2 environment.
                    new_geolayer = VectorGeoLayer(geolayer_id=pv_OutputGeoLayerID,
                                                  qgs_vector_layer=simple_output["OUTPUT"],
                                                  name=pv_Name,
                                                  description=pv_Description,
                                                  input_path_full=GeoLayer.SOURCE_MEMORY,
                                                  input_path=GeoLayer.SOURCE_MEMORY)
                    self.command_processor.add_geolayer(new_geolayer)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process.
                self.warning_count += 1
                message = "Unexpected error fixing GeoLayer geometries {}.".format(pv_GeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred.
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
