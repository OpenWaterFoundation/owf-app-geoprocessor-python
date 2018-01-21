# CreateRegressionTestCommandFile command

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
import re
import sys
import traceback


# TODO smalers 2018-01-21 This command is not yet fully functional
class CreateRegressionTestCommandFile(AbstractCommand):
    """
    The CreateRegressionTestCommandFile examines a folder tree and creates a command
    file with RunCommand commands for all GeoProcessor test command files to run.
    This is used to automate creating the full test suite to test the software.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("SearchFolder", type("")),
        CommandParameterMetadata("FilenamePattern", type("")),
        CommandParameterMetadata("OutputFile", type(""))
    ]

    def __init__(self):
        """
        Initialize a new instance of the command.
        """
        super(CreateRegressionTestCommandFile, self).__init__()
        self.command_name = "CreateRegressionTestCommandFile"
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

        # SearchFolder is required
        pv_SearchFolder = self.get_parameter_value(parameter_name='SearchFolder', command_parameters=command_parameters)
        if not validators.validate_string(pv_SearchFolder, False, False):
            message = "SearchFolder parameter has no value."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify the search folder."))
            print(message)

        # FilenamePattern is optional, will default to "test-*" at runtime

        # OutputFile is required
        pv_OutputFile = self.get_parameter_value(parameter_name='OutputFile', command_parameters=command_parameters)
        if not validators.validate_string(pv_OutputFile, False, False):
            message = "OutputFile parameter has no value."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify the output file."))
            print(message)

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
    def __determine_expected_status_parameter(cls, filename):
        """
        Determine the expected status parameter by searching the command file for an "@expectedStatus" string,
        generally in a comment at the top of the file.

        Args:
            filename (str): Name of file to open and scan.

        Returns:
            a string for the expectedStatus parameter or empty string if no expected status is known.

        Except:
            ValueError if the filename is not found.

        """
        expected_status_parameter = ""
        with open(filename, "r") as f:
            for line in f:
                if line is None:
                    break
                line_upper = line.upper()
                index = line_upper.find("@EXPECTEDSTATUS")
                if index >= 0:
                    # Get the status as the next token after the tag
                    # TODO smalers 2018-01-21 fix the next line
                    # expected_status=StringUtil.getToken(line.substring(index), " \t", StringUtil.DELIM_SKIP_BLANKS, 1)
                    expected_status = "Success"
                    # Translate variations to the official name recognized by RunCommands()
                    expected_status_upper = expected_status.upper()
                    if expected_status_upper == "WARN":
                        expected_status = "Warning"
                    elif expected_status_upper == "FAIL":
                        expected_status = "Failure"
                    expected_status_parameter = ",ExpectedStatus=" + expected_status
                    break
        return expected_status_parameter

    # TODO smalers 2018-01-20 Evaluate whether to include additional functionality as per TSTool
    @classmethod
    def __get_matching_filenames_in_tree(cls, file_list, path, pattern_regex):
        """
        Check all files and directories under the given folder and if
        the file matches a valid pattern it is added to the test list.

        Args:
            file_list ([str]): list of files that are matched, will be appended to.
            path (str): folder in which to start searching for matching files.
            pattern_regex (regex): Pattern to match when searching files, for example "test-*.gp".
        """
        logger = logging.getLogger(__name__)
        if os.path.isdir(path):
            # A directory (folder) so get the children and recurse
            children = os.listdir(path)
            for child in children:
                # Recursively call with full path using the folder and child name.
                CreateRegressionTestCommandFile.__get_matching_filenames_in_tree(file_list, os.path.join(path, child),
                                                                                 pattern_regex)
        else:
            # A file - add to list if file matches the pattern
            logger.info('Checking path "' + path + '" against "' + str(pattern_regex) + '"')
            # Do comparison on file name without directory.
            if pattern_regex.match(path):
                # FIXME SAM 2007-10-15 Need to enable something like the following to make more robust
                # && isValidCommandsFile( dir )
                logger.info("File matched.")
                # Exclude the command file if tag in the file indicates that it is not compatible with
                # this command's parameters.
                # Test is to be included for the OS and test suite.
                file_list.append(path)

    def run_command(self):
        """
        Run the command.

        Returns:
            Nothing.

        Raises:
                ValueError: if a runtime input error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Get data for the command
        pv_SearchFolder = self.get_parameter_value('SearchFolder')
        pv_FilenamePattern = self.get_parameter_value('FilenamePattern')
        if pv_FilenamePattern is None or pv_FilenamePattern == "":
            # The pattern that is desired is Test_*.gp
            pv_FilenamePattern = "[Tt][Ee][Ss][Tt]*.gp"
        pv_OutputFile = self.get_parameter_value('OutputFile')

        # Runtime checks on input

        search_folder_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(self, pv_SearchFolder)))
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(self, pv_OutputFile)))

        if not os.path.exists(search_folder_absolute):
            message = 'The folder to search "' + search_folder_absolute + '" does not exist.'
            logger.warning(message)
            warning_count += 1
            self.command_status.addToLog(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE,
                                 message, "Verify that the folder exists at the time the command is run."))
        else:
            files = []  # List of files to match
            filename_pattern_regex = pv_FilenamePattern.replace("*", "[^/]*")
            filename_pattern_regex_compiled = re.compile(filename_pattern_regex)
            CreateRegressionTestCommandFile.__get_matching_filenames_in_tree(files, search_folder_absolute,
                                                                             filename_pattern_regex_compiled)
            # Sort the list
            files = sorted(files)
            # Open the output file...
            # TODO smalers 2018-10-20 decide whether to support append mode
            out = open(output_file_absolute, "w")
            # Write a standard header to the file so that it is clear when the file was created
            io_util.print_standard_file_header(out, "#", 120, 0)
            # Include the setup command file if requested
            # logger.info('Adding commands from setup command file "' + setup_command_file_absolute + '"')
            # include_setup_file(out, setup_file_absolute, "setup")
            # Include the matching test cases
            nl = os.linesep  # newline character for operating system
            out.write("#" + nl)
            out.write("# The following " + str(len(files)) +
                      " test cases will be run to compare results with expected results." + nl)
            out.write("# Individual log files are generally created for each test.")
            # TODO smalers 2018-01-20 evaluate how to handle output table
            # out.write('StartRegressionTestResultsReport(OutputFile="' + output_file_absolute +
            # '.out.txt"' + tableParam + ")")
            # Find the list of matching files...
            for afile in files:
                # The command files to run are relative to the commands file being created.
                command_file_to_run = io_util.to_relative_path(output_file_absolute.getParent(), files)
                # Determine if the command file has @expectedStatus in it.  If so, define an ExpectedStatus
                # parameter for the command.
                out.write('RunCommands(InputFile="' + command_file_to_run + '"' +
                          CreateRegressionTestCommandFile.__determine_expected_status_parameter(afile) + ')')
            # Include the end command file if requested
            # Message.printStatus ( 2, routine, "Adding commands from end command file \"" + EndCommandFile_full + "\"")
            # includeCommandFile ( out, EndCommandFile_full, "end" );
            out.close()
            # Save the output file name...
            # set_output_file(output_file_absolute)

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings about command parameters."
            logger.warning(message)
            raise ValueError(message)

        # Do the processing

        try:
            pass

        except Exception as e:
            warning_count += 1
            message = 'Unexpected error creating regression test command file "' + output_file_absolute + '"'
            traceback.print_exc(file=sys.stdout)
            logger.exception(message, e)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE, message,
                                 "See the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
