# WriteCommandSummaryToFile command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.io as io_util
import geoprocessor.util.validators as validators

import logging
import os
import sys
import traceback


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
        super(WriteCommandSummaryToFile, self).__init__()
        self.command_name = "WriteCommandSummaryToFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

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

        # OutputFile is required
        pv_OutputFile = self.get_parameter_value(parameter_name='OutputFile', command_parameters=command_parameters)
        if not validators.validate_string(pv_OutputFile, False, False):
            message = "The OutputFile must be specified."
            recommendation = "Specify the output file."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception
        if len(warning_message) > 0:
            logger.warning(warning_message)
            raise ValueError(warning_message)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

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
            # Close
            fp.close()

        except Exception as e:
            warning_count += 1
            message = 'Unexpected error writing file "' + pv_OutputFile_absolute + '"'
            traceback.print_exc(file=sys.stdout)
            logger.exception(message, e)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE, message,
                                 "See the log file for details."))

        except:
            warning_count += 1
            message = 'Unexpected error writing file "' + pv_OutputFile_absolute + '"'
            traceback.print_exc(file=sys.stdout)
            logger.exception(message)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE, message,
                                 "See the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            logger.warning(message)
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)

    def write_command_summary(self, fp):
        """
        Write the command summary tables.

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

        # Output a list of all commands with the most severe status

        i = 0
        for command in self.command_processor.commands:
            i += 1
            fp.write('<tr>' + nl)
            fp.write('<td><a href="#' + str(i) + '">' + str(i) + '</a></td>' + nl)
            status = command_util.get_highest_command_status_severity(self.command_status)
            fp.write('<td class="' + status + '">' + status + '</td>' + nl)
            status = self.command_status.get_command_status_for_phase(command_phase_type.INITIALIZATION)
            fp.write('<td class="' + status + '">' + status + '</td>' + nl)
            status = self.command_status.get_command_status_for_phase(command_phase_type.RUN)
            fp.write('<td class="' + status + '">' + status + '</td>' + nl)
            fp.write('<td><code>' + command.command_string + '<code></td>' + nl)
            fp.write('</tr>' + nl + nl)
        fp.write('</table>' + nl)

        # Output a table for each command

        i = 0
        for command in self.command_processor.commands:
            i += 1
            fp.write('<p>' + nl)
            fp.write('<a name="' + str(i) + '"></a><code>' + str(i) + ': ' + command.command_string + '</code>' + nl)

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
                fp.write('<td>' + command_phase_type.INITIALIZATION + '</td>' + nl)
                fp.write('<td class="' + log_record.severity + '">' + log_record.severity + '</td>' + nl)
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
                fp.write('<td>' + command_phase_type.DISCOVERY + '</td>' + nl)
                fp.write('<td class="' + log_record.severity + '">' + log_record.severity + '</td>' + nl)
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
                fp.write('<td>' + command_phase_type.RUN + '</td>' + nl)
                fp.write('<td class="' + log_record.severity + '">' + log_record.severity + '</td>' + nl)
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
        fp.write('  table.table-style-hover {' + nl)
        fp.write('     border-width: 1px; border-style: solid; border-color: #3A3A3A; border-collapse: collapse; padding: 4px' + nl)
        fp.write('  }' + nl)
        fp.write('  table.table-style-hover th {' + nl)
        fp.write('     border-width: 1px; border-style: solid; border-color: #3A3A3A; padding: 4px' + nl)
        fp.write('  }' + nl)
        fp.write('  table.table-style-hover td {' + nl)
        fp.write('     border-width: 1px; border-style: solid; border-color: #3A3A3A; padding: 4px' + nl)
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
