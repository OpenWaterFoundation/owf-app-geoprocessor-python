# CreateRegressionTestCommandFile command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.io as io_util
import geoprocessor.util.validators as validators

import os

class CreateRegressionTestCommandFile(AbstractCommand):
    """
    The CreateRegressionTestCommandFile examines a folder tree and creates a command
    file with RunCommand commands for all GeoProcessor command files to run.
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
        warning = ""
        # TODO smalers 2017-12-25 need to log the warnings
        pv_SearchFolder = self.get_parameter_value(parameter_name='SearchFolder',command_parameters=command_parameters)
        if not validators.validate_string(pv_SearchFolder,False,False):
            message = "SearchFolder parameter has no value."
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify the search folder."))
            print(message)
        pv_OutputFile = self.get_parameter_value(parameter_name='OutputFile',command_parameters=command_parameters)
        if not validators.validate_string(pv_OutputFile,False,False):
            message = "OutputFile parameter has no value."
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify the output file."))
            print(message)

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = command_util.validate_command_parameter_names ( self, warning )

        # If any warnings were generated, throw an exception
        if len(warning) > 0:
            #Message.printWarning ( warning_level,
            #    MessageUtil.formatMessageTag(command_tag, warning_level), routine, warning )
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION,command_status_type.SUCCESS)

    def run_command(self):
        """
        Run the command.

        Returns:
            Nothing.

        Raises:
                ValueError: if a runtime input error occurs.
        """
        warning_count = 0

        # Get data for the command
        pv_SearchFolder = self.get_parameter_value('SearchFolder')
        pv_SearchFolder_expanded = self.command_processor.expand_parameter_value(pv_SearchFolder)
        pv_FilenamePattern = self.get_parameter_value('FilenamePattern')
        if pv_FilenamePattern == None or pv_FilenamePattern == "":
            # The pattern that is desired is Test_*.gp
            pv_FilenamePattern = "[Tt][Ee][Ss][Tt]*.gp"
        pv_OutputFile = self.get_parameter_value('OutputFile')
        pv_OutputFile_expanded = self.command_processor.expand_parameter_value(pv_OutputFile)

        # Runtime checks on input

        search_folder_full = io_util.verify_path_for_os(
            os.path.abspath(self.command_processor.get_property('WorkingDir'),
                self.command_processor.expand_parameter_value(self, pv_SearchFolder)))
        output_file_full = io_util.verify_path_for_os(
            os.path.abspath(self.command_processor.get_property('WorkingDir'),
                self.command_processor.expand_parameter_value(self, pv_OutputFile)))

        if not os.path.exists(search_folder_full):
            message = 'The folder to search "' + search_folder_full + '" does not exist.'
            #Message.printWarning ( warning_level,
            #    MessageUtil.formatMessageTag(command_tag, ++warning_count), routine, message )
            self.command_status.addToLog(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                message, "Verify that the folder exists at the time the command is run."))

        if warning_count > 0:
            message = "There were " + warning_count + " warnings about command parameters."
            #Message.printWarning ( warning_level,
            #    MessageUtil.formatMessageTag(command_tag, ++warning_count),
            #    routine, message )
            raise ValueError ( message )

        # Do the processing

        try:
            pass
        except:
            message = 'Unexpected error creating regression test command file "' + output_file_full# + '" (' + e + ')."
            #Message.printWarning(warning_level,
            #    MessageUtil.formatMessageTag(command_tag, ++warning_count), routine, message)
            #Message.printWarning(3, routine, e)
            self.command_status.add_to_log(command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE,
                    message, "See the log file for details."))
            raise RuntimeError(message)
