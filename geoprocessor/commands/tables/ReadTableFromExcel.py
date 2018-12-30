# ReadTableFromExcel - command to read a table from an Excel worksheet
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2019 Open Water Foundation
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
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.Table_pandas import Table

import geoprocessor.util.command_util as command_util
import geoprocessor.util.pandas_util as pandas_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validators

import logging


class ReadTableFromExcel(AbstractCommand):

    """
    Reads a Table from an Excel file.

    This command reads a tables from an Excel file and creates a Table object within the geoprocessor. The Table can
    then be accessed in the geoprocessor by its identifier and further processed.

    Command Parameters
    * InputFile (str, required): the relative pathname to the excel data file (known as a workbook)
    * Worksheet (str, optional): the name of the worksheet to read. Default: the first worksheet is read.
    * TableID (str, optional): the Table identifier. Default: the Worksheet's name.
    * IfTableIDExists (str, optional): This parameter determines the action that occurs if the TableID already exists
        within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail` 
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("InputFile", type("")),
        CommandParameterMetadata("Worksheet", type("")),
        CommandParameterMetadata("TableID", type("")),
        CommandParameterMetadata("IfTableIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "ReadTableFromExcel"
        self.command_description = "Read a table from an Excel file"
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
        # - existence of the file will also be checked in run_command().
        pv_InputFile = self.get_parameter_value(parameter_name='InputFile', command_parameters=command_parameters)

        if not validators.validate_string(pv_InputFile, False, False):

            message = "InputFile parameter has no value."
            recommendation = "Specify the InputFile parameter to indicate the input Excel data file."
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

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def __should_read_table(self, file_abs, sheet_name, table_id):

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

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the input file is not a valid file path, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsFilePathValid", "InputFile", file_abs, "FAIL"))

        # If the input file is valid, continue with the checks.
        if False not in should_run_command:

            # If the Worksheet parameter is None, assign it with the name of the first worksheet in the excel file.
            if sheet_name is None:
                sheet_name = pandas_util.create_excel_workbook_obj(file_abs).sheet_names[0]

            # If the input sheet name is not a valid sheet name in the excel workbook file, raise a FAILURE.
            should_run_command.append(validators.run_check(self, "IsExcelSheetNameValid", "Worksheet", sheet_name,
                                                           "FAIL", other_values=[file_abs]))

            # If the TableID parameter is None, assign the parameter with the sheet name.
            if table_id is None:
                table_id = sheet_name

            # If the TableID is the same as an already-existing TableID, raise a WARNING or FAILURE (depends on the
            # value of the IfTableIDExists parameter.)
            should_run_command.append(validators.run_check(self, "IsTableIdUnique", "TableID", table_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self):
        """
        Run the command. Read the tabular data from the Excel workbook/worksheet. Create a Table object, and add to the
        GeoProcessor's tables list.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_InputFile = self.get_parameter_value("InputFile")
        pv_Worksheet = self.get_parameter_value("Worksheet")
        pv_TableID = self.get_parameter_value("TableID")

        # Convert the InputFile parameter value relative path to an absolute path and expand for ${Property} syntax.
        file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_InputFile, self)))

        # If the pv_TableID is a valid %-formatter, assign the pv_GeoLayerID the corresponding value.
        if pv_TableID in ['%f', '%F', '%E', '%P', '%p']:
            pv_TableID = io_util.expand_formatter(file_absolute, pv_TableID)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_read_table(file_absolute, pv_Worksheet, pv_TableID):

            try:

                # Assign the Worksheet parameter to the name of the first Excel worksheet, if it was not specified.
                if pv_Worksheet is None:
                    pv_Worksheet = pandas_util.create_excel_workbook_obj(file_absolute).sheet_names[0]

                # Assign the TableID parameter to the name of the first Excel worksheet, if it was not specified.
                if pv_TableID is None:
                    pv_TableID = pv_Worksheet

                # Create a Pandas Data Frame object.
                df = pandas_util.create_data_frame_from_excel(file_absolute, pv_Worksheet)

                # Create a Table and add it to the geoprocessor's Tables list.
                table_obj = Table(pv_TableID, df, file_absolute)
                self.command_processor.add_table(table_obj)

            # Raise an exception if an unexpected error occurs during the process.
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error reading Table {} from Excel file {}.".format(pv_TableID, pv_InputFile)
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
