# CopyGeoLayer

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.validator_util as validators

import logging


class CopyGeoLayer(AbstractCommand):

    """
    Creates a copy of a GeoLayer in the GeoProcessor's geolayers list. The copied GeoLayer is added to the
    GeoProcessor's geolayers list.

    Command Parameters

    * GeoLayerID (str, required): The ID of the existing GeoLayer to copy.
    * IncludeAttributes (str, optional): A list of attribute names to include in the copied GeoLayer. If configured,
        ExcludeAttributes parameter must not be configured. Default: all attributes are copied to the new GeoLayer.
    * ExcludeAttributes (str, optional): A list of attribute names to exclude in the copied GeoLayer. If configured,
        IncludeAttributes parameter must not be configured. Default: all attributes are copied to the new GeoLayer.
    * IncludeFeaturesIf (str, optional): a valid qgis expression determining which features to keep in the
        copied GeoLayer. Default: all features are copied to the new GeoLayer. See the following reference:
        https://docs.qgis.org/2.14/en/docs/user_manual/working_with_vector/expression.html#fields-and-values
    * CopiedGeoLayerID (str, optional): The ID of the copied GeoLayer. Default "{}_copy".format(GeoLayerID)
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the CopiedGeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("IncludeAttributes", type("")),
        CommandParameterMetadata("ExcludeAttributes", type("")),
        CommandParameterMetadata("IncludeFeaturesIf", type("")),
        CommandParameterMetadata("CopiedGeoLayerID", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super(CopyGeoLayer, self).__init__()
        self.command_name = "CopyGeoLayer"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters):
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
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID',
                                                 command_parameters=command_parameters)

        if not validators.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the GeoLayer to copy."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that optional parameter IfGeoLayerIDExists is either `Replace`, `ReplaceAndWarn`, `Warn`, `Fail`, None.
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        acceptable_values = ["Replace", "ReplaceAndWarn", "Warn", "Fail"]
        if not validators.validate_string_in_list(pv_IfGeoLayerIDExists, acceptable_values, none_allowed=True,
                                                  empty_string_allowed=True, ignore_case=True):
            message = "IfGeoLayerIDExists parameter value ({}) is not recognized.".format(pv_IfGeoLayerIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfGeoLayerIDExists parameter.".format(
                acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def __should_copy_geolayer(self, input_geolayer_id, output_geolayer_id, attrs_to_include, attrs_to_exclude,
                               include_feats_if_expression):
        """
        Checks the following:
        * the ID of the input GeoLayer is an existing GeoLayer ID
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)
        * the attributes to include in the copied GeoLayer are existing
        * the attributes to exclude in the copied GeoLayer are existing (raise a warning, not a failure)
        * only IncludeAttributes or ExcludeAttributes (or None) are configured
        * the IncludeFeaturesIf parameter, if configured, supplies a valid QgsExpression

        Args:
            input_geolayer_id: the ID of the input GeoLayer
            output_geolayer_id: the ID of the output, copied GeoLayer

        Returns:
             Boolean. If TRUE, the GeoLayer should be copied If FALSE, at least one check failed and the GeoLayer
                should not be copied.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the input GeoLayerID is not an existing GeoLayerID, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsGeoLayerExisting", "GeoLayerID", input_geolayer_id,
                                                       "FAIL"))

        # If the input GeoLayer exists, continue with the checks.
        if False not in should_run_command:

            # If any attributes in the list of attributes to be included are non-existing, raise a FAILURE.
            should_run_command.append(validators.run_check(self, "DoAttributesExist", "IncludeAttributes",
                                                           attrs_to_include, "FAIL", other_values=[input_geolayer_id]))

            # If any attributes in the list of attributes to be excluded are non-existing, raise a FAILURE.
            should_run_command.append(validators.run_check(self, "DoAttributesExist", "ExcludeAttributes",
                                                           attrs_to_exclude, "FAIL", other_values=[input_geolayer_id]))

        # If both the IncludeAttributes and the ExcludeAttributes parameters are configured, raise a FAILURE.
        if attrs_to_exclude and attrs_to_include:

            message = "The IncludeAttributes parameter and the ExcludeAttributes parameter cannot both be enabled."
            recommendation = 'Either configure the IncludeAttributes parameter, the ExcludeAttributes parameter or' \
                             'neither parameter.'

            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                    message, recommendation))

        # If the IncludeFeaturesIf parameter is defined, continue with the checks.
        if include_feats_if_expression is not None:

            # If the IncludeFeaturesIf parameter value is not a valid QgsExpression, raise a FAILURE.
            should_run_command.append(validators.run_check(self, "IsQgsExpressionValid", "IncludeFeaturesIf",
                                                           include_feats_if_expression, "FAIL"))

        # If the CopiedGeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE (depends
        # on the value of the IfGeoLayerIDExists parameter.)
        should_run_command.append(validators.run_check(self, "IsGeoLayerIdUnique", "CopiedGeoLayerID",
                                                       output_geolayer_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self):
        """
        Run the command. Make a copy of the GeoLayer and add the copied GeoLayer to the GeoProcessor's geolayers list.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_CopiedGeoLayerID = self.get_parameter_value("CopiedGeoLayerID",
                                                       default_value="{}_copy".format(pv_GeoLayerID))
        pv_IncludeAttributes = self.get_parameter_value("IncludeAttributes")
        pv_ExcludeAttributes = self.get_parameter_value("ExcludeAttributes")
        pv_IncludeFeaturesIf = self.get_parameter_value("IncludeFeaturesIf")

        # If the IncludeAttributes is not None, convert it from string to list of strings.
        if pv_IncludeAttributes:
            attrs_to_include = string_util.delimited_string_to_list(pv_IncludeAttributes)
        else:
            attrs_to_include = []

        # If the ExcludeAttributes is not None, convert it from string to list of strings.
        if pv_ExcludeAttributes:
            attrs_to_exclude = string_util.delimited_string_to_list(pv_ExcludeAttributes)
        else:
            attrs_to_exclude = []

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_copy_geolayer(pv_GeoLayerID, pv_CopiedGeoLayerID, attrs_to_include, attrs_to_exclude,
                                       pv_IncludeFeaturesIf):

            # Copy the GeoLayer and add the copied GeoLayer to the GeoProcessor's geolayers list.
            try:

                # Get the input GeoLayer
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)
                copied_geolayer = input_geolayer.deepcopy(pv_CopiedGeoLayerID)

                # If the features are configured to be removed, continue.
                if pv_IncludeFeaturesIf:

                    # Get the QGSExpression object.
                    exp = qgis_util.get_qgsexpression_obj(pv_IncludeFeaturesIf)

                    # Get a list of Qgs Feature objects that do not match the IncludeFeaturesIf parameter criteria.
                    non_matching_features = qgis_util.get_features_not_matching_expression(
                        copied_geolayer.qgs_vector_layer, exp)

                    # Get the ids of the matching features.
                    non_matching_feats_ids = []
                    for feat in non_matching_features:
                        non_matching_feats_ids.append(feat.id())

                    # Delete the non-matching features.
                    qgis_util.remove_qgsvectorlayer_features(copied_geolayer.qgs_vector_layer, non_matching_feats_ids)

                # If attributes are configured to be removed, continue.
                if attrs_to_exclude or attrs_to_include:

                    # If the user configured the ExcludeAttributes parameter, the attributes to remove are those
                    # listed by the user.
                    if attrs_to_exclude:
                        attrs_to_remove = attrs_to_exclude

                    # If the user configured the IncludeAttributes parameter, the attributes to remove are those
                    # not listed by the user.
                    else:

                        # Get the existing attribute names of the input GeoLayer.
                        list_of_existing_attributes = input_geolayer.get_attribute_field_names()

                        # Get a list of the existing attribute names not listed in the user-defined IncludeAttributes
                        # parameter.
                        attrs_to_remove = []
                        for attr in list_of_existing_attributes:
                            if attr not in attrs_to_include:
                                attrs_to_remove.append(attr)

                    # Remove the desired attributes from the copied geolayer.
                    for attr_to_remove in attrs_to_remove:
                        copied_geolayer.remove_attribute(attr_to_remove)

                # Add the copied GeoLayer to the GeoProcessor's geolayers list.
                self.command_processor.add_geolayer(copied_geolayer)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error copying GeoLayer {} ".format(pv_GeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.error(message, exc_info=True)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message,
                                                                recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
