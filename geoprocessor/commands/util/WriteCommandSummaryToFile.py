# WriteCommandSummaryToFile - command to write command log summary to a file
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


class WriteCommandSummaryToFile(AbstractCommand):
    """
    The WriteCommandsSummaryToFile command writes a summary of command run information.
    CommandLogRecord instances are output to a simple HTML file.
    """

    # TODO smalers 2018-01-28 in the future allow "Format", with "HTML" as default.
    __command_parameter_metadata = [
        CommandParameterMetadata("OutputFile", type(""))
    ]

    def __init__(self):
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data
        super().__init__()
        self.command_name = "WriteCommandSummaryToFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = "This command writes command logging messages to a summary file."
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # OutputFile
        self.parameter_input_metadata['OutputFile.Description'] = "the output file to write"
        self.parameter_input_metadata['OutputFile.Label'] = "Output File"
        self.parameter_input_metadata['OutputFile.Required'] = True
        self.parameter_input_metadata['OutputFile.Tooltip'] = \
            "The output file to write, as an absolute path or relative to the command file.\n" \
            "Can use ${Property}."
        self.parameter_input_metadata['OutputFile.FileSelector.Type'] = "Write"
        self.parameter_input_metadata['OutputFile.FileSelector.Title'] = "select the output file to write to"

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning_message = ""
        logger = logging.getLogger(__name__)

        # OutputFile is required
        pv_OutputFile = self.get_parameter_value(parameter_name='OutputFile', command_parameters=command_parameters)
        if not validators.validate_string(pv_OutputFile, False, False):
            message = "The OutputFile must be specified."
            recommendation = "Specify the output file."
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
        Run the command.  Create a file summarizing command log messages, status, etc.

        Returns:
            None.

        Raises:
            RuntimeError: if a runtime input error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Get data for the command
        pv_OutputFile = self.get_parameter_value('OutputFile')

        # Runtime checks on input

        pv_OutputFile_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings about command parameters."
            logger.warning(message)
            raise ValueError(message)

        # Create the command summary file

        try:
            pv_OutputFile_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                         self.command_processor.expand_parameter_value(pv_OutputFile, self)))

            # Open the file and write command summary
            logger.info('Writing summary to "' + pv_OutputFile_absolute + '"')
            fp = open(pv_OutputFile_absolute, "w")
            self.write_file_header(fp)
            self.write_command_summary(fp)
            self.write_file_footer(fp)
            # Close the file
            fp.close()

        except Exception as e:
            warning_count += 1
            message = 'Unexpected error writing file "' + pv_OutputFile_absolute + '"'
            logger.error(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "See the log file for details."))

        except:
            warning_count += 1
            message = 'Unexpected error writing file "' + pv_OutputFile_absolute + '"'
            logger.error(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "See the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            logger.warning(message)
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)

    def write_command_summary(self, fp):
        """
        Write the command summary table.

        Args:
            fp: Open file object.

        Returns:
            None.
        """
        nl = os.linesep
        fp.write('<h1>Command Summary</h1>' + nl)

        fp.write('<table class="table-style-hover">' + nl)
        fp.write('<thead>' + nl)
        fp.write('<tr>' + nl)
        fp.write('<th>Command #</th>' + nl)
        fp.write('<th>Status (all)</th>' + nl)
        fp.write('<th>Status (init)</th>' + nl)
        # fp.write('<th>Max Status, discovery<th>' + nl)
        fp.write('<th>Status (run)</th>' + nl)
        fp.write('<th>Command</th>' + nl)
        fp.write('</tr>' + nl)
        fp.write('</thead>' + nl)

        # Output a list of all commands with the most severe status shown

        i = 0
        for command in self.command_processor.commands:
            i += 1
            fp.write('<tr>' + nl)
            fp.write('<td><a href="#' + str(i) + '">' + str(i) + '</a></td>' + nl)
            # TODO smalers 2018-01-29 Why don't the commented calls work?
            # overall_status = command_util.get_highest_command_status_severity(self.command_status)
            # initialization_status = self.command_status.get_command_status_for_phase(CommandPhaseType.INITIALIZATION)
            initialization_status = command.command_status.initialization_status
            # run_status = self.command_status.get_command_status_for_phase(CommandPhaseType.RUN)
            run_status = command.command_status.run_status
            overall_status = initialization_status
            if run_status.value > overall_status.value:
                overall_status = run_status
            fp.write('<td class="' + str(overall_status) + '">' + str(overall_status) + '</td>' + nl)
            fp.write('<td class="' + str(initialization_status) + '">' + str(initialization_status) + '</td>' + nl)
            fp.write('<td class="' + str(run_status) + '">' + str(run_status) + '</td>' + nl)
            fp.write('<td><code>' + command.command_string + '<code></td>' + nl)
            fp.write('</tr>' + nl + nl)
        fp.write('</table>' + nl)

        # Output a table for each command

        i = 0
        for command in self.command_processor.commands:
            i += 1
            fp.write('<p>' + nl)
            initialization_status = command.command_status.initialization_status
            run_status = command.command_status.run_status
            fp.write('<a name="' + str(i) + '"></a>' +
                     str(i) + ":" +
                     '<span class="' + str(initialization_status) + '" style="border: solid; border-width: 1px;">' +
                     'Initialization</span> <span class="' + str(run_status) +
                     '" style="border: solid; border-width: 1px;">'
                     + 'Run</span><code> ' + str(command.command_string) + '</code>' + nl)

            fp.write('<table class="table-style-hover">' + nl)
            fp.write('<thead>' + nl)
            fp.write('<tr>' + nl)
            fp.write('<th>#</th>' + nl)
            fp.write('<th>#</th>' + nl)
            fp.write('<th>Phase</th>' + nl)
            fp.write('<th>Severity</th>' + nl)
            fp.write('<th>Problem</th>' + nl)
            fp.write('<th>Recommendation</th>' + nl)
            fp.write('</tr>' + nl)
            fp.write('</thead>' + nl)

            # Output initialization log records
            j = 0
            for log_record in command.command_status.initialization_log_list:
                j += 1
                fp.write('<tr>' + nl)
                fp.write('<td>' + str(j) + '</th>' + nl)
                fp.write('<td></td>' + nl)
                fp.write('<td>' + str(CommandPhaseType.INITIALIZATION) + '</td>' + nl)
                fp.write('<td class="' + str(log_record.severity) + '">' + str(log_record.severity) + '</td>' + nl)
                fp.write('<td>' + log_record.problem + '</td>' + nl)
                fp.write('<td>' + log_record.recommendation + '</td>' + nl)
                fp.write('</tr>' + nl)

            # Output discovery log records
            j = 0
            for log_record in command.command_status.discovery_log_list:
                j += 1
                fp.write('<tr>' + nl)
                fp.write('<td>' + str(j) + '</td>' + nl)
                fp.write('<td></td>' + nl)
                fp.write('<td>' + str(CommandPhaseType.DISCOVERY) + '</td>' + nl)
                fp.write('<td class="' + str(log_record.severity) + '">' + str(log_record.severity) + '</td>' + nl)
                fp.write('<td>' + log_record.problem + '</td>' + nl)
                fp.write('<td>' + log_record.recommendation + '</td>' + nl)
                fp.write('</tr>' + nl)

            # Output run log records
            j = 0
            for log_record in command.command_status.run_log_list:
                j += 1
                fp.write('<tr>' + nl)
                fp.write('<td>' + str(j) + '</td>' + nl)
                fp.write('<td></td>' + nl)
                fp.write('<td>' + str(CommandPhaseType.RUN) + '</td>' + nl)
                fp.write('<td class="' + str(log_record.severity) + '">' + str(log_record.severity) + '</td>' + nl)
                fp.write('<td>' + log_record.problem + '</td>' + nl)
                fp.write('<td>' + log_record.recommendation + '</td>' + nl)
                fp.write('</tr>' + nl)

            # TODO smalers 2018-01-28 Need to figure out how to show records from original commands
            # when a command file is run by RunCommands() command

            fp.write('</table>' + nl)
            fp.write('<hr>' + nl)
            fp.write('</p>' + nl)

    def write_file_footer(self, fp):
        """
        Write the file header.

        Args:
            fp: Open file object.

        Returns:
            None.
        """
        nl = os.linesep
        fp.write('</body>' + nl)
        fp.write('</html>' + nl)

    def write_file_header(self, fp):
        """
        Write the file header.

        Args:
            fp: Open file object.

        Returns:
            None.
        """
        nl = os.linesep
        fp.write('<!DOCTYPE html>' + nl)
        fp.write('<html>' + nl)
        fp.write('<head>' + nl)
        fp.write('<meta charset="utf-8">' + nl)
        fp.write('<style>' + nl)
        fp.write('  html * {' + nl)
        fp.write('    font-family:  "Arial", Helvetica, sans-serif;' + nl)
        fp.write('  }' + nl)
        fp.write('  code {' + nl)
        fp.write('    font-family:  monospace;' + nl)
        fp.write('    font-style:  normal;' + nl)
        fp.write('    font-size:  large;' + nl)
        fp.write('  }' + nl)
        fp.write('  table.table-style-hover {' + nl)
        fp.write('     border-width: 1px; border-style: solid; border-color: #3A3A3A; ' +
                 'border-collapse: collapse; padding: 4px;' + nl)
        fp.write('  }' + nl)
        fp.write('  table.table-style-hover th {' + nl)
        fp.write('     border-width: 1px; border-style: solid; border-color: #3A3A3A; padding: 4px;' + nl)
        fp.write('  }' + nl)
        fp.write('  table.table-style-hover td {' + nl)
        fp.write('     border-width: 1px; border-style: solid; border-color: #3A3A3A; padding: 4px;' + nl)
        fp.write('  }' + nl)
        fp.write('  .UNKNOWN {' + nl)
        fp.write('     background-color: rgb(200,200,200);' + nl)
        fp.write('  }' + nl)
        fp.write('  .SUCCESS {' + nl)
        fp.write('     background-color: rgb(0,255,0);' + nl)
        fp.write('  }' + nl)
        fp.write('  .WARNING {' + nl)
        fp.write('     background-color: rgb(255,255,0);' + nl)
        fp.write('  }' + nl)
        fp.write('  .FAILURE {' + nl)
        fp.write('     background-color: rgb(255,0,0);' + nl)
        fp.write('  }' + nl)
        fp.write('</style>' + nl)
        fp.write('<title>Command Summary</title>' + nl)
        fp.write('</head>' + nl)
        fp.write('<body>' + nl)
