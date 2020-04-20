# SetGeoLayerViewEventHandler - command to set a GeoLayerView event handler
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

from geoprocessor.core.GeoLayerViewEventHandler import GeoLayerViewEventHandler

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validator_util

import logging


class SetGeoLayerViewEventHandler(AbstractCommand):
    """
    Set a GeoLayerView event handler, to be implemented by application that uses map configuration.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoMapID", type("")),
        CommandParameterMetadata("GeoLayerViewGroupID", type("")),
        CommandParameterMetadata("GeoLayerViewID", type("")),
        CommandParameterMetadata("EventType", type("")),
        CommandParameterMetadata("Name", type("")),
        CommandParameterMetadata("Description", type("")),
        CommandParameterMetadata("Properties", type(""))]

    # Command metadata for command editor display.
    # - The * character is equivalent to two spaces for indent.
    __command_metadata = dict()
    __command_metadata['Description'] =\
        "Set a GeoLayerView event handler, which handles layer/symbol interaction events.\n" \
        "An application that uses the map configuration should implement features to handle the event,"\
        "based on the EventType and properties.\n"\
        "    GeoMapProject\n"\
        "      GeoMap [ ]\n"\
        "        GeoLayerViewGroup [ ]\n"\
        "          GeoLayerView [ ]\n"\
        "*          GeoLayer + GeoLayerSymbol + EventHandler [ ]"
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
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
    __parameter_input_metadata['GeoLayerViewID.Description'] = "GeoLayerView identifier"
    __parameter_input_metadata['GeoLayerViewID.Label'] = "GeoLayerViewID"
    __parameter_input_metadata['GeoLayerViewID.Required'] = True
    __parameter_input_metadata['GeoLayerViewID.Tooltip'] = "The GeoLayerViewGroup identifier, can use ${Property}."
    # EventType
    __parameter_input_metadata['EventHandler.Description'] = "Event type"
    __parameter_input_metadata['EventHandler.Label'] = "Name"
    __parameter_input_metadata['EventHandler.Required'] = True
    __parameter_input_metadata['EventHandler.Tooltip'] = "The event type, can use ${Property}."
    # Name
    __parameter_input_metadata['Name.Description'] = "Event handler name"
    __parameter_input_metadata['Name.Label'] = "Name"
    __parameter_input_metadata['Name.Required'] = False
    __parameter_input_metadata['Name.Tooltip'] = "The event handler name, can use ${Property}."
    # Description
    __parameter_input_metadata['Description.Description'] = "Event handler description"
    __parameter_input_metadata['Description.Label'] = "Description"
    __parameter_input_metadata['Description.Required'] = False
    __parameter_input_metadata['Description.Tooltip'] = "The event handler description, can use ${Property}."
    # Properties
    __parameter_input_metadata['Properties.Description'] = "properties for the event handler"
    __parameter_input_metadata['Properties.Label'] = "Properties"
    __parameter_input_metadata['Properties.Required'] = False
    __parameter_input_metadata['Properties.Tooltip'] = \
        "Properties for the event handler using syntax:  property:value,property:'value'"

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "SetGeoLayerViewEventHandler"
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

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            self.logger.warning(warning_message)
            raise CommandParameterError(warning_message)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, geomap_id, geolayerviewgroup_id, geolayerview_id) -> bool:
        """
        Checks whether runtime data are valid.  Checks the following:
        * the ID of the GeoMap is an existing GeoMapID
        * the ID of the GeoLayerViewGroupID is an existing GeoLayerViewGroupID
        * the ID of the GeoLayerViewID is an existing GeoLayerViewID

        Args:
            geomap_id (str): the ID of the GeoMap to be modify
            geolayerviewgroup_id (str): the ID of the GeoLayerViewGroup to modify
            geolayerview_id (str): the ID of the GeoLayerView to modify

        Returns:
             True if the runtime data are valid.
        """

        # The Boolean values correspond to the results of the following tests.
        should_run_command = list()

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
            else:
                # If the GeoLayerView ID is not an existing GeoLayerView ID, fail.
                geolayerview = geolayerviewgroup.get_geolayerview(geolayerview_id)
                if geolayerview is None:
                    message = "GeoLayerView for GeoLayerViewID '{}' was not found.".format(geolayerview_id)
                    recommendation = "Check that the GeoLayerViewID is valid."
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
                    should_run_command.append(False)

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command.  Set an event handler for the GeoLayerView.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values
        # noinspection PyPep8Naming
        pv_GeoMapID = self.get_parameter_value("GeoMapID")
        # noinspection PyPep8Naming
        pv_GeoLayerViewGroupID = self.get_parameter_value("GeoLayerViewGroupID")
        # noinspection PyPep8Naming
        pv_GeoLayerViewID = self.get_parameter_value("GeoLayerViewID")
        # noinspection PyPep8Naming
        pv_EventType = self.get_parameter_value("EventType")
        # noinspection PyPep8Naming
        pv_Name = self.get_parameter_value("Name")
        # noinspection PyPep8Naming
        pv_Description = self.get_parameter_value("Description", default_value='')
        # noinspection PyPep8Naming
        pv_Properties = self.get_parameter_value("Properties")

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_GeoMapID = self.command_processor.expand_parameter_value(pv_GeoMapID, self)
        # noinspection PyPep8Naming
        pv_GeoLayerViewGroupID = self.command_processor.expand_parameter_value(pv_GeoLayerViewGroupID, self)
        # noinspection PyPep8Naming
        pv_GeoLayerViewID = self.command_processor.expand_parameter_value(pv_GeoLayerViewID, self)
        # noinspection PyPep8Naming
        pv_EventType = self.command_processor.expand_parameter_value(pv_EventType, self)
        # noinspection PyPep8Naming
        pv_Name = self.command_processor.expand_parameter_value(pv_Name, self)
        # noinspection PyPep8Naming
        pv_Description = self.command_processor.expand_parameter_value(pv_Description, self)
        # noinspection PyPep8Naming
        pv_Properties = self.command_processor.expand_parameter_value(pv_Properties, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        # - TODO smalers 2020-03-18 not sure if the following is useful because need to handle checks granularly
        if self.check_runtime_data(pv_GeoMapID, pv_GeoLayerViewGroupID, pv_GeoLayerViewID):
            # noinspection PyBroadException
            try:
                # Initialize so can check below
                geolayerview = None
                geolayerviewgroup = None
                # Get the GeoMap
                geomap = self.command_processor.get_geomap(pv_GeoMapID)
                if geomap is None:
                    self.warning_count += 1
                    message = "GeoMap for GeoMapID '{}' was not found.".format(pv_GeoMapID)
                    recommendation = "Check that the GeoMapID is valid."
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
                else:
                    # Get the GeoLayerViewGroup
                    geolayerviewgroup = geomap.get_geolayerviewgroup(pv_GeoLayerViewGroupID)
                    if geolayerviewgroup is None:
                        self.warning_count += 1
                        message = "GeoLayerViewGroup for GeoLayerViewGroup '{}' was not found.".format(
                            pv_GeoLayerViewGroupID)
                        recommendation = "Check that the GeoLayerViewGroupID is valid."
                        self.logger.warning(message, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.FAILURE,
                                                                        message, recommendation))
                    else:
                        # Get the GeoLayerView
                        geolayerview = geolayerviewgroup.get_geolayerview(pv_GeoLayerViewID)
                        if geolayerview is None:
                            self.warning_count += 1
                            message = "GeoLayerViewGroup for GeoLayerViewGroup '{}' was not found.".format(
                                pv_GeoLayerViewGroupID)
                            recommendation = "Check that the GeoLayerViewGroupID is valid."
                            self.logger.warning(message, exc_info=True)
                            self.command_status.add_to_log(CommandPhaseType.RUN,
                                                           CommandLogRecord(CommandStatusType.FAILURE,
                                                                            message, recommendation))

                if (geomap is not None) and (geolayerviewgroup is not None) and (geolayerview is not None):
                    # Set the properties
                    properties = command_util.parse_properties_from_parameter_string(pv_Properties)

                    event_handler = GeoLayerViewEventHandler(pv_EventType, properties=properties, name=pv_Name,
                                                             description=pv_Description)

                    # Append the event handler
                    geolayerview.event_handlers.append(event_handler)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process
                self.warning_count += 1
                message = "Unexpected error setting event handler for GeoLayerView {}.".format(pv_GeoLayerViewID)
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
