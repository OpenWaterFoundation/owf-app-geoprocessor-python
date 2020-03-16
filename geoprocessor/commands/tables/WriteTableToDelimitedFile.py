# WriteTableToDelimitedFile - command to write a table to a delimited file
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
from geoprocessor.core.Table import Table

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import csv
import logging
from operator import itemgetter, attrgetter


class WriteTableToDelimitedFile(AbstractCommand):
    """
    Writes a Table to an delimiter-separated file.

    Command Parameters
    * TableID (str, required): the identifier of the Table to be written to the delimited file
    * OutputFile (str, required): the relative pathname of the output delimited file.
    * Delimiter (str, optional): the delimiter of the output file. Default is `,` Must be a one-character
        string (limitation is built into the Pandas to_csv command).
    * IncludeColumns (str, optional): A list of glob-style patterns to determine the table columns to include in the
        output delimited file. Default: * (All columns are written).
    * ExcludeColumns (str, optional): A list of glob-style patterns to determine the table columns to exclude in the
        output delimited file. Default: Default: '' (No columns are excluded from the output delimited file).
    * WriteHeaderRow (bool, optional): If TRUE, the header row is written, If FALSE, the header row is excluded.
        Default: True
    * WriteIndexColumn (bool, optional): If TRUE, the index column is written, If FALSE, the index column is excluded.
        Default: True
    * SortColumns (str, optional): The names of the Table columns, separated by commas, used to sort the order that
        the table records are written to the delimited file. Default: The first Table column.
    * SortOrder(str, optional): The sort order for the columns specified by SortColumns, using the syntax:
        SortColumn1:Ascending,SortColumn2:Descending Default: Ascending
    * ArrayFormat (str, optional): If SquareBrackets, table column array values are written as a string with square
        brackets. If CurlyBrackets, table column array values are written as a string with curly brackets.
        Default: SquareBrackets
    * NullValueFormat (str, optional): If `NULL`, table column array values with None items are changed to NULL.
        If `None`, table column array values with None items remain None. Default: NULL
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("TableID", type("")),
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("Delimiter", type("")),
        CommandParameterMetadata("IncludeColumns", type("")),
        CommandParameterMetadata("ExcludeColumns", type("")),
        CommandParameterMetadata("WriteHeaderRow", type("")),
        CommandParameterMetadata("WriteIndexColumn", type("")),
        CommandParameterMetadata("SortColumns", type("")),
        CommandParameterMetadata("SortOrder", type("")),
        CommandParameterMetadata("ArrayFormat", type("")),
        CommandParameterMetadata("NullValueFormat", type(""))]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Write a table to a delimited file."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata
    __parameter_input_metadata = dict()
    # TableID
    __parameter_input_metadata['TableID.Description'] = "table identifier"
    __parameter_input_metadata['TableID.Label'] = "TableID"
    __parameter_input_metadata['TableID.Required'] = True
    __parameter_input_metadata['TableID.Tooltip'] = "A Table identifier to write"
    # OutputFile
    __parameter_input_metadata['OutputFile.Description'] = "output delimited file"
    __parameter_input_metadata['OutputFile.Label'] = "Output file"
    __parameter_input_metadata['OutputFile.Required'] = True
    __parameter_input_metadata['OutputFile.Tooltip'] = (
        "The output delimited file (relative or absolute path).\n"
        "${Property} syntax is recognized.")
    __parameter_input_metadata['OutputFile.FileSelector.Type'] = 'Write'
    __parameter_input_metadata['OutputFile.FileSelector.Title'] = 'Select delimited file'
    __parameter_input_metadata['OutputFile.FileSelector.Filters'] = \
        ["Delimited file (*.csv *.txt)", "All files (*)"]
    # Delimiter
    __parameter_input_metadata['Delimiter.Description'] = "delimiter for file"
    __parameter_input_metadata['Delimiter.Label'] = "Delimiter"
    __parameter_input_metadata['Delimiter.Tooltip'] = \
        "The delimiter of the output delimited file. Must be a single character."
    __parameter_input_metadata['Delimiter.Value.Default'] = ","
    # IncludeColumns
    __parameter_input_metadata['IncludeColumns.Description'] = "columns to include"
    __parameter_input_metadata['IncludeColumns.Label'] = "Include columns"
    __parameter_input_metadata['IncludeColumns.Tooltip'] = \
        "A comma-separated list of the glob-style patterns filtering which columns to write."
    __parameter_input_metadata['IncludeColumns.Value.Default.Description'] = "* - all columns"
    # ExcludeColumns
    __parameter_input_metadata['ExcludeColumns.Description'] = "columns to exclude "
    __parameter_input_metadata['ExcludeColumns.Label'] = "Exclude columns"
    __parameter_input_metadata['ExcludeColumns.Tooltip'] = \
        "A comma-separated list of the glob-style patterns filtering which columns to write. "
    __parameter_input_metadata['ExcludeColumns.Value.Default.Description'] = "no columns are excluded"
    # WriteHeaderRow
    __parameter_input_metadata['WriteHeaderRow.Description'] = "how to write headers"
    __parameter_input_metadata['WriteHeaderRow.Label'] = "Write header row"
    __parameter_input_metadata['WriteHeaderRow.Tooltip'] = (
        "If TRUE, the Table's header row is included in the output delimited file.\n"
        "If FALSE, the Table's header row is not included in the output delimited file.")
    __parameter_input_metadata['WriteHeaderRow.Value.Default'] = "TRUE"
    __parameter_input_metadata['WriteHeaderRow.Values'] = ["", "TRUE", "FALSE"]
    # WriteIndexColumn
    __parameter_input_metadata['WriteIndexColumn.Description'] = "write index column"
    __parameter_input_metadata['WriteIndexColumn.Label'] = "Write index column"
    __parameter_input_metadata['WriteIndexColumn.Tooltip'] = (
        "If TRUE, the Table's index column is included in the output delimited file. "
        "The index column header is an empty string.\n"
        "If FALSE, the Table's index column is not included in the output delimited file.")
    __parameter_input_metadata['WriteIndexColumn.Value.Default'] = "FALSE"
    __parameter_input_metadata['WriteIndexColumn.Values'] = ["", "TRUE", "FALSE"]
    # SortColumns
    __parameter_input_metadata['SortColumns.Description'] = "columns to sort data"
    __parameter_input_metadata['SortColumns.Label'] = "Sort columns"
    __parameter_input_metadata['SortColumns.Tooltip'] = (
        "The names of the Table columns, separated by columns, used to sort the order that the table records "
        "are written to the delimited file")
    __parameter_input_metadata['SortColumns.Value.Default'] = "the first table column"
    # SortOrder
    __parameter_input_metadata['SortOrder.Description'] = "sort order for columns"
    __parameter_input_metadata['SortOrder.Label'] = "Sort order"
    __parameter_input_metadata['SortOrder.Tooltip'] = (
        "The sort order for columns specified by SortColumns, using the syntax:\n\n"
        "SortColumn1:Ascending,SortColumn2:Descending\n\n"
        "As indicated in the above example, the sort order must be specified as one of "
        "the following: Ascending or Descending.")
    __parameter_input_metadata['SortOrder.Value.Default'] = "Ascending"
    # ArrayFormat
    __parameter_input_metadata['ArrayFormat.Description'] = "how column array values are written"
    __parameter_input_metadata['ArrayFormat.Label'] = "Array format"
    __parameter_input_metadata['ArrayFormat.Tooltip'] = (
        "If SquareBrackets, table column array values are written as a string with square brackets ([]) "
        "and comma delimiter.\n"
        "If CurlyBrackets, table column array values are written as a string with curly brackets ({}) "
        "and comma delimiter.")
    __parameter_input_metadata['ArrayFormat.Value.Default'] = "SquareBrackets"
    __parameter_input_metadata['ArrayFormat.Values'] = ["", "SqaureBrackets", "CurlyBrackets"]
    # NullValueFormat
    __parameter_input_metadata['NullValueFormat.Description'] = "specify how NONE values should be written"
    __parameter_input_metadata['NullValueFormat.Label'] = "Null value format"
    __parameter_input_metadata['NullValueFormat.Tooltip'] = (
        "If NULL, None items in table column array values are written as NULL. ex: '[NULL, 4, NULL]'\n"
        "If None, None items in table column array values are written as None. ex: '[None, 4, None]'")
    __parameter_input_metadata['NullValueFormat.Value.Default'] = "NULL"
    __parameter_input_metadata['NullValueFormat.Values'] = ["", "NULL", "None"]

    # Choices for parameters, used to validate parameter and display in editor
    __choices_ArrayFormat = ["SquareBrackets", "CurlyBrackets"]
    __choices_NullValueFormat = ["Null", "None"]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "WriteTableToDelimitedFile"
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

        warning = ""

        # Check that parameter TableID is a non-empty, non-None string.
        # noinspection PyPep8Naming
        pv_TableID = self.get_parameter_value(parameter_name='TableID', command_parameters=command_parameters)

        if not validator_util.validate_string(pv_TableID, False, False):
            message = "TableID parameter has no value."
            recommendation = "Specify the TableID parameter to indicate the Table to write."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that parameter OutputFile is a non-empty, non-None string.
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value(parameter_name='OutputFile', command_parameters=command_parameters)

        if not validator_util.validate_string(pv_OutputFile, False, False):
            message = "OutputFile parameter has no value."
            recommendation = "Specify the OutputFile parameter (relative or absolute pathname) to indicate the " \
                             "location and name of the output delimited file."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that the required parameters are valid Boolean values or None.
        parameters = ['WriteIndexColumn', 'WriteHeaderRow']

        for parameter in parameters:
            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)

            if not validator_util.validate_bool(parameter_value, True, False):
                message = "{} parameter ({}) is not a valid Boolean value.".format(parameter, parameter_value)
                recommendation = "Specify a valid Boolean value for the {} parameter.".format(parameter)
                warning += "\n" + message
                self.command_status.add_to_log(
                    CommandPhaseType.INITIALIZATION,
                    CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional parameter ArrayFormat is one of the acceptable values or is None.
        # noinspection PyPep8Naming
        pv_ArrayFormat = self.get_parameter_value(parameter_name="ArrayFormat", command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_ArrayFormat, self.__choices_ArrayFormat,
                                                      none_allowed=True,
                                                      empty_string_allowed=False, ignore_case=True):
            message = "ArrayFormat parameter value ({}) is not recognized.".format(pv_ArrayFormat)
            recommendation = "Specify one of the acceptable values ({}) for the ArrayFormat parameter.".format(
                self.__choices_ArrayFormat)
            warning += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional parameter NullValueFormat is one of the acceptable values or is None.
        # noinspection PyPep8Naming
        pv_NullValueFormat = self.get_parameter_value(parameter_name="NullValueFormat",
                                                      command_parameters=command_parameters)
        if not validator_util.validate_string_in_list(pv_NullValueFormat, self.__choices_NullValueFormat,
                                                      none_allowed=True, empty_string_allowed=False, ignore_case=True):
            message = "NullValueFormat parameter value ({}) is not recognized.".format(pv_NullValueFormat)
            recommendation = "Specify one of the acceptable values ({}) for the NullValueFormat parameter.".format(
                self.__choices_NullValueFormat)
            warning += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def __should_write_table(self, table_id: str, output_file_abs: str, delimiter: str, sort_columns: [str]) -> bool:
        """
       Checks the following:
       * the ID of the Table is an existing Table ID
       * the output folder is a valid folder
       * check that the delimiter is only one character
       * check that the columns within the SortColumns are existing columns

       Args:
           table_id: the ID of the Table to be written
           output_file_abs: the full pathname to the output file
           delimiter: the delimiter string that will separate each column in the output file
           sort_columns: a list of table columns used to sort the records

       Returns:
           run_write: Boolean. If TRUE, the writing process should be run. If FALSE, it should not be run.
       """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the Table ID is not an existing Table ID, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsTableIdExisting", "TableID", table_id, "FAIL"))

        # If the Table ID does exist and the sort_columns is not None, continue with checks.
        if True in should_run_command and sort_columns is not None:

            # Get the Table object
            table = self.command_processor.get_table(table_id)

            # Get a list of the columns in the table.
            columns = table.return_fieldnames()

            # If one of the SortingColumns does not exist in the Table, raise a FAILURE.
            invalid_columns = []
            for sort_column in sort_columns:
                if sort_column not in columns:
                    invalid_columns.append(sort_column)

            if invalid_columns:

                message = 'The SortColumns ({}) are not columns in the table ({}).'.format(invalid_columns, table_id)
                recommendation = 'Specify columns within the Table. \nValid columns: {}'.format(columns)

                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.FAILURE,
                                                                                      message, recommendation))
                should_run_command.append(False)

        # Get the full path to the output folder
        output_folder_abs = io_util.get_path(output_file_abs)

        # If the output folder is not an existing folder, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsFolderPathValid", "OutputFile", output_folder_abs,
                                                           "FAIL"))

        # If the delimiter is not 1 character, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsStringLengthCorrect", "Delimiter", delimiter,
                                                           "FAIL", other_values=[1]))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    @ staticmethod
    def __write_table_to_delimited_file(path: str, table_obj: Table, delimiter: str, cols_to_include_list: [str],
                                        cols_to_exclude_list: [str], include_header: bool, include_index: bool,
                                        sort_columns: [str], sorting_dic: dict, use_sq_brackets: bool,
                                        use_null_values: bool):
        """
        Writes a GeoProcessor table to a delimited file. There are many parameters to customize how the table is
        written to the delimited file.

        Args:
            path (str): the full pathname to the output file (can be an existing file or a new file). If it is
                existing, the file will be overwritten.
            table_obj (obj): the GeoProcessor Table to write
            delimiter (str): a single character delimiter to separate each column in the delimited file
            cols_to_include_list (list): a list of glob-style pattern strings used to select the columns to write
            cols_to_exclude_list (list): a list of glob-style pattern strings used to select the columns to NOT write
            include_header (boolean): boolean to determine if the header row should be written. If TRUE, the header
                row is written. If FALSE, the header row is not written.
            include_index (boolean): boolean to determine if the index column should be written. If TRUE, the index
                column is written. If FALSE, the index column is not written.
            sort_columns (list): the names of the columns to use to sort the table records
            sorting_dic (dic): a dictionary that relates each sorting column with the its corresponding order
                Available options: ASCENDING or DESCENDING
                Key: the name of the sorting column
                Value: the sorting order
            use_sq_brackets (boolean): boolean specifying the types of brackets to use around list/array data values.
                If TRUE, square brackets are used. If FALSE, curly brackets are used.
            use_null_values (boolean): boolean specifying if None values in arrays should be represented as None or as
                NULL. If TRUE, NULL is used. If FALSE, None is used.

        Return: None
        """

        # Get a list of the table's fieldnames.
        fieldnames = table_obj.return_fieldnames()

        # Get a list of the table's records. Each record is a list of data values.
        all_records = [table_record.items for table_record in table_obj.table_records]

        # Sort the records by the values of a field.
        # noinspection PyBroadException
        try:
            if sort_columns:

                for i in range(len(sort_columns)):

                    # Get the sort column.
                    sort_column = sort_columns[i]

                    # Get the column index.
                    index = fieldnames.index(sort_column)

                    # Get the appropriate sorting order.
                    if sort_column in list(sorting_dic.keys()):
                        sort_order = sorting_dic[sort_column]
                    else:
                        sort_order = "ASCENDING"

                    s = None
                    if sort_order.upper() == "ASCENDING" and i == 0:
                        s = sorted(all_records, key=itemgetter(index))
                    elif sort_order.upper() == "DESCENDING" and i == 0:
                        s = sorted(all_records, key=itemgetter(index), reverse=True)
                    elif sort_order.upper() == "ASCENDING":
                        s = sorted(s, key=itemgetter(index))
                    elif sort_order.upper() == "DESCENDING":
                        s = sorted(s, key=itemgetter(index), reverse=True)

                    all_records = s

            # If a sorting column is not specified, sort the records with the first column.
            else:

                # Sort the records in ascending order of the first table column.
                all_records = sorted(all_records, key=itemgetter(0))

        # Try to sort but do not throw an error if the sort fails. Instead keep the records in the original order.
        except Exception:
            all_records = all_records

        # If an index column is specified to be written, add the index column to each record.
        if include_index:

            # Iterate over each record and insert the record count as the first item in the record.
            for i in range(len(all_records)):
                all_records[i].insert(0, str(i))

        # If a header row is specified to be written, continue.
        if include_header:

            # If an index column is specified to be written, add an empty string to the first item of the header list.
            if include_index:
                fieldnames.insert(0, "")

            # Insert the header list (fieldnames) as the first item of the all_records list.
            all_records.insert(0, fieldnames)

        # Determine the fieldnames of the columns that should NOT be written to the delimited file.
        cols_to_remove = string_util.filter_list_of_strings(fieldnames, cols_to_include_list, cols_to_exclude_list,
                                                            return_inclusions=False)

        # If an index column is specifies to be written, make sure that the first column (the index column) is not
        # specified to be removed.
        if include_index:
            del cols_to_remove[0]

        # Get the indexes of the columns that should NOT be written to the delimited file.
        cols_to_remove_indexes = [fieldnames.index(col) for col in cols_to_remove]

        # Iterate over each record in the table.
        for record in all_records:

            # Iterate over each column index specified NOT to be written to the delimited file. Remove the record's
            # data value for each column specified NOT to be written to the delimited file.Must iterate over the
            # indexes in reverse to ensure that the proper values are removed.
            for index in sorted(cols_to_remove_indexes, reverse=True):
                del record[index]

        # Open the output delimited file. Can be an existing or a new file path.
        with open(path, "w") as f:

            # Write the records (one record for each row) to the output delimited file. Use the specified delimiter
            # character.
            writer = csv.writer(f, delimiter=delimiter, lineterminator='\n')
            writer.writerows(all_records)

        # If configured to use NULL values in an array instead of default None values, continue.
        if use_null_values:

            # A dictionary to store all of the strings that are to be replaced with different strings.
            # Key: the string within the delimited file to be replaced
            # Value: the replacement string
            replacement_dictionary = {}

            # Open the output delimited file.
            with open(path, "r") as f:

                # Iterate over each row of the output delimited file.
                reader = csv.reader(f, delimiter=delimiter)
                for row in reader:

                    # Iterate over each item in the row.
                    for item in row:

                        # If the item represents a list/array, continue.
                        if item.startswith("[") and item.endswith("]"):

                            # Remove the list/array brackets.
                            new_item = item.replace("[", "")
                            new_item = new_item.replace("]", "")

                            # Convert the string into a list.
                            items = new_item.split(",")

                            # The replacement list holds the values that will be used to replace the original array.
                            replacement_list = []

                            # Iterate over each item in the list/array.
                            for subitem in items:

                                # Remove leading and ending whitespaces from the item.
                                subitem = subitem.strip()

                                # If the item represents a None value, add a "NULL" string to the replacement_list.
                                if subitem.upper() == "NONE":
                                    replacement_list.append("NULL")

                                # If the item does not represent a None value, add the original value to the
                                # replacement_list.
                                else:
                                    replacement_list.append(str(subitem))

                            # Join the items in the replacement list back into a string. Add the brackets back.
                            replace_str = ",".join(replacement_list).join(("[", "]"))

                            # Add the replacement string to the master replacement dictionary.
                            replacement_dictionary[item] = replace_str

            # If there are items to replace, continue.
            if replacement_dictionary:

                # Open the output csv file and read the text in as a variable.
                with open(path, 'r') as f:
                    file_text = f.read()

                # Iterate over the characters to be replaced.
                for orig, new in replacement_dictionary.items():
                    # Replace the text variable with the correct character.
                    file_text = file_text.replace(orig, new)

                # Open the output csv file and overwrite the content with the updated text.
                with open(path, "w") as f:
                    f.write(file_text)

        # If specified to use curly brackets around array/list data values, continue.
        # Otherwise, the lists and arrays uses the default square brackets.
        if not use_sq_brackets:

            # A dictionary to store all of the strings that are to be replaced with different strings.
            # Key: the string within the delimited file to be replaced
            # Value: the replacement string
            replacement_dictionary = dict()

            # A dictionary to determine which characters are to be replaced (and their replacement characters).
            replacement_dictionary["["] = "{"
            replacement_dictionary["]"] = "}"

            # Open the output csv file and read the text in as a variable.
            with open(path, 'r') as f:
                file_text = f.read()

            # Iterate over the characters to be replaced.
            for orig, new in replacement_dictionary.items():
                # Replace the text variable with the correct character.
                file_text = file_text.replace(orig, new)

            # Open the output csv file and overwrite the content with the updated text.
            with open(path, "w") as f:
                f.write(file_text)

            # If there are items to replace, continue.
            if replacement_dictionary:

                # Open the output csv file and read the text in as a variable.
                with open(path, 'r') as f:
                    file_text = f.read()

                # Iterate over the characters to be replaced.
                for orig, new in replacement_dictionary.items():
                    # Replace the text variable with the correct character.
                    file_text = file_text.replace(orig, new)

                # Open the output csv file and overwrite the content with the updated text.
                with open(path, "w") as f:
                    f.write(file_text)

    def run_command(self) -> None:
        """
        Run the command. Write the Table to a delimited file.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_TableID = self.get_parameter_value("TableID")
        # noinspection PyPep8Naming
        pv_OutputFile = self.get_parameter_value("OutputFile")
        # noinspection PyPep8Naming
        pv_Delimiter = self.get_parameter_value("Delimiter", default_value=",")
        # noinspection PyPep8Naming
        pv_IncludeColumns = self.get_parameter_value("IncludeColumns", default_value="*")
        # noinspection PyPep8Naming
        pv_ExcludeColumns = self.get_parameter_value("ExcludeColumns", default_value="")
        # noinspection PyPep8Naming
        pv_WriteHeaderRow = self.get_parameter_value("WriteHeaderRow", default_value="True")
        # noinspection PyPep8Naming
        pv_WriteIndexColumn = self.get_parameter_value("WriteIndexColumn", default_value="False")
        # noinspection PyPep8Naming
        pv_SortColumns = self.get_parameter_value("SortColumns")
        # noinspection PyPep8Naming
        pv_SortOrder = self.get_parameter_value("SortOrder", default_value="")
        # noinspection PyPep8Naming
        pv_ArrayFormat = self.get_parameter_value("ArrayFormat", default_value="SquareBrackets")
        # noinspection PyPep8Naming
        pv_NullValueFormat = self.get_parameter_value("NullValueFormat", default_value="Null")

        # Convert the IncludeColumns, ExcludeColumns, and SortColumns parameter values to lists.
        cols_to_include = string_util.delimited_string_to_list(pv_IncludeColumns)
        cols_to_exclude = string_util.delimited_string_to_list(pv_ExcludeColumns)
        sort_cols_list = string_util.delimited_string_to_list(pv_SortColumns)

        # Convert the SortOrder to a dictionary.
        sort_dictionary = string_util.delimited_string_to_dictionary_one_value(pv_SortOrder, entry_delimiter=",",
                                                                               key_value_delimiter=":",
                                                                               trim=True)

        # Convert the OutputFile parameter value relative path to an absolute path and expand for ${Property} syntax
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        # Covert the Boolean parameters from string to Boolean values.
        # noinspection PyPep8Naming
        pv_WriteHeaderRow = string_util.str_to_bool(pv_WriteHeaderRow)
        # noinspection PyPep8Naming
        pv_WriteIndexColumn = string_util.str_to_bool(pv_WriteIndexColumn)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_write_table(pv_TableID, output_file_absolute, pv_Delimiter, sort_cols_list):

            # noinspection PyBroadException
            try:

                # Get the Table object
                table = self.command_processor.get_table(pv_TableID)

                # Determine if square brackets should be used depending on the user input of the ArrayFormat parameter.
                use_sq_brackets = False
                if pv_ArrayFormat.upper() == "SQUAREBRACKETS":
                    use_sq_brackets = True

                # Determine if the null values should be used depending on the user input of the NullValueFormat
                # parameter.
                use_null_value = False
                if pv_NullValueFormat.upper() == "NULL":
                    use_null_value = True

                # Write the table to the delimited file.
                self.__write_table_to_delimited_file(output_file_absolute, table, pv_Delimiter, cols_to_include,
                                                     cols_to_exclude, pv_WriteHeaderRow, pv_WriteIndexColumn,
                                                     sort_cols_list, sort_dictionary, use_sq_brackets, use_null_value)

            # Raise an exception if an unexpected error occurs during the process
            except Exception:
                self.warning_count += 1
                message = "Unexpected error writing Table {} to delimited file {}.".format(pv_TableID,
                                                                                           pv_OutputFile)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
