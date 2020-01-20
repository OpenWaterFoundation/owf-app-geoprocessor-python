# RunGdalProgram - command to run a program
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
import geoprocessor.util.log_util as log_util
import geoprocessor.util.os_util as os_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import logging
import os
import shlex
import subprocess


class RunGdalProgram(AbstractCommand):
    """
    The RunGdalProgram command runs a gdal* program.
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GdalProgram", str),
        CommandParameterMetadata("CommandLine", str),
        CommandParameterMetadata("UseCommandShell", str),
        CommandParameterMetadata("IncludeParentEnvVars", str),
        CommandParameterMetadata("IncludeEnvVars", str),
        CommandParameterMetadata("Timeout", int),
        CommandParameterMetadata("OutputFiles", str),
        CommandParameterMetadata("StdoutFile", str),
        CommandParameterMetadata("StderrFile", str)
    ]

    # Choices for UseCommandShell, used to validate parameter and display in editor
    # See: https://gdal.org/programs/index.html
    __choices_GdalProgram = [
        "gdaladdo",
        "gdalbuildvrt",
        "gdal_calc.py",
        "gdalcompare",
        "gdal-config",
        "gdal_contour",
        "gdaldem",
        "gdal_edit",
        "gdal_fillnodata",
        "gdal_grid",
        "gdalinfo",
        "gdallocationinfo",
        "gdalmanage",
        "gdalmdiminfo",
        "gdalmdimtranslate",
        "gdal_merge",
        "gdalmove",
        "gdal_pansharpen.py",
        "gdal_polygonize",
        "gdal_proximity",
        "gdal_rasterize",
        "gdal_retile",
        "gdal_sieve",
        "gdalsrsinfo",
        "gdaltindex",
        "gdaltransform",
        "gdal_translate",
        "gdal_viewshed",
        "gdalwarp",
        "gdal2tiles",
        "nearblack",
        "pct2rgb",
        "rgb2pct",
    ]

    # Description for each program
    # See: https://gdal.org/programs/index.html
    __gdal_program_description = {
        "gdaladdo": "Builds or rebuilds overview images.",
        "gdalbuildvrt": "Builds a VRT from a list of datasets.",
        "gdal_calc.py": "Command line raster calculator with numpy syntax.",
        "gdalcompare": "Compare two images.",
        "gdal-config": "Determines various information about a GDAL installation.",
        "gdal_contour": "Builds vector contour lines from a raster elevation model.",
        "gdaldem": "Tools to analyze and visualize DEMs.",
        "gdal_edit": "Edit in place various information of an existing GDAL dataset.",
        "gdal_fillnodata": "Fill raster regions by interpolation from edges.",
        "gdal_grid": "Creates regular grid from the scattered data.",
        "gdalinfo": "Lists information about a raster dataset.",
        "gdallocationinfo": "Raster query tool.",
        "gdalmanage": "Identify, delete, rename and copy raster data files.",
        "gdalmdiminfo": "Reports structure and content of a multidimensional dataset.",
        "gdalmdimtranslate": "Converts multidimensional data between different formats, and perform subsetting.",
        "gdal_merge": "Mosaics a set of images.",
        "gdalmove": "Transform georeferencing of raster file in place.",
        "gdal_pansharpen.py": "Perform a pansharpen operation.",
        "gdal_polygonize": "Produces a polygon feature layer from a raster.",
        "gdal_proximity": "Produces a raster proximity map.",
        "gdal_rasterize": "Burns vector geometries into a raster.",
        "gdal_retile": "Retiles a set of tiles and/or build tiled pyramid levels.",
        "gdal_sieve": "Removes small raster polygons.",
        "gdalsrsinfo": "Lists info about a given SRS in number of formats (WKT, PROJ.4, etc.)",
        "gdaltindex": "Builds a shapefile as a raster tileindex.",
        "gdaltransform": "Transforms coordinates.",
        "gdal_translate": "Converts raster data between different formats.",
        "gdal_viewshed": "Compute a visibility mask for a raster.",
        "gdalwarp": "Image reprojection and warping utility.",
        "gdal2tiles": "Generates directory with TMS tiles, KMLs and simple web viewers.",
        "nearblack": "Convert nearly black/white borders to black.",
        "pct2rgb": "Convert an 8bit paletted image to 24bit RGB.",
        "rgb2pct": "Convert a 24bit RGB image to 8bit paletted.",
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
        self.command_name = "RunGdalProgram"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = (
            "Run a GDAL program to process a raster data file, given the program arguments.\n"
            "For portable command files, specify the GDAL program to run using ${GdalBinDir} property or similar.\n"
            "If ${ is not found at the start of the command line, ${GdalBinDir} is automatically inserted.")
        self.command_metadata['EditorType'] = "Simple"

        # Parameter metadata
        self.parameter_input_metadata = dict()

        # GDAL program
        self.parameter_input_metadata['GdalProgram.Description'] = "GDAL program to run"
        self.parameter_input_metadata['GdalProgram.Label'] = "GDAL program"
        self.parameter_input_metadata['GdalProgram.Tooltip'] = "GDAL program to run."
        self.parameter_input_metadata['GdalProgram.Values'] = RunGdalProgram.__choices_GdalProgram
        self.parameter_input_metadata['GdalProgram.Values.Default'] = RunGdalProgram.__choices_GdalProgram[0]
        self.parameter_input_metadata['GdalProgram.Required'] = True

        # CommandLine
        self.parameter_input_metadata['CommandLine.Description'] = "command line"
        self.parameter_input_metadata['CommandLine.Label'] = "Command line"
        self.parameter_input_metadata['CommandLine.Tooltip'] = "Full command line, separated by spaces."
        self.parameter_input_metadata['CommandLine.Required'] = True

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

        # Timeout
        self.parameter_input_metadata['Timeout.Description'] = ""
        self.parameter_input_metadata['Timeout.Label'] = 'Timeout (seconds)'
        self.parameter_input_metadata['Timeout.Default'] = "0"
        self.parameter_input_metadata['Timeout.Tooltip'] = (
            "Timeout for process (seconds), after which the process will be killed.")

        # OutputFiles
        self.parameter_input_metadata['OutputFiles.Description'] = ""
        self.parameter_input_metadata['OutputFiles.Label'] = "Output files"
        self.parameter_input_metadata['OutputFiles.Tooltip'] = (
            "Specify the output files to add to Results, separated by commas.  Can specify with ${Property}.")

        # StdoutFile
        self.parameter_input_metadata['StdoutFile.Description'] = "standard output file"
        self.parameter_input_metadata['StdoutFile.Label'] = "Standard output file"
        self.parameter_input_metadata['StdoutFile.Tooltip'] = (
            "Name of file for program standard output, or 'logfile' to write to the log file.  "
            "${Property} syntax is recognized.")
        self.parameter_input_metadata['StdoutFile.FileSelector.Type'] = "Write"
        self.parameter_input_metadata['StdoutFile.FileSelector.Title'] = "Select a file to write standard output"

        # StderrFile
        self.parameter_input_metadata['StderrFile.Description'] = "standard error file"
        self.parameter_input_metadata['StderrFile.Label'] = "Standard error file"
        self.parameter_input_metadata['StderrFile.Tooltip'] = (
            "Name of file for program standard error, or 'logfile' to write to the log file.  "
            "${Property} syntax is recognized.")
        self.parameter_input_metadata['StderrFile.Required'] = False
        self.parameter_input_metadata['StderrFile.FileSelector.Type'] = "Write"
        self.parameter_input_metadata['StderrFile.FileSelector.Title'] = "Select a file to write standard error"

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
        logger.info('In RunGdalProgram.run_command')

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
        pv_Timeout = self.get_parameter_value('Timeout')
        timeout = None  # handled by subprocess.run()
        if pv_Timeout is not None and pv_Timeout != "":
            # Have specified environment variables to exclude
            timeout = int(pv_Timeout)

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

        # noinspection PyPep8Naming
        pv_StdoutFile = self.get_parameter_value('StdoutFile')
        stdout_file_full = pv_StdoutFile
        if pv_StdoutFile is not None and pv_StdoutFile != "":
            # Have specified stdout file to use for stdout
            stdout_file_full = io_util.verify_path_for_os(
                io_util.to_absolute_path(
                    self.command_processor.get_property('WorkingDir'),
                    self.command_processor.expand_parameter_value(pv_StdoutFile, self)))
        else:
            # Make sure it is None if an empty string was specified
            # noinspection PyPep8Naming
            pv_StdoutFile = None

        # noinspection PyPep8Naming
        pv_StderrFile = self.get_parameter_value('StderrFile')
        stderr_file_full = pv_StderrFile
        if pv_StderrFile is not None and pv_StderrFile != "":
            # Have specified stderr file to use for stdout
            stderr_file_full = io_util.verify_path_for_os(
                io_util.to_absolute_path(
                    self.command_processor.get_property('WorkingDir'),
                    self.command_processor.expand_parameter_value(pv_StderrFile, self)))
        else:
            # Make sure it is None if an empty string was specified
            # noinspection PyPep8Naming
            pv_StderrFile = None

        logger.info('Command line before expansion="' + pv_CommandLine + '"')

        # Runtime checks on input

        # TODO smalers 2020-01-18 determine if 'GdalProgram' is found in the ${GdalBinDir} folder
        # - for now put in some logic to avoid warning about non-use of the variable
        if pv_GdalProgram is None:
            pass

        # Expand the command line
        if not pv_CommandLine.startswith("${"):
            # Make sure that the execable location has the full path
            # noinspection PyPep8Naming
            pv_CommandLine = "${GdalBinDir}/" + pv_CommandLine
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
            env_dict = RunGdalProgram.create_env_dict(include_parent_env_vars, include_env_vars_dict,
                                                      exclude_env_vars_list)
            # print("env_dict=" + string_util.format_dict(env_dict))
            # TODO smalers 2018-12-16 evaluate using shlex.quote() to handle command string
            # TODO smalers 2018-12-16 handle standard input and output
            use_run = False
            return_status = -1
            if use_run:
                # Use subprocess.run(), available as of Python 3.5
                # - shlex is used to parse command line string into arguments.
                # - For the following logic, 'capture_output' is not used because output is immediately redirected
                #   to the appropriate location.  'capture_output' is used ot retrieve output from
                #   subprocess.CompletedProcess.
                args = shlex.split(command_line_expanded)
                # By default the stdout and stderr are just output by the subprocess defaults.
                # However, the output can be redirected to a file.
                # If either stdout our stderr is to be captured, use the 'capture_output' parameter.
                capture_output = None  # Do not capture output because stderr and stdout are being specified
                stderr = None  # Default is don't capture stderr
                stdout = None  # Default is don't capture stdout
                stdout_file = None
                stderr_file = None

                # Handle stdout parameters
                if pv_StdoutFile is not None:
                    capture_output = True
                    if pv_StdoutFile == 'logfile':
                        # Get the file number of the current log file
                        logfile_handler: logging.FileHandler = log_util.get_logfile_handler()
                        if logfile_handler is not None:
                            stdout = logfile_handler.stream.fileno()
                    elif pv_StdoutFile == 'DEVNULL':
                        # Special value that should be passed as is
                        # - will write standard output to /dev/null on Linux
                        stdout = 'DEVNULL'
                    else:
                        # Open the file to receive stdout output, perhaps the desired output of the program if it
                        # does not create its own output file
                        stdout_file = open(stdout_file_full)
                        stderr = stdout_file.fileno()

                # Handle stderr parameters
                if pv_StderrFile is not None:
                    if pv_StderrFile == 'logfile':
                        # Get the file number of the current log file
                        logfile_handler: logging.FileHandler = log_util.get_logfile_handler()
                        if logfile_handler is not None:
                            stderr = logfile_handler.stream.fileno()
                    elif pv_StderrFile == 'DEVNULL' or pv_StderrFile == 'STDOUT':
                        # Special value that should be passed as is
                        # - will write standard output to /dev/null on Linux
                        stderr = pv_StderrFile
                    else:
                        # Open the file to receive stderr output, for example to isolate errors to a file
                        stderr_file = open(stderr_file_full)
                        stderr = stderr_file.fileno()
                # Now run the process
                completed_process = subprocess.run(args, shell=use_command_shell, env=env_dict, timeout=timeout,
                                                   capture_output=capture_output, stdout=stdout, stderr=stderr)

                # Get the return information
                # - note that capture_output=None above so stdout and stderr cannot be returned from CompletedProcess
                return_status = completed_process.returncode

                # Close any files that may have been opened
                # - this does not close the log file, which should remain open for other logging messages
                if stdout_file is not None:
                    stdout_file.close()
                if stderr_file is not None:
                    stderr_file.close()
            else:
                # Older logic that will be phased out if the above 'run()' logic works
                # Use subprocess.Popen
                p = subprocess.Popen(command_line_expanded, shell=use_command_shell, env=env_dict)
                # Wait for the process to terminate since need it to be done before other commands do their work
                # with the command output.
                p.wait()
                return_status = p.poll()
                # Wait for the process to terminate since need it to be done before other commands do their work

            if return_status == 0:
                logger.info("Return status of " + str(return_status) + " running program.")
            else:
                warning_count += 1
                message = 'Nonzero return status (' + str(return_status) + ' running program "' + \
                          command_line_expanded + '"'
                logger.warning(message, exc_info=True)
                self.command_status.add_to_log(
                    CommandPhaseType.RUN,
                    CommandLogRecord(CommandStatusType.FAILURE, message,
                                     "See the log file for details."))

        except Exception:
            warning_count += 1
            message = 'Unexpected error running GDAL program "' + command_line_expanded + '"'
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
