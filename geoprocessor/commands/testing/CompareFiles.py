# CompareFiles command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validators

import logging
import os
import sys
import traceback


class CompareFiles(AbstractCommand):
    """
    The CompareFiles command compares two files (typically text files) and indicates if there are
    differences.  The command is useful for automated testing.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("InputFile1", type("")),
        CommandParameterMetadata("InputFile2", type("")),
        CommandParameterMetadata("CommentLineChar", type("")),
        CommandParameterMetadata("MatchCase", type("")),
        CommandParameterMetadata("IgnoreWhitespace", type("")),
        CommandParameterMetadata("AllowedDiffCount", type("")),
        CommandParameterMetadata("IfDifferent", type("")),
        CommandParameterMetadata("IfSame", type(""))
    ]

    # Choices for IfSourceFileNotFound, used to validate parameter and display in editor
    __choices_MatchCase = ["True", "False"]
    __choices_IgnoreWhitespace = ["True", "False"]
    __choices_IfDifferent = ["Ignore", "Warn", "Fail"]
    __choices_IfSame = ["Ignore", "Warn", "Fail"]

    def __init__(self):
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data
        super().__init__()
        self.command_name = "CompareFiles"
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

        # InputFile1 is required
        pv_InputFile1 = self.get_parameter_value(parameter_name='InputFile1', command_parameters=command_parameters)
        if not validators.validate_string(pv_InputFile1, False, False):
            message = "The InputFile1 parameter must be specified."
            recommendation = "Specify the first input file."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # InputFile2 is required
        pv_InputFile2 = self.get_parameter_value(parameter_name='InputFile2', command_parameters=command_parameters)
        if not validators.validate_string(pv_InputFile2, False, False):
            message = "The InputFile2 parameter must be specified."
            recommendation = "Specify the second input file."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # CommentLineChar is optional, defaults to # at runtime, for now no checks

        # MatchCase is optional, defaults to True at runtime
        pv_MatchCase = self.get_parameter_value(parameter_name='MatchCase',
                                                command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_MatchCase, self.__choices_MatchCase, True, True):
            message = "MatchCase parameter is invalid."
            recommendation = "Specify the MatchCase parameter as blank or one of " + str(self.__choices_MatchCase)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # IgnoreWhitespace is optional, defaults to True at runtime
        pv_IgnoreWhitespace = self.get_parameter_value(parameter_name='IgnoreWhitespace',
                                                       command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_IgnoreWhitespace, self.__choices_MatchCase, True, True):
            message = "IgnoreWhitespace parameter is invalid."
            recommendation = "Specify the IgnoreWhitespace parameter as blank or one of " + \
                             str(self.__choices_IgnoreWhitespace)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # AllowedDiffCount is optional, defaults to 0 at runtime, but must be a number if specified
        pv_AllowedDiffCount = self.get_parameter_value(parameter_name='AllowedDiffCount',
                                                       command_parameters=command_parameters)
        if not validators.validate_int(pv_AllowedDiffCount, True, True):
            message = "The AllowedDiffCount parameter is invalid."
            recommendation = "Specify the allowed difference count as an integer."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # IfDifferent is optional, defaults to Ignore at runtime
        pv_IfDifferent = self.get_parameter_value(parameter_name='IfDifferent',
                                                  command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_IfDifferent, self.__choices_IfDifferent, True, True):
            message = "IfDifferent parameter is invalid."
            recommendation = "Specify the IfDifferent parameter as blank or one of " + str(self.__choices_IfDifferent)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # IfSame is optional, defaults to Ignore at runtime
        pv_IfSame = self.get_parameter_value(parameter_name='IfSame',
                                             command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_IfSame, self.__choices_IfSame, True, True):
            message = "IfSame parameter is invalid."
            recommendation = "Specify the IfSame parameter as blank or one of " + str(self.__choices_IfSame)
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
    def __read_line(cls, inf, comment_line_char, ignore_whitespace):
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
            try:
                iline = inf.readline()
            except Exception as e:
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

    def run_command(self):
        """
        Run the command.  Compare the input files.

        Returns:
            Nothing.

        Raises:
                RuntimeError: if a runtime input error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Get runtime data for the command
        pv_InputFile1 = self.get_parameter_value('InputFile1')
        pv_InputFile2 = self.get_parameter_value('InputFile2')
        pv_CommentLineChar = self.get_parameter_value('CommentLineChar')
        if pv_CommentLineChar is None or pv_CommentLineChar == "":
            pv_CommentLineChar = "#"  # Default value
        pv_MatchCase = self.get_parameter_value('MatchCase')
        if pv_MatchCase is None or pv_MatchCase == "":
            pv_MatchCase = True  # Default value
        pv_IgnoreWhitespace = self.get_parameter_value('IgnoreWhitespace')
        if pv_IgnoreWhitespace is None or pv_IgnoreWhitespace == "":
            pv_IgnoreWhitespace = True  # Default value
        pv_AllowedDiffCount = self.get_parameter_value('AllowedDiffCount')
        if pv_AllowedDiffCount is None or pv_AllowedDiffCount == "":
            allowed_diff_count = 0  # Default value
        else:
            allowed_diff_count = int(pv_AllowedDiffCount)
        # Convert IfDifferent and IfSame to internal types, Ignore will convert to None, which is OK
        pv_IfDifferent = self.get_parameter_value('IfDifferent')
        if pv_IfDifferent is None or pv_IfDifferent == "":
            pv_IfDifferent = "Ignore"  # Default value
        pv_IfDifferent_command_status_type = command_status_type.value_of(pv_IfDifferent, True)
        pv_IfSame = self.get_parameter_value('IfSame')
        if pv_IfSame is None or pv_IfSame == "":
            pv_IfSame = "Ignore"  # Default value
        pv_IfSame_command_status_type = command_status_type.value_of(pv_IfSame, True)

        # Runtime checks on input

        pv_InputFile1_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_InputFile1, self)))
        pv_InputFile2_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_InputFile2, self)))

        if warning_count > 0:
            message = "There were " + warning_count + " warnings about command parameters."
            logger.warning(message)
            raise ValueError(message)

        # Do the processing

        diff_count = 0
        line_count_compared = 0
        try:
            input_count = 2
            if not os.path.exists(pv_InputFile1_absolute):
                warning_count += 1
                message = 'The first input file does not exist: "' + pv_InputFile1_absolute + '"'
                self.command_status.add_to_log(
                    command_phase_type.RUN,
                    CommandLogRecord(command_status_type.FAILURE, message,
                                     "Verify that the first input file exists at the time the command is run."))
                logger.warning(message)
                input_count -= 1

            if not os.path.exists(pv_InputFile2_absolute):
                warning_count += 1
                message = 'The second input file does not exist: "' + pv_InputFile2_absolute + '"'
                self.command_status.add_to_log(
                    command_phase_type.RUN,
                    CommandLogRecord(command_status_type.FAILURE, message,
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
                    iline1 = CompareFiles.__read_line(in1, pv_CommentLineChar, pv_IgnoreWhitespace)
                    iline2 = CompareFiles.__read_line(in2, pv_CommentLineChar, pv_IgnoreWhitespace)
                    if iline1 is None and iline2 is None:
                        # Both are done at the same time...
                        break
                    # TODO smalers 2006-04-20 The following needs to handle comments at the end...
                    if iline1 is None and iline2 is not None:
                        # First file is done (second is not) so files are different...
                        diff_count += 1
                        break
                    if iline2 is None and iline1 is not None:
                        # Second file is done (first is not) so files are different...
                        diff_count += 1
                        break
                    line_count_compared += 1
                    if pv_MatchCase:
                        # Compare the lines as is since case-specific
                        if iline1 != iline2:
                            diff_count += 1
                    else:
                        # Compare by ignoring case
                        if iline1.upper() != iline2.upper():
                            diff_count += 1
                    # logger.debug('Compared:\n"' + iline1 + '"\n"' + iline2 + '"\ndiff_count=' + str(diff_count))
                in1.close()
                in2.close()
                if line_count_compared == 0:
                    line_count_compared = 1  # to avoid divide by zero below.
                logger.info("There are " + str(diff_count) + " lines that are different, " +
                            '{:4f}'.format(100.0*float(diff_count)/float(line_count_compared)) +
                            '% (compared ' + str(line_count_compared) + ' lines).')

        except Exception as e:
            warning_count += 1
            message = 'Unexpected error comparing file "' + pv_InputFile1_absolute + '" to "' + \
                      pv_InputFile2_absolute + '"'
            traceback.print_exc(file=sys.stdout)
            logger.exception(message, e)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE, message,
                                 "See the log file for details."))

        if diff_count > allowed_diff_count and \
            ((pv_IfDifferent_command_status_type == command_status_type.WARNING) or
             (pv_IfDifferent_command_status_type == command_status_type.FAILURE)):
            message = "" + str(diff_count) + " lines were different, " + \
                '{:4f}'.format(100.0*float(diff_count)/float(line_count_compared)) + \
                "% (compared " + str(line_count_compared) + " lines)."
            if pv_IfDifferent_command_status_type == command_status_type.WARNING:
                logger.warning(message)
            else:
                logger.error(message)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(pv_IfDifferent_command_status_type,
                                 message, "Check files because difference is not expected."))
            raise RuntimeError(message)
        if diff_count == 0 and \
            ((pv_IfSame_command_status_type == command_status_type.WARNING) or
             (pv_IfSame_command_status_type == command_status_type.FAILURE)):
            message = "No lines were different (the files are the same)."
            if pv_IfDifferent_command_status_type == command_status_type.WARNING:
                logger.warning(message)
            else:
                logger.error(message)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(pv_IfSame_command_status_type,
                                 message, "Check files because match is not expected."))
            raise RuntimeError(message)

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
