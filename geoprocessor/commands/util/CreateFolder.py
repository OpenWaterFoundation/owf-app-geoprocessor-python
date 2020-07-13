# CreateFolder - command to create a folder
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
import geoprocessor.util.validator_util as validator_util

import logging
import os
from pathlib import Path


class CreateFolder(AbstractCommand):
    """
    The CreateFolder command creates a folder and optionally its parent folders.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("Folder", type("")),
        CommandParameterMetadata("CreateParentFolders", type("")),
        CommandParameterMetadata("IfFolderExists", type(""))
    ]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Create a folder and optionally its parent folders."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # Folder
    __parameter_input_metadata['Folder.Description'] = "the name of the folder to create"
    __parameter_input_metadata['Folder.Label'] = "Folder"
    __parameter_input_metadata['Folder.Required'] = True
    __parameter_input_metadata['Folder.Tooltip'] = \
        "The name of the folder to create. Can be specified using ${Property}."
    __parameter_input_metadata['SourceFile.FileSelector.Type'] = "Read"
    __parameter_input_metadata['SourceFile.FileSelector.SelectFolder'] = True
    __parameter_input_metadata['SourceFile.FileSelector.Title'] = "Select the folder to create"
    __parameter_input_metadata['SourceFile.FileSelector.Filters'] = ["All files (*)"]
    # CreateParentFolders
    __parameter_input_metadata['CreateParentFolders.Description'] = "create parent folders"
    __parameter_input_metadata['CreateParentFolders.Label'] = "Create parent folders?"
    __parameter_input_metadata['CreateParentFolders.Tooltip'] = (
        "Indicate whether to create parent folders.")
    __parameter_input_metadata['CreateParentFolders.Values'] = ["", "False", "True"]
    __parameter_input_metadata['CreateParentFolders.Value.Default'] = "False"
    # IfFolderExists
    __parameter_input_metadata['IfFolderExists.Description'] = "action if folder exists"
    __parameter_input_metadata['IfFolderExists.Label'] = "If folder exists?"
    __parameter_input_metadata['IfFolderExists.Tooltip'] = (
        "Indicate an action if the folder exists:\n\n"
        "Ignore (ignore the existing folder and do not warn)\n"
        "Warn (generate a warning message)\n"
        "Fail (generate a failure message). ")
    __parameter_input_metadata['IfFolderExists.Values'] = ["", "Ignore", "Warn", "Fail"]
    __parameter_input_metadata['IfFolderExists.Value.Default'] = "Warn"

    # Choices for IfFolderExists, used to validate parameter and display in editor
    __choices_IfFolderExists = ["Ignore", "Warn", "Fail"]

    # Choices for CreateParentFolders, used to validate parameter and display in editor
    __choices_CreateParentFolders = ["False", "True"]

    def __init__(self) -> None:
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data
        super().__init__()
        self.command_name = "CreateFolder"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata
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

        # CreateParentFolders is optional, defaults to False at runtime
        # noinspection PyPep8Naming
        pv_IfNotFound = self.get_parameter_value(parameter_name='CreateParentFolders',
                                                 command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_IfNotFound, self.__choices_CreateParentFolders, True, True):
            message = "CreateParentFolders parameter is invalid."
            recommendation = "Specify the CreateParentFolders parameter as blank or one of " + \
                             str(self.__choices_IfFolderExists)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # IfFolderExists is optional, defaults to Warn at runtime
        # noinspection PyPep8Naming
        pv_IfNotFound = self.get_parameter_value(parameter_name='IfFolderExists',
                                                 command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_IfNotFound, self.__choices_IfFolderExists, True, True):
            message = "IfFolderExists parameter is invalid."
            recommendation = "Specify the IfFolderExists parameter as blank or one of " + \
                             str(self.__choices_IfFolderExists)
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
        Copy the source file to the destination.

        Returns:
            None

        Raises:
            RuntimeError: if a runtime input error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Get data for the command
        # noinspection PyPep8Naming
        pv_Folder = self.get_parameter_value('Folder')
        # noinspection PyPep8Naming
        pv_CreateParentFolders = self.get_parameter_value('CreateParentFolders')
        if pv_CreateParentFolders is None or pv_CreateParentFolders == "":
            # noinspection PyPep8Naming
            pv_CreateParentFolders =\
                CreateFolder.__parameter_input_metadata['CreateParentFolders.Value.Default']
        # noinspection PyPep8Naming
        pv_IfFolderExists = self.get_parameter_value('IfFolderExists')
        if pv_IfFolderExists is None or pv_IfFolderExists == "":
            # noinspection PyPep8Naming
            pv_IfFolderExists = CreateFolder.__parameter_input_metadata['IfFolderExists.Value.Default']
        logger.info("CreateParentFolders={}".format(pv_CreateParentFolders))
        logger.info("IfFolderExists={}".format(pv_IfFolderExists))

        # Runtime checks on input

        # noinspection PyPep8Naming
        pv_Folder_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_Folder, self)))
        logger.info("Creating folder: {}".format(pv_Folder_absolute))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings about command parameters."
            logger.warning(message)
            raise CommandError(message)

        # Do the processing

        folder_path = Path(pv_Folder_absolute)
        # noinspection PyBroadException
        try:
            if folder_path.exists():
                # Folder exists so generate a warning if requested
                message = 'The folder exists: "' + pv_Folder_absolute + '"'
                if pv_IfFolderExists.upper() == 'FAIL':
                    warning_count += 1
                    self.command_status.add_to_log(
                        CommandPhaseType.RUN,
                        CommandLogRecord(CommandStatusType.FAILURE, message,
                                         "Verify that the folder should not exist or ignore the error."))
                    logger.warning(message)
                elif pv_IfFolderExists.upper() == 'WARN':
                    warning_count += 1
                    self.command_status.add_to_log(
                        CommandPhaseType.RUN,
                        CommandLogRecord(CommandStatusType.WARNING, message,
                                         "Verify that the folder should not exist or ignore the error."))
                    logger.warning(message)
                else:
                    # Ignore
                    pass
            else:
                # Create the folder.
                parent_path = folder_path.parent
                if not parent_path.exists():
                    # Parent does not exist, create the folder and parents.
                    if pv_CreateParentFolders.upper() == 'TRUE':
                        logger.info("Creating folder and parents for '{}'".format(pv_Folder_absolute))
                        folder_path.mkdir(parents=True)
                    else:
                        message = "Parent folder does not exist and CreateParentFolders=False.  Cannot create folder."
                        warning_count += 1
                        self.command_status.add_to_log(
                            CommandPhaseType.RUN,
                            CommandLogRecord(CommandStatusType.WARNING, message,
                                             "Verify that the folder should not exist or ignore the error."))
                        logger.warning(message)
                else:
                    # Parent does exist.  Create the folder.
                    logger.info("Creating folder '{}'".format(pv_Folder_absolute))
                    folder_path.mkdir()

        except Exception:
            warning_count += 1
            message = 'Unexpected error creating folder "' + pv_Folder_absolute + '"'
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "See the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise CommandError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
