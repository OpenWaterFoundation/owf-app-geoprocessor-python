# RemoveGeoLayerFeatures - command to remove GeoLayer features
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

from geoprocessor.core.CommandError import CommandError
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.validator_util as validator_util

import logging


class RemoveGeoLayerFeatures(AbstractCommand):
    """
    Removes one or more features from a GeoLayer.
    Currently the feature values are checked against the values in a table.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", str),
        CommandParameterMetadata("MatchAttribute", str),
        CommandParameterMetadata("IncludeTableID", str),
        CommandParameterMetadata("IncludeTableColumn", str)
    ]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = (
        "Remove one or more feature from a GeoLayer.\n"
        "Currently, the only option is to compare an attribute value with table column and include matches."
    )
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "GeoLayer identifier"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = "The ID of the GeoLayer with the attribute to be removed."
    # MatchAttribute
    __parameter_input_metadata['MatchAttribute.Description'] = "name of attribute to match against table value"
    __parameter_input_metadata['MatchAttribute.Label'] = "Attribute to match against table column value"
    __parameter_input_metadata['MatchAttribute.Required'] = True
    __parameter_input_metadata['MatchAttribute.Tooltip'] = \
        "The name of the attribute to be checked against a table column, with matches included in result."
    # IncludeTableID
    __parameter_input_metadata['IncludeTableID.Description'] = "name of table ID to match values"
    __parameter_input_metadata['IncludeTableID.Label'] = "Include table ID"
    __parameter_input_metadata['IncludeTableID.Required'] = True
    __parameter_input_metadata['IncludeTableID.Tooltip'] = \
        "The name of the table to be checked."
    # IncludeTableColumn
    __parameter_input_metadata['IncludeTableColumn.Description'] = "name of table column to match values"
    __parameter_input_metadata['IncludeTableColumn.Label'] = "Include table column"
    __parameter_input_metadata['IncludeTableColumn.Required'] = True
    __parameter_input_metadata['IncludeTableColumn.Tooltip'] = \
        "The name of the table column to be checked."

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "RemoveGeoLayerFeatures"
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

    def check_runtime_data(self, geolayer_id: str, include_attribute: str, include_table_id: str,
                           include_table_column: str) -> bool:
        """
        Checks the following:
         * The ID of the input GeoLayer is an actual GeoLayer (if not, log an error message and do not continue.)
         * The include attribute name is valid for the GeoLayer (if not, log an error message and do not continue.)
         * The table ID is valid.
         * The column name for the table is valid.

        Args:
            geolayer_id (str): the ID of the GeoLayer to process
            include_attribute (str): the name of the attributes to check
            include_table_id (str): the ID of the table to check
            include_table_column (str): the table column to check

        Returns:
            ok: Boolean. If True, processing can continue.  If False, processing should not continue.
        """

        # Boolean to determine if the attribute should be removed. Set to TRUE until one or many checks fail.
        ok = True

        # If the input GeoLayer does not exist, raise a FAILURE.
        geolayer = self.command_processor.get_geolayer(geolayer_id)
        if geolayer is None:

            # Boolean to determine if the attribute should be removed.
            ok = False
            self.warning_count += 1
            message = 'The input GeoLayer ID ({}) does not exist.'.format(geolayer_id)
            recommendation = 'Specify a valid GeoLayerID.'
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        else:
            # If the input GeoLayer does exist, continue with the checks.

            # Get the input GeoLayer object.
            input_geolayer = self.command_processor.get_geolayer(geolayer_id)

            # Get the existing attribute names of the input GeoLayer.
            list_of_existing_attributes = input_geolayer.get_attribute_field_names()

            # Create a list of invalid input attribute names. An invalid attribute name is an input attribute name
            # that is not matching any of the existing attribute names of the GeoLayer.
            attribute_names = [include_attribute]
            invalid_attrs = (attr_name for attr_name in attribute_names if attr_name not in list_of_existing_attributes)

            # Iterate over the invalid input attribute names and raise a FAILURE for each.
            for invalid_attr in invalid_attrs:

                ok = False
                self.warning_count += 1
                message = 'The attribute name ({}) is not valid.'.format(invalid_attr)
                recommendation = 'Specify a valid attribute name. Valid attributes for this layer are' \
                                 ' as follows: {}'.format(list_of_existing_attributes)
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        table = self.command_processor.get_table(include_table_id)
        if table is None:
            # If the input table does not exist, raise a FAILURE.

            ok = False
            self.warning_count += 1
            message = 'The input Table ID ({}) does not exist.'.format(include_table_id)
            recommendation = 'Specify a valid TableID.'
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        else:
            # If the input table does exist, check for the requested column.
            if table.get_field_index(include_table_column) < 0:
                ok = False
                self.warning_count += 1
                message = 'The input Table ID ({}) column ({}) does not exist.'.format(include_table_id,
                                                                                       include_table_column)
                recommendation = 'Specify a valid column name.'
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Return the Boolean to determine if the attribute should be removed.
        # If True, all runtime checks passed. If False, one or many checks failed.
        return ok

    def run_command(self) -> None:
        """
        Run the command.

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
        pv_MatchAttribute = self.get_parameter_value("MatchAttribute")
        # noinspection PyPep8Naming
        pv_IncludeTableID = self.get_parameter_value("IncludeTableID")
        # noinspection PyPep8Naming
        pv_IncludeTableColumn = self.get_parameter_value("IncludeTableColumn")

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(pv_GeoLayerID, pv_MatchAttribute, pv_IncludeTableID, pv_IncludeTableColumn):
            # Run the process.
            # noinspection PyBroadException
            try:
                # Get the input GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Get the table.
                table = self.command_processor.get_table(pv_IncludeTableID)

                # Iterate over the features and check that the requested attribute value is in the table column
                attribute_name = pv_MatchAttribute
                table_columns = [pv_IncludeTableColumn]
                feature_ids_to_remove = []
                feature_count_start = input_geolayer.qgs_layer.featureCount()
                for feature in input_geolayer.qgs_layer.getFeatures():
                    # Remove the attribute from the GeoLayer.
                    attribute_value = feature[attribute_name]
                    # Column values to check in table
                    column_values = [attribute_value]
                    records = table.get_records(table_columns, column_values)
                    if len(records) == 0:
                        # No table records matched the feature attribute value so remove the feature
                        # - TODO smalers 2020-11-14 probably have to fix so don't get an iterator concurrency issue
                        feature_ids_to_remove.append(feature.id())

                # Remove the features
                qgis_util.remove_qgsvectorlayer_features(input_geolayer.qgs_layer, feature_ids_to_remove)
                self.logger.info("Started with {} features, have {} features after matching with table.".format(
                    feature_count_start, input_geolayer.qgs_layer.featureCount()))

            except Exception:
                # Raise an exception if an unexpected error occurs during the process

                self.warning_count += 1
                message = "Unexpected error removing features from GeoLayer {}.".format(pv_GeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
