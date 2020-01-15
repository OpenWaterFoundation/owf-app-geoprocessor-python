# CommandLogRecord - class to store one log record for a command
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

from geoprocessor.core.CommandStatusType import CommandStatusType


class CommandLogRecord(object):
    """
    Command log record, which carries a single message and corresponding status.
    """

    def __init__(self, command_status_type: CommandStatusType, problem: str, recommendation: str,
                 log_record_type=None):
        """
        Initialize an instance.

        Args:
            command_status_type (CommandStatusType):  The command status type, indicating severity of log record.
            problem:  The message describing the problem.
            recommendation:  The recommendation for how to resolve the problem.
            log_record_type:  The log record type, to group the messages, currently not used.
        """
        self.severity = command_status_type
        self.problem = problem
        self.recommendation = recommendation
        # TODO smalers 2020-01-14 Log record type is not currently used
        self.log_record_type = log_record_type

        # Only used when accumulating logs such as with RunCommands
        # - in that case the log record is used to point to the original command,
        #   because multiple commands are executed within the RunCommands command file
        self.command = None
