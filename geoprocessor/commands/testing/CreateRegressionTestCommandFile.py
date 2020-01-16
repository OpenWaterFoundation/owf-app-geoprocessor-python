# CreateRegressionTestCommandFile - command to create a command file to run tests
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

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validator_util

import logging
import os
import re
from typing import Pattern


# TODO smalers 2018-01-21 This command is not yet fully functional
class CreateRegressionTestCommandFile(AbstractCommand):
    """
    The CreateRegressionTestCommandFile examines a folder tree and creates a command
    file with RunCommand commands for all GeoProcessor test command files to run.
    This is used to automate creating the full test suite to test the software.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("SearchFolder", type("")),
        CommandParameterMetadata("FilenamePattern", type("")),
        CommandParameterMetadata("OutputFile", type(""))
    ]

    def __init__(self) -> None:
        """
        Initialize a new instance of the command.
        """
        super().__init__()
        self.command_name = "CreateRegressionTestCommandFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = (
            "This command is used for software functional testing and validation of workflow processes.\n"
            "It searches all folders in the selected folder to find tests to run and creates a "
            "test suite command file.")
        self.command_metadata['EditorType'] = "Simple"

        # Parameter Metadata
        self.parameter_input_metadata = dict()
        # SearchFolder
        self.parameter_input_metadata['SearchFolder.Description'] = ""
        self.parameter_input_metadata['SearchFolder.Label'] = "Search folder"
        self.parameter_input_metadata['SearchFolder.Tooltip'] = (
            "The folder to search for regression test command files. "
            "All subfolders will also be searched. Can use ${Property}.")
        self.parameter_input_metadata['SearchFolder.Required'] = True
        self.parameter_input_metadata['SearchFolder.FileSelector.Type'] = "Read"
        self.parameter_input_metadata['SearchFolder.FileSelector.Button.Tooltip'] = "Browse for folder"
        self.parameter_input_metadata['SearchFolder.FileSelector.Tile'] = "Select folder to search for tests"
        self.parameter_input_metadata['SearchFolder.FileSelector.SelectFolder'] = True
        # OutputFile
        self.parameter_input_metadata['OutputFile.Description'] = "property file to write"
        self.parameter_input_metadata['OutputFile.Label'] = "Output file"
        self.parameter_input_metadata['OutputFile.Tooltip'] = (
            "The property file to write, as an absolute path or relative to the command file, can use ${Property}.")
        self.parameter_input_metadata['OutputFile.Required'] = True
        self.parameter_input_metadata['OutputFile.FileSelector.Type'] = "Write"
        # FilenamePattern
        self.parameter_input_metadata['FilenamePattern.Description'] = "pattern to find command files"
        self.parameter_input_metadata['FilenamePattern.Label'] = "Filename pattern"
        self.parameter_input_metadata['FilenamePattern.Tooltip'] = (
            "Pattern to find GeoProcessor command files, using * wildcards.")
        self.parameter_input_metadata['FilenamePattern.Value.Default'] = "test-*.gp"

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

        # SearchFolder is required
        # noinspection PyPep8Naming
        pv_SearchFolder = self.get_parameter_value(parameter_name='SearchFolder', command_parameters=command_parameters)
        if not validator_util.validate_string(pv_SearchFolder, False, False):
            message = "SearchFolder parameter has no value."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, "Specify the search folder."))
            print(message)

        # FilenamePattern is optional, will default to "test-*" at runtime

        # OutputFile is required
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value(parameter_name='OutputFile', command_parameters=command_parameters)
        if not validator_util.validate_string(pv_OutputFile, False, False):
            message = "OutputFile parameter has no value."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, "Specify the output file."))
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
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    @classmethod
    def __determine_expected_status_parameter(cls, filename: str) -> str:
        """
        Determine the expected status parameter by searching the command file for an "@expectedStatus" string,
        generally in a comment at the top of the file.

        Args:
            filename (str): Name of file to open and scan.

        Returns:
            A string for the expectedStatus parameter or empty string if no expected status is known.

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
                    expected_status = line_upper[index + len("@EXPECTEDSTATUS"):].strip()
                    # Translate variations to the official name recognized by RunCommands()
                    expected_status_upper = expected_status.upper()
                    if expected_status_upper == "WARN" or expected_status_upper == "WARNING":
                        expected_status = "Warning"
                    elif expected_status_upper == "FAIL" or expected_status_upper == "FAILURE":
                        expected_status = "Failure"
                    expected_status_parameter = ',ExpectedStatus="' + expected_status + '"'
                    break
        return expected_status_parameter

    # TODO smalers 2018-01-20 Evaluate whether to include additional functionality as per TSTool
    # Pattern type hint corresponds to re.compile("...")
    @classmethod
    def __get_matching_filenames_in_tree(cls, file_list: [str], path: str, pattern_regex: Pattern[str],
                                         pattern_string: str = None):
        """
        Check all files and directories under the given folder and if
        the file matches a valid pattern it is added to the test list.

        Args:
            file_list ([str]): list of files that are matched, will be appended to.
            path (str): folder in which to start searching for matching files.
            pattern_regex (regex): Compiled Python regex to match when searching files, for example "test-*.gp".
            pattern_string (str): The pattern regex string before being compiled, used in logging.
        """
        logger = logging.getLogger(__name__)
        # Use the following for troubleshooting
        debug = False
        if os.path.isdir(path):
            # A directory (folder) so get the children and recurse
            children = os.listdir(path)
            for child in children:
                # Recursively call with full path using the folder and child name.
                CreateRegressionTestCommandFile.__get_matching_filenames_in_tree(file_list, os.path.join(path, child),
                                                                                 pattern_regex,
                                                                                 pattern_string=pattern_string)
        else:
            # A file - add to list if file matches the pattern, but only check the filename (not leading path)
            filename = os.path.basename(path)
            if debug:
                logger.debug('Checking filename "' + filename + '" against "' + pattern_string + '"')
            # Do comparison on file name without directory.
            match_object = pattern_regex.match(filename)
            # If the match_object matching string is the same length as the input, then the whole string matches.
            # Otherwise, only a leading part matched this is not an exact match on the filename.
            # Note that the MatchObject.end() seems to be one past the input filename last character.
            # if match_object is not None:
            #    # logger.info("start=" + str(match_object.start()))
            #    # logger.info("end=" + str(match_object.end()))
            if match_object is not None and match_object.start() == 0 and match_object.end() == len(filename):
                # FIXME SAM 2007-10-15 Need to enable something like the following to make more robust
                # && isValidCommandsFile( dir )
                if debug:
                    logger.debug("File matched.")
                # Exclude the command file if tag in the file indicates that it is not compatible with
                # this command's parameters.
                # Test is to be included for the OS and test suite.
                # Include the path because it should be relative to the search path.
                file_list.append(path)
            else:
                if debug:
                    logger.debug("File not matched.")
                pass

    def run_command(self) -> None:
        """
        Run the command.

        Returns:
            None

        Raises:
                ValueError: if a runtime input error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Get data for the command
        # noinspection PyPep8Naming
        pv_SearchFolder = self.get_parameter_value('SearchFolder')
        # noinspection PyPep8Naming
        pv_FilenamePattern = self.get_parameter_value('FilenamePattern')
        if pv_FilenamePattern is None or pv_FilenamePattern == "":
            # The pattern that is desired is test_*.gp, using globbing syntax
            # noinspection PyPep8Naming
            pv_FilenamePattern = "[Tt][Ee][Ss][Tt]-*.gp"
            # noinspection PyPep8Naming
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value('OutputFile')

        # Runtime checks on input

        working_dir = self.command_processor.get_property('WorkingDir')
        logger.info('working_dir: "' + working_dir + '"')
        search_folder_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(working_dir, self.command_processor.expand_parameter_value(pv_SearchFolder, self)))
        search_folder_absolute_internal = io_util.verify_path_for_os(search_folder_absolute,
                                                                     always_use_forward_slashes=True)
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(working_dir, self.command_processor.expand_parameter_value(pv_OutputFile, self)))
        output_file_absolute_internal = io_util.verify_path_for_os(output_file_absolute,
                                                                   always_use_forward_slashes=True)
        logger.info('search_folder_absolute: "' + search_folder_absolute + '"')
        logger.info('search_folder_absolute_internal: "' + search_folder_absolute_internal + '"')

        if not os.path.exists(search_folder_absolute_internal):
            message = 'The folder to search "' + search_folder_absolute + '" does not exist.'
            logger.warning(message)
            warning_count += 1
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE,
                                 message, "Verify that the folder exists at the time the command is run."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings about command parameters."
            logger.warning(message)
            raise ValueError(message)

        # Do the processing

        # noinspection PyBroadException
        try:
            # Output folder is used when constructing filenames for command files to run
            output_folder_absolute = os.path.dirname(output_file_absolute_internal)
            logger.info('output_folder_absolute: "' + output_folder_absolute + '"')
            logger.info('output_folder_absolute_internal: "' + output_file_absolute_internal + '"')
            files = []  # List of files to match
            # Convert globbing-style wildcards to Pythonic regex
            logger.info('Filename pattern using globbing = "' + pv_FilenamePattern + '"')
            # filename_pattern_regex = pv_FilenamePattern.replace("*", "[^/]*")
            # Match any character of any length, making sure that special characters are dealt with
            filename_pattern_regex = pv_FilenamePattern.replace(".", "\\.")  # So .gp is handled literally
            # The following is used to match between "test-" and ".gp"
            filename_pattern_regex = filename_pattern_regex.replace("*", ".*")
            logger.info('Filename pattern using Python regex = "' + filename_pattern_regex + '"')
            filename_pattern_regex_compiled = re.compile(filename_pattern_regex)
            CreateRegressionTestCommandFile.__get_matching_filenames_in_tree(files, search_folder_absolute_internal,
                                                                             filename_pattern_regex_compiled,
                                                                             pattern_string=filename_pattern_regex)
            # Sort the list
            files = sorted(files)
            # Open the output file...
            # TODO smalers 2018-10-20 decide whether to support append mode
            out = open(output_file_absolute_internal, "w")
            # Write a standard header to the file so that it is clear when the file was created
            io_util.print_standard_file_header(out, comment_line_prefix="#")
            # Include the setup command file if requested
            # logger.info('Adding commands from setup command file "' + setup_command_file_absolute + '"')
            # include_setup_file(out, setup_file_absolute, "setup")
            # Include the matching test cases
            # Python 2...
            # nl = os.linesep  # newline character for operating system
            # Python 3 translates \n into the OS-specific end of line so os.linesep introduces extra end of lines
            nl = "\n"
            out.write("#" + nl)
            out.write("# The following " + str(len(files)) +
                      " test cases will be run to compare results with expected results." + nl)
            out.write("# Individual log files are generally created for each test." + nl)
            # TODO smalers 2018-01-20 evaluate how to handle output table
            # - Currently the GeoProcessor does not have table commands
            table_param = ""
            # Use absolute path since each developer will regenerate this file.
            out.write('StartRegressionTestResultsReport(OutputFile="' +
                      output_file_absolute + '.out.txt"' + table_param + ")" + nl)
            # Find the list of matching files...
            # logger.debug('output_folder_absolute"' + output_folder_absolute + '"')
            for a_file in files:
                logger.info('Adding command file "' + a_file + '"')
                # The command files to run are relative to the commands file being created.
                # - use the operating system separator
                command_file_to_run = io_util.verify_path_for_os(
                    io_util.to_relative_path(output_folder_absolute, a_file))
                # Determine if the command file has @expectedStatus in it.  If so, define an ExpectedStatus
                # parameter for the command.
                logger.info('Relative path to command file is "' + command_file_to_run + '"')
                out.write('RunCommands(CommandFile="' + command_file_to_run + '"' +
                          CreateRegressionTestCommandFile.__determine_expected_status_parameter(a_file) + ')' + nl)
            # TODO smalers 2018-12-30 Maybe the output file is relative to the working folder
            # output_file_relative = io_util.to_relative_path(working_dir, output_file_absolute)
            # out.write('WriteCommandSummaryToFile(OutputFile="' + output_file_relative + '.summary.html")' + nl)
            out.write('WriteCommandSummaryToFile(OutputFile="' + output_file_absolute + '.summary.html")' + nl)
            # TODO smalers 2018-01-28 evaluate whether to support end content
            # Include the end command file if requested
            # Message.printStatus ( 2, routine, "Adding commands from end command file \"" + EndCommandFile_full + "\"")
            # includeCommandFile ( out, EndCommandFile_full, "end" );
            out.close()
            # Add the log file to output
            self.command_processor.add_output_file(output_file_absolute)

        except Exception:
            warning_count += 1
            message = 'Unexpected error creating regression test command file "' + output_file_absolute + '"'
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "See the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
