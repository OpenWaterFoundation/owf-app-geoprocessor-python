# RunOgrProgram - command to run an OGR program
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
import geoprocessor.util.os_util as os_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import logging
import os
import subprocess


class RunOgrProgram(AbstractCommand):
    """
    The RunOgrProgram command runs a ogr* program.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("OgrProgram", type("")),
        CommandParameterMetadata("CommandArguments", type("")),
        CommandParameterMetadata("UseCommandShell", type("")),
        CommandParameterMetadata("IncludeParentEnvVars", type("")),
        CommandParameterMetadata("IncludeEnvVars", type("")),
        CommandParameterMetadata("OutputFiles", type(""))
    ]

    # Choices for OgrProgram, used to validate parameter and display in editor
    # See: https://gdal.org/programs/index.html
    __choices_OgrProgram = [
        "ogrinfo"
        "ogrlineref",
        "ogrmerge",
        "ogrtindex",
        "ogr2ogr"
    ]

    # Description for each program
    # See: https://gdal.org/programs/index.html
    __ogr_program_description = {
        "ogrinfo": "Lists information about an OGR-supported data source.",
        "ogrlineref": "Create linear reference and provide some calculations using it.",
        "ogrmerge": "Merge several vector datasets into a single one.",
        "ogrtindex": "Creates a tileindex.",
        "ogr2ogr": "Converts simple features data between file formats."
    }

    # Choices for UseCommandShell, used to validate parameter and display in editor
    __choices_UseCommandShell = ["False", "True"]

    # Choices for IncludeParentEnvVars, used to validate parameter and display in editor
    __choices_IncludeParentEnvVars = ["False", "True"]

    # Choices for IncludeEnvVars, used to validate parameter and display in editor
    __choices_IncludeEnvVars = ["False", "True"]

    def __init__(self) -> None:
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data
        super().__init__()
        self.command_name = "RunGdal"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = (
            "Run an ogr* program to process a vector spatial data file, given the program arguments.")
        self.command_metadata['EditorType'] = "Simple"

        # Parameter metadata
        self.parameter_input_metadata = dict()
        # GDAL program
        self.parameter_input_metadata['OgrProgram.Description'] = "OGR program to run."
        self.parameter_input_metadata['OgrProgram.Label'] = "OGR program"
        self.parameter_input_metadata['OgrProgram.Tooltip'] = "OGR program to run."
        self.parameter_input_metadata['OgrProgram.Required'] = True
        # CommandLine
        self.parameter_input_metadata['CommandArguments.Description'] = "Command line arguments."
        self.parameter_input_metadata['CommandArguments.Label'] = "Command arguments"
        self.parameter_input_metadata['CommandArguments.Tooltip'] = "Command arguments, separated by spaces."
        self.parameter_input_metadata['CommandArguments.Required'] = True
        # UseCommandShell
        self.parameter_input_metadata['UseCommandShell.Description'] = "use command shell"
        self.parameter_input_metadata['UseCommandShell.Label'] = "Use command shell?"
        self.parameter_input_metadata['UseCommandShell.Tooltip'] = ""
        self.parameter_input_metadata['UseCommandShell.Values'] = ["", "False", "True"]
        self.parameter_input_metadata['UseCommandShell.Value.Default'] = "False"
        # IncludeParentEnvVars
        self.parameter_input_metadata['IncludeParentEnvVars.Description'] = ""
        self.parameter_input_metadata['IncludeParentEnvVars.Label'] = "Include parent environment variables"
        self.parameter_input_metadata['IncludeParentEnvVars.Tooltip'] = (
            "Indicate whether the parent environment variables should be passed to the program run environment.")
        self.parameter_input_metadata['IncludeParentEnvVars.Values'] = ["", "True", "False"]
        self.parameter_input_metadata['IncludeParentEnvVars.Value.Default'] = "True"
        # IncludeEnvVars
        self.parameter_input_metadata['IncludeEnvVars.Description'] = ""
        self.parameter_input_metadata['IncludeEnvVars.Label'] = "Include environment variables"
        self.parameter_input_metadata['IncludeEnvVars.Tooltip'] = (
            "Specify environment variables to be defined for the program run environment in format:"
            "VAR1=Value1,VAR2=Value2.")
        # ExcludeEnvVars
        self.parameter_input_metadata['ExcludeEnvVars.Description'] = ""
        self.parameter_input_metadata['ExcludeEnvVars.Label'] = 'Exclude environment variables'
        self.parameter_input_metadata['ExcludeEnvVars.Tooltip'] = (
            "Specify environment variables to be removed from the program run environment, separated by commas.")
        # OutputFiles
        self.parameter_input_metadata['OutputFiles.Description'] = ""
        self.parameter_input_metadata['OutputFiles.Label'] = "Output files"
        self.parameter_input_metadata['OutputFiles.Tooltip'] = (
            "Specify the output files, separated by commas.  Can specify with ${Property}.")

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

        # CommandLine is required, pending other options
        # noinspection PyPep8Naming
        pv_CommandLine = self.get_parameter_value(parameter_name='CommandLine', command_parameters=command_parameters)
        if not validator_util.validate_string(pv_CommandLine, False, False):
            message = "The CommandLine must be specified."
            recommendation = "Specify the command line."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # IncludeParentEnvVars is optional, will default to True at runtime
        # noinspection PyPep8Naming
        pv_IncludeParentEnvVars = self.get_parameter_value(parameter_name='IncludeParentEnvVars',
                                                           command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_IncludeParentEnvVars,
                                                      self.__choices_IncludeParentEnvVars, True, True):
            message = "IncludeParentEnvVars parameter is invalid."
            recommendation = "Specify the IncludeParentEnvVars parameter as blank or one of " + \
                             str(self.__choices_IncludeParentEnvVars)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # UseCommandShell is optional, will default to False at runtime
        # noinspection PyPep8Naming
        pv_UseCommandShell = self.get_parameter_value(parameter_name='UseCommandShell',
                                                      command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_UseCommandShell,
                                                      self.__choices_UseCommandShell, True, True):
            message = "UseCommandShell parameter is invalid."
            recommendation = "Specify the UseCommandShell parameter as blank or one of " + \
                             str(self.__choices_UseCommandShell)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # TODO smalers 2018-12-16 need to make sure IncludeEnvVars and ExcludeEnvVars are valid lists
        # - for now allow any string to be specified

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
    def create_env_dict(cls, include_parent_env_vars: bool, include_env_vars_dict: dict,
                        exclude_env_vars_list: [str]) -> dict or None:
        """
        Create the environment variable dictionary for the called program.

        Args:
            include_parent_env_vars:  If True, include the parent environment variables.
                If include_env_vars and exclude_env_vars are None, return None since None
                will cause the parent environment to be passed by default.
                If include_env_vars or exclude_env_vars are not None, copy the parent environment variables
                and then modify as per include_env_vars and exclude_env_vars.
            include_env_vars_dict:  A dictionary of environment variables to include in the environment.
                Any variables found in the environment variable list will be reset to the given value.
            exclude_env_vars_list:  A list of environment variables to not include in the environment.
                Variables will be removed from the returned dictionary.

        Returns:  A dictionary of environment variables to use when calling the program, or None to
            default to the entire parent environment.
        """
        if include_env_vars_dict is not None or exclude_env_vars_list is not None:
            # Need to process the dictionary specifically
            env_dict = {}
            # First, if the parent environment variables are to be used, create a dictionary that has
            # a copy of all parent environment variables.
            if include_parent_env_vars:
                for key, value in os.environ.items():
                    env_dict[key] = value
            # Add the environment variables to be included.
            if include_env_vars_dict is not None:
                for key, value in include_env_vars_dict.items():
                    env_dict[key] = value
            # Remove the environment variables to be excluded.
            if exclude_env_vars_list is not None:
                for key in exclude_env_vars_list:
                    try:
                        del env_dict[key]
                    except KeyError:
                        # OK to ignore because may not exist in the dictionary
                        pass
            # Return the environment variable dictionary
            return env_dict
        else:
            # No granular handling of environment variables occurs
            if include_parent_env_vars:
                # All of the parent environment variables should be used
                # - return None since the default is to use the parent environment
                return None
            else:
                # Don't want the parent environment to be visible to called program.
                # - because None would return the default, create an empty dictionary
                # - also add SystemRoot as per Python documentation, to find DLLs.
                env_dict = {}
                if os_util.is_windows_os():
                    env_dict['SystemRoot'] = os.environ['SystemRoot']
                return env_dict

    def run_command(self) -> None:
        """
        Run the command.  Run the program, which can generate output files.

        Returns:
            None.

        Raises:
                ValueError: if a runtime input error occurs.
                RuntimeError: if a runtime error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)
        logger.info('In RunOgrProgram.run_command')

        # Get data for the command
        print("command parameters=" + string_util.format_dict(self.command_parameters))
        # noinspection PyPep8Naming
        pv_GdalProgram = self.get_parameter_value('GdalProgram')
        # noinspection PyPep8Naming
        pv_CommandLine = self.get_parameter_value('CommandLine')
        # noinspection PyPep8Naming
        pv_UseCommandShell = self.get_parameter_value('UseCommandShell')
        use_command_shell = False  # Default
        if pv_UseCommandShell is not None and pv_UseCommandShell == 'True':
            use_command_shell = True
        # noinspection PyPep8Naming
        pv_IncludeParentEnvVars = self.get_parameter_value('IncludeParentEnvVars')
        include_parent_env_vars = True  # Default
        if pv_IncludeParentEnvVars is not None and pv_IncludeParentEnvVars == 'False':
            include_parent_env_vars = False
        # noinspection PyPep8Naming
        pv_IncludeEnvVars = self.get_parameter_value('IncludeEnvVars')
        include_env_vars_dict = None
        if pv_IncludeEnvVars is not None and pv_IncludeEnvVars != "":
            # Have specified environment variables to include
            # - expand the environment variable value using processor properties
            include_env_vars_dict = string_util.delimited_string_to_dictionary_one_value(pv_IncludeEnvVars,
                                                                                         key_value_delimiter="=",
                                                                                         trim=True)
            for key, value in include_env_vars_dict.items():
                include_env_vars_dict[key] = self.command_processor.expand_parameter_value(value, self)

        # noinspection PyPep8Naming
        pv_ExcludeEnvVars = self.get_parameter_value('ExcludeEnvVars')
        exclude_env_vars_list = None
        if pv_ExcludeEnvVars is not None and pv_ExcludeEnvVars != "":
            # Have specified environment variables to exclude
            exclude_env_vars_list = string_util.delimited_string_to_list(pv_ExcludeEnvVars, trim=True)

        # noinspection PyPep8Naming
        pv_OutputFiles = self.get_parameter_value('OutputFiles')
        output_files_list = None
        if pv_OutputFiles is not None and pv_OutputFiles != "":
            # Have specified output files to add to command output files
            output_files_list = string_util.delimited_string_to_list(pv_OutputFiles, trim=True)
            # Expand each output file
            ifile = -1
            for output_file in output_files_list:
                ifile = ifile + 1
                output_files_list[ifile] = io_util.verify_path_for_os(
                    io_util.to_absolute_path(
                        self.command_processor.get_property('WorkingDir'),
                        self.command_processor.expand_parameter_value(output_file, self)))

        logger.info('Command line before expansion="' + pv_CommandLine + '"')

        # Runtime checks on input

        command_line_expanded = self.command_processor.expand_parameter_value(pv_CommandLine, self)

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings about command parameters."
            logger.warning(message)
            raise ValueError(message)

        # Run the program as a subprocess

        # noinspection PyBroadException
        try:
            logger.info('Running command line "' + command_line_expanded + '"')
            # Create the environment dictionary
            env_dict = RunOgrProgram.create_env_dict(include_parent_env_vars, include_env_vars_dict, exclude_env_vars_list)
            print("env_dict=" + string_util.format_dict(env_dict))
            # TODO smalers 2018-12-16 evaluate using shlex.quote() to handle command string
            # TODO smalers 2018-12-16 handle standard input and output
            p = subprocess.Popen(command_line_expanded, shell=use_command_shell, env=env_dict)
            # Wait for the process to terminate since need it to be done before other commands do their work
            # with the command output.
            p.wait()
            return_status = p.poll()
            if return_status != 0:
                warning_count += 1
                message = 'Nonzero return status running program "' + command_line_expanded + '"'
                logger.warning(message, exc_info=True)
                self.command_status.add_to_log(
                    CommandPhaseType.RUN,
                    CommandLogRecord(CommandStatusType.FAILURE, message,
                                     "See the log file for details."))

        except Exception:
            warning_count += 1
            message = 'Unexpected error running program "' + command_line_expanded + '"'
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "See the log file for details."))

        # If any output files were indicated, add to the command output if they exist
        if output_files_list is not None and len(output_files_list) > 0:
            for output_file in output_files_list:
                if os.path.isfile(output_file):
                    # Add the log file to output
                    self.command_processor.add_output_file(output_file)

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            logger.warning(message)
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
