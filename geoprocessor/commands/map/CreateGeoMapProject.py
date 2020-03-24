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

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validator_util

import logging


class CreateGeoMapProject(AbstractCommand):
    """
    Creates a new GeoMapProject, which is used to serialize a map product.

    Command Parameters
    * NewGeoMapProjectID (str, required): The identifier for the new GeoMapProject.
    * Name (str, required): The name of the new GeoMapProject, used for displays.
    * Description (str, optional): The description of the new GeoMapProject, used for displays.
    * IfGeoMapProjectIDExists (str, optional): This parameter determines the action that occurs if the GeoMapProjectID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("NewGeoMapProjectID", type("")),
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
    __parameter_input_metadata['NewGeoMapProjctID.Description'] = "identifier for the new GeoMapProject"
    __parameter_input_metadata['NewGeoMapProjctID.Label'] = "New GeoMapProjectID"
    __parameter_input_metadata['NewGeoMapProjctID.Required'] = True
    __parameter_input_metadata['NewGeoMapProjctID.Tooltip'] = "The identifier for the new GeoMapProject."
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
        "Warn: The new GeoMapProject is not created. A warning is logged.\n"
        "Fail: The new GeoMapProject is not created. A fail message is logged.")
    __parameter_input_metadata['IfGeoMapProjectIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
    __parameter_input_metadata['IfGeoMapProjectIDExists.Value.Default'] = "Replace"

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
        acceptable_values = ["Replace", "Warn", "Fail", "ReplaceAndWarn"]
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

    def check_runtime_data(self, geomapproject_id: str):
        """
        Checks the following:
        * the identifier of the new GeoMapProject is unique (not an existing GeoMapProjectID)

        Args:
            geomapproject_id (str): the id of the GeoMapProject to be created

        Returns:
             True if the GeoMap should be created or False if at least one check failed.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the GeoMapID is the same as an already-existing GeoMapID, raise a WARNING or FAILURE
        # (depends on the value of the IfGeoMapIDExists parameter.)
        should_run_command.append(validator_util.run_check(self, "IsGeoMapProjectIDUnique",
                                                           "NewGeoMapProjectID", geomapproject_id, None))

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
        pv_Name = self.get_parameter_value("Name")
        # noinspection PyPep8Naming
        pv_Description =\
            self.get_parameter_value("Description",
                                     default_value=self.parameter_input_metadata['Description.Value.Default'])
        # noinspection PyPep8Naming
        pv_Properties = self.get_parameter_value("Properties")

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_NewGeoMapProjectID = self.command_processor.expand_parameter_value(pv_NewGeoMapProjectID, self)
        # noinspection PyPep8Naming
        pv_Name = self.command_processor.expand_parameter_value(pv_Name, self)
        # noinspection PyPep8Naming
        pv_Description = self.command_processor.expand_parameter_value(pv_Description, self)
        # noinspection PyPep8Naming
        pv_Properties = self.command_processor.expand_parameter_value(pv_Properties, self)

        if self.check_runtime_data(pv_NewGeoMapProjectID):
            # noinspection PyBroadException
            try:
                # TODO smalers 2020-03-09 need to decide if manage a list of QGIS maps or just GeoProcessor form
                # Create a new GeoMapProject and add it to the GeoProcesor's geomapprojects list if the
                # ID does not exist.
                self.logger.debug("Creating map project with ID: '" + str(pv_NewGeoMapProjectID) + "'")
                new_geomaproject = GeoMapProject(geomapproject_id=pv_NewGeoMapProjectID, name=pv_Name,
                                                 description=pv_Description)
                self.command_processor.add_geomapproject(new_geomaproject)

                # Set the properties
                properties = command_util.parse_properties_from_parameter_string(pv_Properties)
                # Set the properties as additional properties (don't just reset the properties dictionary)
                new_geomaproject.set_properties(properties)

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
