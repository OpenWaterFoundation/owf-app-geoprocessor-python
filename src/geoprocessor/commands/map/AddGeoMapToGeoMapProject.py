# AddGeoMapToGeoMapProject - command to add a GeoMap to GeoMapProject
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

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validator_util

import logging


class AddGeoMapToGeoMapProject(AbstractCommand):
    """
    Add a GeoMap to a GeoMapProject, which allows maps to be added for configuration output.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoMapProjectID", type("")),
        CommandParameterMetadata("GeoMapID", type("")),
        CommandParameterMetadata("InsertPosition", type("")),
        CommandParameterMetadata("InsertBefore", type("")),
        CommandParameterMetadata("InsertAfter", type(""))]

    # Command metadata for command editor display:
    # - * character takes up about two spaces for indentation
    __command_metadata = dict()
    __command_metadata['Description'] = "Add a GeoMap to a GeoMapProject, to construct an overall visualization.\n"\
        "*  GeoMapProject\n"\
        "*    GeoMap [ ]\n"\
        "       GeoLayerViewGroup [ ]\n"\
        "          GeoLayerView [ ]\n"\
        "            GeoLayer + GeoLayerSymbol\n"\
        "The first GeoMap in the list is displayed on the top of the map.\n"\
        "The last GeoMap in the list is displayed on the bottom of the map."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # GeoMapProjectID
    __parameter_input_metadata['GeoMapProjectID.Description'] = "GeoMapProject identifier"
    __parameter_input_metadata['GeoMapProjectID.Label'] = "GeoMapProjectID"
    __parameter_input_metadata['GeoMapProjectID.Required'] = False
    __parameter_input_metadata['GeoMapProjectID.Tooltip'] = "The GeoMapProject identifier, can use ${Property}."
    __parameter_input_metadata['GeoMapProjectID.Value.Default.Description'] = "last added GeoMapProject ID."
    # GeoMapID
    __parameter_input_metadata['GeoMapID.Description'] = "GeoMap identifier"
    __parameter_input_metadata['GeoMapID.Label'] = "GeoMapID"
    __parameter_input_metadata['GeoMapID.Required'] = True
    __parameter_input_metadata['GeoMapID.Tooltip'] = "The GeoMap identifier, can use ${Property}."
    __parameter_input_metadata['Description.Tooltip'] = "The GeoLayerViewGroup description, can use ${Property}."
    # InsertPosition
    __parameter_input_metadata['InsertPosition.Description'] = "insert position"
    __parameter_input_metadata['InsertPosition.Label'] = "Insert position"
    __parameter_input_metadata['InsertPosition.Required'] = False
    __parameter_input_metadata['InsertPosition.Values'] = ['', 'Bottom', 'Top']
    __parameter_input_metadata['InsertPosition.Value.Default'] = 'Bottom'
    __parameter_input_metadata['InsertPosition.Tooltip'] =\
        "Insert position relative to other GeoLayerViewGroup, can use ${Property}."
    # InsertBefore
    __parameter_input_metadata['InsertBefore.Description'] = "insert before GeoLayerViewGroup"
    __parameter_input_metadata['InsertBefore.Label'] = "Insert before"
    __parameter_input_metadata['InsertBefore.Required'] = False
    __parameter_input_metadata['InsertBefore.Tooltip'] =\
        "The GeoLayerViewGroupID to insert before, can use ${Property}."
    # InsertAfter
    __parameter_input_metadata['InsertAfter.Description'] = "insert after GeoLayerViewGroup"
    __parameter_input_metadata['InsertAfter.Label'] = "Insert after"
    __parameter_input_metadata['InsertAfter.Required'] = False
    __parameter_input_metadata['InsertAfter.Tooltip'] =\
        "The GeoLayerViewGroupID to insert after, can use ${Property}."

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data.
        super().__init__()
        self.command_name = "AddGeoMapToGeoMapProject"
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
                message = "Required {} parameter is not specified.".format(parameter)
                recommendation = "Specify the {} parameter.".format(parameter)
                warning_message += "\n" + message
                self.command_status.add_to_log(
                    CommandPhaseType.INITIALIZATION,
                    CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Only allow one of InsertPosition, InsertBefore, and InsertAfter can be specified.
        # noinspection PyPep8Naming
        pv_InsertPosition = self.get_parameter_value(parameter_name='InsertPosition',
                                                     command_parameters=command_parameters)
        # noinspection PyPep8Naming
        pv_InsertBefore = self.get_parameter_value(parameter_name='InsertBefore',
                                                   command_parameters=command_parameters)
        # noinspection PyPep8Naming
        pv_InsertAfter = self.get_parameter_value(parameter_name='InsertAfter',
                                                  command_parameters=command_parameters)
        check_list = list()
        check_list.append(pv_InsertPosition)
        check_list.append(pv_InsertBefore)
        check_list.append(pv_InsertAfter)
        if validator_util.validate_list_has_one_value(check_list, True):
            # List has at least one value.
            if not validator_util.validate_list_has_one_value(check_list):
                # List does not have exactly one value.
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

        # Refresh the phase severity.
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, geomapproject_id: str, geomap_id: str,
                           insert_before: str, insert_after: str) -> bool:
        """
        Checks whether runtime data are valid.  Checks the following:
        * the ID of the GeoMap is an existing GeoMapID

        Args:
            geomapproject_id (str): the ID of the GeoMapProject
            geomap_id (str): the ID of the GeoMap
            insert_before (str):  the GeoLayerViewGroupID to insert before
            insert_after (str):  the GeoLayerViewGroupID to insert after

        Returns:
             True if the GeoMap should be modified, False if not.
        """

        # The Boolean values correspond to the results of the following tests.
        should_run_command = list()

        # If the GeoMapProject ID is not an existing GeoMapProject ID, fail.
        should_run_command.append(validator_util.run_check(self, "IsGeoMapProjectIdExisting", "GeoMapProjectID",
                                                           geomapproject_id, "FAIL"))

        # If the GeoMap ID is not an existing GeoMap ID, fail.
        should_run_command.append(validator_util.run_check(self, "IsGeoMapIdExisting", "GeoMapID", geomap_id, "FAIL"))

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
        Run the command. Add the GeoLayerViewGroup to the GeoMap.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_GeoMapProjectID = self.get_parameter_value("GeoMapProjectID")
        geomapproject_id = None
        if pv_GeoMapProjectID is None or pv_GeoMapProjectID == "":
            # No map project ID was specified so get the latest added map project from the processor.
            if len(self.command_processor.geomapprojects) == 0:
                self.warning_count += 1
                message = "No GeoMapProjects have been created.  Cannot determine default GeoMapProject."
                recommendation = "Check that the GeoMapProjectID is valid."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
            else:
                # Use the last added.
                geomapproject_id = self.command_processor.last_geomapproject_added.id
                self.logger.info('Using default map GeoMapProjectID: {}'.format(geomapproject_id))
        else:
            geomapproject_id = pv_GeoMapProjectID
        # noinspection PyPep8Naming
        pv_GeoMapID = self.get_parameter_value("GeoMapID")
        # noinspection PyPep8Naming
        pv_InsertPosition = self.get_parameter_value("InsertPosition")  # None is OK
        # noinspection PyPep8Naming
        pv_InsertBefore = self.get_parameter_value("InsertBefore")  # None is OK
        # noinspection PyPep8Naming
        pv_InsertAfter = self.get_parameter_value("InsertAfter")  # None is OK

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        geomapproject_id = self.command_processor.expand_parameter_value(geomapproject_id, self)
        # noinspection PyPep8Naming
        pv_GeoMapID = self.command_processor.expand_parameter_value(pv_GeoMapID, self)
        # noinspection PyPep8Naming
        pv_InsertBefore = self.command_processor.expand_parameter_value(pv_InsertBefore, self)
        # noinspection PyPep8Naming
        pv_InsertAfter = self.command_processor.expand_parameter_value(pv_InsertAfter, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(geomapproject_id, pv_GeoMapID, pv_InsertBefore, pv_InsertAfter):
            # noinspection PyBroadException
            try:
                # Get the GeoMapProject
                geomapproject = self.command_processor.get_geomapproject(geomapproject_id)
                if geomapproject is None:
                    self.warning_count += 1
                    message = "GeoMapProject for GeoMapProjectID={} was not found.".format(geomapproject_id)
                    recommendation = "Check that the GeoMapProjectID is valid."
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

                # Get the GeoMap.
                geomap = self.command_processor.get_geomap(pv_GeoMapID)
                if geomap is None:
                    self.warning_count += 1
                    message = "GeoMap for GeoMapID={} was not found.".format(pv_GeoMapID)
                    recommendation = "Check that the GeoMapID is valid."
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

                # Add the GeoMap to the GeoMapProject.
                if (geomapproject is not None) and (geomap is not None):
                    geomapproject.add_geomap(geomap, insert_position=pv_InsertPosition,
                                             insert_before=pv_InsertBefore, insert_after=pv_InsertAfter)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process.
                self.warning_count += 1
                message = "Unexpected error adding GeoMap {} to GeoMapProject {}.".format(pv_GeoMapID,
                                                                                          geomapproject_id)
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
