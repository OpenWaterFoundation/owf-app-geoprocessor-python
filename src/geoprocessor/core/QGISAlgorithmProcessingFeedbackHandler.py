# QGISAlgorithmProcessingFeedbackHandler - handle feedback calls from Processing
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


from qgis.core import QgsProcessingFeedback

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import logging


class QgisAlgorithmProcessingFeedbackHandler(QgsProcessingFeedback):
    """
    Provide methods o handle the Processing feedback calls.
    """

    def __init__(self, command: AbstractCommand) -> None:
        """
        Initialize the feedback handler.
        See https://qgis.org/pyqgis/latest/core/Processing/QgsProcessingFeedback.html.
        """
        # AbstractCommand data
        super().__init__()

        # The command associated with the feedback handler, so that feedback messages can be logged with the command.
        self.command = command

        # Warning count based on feedback, can be added to command internal warning count for overall warning count.
        self.warning_count = 0

        # Logger for the handler.
        self.logger = logging.getLogger(__name__)

    def get_warning_count(self):
        """
        Get the number of warnings handled.

        Returns:
            Number of warnings linked in 'reportError' function.
        """
        return self.warning_count

    def message_is_error(self, message: str) -> str or None:
        """
        Evaluate whether an algorithm message is an error.
        This is necessary because some algorithm messages are fatal but are not handles through 'reportError' function.

        Args:
            message (str): message to evaluate

        Returns:
            String recommendation to resolve the error or None if the message does not appear to be an error.
        """
        errors_to_check = {
            "ERROR: 1: DELETING": "Check that file is not being used in another application.",
            "PERMISSION DENIED": "Check that file is writeable and file is not being used in another application."
        }
        for key, value in errors_to_check.items():
            # self.logger.info("checking message {} against key {}".format(message, key) )
            if message.upper().find(key) >= 0:
                # The message includes the search string so assume it is an error:
                # - return the recommendation string
                # self.logger.info("Returning recommendation: {}".format(value))
                return value
        # No error string was matched.
        # self.logger.info("Returning none.")
        return None

    def pushCommandInfo(self, info: str) -> None:
        """
        Print command (command line program calls) output.

        Args:
            info:

        Returns:
            None
        """
        recommendation = self.message_is_error(info)
        if recommendation is None:
            # Was not an error so just log an info message.
            self.logger.info(info)
        else:
            # Message appears to be an error.
            self.report_error(info, fatal_error=True, recommendation=recommendation)

    def pushConsoleInfo(self, info: str) -> None:
        """
        Print algorithm console output.

        Args:
            info:

        Returns:
            None
        """
        recommendation = self.message_is_error(info)
        if recommendation is None:
            # Was not an error so just log an info message.
            self.logger.info(info)
        else:
            # Message appears to be an error.
            self.report_error(info, fatal_error=True, recommendation=recommendation)

    def pushDebugInfo(self, info: str) -> None:
        """
        Print algorithm debug output.

        Args:
            info:

        Returns:
            None
        """
        self.logger.debug(info)

    def pushInfo(self, info: str) -> None:
        """
        Print algorithm informational output.

        Args:
            info:

        Returns:
            None
        """
        recommendation = self.message_is_error(info)
        if recommendation is None:
            # Was not an error so just log an info message.
            self.logger.info(info)
        else:
            # Message appears to be an error.
            self.report_error(info, fatal_error=True, recommendation=recommendation)

    def report_error(self, message: str, fatal_error: bool = False, recommendation: str = None) -> None:
        """
        Handle error reporting.  This is an internal method to handle a recommendation.

        Args:
            message (str):  error message
            fatal_error (bool): whether the error is fatal (processing should not continue)
            recommendation (str): recommendation for command log message

        Returns:
            None
        """
        self.warning_count += 1
        message = "Algorithm feedback error:  {}.".format(message)
        if recommendation is None:
            recommendation = "Check the log file for details."
        if fatal_error:
            # Log as a failure.
            self.logger.error(message)
            self.command.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
        else:
            # Log as a warning.
            self.logger.warning(message)
            self.command.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.WARNING, message, recommendation))

    def reportError(self, message: str, fatalError: bool = False) -> None:
        """
        Handle error reporting.

        Args:
            message (str):  error message
            fatalError (bool): whether the error is fatal (processing should not continue)

        Returns:
            None
        """
        self.warning_count += 1
        message = "Algorithm feedback error:  {}.".format(message)
        recommendation = "Check the log file for details."
        if fatalError:
            # Log as a failure.
            self.logger.error(message, exc_info=True)
            self.command.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
        else:
            # Log as a warning.
            self.logger.warning(message, exc_info=True)
            self.command.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.WARNING, message, recommendation))

    def setProgressText(self, text: str) -> None:
        """
        Progress report text.

        Args:
            text:

        Returns:
            None
        """
        self.logger.info(text)
