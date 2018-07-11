# WriteTableToDelimitedFile

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validators

import csv
import logging
from operator import itemgetter


class WriteTableToDelimitedFile(AbstractCommand):
    """
    Writes a Table to an delimiter-separated file.

    Command Parameters
    * TableID (str, required): the identifier of the Table to be written to the delimited file
    * OutputFile (str, required): the relative pathname of the output delimited file.
    * Delimiter (str, optional): the delimiter of the output file. Default is `,` Must be a one-character
        string (limitation is built into the Pandas to_csv command).
    * ColumnsToInclude (str, optional): A list of glob-style patterns to determine the table columns to include in the
        output delimited file. Default: * (All columns are written).
    * ColumnsToExclude (str, optional): A list of glob-style patterns to determine the table columns to exclude in the
        output delimited file. Default: Default: '' (No columns are excluded from the output delimited file).
    * WriteHeaderRow (bool, optional): If TRUE, the header row is written, If FALSE, the header row is excluded.
        Default: True
    * WriteIndexColumn (bool, optional): If TRUE, the index column is written, If FALSE, the index column is excluded.
        Default: True
    * SortingColumn (str, optional): The name of the Table column used to sort the order that the table records are
        written to the delimited file. Default: The first Table column.
    * SortingOrder(str, optional): The order to sort the records based on the values of the SortingColumn.
        The available options are: Ascending, Descending. Default: Ascending
    * UseSquareBrackets (str, optional): If TRUE, table column array values are written as a string with square
        brackets. If FALSE, table column array values are written as a string with curly brackets. Default: True
    * UseNullValue (str, optional): If TRIE, table column array values with None items are changed to NULL. If FALSE,
        table column array values with None items remain None. Default: True
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("TableID", type("")),
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("Delimiter", type("")),
        CommandParameterMetadata("ColumnsToInclude", type("")),
        CommandParameterMetadata("ColumnsToExclude", type("")),
        CommandParameterMetadata("WriteHeaderRow", type("")),
        CommandParameterMetadata("WriteIndexColumn", type("")),
        CommandParameterMetadata("SortingColumn", type("")),
        CommandParameterMetadata("SortingOrder", type("")),
        CommandParameterMetadata("UseSquareBrackets", type("")),
        CommandParameterMetadata("UseNullValue", type(""))]

    # Choices for SortingOrder, used to validate parameter and display in editor
    __choices_SortingOrder = ["Ascending", "Descending"]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "WriteTableToDelimitedFile"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Class data
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

        warning = ""

        # Check that parameter TableID is a non-empty, non-None string.
        pv_TableID = self.get_parameter_value(parameter_name='TableID', command_parameters=command_parameters)

        if not validators.validate_string(pv_TableID, False, False):
            message = "TableID parameter has no value."
            recommendation = "Specify the TableID parameter to indicate the Table to write."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that parameter OutputFile is a non-empty, non-None string.
        pv_OutputFile = self.get_parameter_value(parameter_name='OutputFile', command_parameters=command_parameters)

        if not validators.validate_string(pv_OutputFile, False, False):
            message = "OutputFile parameter has no value."
            recommendation = "Specify the OutputFile parameter (relative or absolute pathname) to indicate the " \
                             "location and name of the output delimited file."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that the required parameters are valid Boolean values or None.
        parameters = ['WriteIndexColumn', 'WriteHeaderRow', 'UseSquareBrackets', 'UseNullValue']

        for parameter in parameters:
            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)

            if not validators.validate_bool(parameter_value, True, False):
                message = "{} parameter ({}) is not a valid Boolean value.".format(parameter, parameter_value)
                recommendation = "Specify a valid Boolean value for the {} parameter.".format(parameter)
                warning += "\n" + message
                self.command_status.add_to_log(
                    command_phase_type.INITIALIZATION,
                    CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that optional parameter SortingOrder is one of the acceptable values or is None.
        pv_SortingOrder = self.get_parameter_value(parameter_name="SortingOrder", command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_SortingOrder, self.__choices_SortingOrder,
                                                  none_allowed=True,
                                                  empty_string_allowed=False, ignore_case=True):
            message = "SortingOrder parameter value ({}) is not recognized.".format(pv_SortingOrder)
            recommendation = "Specify one of the acceptable values ({}) for the SortingOrder parameter.".format(
                self.__choices_SortingOrder)
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def __should_write_table(self, table_id, output_file_abs, delimiter, sorting_column):
        """
       Checks the following:
       * the ID of the Table is an existing Table ID
       * the output folder is a valid folder
       * check that the delimiter is only one character
       * check that the SortingColumn is an existing column

       Args:
           table_id: the ID of the Table to be written
           output_file_abs: the full pathname to the output file
           delimiter: the delimiter string that will separate each column in the output file
           sorting_col: the table column used to sort the records

       Returns:
           run_write: Boolean. If TRUE, the writing process should be run. If FALSE, it should not be run.
       """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the Table ID is not an existing Table ID, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsTableIdExisting", "TableID", table_id, "FAIL"))

        # If the Table ID does exist and the sorting_column is not None, continue with checks.
        if True in should_run_command and sorting_column is not None:

            # Get the Table object
            table = self.command_processor.get_table(table_id)

            # Get a list of the columns in the table.
            columns = table.return_fieldnames()

            # If the SortingColumn does not exist in the Table, raise a FAILURE.
            if sorting_column not in columns:

                message = 'The SortingColumn ({}) is not a column in the table ({}).'.format(sorting_column, table_id)
                recommendation = 'Specify a column within the Table. \n Existing columns: {}'.format(columns)

                self.warning_count += 1
                self.logger.error(message)
                self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                            message, recommendation))
                should_run_command.append(False)

        # Get the full path to the output folder
        output_folder_abs = io_util.get_path(output_file_abs)

        # If the output folder is not an existing folder, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsFolderPathValid", "OutputFile", output_folder_abs,
                                                       "FAIL"))

        # If the delimiter is not 1 character, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsStringLengthCorrect", "Delimiter", delimiter,
                                                       "FAIL", other_values=[1]))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    @ staticmethod
    def __write_table_to_delimited_file(path, table_obj, delimiter, cols_to_include_list, cols_to_exclude_list,
                                        include_header, include_index, sorting_column, sort_order, use_sq_brackets,
                                        use_null_values):
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
            sorting_column (str): the name of the column to use to sort the table records
            sort_order (str): the order that the records are sorted. Available options: ASCENDING or DESCENDING
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
        try:
            # If a sorting column is specified, sort the records with the data values from the specified column.
            # Get the index of the sorting column.
            if sorting_column:
                index = fieldnames.index(sorting_column)

            # If a sorting column is not specified, sort the records with the first column.
            else:
                index = 0

            # If the sorting order is ascending, then sort the records in ascending order of the sorting column.
            if sort_order.upper() == "ASCENDING":
                all_records = sorted(all_records, key=itemgetter(index))

            # If the sorting order is descending, then sort the records in descending order of the sorting column.
            else:
                all_records = sorted(all_records, key=itemgetter(index), reverse=True)

        # Try to sort but do not throw an error if the sort fails. Instead keep the records in the original order.
        except:
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
            replacement_dictionary = {}

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

    def run_command(self):
        """
        Run the command. Write the Table to a delimited file.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_TableID = self.get_parameter_value("TableID")
        pv_OutputFile = self.get_parameter_value("OutputFile")
        pv_Delimiter = self.get_parameter_value("Delimiter", default_value=",")
        pv_ColumnsToInclude = self.get_parameter_value("ColumnsToInclude", default_value="*")
        pv_ColumnsToExclude = self.get_parameter_value("ColumnsToExclude", default_value="")
        pv_WriteHeaderRow = self.get_parameter_value("WriteHeaderRow", default_value="True")
        pv_WriteIndexColumn = self.get_parameter_value("WriteIndexColumn", default_value="True")
        pv_SortingColumn = self.get_parameter_value("SortingColumn")
        pv_SortingOrder = self.get_parameter_value("SortingOrder", default_value="Ascending")
        pv_UseSquareBrackets = self.get_parameter_value("UseSquareBrackets", default_value="True")
        pv_UseNullValue = self.get_parameter_value("UseNullValue", default_value="True")

        # Convert the ColumnsToInclude and ColumnsToExclude parameter values to lists.
        cols_to_include = string_util.delimited_string_to_list(pv_ColumnsToInclude)
        cols_to_exclude = string_util.delimited_string_to_list(pv_ColumnsToExclude)

        # Convert the OutputFile parameter value relative path to an absolute path and expand for ${Property} syntax
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        # Covert the Boolean parameters from string to Boolean values.
        pv_WriteHeaderRow = string_util.str_to_bool(pv_WriteHeaderRow)
        pv_WriteIndexColumn = string_util.str_to_bool(pv_WriteIndexColumn)
        pv_UseSquareBrackets = string_util.str_to_bool(pv_UseSquareBrackets)
        pv_UseNullValue = string_util.str_to_bool(pv_UseNullValue)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_write_table(pv_TableID, output_file_absolute, pv_Delimiter, pv_SortingColumn):

            try:

                # Get the Table object
                table = self.command_processor.get_table(pv_TableID)

                # Write the table to the delimited file.
                self.__write_table_to_delimited_file(output_file_absolute, table, pv_Delimiter, cols_to_include,
                                                     cols_to_exclude, pv_WriteHeaderRow, pv_WriteIndexColumn,
                                                     pv_SortingColumn, pv_SortingOrder, pv_UseSquareBrackets,
                                                     pv_UseNullValue)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error writing Table {} to delimited file {}.".format(pv_TableID,
                                                                                                pv_OutputFile)
                recommendation = "Check the log file for details."
                self.logger.error(message, exc_info=True)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
