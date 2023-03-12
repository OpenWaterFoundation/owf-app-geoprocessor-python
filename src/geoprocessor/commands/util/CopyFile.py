# CopyFile - command to copy a file
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
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validator_util

import logging
import os
from shutil import copyfile


class CopyFile(AbstractCommand):
    """
    The CopyFile command copies a source file to a destination copy.
    The command is useful as a utility and is often used in automated testing to provide input data from a saved copy.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("SourceFile", type("")),
        CommandParameterMetadata("DestinationFile", type("")),
        CommandParameterMetadata("IfSourceFileNotFound", type(""))
    ]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = "Copy a source file to a destination."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # SourceFile
    __parameter_input_metadata['SourceFile.Description'] = "the name of the source file to copy"
    __parameter_input_metadata['SourceFile.Label'] = "Source file"
    __parameter_input_metadata['SourceFile.Required'] = True
    __parameter_input_metadata['SourceFile.Tooltip'] = \
        "The name of the source file to copy. Can be specified using ${Property}."
    __parameter_input_metadata['SourceFile.FileSelector.Type'] = "Read"
    __parameter_input_metadata['SourceFile.FileSelector.Title'] = "Select the source file to copy"
    __parameter_input_metadata['SourceFile.FileSelector.Filters'] = ["All files (*)"]
    # DestinationFile
    __parameter_input_metadata['DestinationFile.Description'] = "the name of the destination file"
    __parameter_input_metadata['DestinationFile.Label'] = "Destination file"
    __parameter_input_metadata['DestinationFile.Required'] = True
    __parameter_input_metadata['DestinationFile.Tooltip'] = \
        "The name of the destination file. Can be specified using ${Property}."
    __parameter_input_metadata['DestinationFile.FileSelector.Type'] = "Write"
    __parameter_input_metadata['DestinationFile.FileSelector.Title'] = "select the destination file"
    __parameter_input_metadata['DestinationFile.FileSelector.Filters'] = ["All files (*)"]
    # IfSourceFileNotFound
    __parameter_input_metadata['IfSourceFileNotFound.Description'] = "action if file not found"
    __parameter_input_metadata['IfSourceFileNotFound.Label'] = "If not found?"
    __parameter_input_metadata['IfSourceFileNotFound.Tooltip'] = (
        "Indicate an action if the source file is not found:\n\n"
        "Ignore (ignore the missing file and do not warn)\n"
        "Warn (generate a warning message)\n"
        "Fail (generate a failure message). ")
    __parameter_input_metadata['IfSourceFileNotFound.Values'] = ["", "Ignore", "Warn", "Fail"]
    __parameter_input_metadata['IfSourceFileNotFound.Value.Default'] = "Warn"

    # Choices for IfSourceFileNotFound, used to validate parameter and display in editor.
    __choices_IfSourceFileNotFound = ["Ignore", "Warn", "Fail"]

    def __init__(self) -> None:
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data.
        super().__init__()
        self.command_name = "CopyFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display.
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata.
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

        # IfSourceFileNotFound is optional, defaults to Warn at runtime.
        # noinspection PyPep8Naming
        pv_IfNotFound = self.get_parameter_value(parameter_name='IfSourceFileNotFound',
                                                 command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_IfNotFound, self.__choices_IfSourceFileNotFound, True, True):
            message = "IfSourceFileNotFound parameter is invalid."
            recommendation = "Specify the IfSourceFileNotFound parameter as blank or one of " + \
                             str(self.__choices_IfSourceFileNotFound)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            logger.warning(warning_message)
            raise CommandParameterError(warning_message)

        # Refresh the phase severity.
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def run_command(self) -> None:
        """
        Run the command.
        Copy the source file to the destination.

        Returns:
            None

        Raises:
                RuntimeError: if a runtime input error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Get data for the command.
        # noinspection PyPep8Naming
        pv_SourceFile = self.get_parameter_value('SourceFile')
        # noinspection PyPep8Naming
        pv_DestinationFile = self.get_parameter_value('DestinationFile')

        # Runtime checks on input.

        # noinspection PyPep8Naming
        pv_SourceFile_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_SourceFile, self)))
        # noinspection PyPep8Naming
        pv_DestinationFile_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_DestinationFile, self)))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings about command parameters."
            logger.warning(message)
            raise CommandError(message)

        # Do the processing.

        # noinspection PyBroadException
        try:
            # Need both the input file and output folder to exist to complete the copy.
            input_count = 0
            if os.path.exists(pv_SourceFile_absolute):
                input_count += 1
            else:
                warning_count += 1
                message = "The source file does not exist: {}".format(pv_SourceFile_absolute)
                self.command_status.add_to_log(
                    CommandPhaseType.RUN,
                    CommandLogRecord(CommandStatusType.FAILURE, message,
                                     "Verify that the source exists at the time the command is run."))
                logger.warning(message)

            destination_folder = os.path.dirname(pv_DestinationFile_absolute)
            if os.path.exists(destination_folder):
                input_count += 1
            else:
                warning_count += 1
                message = "The destination folder does not exist: {}".format(destination_folder)
                self.command_status.add_to_log(
                    CommandPhaseType.RUN,
                    CommandLogRecord(CommandStatusType.FAILURE, message,
                                     "Verify that the destination folder exists at the time the command is run."))

            if input_count == 2:
                # Try to do the copy.
                logger.info('Copying file "' + pv_SourceFile_absolute + '" to "' + pv_DestinationFile_absolute + '"')
                copyfile(pv_SourceFile_absolute, pv_DestinationFile_absolute)

        except Exception:
            warning_count += 1
            message = "Unexpected error copying file '{}' to '{}'".format(pv_SourceFile_absolute,
                                                                          pv_DestinationFile_absolute)
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "See the log file for details."))

        if warning_count > 0:
            message = "There were {} warnings processing the command.".format(warning_count)
            raise CommandError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
