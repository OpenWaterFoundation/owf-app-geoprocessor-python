# RunProgram command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validators

import logging
import subprocess


class RunProgram(AbstractCommand):
    """
    The RunProgram command runs a command file.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("CommandLine", type("")),
        CommandParameterMetadata("UseCommandShell", type(""))
    ]

    # Choices for UseCommandShell, used to validate parameter and display in editor
    __choices_UseCommandShell = ["False", "True"]

    def __init__(self):
        """
        Initialize a new instance of the command.
        """
        # AbstractCommand data
        super(RunProgram, self).__init__()
        self.command_name = "RunProgram"
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

        # CommandLine is required, pending other options
        pv_CommandLine = self.get_parameter_value(parameter_name='CommandLine', command_parameters=command_parameters)
        if not validators.validate_string(pv_CommandLine, False, False):
            message = "The CommandLine must be specified."
            recommendation = "Specify the command line."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # UseCommandShell is optional, will default to False at runtime
        pv_UseCommandShell = self.get_parameter_value(parameter_name='UseCommandShell',
                                                      command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_UseCommandShell,
                                                  self.__choices_UseCommandShell, True, True):
            message = "UseCommandShell parameter is invalid."
            recommendation = "Specify the UseCommandShell parameter as blank or one of " + \
                             str(self.__choices_UseCommandShell)
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

    def run_command(self):
        """
        Run the command.  Run a separate command file and save results to the current processor.

        Returns:
            None.

        Raises:
                ValueError: if a runtime input error occurs.
                RuntimeError: if a runtime error occurs.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)
        logger.info('In RunProgram.run_command')

        # Get data for the command
        pv_CommandLine = self.get_parameter_value('CommandLine')
        pv_UseCommandShell = self.get_parameter_value('UseCommandShell')
        use_command_shell = False
        if pv_UseCommandShell is not None and pv_UseCommandShell == 'True':
            use_command_shell = True

        logger.info('Command line before expansion="' + pv_CommandLine + '"')

        # Runtime checks on input

        command_line_expanded = self.command_processor.expand_parameter_value(pv_CommandLine, self)

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings about command parameters."
            logger.warning(message)
            raise ValueError(message)

        # Run the program as a subprocess

        try:
            logger.info('Running command line "' + command_line_expanded + '"')
            # TODO evaluate whether to allow shell=True to be passed (good for flexibility, but a security risk)
            # TODO handle standard input and output
            p = subprocess.Popen(command_line_expanded, shell=use_command_shell)
            # Wait for the process to terminate since need it to be done before other commands do their work
            # with the command output.
            p.wait()
            return_status = p.poll()
            if return_status != 0:
                warning_count += 1
                message = 'Nonzero return status running program "' + command_line_expanded + '"'
                logger.error(message, exc_info=True)
                self.command_status.add_to_log(
                    command_phase_type.RUN,
                    CommandLogRecord(command_status_type.FAILURE, message,
                                     "See the log file for details."))

        except Exception as e:
            warning_count += 1
            message = 'Unexpected error running program "' + command_line_expanded + '"'
            logger.error(message, exc_info=True)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE, message,
                                 "See the log file for details."))

        except:
            warning_count += 1
            message = 'Unexpected error running program "' + command_line_expanded + '"'
            logger.error(message, exc_info=True)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE, message,
                                 "See the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            logger.warning(message)
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
