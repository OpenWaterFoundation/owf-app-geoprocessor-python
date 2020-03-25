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
from geoprocessor.core.Table import Table
from geoprocessor.core.Table import TableRecord
from geoprocessor.core.Table import TableField

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import csv
import logging


class ReadTableFromDelimitedFile(AbstractCommand):
    """
    Reads a Table from a delimited file.

    Command Parameters
    * InputFile (str, required): the relative or absolute pathname of the delimited file to read.
    * TableID (str, required): the identifier of the Table.
    * Delimiter (str, optional): the delimiter of the input file. Default is `,`.
    * HeaderLines (str, optional): The number of rows representing non-data comments. These columns are not included
        in the output Table data values. Default: 0
    * NullValues (str, optional): A list of values within the delimited file that represent null values.
        Default: '' (an empty string)
    * IfTableIDExists (str, optional): This parameter determines the action that occurs if the TableID already exists
        within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("InputFile", type("")),
        CommandParameterMetadata("Delimiter", type("")),
        CommandParameterMetadata("TableID", type("")),
        CommandParameterMetadata("HeaderLines", type("")),
        CommandParameterMetadata("NullValues", type("")),
        CommandParameterMetadata("IfTableIDExists", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Read a table from a delimited file."
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
    # HeaderLines
    __parameter_input_metadata['HeaderLines.Description'] = "number of rows of non-data comments"
    __parameter_input_metadata['HeaderLines.Label'] = "Header lines"
    __parameter_input_metadata['HeaderLines.Tooltip'] = (
        "The number of rows representing non-data comments. "
        "These columns are not included in the output Table data values.")
    __parameter_input_metadata['HeaderLines.Value.Default'] = "0"
    # NullValues
    __parameter_input_metadata['NullValues.Description'] = "values that should convert to NULL"
    __parameter_input_metadata['NullValues.Label'] = "Null values"
    __parameter_input_metadata['NullValues.Tooltip'] = (
        "A list of values within the delimited file that should br converted to NULL values. "
        "The Python None will be used internally.")
    __parameter_input_metadata['NullValues.Value.Default'] = "None"
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

        # If the HeaderLines is used, continue with the checks.
        # noinspection PyPep8Naming
        pv_HeaderLines = self.get_parameter_value("HeaderLines", command_parameters=command_parameters)
        if pv_HeaderLines:

            # Check that the HeaderLines parameter is an integer or None.
            if not validator_util.validate_int(pv_HeaderLines, True, False):

                message = "HeaderLines parameter value ({}) is not a valid integer value.".format(pv_HeaderLines)
                recommendation = "Specify a positive integer for the HeaderLines parameter to specify how" \
                                 " many rows represent the header contnet of the delimited file."
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

    @staticmethod
    def __read_table_from_delimited_file(path: str, table_id: str, delimiter: str, header_count: int,
                                         null_values: [str]) -> Table:
        """
        Creates a GeoProcessor table object from a delimited file.

        Args:
            path (str): the path to the delimited file on the local machine
            table_id (str): the id of the GeoProcessor Table that is to be created
            delimiter (str): the delimiter of the input file
            header_count (int): the number of rows representing the header content (not data values)
            null_values (list): list of strings that are values in the delimited file representing null values

        Return: A GeoProcessor Table object.
        """

        # Create a table object
        table = Table(table_id)

        # Open the csv file to read.
        with open(path, 'r') as csvfile:

            # Pass the csv file to the csv.reader object. Specify the delimiter.
            csvreader = csv.reader(csvfile, delimiter=delimiter)

            # Get the column headers as a list. Skip over any header lines of comments.
            for i in range(header_count + 1):
                col_headers = next(csvreader)

            # Iterate over the number of columns specified by a column header name.
            for i in range(len(col_headers)):

                # Create a TableField object and assign the field "name" as the column header name.
                table_field = TableField(col_headers[i])

                # An empty list to hold the items within the TableField.
                col_content = []

                # Reset the csv reader to start the reading of the csv file at the first row.
                csvfile.seek(0)

                # Skip the header rows.
                for i_head in range(header_count+1):
                    next(csvreader)

                # Iterate over the non-header rows and append the column items to the col_content list.
                for row in csvreader:
                    col_content.append(row[i])

                # Add the column contents to the TableField object.
                table_field.items = col_content

                # Set the null values
                table_field.null_values = null_values

                # Convert the data value that represent null values into None value.\
                table_field.assign_nulls()

                # Convert the column contents to the correct data type.
                table_field.assign_data_type()

                # Add the updated table field object to the Table attribute.
                table.add_table_field(table_field)

            # Get the number of row entries.
            table.entry_count = len(table_field.items)

        # Iterate over the number of row entries.
        for i_row in range(table.entry_count):

            # Create a TableRecord object.
            table_record = TableRecord()

            # Iterate over the table fields.
            for i_col in range(len(table.table_fields)):
                new_item = table.table_fields[i_col].items[i_row]
                table_record.add_item(new_item)

            # Add the table record to the Table attributes.
            table.table_records.append(table_record)

        # Return the GeoProcessor Table object.
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
        pv_HeaderLines = int(self.get_parameter_value("HeaderLines", default_value="0"))
        # noinspection PyPep8Naming
        pv_NullValues = self.get_parameter_value("NullValues", default_value="''")

        # Convert the InputFile parameter value relative path to an absolute path and expand for ${Property} syntax
        input_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_InputFile, self)))

        # Convert the NullValues parameter values to a list.
        # noinspection PyPep8Naming
        pv_NullValues = string_util.delimited_string_to_list(pv_NullValues)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(input_file_absolute, pv_TableID):
            # noinspection PyBroadException
            try:
                # Create the table from the delimited file.
                table = self.__read_table_from_delimited_file(input_file_absolute, pv_TableID, pv_Delimiter,
                                                              pv_HeaderLines, pv_NullValues)

                # Add the table to the GeoProcessor's Tables list.
                self.command_processor.add_table(table)

            # Raise an exception if an unexpected error occurs during the process
            except Exception:
                self.warning_count += 1
                message = "Unexpected error reading Table {} from delimited file ({}).".format(pv_TableID,
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