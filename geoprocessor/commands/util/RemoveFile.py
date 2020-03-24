# RemoveFile - command to remove a file
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
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import logging
import os
import shutil


class RemoveFile(AbstractCommand):
    """
    The RemoveFile command removes a file (or a folder) from the computer.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("SourceFile", type("")),
        CommandParameterMetadata("IfSourceFileNotFound", type("")),
        CommandParameterMetadata("RemoveIfFolder", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = (
        'Remove a file from the file system.  '
        'The file to be removed does not need to exist when editing this command.')
    __command_metadata['EditorType'] = 'Simple'

    # Parameter input metadata
    __parameter_input_metadata = dict()
    # SourceFile
    __parameter_input_metadata['SourceFile.Description'] = ""
    __parameter_input_metadata['SourceFile.Label'] = 'File to remove'
    __parameter_input_metadata['SourceFile.Tooltip'] = "Specify the file to remove, can use ${Property} notation."
    __parameter_input_metadata['SourceFile.Required'] = True
    __parameter_input_metadata['SourceFile.FileSelector.Type'] = "Read"
    __parameter_input_metadata['SourceFile.FileSelector.Filters'] = ["All files (*)"]
    # IfSourceFileNotFound
    __parameter_input_metadata['IfSourceFileNotFound.Description'] = "action if file not found"
    __parameter_input_metadata['IfSourceFileNotFound.Label'] = "If not found?"
    __parameter_input_metadata['IfSourceFileNotFound.Tooltip'] = \
        "Specify the file to remove, can use ${Property} notation."
    __parameter_input_metadata['IfSourceFileNotFound.Values'] = ["", "Ignore", "Warn", "Fail"]
    __parameter_input_metadata['IfSourceFileNotFound.Value.Default'] = "Warn"
    # RemoveIfFolder
    __parameter_input_metadata['RemoveIfFolder.Description'] = ""
    __parameter_input_metadata['RemoveIfFolder.Label'] = "Remove if folder"
    __parameter_input_metadata['RemoveIfFolder.Tooltip'] = ""
    __parameter_input_metadata['RemoveIfFolder.Values'] = ["", "False", "True"]
    __parameter_input_metadata['RemoveIfFolder.Value.Default'] = "False"

    # Choices for IfNotFound, used to validate parameter and display in editor
    __choices_IfSourceFileNotFound = ["Ignore", "Warn", "Fail"]

    def __init__(self) -> None:
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data
        super().__init__()
        self.command_name = "RemoveFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

        # Parameter input metadata
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

        # RemoveIfFolder must be a boolean value or None.
        # noinspection PyPep8Naming
        pv_RemoveIfFolder = self.get_parameter_value(parameter_name='RemoveIfFolder',
                                                     command_parameters=command_parameters)
        if not validator_util.validate_bool(pv_RemoveIfFolder, True, False):
            message = "The RemoveIfFolder must be either True or False."
            recommendation = "Specify a valid Boolean value."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # IfSourceFileNotFound is optional, will default to Warn at runtime
        # noinspection PyPep8Naming
        pv_IfSourceFileNotFound = self.get_parameter_value(parameter_name='IfSourceFileNotFound',
                                                           command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_IfSourceFileNotFound,
                                                      self.__choices_IfSourceFileNotFound, True, True):
            message = "IfSourceFileNotFound parameter is invalid."
            recommendation = "Specify the IfSourceFileNotFound parameter as blank or one of " + \
                             str(self.__choices_IfSourceFileNotFound)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
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
        Run the command.
        Remove the specified file from the operating system.

        Returns:
            None

        Raises:
                RuntimeError: if a runtime input error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Get data for the command
        # noinspection PyPep8Naming
        pv_SourceFile = self.get_parameter_value('SourceFile')
        # noinspection PyPep8Naming
        pv_IfSourceFileNotFound = self.get_parameter_value('IfSourceFileNotFound')
        if pv_IfSourceFileNotFound is None or pv_IfSourceFileNotFound == "":
            # noinspection PyPep8Naming
            pv_IfSourceFileNotFound = 'Warn'  # Default
        # noinspection PyPep8Naming
        pv_RemoveIfFolder = self.get_parameter_value('RemoveIfFolder', default_value="False")
        # noinspection PyPep8Naming
        pv_RemoveIfFolder = string_util.str_to_bool(pv_RemoveIfFolder)

        # Runtime checks on input

        # noinspection PyPep8Naming
        pv_SourceFile_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_SourceFile, self)))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings about command parameters."
            logger.warning(message)
            raise CommandError(message)

        # Remove the file

        # noinspection PyBroadException
        try:
            input_count = 1
            if not os.path.exists(pv_SourceFile_absolute):
                message = 'The source file does not exist: "' + pv_SourceFile_absolute + '"'
                if pv_IfSourceFileNotFound == 'Warn':
                    warning_count += 1
                    self.command_status.add_to_log(
                        CommandPhaseType.RUN,
                        CommandLogRecord(CommandStatusType.WARNING, message,
                                         "Verify that the source exists at the time the command is run."))
                    logger.warning(message)
                elif pv_IfSourceFileNotFound == 'Fail':
                    warning_count += 1
                    self.command_status.add_to_log(
                        CommandPhaseType.RUN,
                        CommandLogRecord(CommandStatusType.FAILURE, message,
                                         "Verify that the source exists at the time the command is run."))
                    logger.warning(message)
                input_count -= 1

            if input_count == 1:
                # noinspection PyBroadException
                try:
                    logger.info('Removing file "' + pv_SourceFile_absolute + '"')
                    os.remove(pv_SourceFile_absolute)
                except Exception:
                    if pv_RemoveIfFolder:
                        shutil.rmtree(pv_SourceFile_absolute)

        # noinspection PyBroadException
        except Exception:
            warning_count += 1
            message = 'Unexpected error removing file "' + pv_SourceFile_absolute + '"'
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "See the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise CommandError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
