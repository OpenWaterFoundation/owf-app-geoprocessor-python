# CreateGeoMapProject - command to create a new GeoMap
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
from geoprocessor.core.GeoMapProject import GeoMapProject
from geoprocessor.core.GeoMapProjectType import GeoMapProjectType
from geoprocessor.core.IfExistsActionType import IfExistsActionType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validator_util

import logging


class CreateGeoMapProject(AbstractCommand):
    """
    Creates a new GeoMapProject, which is used to serialize a map product.
    """
    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("NewGeoMapProjectID", type("")),
        CommandParameterMetadata("ProjectType", type("")),
        CommandParameterMetadata("Name", type("")),
        CommandParameterMetadata("Description", type("")),
        CommandParameterMetadata("Properties", type("")),
        CommandParameterMetadata("IfGeoMapProjectIDExists", type(""))]

    # Command metadata for command editor display
    # - * character takes up about two spaces in the following
    __command_metadata = dict()
    __command_metadata['Description'] = "Create a new GeoMapProject, to save the map configuration.\n"\
        "*  GeoMapProject\n"\
        "      GeoMap [ ]\n"\
        "        GeoLayerViewGroup [ ]\n"\
        "          GeoLayerView [ ]\n"\
        "            GeoLayer + GeoLayerSymbol\n"
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # NewGeoMapID
    __parameter_input_metadata['NewGeoMapProjectID.Description'] = "identifier for the new GeoMapProject"
    __parameter_input_metadata['NewGeoMapProjectID.Label'] = "New GeoMapProjectID"
    __parameter_input_metadata['NewGeoMapProjectID.Required'] = True
    __parameter_input_metadata['NewGeoMapProjectID.Tooltip'] = "The identifier for the new GeoMapProject."
    # ProjectType
    __parameter_input_metadata['ProjectType.Description'] = "project type"
    __parameter_input_metadata['ProjectType.Label'] = "Project type"
    __parameter_input_metadata['ProjectType.Tooltip'] = (
        "GeoMapProject type, used by applications that display maps.")
    __parameter_input_metadata['ProjectType.Values'] =\
        GeoMapProjectType.get_geomapproject_types_as_str(include_blank=True)
    __parameter_input_metadata['ProjectType.Value.Default'] = str(GeoMapProjectType.SingleMap)
    # GeoMapName
    __parameter_input_metadata['Name.Description'] = "name for the new GeoMapProject"
    __parameter_input_metadata['Name.Label'] = "Name"
    __parameter_input_metadata['Name.Required'] = True
    __parameter_input_metadata['Name.Tooltip'] = "The name for the new GeoMapProject."
    # Description
    __parameter_input_metadata['Description.Description'] = "description for the new GeoMapProject"
    __parameter_input_metadata['Description.Label'] = "Description"
    __parameter_input_metadata['Description.Required'] = False
    __parameter_input_metadata['Description.Tooltip'] = "The description for the new GeoMapProject."
    __parameter_input_metadata['Description.Value.Default'] = ''
    # Properties
    __parameter_input_metadata['Properties.Description'] = "properties for the new GeoMapProject"
    __parameter_input_metadata['Properties.Label'] = "Properties"
    __parameter_input_metadata['Properties.Required'] = False
    __parameter_input_metadata['Properties.Tooltip'] =\
        "Properties for the new GeoMapProject using syntax:  property:value,property:'value'"
    # IfGeoMapProjectIDExists
    __parameter_input_metadata['IfGeoMapProjectIDExists.Description'] = "action if map exists"
    __parameter_input_metadata['IfGeoMapProjectIDExists.Label'] = "If GeoMapProjectID exists"
    __parameter_input_metadata['IfGeoMapProjectIDExists.Tooltip'] = (
        "The action that occurs if the NewGeoMapProjectID already exists within the GeoProcessor.\n"
        "Replace: The existing GeoMapProject within the GeoProcessor is replaced with the new GeoMapProject. "
        "No warning is logged.\n"
        "ReplaceAndWarn: The existing GeoMap within the GeoProcessor is replaced with the new GeoMapProject. "
        "A warning is logged.\n"
        "Warn: The new GeoMapProject is not created. A warning message is logged.\n"
        "Fail: The new GeoMapProject is not created. A fail message is logged.")
    __parameter_input_metadata['IfGeoMapProjectIDExists.Values'] =\
        IfExistsActionType.get_ifexistsaction_types_as_str(include_blank=True)
    __parameter_input_metadata['IfGeoMapProjectIDExists.Value.Default'] = str(IfExistsActionType.ReplaceAndWarn)

    def __init__(self) -> None:
        """
        Initialize the command.
        """
        # AbstractCommand data
        super().__init__()
        self.command_name = "CreateGeoMapProject"
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

        # Check that optional IfGeoMapProjectIDExists param is either `Replace`, `Warn`, `Fail`,
        # `ReplaceAndWarn` or None.
        # noinspection PyPep8Naming
        pv_IfGeoMapIDExists = self.get_parameter_value(parameter_name="IfGeoMapProjectIDExists",
                                                       command_parameters=command_parameters)
        acceptable_values = IfExistsActionType.get_ifexistsaction_types_as_str(include_blank=True)
        if not validator_util.validate_string_in_list(pv_IfGeoMapIDExists, acceptable_values, none_allowed=True,
                                                      empty_string_allowed=True, ignore_case=True):
            message = "IfGeoMapProjectIDExists parameter value ({}) is not recognized.".format(pv_IfGeoMapIDExists)
            recommendation =\
                "Specify one of the acceptable values ({}) for the IfGeoMapProjectIDExists parameter.".format(
                    acceptable_values)
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
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    # noinspection PyPep8Naming
    def check_runtime_data(self, geomapproject_id: str, project_type_str: str,
                           ifgeomapprojectidexists: IfExistsActionType):
        """
        Checks the following:
        * the identifier of the new GeoMapProject is unique (not an existing GeoMapProjectID)
        * the project type is a valid type

        Args:
            geomapproject_id (str): the id of the GeoMapProject to be created
            project_type_str (str): the project type as a string
            ifgeomapprojectidexists (str): action to take if a GeoMapProjectID exists in the processor

        Returns:
             True if the GeoMapProject should be created or False if at least one check failed.
        """
        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the ProjectType is in the list of recognized values
        # (depends on the value of the IfGeoMapIDExists parameter.)
        should_run_command.append(validator_util.validate_string_in_list(
            project_type_str, GeoMapProjectType.get_geomapproject_types_as_str(), False, False, True))

        # If the GeoMapProjectID is the same as an already-existing GeoMapProjectID, take action
        if self.command_processor.get_geomapproject(geomapproject_id) is not None:
            # Warnings/recommendations if the GeolayerID is the same as a registered GeoLayerID.
            message = 'The GeoMapProjectID ({}) is already in use.'.format(geomapproject_id)
            recommendation = 'Specify a new unique GeoMapProjectID.'

            if ifgeomapprojectidexists is IfExistsActionType.ReplaceAndWarn:
                # The registered GeoLayer should be replaced with the new GeoLayer (with warnings).
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING, message, recommendation))
            elif ifgeomapprojectidexists is IfExistsActionType.Warn:
                # The registered GeoLayer should not be replaced. A warning should be logged.
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING, message, recommendation))
                should_run_command.append(False)
            elif ifgeomapprojectidexists is IfExistsActionType.Fail:
                # The matching IDs should cause a failure.
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
                should_run_command.append(False)
            else:
                # "Replace" requires no logging.
                pass

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Create the GeoMap.  Add the GeoMap to the GeoProcessor's geomaps list.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """
        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_NewGeoMapProjectID = self.get_parameter_value("NewGeoMapProjectID")
        # noinspection PyPep8Naming
        pv_ProjectType = \
            self.get_parameter_value("ProjectType",
                                     default_value=self.parameter_input_metadata['ProjectType.Value.Default'])
        # noinspection PyPep8Naming
        pv_Name = self.get_parameter_value("Name")
        # noinspection PyPep8Naming
        pv_Description =\
            self.get_parameter_value("Description",
                                     default_value=self.parameter_input_metadata['Description.Value.Default'])
        # noinspection PyPep8Naming
        pv_Properties = self.get_parameter_value("Properties")
        # noinspection PyPep8Naming
        pv_IfGeoMapProjectIDExists =\
            self.get_parameter_value("IfGeoMapProjectIDExists",
                                     default_value=self.parameter_input_metadata[
                                         'IfGeoMapProjectIDExists.Value.Default'])
        ifgeomapprojectidexists = IfExistsActionType.value_of_ignore_case(pv_IfGeoMapProjectIDExists)

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_NewGeoMapProjectID = self.command_processor.expand_parameter_value(pv_NewGeoMapProjectID, self)
        # noinspection PyPep8Naming
        pv_ProjectType = self.command_processor.expand_parameter_value(pv_ProjectType, self)
        # noinspection PyPep8Naming
        pv_Name = self.command_processor.expand_parameter_value(pv_Name, self)
        # noinspection PyPep8Naming
        pv_Description = self.command_processor.expand_parameter_value(pv_Description, self)
        # noinspection PyPep8Naming
        pv_Properties = self.command_processor.expand_parameter_value(pv_Properties, self)

        if self.check_runtime_data(pv_NewGeoMapProjectID, pv_ProjectType, ifgeomapprojectidexists):
            # noinspection PyBroadException
            try:
                # Create a new GeoMapProject and add it to the GeoProcesor's geomapprojects list.
                self.logger.debug("Creating map project with ID: '" + str(pv_NewGeoMapProjectID) + "'")

                project_type = GeoMapProjectType.value_of_ignore_case(pv_ProjectType)
                properties = command_util.parse_properties_from_parameter_string(pv_Properties)

                new_geomaproject = GeoMapProject(geomapproject_id=pv_NewGeoMapProjectID,
                                                 project_type=project_type,
                                                 name=pv_Name,
                                                 description=pv_Description,
                                                 properties=properties)

                # This will replace the existing if a matching identifier
                # - this will automatically add as the latest GeoMapProject
                self.command_processor.add_geomapproject(new_geomaproject)

            except Exception as e:
                # Raise an exception if an unexpected error occurs during the process.
                self.warning_count += 1
                message = "Unexpected error creating GeoMapProject ({}): {}".format(pv_NewGeoMapProjectID, e)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
        else:
            self.logger.debug("Not enough data to create GeoMapProject.")

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
