# RunCommands - command to run a command file
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

from geoprocessor.commands.testing.StartRegressionTestResultsReport import StartRegressionTestResultsReport

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


class RunCommands(AbstractCommand):
    """
    The RunCommands command runs a command file.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("CommandFile", type("")),
        CommandParameterMetadata("ExpectedStatus", type(""))
    ]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = (
        "Run a command file using a separate command processor as a 'child' of the main processor.\n"
        "This command can be used to manage workflow where multiple command files are run, "
        "and is also used extensively for testing,\n"
        "where a test suite consists of running separate test case command files.")
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # CommandFile
    __parameter_input_metadata['CommandFile.Description'] = "the command file to run"
    __parameter_input_metadata['CommandFile.Label'] = "Command file"
    __parameter_input_metadata['CommandFile.Required'] = True
    __parameter_input_metadata['CommandFile.Tooltip'] = \
        "The command file to run. A path relative to the master command file can be specified. Can use ${Property}."
    __parameter_input_metadata['CommandFile.FileSelector.Type'] = "Read"
    __parameter_input_metadata['CommandFile.FileSelector.Title'] = "Select command file to run"
    # ExpectedStatus
    __parameter_input_metadata['ExpectedStatus.Description'] = "used for testing"
    __parameter_input_metadata['ExpectedStatus.Label'] = "Expected status"
    __parameter_input_metadata['ExpectedStatus.Tooltip'] = (
        "Used for testing – indicates the expected status from the command, one of:\n\n"
        "Unknown\n"
        "Success\n"
        "Warning\n"
        "Failure\n\n"
        "If this parameter is NOT used, the command log messages from commands that are run will be\n"
        "appended to the RunCommands command log. However, using this parameter will not append those\n"
        "messages – this is used in automated testing to allow a successful test even when there are\n"
        "warning and failure messages.")
    __parameter_input_metadata['ExpectedStatus.Value.Default'] = "Success"
    __parameter_input_metadata['ExpectedStatus.Values'] = ["", "Unknown", "Success", "Warning", "Failure"]

    # Choices for ExpectedStatus, used to validate parameter and display in editor.
    __choices_ExpectedStatus: [str] = ["Unknown", "Success", "Warning", "Failure"]

    __PASS = "PASS"
    __FAIL = "FAIL"

    def __init__(self) -> None:
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data.
        super().__init__()
        self.command_name = "RunCommands"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display.
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata.
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

        # ExpectedStatus is optional, will default to Success at runtime.
        # noinspection PyPep8Naming
        pv_ExpectedStatus = self.get_parameter_value(parameter_name='ExpectedStatus',
                                                     command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_ExpectedStatus,
                                                      self.__choices_ExpectedStatus, True, True):
            message = "ExpectedStatus parameter is invalid."
            recommendation = "Specify the ExpectedStatus parameter as blank or one of " + \
                             str(self.__choices_ExpectedStatus)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
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

    def run_command(self) -> None:
        """
        Run the command.  Run a separate command file and save results to the current processor.

        Returns:
            None.

        Raises:
                ValueError: if a runtime input error occurs.
                RuntimeError: if a runtime error occurs.
        """
        # The following import is deferred until runtime because if included at the top of the module
        # it causes a circular dependency and the GeoProcessor won't load.
        from geoprocessor.core.CommandFileRunner import CommandFileRunner
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Get data for the command.
        # noinspection PyPep8Naming
        pv_CommandFile = self.get_parameter_value('CommandFile')
        # noinspection PyPep8Naming
        pv_ExpectedStatus = self.get_parameter_value('ExpectedStatus')
        # expected_status = pv_ExpectedStatus
        if pv_ExpectedStatus == "":
            # noinspection PyPep8Naming
            pv_ExpectedStatus = None  # Default - was not specified in the command.

        # Runtime checks on input.

        # noinspection PyPep8Naming
        pv_CommandFile_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_CommandFile, self)))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings about command parameters."
            logger.warning(message)
            raise CommandError(message)

        # Write the output file.

        # noinspection PyBroadException
        try:
            command_file_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                         self.command_processor.expand_parameter_value(pv_CommandFile, self)))
            logger.info('Processing commands from file "' + command_file_absolute + '" using command file runner.')

            runner = CommandFileRunner()
            # This will set the initial working directory of the runner to that of the command file.
            file_found = True
            try:
                runner.read_command_file(command_file_absolute)
            except FileNotFoundError:
                warning_count += 1
                message = 'File does not exist:  "' + command_file_absolute + '"'
                self.command_status.add_to_log(
                    CommandPhaseType.RUN,
                    CommandLogRecord(CommandStatusType.FAILURE, message,
                                     "Confirm that the command file exists."))
                # Set the following to skip code below
                file_found = False

            # If the command file is not enabled, don't need to initialize or process.
            # TODO SAM 2013-04-20 Even if disabled, will still run discovery above:
            # - need to disable discovery in this case
            is_enabled = runner.is_command_file_enabled()
            expected_status = str(CommandStatusType.SUCCESS)
            if pv_ExpectedStatus is not None:
                expected_status = pv_ExpectedStatus

            if not file_found:
                # Need to add logic to indicate a failed test.
                self.command_status.add_to_log(
                    CommandPhaseType.RUN,
                    CommandLogRecord(
                        CommandStatusType.FAILURE, "Command file does not exist.",
                        "Confirm that the command file exists."))
                # Set the results to fail.
                # test_pass_fail = self.__FAIL
            elif is_enabled:
                # TODO smalers, 2018-01-26 Java code set datastores here.
                # TODO SAM 2010-09-30 Need to evaluate how to share properties - issue is that built-in properties are
                # handled explicitly whereas user-defined properties are in a list that can be easily shared.
                # Also, some properties like the working directory receive special treatment.
                # For now don't bite off the property issue.
                runner.run_commands(env_properties=self.command_processor.env_properties)
                logger.info("Done running commands")
                # Total runtime for the commands.
                # long run_time_total = TSCommandProcessorUtil.getRunTimeTotal(runner.getProcessor().getCommands());

                # Set the CommandStatus for this command to the most severe status of the
                # commands file that was just run.
                max_severity = command_util.get_command_status_max_severity(runner.command_processor)
                logger.info("Max severity from commands = " + str(max_severity))
                # test_pass_fail = "????"  # Status for the test, which is not always the same as max_severity.
                if pv_ExpectedStatus is not None:
                    expected_status_type = CommandStatusType.value_of(expected_status, ignore_case=True)
                    if max_severity is expected_status_type:
                        # Expected status matches the actual so consider this a success.
                        # This should generally be used only when running a test that is expected to fail
                        # (e.g., run obsolete command or testing handling of errors).
                        self.command_status.add_to_log(
                            CommandPhaseType.RUN,
                            CommandLogRecord(CommandStatusType.SUCCESS,
                                             "Severity for RunCommands (" + str(max_severity) +
                                             ") is max of commands in command file that was run - matches expected (" +
                                             expected_status + ") so RunCommands status=Success.",
                                             "Additional status messages are omitted to allow test to be success - " +
                                             "refer to log file if warning/failure."))
                        # TODO SAM 2008-07-09 Need to evaluate how to append all the log messages but still
                        # have a successful status that shows in the displays.
                        # DO NOT append the messages from the command because their status will cause the
                        # error displays to show problem indicators.
                        test_pass_fail = self.__PASS
                    else:
                        # Expected status does NOT match the actual status so this is a failure.
                        self.command_status.add_to_log(
                            CommandPhaseType.RUN,
                            CommandLogRecord(CommandStatusType.SUCCESS,
                                             "Severity for RunCommands (" + str(max_severity) +
                                             ") is max of commands in command file that was run - " +
                                             "does not match expected (" +
                                             expected_status + ") so RunCommands status=Failure.",
                                             "Check the command to confirm the expected status."))
                        # TODO SAM 2008-07-09 Need to evaluate how to append all the log messages but still
                        # have a successful status that shows in the displays.
                        # DO NOT append the messages from the command because their status will cause the
                        # error displays to show problem indicators.
                        test_pass_fail = self.__FAIL
                else:
                    # TODO smalers 2018-01-28 evaluate whether this is needed given that success is default expected
                    # status.
                    # Expected status is not specified.
                    self.command_status.add_to_log(
                        CommandPhaseType.RUN,
                        CommandLogRecord(
                            max_severity, "Severity for RunCommands (" + str(max_severity) +
                            ") is max of commands in command file that was run.",
                            "Status messages from commands that were run are appended to RunCommand status messages."))

                    # Append the log records from the command file that was run.
                    # The status contains lists of CommandLogRecord for each run mode.
                    # For RunCommands() the log messages should be associated with the originating command,
                    # not this RunCommand command.
                    logger.info("Appending log records")
                    command_util.append_command_status_log_records(
                        self.command_status, runner.command_processor.commands)
                    if max_severity.value >= CommandStatusType.WARNING.value:
                        test_pass_fail = self.__FAIL
                    else:
                        test_pass_fail = self.__PASS

                # Add a record to the regression test report.

                logger.info("Adding record to regression test report")
                run_time_total = 0
                StartRegressionTestResultsReport.append_to_regression_test_report(
                    is_enabled, run_time_total,
                    test_pass_fail, expected_status, max_severity, command_file_absolute)

                # If it was requested to append the results to the calling processor, get
                # the results from the runner and do so.

                # if ( (AppendResults != null) && AppendResults.equalsIgnoreCase("true")) {
                #     TSCommandProcessor processor2 = runner.getProcessor();
                #     Object o_tslist = processor2.getPropContents("TSResultsList");
                #     PropList request_params = new PropList ( "" );
                #     if ( o_tslist != null ) {
                #         @SuppressWarnings("unchecked")
                #         List<TS> tslist = (List<TS>)o_tslist;
                #         int size = tslist.size()
                #         TS ts;
                #         for ( int i = 0; i < size; i++ ) {
                #             ts = tslist.get(i);
                #             request_params.setUsingObject( "TS", ts );
                #             processor.processRequest( "AppendTimeSeries", request_params );
                #         }
                #     }
                # }
                logger.info("...done processing commands from file.")
            else:
                # Add a record to the regression report (the is_enabled value is what is important for the report
                # because the test is not actually run).
                # TODO smalers 2018-01-26 finish.
                logger.info("Command file is not enabled")
                run_time_total = 0
                test_pass_fail = ""
                max_severity = CommandStatusType.UNKNOWN
                StartRegressionTestResultsReport.append_to_regression_test_report(
                    is_enabled, run_time_total,
                    test_pass_fail, expected_status, max_severity, command_file_absolute)
                pass

        except Exception:
            warning_count += 1
            message = 'Unexpected error running command file "' + pv_CommandFile_absolute + '"'
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "See the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            logger.warning(message)
            raise CommandError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
