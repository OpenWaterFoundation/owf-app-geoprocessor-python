# CopyFile - command to copy a file
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2019 Open Water Foundation
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

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validators

import logging
import os
from shutil import copyfile
import sys
import traceback


class CopyFile(AbstractCommand):
    """
    The CopyFile command copies a source file to a destination copy.
    The command is useful as a utility and is often used in automated testing to provide
    input data from a saved copy.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("SourceFile", type("")),
        CommandParameterMetadata("DestinationFile", type("")),
        CommandParameterMetadata("IfSourceFileNotFound", type(""))
    ]

    # Choices for IfSourceFileNotFound, used to validate parameter and display in editor
    __choices_IfSourceFileNotFound = ["Ignore", "Warn", "Fail"]

    def __init__(self):
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data
        super().__init__()
        # Name of command for menu and window title
        self.command_name = "CopyFile"
        # Description for menu "Command()... <description>"
        self.command_description = "Copy a file to a new file"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = {}
        self.command_metadata['Description'] = 'The CopyFile command copies a source file to a destination.'
        self.command_metadata['EditorType'] = 'Generic'

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            Nothing.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning_message = ""
        logger = logging.getLogger(__name__)

        # SourceFile is required
        pv_SourceFile = self.get_parameter_value(parameter_name='SourceFile', command_parameters=command_parameters)
        if not validators.validate_string(pv_SourceFile, False, False):
            message = "The SourceFile must be specified."
            recommendation = "Specify the source file."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # DestinationFile is required
        pv_DestinationFile = self.get_parameter_value(
            parameter_name='DestinationFile', command_parameters=command_parameters)
        if not validators.validate_string(pv_DestinationFile, False, False):
            message = "The DestinationFile must be specified."
            recommendation = "Specify the destination file."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # IfSourceFileNotFound is optional, defaults to Warn at runtime
        pv_IfNotFound = self.get_parameter_value(parameter_name='IfSourceFileNotFound',
                                                 command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_IfNotFound, self.__choices_IfSourceFileNotFound, True, True):
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
            raise ValueError(warning_message)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def run_command(self):
        """
        Run the command.
        Copy the source file to the destination.

        Returns:
            Nothing.

        Raises:
                RuntimeError: if a runtime input error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Get data for the command
        pv_SourceFile = self.get_parameter_value('SourceFile')
        pv_DestinationFile = self.get_parameter_value('DestinationFile')

        # Runtime checks on input

        pv_SourceFile_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_SourceFile, self)))
        pv_DestinationFile_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_DestinationFile, self)))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings about command parameters."
            logger.warning(message)
            raise ValueError(message)

        # Do the processing

        try:
            input_count = 2
            if not os.path.exists(pv_SourceFile_absolute):
                warning_count += 1
                message = 'The source file does not exist: "' + pv_SourceFile_absolute + '"'
                self.command_status.addToLog(
                    CommandPhaseType.RUN,
                    CommandLogRecord(CommandStatusType.FAILURE, message,
                                     "Verify that the source exists at the time the command is run."))
                logger.warning(message)
                input_count -= 1

            destination_folder = os.path.dirname(pv_DestinationFile_absolute)
            if not os.path.exists(destination_folder):
                warning_count += 1
                message = 'The destination folder does not exist: "' + destination_folder + '"'
                self.command_status.addToLog(
                    CommandPhaseType.RUN,
                    CommandLogRecord(CommandStatusType.FAILURE, message,
                                     "Verify that the destination folder exists at the time the command is run."))
                input_count -= 1

            if input_count == 2:
                # Try to do the copy
                logger.info('Copying file "' + pv_SourceFile_absolute + '" to "' + pv_DestinationFile_absolute + '"')
                copyfile(pv_SourceFile_absolute, pv_DestinationFile_absolute)

        except Exception as e:
            warning_count += 1
            message = 'Unexpected error copying file "' + pv_SourceFile_absolute + '" to "' + \
                      pv_DestinationFile_absolute + '"'
            traceback.print_exc(file=sys.stdout)
            logger.exception(message, e)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "See the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
