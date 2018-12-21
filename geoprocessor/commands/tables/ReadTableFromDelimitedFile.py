# ReadTableFromDelimitedFile

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.Table import Table
from geoprocessor.core.Table import TableRecord
from geoprocessor.core.Table import TableField

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validators

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
    __command_parameter_metadata = [
        CommandParameterMetadata("InputFile", type("")),
        CommandParameterMetadata("Delimiter", type("")),
        CommandParameterMetadata("TableID", type("")),
        CommandParameterMetadata("HeaderLines", type("")),
        CommandParameterMetadata("NullValues", type("")),
        CommandParameterMetadata("IfTableIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "ReadTableFromDelimitedFile"
        self.command_description = "Read a table from a delimited file"
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

        # Check that parameter InputFile is a non-empty, non-None string.
        pv_InputFile = self.get_parameter_value(parameter_name='InputFile', command_parameters=command_parameters)

        if not validators.validate_string(pv_InputFile, False, False):
            message = "InputFile parameter has no value."
            recommendation = "Specify the InputFile parameter (relative or absolute pathname) to indicate the " \
                             "location and name of the output Excel file."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))
            
        # Check that parameter TableID is a non-empty, non-None string.
        pv_TableID = self.get_parameter_value(parameter_name='TableID', command_parameters=command_parameters)

        if not validators.validate_string(pv_TableID, False, False):
            message = "TableID parameter has no value."
            recommendation = "Specify the TableID parameter."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that optional parameter IfTableIDExists is either `Replace`, `ReplaceAndWarn`, `Warn`, `Fail`, None.
        pv_IfTableIDExists = self.get_parameter_value(parameter_name="IfTableIDExists",
                                                      command_parameters=command_parameters)
        acceptable_values = ["Replace", "ReplaceAndWarn", "Warn", "Fail"]
        if not validators.validate_string_in_list(pv_IfTableIDExists, acceptable_values, none_allowed=True,
                                                  empty_string_allowed=True, ignore_case=True):
            message = "IfTableIDExists parameter value ({}) is not recognized.".format(pv_IfTableIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfTableIDExists parameter.".format(
                acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # If the HeaderLines is used, continue with the checks.
        pv_HeaderLines = self.get_parameter_value("HeaderLines", command_parameters=command_parameters)
        if pv_HeaderLines:

            # Check that the HeaderLines parameter is an integer or None.
            if not validators.validate_int(pv_HeaderLines, True, False):

                message = "HeaderLines parameter value ({}) is not a valid integer value.".format(pv_HeaderLines)
                recommendation = "Specify a positive integer for the HeaderLines parameter to specify how" \
                                 " many rows represent the header contnet of the delimited file."
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

    def __should_read_table(self, input_file_abs, table_id):
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
        should_run_command = []

        # If the input file is not a valid file path, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsFilePathValid", "InputFile", input_file_abs, "FAIL"))

        # If the TableID is the same as an already-existing TableID, raise a WARNING or FAILURE (depends on the
        # value of the IfTableIDExists parameter.)
        should_run_command.append(validators.run_check(self, "IsTableIdUnique", "TableID", table_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    @staticmethod
    def __read_table_from_delimited_file(path, table_id, delimiter, header_count, null_values):
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

    def run_command(self):
        """
        Run the command. Read the Table from the delimited file.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_InputFile = self.get_parameter_value("InputFile")
        pv_Delimiter = self.get_parameter_value("Delimiter", default_value=",")
        pv_TableID = self.get_parameter_value("TableID")
        pv_HeaderLines = int(self.get_parameter_value("HeaderLines", default_value="0"))
        pv_NullValues = self.get_parameter_value("NullValues", default_value="''")

        # Convert the InputFile parameter value relative path to an absolute path and expand for ${Property} syntax
        input_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_InputFile, self)))

        # Convert the NullValues parameter values to a list.
        pv_NullValues = string_util.delimited_string_to_list(pv_NullValues)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_read_table(input_file_absolute, pv_TableID):

            try:

                # Create the table from the delimited file.
                table = self.__read_table_from_delimited_file(input_file_absolute, pv_TableID, pv_Delimiter,
                                                              pv_HeaderLines, pv_NullValues)

                # Add the table to the GeoProcessor's Tables list.
                self.command_processor.add_table(table)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error reading Table {} from delimited file ({}).".format(pv_TableID,
                                                                                               input_file_absolute)
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
