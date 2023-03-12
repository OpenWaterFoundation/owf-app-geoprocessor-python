# CompareFilesEditor - class for CompareFiles editor
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

    # Usual locations of the KDiff3 software executable.
    visual_diff_program1 = r"C:\Program Files\KDiff3\kdiff3.exe"
    visual_diff_program2 = r"C:\Program Files\KDiff3\bin\kdiff3.exe"

    def __init__(self, command: AbstractCommand, app_session: GeoProcessorAppSession) -> None:
        """
        Initialize the AbstractCommandEditor instance.

        Args:
            command (AbstractCommand): a command object derived from AbstractCommand
            app_session (GeoProcessorAppSession): the application session, used to determine the user's home directory.

        Returns:
            None
        """

        # Declare this before calling super because called code initializes the buttons.
        self.visual_diff_button: QtWidgets.QPushButton or None = None

        # The following will initialize shared components in AbstractCommandEditor.
        super().__init__(command, app_session)

    def refresh_ui(self) -> None:
        """
        This function is called to ensure that the UI and command are consistent in the UI:

        1. The first time called:
            - Make sure the UI is up-to-date with initial command parameters
        2. Every time called:
            - Update the command string from values in the UI components.
            - Only non-empty values are set in the string.

        Returns:
            None
        """
        # Call the parent to make sure the UI is up-to-date.
        super().refresh_ui()

        # If both input files and visual diff program exist, enable the 'Visual Diff' button
        # noinspection PyBroadException
        try:
            # Get the input file parameter values from the UI.
            inputfile1 = self.get_parameter_value('InputFile1')
            inputfile2 = self.get_parameter_value('InputFile2')
            # Convert path to absolute
            inputfile1_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command.command_processor.get_property('WorkingDir'),
                                         self.command.command_processor.expand_parameter_value(inputfile1, self)))
            inputfile2_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command.command_processor.get_property('WorkingDir'),
                                         self.command.command_processor.expand_parameter_value(inputfile2, self)))
            if os.path.exists(inputfile1_absolute) and os.path.exists(inputfile2_absolute) and \
                    os.path.exists(self.visual_diff_program1):
                self.visual_diff_button.setEnabled(True)
            elif os.path.exists(inputfile1_absolute) and os.path.exists(inputfile2_absolute) and \
                    os.path.exists(self.visual_diff_program2):
                self.visual_diff_button.setEnabled(True)
            else:
                self.visual_diff_button.setEnabled(False)

        except Exception:
            # Log a message for developers.
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
        # Object name has parameter at front, which can be parsed out in event-handling code.
        self.visual_diff_button.setObjectName(qt_util.from_utf8("Cancel"))
        self.visual_diff_button.setToolTip("Run program to visually compare input files.")
        # self.visual_diff_button.clicked.connect(
        # lambda clicked, f.y_parameter: self.ui_action_open_file(self.load_file_button))
        # Use action role because action is handled in the dialog.
        self.dialog_ButtonBox.addButton(self.visual_diff_button, QtWidgets.QDialogButtonBox.ActionRole)
        # Use the following because connect() is shown as unresolved reference in PyCharm.
        # noinspection PyUnresolvedReferences
        self.visual_diff_button.clicked.connect(self.ui_action_visual_diff_clicked)

    def ui_action_visual_diff_clicked(self) -> None:
        """
        Run program to compare the input files.
        If here, the input files and KDiff3 executable exist so OK to run.
        """
        logger = logging.getLogger(__name__)
        inputfile1_absolute = "?"
        inputfile2_absolute = "?"
        visual_diff_program = None

        # noinspection PyBroadException
        try:
            # Get the input file parameter values from the UI.
            inputfile1 = self.get_parameter_value('InputFile1')
            inputfile2 = self.get_parameter_value('InputFile2')
            # Convert path to absolute paths.
            inputfile1_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command.command_processor.get_property('WorkingDir'),
                                         self.command.command_processor.expand_parameter_value(inputfile1, self)))
            inputfile2_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command.command_processor.get_property('WorkingDir'),
                                         self.command.command_processor.expand_parameter_value(inputfile2, self)))

            if os.path.exists(self.visual_diff_program1):
                visual_diff_program = self.visual_diff_program1
            elif os.path.exists(self.visual_diff_program2):
                visual_diff_program = self.visual_diff_program2

            if visual_diff_program:
                # Visual diff program does exist.
                logger.info("Running subprocess with arguments:")
                logger.info("  " + visual_diff_program)
                logger.info("  " + inputfile1_absolute)
                logger.info("  " + inputfile2_absolute)
                # Create the environment dictionary.
                # env_dict = RunProgram.create_env_dict(include_parent_env_vars, include_env_vars_dict,
                #            exclude_env_vars_list)
                # TODO smalers 2018-12-16 evaluate using shlex.quote() to handle command string.
                # TODO smalers 2018-12-16 handle standard input and output.
                # env_dict = {}
                # Do not use a command shell since can reference the executable program directly.
                use_command_shell = False
                # Use Popen parameters for no-wait process:
                # - if passing separate parameters the 'Popopen' handles escaping spaces, backslashes, etc.
                # - passing all the parameters caused an error so use the bare minimum
                args = [visual_diff_program, inputfile1_absolute, inputfile2_absolute]
                subprocess.Popen(args, shell=use_command_shell, creationflags=subprocess.DETACHED_PROCESS)
                # subprocess.Popen(args, shell=use_command_shell, env=env_dict, stdin=None, stdout=None,
                #                 close_fds=True, creationflags=subprocess.DETACHED_PROCESS)
                # subprocess.run([visual_diff_program, inputfile1_absolute, inputfile2_absolute],
                #               shell=use_command_shell, env=env_dict, stdin=None, stdout=None,
                #               close_fds=True, creationflags=subprocess.DETACHED_PROCESS)
                # Don't wait for exit status since an independent process.
                # Just let the process run separately until the diff tool is closed.
            else:
                # Visual diff program does not exist.
                message = "'Visual Diff' programs do not exist.\n" +\
                          self.visual_diff_program1 + "\n" +\
                          self.visual_diff_program2
                logger.warning(message, exc_info=True)
                qt_util.warning_message_box(message)

        except Exception:
            message = 'Error running program:\n  {}\n  {}\n  {}'.format(visual_diff_program,
                                                                        inputfile1_absolute, inputfile2_absolute)
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
