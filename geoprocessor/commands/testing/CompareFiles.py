# CompareFiles - command to compare files
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
import typing


class CompareFiles(AbstractCommand):
    """
    The CompareFiles command compares two files (typically text files) and indicates if there are
    differences.  The command is useful for automated testing.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("InputFile1", type("")),
        CommandParameterMetadata("InputFile2", type("")),
        CommandParameterMetadata("CommentLineChar", type("")),
        CommandParameterMetadata("MatchCase", type("")),
        CommandParameterMetadata("IgnoreWhitespace", type("")),
        CommandParameterMetadata("AllowedDiffCount", type("")),
        CommandParameterMetadata("IfDifferent", type("")),
        CommandParameterMetadata("IfSame", type("")),
        CommandParameterMetadata("LineDiffCountProperty", type("")),
        CommandParameterMetadata("FileDiffProperty", type(""))
    ]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = (
        "Compare text files to determine differences.\n"
        "For example, the command can be used to compare current and expected files produced by a program or "
        "process.")
    __command_metadata['EditorType'] = "Simple"

    # Parameter Metadata
    __parameter_input_metadata = dict()
    # InputFile1
    __parameter_input_metadata['InputFile1.Description'] = "name of the first file for comparison"
    __parameter_input_metadata['InputFile1.Label'] = "First input file"
    __parameter_input_metadata['InputFile1.Tooltip'] = \
        "The name of the first file to compare.  Can be specified using ${Property}."
    __parameter_input_metadata['InputFile1.Required'] = True
    __parameter_input_metadata['InputFile1.FileSelector.Type'] = "Read"
    __parameter_input_metadata['InputFile1.FileSelector.Title'] = "Select first file to compare"
    __parameter_input_metadata['InputFile1.FileSelector.Tooltip'] = "Browse for file"
    # InputFile2
    __parameter_input_metadata['InputFile2.Description'] = "name of the second file for comparison"
    __parameter_input_metadata['InputFile2.Label'] = "Second input file"
    __parameter_input_metadata['InputFile2.Tooltip'] = \
        "The name of the second file to compare. Can be specified using ${Property}."
    __parameter_input_metadata['InputFile2.Required'] = True
    __parameter_input_metadata['InputFile2.FileSelector.Type'] = "Read"
    __parameter_input_metadata['InputFile2.FileSelector.Title'] = "Select second file to compare"
    __parameter_input_metadata['InputFile2.FileSelector.Tooltip'] = "Browse for file"
    # CommentLineChar
    __parameter_input_metadata['CommentLineChar.Description'] = "character indicating comment lines"
    __parameter_input_metadata['CommentLineChar.Label'] = "Comment line character"
    __parameter_input_metadata['CommentLineChar.Tooltip'] = \
        "The character(s) that if found at the start of a line indicate comment lines."
    __parameter_input_metadata['CommentLineChar.Value.Default'] = "#"
    # MatchCase
    __parameter_input_metadata['MatchCase.Description'] = "match case"
    __parameter_input_metadata['MatchCase.Label'] = "Match case"
    __parameter_input_metadata['MatchCase.Tooltip'] = \
        "If True, lines must match exactly. If False, case is ignored for the comparison."
    __parameter_input_metadata['MatchCase.Values'] = ["", "True", "False"]
    __parameter_input_metadata['MatchCase.Value.Default'] = "True"
    # IgnoreWhitespace
    __parameter_input_metadata['IgnoreWhitespace.Description'] = "ignore whitespace"
    __parameter_input_metadata['IgnoreWhitespace.Label'] = "Ignore whitespace"
    __parameter_input_metadata['IgnoreWhitespace.Tooltip'] = (
        "If True, then each line is trimmed to remove leading and trailing whitespace characters ("
        "spaces, tabs, etc.) before doing the comparison.  If False, then whitespace is retained for "
        "the comparison.")
    __parameter_input_metadata['IgnoreWhitespace.Values'] = ["", "False", "True"]
    __parameter_input_metadata['IgnoreWhitespace.Value.Default'] = "False"
    # AllowedDiffCount
    __parameter_input_metadata['AllowedDiffCount.Description'] = "number of lines allowed to be different"
    __parameter_input_metadata['AllowedDiffCount.Label'] = "Allowed difference count"
    __parameter_input_metadata['AllowedDiffCount.Tooltip'] = \
        "The number of lines allowed to be different, when checking for differences. "
    __parameter_input_metadata['AllowedDiffCount.Value.Default'] = "0"
    # IfDifferent
    __parameter_input_metadata['IfDifferent.Description'] = "indicate action if source files are different"
    __parameter_input_metadata['IfDifferent.Label'] = "If different"
    __parameter_input_metadata['IfDifferent.Tooltip'] = (
        "Indicate the action if the source files are different: Ignore (ignore differences and do not "
        "warn), Warn (generate a warning message), Fail (generate a failure message)")
    __parameter_input_metadata['IfDifferent.Values'] = ["", "Ignore", "Warn", "Fail"]
    __parameter_input_metadata['IfDifferent.Value.Default'] = "Ignore"
    # IfSame
    __parameter_input_metadata['IfSame.Description'] = "indicate action if source files are same"
    __parameter_input_metadata['IfSame.Label'] = "If same"
    __parameter_input_metadata['IfSame.Tooltip'] = (
        "Indicate the action if the source files are the same: Ignore (ignore if same and do not warn), "
        "Warn (generate a warning message), Fail (generate a failure message)")
    __parameter_input_metadata['IfSame.Values'] = ["", "Ignore", "Warn", "Fail"]
    __parameter_input_metadata['IfSame.Value.Default'] = "Ignore"
    # LineDiffCountProperty
    __parameter_input_metadata['LineDiffCountProperty.Description'] = "property name for file difference count"
    __parameter_input_metadata['LineDiffCountProperty.Label'] = "Property for difference count"
    __parameter_input_metadata['LineDiffCountProperty.Tooltip'] = (
        "Name of property to set count of file count differences (integer).")
    # FileDiffProperty
    __parameter_input_metadata['FileDiffProperty.Description'] = "property name for whether files are different"
    __parameter_input_metadata['FileDiffProperty.Label'] = "Property for files different"
    __parameter_input_metadata['FileDiffProperty.Tooltip'] = (
        "Name of property to set whether files are different (boolean).")

    # Choices for IfSourceFileNotFound, used to validate parameter and display in editor
    __choices_MatchCase = ["True", "False"]
    __choices_IgnoreWhitespace = ["True", "False"]
    __choices_IfDifferent = ["Ignore", "Warn", "Fail"]
    __choices_IfSame = ["Ignore", "Warn", "Fail"]

    def __init__(self) -> None:
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data
        super().__init__()
        self.command_name = "CompareFiles"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

        # Parameter Metadata
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

        # InputFile1 is required
        # noinspection PyPep8Naming
        pv_InputFile1 = self.get_parameter_value(parameter_name='InputFile1', command_parameters=command_parameters)
        if not validator_util.validate_string(pv_InputFile1, False, False):
            message = "The InputFile1 parameter must be specified."
            recommendation = "Specify the first input file."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # InputFile2 is required
        # noinspection PyPep8Naming
        pv_InputFile2 = self.get_parameter_value(parameter_name='InputFile2', command_parameters=command_parameters)
        if not validator_util.validate_string(pv_InputFile2, False, False):
            message = "The InputFile2 parameter must be specified."
            recommendation = "Specify the second input file."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # CommentLineChar is optional, defaults to # at runtime, for now no checks

        # MatchCase is optional, defaults to True at runtime
        # noinspection PyPep8Naming
        pv_MatchCase = self.get_parameter_value(parameter_name='MatchCase',
                                                command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_MatchCase, self.__choices_MatchCase, True, True):
            message = "MatchCase parameter is invalid."
            recommendation = "Specify the MatchCase parameter as blank or one of " + str(self.__choices_MatchCase)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # IgnoreWhitespace is optional, defaults to True at runtime
        # noinspection PyPep8Naming
        pv_IgnoreWhitespace = self.get_parameter_value(parameter_name='IgnoreWhitespace',
                                                       command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_IgnoreWhitespace, self.__choices_MatchCase, True, True):
            message = "IgnoreWhitespace parameter is invalid."
            recommendation = "Specify the IgnoreWhitespace parameter as blank or one of " + \
                             str(self.__choices_IgnoreWhitespace)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # AllowedDiffCount is optional, defaults to 0 at runtime, but must be a number if specified
        # noinspection PyPep8Naming
        pv_AllowedDiffCount = self.get_parameter_value(parameter_name='AllowedDiffCount',
                                                       command_parameters=command_parameters)
        if not validator_util.validate_int(pv_AllowedDiffCount, True, True):
            message = "The AllowedDiffCount parameter is invalid."
            recommendation = "Specify the allowed difference count as an integer."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # IfDifferent is optional, defaults to Ignore at runtime
        # noinspection PyPep8Naming
        pv_IfDifferent = self.get_parameter_value(parameter_name='IfDifferent',
                                                  command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_IfDifferent, self.__choices_IfDifferent, True, True):
            message = "IfDifferent parameter is invalid."
            recommendation = "Specify the IfDifferent parameter as blank or one of " + str(self.__choices_IfDifferent)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # IfSame is optional, defaults to Ignore at runtime
        # noinspection PyPep8Naming
        pv_IfSame = self.get_parameter_value(parameter_name='IfSame',
                                             command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_IfSame, self.__choices_IfSame, True, True):
            message = "IfSame parameter is invalid."
            recommendation = "Specify the IfSame parameter as blank or one of " + str(self.__choices_IfSame)
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

    def read_line(self, inf: typing.TextIO, comment_line_char: str, ignore_whitespace: bool) -> str or None:
        """
        Read a single line from the indicated file.

        Args:
            inf (file):  Open file object to read.
            comment_line_char (str):  Character at start of line indicating a comment character.
            ignore_whitespace (bool):  Indicates whether whitespace should be ignored (strip whitespace).

        Returns:  The line as a string or None if the end of file (file is not closed).
        """
        comment_count = 0
        while True:
            # Read until a non-comment line is found
            # noinspection PyBroadException
            try:
                iline = inf.readline()
            except Exception:
                return None
            if iline is None:
                return None
                # TODO smalers 2018-01-08 need to figure out how to allow reading blank lines if not end of file
            elif len(iline) == 0:
                return None
            elif len(iline) > 0 and comment_line_char.find(iline[0:1]) >= 0:
                # check for comments
                comment_count += 1
                continue
            else:
                # logger.debug("Skipped " + str(comment_count) + " comments before getting to data line")
                pass
            if ignore_whitespace:
                return iline.strip()
            else:
                return iline

    def run_command(self) -> None:
        """
        Run the command.  Compare the input files.

        Returns:
            None

        Raises:
                RuntimeError: if a runtime input error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Get runtime data for the command

        # InputFile1
        # noinspection PyPep8Naming
        pv_InputFile1 = self.get_parameter_value('InputFile1')
        if pv_InputFile1 is not None and (pv_InputFile1 != "") and pv_InputFile1.find('${') >= 0:
            # noinspection PyPep8Naming
            pv_InputFile1 = self.command_processor.expand_parameter_value(pv_InputFile1, self)

        # InputFile2
        # noinspection PyPep8Naming
        pv_InputFile2 = self.get_parameter_value('InputFile2')
        if pv_InputFile2 is not None and (pv_InputFile2 != "") and pv_InputFile2.find('${') >= 0:
            # noinspection PyPep8Naming
            pv_InputFile2 = self.command_processor.expand_parameter_value(pv_InputFile2, self)

        # CommentLineChar
        # noinspection PyPep8Naming
        pv_CommentLineChar = self.get_parameter_value('CommentLineChar')
        if pv_CommentLineChar is None or pv_CommentLineChar == "":
            # noinspection PyPep8Naming
            pv_CommentLineChar = "#"  # Default value

        # MatchCase
        # noinspection PyPep8Naming
        pv_MatchCase = self.get_parameter_value('MatchCase')
        if pv_MatchCase is None or pv_MatchCase == "":
            # noinspection PyPep8Naming
            pv_MatchCase = True  # Default value

        # IgnoreWhitespace
        # noinspection PyPep8Naming
        pv_IgnoreWhitespace = self.get_parameter_value('IgnoreWhitespace')
        if pv_IgnoreWhitespace is None or pv_IgnoreWhitespace == "":
            # noinspection PyPep8Naming
            pv_IgnoreWhitespace = True  # Default value

        # AllowedDiffCount
        # noinspection PyPep8Naming
        pv_AllowedDiffCount = self.get_parameter_value('AllowedDiffCount')
        if pv_AllowedDiffCount is None or pv_AllowedDiffCount == "":
            allowed_diff_count = 0  # Default value
        else:
            allowed_diff_count = int(pv_AllowedDiffCount)
        # Convert IfDifferent and IfSame to internal types, Ignore will convert to None, which is OK

        # IfDifferent
        # noinspection PyPep8Naming
        pv_IfDifferent = self.get_parameter_value('IfDifferent')
        if pv_IfDifferent is None or pv_IfDifferent == "":
            # noinspection PyPep8Naming
            pv_IfDifferent = "Ignore"  # Default value
        # noinspection PyPep8Naming
        pv_IfDifferent_CommandStatusType = CommandStatusType.value_of(pv_IfDifferent, True)

        # IfSame
        # noinspection PyPep8Naming
        pv_IfSame = self.get_parameter_value('IfSame')
        if pv_IfSame is None or pv_IfSame == "":
            # noinspection PyPep8Naming
            pv_IfSame = "Ignore"  # Default value
        # noinspection PyPep8Naming
        pv_IfSame_CommandStatusType = CommandStatusType.value_of(pv_IfSame, True)

        # LineDiffCountProperty
        # noinspection PyPep8Naming
        pv_LineDiffCountProperty = self.get_parameter_value('LineDiffCountProperty')
        if pv_LineDiffCountProperty is not None and (pv_LineDiffCountProperty != "") and \
            pv_LineDiffCountProperty.find('${') >= 0:
            # noinspection PyPep8Naming
            pv_LineDiffCountProperty = self.command_processor.expand_parameter_value(pv_LineDiffCountProperty, self)

        # FileDiffProperty
        # noinspection PyPep8Naming
        pv_FileDiffProperty = self.get_parameter_value('FileDiffProperty')
        if pv_FileDiffProperty is not None and (pv_FileDiffProperty != "") and pv_FileDiffProperty.find('${') >= 0:
            # noinspection PyPep8Naming
            pv_FileDiffProperty = self.command_processor.expand_parameter_value(pv_FileDiffProperty, self)

        # Runtime checks on input

        # noinspection PyPep8Naming
        pv_InputFile1_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_InputFile1, self)))
        # noinspection PyPep8Naming
        pv_InputFile2_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_InputFile2, self)))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings about command parameters."
            logger.warning(message)
            raise ValueError(message)

        # Do the processing

        line_diff_count = 0
        line_count_compared = 0
        file1_end_found = False
        file2_end_found = False
        # noinspection PyBroadException
        try:
            input_count = 2
            if not os.path.exists(pv_InputFile1_absolute):
                warning_count += 1
                message = 'The first input file does not exist: "' + pv_InputFile1_absolute + '"'
                self.command_status.add_to_log(
                    CommandPhaseType.RUN,
                    CommandLogRecord(CommandStatusType.FAILURE, message,
                                     "Verify that the first input file exists at the time the command is run."))
                logger.warning(message)
                input_count -= 1

            if not os.path.exists(pv_InputFile2_absolute):
                warning_count += 1
                message = 'The second input file does not exist: "' + pv_InputFile2_absolute + '"'
                self.command_status.add_to_log(
                    CommandPhaseType.RUN,
                    CommandLogRecord(CommandStatusType.FAILURE, message,
                                     "Verify that the second input file exists at the time the command is run."))
                logger.warning(message)
                input_count -= 1

            if input_count == 2:
                # Try to do the comparison, just inline the logic
                # Open the files...
                in1 = open(pv_InputFile1_absolute, 'r')
                in2 = open(pv_InputFile2_absolute, 'r')
                # Loop through the files, comparing non-comment lines...
                while True:
                    # The following will discard comments and only return non-comment lines
                    # Therefore, comparisons are made on chunks of non-comment lines.
                    # TODO smalers 2018-01-08 Could make this comparison more intelligent if the # of comments varies
                    if not file1_end_found:
                        # Read another line if not at the end of the first file
                        iline1 = self.read_line(in1, pv_CommentLineChar, pv_IgnoreWhitespace)
                        if iline1 is None:
                            # First file is done...
                            logger.info("Found end of first file.")
                            file1_end_found = True
                    if not file2_end_found:
                        # Read another line if not at the end of the second file
                        iline2 = self.read_line(in2, pv_CommentLineChar, pv_IgnoreWhitespace)
                        if iline2 is None:
                            # Second file is done...
                            logger.info("Found end of second file.")
                            file2_end_found = True
                    if file1_end_found and file2_end_found:
                        # Both are done so quit comparing...
                        break
                    # Increment the line count compared (eventually will be number of data lines in longest file)
                    line_count_compared += 1
                    if file1_end_found or file2_end_found:
                        # One file is done so increment the difference count
                        line_diff_count += 1
                    else:
                        # Both have strings so can compare
                        if pv_MatchCase:
                            # Compare the lines as is since case-specific
                            if iline1 != iline2:
                                line_diff_count += 1
                        else:
                            # Compare by ignoring case
                            if iline1.upper() != iline2.upper():
                                line_diff_count += 1
                    # logger.debug('Compared:\n"' + iline1 + '"\n"' + iline2 + '"\nline_diff_count=' +
                    # str(line_diff_count))
                in1.close()
                in2.close()
                if line_count_compared == 0:
                    line_count_compared = 1  # to avoid divide by zero below - should never happen
                logger.info("There are " + str(line_diff_count) + " lines that are different, " +
                            '{:4f}'.format(100.0*float(line_diff_count)/float(line_count_compared)) +
                            '% (compared ' + str(line_count_compared) + ' lines from longest file).')

                if pv_LineDiffCountProperty is not None and pv_LineDiffCountProperty:
                    # Set a processor property for the line difference count property
                    self.command_processor.set_property(pv_LineDiffCountProperty, line_diff_count)
                    pass

                if pv_FileDiffProperty is not None and pv_FileDiffProperty:
                    if line_diff_count > allowed_diff_count:
                        # Set a processor property for whether the files are different or not
                        self.command_processor.set_property(pv_FileDiffProperty, True)
                    else:
                        self.command_processor.set_property(pv_FileDiffProperty, False)

        except Exception:
            warning_count += 1
            message = 'Unexpected error comparing file "' + pv_InputFile1_absolute + '" to "' + \
                      pv_InputFile2_absolute + '"'
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "See the log file for details."))

        file_end_string = ""
        if file1_end_found:
            file_end_string = ", file1 shorter than file2"
        elif file2_end_found:
            file_end_string = ", file2 shorter than file1"
        if line_diff_count > allowed_diff_count and \
            ((pv_IfDifferent_CommandStatusType == CommandStatusType.WARNING) or
             (pv_IfDifferent_CommandStatusType == CommandStatusType.FAILURE)):
            message = "" + str(line_diff_count) + " lines were different, " + \
                '{:4f}'.format(100.0*float(line_diff_count)/float(line_count_compared)) + \
                "% (compared " + str(line_count_compared) + " lines" + file_end_string + ")."
            if pv_IfDifferent_CommandStatusType == CommandStatusType.WARNING:
                logger.warning(message)
            else:
                logger.error(message)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(pv_IfDifferent_CommandStatusType,
                                 message, "Check files because difference is not expected."))
            raise RuntimeError(message)
        if (line_diff_count == 0) and (file1_end_found != file2_end_found) and \
            ((pv_IfSame_CommandStatusType == CommandStatusType.WARNING) or
             (pv_IfSame_CommandStatusType == CommandStatusType.FAILURE)):
            message = "No lines were different (the files are the same)."
            if pv_IfDifferent_CommandStatusType == CommandStatusType.WARNING:
                logger.warning(message)
            else:
                logger.error(message)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(pv_IfSame_CommandStatusType,
                                 message, "Check files because match is not expected."))
            raise RuntimeError(message)

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
