# ReadTableFromDelimitedFile - command to read a table from a delimited file
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
from geoprocessor.core.DataTable import DataTable
from geoprocessor.core.TableRecord import TableRecord
from geoprocessor.core.TableField import TableField

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import csv
import logging


class ReadTableFromDelimitedFile(AbstractCommand):
    """
    Reads a table from a delimited file and store as a DataTable instance in the geoprocessor.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("InputFile", str),
        CommandParameterMetadata("Delimiter", str),
        CommandParameterMetadata("TableID", str),
        CommandParameterMetadata("SkipLines", str),
        CommandParameterMetadata("ColumnNames", str),
        CommandParameterMetadata("FloatColumns", str),
        CommandParameterMetadata("IntegerColumns", str),
        CommandParameterMetadata("TextColumns", str),
        CommandParameterMetadata("Top", int),
        CommandParameterMetadata("RowCountProperty", str),
        CommandParameterMetadata("IfTableIDExists", str)]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = (
        "Read a table from a delimited file.\n"
        "Columns in the file should be delimited by commas (default) or other character.\n"
        "An example data file is shown below (line and data row numbers are shown on the left for illustration):\n"
        "  1     | # This is a comment\n"
        "  2     | # This is another comment\n"
        "  3     | # Column names are assumed to be the first non-comment line (next line).\n"
        "  4     | Column1,Column2,\"Column3\",Column4\n"
        "  5  1  | 1,1.0,1.5\n"
        "  6  2  | 2,2.0,3.0\n"
        "  7     | # Embedded comment will be skipped\n"
        "  8  3  | 3,3.0,4.5\n")
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # InputFile
    __parameter_input_metadata['InputFile.Description'] = "delimited file to read"
    __parameter_input_metadata['InputFile.Label'] = "Input file"
    __parameter_input_metadata['InputFile.Required'] = True
    __parameter_input_metadata['InputFile.Tooltip'] = \
        "The delimited file (relative or absolute path) to read. ${Property} syntax is recognized."
    __parameter_input_metadata['InputFile.FileSelector.Type'] = "Read"
    __parameter_input_metadata['InputFile.FileSelector.Title'] = "Select a delimited file to read"
    __parameter_input_metadata['InputFile.FileSelector.Filters'] = \
        ["Delimited file (*.csv *.txt)", "All files (*)"]
    # TableID
    __parameter_input_metadata['TableID.Description'] = "output table identifier"
    __parameter_input_metadata['TableID.Label'] = "TableID"
    __parameter_input_metadata['TableID.Required'] = True
    __parameter_input_metadata['TableID.Tooltip'] = "A Table identifier"
    # Delimiter
    __parameter_input_metadata['Delimiter.Description'] = "delimiter character"
    __parameter_input_metadata['Delimiter.Label'] = "Delimiter"
    __parameter_input_metadata['Delimiter.Tooltip'] = "The delimiter character of the input delimited file."
    __parameter_input_metadata['Delimiter.Value.Default'] = ","
    __parameter_input_metadata['Delimiter.Value.Default.Description'] = ", comma"
    # SkipLines
    __parameter_input_metadata['SkipLines.Description'] = "number(s) of lines to skip"
    __parameter_input_metadata['SkipLines.Label'] = "Skip lines"
    __parameter_input_metadata['SkipLines.Tooltip'] = (
        "The lines to skip, whice would otherwise interfere with reading data. "
        "Individual rows and ranges can be specified (e.g., 1, 1-10).")
    # ColumnNames
    __parameter_input_metadata['ColumnNames.Description'] = "column names if not read from file"
    __parameter_input_metadata['ColumnNames.Label'] = "Column names"
    __parameter_input_metadata['ColumnNames.Tooltip'] = (
        "Column names, separated by commas, if not read from the file")
    # FloatColumns
    __parameter_input_metadata['FloatColumns.Description'] = "columns that floating point numbers, separated by commas"
    __parameter_input_metadata['FloatColumns.Label'] = "Text columns"
    __parameter_input_metadata['FloatColumns.Tooltip'] = (
        "Column names, separated by commas, for columns that contain floating point numbers.")
    # IntegerColumns
    __parameter_input_metadata['IntegerColumns.Description'] = "columns that contain integers, separate by commas"
    __parameter_input_metadata['IntegerColumns.Label'] = "Integer columns"
    __parameter_input_metadata['IntegerColumns.Tooltip'] = (
        "Column names, separated by commas, for columns that contain integer.")
    # TextColumns
    __parameter_input_metadata['TextColumns.Description'] = "columns that contain text, separated by commas"
    __parameter_input_metadata['TextColumns.Label'] = "Text columns"
    __parameter_input_metadata['TextColumns.Tooltip'] = (
        "Column names, separated by commas, for columns that contain text.")
    # Top
    __parameter_input_metadata['Top.Description'] = "only read top N data rows"
    __parameter_input_metadata['Top.Label'] = "Top N rows"
    __parameter_input_metadata['Top.Tooltip'] = (
        "Specify a maximum number of data rows to read, useful for inspecting a file.")
    # RowCountProperty
    __parameter_input_metadata['RowCountProperty.Description'] = "processor property to set as output table row count"
    __parameter_input_metadata['RowCountProperty.Label'] = "Row count property"
    __parameter_input_metadata['RowCountProperty.Tooltip'] = (
        "Name of processor property to set to the number of data rows read.")
    # IfTableIDExists
    __parameter_input_metadata[
        'IfTableIDExists.Description'] = "action if TableID exists"
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

        # AbstractCommand data
        super().__init__()
        self.command_name = "ReadTableFromDelimitedFile"
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

        # Check that optional parameter Top is an integer.
        # noinspection PyPep8Naming
        pv_Top = self.get_parameter_value(parameter_name="Top", command_parameters=command_parameters)
        if not validator_util.validate_int(pv_Top, True, True):
            message = "Top parameter value ({}) is not an integer.".format(pv_Top)
            recommendation = "Specify as an integer 1+."
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.WARNING, message, recommendation))

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

        # If the SkipLines is used, continue with the checks.
        # noinspection PyPep8Naming
        pv_SkipLines = self.get_parameter_value("SkipLines", command_parameters=command_parameters)
        if pv_SkipLines:

            # Check that the SkipLines parameter is an integer or None.
            if not validator_util.validate_int(pv_SkipLines, True, False):

                message = "SkipLines parameter value ({}) is not a valid integer value.".format(pv_SkipLines)
                recommendation = "Specify a positive integer for the SkipLines parameter to specify how" \
                                 " many rows represent the header content of the delimited file."
                warning_message += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
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

    def check_runtime_data(self, input_file_abs: str, table_id: str) -> bool:
        """
       Checks the following:
        * the InputFile (absolute) is a valid file
        * the ID of the Table is unique (not an existing Table ID)

       Args:
           input_file_abs (str): the full pathname to the input data file
           table_id (str): the ID of the output Table

       Returns:
           Boolean. If TRUE, the reading process should be run. If FALSE, it should not be run.
       """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the input file is not a valid file path, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsFilePathValid", "InputFile",
                                                           input_file_abs, "FAIL"))

        # If the TableID is the same as an already-existing TableID, raise a WARNING or FAILURE (depends on the
        # value of the IfTableIDExists parameter.)
        should_run_command.append(validator_util.run_check(self, "IsTableIdUnique", "TableID", table_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    @classmethod
    def need_to_skip_line(cls, line: int, skip_lines: [int]) -> bool:
        """
        Evaluate whether an input file line needs to be skipped.

        Args:
            line (int):  Line number 1+ being read.
            skip_lines ([int]):  Array of line numbers to skip.

        Returns:
            bool indicating whether to skip the line.
        """
        if skip_lines is None:
            return False

        for skip_line in skip_lines:
            if line == skip_line:
                return True

        return False

    @classmethod
    def read_table_from_delimited_file(cls, path: str, table_id: str, problems: [str],
                                       column_names: [str] = None,
                                       delimiter: str = ",",
                                       float_columns: [str] = None,
                                       integer_columns: [str] = None,
                                       text_columns: [str] = None,
                                       top: int = None,
                                       skip_lines: [int] = None) -> DataTable:
        """
        Creates a GeoProcessor table object from a delimited file.
        This method uses the Python 'csv' object, which may have limitations.

        Args:
            path (str): the path to the delimited file on the local machine
            table_id (str): the id of the GeoProcessor Table that is to be created
            problems ([str]): a list to be filled with problems, for use in calling code
            column_names ([str]): list of column names, if not read from first row
            delimiter (str): the delimiter character of the input file
            float_columns ([str]): list of column names for columns that contain floating point numbers
            integer_columns ([str]): list of column names for columns that contain integers
            skip_lines ([int]): a list of line numbers to skip
            text_columns ([str]): list of column names for columns that contain text
            top (int): number of data rows to read

        Return:
            A GeoProcessor DataTable object.
        """

        logger = logging.getLogger(__name__)

        # Read lines from the CSV file using the Python 'csv' module:
        # - skip_lines is checked to see if any lines need to be skipped
        # - comment lines are those where the first item starts with '#'
        # - header line is the first line that is read

        # Processing occurs in 3 steps, similar to TSTool design:
        # 1. parse the file into strings, saving the initial parsed results
        # 2. evaluate the strings for column type
        # 3. create and save the table based on column types and converted strings

        line_count = 0
        parsed_lines = []
        comment_char = '#'
        num_columns = -1
        with open(path, 'r') as csvfile:

            # Pass the csv file to the csv.reader object. Specify the delimiter.
            csvreader = csv.reader(csvfile, delimiter=delimiter)

            for row in csvreader:
                # Increment the counter
                line_count = line_count + 1

                # Skip rows if requested
                if ReadTableFromDelimitedFile.need_to_skip_line(line_count, skip_lines):
                    continue

                # Skip comment lines
                if (len(row) > 0) and row[0].startswith(comment_char):
                    continue

                # Save the parsed lines
                parsed_lines.append(row)

                # Save the number of columns
                # - should be the same for all rows and if not the final table may be string cell values with some
                #   empty cells
                # - add to problems if number of columns is different for any row
                if num_columns < 0:
                    num_columns = len(row)
                elif len(row) != num_columns:
                    problems.append("Line {} has {} columns, which is different from first line".format(len(row),
                                    line_count))
                    if len(row) > num_columns:
                        num_columns = len(row)

        # Now have parsed lines
        logger.info("Read {} header and data lines after skipping requested lines and comments".format(
            len(parsed_lines)))
        logger.info("Read {} columns".format(num_columns))

        # Read through the parsed data and estimate column types from string values.
        # The count arrays are for each column.
        bool_count = [0]*num_columns
        int_count = [0]*num_columns
        float_count = [0]*num_columns
        str_count = [0]*num_columns

        # Determine which row is the first data row.
        # - depends on whether column names where specified
        first_data_row = 1 # 0-index
        num_data_rows = len(parsed_lines) - 1
        if column_names is not None and (len(column_names) > 0):
            # Column names were specified since not in the file so process all rows as data.
            first_data_row = 0
            num_data_rows = len(parsed_lines)

        # Only process data rows (not column heading) so that data types are properly determined
        for irow in range(first_data_row, len(parsed_lines)):
            row = parsed_lines[irow]
            icol = -1
            for cell in row:
                # Trim surrounding whitespace
                cell = cell.strip()
                icol += 1
                # Check whether the string can convert to a type.  Allow empty cell to be any type and set to
                # None or NaN below when parsing actually occurs.
                if (len(cell) == 0) or string_util.is_bool(cell):
                    bool_count[icol] += 1
                if (len(cell) == 0) or string_util.is_int(cell):
                    int_count[icol] += 1
                if (len(cell) == 0) or string_util.is_float(cell):
                    float_count[icol] += 1
                # Always count as string
                str_count[icol] += 1

        for icol in range(num_columns):
            logger.info("Column [{}] data rows have {} bool".format(icol, bool_count[icol]))
            logger.info("Column [{}] data rows have {} int".format(icol, int_count[icol]))
            logger.info("Column [{}] data rows have {} float".format(icol, float_count[icol]))
            logger.info("Column [{}] data rows have {} str".format(icol, str_count[icol]))

        # Create a table object with columns of the correct type
        table = DataTable(table_id)
        # Whether header row is in data rows and need to offset when processing data records
        for icol in range(num_columns):
            # Data type is based on counts of types from inspection.
            # - use integer before float
            data_type = str
            if int_count[icol] == num_data_rows:
                data_type = int
            elif float_count[icol] == num_data_rows:
                data_type = float
            elif bool_count[icol] == num_data_rows:
                data_type = bool
            # TODO smalers 2020-11-14 need to enable date or date/time similar to Java code

            # Column name is just the first row parsed
            if column_names is not None and (len(column_names) > 0):
                # Column names were specified
                if len(column_names) > icol:
                    column_name = column_names[icol]
                else:
                    column_name = "Column{}".format((icol + 1))
            else:
                # Column names are taken from the first row of parsed data
                column_name = parsed_lines[0][icol]

            # If data types were specified via column names, override the data type.
            if float_columns is not None:
                for float_column in float_columns:
                    if float_column.equals(column_name):
                        data_type = float
            if integer_columns is not None:
                for integer_column in float_columns:
                    if integer_column.equals(column_name):
                        data_type = int
            if text_columns is not None:
                for text_column in float_columns:
                    if text_column.equals(column_name):
                        data_type = str

            # Default is to set the description the same as the name
            description = column_name
            # TODO smalers 2020-11-14 set the width and precision based on string length, etc.
            width = None
            precision = None
            units = ""
            table.add_field(TableField(data_type, column_name, description=description, width=width,
                                       precision=precision, units=units))

        # Populate the table with data by traversing the parsed data again and converting from strings to types.
        for irow, row in enumerate(parsed_lines):
            # Skip header
            if irow < first_data_row:
                continue
            # Break if only reading top rows
            if top is not None and (irow == top):
                break
            table_record = TableRecord()
            # Process each row in the table.
            for icol in range(len(row)):
                cell = row[icol]
                cell_len = len(cell)
                table_field_data_type = table.table_fields[icol].data_type
                # Process each item in the row and add to the record.
                # First convert to the column type.
                if table_field_data_type == int:
                    if cell_len == 0:
                        value = None
                    else:
                        value = "{}".format(cell)
                elif table_field_data_type == float:
                    if cell_len == 0:
                        value = None
                    else:
                        # The following will handle parsing 'NaN' in any case.
                        value = float(cell)
                elif table_field_data_type == bool:
                    if cell_len == 0:
                        value = None
                    else:
                        value = int(cell)
                else:
                    # Treat as a string
                    value = "{}".format(cell)
                # Add the value to the table record.
                table_record.add_field_value(value)

            # Add the record to the table
            table.add_record(table_record)

        return table

    def run_command(self) -> None:
        """
        Run the command. Read the Table from the delimited file.

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
        pv_Delimiter = self.get_parameter_value("Delimiter", default_value=",")
        # noinspection PyPep8Naming
        pv_TableID = self.get_parameter_value("TableID")
        # noinspection PyPep8Naming
        pv_SkipLines = self.get_parameter_value("SkipLines")
        skip_lines = string_util.parse_integer_list(pv_SkipLines)
        # noinspection PyPep8Naming
        pv_ColumnNames = self.get_parameter_value("ColumnNames")
        column_names = string_util.delimited_string_to_list(pv_ColumnNames)
        # noinspection PyPep8Naming
        pv_FloatColumns = self.get_parameter_value("FloatColumns")
        float_columns = string_util.delimited_string_to_list(pv_FloatColumns)
        # noinspection PyPep8Naming
        pv_IntegerColumns = self.get_parameter_value("IntegerColumns")
        integer_columns = string_util.delimited_string_to_list(pv_IntegerColumns)
        # noinspection PyPep8Naming
        pv_TextColumns = self.get_parameter_value("TextColumns")
        text_columns = string_util.delimited_string_to_list(pv_TextColumns)
        # noinspection PyPep8Naming
        pv_Top = self.get_parameter_value("Top")
        top = None
        if pv_Top is not None and pv_Top != "":
            top = int(pv_Top)
        # noinspection PyPep8Naming
        pv_RowCountProperty = self.get_parameter_value("RowCountProperty")

        # Convert the InputFile parameter value relative path to an absolute path and expand for ${Property} syntax
        input_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_InputFile, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(input_file_absolute, pv_TableID):
            # noinspection PyBroadException
            try:
                # Create the table from the delimited file.
                problems = []
                table = ReadTableFromDelimitedFile.read_table_from_delimited_file(input_file_absolute, pv_TableID,
                                                                                  problems,
                                                                                  column_names=column_names,
                                                                                  delimiter=pv_Delimiter,
                                                                                  float_columns=float_columns,
                                                                                  integer_columns=integer_columns,
                                                                                  skip_lines=skip_lines,
                                                                                  text_columns=text_columns,
                                                                                  top=top)

                # Add the table to the GeoProcessor's Tables list.
                self.command_processor.add_table(table)

                # Add problems if any as warnings
                if len(problems) > 0:
                    for problem in problems:
                        self.warning_count += 1
                        recommendation = "Check the log file for details."
                        self.logger.warning(problem, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.WARNING, problem,
                                                                        recommendation))

                # Set the row count property in the processor if requested.
                if pv_RowCountProperty is not None and (len(pv_RowCountProperty) > 0):
                    self.command_processor.set_property(pv_RowCountProperty, table.get_number_of_rows())

            # Raise an exception if an unexpected error occurs during the process
            except Exception:
                self.warning_count += 1
                message = "Unexpected error reading table {} from delimited file ({}).".format(pv_TableID,
                                                                                               input_file_absolute)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
