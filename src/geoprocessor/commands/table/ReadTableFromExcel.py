# ReadTableFromExcel - command to read a table from an Excel worksheet
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
from geoprocessor.core.Table_pandas import Table

import geoprocessor.util.command_util as command_util
import geoprocessor.util.pandas_util as pandas_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validator_util

import logging


class ReadTableFromExcel(AbstractCommand):
    """
    Reads a Table from an Excel file.

    This command reads a tables from an Excel file and creates a Table object within the geoprocessor.
    The Table can then be accessed in the geoprocessor by its identifier and further processed.

    Command Parameters
    * InputFile (str, required): the relative pathname to the excel data file (known as a workbook)
    * Worksheet (str, optional): the name of the worksheet to read. Default: the first worksheet is read.
    * TableID (str, optional): the Table identifier. Default: the Worksheet's name.
    * IfTableIDExists (str, optional): This parameter determines the action that occurs if the TableID already exists
        within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail` 
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("InputFile", type("")),
        CommandParameterMetadata("Worksheet", type("")),
        CommandParameterMetadata("TableID", type("")),
        CommandParameterMetadata("IfTableIDExists", type(""))]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = "Read a table from an Excel worksheet." \
                                        "This command is under development."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # InputFile
    __parameter_input_metadata['InputFile.Description'] = "Excel file to read"
    __parameter_input_metadata['InputFile.Label'] = "Input file"
    __parameter_input_metadata['InputFile.Required'] = True
    __parameter_input_metadata['InputFile.Tooltip'] = (
        "The Excel workbook file (.xls or .xlsx) with the Excel worksheet to read (relative or absolute path).\n"
        "${Property} syntax is recognized.")
    __parameter_input_metadata['InputFile.FileSelector.Type'] = "Read"
    __parameter_input_metadata['InputFile.FileSelector.Title'] = "Select an Excel file to read"
    __parameter_input_metadata['InputFile.FileSelector.Filters'] = \
        ["Excel file (*.xlsx *.xls)", "All files (*)"]
    # Worksheet
    __parameter_input_metadata['Worksheet.Description'] = "Excel worksheet"
    __parameter_input_metadata['Worksheet.Label'] = "Worksheet"
    __parameter_input_metadata['Worksheet.Tooltip'] = \
        "The name of the Excel worksheet within the Excel workbook to read."
    __parameter_input_metadata['Worksheet.Value.Default'] = "The first worksheet in the Excel workbook."
    # TODO jurentie 01/22/2019 is this a read file?
    # TableID
    __parameter_input_metadata['TableID.Description'] = "output table identifier"
    __parameter_input_metadata['TableID.Label'] = "TableID"
    __parameter_input_metadata['TableID.Tooltip'] = "A Table identifier"
    __parameter_input_metadata['TableID.Value.Default.Description'] = "worksheet name"
    # IfTableIDExists
    __parameter_input_metadata[
        'IfTableIDExists.Description'] = "action if the TableID exists"
    __parameter_input_metadata['IfTableIDExists.Label'] = "If table exists"
    __parameter_input_metadata['IfTableIDExists.Tooltip'] = (
        "The action that occurs if the TableID already exists within the GeoProcessor.\n"
        "Replace : The existing Table within the GeoProcessor is overwritten with the new Table. "
        "No warning is logged.\n"
        "ReplaceAndWarn: The existing Table within the GeoProcessor is overwritten with the new Table. "
        "A warning is logged.\n"
        "Warn : The new Table is not created. A warning is logged.\n"
        "Fail : The new Table is not created. A fail message is logged.")
    __parameter_input_metadata['IfTableIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
    __parameter_input_metadata['IfTableIDExists.Value.Default'] = "Replace"

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data.
        super().__init__()
        self.command_name = "ReadTableFromExcel"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display.
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata.
        self.parameter_input_metadata = self.__parameter_input_metadata

        # Class data.
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns: None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning_message = ""

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

        # Check that optional parameter IfTableIDExists is either `Replace`, `ReplaceAndWarn`, `Warn`, `Fail`, None.
        # noinspection PyPep8Naming
        pv_IfTableIDExists = self.get_parameter_value(parameter_name="IfTableIDExists",
                                                      command_parameters=command_parameters)
        acceptable_values = ["Replace", "ReplaceAndWarn", "Warn", "Fail"]
        if not validator_util.validate_string_in_list(pv_IfTableIDExists, acceptable_values, none_allowed=True,
                                                      empty_string_allowed=True, ignore_case=True):

            message = "IfTableIDExists parameter value ({}) is not recognized.".format(pv_IfTableIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfTableIDExists parameter.".format(
                acceptable_values)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            self.logger.warning(warning_message)
            raise CommandParameterError(warning_message)
        else:
            # Refresh the phase severity.
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, file_abs, sheet_name, table_id):
        """
        Checks the following:
        * the InputFile (absolute) is a valid file
        * the Worksheet is a valid sheet in the Excel workbook
        * the ID of the Table is unique (not an existing Table ID)

        Args:
            file_abs (str): the full pathname to the input data file (Excel workbook)
            sheet_name (str): the name of the Excel worksheet to read
            table_id (str): the ID of the output Table

        Returns:
             Boolean. If TRUE, the GeoLayer should be read. If FALSE, at least one check failed and the GeoLayer
                should not be read.
        """

        # List of Boolean values.
        # The Boolean values correspond to the results of the following tests.
        # If TRUE, the test confirms that the command should be run.
        should_run_command = list()

        # If the input file is not a valid file path, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsFilePathValid", "InputFile", file_abs, "FAIL"))

        # If the input file is valid, continue with the checks.
        if False not in should_run_command:

            # If the Worksheet parameter is None, assign it with the name of the first worksheet in the Excel file.
            if sheet_name is None:
                sheet_name = pandas_util.create_excel_workbook_obj(file_abs).sheet_names[0]

            # If the input sheet name is not a valid sheet name in the Excel workbook file, raise a FAILURE.
            should_run_command.append(validator_util.run_check(self, "IsExcelSheetNameValid", "Worksheet", sheet_name,
                                                               "FAIL", other_values=[file_abs]))

            # If the TableID parameter is None, assign the parameter with the sheet name.
            if table_id is None:
                table_id = sheet_name

            # If the TableID is the same as an already-existing TableID, raise a WARNING or FAILURE
            # (depends on the value of the IfTableIDExists parameter).
            should_run_command.append(validator_util.run_check(self, "IsTableIdUnique", "TableID", table_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self):
        """
        Run the command. Read the tabular data from the Excel workbook/worksheet.
        Create a Table object, and add to the GeoProcessor's tables list.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_InputFile = self.get_parameter_value("InputFile")
        # noinspection PyPep8Naming
        pv_Worksheet = self.get_parameter_value("Worksheet")
        # noinspection PyPep8Naming
        pv_TableID = self.get_parameter_value("TableID")

        # Convert the InputFile parameter value relative path to an absolute path and expand for ${Property} syntax.
        file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_InputFile, self)))

        # If the pv_TableID is a valid %-formatter, assign the pv_GeoLayerID the corresponding value.
        if pv_TableID in ['%f', '%F', '%E', '%P', '%p']:
            # noinspection PyPep8Naming
            pv_TableID = io_util.expand_formatter(file_absolute, pv_TableID)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(file_absolute, pv_Worksheet, pv_TableID):
            # noinspection PyBroadException
            try:
                # Assign the Worksheet parameter to the name of the first Excel worksheet, if it was not specified.
                if pv_Worksheet is None:
                    # noinspection PyPep8Naming
                    pv_Worksheet = pandas_util.create_excel_workbook_obj(file_absolute).sheet_names[0]

                # Assign the TableID parameter to the name of the first Excel worksheet, if it was not specified.
                if pv_TableID is None:
                    # noinspection PyPep8Naming
                    pv_TableID = pv_Worksheet

                # Create a Pandas Data Frame object.
                df = pandas_util.create_data_frame_from_excel(file_absolute, pv_Worksheet)

                # Create a Table and add it to the geoprocessor's Tables list.
                table_obj = Table(pv_TableID, df, file_absolute)
                self.command_processor.add_table(table_obj)

            # Raise an exception if an unexpected error occurs during the process.
            except Exception:
                self.warning_count += 1
                message = "Unexpected error reading Table {} from Excel file {}.".format(pv_TableID, pv_InputFile)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred.
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
