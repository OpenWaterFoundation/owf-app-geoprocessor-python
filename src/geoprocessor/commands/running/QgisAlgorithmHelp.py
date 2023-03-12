# QgisAlgorithmHelp - command to list and writes QGIS algorithm help
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

from geoprocessor.core.CommandError import CommandError
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validator_util
import geoprocessor.ui.util.qt_util as qt_util

import logging


class QgisAlgorithmHelp(AbstractCommand):
    """
    The QgisAlgorithmHelp command prints QGIS algorithm help.

    See:  https://docs.qgis.org/3.10/en/docs/user_manual/processing/console.html
    """

    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("ListAlgorithms", str),
        CommandParameterMetadata("AlgorithmIDs", str),
        CommandParameterMetadata("OutputFile", str),
        CommandParameterMetadata("ShowHelp", str)
    ]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = (
        "Print QGIS algorithm help.\n"
        "Currently can only print to standard output (console window), not to output file."
    )
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # ListAlgorithms
    __parameter_input_metadata['ListAlgorithms.Description'] = "should algorithms be listed?"
    __parameter_input_metadata['ListAlgorithms.Label'] = "List algorithms?"
    __parameter_input_metadata['ListAlgorithms.Required'] = False
    __parameter_input_metadata['ListAlgorithms.Values'] = ['', 'False', 'True']
    __parameter_input_metadata['ListAlgorithms.Value.Default'] = 'False'
    __parameter_input_metadata['ListAlgorithms.Value.Default.ForEditor'] = ''
    __parameter_input_metadata['ListAlgorithms.Tooltip'] = \
        "Should the list of algorithms be printed?"
    # AlgorithmIDs
    __parameter_input_metadata['AlgorithmIDs.Description'] = "algorithm identifiers"
    __parameter_input_metadata['AlgorithmIDs.Label'] = "Algorithm IDs"
    __parameter_input_metadata['AlgorithmIDs.Required'] = False
    __parameter_input_metadata['AlgorithmIDs.Tooltip'] = \
        "List of comma-separated algorithm identifiers, from the algorithm list (e.g., 'gdal:aspect')."
    # OutputFile
    __parameter_input_metadata['OutputFile.Description'] = "output file to write (IGNORED)"
    __parameter_input_metadata['OutputFile.Label'] = "Output file (IGNORED)"
    __parameter_input_metadata['OutputFile.Required'] = False
    __parameter_input_metadata['OutputFile.Tooltip'] = \
        "The output file (relative or absolute path).  ${Property} syntax is recognized.  CURRENTLY NOT ENABLED."
    __parameter_input_metadata['OutputFile.FileSelector.Type'] = "Write"
    __parameter_input_metadata['OutputFile.FileSelector.Title'] = "Select output file to write"
    __parameter_input_metadata['OutputFile.FileSelector.Filters'] = \
        ["Text file (*.txt)", "All files (*.*)"]
    # ShowHelp
    __parameter_input_metadata['ShowHelp.Description'] = "show help in a window?"
    __parameter_input_metadata['ShowHelp.Label'] = "Show help?"
    __parameter_input_metadata['ShowHelp.Tooltip'] = \
        "Show the algorithm help in a user interface (UI) window?  Currently limited because can't capture output."
    __parameter_input_metadata['ShowHelp.Values'] = ["", "False", "True"]
    __parameter_input_metadata['ShowHelp.Value.Default'] = "True"

    def __init__(self) -> None:
        """
        Initialize a command instance.
        """
        # AbstractCommand data.
        super().__init__()
        self.command_name = "QgisAlgorithmHelp"
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

        # Check that the optional parameter ListAlgorithms is a valid Boolean.
        # noinspection PyPep8Naming
        pv_ListAlgorithms = self.get_parameter_value(parameter_name="ListAlgorithms",
                                                     command_parameters=command_parameters)
        if not validator_util.validate_bool(pv_ListAlgorithms, True, False):
            message = "ListAlgorithms is not a valid boolean value."
            recommendation = "Specify a valid boolean value for the ListAlgorithms parameter."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional IfGeoLayerIDExists param is either `Replace`, `Warn`, `Fail`, `ReplaceAndWarn` or None.
        # noinspection PyPep8Naming
        pv_ShowHelp = self.get_parameter_value(parameter_name="ShowHelp", command_parameters=command_parameters)
        if not validator_util.validate_bool(pv_ShowHelp, True, False):
            message = "ShowHelp is not a valid boolean value."
            recommendation = "Specify a valid boolean value for the ShowHelp parameter."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            # Message.printWarning ( warning_level,
            #    MessageUtil.formatMessageTag(command_tag, warning_level), routine, warning );
            logger.warning(warning_message)
            raise CommandParameterError(warning_message)

        # Refresh the phase severity.
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, output_file_abs):
        """
        Checks the following:
        * if specified, the output folder is a valid folder

        Args:
            output_file_abs: the full pathname to the output file, can be None

        Returns:
            Boolean. If TRUE, the GeoLayer should be written. If FALSE, at least one check failed and the GeoLayer
               should not be written.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests.
        # If TRUE, the test confirms that the command should be run.
        should_run_command = list()

        # If the folder of the OutputFile file path is not a valid folder, raise a FAILURE.
        if output_file_abs is not None:
            should_run_command.append(validator_util.run_check(self, "DoesFilePathHaveAValidFolder", "OutputFile",
                                                               output_file_abs, "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command.  List QGIS algorithm help.

        Returns:
            None

        Raises:
            RuntimeError if there is any exception running the command.
        """
        warning_count = 0
        logger = logging.getLogger(__name__)

        # noinspection PyPep8Naming
        pv_ListAlgorithms = self.get_parameter_value('ListAlgorithms')
        list_algorithms = False
        if pv_ListAlgorithms is not None and string_util.is_bool(pv_ListAlgorithms):
            list_algorithms = bool(pv_ListAlgorithms)
        # noinspection PyPep8Naming
        pv_AlgorithmIDs = self.get_parameter_value('AlgorithmIDs')
        algorithm_ids = []
        if pv_AlgorithmIDs is not None and pv_AlgorithmIDs != "":
            # Have algorithm IDs to print help.
            algorithm_ids = pv_AlgorithmIDs.split(",")
            for i in range(len(algorithm_ids)):
                algorithm_ids[i] = algorithm_ids[i].strip()
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value('OutputFile')
        # noinspection PyPep8Naming
        pv_ShowHelp = self.get_parameter_value('ShowHelp')
        show_help = True  # Default
        if pv_ShowHelp is not None and string_util.is_bool(pv_ShowHelp):
            if pv_ShowHelp.upper() == 'FALSE':
                show_help = False

        # Convert the OutputFile parameter value relative path to an absolute path and expand for ${Property} syntax.
        output_file_absolute = None
        if pv_OutputFile is not None:
            output_file_absolute = io_util.verify_path_for_os(
                io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                         self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        # noinspection PyBroadException
        try:
            # Run the checks on the parameter values. Only continue if the checks passed.
            if self.check_runtime_data(output_file_absolute):
                output_list = qgis_util.write_algorithm_help(output_file=output_file_absolute,
                                                             list_algorithms=list_algorithms,
                                                             algorithm_ids=algorithm_ids)

                if show_help:
                    qt_util.info_message_box(output_list, title="QGIS Algorithm Help")

            # Save the output file in the processor, used by the UI to list output files.
            self.command_processor.add_output_file(output_file_absolute)
        except Exception:
            warning_count += 1
            message = 'Unexpected error writing QGIS algorithm help.'
            logger.warning(message, exc_info=True)
            self.command_status.add_to_log(
                CommandPhaseType.RUN,
                CommandLogRecord(CommandStatusType.FAILURE, message,
                                 "Check the log file for details."))

        if warning_count > 0:
            message = "There were " + str(warning_count) + " warnings processing the command."
            raise CommandError(message)

        self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
