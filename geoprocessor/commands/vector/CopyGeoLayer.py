# CopyGeoLayer - command to copy a GeoLayer
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

import geoprocessor.util.command_util as command_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.validator_util as validator_util

import logging


class CopyGeoLayer(AbstractCommand):

    """
    Creates a copy of a GeoLayer in the GeoProcessor's geolayers list. The copied GeoLayer is added to the
    GeoProcessor's geolayers list.

    Command Parameters

    * GeoLayerID (str, required): The ID of the existing GeoLayer to copy.
    * IncludeAttributes (str, optional): A list of glob-style patterns to determine the attributes to include in the
        copied GeoLayer. Default: * (All attributes are copied to the new GeoLayer).
    * ExcludeAttributes (str, optional): A list of glob-style patterns to determine the attributes to exclude in the
        copied GeoLayer. Default: '' (All attributes are copied to the new GeoLayer).
    * IncludeFeaturesIf (str, optional): a valid qgis expression determining which features to keep in the
        copied GeoLayer. Default: all features are copied to the new GeoLayer. See the following reference:
        https://docs.qgis.org/2.14/en/docs/user_manual/working_with_vector/expression.html#fields-and-values
    * CopiedGeoLayerID (str, optional): The ID of the copied GeoLayer. Default "{}_copy".format(GeoLayerID)
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the CopiedGeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("IncludeAttributes", type("")),
        CommandParameterMetadata("ExcludeAttributes", type("")),
        CommandParameterMetadata("IncludeFeaturesIf", type("")),
        CommandParameterMetadata("CopiedGeoLayerID", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "CopyGeoLayer"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] =\
            "Copy a GeoLayer to a new GeoLayer, optionally constrain the copy to a subset of the original features."
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # GeoLayerID
        self.parameter_input_metadata['GeoLayerID.Description'] = "the id of the GeoLayer to be copied"
        self.parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
        self.parameter_input_metadata['GeoLayerID.Required'] = True
        self.parameter_input_metadata['GeoLayerID.Tooltip'] =\
            "The ID of the GeoLayer to be copied. ${Property} syntax is recognized."
        # IncludeAttributes
        self.parameter_input_metadata['IncludeAttributes.Label'] = "Include attributes"
        self.parameter_input_metadata['IncludeAttributes.Tooltip'] =\
            "A comma-separated list of the glob-style patterns to filter the attributes to include in the copy."
        self.parameter_input_metadata['IncludeAttributes.Value.Default'] = "*"
        # ExcludeAttributes
        self.parameter_input_metadata['ExcludeAttributes.Label'] = "Exclude attributes"
        self.parameter_input_metadata['ExcludeAttributes.Tooltip'] =\
            "A comma-separated list of the glob-style patterns to filter the attributes to exclude from the copy."
        self.parameter_input_metadata['ExcludeAttributes.Value.Default'] = "'' (empty string)"
        # IncludeFeaturesIf
        self.parameter_input_metadata['IncludeFeaturesIf.Description'] = "an attribute query specifying features"
        self.parameter_input_metadata['IncludeFeaturesIf.Label'] = "Include features if"
        self.parameter_input_metadata['IncludeFeaturesIf.Tooltip'] = (
            "An attribute query specifying features to include in the copied GeoLayer.\n"
            "Expression syntax and capabilities follows QGIS Expression standards. ${Property} syntax is recognized.")
        self.parameter_input_metadata['IncludeFeaturesIf.Value.Default.Description'] = "all features are copied"
        # CopiedGeoLayerID
        self.parameter_input_metadata['CopiedGeoLayerID.Description'] = "the ID of the copied GeoLayer"
        self.parameter_input_metadata['CopiedGeoLayerID.Label'] = "Copied GeoLayerID"
        self.parameter_input_metadata['CopiedGeoLayerID.Tooltip'] =\
            "The ID of the copied GeoLayer. ${Property} syntax is recognized."
        self.parameter_input_metadata['CopiedGeoLayerID.Value.Default'] = "GeoLayerID_copy"
        # IfGeoLayerIDExists
        self.parameter_input_metadata['IfGeoLayerIDExists.Description'] = "action if output exists"
        self.parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID exists"
        self.parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = (
            "The action that occurs if the CopiedGeoLayerID already exists within the GeoProcessor.\n"
            "Replace : The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer. "
            "No warning is logged. \n"
            "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer.  "
            "A warning is logged. \n"
            "Warn : The new GeoLayer is not created. A warning is logged. \n"
            "Fail : The new GeoLayer is not created. A fail message is logged.")
        self.parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
        self.parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"

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
        warning = ""

        # Check that parameter GeoLayerID is a non-empty, non-None string.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID',
                                                 command_parameters=command_parameters)

        if not validator_util.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the GeoLayer to copy."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
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

    def __should_copy_geolayer(self, input_geolayer_id: str, output_geolayer_id: str,
                               include_feats_if_expression: str) -> bool:
        """
        Checks the following:
        * the ID of the input GeoLayer is an existing GeoLayer ID
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)
        * the IncludeFeaturesIf parameter, if configured, supplies a valid QgsExpression

        Args:
            input_geolayer_id: the ID of the input GeoLayer
            output_geolayer_id: the ID of the output, copied GeoLayer
            include_feats_if_expression: the QGSexpression string that determines which features to copy

        Returns:
             Boolean. If TRUE, the GeoLayer should be copied If FALSE, at least one check failed and the GeoLayer
                should not be copied.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the input GeoLayerID is not an existing GeoLayerID, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIdExisting", "GeoLayerID",
                                                           input_geolayer_id, "FAIL"))

        # If the IncludeFeaturesIf parameter is defined, continue with the checks.
        if include_feats_if_expression is not None:

            # If the IncludeFeaturesIf parameter value is not a valid QgsExpression, raise a FAILURE.
            should_run_command.append(validator_util.run_check(self, "IsQgsExpressionValid", "IncludeFeaturesIf",
                                                               include_feats_if_expression, "FAIL"))

        # If the CopiedGeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE (depends
        # on the value of the IfGeoLayerIDExists parameter.)
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIdUnique", "CopiedGeoLayerID",
                                                           output_geolayer_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Make a copy of the GeoLayer and add the copied GeoLayer to the GeoProcessor's geolayers list.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        # noinspection PyPep8Naming
        pv_CopiedGeoLayerID = self.get_parameter_value("CopiedGeoLayerID",
                                                       default_value="{}_copy".format(pv_GeoLayerID))
        # noinspection PyPep8Naming
        pv_IncludeAttributes = self.get_parameter_value("IncludeAttributes", default_value="*")
        # noinspection PyPep8Naming
        pv_ExcludeAttributes = self.get_parameter_value("ExcludeAttributes", default_value="''")
        # noinspection PyPep8Naming
        pv_IncludeFeaturesIf = self.get_parameter_value("IncludeFeaturesIf")

        # Convert the IncludeAttributes and ExcludeAttributes to lists.
        attrs_to_include = string_util.delimited_string_to_list(pv_IncludeAttributes)
        attrs_to_exclude = string_util.delimited_string_to_list(pv_ExcludeAttributes)

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.command_processor.expand_parameter_value(pv_GeoLayerID, self)
        # noinspection PyPep8Naming
        pv_CopiedGeoLayerID = self.command_processor.expand_parameter_value(pv_CopiedGeoLayerID, self)
        # noinspection PyPep8Naming
        pv_IncludeFeaturesIf = self.command_processor.expand_parameter_value(pv_IncludeFeaturesIf, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_copy_geolayer(pv_GeoLayerID, pv_CopiedGeoLayerID, pv_IncludeFeaturesIf):

            # Copy the GeoLayer and add the copied GeoLayer to the GeoProcessor's geolayers list.
            # noinspection PyBroadException
            try:

                # Get the input GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)
                copied_geolayer = input_geolayer.deepcopy(pv_CopiedGeoLayerID)

                # If the features are configured to be removed, continue.
                if pv_IncludeFeaturesIf:

                    # Get the QGSExpression object.
                    exp = qgis_util.get_qgsexpression_obj(pv_IncludeFeaturesIf)

                    # Get a list of Qgs Feature objects that do not match the IncludeFeaturesIf parameter criteria.
                    non_matching_features = qgis_util.get_features_not_matching_expression(
                        copied_geolayer.qgs_layer, exp)

                    # Get the ids of the matching features.
                    non_matching_feats_ids = []
                    for feat in non_matching_features:
                        non_matching_feats_ids.append(feat.id())

                    # Delete the non-matching features.
                    qgis_util.remove_qgsvectorlayer_features(copied_geolayer.qgs_layer, non_matching_feats_ids)

                # Remove the attributes of the copied GeoLayer if configured to be excluded.
                copied_geolayer.remove_attributes(attrs_to_include, attrs_to_exclude)

                # Add the copied GeoLayer to the GeoProcessor's geolayers list.
                self.command_processor.add_geolayer(copied_geolayer)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process
                self.warning_count += 1
                message = "Unexpected error copying GeoLayer {} ".format(pv_GeoLayerID)
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
