# If - command to start an If block
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
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import logging


class If(AbstractCommand):
    """
    The If command starts an If block.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("Name", type("")),
        CommandParameterMetadata("Condition", type("")),
        CommandParameterMetadata("CompareAsStrings", type(True))  # Not yet implemented
    ]

    def __init__(self) -> None:
        """
        Initialize the command instance.
        """
        super().__init__()
        # AbstractCommand data
        self.command_name: str = "If"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = (
            "The If command evaluates a conditional statement and if true will "
            "result in the commands between If and matching EndIf being executed. ")
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # Name
        self.parameter_input_metadata['Name.Description'] = \
            "the name of the If command to be matched with the EndIf command"
        self.parameter_input_metadata['Name.Label'] = "Name"
        self.parameter_input_metadata['Name.Required'] = True
        self.parameter_input_metadata['Name.Tooltip'] = (
            "The name of the If command, which will be matched with the name of an EndIf command to indicate\n"
            "the block of commands in the if condition.")
        # Condition
        self.parameter_input_metadata['Condition.Description'] = "the conditional statement to evaluate"
        self.parameter_input_metadata['Condition.Label'] = "Condition"
        self.parameter_input_metadata['Condition.Required'] = True
        self.parameter_input_metadata['Condition.Tooltip'] = "The conditional statement to evaluate."
        # CompareAsStrings
        self.parameter_input_metadata['CompareAsStrings.Description'] = "boolean"
        self.parameter_input_metadata['CompareAsStrings.Label'] = "Compare As Strings"
        self.parameter_input_metadata['CompareAsStrings.Tooltip'] = (
            "If True, the comparison will be done as strings even if the values could be treated as numbers or "
            "Booleans. ")
        self.parameter_input_metadata['CompareAsStrings.Value.Default'] = "FALSE"

        # Local private data
        self.__condition_eval = True  # The result of evaluating the condition

    def check_command_parameters(self, command_parameters: dict) -> None:
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
        warning = ""
        logger = logging.getLogger(__name__)

        # Unlike most commands, set internal data here because it is needed by initial call to next()
        # before calls to run_command

        # Name is required
        pv_Name = self.get_parameter_value(parameter_name='Name', command_parameters=command_parameters)
        if not validator_util.validate_string(pv_Name, False, False):
            message = "A name for the If block must be specified"
            recommendation = "Specify the Name."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Condition is required
        pv_Condition = self.get_parameter_value(parameter_name='Condition', command_parameters=command_parameters)
        if not validator_util.validate_string(pv_Condition, False, False):
            message = "A condition for the If command must be specified"
            recommendation = "Specify the condition."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception
        if len(warning) > 0:
            logger.warn(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def get_condition_eval(self) -> bool:
        """
        Return the result of evaluating the condition, which is set when run_command() is called.

        Returns:
            Return the result (bool) of evaluating the condition,
            which is set when run_command() is called.
        """
        return self.__condition_eval

    def get_name(self) -> str:
        """
        Return the name of the If (will match name of corresponding EndIf).

        Returns:
            The name of the If (will match name of corresponding EndIf).
        """
        return self.get_parameter_value("Name")

    # The logic of this command closely matches the TSTool If command
    # - could possibly improve but for now implement something basic that works
    def run_command(self) -> None:
        """
        Run the command.  Initializes the If.

        Returns:
            None.
        """
        logger = logging.getLogger(__name__)
        debug = True  # Use for troubleshooting
        warning_count = 0  # General count for issues

        pv_Name = self.get_parameter_value("Name")
        pv_Condition = self.get_parameter_value("Condition")
        condition_upper = None
        if pv_Condition is not None:
            condition_upper = pv_Condition.upper()
        pv_CompareAsStrings = self.get_parameter_value("CompareAsStrings")
        compare_as_strings = False
        if pv_CompareAsStrings is not None and pv_CompareAsStrings.upper == "TRUE":
            compare_as_strings = True
        # TODO smalers 2018-02-18 need to add other special conditions such as empty properties, GeoLayer exists, etc.
        # - see TSTool code

        try:
            condition_eval = False
            self.__condition_eval = condition_eval
            if pv_Condition is not None and pv_Condition != "":
                # Condition is specified, rather than special check.
                # First determine the condition operator.
                # TODO SAM 2013-12-07 Figure out if there is a more elegant way to do this
                #  Currently only Value1 Operator Value2 is allowed.  Brute force split by finding the operator
                logger.info('Evaluating Condition="' + pv_Condition + '"')
                pos1 = -1
                pos2 = -1
                value1 = ""
                value2 = ""
                op = "??"
                if pv_Condition.find("<=") > 0:
                    pos = pv_Condition.find("<=")
                    op = "<="
                    pos1 = pos
                    pos2 = pos + 2
                elif pv_Condition.find("<") > 0:
                    pos = pv_Condition.find("<")
                    op = "<"
                    pos1 = pos
                    pos2 = pos + 1
                elif pv_Condition.find(">=") > 0:
                    pos = pv_Condition.find(">=")
                    op = ">="
                    pos1 = pos
                    pos2 = pos + 2
                elif pv_Condition.find(">") > 0:
                    pos = pv_Condition.find(">")
                    op = ">"
                    pos1 = pos
                    pos2 = pos + 1
                elif pv_Condition.find("==") > 0:
                    pos = pv_Condition.find("==")
                    op = "=="
                    pos1 = pos
                    pos2 = pos + 2
                elif pv_Condition.find("!=") > 0:
                    pos = pv_Condition.find("!=")
                    op = "!="
                    pos1 = pos
                    pos2 = pos + 2
                elif condition_upper.find("!CONTAINS") > 0:
                    # Put this before the next "CONTAINS" operator
                    pos = condition_upper.find("!CONTAINS")
                    op = "!CONTAINS"
                    pos1 = pos
                    pos2 = pos + 9
                    compare_as_strings = True   # "!contains" is only used on strings
                elif condition_upper.find("CONTAINS") > 0:
                    pos = condition_upper.find("CONTAINS")
                    op = "CONTAINS"
                    pos1 = pos
                    pos2 = pos + 8
                    compare_as_strings = True  # "contains" is only used on strings
                elif pv_Condition.find("=") > 0:
                    message = "Bad use of = in condition."
                    recommendation = "Use == to check for equality."
                    logger.warning(message)
                    self.command_status.add_to_log(
                        CommandPhaseType.RUN,
                        CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))
                else:
                    message = 'Unknown condition operator for "' + pv_Condition + '"'
                    recommendation =\
                        "Make sure condition operator is supported - refer to command editor and documentation."
                    logger.warning(message)
                    self.command_status.add_to_log(
                        CommandPhaseType.RUN,
                        CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

                logger.info('operator="' + op + '" pos1=' + str(pos1) + " pos2=" + str(pos2))
                # Now evaluate the left and right sides of the condition
                arg1 = pv_Condition[0:pos1].strip()
                if debug:
                    logger.info('Left side of condition before property expansion check: "' + str(arg1) + '"')
                if arg1.find("${") >= 0:
                    value1 = self.command_processor.expand_parameter_value(arg1, self)
                    if debug:
                        logger.info("Left side of condition after property expansion: " + value1)
                else:
                    value1 = arg1
                    if debug:
                        logger.info("Left side (no expansion needed): " + value1)
                arg2 = pv_Condition[pos2:].strip()
                if debug:
                    logger.info('Right side of condition before property expansion check: "' + str(arg2) + '"')
                if arg2.find("${") >= 0:
                    value2 = self.command_processor.expand_parameter_value(arg2, self)
                    if debug:
                        logger.info("Right side after property expansion: " + value2)
                else:
                    value2 = arg2
                    if debug:
                        logger.info("Right side (no expansion needed): " + value2)
                # If the arguments are quoted, then all of the following will be false
                is_value1_int = string_util.is_int(value1)
                is_value2_int = string_util.is_int(value2)
                is_value1_float = string_util.is_float(value1)
                is_value2_float = string_util.is_float(value2)
                is_value1_bool = string_util.is_bool(value1)
                is_value2_bool = string_util.is_bool(value2)
                # Strip surrounding double quotes for comparisons below - do after above checks for type
                value1 = value1.replace('"', "")
                value2 = value2.replace('"', "")
                if not compare_as_strings and is_value1_int and is_value2_int:
                    # Do an integer comparison
                    ivalue1 = int(value1)
                    ivalue2 = int(value2)
                    if op == "<=":
                        if ivalue1 <= ivalue2:
                            condition_eval = True
                    elif op == "<":
                        if ivalue1 < ivalue2:
                            condition_eval = True
                    elif op == ">=":
                        if ivalue1 >= ivalue2:
                            condition_eval = True
                    elif op == ">":
                        if ivalue1 > ivalue2:
                            condition_eval = True
                    elif op == "==":
                        if ivalue1 == ivalue2:
                            condition_eval = True
                    elif op == "!=":
                        if ivalue1 != ivalue2:
                            condition_eval = True
                elif not compare_as_strings and is_value1_float and is_value2_float:
                    # Compare floats
                    fvalue1 = float(value1)
                    fvalue2 = float(value2)
                    if op == "<=":
                        if fvalue1 <= fvalue2:
                            condition_eval = True
                    elif op == "<":
                        if fvalue1 < fvalue2:
                            condition_eval = True
                    elif op == ">=":
                        if fvalue1 >= fvalue2:
                            condition_eval = True
                    elif op == ">":
                        if fvalue1 > fvalue2:
                            condition_eval = True
                    elif op == "==":
                        if fvalue1 == fvalue2:
                            condition_eval = True
                    elif op == "!=":
                        if fvalue1 != fvalue2:
                            condition_eval = True
                elif not compare_as_strings and is_value1_bool and is_value2_bool:
                    # Do a boolean comparison
                    # - bool("") is False, every other string is True!
                    bvalue1 = string_util.str_to_bool(value1)
                    bvalue2 = string_util.str_to_bool(value2)
                    if debug:
                        logger.info('Evaluating boolean condition "' + str(bvalue1) + " " + op + " " + str(bvalue2))
                    if op == "<=":
                        if not bvalue1:
                            # false <= false or true (does not matter what right side is)
                            condition_eval = True
                    elif op == "<":
                        if not bvalue1 and bvalue2:
                            # false < true
                            condition_eval = True
                    elif op == ">=":
                        if bvalue1:
                            # true >= false or true (does not matter what right side is)
                            condition_eval = True
                    elif op == ">":
                        if bvalue1 and not bvalue2:
                            # true > false
                            condition_eval = True
                    elif op == "==":
                        if bvalue1 == bvalue2:
                            condition_eval = True
                    elif op == "!=":
                        if bvalue1 != bvalue2:
                            condition_eval = True
                elif compare_as_strings or\
                    (not is_value1_int and not is_value2_int and
                     not is_value1_float and not is_value2_float and not is_value1_bool and not is_value2_bool):
                    # Always compare the string values or the input is not other types so assume strings
                    if op == "CONTAINS":
                        if value1.find(value2) >= 0:
                            condition_eval = True
                    elif op == "!CONTAINS":
                        if value1.find(value2) < 0:
                            condition_eval = True
                    else:
                        # Do a comparison of the strings to figure out lexicographically order
                        if value1 < value2:
                            comp = -1
                        elif value1 == value2:
                            comp = 0
                        else:
                            comp = 1
                        if op == "<=":
                            if comp <= 0:
                                condition_eval = True
                        elif op == "<":
                            if comp < 0:
                                condition_eval = True
                        elif op == ">=":
                            if comp >= 0:
                                condition_eval = True
                        elif op == ">":
                            if comp > 0:
                                condition_eval = True
                        elif op == "==":
                            if comp == 0:
                                condition_eval = True
                        elif op == "!=":
                            if comp != 0:
                                condition_eval = True
                else:
                    message = 'Left and right have different type - cannot evaluate condition "' + pv_Condition + '"'
                    recommendation = "Make sure data types on each side of operator are the same - " + \
                        "refer to command editor and documentation."
                    logger.warning(message)
                    self.command_status.add_to_log(
                        CommandPhaseType.RUN,
                        CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

                if debug:
                    logger.info("Condition evaluated to: " + str(condition_eval))

                # For now leave the following two messages in to reinforce to user the evaluation
                # - may only output when in debug mode in the future
                if pv_Condition.find("${") >= 0:
                    # Show the original
                    message = pv_Condition + " (showing ${Property} notation) evaluates to " + str(condition_eval)
                    recommendation = "Informational message."
                    self.command_status.add_to_log(
                        CommandPhaseType.RUN,
                        CommandLogRecord(CommandStatusType.SUCCESS, message, recommendation))

                # Always also show the expanded
                message = str(value1) + " " + op + " " + str(value2) + " evaluates to " + str(condition_eval)
                recommendation = "Informational message."
                self.command_status.add_to_log(
                    CommandPhaseType.RUN,
                    CommandLogRecord(CommandStatusType.SUCCESS, message, recommendation))
                self.__condition_eval = condition_eval

        except Exception:
            warning_count += 1
            message = 'Unexpected error in If, Name="' + pv_Name + '"'
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "Check the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
