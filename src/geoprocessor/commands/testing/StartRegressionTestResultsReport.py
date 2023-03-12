# StartRegressionTestResultsReport - command to start the regression test results report
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
# import os
import re


class StartRegressionTestResultsReport(AbstractCommand):
    """
    The StartRegressionTestResultsReport command starts the regression test results report file.
    The file is appended to each time a command file is run with a RunCommands command.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("OutputFile", type(""))
    ]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = \
        "Start a report file (and optionally results table) to be written to as regression tests are run."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # OutputFile
    __parameter_input_metadata['OutputFile.Description'] = "regression results report file"
    __parameter_input_metadata['OutputFile.Label'] = "Output file"
    __parameter_input_metadata['OutputFile.Required'] = True
    __parameter_input_metadata['OutputFile.Tooltip'] = (
        "The regression results report file to write, as an absolute path or relative to the command file.\n"
        "Can use ${Property}.")
    __parameter_input_metadata['OutputFile.FileSelector.Type'] = "Write"
    __parameter_input_metadata['OutputFile.FileSelector.Title'] = "Select the report file to create"
    __parameter_input_metadata['OutputFile.FileSelector.Filters'] = \
        ["Report file (*.txt)", "All files (*)"]

    # Only one regression command test file.
    __regression_test_file = None  # Name of regression test results file.
    __regression_test_fp = None  # Open file pointer to write regression test results.
    __regression_test_line_count = 0
    __regression_test_disabled_count = 0
    __regression_test_fail_count = 0
    __regression_test_pass_count = 0

    def __init__(self) -> None:
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data.
        super().__init__()
        self.command_name = "StartRegressionTestResultsReport"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display.
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata.
        self.parameter_input_metadata = self.__parameter_input_metadata

    @classmethod
    def append_to_regression_test_report(cls, is_enabled: bool, run_time_ms: int, test_pass_fail: str,
                                         expected_status: str, max_severity: CommandStatusType,
                                         test_command_file: str) -> None:
        """
        Add a record to the regression test results report and optionally results tables.
        The report is a simple text file that indicates whether a test passed.
        The data tables is a tables maintained by the processor to report on test results.

        Args:
            is_enabled (bool): whether the command file is enabled (it is useful to list all tests even if not
                enabled in order to generate an inventory of disabled tests that need cleanup)
            run_time_ms (int): run time for the command in milliseconds
            test_pass_fail (str): whether the test was a success or failure (it is possible for the test to
                be a successful even if the command file failed, if failure was expected)
            expected_status (str): the expected status (as a string)
            max_severity (CommandStatusType): the maximum severity from the command file that was run.
            test_command_file (str): the full path to the command file that was run.

        Returns:
            None.
        """
        logger = logging.getLogger(__name__)
        cls.__regression_test_line_count += 1
        indicator = " "
        enabled = "TRUE   "
        if is_enabled:
            if test_pass_fail.upper().find("FAIL") >= 0:
                indicator = "*"
                cls.__regression_test_fail_count += 1
            else:
                cls.__regression_test_pass_count += 1
        else:
            cls.__regression_test_disabled_count += 1
            enabled = "FALSE  "
            test_pass_fail = "    "
        line_count = '{:05d}'.format(cls.__regression_test_line_count)
        # String runTime = "        "
        # runTime = StringUtil.formatString(runTimeMs,"%7d")
        delim = "|"
        # nl = os.linesep
        nl = "\n"
        if cls.__regression_test_fp is None:
            # Regression test results report is not open.
            logger.warning("Regression test report file is not open.")
        else:
            cls.__regression_test_fp.write(
                line_count + delim +
                enabled + delim +
                # run_time is in the tables because in the report it makes it difficult to "diff" previous
                # and current reports because the run time will change for each run.
                # runTime + delim +
                indicator + '{:4}'.format(test_pass_fail) + indicator + delim +
                '{:10}'.format(expected_status) + delim +
                '{:10}'.format(str(max_severity)) + " " + delim + test_command_file + nl)
        # TODO smalers 2018-01-27 need to decide how to handle tables output.
        """
        if StartRegressionTestResultsReport.__regression_test_table is not None:
            TableRecord rec = __regressionTestTable.emptyRecord();
            # Look up the column numbers using the names from the tables initialization - make sure they agree!
            int col = -1;
            try:
                col = __regressionTestTable.getFieldIndex("Num");
                rec.setFieldValue(col, new Integer(__regressionTestLineCount));
                col = __regressionTestTable.getFieldIndex("Enabled");
                rec.setFieldValue(col, enabled.trim());
                col = __regressionTestTable.getFieldIndex("Run Time (ms)");
                rec.setFieldValue(col, runTimeMs);
                col = __regressionTestTable.getFieldIndex("Test Pass/Fail");
                rec.setFieldValue(col, testPassFail.trim());
                col = __regressionTestTable.getFieldIndex("Commands Expected Status");
                rec.setFieldValue(col, expectedStatus.trim());
                col = __regressionTestTable.getFieldIndex("Commands Actual Status");
                rec.setFieldValue(col, ""+maxSeverity);
                col = __regressionTestTable.getFieldIndex("Command File");
                rec.setFieldValue(col, testCommandFile);
                __regressionTestTable.addRecord(rec);
            except:
                # Just ignore adding the test record to the tables
                pass
            pass
        """

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

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, and if non-empty
        # triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            logger.warning(warning_message)
            raise CommandParameterError(warning_message)

        # Refresh the phase severity.
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    # Class method because need to call from outside an instance of this command.
    @classmethod
    def close_regression_test_report_file(cls) -> None:
        """
        Close the regression test report file.
        Also create a file that is the same but with name including '.nonum' at the end that
        does not have test numbers, which facilitates comparing the results, for example in KDiff3.

        Returns:
            None
        """

        logger = logging.getLogger(__name__)
        if cls.__regression_test_fp is None:
            # Regression test file was never opened:
            # - this is not important to most users, especially if not running tests
            # logger.info("The test results file was never opened so not closing.")
            return

        logger.info("Closing the test results file: " + cls.__regression_test_file)

        # nl = os.linesep
        nl = "\n"
        fp = cls.__regression_test_fp
        fp.write(
            "#----+-------+-------+------+----------+-----------+------------------" +
            "---------------------------------------------------------------------------" + nl)
        total_count = cls.__regression_test_fail_count + cls.__regression_test_pass_count +\
            cls.__regression_test_disabled_count
        fp.write(
            "FAIL count     = " + str(cls.__regression_test_fail_count) +
            ", " + '{:.3f}'.format(100.0*float(cls.__regression_test_fail_count)/float(total_count)) + "%" + nl)
        fp.write(
            "PASS count     = " + str(cls.__regression_test_pass_count) +
            ", " + '{:.3f}'.format(100.0*float(cls.__regression_test_pass_count)/float(total_count)) + "%" + nl)
        fp.write(
            "Disabled count = " + str(cls.__regression_test_disabled_count) +
            ", " + '{:.3f}'.format(100.0*float(cls.__regression_test_disabled_count)/float(total_count)) + "%" + nl)
        fp.write("#--------------------------------" + nl)
        fp.write("Total          = " + str(total_count) + nl)

        # Close the normal results file.
        cls.__regression_test_fp.close()
        cls.__regression_test_fp = None  # Set so that it can be opened again.

        # Create a filename that has extension: .nonum.ext
        ext = io_util.get_extension(cls.__regression_test_file)
        output_file = None
        if not ext:
            output_file = cls.__regression_test_file + ".nonum.txt"
        else:
            output_file = cls.__regression_test_file[0:len(cls.__regression_test_file) - len(ext)] + "nonum." + ext

        logger.info("Creating the 'nonum' test results file: " + output_file)

        try:
            # Open the normal results file to read and transfer to the 'nonum' version.
            with open(cls.__regression_test_file, 'r') as ifp, open(output_file, 'w') as ofp:
                # Read the normal report file, which contains the test number in the left column.
                while True:
                    line = ifp.readline()
                    if not line:
                        break
                    # Replace the number column with spaces:
                    # - the newline is read and is retaned when writing
                    line = re.sub("^[ 0-9][ 0-9][ 0-9][ 0-9][ 0-9]", "     ",line)
                    ofp.write(line)
        # noinspection PyBroadException
        except Exception:
            message = 'Unexpected error creating "nonum" test results file: {}'.format(output_file)
            logger.warning(message, exc_info=True)
        finally:
            if ifp:
                ifp.close()
            if ofp:
                ofp.close()

    # TODO smalers 2018-01-28 Evaluate whether to make this a class method.
    @staticmethod
    def __open_new_regression_test_report_file(output_file: str, append: bool = False) -> None:
        """
        Open a new regression test report file.
        This file is used by the processor to record the tests that are run and test status.

        Args:
            output_file:  Name of the output file to open.
            append:  Whether to append to the output file (default=False).

        Returns:
            None.
        """
        # TODO smalers 2018-01-27 evaluate how to use the counts (is used in Java).
        # Initialize the report counts.
        StartRegressionTestResultsReport.__regression_test_line_count = 0
        StartRegressionTestResultsReport.__regression_test_fail_count = 0
        StartRegressionTestResultsReport.__regression_test_pass_count = 0
        # TODO smalers 2018-01-27 evaluate how to support tables for output
        # Save the tables to be used for the regression summary.
        # __regressionTestTable = tables;
        # Print the report headers.
        mode = "w"
        if append:
            mode = "a"
        StartRegressionTestResultsReport.__regression_test_file = output_file
        StartRegressionTestResultsReport.__regression_test_fp = open(output_file, mode)
        fp = StartRegressionTestResultsReport.__regression_test_fp  # Local variable for class data.
        io_util.print_standard_file_header(fp, comment_line_prefix="#", max_width=80)
        # nl = os.linesep
        nl = "\n"
        fp.write("#" + nl)
        fp.write("# Command file regression test report from StartRegressionTestResultsReport() and RunCommands()" + nl)
        fp.write("#" + nl)
        fp.write("# Explanation of columns:" + nl)
        fp.write("#" + nl)
        fp.write("# Num: count of the tests" + nl)
        fp.write('# Enabled: TRUE if test enabled or FALSE if "#@enabled false" in command file' + nl)
        fp.write("# Run Time: run time in milliseconds" + nl)
        fp.write("# Test Pass/Fail:" + nl)
        fp.write("#    The test status below may be PASS or FAIL (or blank if disabled)." + nl)
        fp.write("#    A test will pass if the command file actual status matches the expected status." + nl)
        fp.write("#    Disabled tests are not run and do not count as PASS or FAIL." + nl)
        fp.write("#    Search for *FAIL* to find failed tests." + nl)
        fp.write("# Commands Expected Status:" + nl)
        fp.write("#    Default is assumed to be SUCCESS." + nl)
        fp.write("#    \"#@expectedStatus Warning|Failure\" comment in command file overrides default." + nl)
        fp.write("# Commands Actual Status:" + nl)
        fp.write("#    The most severe status (Success|Warning|Failure) for each command file." + nl)
        fp.write("#" + nl)
        fp.write("#    |       |Test  |Command   |Command    |" + nl)
        fp.write("#    |       |Pass/ |Expected  |Actual     |" + nl)
        fp.write("# Num|Enabled|Fail  |Status    |Status     |Command File" + nl)
        fp.write(
            "#----+-------+------+----------+-----------+------------------" +
            "---------------------------------------------------------------------------" + nl)

    def run_command(self) -> None:
        """
        Run the command.  Open a file to receive regression test results.

        Returns:
            None.

        Raises:
            RuntimeError: if a runtime input error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Get data for the command.
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value('OutputFile')

        # Runtime checks on input.

        if warning_count > 0:
            message = "There were {} warnings about command parameters.".format(warning_count)
            logger.warning(message)
            raise CommandError(message)

        # Open the regression test results file.

        output_file_absolute = pv_OutputFile
        # noinspection PyBroadException
        try:
            # noinspection PyPep8Naming
            output_file_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                         self.command_processor.expand_parameter_value(pv_OutputFile, self)))
            self.__open_new_regression_test_report_file(output_file_absolute, False)  # Do not append.
            logger.info('Opened regression test results report file: {}'.format(output_file_absolute))

            # Save the output file in the processor, used by the UI to list output files.
            self.command_processor.add_output_file(output_file_absolute)

        except Exception:
            warning_count += 1
            message = 'Unexpected error opening regression test results file: {}'.format(output_file_absolute)
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "See the log file for details."))

        if warning_count > 0:
            message = "There were {} warnings processing the command.".format(warning_count)
            logger.warning(message)
            raise CommandError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
