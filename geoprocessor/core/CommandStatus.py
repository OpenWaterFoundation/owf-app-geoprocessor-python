# CommandStatus - class to hold command status log records and status summary
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

import geoprocessor.core.command_status_type as command_status_type
import geoprocessor.core.command_phase_type as command_phase_type


class CommandStatus(object):
    """
    Class to hold the command status, including a log of messages generated
    when initializing, discovering, and running the command.
    """
    def __init__(self):
        """
        Initialize the instance.
        """
        # The default status of the command is UNKNOWN
        self.initialization_status = command_status_type.UNKNOWN
        self.discovery_status = command_status_type.UNKNOWN
        self.run_status = command_status_type.UNKNOWN

        self.initialization_log_list = []
        self.discovery_log_list = []
        self.run_log_list = []

    def add_to_log(self, command_phase, log_record):
        """
        Add a CommandLogRecord instance to the command status, for the specific command phase.
        The overall status for the command phase is also set to the maximum severity,
        which is the previous maximum severity and that of the new log record.

        Args:
            command_phase: The command phase for the log record, e.g, command_phase_type.RUN
            log_record: A CommandLogRecord instance.

        Returns:
            None.
        """
        if command_phase == command_phase_type.INITIALIZATION:
            self.initialization_status = command_status_type.max_severity(
                self.initialization_status, log_record.severity)
            self.initialization_log_list.append(log_record)
        elif command_phase == command_phase_type.DISCOVERY:
            self.discovery_status = command_status_type.max_severity(self.discovery_status, log_record.severity)
            self.discovery_log_list.append(log_record)
        elif command_phase == command_phase_type.RUN:
            self.run_status = command_status_type.max_severity(self.run_status, log_record.severity)
            self.run_log_list.append(log_record)

    def clear_log(self, command_phase=None):
        """
        Clear the CommandLogRecord list for the command.
        The run status for all phases is set to command_status_type.UNKNOWN.

        Args:
            command_phase: Phase of running a command (see command_phase_type) or None to clear logs for all phases.

        Returns:
            None.
        """
        if command_phase == command_phase_type.INITIALIZATION or command_phase is None:
            del self.initialization_log_list[:]
            self.initialization_status = command_status_type.UNKNOWN
        elif command_phase == command_phase_type.DISCOVERY or command_phase is None:
            del self.discovery_log_list[:]
            self.discovery_status = command_status_type.UNKNOWN
        elif command_phase == command_phase_type.RUN or command_phase is None:
            del self.run_log_list[:]
            self.run_status = command_status_type.UNKNOWN

    def get_command_status_for_phase(self, command_phase):
        """
        Return the command status for a phase of command processing.

        Args:
            command_phase:  Command phase for which to get the status.

        Returns:
            Command status for the specified command phase.
        """
        if command_phase == command_phase_type.INITIALIZATION:
            return self.initialization_status
        elif command_phase == command_phase_type.DISCOVERY:
            return self.discovery_status
        elif command_phase == command_phase_type.RUN:
            return self.run_status
        else:  # This should never happen.
            return command_status_type.UNKNOWN

    def get_log_count(self, phase=None, severity=None):
        """

        Args:
            phase: the command phase type (e.g., command_phase_type.RUN), or None to include all phases.
            severity: the severity (e.g., command_status_type.WARNING) of log messages to count

        Returns: the count of the log messages for the given phase and severity
        """
        log_count = 0
        if phase == command_phase_type.INITIALIZATION or phase is None:
            for log_message in self.initialization_log_list:
                if log_message.severity == severity:
                    log_count = log_count + 1
        if phase == command_phase_type.DISCOVERY or phase is None:
            for log_message in self.discovery_log_list:
                if log_message.severity == severity:
                    log_count = log_count + 1
        if phase == command_phase_type.RUN or phase is None:
            for log_message in self.run_log_list:
                if log_message.severity == severity:
                    log_count = log_count + 1
        return log_count

    def refresh_phase_severity(self, phase, severity_if_unknown):
        """
        Refresh the command status for a phase.  This should normally only be called when
        initializing a status or setting to success.  Otherwise, add_to_log() should be
        used and the status determined from the CommandLogRecord status values.
        This ensures that the command has a status even if no log messages were generated.

        Args:
            phase: Command phase, such as command_phase_type.RUN.
            severity_if_unknown: The severity to set for the phase if it is currently UNKNOWN.
                For example, specify as command_status_type.SUCCESS to override the
                initial command_status_type.UNKNOWN value.

        Returns:
            None.
        """
        if phase == command_phase_type.INITIALIZATION:
            if self.initialization_status == command_status_type.UNKNOWN:
                self.initialization_status = severity_if_unknown
        elif phase == command_phase_type.DISCOVERY:
            if self.discovery_status == command_status_type.UNKNOWN:
                self.discovery_status = severity_if_unknown
        elif phase == command_phase_type.RUN:
            if self.run_status == command_status_type.UNKNOWN:
                self.run_status = severity_if_unknown
