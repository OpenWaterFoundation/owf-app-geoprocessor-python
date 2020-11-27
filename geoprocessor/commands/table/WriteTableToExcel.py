# WriteTableToExcel - command to write a table to an Excel worksheet
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

from geoprocessor.core.CommandError import CommandError
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.pandas_util as pandas_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import logging
import os


class WriteTableToExcel(AbstractCommand):
    """
    Writes a Table to an Excel file.

    Command Parameters
    * TableID (str, required): the identifier of the Table to be written to the Excel file 
    * OutputFile (str, required): the relative pathname of the output Excel file.
    * OutputWorksheet (str, required): the name of the worksheet that the Table will be written
    * ColumnsToInclude (str, optional): A list of glob-style patterns to determine the table columns to include in the
        output delimited file. Default: * (All columns are written).
    * ColumnsToExclude (str, optional): A list of glob-style patterns to determine the table columns to exclude in the
        output delimited file. Default: Default: '' (No columns are excluded from the output delimited file).
    * WriteIndexColumn (bool, optional): If TRUE, the index column is written, If FALSE, the index column is excluded.
        Default: True
    """

    # Define the command parameters/
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("TableID", type("")),
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("OutputWorksheet", type("")),
        CommandParameterMetadata("ColumnsToInclude", type("")),
        CommandParameterMetadata("ColumnsToExclude", type("")),
        CommandParameterMetadata("WriteIndexColumn", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Write a table to an Excel file."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # TableID
    __parameter_input_metadata['TableID.Description'] = "table identifier"
    __parameter_input_metadata['TableID.Label'] = "TableID"
    __parameter_input_metadata['TableID.Required'] = True
    __parameter_input_metadata['TableID.Tooltip'] = "A Table identifier to write"
    # OutputFile
    __parameter_input_metadata['OutputFile.Description'] = "output Excel file"
    __parameter_input_metadata['OutputFile.Label'] = "Output file"
    __parameter_input_metadata['OutputFile.Required'] = True
    __parameter_input_metadata['OutputFile.Tooltip'] = (
        "The name of the Excel workbook to write to (relative or absolute path). ${Property} syntax is recognized.\n"
        "Can be an existing or non-existing Excel file. If non-existing, the Excel workbook file (.xlsx) is created.")
    __parameter_input_metadata['OutputFile.FileSelector.Filters'] = \
        ["Excel file (*.xlsx *.xls)", "All files (*)"]
    # OutputWorksheet
    __parameter_input_metadata['OutputWorksheet.Description'] = "worksheet to write"
    __parameter_input_metadata['OutputWorksheet.Label'] = "Output worksheet"
    __parameter_input_metadata['OutputWorksheet.Required'] = True
    __parameter_input_metadata['OutputWorksheet.Tooltip'] = (
        "The name of the worksheet that the Table will be written to. Can be an existing or non-existing "
        "worksheet.\nIf existing, the worksheet will be overwritten with the Table data.")
    # ColumnsToInclude
    __parameter_input_metadata['ColumnsToInclude.Description'] = "columns to include"
    __parameter_input_metadata['ColumnsToInclude.Label'] = "Include Columns"
    __parameter_input_metadata['ColumnsToInclude.Tooltip'] = \
        "A comma-separated list of the glob-style patterns filtering which columns to write."
    __parameter_input_metadata['ColumnsToInclude.Value.Default'] = "* - all columns are processed"
    # ColumnsToExclude
    __parameter_input_metadata['ColumnsToExclude.Description'] = "columns to exclude"
    __parameter_input_metadata['ColumnsToExclude.Label'] = "Exclude columns"
    __parameter_input_metadata['ColumnsToExclude.Tooltip'] = \
        "A comma-separated list of the glob-style patterns filtering which columns to write. "
    __parameter_input_metadata['ColumnsToExclude.Value.Default'] = "all columns are processed"
    # WriteIndexColumn
    __parameter_input_metadata['WriteIndexColumn.Description'] = "whether to write index column"
    __parameter_input_metadata['WriteIndexColumn.Label'] = "Write index column?"
    __parameter_input_metadata['WriteIndexColumn.Tooltip'] = (
        "If TRUE, the Table's index column is included in the output Excel file.\n"
        "If FALSE, the Table's index column is not included in the output Excel file")
    __parameter_input_metadata['WriteIndexColumn.Value.Default'] = "TRUE"
    __parameter_input_metadata['WriteIndexColumn.Values'] = ["", "TRUE", "FALSE"]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "WriteTableToExcel"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata
        self.parameter_input_metadata = self.__parameter_input_metadata

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters: dict) -> None:
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

        # Check that parameter WriteIndexColumn is a valid Boolean value or None.
        # noinspection PyPep8Naming
        pv_WriteIndexColumn = self.get_parameter_value(parameter_name='WriteIndexColumn',
                                                       command_parameters=command_parameters)

        if not validator_util.validate_bool(pv_WriteIndexColumn, True, False):
            message = "WriteIndexColumn parameter is not a valid Boolean value."
            recommendation = "Specify a valid Boolean value for the WriteIndexColumn parameter."
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

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, table_id: str, output_file_abs: str) -> bool:
        """
        Checks the following:
        * the ID of the Table is an existing Table ID
        * the output folder is a valid folder

        Args:
            table_id: the ID of the Table to be written
            output_file_abs: the full pathname to the output file

        Returns:
            run_write: Boolean. If TRUE, the writing process should be run. If FALSE, it should not be run.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the Table ID is not an existing Table ID, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsTableIdExisting", "TableID", table_id, "FAIL"))

        # Get the full path to the output folder
        output_folder_abs = io_util.get_path(output_file_abs)

        # If the output folder is not an existing folder, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsFolderPathValid", "OutputFile", output_folder_abs,
                                                           "FAIL"))
        # Continue if the output file is an existing file.
        if os.path.exists(output_folder_abs):

            if io_util.get_extension(output_file_abs).upper() == "XLS":

                message = 'At the current time, a Table object cannot be appended to or overwrite an existing Excel ' \
                          'file in XLS format.'
                recommendation = "Update the XLS file ({}) to an XLSX file or write the table " \
                                 "to a new XLS file.".format(output_file_abs)

                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.FAILURE,
                                                                                      message, recommendation))
                should_run_command.append(False)

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Write the Table to an excel file.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values except for the OutputCRS
        # noinspection PyPep8Naming
        pv_TableID = self.get_parameter_value("TableID")
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value("OutputFile")
        # noinspection PyPep8Naming
        pv_OutputWorksheet = self.get_parameter_value("OutputWorksheet")
        # noinspection PyPep8Naming
        pv_ColumnsToInclude = self.get_parameter_value("ColumnsToInclude", default_value="*")
        # noinspection PyPep8Naming
        pv_ColumnsToExclude = self.get_parameter_value("ColumnsToExclude", default_value="")
        # noinspection PyPep8Naming
        pv_WriteIndexColumn = self.get_parameter_value("WriteIndexColumn", default_value="True")

        # Convert the Boolean parameters from string to valid Boolean values.
        # noinspection PyPep8Naming
        pv_WriteIndexColumn = string_util.str_to_bool(pv_WriteIndexColumn)

        # Convert the ColumnsToInclude and ColumnsToExclude parameter values to lists.
        cols_to_include = string_util.delimited_string_to_list(pv_ColumnsToInclude)
        cols_to_exclude = string_util.delimited_string_to_list(pv_ColumnsToExclude)

        # Convert the OutputFile parameter value relative path to an absolute path and expand for ${Property} syntax
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(pv_TableID, output_file_absolute):
            # noinspection PyBroadException
            try:
                # Get the Table object
                table = self.command_processor.get_table(pv_TableID)

                # Get a list of all the available column names in the Table.
                all_cols_names = list(table.df)

                # Sort the list to create a second list that only includes the attributes that should be removed.
                cols_to_keep = string_util.filter_list_of_strings(list(table.df), cols_to_include, cols_to_exclude,
                                                                  return_inclusions=True)

                # For the columns configured to be written, order them in the same order that they were in with the
                # original table. This step ensures that the output table product has the columns in the same order as
                # the user would expect.
                sorted_cols_to_keep = []
                for col in all_cols_names:
                    if col in cols_to_keep:
                        sorted_cols_to_keep.append(col)

                # Write the tables to an Excel file.
                pandas_util.write_df_to_excel(table.df, output_file_absolute, pv_OutputWorksheet, sorted_cols_to_keep,
                                              pv_WriteIndexColumn)

                # Add the output file to the GeoProcessor's list of output files.
                self.command_processor.add_output_file(output_file_absolute)

            except Exception:
                # Raise an exception if an unexpected error occurs during the process
                self.warning_count += 1
                message = "Unexpected error writing Table {} to Excel workbook file {}.".format(pv_TableID,
                                                                                                pv_OutputFile)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
