# WriteGeoMapProjectToJSON - command to write a GeoMapProject to a JSON file
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
from geoprocessor.core.GeoMapCustomJsonEncoder import GeoMapCustomJsonEncoder

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validator_util

import json
import logging


class WriteGeoMapProjectToJSON(AbstractCommand):
    """
    Writes a GeoMapProject to a JSON file, suitable for use in other applications such as web mapping.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoMapProjectID", type("")),
        CommandParameterMetadata("Indent", int),
        CommandParameterMetadata("OutputFile", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Write a GeoMapProject to a JSON file."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # GeoMapID
    __parameter_input_metadata['GeoMapProjectID.Description'] = "GeoMapProject identifier"
    __parameter_input_metadata['GeoMapProjectID.Label'] = "GeoMapProjectID"
    __parameter_input_metadata['GeoMapProjectID.Required'] = True
    __parameter_input_metadata['GeoMapProjectID.Tooltip'] = "The GeoMapProject identifier, can use ${Property}."
    # Indent
    __parameter_input_metadata['Indent.Description'] = "indent number"
    __parameter_input_metadata['Indent.Label'] = "Indent (# of spaces)"
    __parameter_input_metadata['Indent.Required'] = False
    __parameter_input_metadata['Indent.Tooltip'] = "The indent as number of spaces, for pretty printing."
    # OutputFile
    __parameter_input_metadata['OutputFile.Description'] = "JSON file to write"
    __parameter_input_metadata['OutputFile.Label'] = "Output file"
    __parameter_input_metadata['OutputFile.Required'] = True
    __parameter_input_metadata['OutputFile.Tooltip'] = (
        "The output JSON file (relative or absolute path)."
        "${Property} syntax is recognized.")
    __parameter_input_metadata['OutputFile.FileSelector.Type'] = "Write"
    __parameter_input_metadata['OutputFile.FileSelector.Title'] = "Select JSON file to write"
    __parameter_input_metadata['OutputFile.FileSelector.Filters'] = \
        ["JSON file (*.json)", "All files (*.*)"]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "WriteGeoMapProjectToJSON"
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
            command_parameters (dict): the dictionary of command parameters to check (key:string_value)

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

        # Check that parameter Indent is a valid integer if specified.
        # noinspection PyPep8Naming
        pv_Indent = self.get_parameter_value(parameter_name='Indent', command_parameters=command_parameters)

        if not validator_util.validate_int(pv_Indent, True, True):
            message = "The Indent parameter ({}) is invalid.".format(pv_Indent)
            recommendation = "Specify the Indent parameter as the number of spaces to indent."
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

    def check_runtime_data(self, geomapproject_id, output_file_abs):
        """
       Checks the following:
       * the ID of the GeoMapProject is an existing GeoMapProjectID
       * the output folder is a valid folder

       Args:
           geomapproject_id (str): the ID of the GeoMapProject to be written
           output_file_abs (str): the full pathname to the output file

       Returns:
             True if the GeoMapProject should be written, False if not.
       """

        # The Boolean values correspond to the results of the following tests.
        should_run_command = list()

        # If the GeoMap ID is not an existing GeoMap ID, fail.
        should_run_command.append(validator_util.run_check(self, "IsGeoMapProjectIdExisting", "GeoMapProjectID",
                                                           geomapproject_id, "FAIL"))

        # If the folder of the OutputFile file path is not a valid folder, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "DoesFilePathHaveAValidFolder", "OutputFile",
                                                           output_file_abs, "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Write the GeoMapProject to a JSON format.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values
        # noinspection PyPep8Naming
        pv_GeoMapProjectID = self.get_parameter_value("GeoMapProjectID")
        # noinspection PyPep8Naming
        pv_Indent = self.get_parameter_value("Indent")  # None is OK
        indent = None
        if pv_Indent is not None:
            indent = int(pv_Indent)
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value("OutputFile")

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_GeoMapProjectID = self.command_processor.expand_parameter_value(pv_GeoMapProjectID, self)

        # Convert the OutputFile parameter value relative path to an absolute path and expand for ${Property} syntax
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        # Run the checks on the runtime data. Only continue if the checks passed.
        if self.check_runtime_data(pv_GeoMapProjectID, output_file_absolute):
            # noinspection PyBroadException
            try:
                # Get the GeoMap
                geomapproject = self.command_processor.get_geomapproject(pv_GeoMapProjectID)
                if geomapproject is None:
                    self.warning_count += 1
                    message = "GeoMapProject for GeoMapProjectID={} was not found.".format(pv_GeoMapProjectID)
                    recommendation = "Check that the GeoMapProjectID is valid."
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

                # Create the JSON string to write
                # - the GeoMapProjectCustomJsonEncoder.default() function handles encoding types that cannot otherwise
                #   be serialized, for example PyQGIS types
                json_string = json.dumps(geomapproject, indent=indent, cls=GeoMapCustomJsonEncoder)

                # Write the JSON string
                with open(output_file_absolute, 'w') as file:
                    file.write(json_string)

                # Save the output file in the processor
                self.command_processor.add_output_file(output_file_absolute)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process
                self.warning_count += 1
                message = "Unexpected error writing GeoMapProject {} to JSON format.".format(pv_GeoMapProjectID)
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
