# AddGeoLayerViewToGeoMap - command to add a GeoLayerView to GeoMap
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

from geoprocessor.core.GeoLayerView import GeoLayerView

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validator_util

import logging


class AddGeoLayerViewToGeoMap(AbstractCommand):
    """
    Add a GeoLayerView to a GeoMap, which allows layers to be added to the group.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("GeoMapID", type("")),
        CommandParameterMetadata("GeoLayerViewGroupID", type("")),
        CommandParameterMetadata("GeoLayerViewID", type("")),
        CommandParameterMetadata("Name", type("")),
        CommandParameterMetadata("Description", type("")),
        CommandParameterMetadata("Properties", type("")),
        CommandParameterMetadata("InsertPosition", type("")),
        CommandParameterMetadata("InsertBefore", type("")),
        CommandParameterMetadata("InsertAfter", type(""))]

    # Command metadata for command editor display
    # - * character takes up two spaces for indent below
    __command_metadata = dict()
    __command_metadata['Description'] = "Create a new GeoLayerView and add to a GeoLayerViewGroup in a GeoMap.\n"\
        "A GeoLayerView consists of GeoLayer and GeoLayerSymbol (see SetGeoLayerView*Symbol commands).\n"\
        "    GeoMapProject\n"\
        "      GeoMap [ ]\n"\
        "*      GeoLayerViewGroup [ ]\n"\
        "*        GeoLayerView [ ]\n"\
        "            GeoLayer + GeoLayerSymbol\n"\
        "The first GeoLayerView in the list is displayed on the top of the group.\n"\
        "The last GeoLayerView in the list is displayed on the bottom of the group."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "GeoLayer identifier"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = "The GeoLayer identifier, can use ${Property}."
    # GeoMapID
    __parameter_input_metadata['GeoMapID.Description'] = "GeoMap identifier"
    __parameter_input_metadata['GeoMapID.Label'] = "GeoMapID"
    __parameter_input_metadata['GeoMapID.Required'] = True
    __parameter_input_metadata['GeoMapID.Tooltip'] = "The GeoMap identifier, can use ${Property}."
    # GeoLayerViewGroupID
    __parameter_input_metadata['GeoLayerViewGroupID.Description'] = "GeoLayerViewGroup identifier"
    __parameter_input_metadata['GeoLayerViewGroupID.Label'] = "GeoLayerViewGroupID"
    __parameter_input_metadata['GeoLayerViewGroupID.Required'] = True
    __parameter_input_metadata['GeoLayerViewGroupID.Tooltip'] = "The GeoLayerViewGroup identifier, can use ${Property}."
    # GeoLayerViewID
    __parameter_input_metadata['GeoLayerViewID.Description'] = "New GeoLayerView identifier"
    __parameter_input_metadata['GeoLayerViewID.Label'] = "GeoLayerViewID"
    __parameter_input_metadata['GeoLayerViewID.Required'] = True
    __parameter_input_metadata['GeoLayerViewID.Tooltip'] = "The GeoLayerViewGroup identifier, can use ${Property}."
    # Name
    __parameter_input_metadata['Name.Description'] = "GeoLayerView name"
    __parameter_input_metadata['Name.Label'] = "Name"
    __parameter_input_metadata['Name.Required'] = False
    __parameter_input_metadata['Name.Tooltip'] = "The GeoLayerView name, can use ${Property}, default is layer name."
    __parameter_input_metadata['Name.Value.Default'] = ''
    # Description
    __parameter_input_metadata['Description.Description'] = "GeoLayerView description"
    __parameter_input_metadata['Description.Label'] = "Description"
    __parameter_input_metadata['Description.Required'] = False
    __parameter_input_metadata['Description.Tooltip'] =\
        "The GeoLayerView description, can use ${Property}, default is description."
    __parameter_input_metadata['Description.Value.Default'] = ''
    # Properties
    __parameter_input_metadata['Properties.Description'] = "properties for the new GeoLayerViewGroup"
    __parameter_input_metadata['Properties.Label'] = "Properties"
    __parameter_input_metadata['Properties.Required'] = False
    __parameter_input_metadata['Properties.Tooltip'] = \
        "Properties for the new GeoLayerViewGroup using syntax:  property:value,property:'value'"
    # InsertPosition
    __parameter_input_metadata['InsertPosition.Description'] = "insert position"
    __parameter_input_metadata['InsertPosition.Label'] = "Insert position"
    __parameter_input_metadata['InsertPosition.Required'] = False
    __parameter_input_metadata['InsertPosition.Values'] = ['', 'Bottom', 'Top']
    __parameter_input_metadata['InsertPosition.Value.Default'] = 'Bottom'
    __parameter_input_metadata['InsertPosition.Tooltip'] =\
        "Insert position relative to other GeoLayer, can use ${Property}."
    # InsertBefore
    __parameter_input_metadata['InsertBefore.Description'] = "insert before GeoLayerViewGroup"
    __parameter_input_metadata['InsertBefore.Label'] = "Insert before"
    __parameter_input_metadata['InsertBefore.Required'] = False
    __parameter_input_metadata['InsertBefore.Tooltip'] =\
        "The GeoLayerID to insert before, can use ${Property}."
    # InsertAfter
    __parameter_input_metadata['InsertAfter.Description'] = "insert after GeoLayerViewGroup"
    __parameter_input_metadata['InsertAfter.Label'] = "Insert after"
    __parameter_input_metadata['InsertAfter.Required'] = False
    __parameter_input_metadata['InsertAfter.Tooltip'] =\
        "The GeoLayerID to insert after, can use ${Property}."

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "AddGeoLayerViewToGeoMap"
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
                message = "Required {} parameter is not specified.".format(parameter)
                recommendation = "Specify the {} parameter.".format(parameter)
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
            recommendation = "Check the properties string format."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Only allow one of InsertPosition, InsertBefore, and InsertAfter
        # noinspection PyPep8Naming
        pv_InsertPosition = self.get_parameter_value(parameter_name='InsertPosition',
                                                     command_parameters=command_parameters)
        # noinspection PyPep8Naming
        pv_InsertBefore = self.get_parameter_value(parameter_name='InsertBefore',
                                                   command_parameters=command_parameters)
        # noinspection PyPep8Naming
        pv_InsertAfter = self.get_parameter_value(parameter_name='InsertAfter', command_parameters=command_parameters)
        check_list = list()
        check_list.append(pv_InsertPosition)
        check_list.append(pv_InsertBefore)
        check_list.append(pv_InsertAfter)
        if validator_util.validate_list_has_one_value(check_list, True):
            # List has at least one value
            if not validator_util.validate_list_has_one_value(check_list):
                # List does not have exactly one value
                message = "Zero or one of InsertPosition, InsertBefore, and InsertAfter can be specified."
                recommendation = "Specify only one insert parameter (or none)."
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

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, geolayer_id, geomap_id, geolayerviewgroup_id,
                           insert_before, insert_after) -> bool:
        """
        Checks whether runtime data are valid.  Checks the following:
        * the ID of the GeoLayer is an existing GeoLayerID
        * the ID of the GeoMap is an existing GeoMapID
        * the ID of the GeoLayerViewGroupID is an existing GeoLayerViewGroupID

        Args:
            geolayer_id (str): the ID of the GeoLayer to add
            geomap_id (str): the ID of the GeoMap to be modify
            geolayerviewgroup_id (str): the ID of the GeoLayerViewGroup to modify
            insert_before (str):  the GeoLayerID to insert before
            insert_after (str):  the GeoLayerID to insert after

        Returns:
             True if the GeoMap should be modified, False if not.
        """

        # The Boolean values correspond to the results of the following tests.
        should_run_command = list()

        # If the GeoLayer ID is not an existing GeoLayer ID, fail.
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIdExisting",
                                                           "GeoLayerID", geolayer_id, "FAIL"))

        # If the GeoMap ID is not an existing GeoMap ID, fail.
        geomap = self.command_processor.get_geomap(geomap_id)
        if geomap is None:
            message = "GeoMap for GeoMapID '{}' was not found.".format(geomap_id)
            recommendation = "Check that the GeoMapID is valid."
            self.logger.warning(message, exc_info=True)
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
            should_run_command.append(False)
        else:
            # If the GeoLayerViewGroup ID is not an existing GeoLayerViewGroup ID, fail.
            geolayerviewgroup = geomap.get_geolayerviewgroup(geolayerviewgroup_id)
            if geolayerviewgroup is None:
                message = "GeoLayerViewGroup for GeoLayerViewGroupID '{}' was not found.".format(geolayerviewgroup_id)
                recommendation = "Check that the GeoLayerViewGroupID is valid."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
                should_run_command.append(False)

        # If the insert_before is specified and is not an existing GeoLayerViewGroupID, fail.
        if insert_before is not None and (insert_before != ""):
            should_run_command.append(validator_util.run_check(self, "IsGeoLayerViewGroupIdExisting",
                                                               "InsertBefore", insert_before, "FAIL"))

        # If the insert_after is specified and is not an existing GeoLayerViewGroupID, fail.
        if insert_after is not None and (insert_before != ""):
            should_run_command.append(validator_util.run_check(self, "IsGeoLayerViewGroupIdExisting",
                                                               "InsertAfter", insert_after, "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Add the GeoLayer to the GeoMap.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        # noinspection PyPep8Naming
        pv_GeoMapID = self.get_parameter_value("GeoMapID")
        # noinspection PyPep8Naming
        pv_GeoLayerViewGroupID = self.get_parameter_value("GeoLayerViewGroupID")
        # noinspection PyPep8Naming
        pv_GeoLayerViewID = self.get_parameter_value("GeoLayerViewID")
        # noinspection PyPep8Naming
        pv_Name = self.get_parameter_value("Name", default_value=self.parameter_input_metadata['Name.Value.Default'])
        # noinspection PyPep8Naming
        pv_Description =\
            self.get_parameter_value("Description",
                                     default_value=self.parameter_input_metadata['Description.Value.Default'])
        # noinspection PyPep8Naming
        pv_Properties = self.get_parameter_value("Properties")
        # noinspection PyPep8Naming
        pv_InsertPosition = self.get_parameter_value("InsertPosition")  # None is OK
        # noinspection PyPep8Naming
        pv_InsertBefore = self.get_parameter_value("InsertBefore")  # None is OK
        # noinspection PyPep8Naming
        pv_InsertAfter = self.get_parameter_value("InsertAfter")  # None is OK

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.command_processor.expand_parameter_value(pv_GeoLayerID, self)
        # noinspection PyPep8Naming
        pv_GeoMapID = self.command_processor.expand_parameter_value(pv_GeoMapID, self)
        # noinspection PyPep8Naming
        pv_GeoLayerViewGroupID = self.command_processor.expand_parameter_value(pv_GeoLayerViewGroupID, self)
        # noinspection PyPep8Naming
        pv_GeoLayerViewID = self.command_processor.expand_parameter_value(pv_GeoLayerViewID, self)
        # noinspection PyPep8Naming
        pv_Name = self.command_processor.expand_parameter_value(pv_Name, self)
        # noinspection PyPep8Naming
        pv_Description = self.command_processor.expand_parameter_value(pv_Description, self)
        # noinspection PyPep8Naming
        pv_Properties = self.command_processor.expand_parameter_value(pv_Properties, self)
        # noinspection PyPep8Naming
        pv_InsertBefore = self.command_processor.expand_parameter_value(pv_InsertBefore, self)
        # noinspection PyPep8Naming
        pv_InsertAfter = self.command_processor.expand_parameter_value(pv_InsertAfter, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        # - TODO smalers 2020-03-18 not sure if the following is useful because need to handle checks granularly
        if self.check_runtime_data(pv_GeoLayerID, pv_GeoMapID, pv_GeoLayerViewGroupID,
                                   pv_InsertBefore, pv_InsertAfter):
            # noinspection PyBroadException
            try:
                # Get the GeoLayer
                geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)
                if geolayer is None:
                    self.warning_count += 1
                    message = "GeoLayer for GeoLayerID '{}' was not found.".format(pv_GeoLayerID)
                    recommendation = "Check that the GeoLayerID is valid."
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
                # Get the GeoMap
                geomap = self.command_processor.get_geomap(pv_GeoMapID)
                if geomap is None:
                    self.warning_count += 1
                    message = "GeoMap for GeoMapID '{}' was not found.".format(pv_GeoMapID)
                    recommendation = "Check that the GeoMapID is valid."
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
                # Get the GeoLayerViewGroup
                geolayerviewgroup = geomap.get_geolayerviewgroup(pv_GeoLayerViewGroupID)
                if geolayerviewgroup is None:
                    self.warning_count += 1
                    message = "GeoLayerViewGroup for GeoLayerViewGroup '{}' was not found.".format(
                        pv_GeoLayerViewGroupID)
                    recommendation = "Check that the GeoLayerViewGroupID is valid."
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

                # Create a new GeoLayerView
                properties = command_util.parse_properties_from_parameter_string(pv_Properties)
                geolayerview = GeoLayerView(pv_GeoLayerViewID, geolayer, name=pv_Name, description=pv_Description,
                                            properties=properties)

                # Add the GeoLayerView to the GeoMap
                if (geomap is not None) and (geolayerviewgroup is not None):
                    geomap.add_geolayerview_to_geolayerviewgroup(geolayerview, geolayerviewgroup,
                                                                 insert_position=pv_InsertPosition,
                                                                 insert_before=pv_InsertBefore,
                                                                 insert_after=pv_InsertAfter)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process
                self.warning_count += 1
                message = "Unexpected error adding the GeoLayerView {} to the GeoLayerViewGroup {}.".format(
                    pv_GeoLayerViewID, pv_GeoLayerViewGroupID)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
