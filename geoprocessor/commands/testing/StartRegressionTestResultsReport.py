# StartRegressionTestResultsReport command

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


class StartRegressionTestResultsReport(AbstractCommand):
    """
    The StartRegressionTestResultsReport command starts the regression test results report file.
    The file is appended to each time a command file is run with a RunCommands command.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("OutputFile", type(""))
    ]

    # Only one regression command test file
    __regression_test_fp = None  # Open file pointer to write regression test results
    __regression_test_line_count = 0
    __regression_test_disabled_count = 0
    __regression_test_fail_count = 0
    __regression_test_pass_count = 0

    def __init__(self):
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data
        super(StartRegressionTestResultsReport, self).__init__()
        self.command_name = "StartRegressionTestResultsReport"
        self.command_parameter_metadata = self.__command_parameter_metadata

    @classmethod
    def append_to_regression_test_report(cls, is_enabled, run_time_ms, test_pass_fail, expected_status,
                                         max_severity, test_command_file):
        """
        Add a record to the regression test results report and optionally results table.
        The report is a simple text file that indicates whether a test passed.
        The data table is a table maintained by the processor to report on test results.

        Args:
            is_enabled (bool): whether the command file is enabled (it is useful to list all tests even if not
                enabled in order to generate an inventory of disabled tests that need cleanup)
            run_time_ms (int): run time for the command in milliseconds
            test_pass_fail (bool): whether the test was a success or failure (it is possible for the test to
                be a successful even if the command file failed, if failure was expected)
            expected_status (str): the expected status (as a string)
            max_severity (str): the maximum severity from the command file that was run.
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
        nl = os.linesep
        if cls.__regression_test_fp is None:
            # Regression test results report is not open
            logger.warning("Regression test report file is not open")
        else:
            cls.__regression_test_fp.write(
                line_count + delim +
                enabled + delim +
                # run_time is in the table because in the report it makes it difficult to "diff" previous
                # and current reports because the run time will change for each run
                # runTime + delim +
                indicator + '{:4}'.format(test_pass_fail) + indicator + delim +
                '{:10}'.format(expected_status) + delim +
                '{:10}'.format(max_severity) + " " + delim + test_command_file + nl)
        # TODO smalers 2018-01-27 need to decide how to handle table output
        """
        if StartRegressionTestResultsReport.__regression_test_table is not None:
            TableRecord rec = __regressionTestTable.emptyRecord();
            # Look up the column numbers using the names from the table initialization - make sure they agree!
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
                # Just ignore adding the test record to the table
                pass
            pass
        """

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

    @classmethod
    def close_regression_test_report_file(cls):
        """
        Close the regression test report file.

        Returns:
            None
        """
        logger = logging.getLogger(__name__)
        if cls.__regression_test_fp is None:
            # Regression test file was never opened
            logger.info("Regression report file is None")
            return

        nl = os.linesep
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

        cls.__regression_test_fp.close()
        cls.__regression_test_fp = None  # Set so that it can be opened again

    # TODO smalers 2018-01-28 Evaluate whether to make this a class method
    def __open_new_regression_test_report_file(self, output_file, append=False):
        """
        Open a new regression test report file.
        This file is used by the processor to record the tests that are run and test status.

        Args:
            output_file:  Name of the output file to open.
            append:  Whether to append to the output file (default=False).

        Returns:
            None.
        """
        # TODO smalers 2018-01-27 evaluate how to use the counts (is used in Java)
        # Initialize the report counts.
        StartRegressionTestResultsReport.__regression_test_line_count = 0
        StartRegressionTestResultsReport.__regression_test_fail_count = 0
        StartRegressionTestResultsReport.__regression_test_pass_count = 0
        # TODO smalers 2018-01-27 evaluate how to support table for output
        # Save the table to be used for the regression summary
        # __regressionTestTable = table;
        # Print the report headers.
        mode = "w"
        if append:
            mode = "a"
        StartRegressionTestResultsReport.__regression_test_fp = open(output_file, mode)
        fp = StartRegressionTestResultsReport.__regression_test_fp  # Local variable for class data
        io_util.print_standard_file_header(fp, comment_line_prefix="#", max_width=80)
        nl = os.linesep
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

    def run_command(self):
        """
        Run the command.  Open a file to receive regression test results.

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

        # Open the regression test results file

        try:
            pv_OutputFile_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                         self.command_processor.expand_parameter_value(pv_OutputFile, self)))
            self.__open_new_regression_test_report_file(pv_OutputFile_absolute, False)  # Do not append
            logger.info('Opened regression test results report file "' + pv_OutputFile_absolute + '"')

        except Exception as e:
            warning_count += 1
            message = 'Unexpected error opening file "' + pv_OutputFile_absolute + '"'
            traceback.print_exc(file=sys.stdout)
            logger.exception(message, e)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE, message,
                                 "See the log file for details."))

        except:
            warning_count += 1
            message = 'Unexpected error opening file "' + pv_OutputFile_absolute + '"'
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
