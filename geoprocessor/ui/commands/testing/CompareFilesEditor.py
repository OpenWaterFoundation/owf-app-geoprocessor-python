# CompareFilesEditor - class for CompareFiles editor
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

from PyQt5 import QtWidgets

from geoprocessor.app.GeoProcessorAppSession import GeoProcessorAppSession
from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand
from geoprocessor.ui.commands.abstract.SimpleCommandEditor import SimpleCommandEditor

import geoprocessor.util.io_util as io_util

import geoprocessor.ui.util.qt_util as qt_util

import logging
import os
import subprocess


class CompareFilesEditor(SimpleCommandEditor):
    """
    Editor for CompareFiles command.
    The SimpleCommandEditor parent class provides most of the functionality and in addition a "Visual Diff" button
    is added to call KDiff3.
    """

    def __init__(self, command: AbstractCommand, app_session: GeoProcessorAppSession) -> None:
        """
        Initialize the Abstract Dialog instance.

        Args:
            command (AbstractCommand): a command object derived from AbstractCommand
            app_session (GeoProcessorAppSession): the application session, used to determine the user's home directory.
        """

        # The following will initialize shared components in AbstractCommandEditor
        super().__init__(command, app_session)

        self.visual_diff_button: QtWidgets.QPushButton or None = None

    def refresh_ui(self) -> None:
        """
        This function is called to ensure that the UI and command are consistent in the UI:

        1. The first time called:
            - Make sure the UI is up to date with initial command parameters
        2. Every time called:
            - Update the command string from values in the UI components.
            - Only non-empty values are set in the string.

        Returns:
            None
        """
        # Call the parent to make sure the UI is up to date
        super().refresh_ui()

        # If both input files and visual diff program exist, enable the 'Visual Diff' button
        # noinspection PyBroadException
        try:
            # Get the input file parameter values from the UI
            inputfile1 = self.get_parameter_value('InputFile1')
            inputfile2 = self.get_parameter_value('InputFile2')
            # Convert path to absolute
            inputfile1_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command.command_processor.get_property('WorkingDir'),
                                         self.command.command_processor.expand_parameter_value(inputfile1, self)))
            inputfile2_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command.command_processor.get_property('WorkingDir'),
                                         self.command.command_processor.expand_parameter_value(inputfile2, self)))
            visual_diff_program = r"C:\Program Files\KDiff3\kdiff3.exe"
            if os.path.exists(inputfile1_absolute) and os.path.exists(inputfile2_absolute) and \
                    os.path.exists(visual_diff_program):
                self.visual_diff_button.setEnabled(True)
            else:
                self.visual_diff_button.setEnabled(False)

        except Exception:
            # Log a message for developers
            logger = logging.getLogger(__name__)
            message = "Error updating 'Visual Diff' button state"
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

    def setup_ui_2(self) -> None:
        """
        Set up the user interface after dialog components have been added, specifically:
        - add a View Diff button on the right side

        Returns:
            None
        """

        self.visual_diff_button = QtWidgets.QPushButton("Visual Diff")
        # Object name has parameter at front, which can be parsed out in event-handling code
        self.visual_diff_button.setObjectName(qt_util.from_utf8("Cancel"))
        self.visual_diff_button.setToolTip("Run program to visually compare input files.")
        # self.visual_diff_button.clicked.connect(
        # lambda clicked, f.y_parameter: self.ui_action_open_file(self.load_file_button))
        # Use action role because action is handled in the dialog
        self.dialog_ButtonBox.addButton(self.visual_diff_button, QtWidgets.QDialogButtonBox.ActionRole)
        # Use the following because connect() is shown as unresolved reference in PyCharm
        # noinspection PyUnresolvedReferences
        self.visual_diff_button.clicked.connect(self.ui_action_visual_diff_clicked)

    def ui_action_visual_diff_clicked(self) -> None:
        """
        Run program to compare the input files.
        """
        logger = logging.getLogger(__name__)
        command_line = "unknown (not created before error)"
        # noinspection PyBroadException
        try:
            # Get the input file parameter values from the UI
            inputfile1 = self.get_parameter_value('InputFile1')
            inputfile2 = self.get_parameter_value('InputFile2')
            # Convert path to absolute
            inputfile1_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command.command_processor.get_property('WorkingDir'),
                                         self.command.command_processor.expand_parameter_value(inputfile1, self)))
            inputfile2_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command.command_processor.get_property('WorkingDir'),
                                         self.command.command_processor.expand_parameter_value(inputfile2, self)))

            command_line = r"C:\Program Files\KDiff3\kdiff3.exe {} {}".format(inputfile1_absolute, inputfile2_absolute)
            logger.info('Running command line "' + command_line + '"')
            # Create the environment dictionary
            # env_dict = RunProgram.create_env_dict(include_parent_env_vars, include_env_vars_dict,
            #            exclude_env_vars_list)
            # TODO smalers 2018-12-16 evaluate using shlex.quote() to handle command string
            # TODO smalers 2018-12-16 handle standard input and output
            env_dict = {}
            use_command_shell = False
            p = subprocess.Popen(command_line, shell=use_command_shell, env=env_dict)
            # Wait for the process to terminate since need it to be done before other commands do their work
            # with the command output.
            p.wait()
            return_status = p.poll()
            if return_status != 0:
                # TODO smalers 2020-03-30 KDiff3 seems to exist with 1 when it should be 0
                # - therefore, don't include this check for now
                # message = 'Error running program (exit code {}):  {}'.format(return_status, command_line)
                # logger.warning(message, exc_info=True)
                # qt_util.warning_message_box(message)
                pass

        except Exception:
            message = 'Error running program:  {}'.format(command_line)
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
