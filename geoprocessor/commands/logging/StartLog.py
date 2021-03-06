# StartLog - command to (re)start the log file
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
import geoprocessor.util.io_util as io_util
import geoprocessor.util.log_util as log_util
import geoprocessor.util.validator_util as validator_util

import logging


class StartLog(AbstractCommand):
    """
    The StartLog command (re)starts the log file.
    This is useful to ensure that a local log file is created with the command file.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("LogFile", type(""))
    ]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = \
        '(Re)start the log file.  This is useful when it is desirable to save a log file for a command file.'
    __command_metadata['EditorType'] = 'Simple'

    # Parameter metadata
    __parameter_input_metadata = dict()
    __parameter_input_metadata["LogFile.Group"] = ""
    __parameter_input_metadata["LogFile.Description"] = ""
    __parameter_input_metadata["LogFile.Label"] = "Log file"
    __parameter_input_metadata["LogFile.Tooltip"] = \
        "Specify the path to the log file to write, can use ${Property} notation."
    __parameter_input_metadata["LogFile.Required"] = True
    __parameter_input_metadata["LogFile.Values"] = ""
    __parameter_input_metadata["LogFile.Value.Default"] = ""
    __parameter_input_metadata["LogFile.FileSelector.Type"] = "Read"
    __parameter_input_metadata["LogFile.FileSelector.Title"] = "Select Log File"

    def __init__(self) -> None:
        """
        Initialize the command instance.
        """
        super().__init__()
        self.command_name = "StartLog"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

        # Parameter metadata
        self.parameter_input_metadata = self.__parameter_input_metadata

    def check_command_parameters(self, command_parameters: dict) -> None:
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            None

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning_message = ""
        logger = logging.getLogger(__name__)

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
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception
        if len(warning_message) > 0:
            logger.warning(warning_message)
            raise CommandParameterError(warning_message)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def run_command(self) -> None:
        """
        Run the command.  Restart the lof file with the given name.
        Subsequent logging messages will go to the file until another StartLog() command is run.

        Returns:
            None

        Raises:
            RuntimeError if any exception occurs running the command.
        """
        logger = logging.getLogger(__name__)
        warning_count = 0

        # noinspection PyPep8Naming
        pv_LogFile = self.get_parameter_value('LogFile')
        log_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(
                self.command_processor.get_property('WorkingDir'),
                self.command_processor.expand_parameter_value(pv_LogFile)))

        # noinspection PyBroadException
        try:
            # Change the GeoProcessor logger to use the specified file
            # - The initial application log file will be closed.
            log_util.reset_log_file_handler(log_file_absolute)
            # Add the log file to output
            self.command_processor.add_output_file(log_file_absolute)
        except Exception:
            warning_count += 1
            message = 'Unexpected error (re)starting log file "' + log_file_absolute + '"'
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "Check the old log file or command window for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise CommandError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
