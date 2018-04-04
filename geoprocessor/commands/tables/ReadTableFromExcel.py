# ReadTableFromExcel

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.Table import Table

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
    * File (str, required): the relative pathname to the excel data file (known as a workbook)
    * SheetName (str, optional): the name of the worksheet to read. Default: the first worksheet is read. 
    * TableID (str, optional): the Table identifier. Default: the SheetName. 
    * IfTableIDExists (str, optional): This parameter determines the action that occurs if the TableID already exists
        within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail` 
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("File", type("")),
        CommandParameterMetadata("SheetName", type("")),
        CommandParameterMetadata("TableID", type("")),
        CommandParameterMetadata("IfTableIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super(ReadTableFromExcel, self).__init__()
        self.command_name = "ReadTableFromExcel"
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

        # Check that parameter File is a non-empty, non-None string.
        # - existence of the file will also be checked in run_command().
        pv_File = self.get_parameter_value(parameter_name='File', command_parameters=command_parameters)

        if not validators.validate_string(pv_File, False, False):

            message = "File parameter has no value."
            recommendation = "Specify the File parameter to indicate the input Excel data file."
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

    def __should_read_geolayer(self, file_abs, sheet_name, table_id):

        """
        Checks the following:
        * the File (absolute) is a valid file
        * the SheetName is a valid sheet in the Excel workbook
        * the ID of the Table is unique (not an existing Table ID)

        Args:
            file_abs (str): the full pathname to the input data file (Excel workbook)
            sheet_name (str): the name of the Excel worksheet to read
            table_id (str): the ID of the output Table

        Returns:
            run_read: Boolean. If TRUE, the read process should be run. If FALSE, the read process should not be run.
        """

        # TODO fill out the checks/validators
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
        pv_File = self.get_parameter_value("File")
        pv_SheetName = self.get_parameter_value("SheetName")
        pv_TableID = self.get_parameter_value("TableID")

        # Convert the File parameter value relative path to an absolute path and expand for ${Property} syntax.
        file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_File, self)))

        # If the pv_TableID is a valid %-formatter, assign the pv_GeoLayerID the corresponding value.
        if pv_TableID in ['%f', '%F', '%E', '%P', '%p']:
            pv_TableID = io_util.expand_formatter(file_absolute, pv_TableID)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_read_geolayer(file_absolute, pv_SheetName, pv_TableID):

            try:

                # Assign the SheetName parameter to the name of the first Excel worksheet, if it was not specified.
                if pv_SheetName is None:
                    pv_SheetName = pandas_util.create_excel_workbook_obj(file_absolute).sheet_names[0]

                    # Assign the TableID parameter to the name of the first Excel worksheet, if it was not specified.
                    if pv_TableID is None:
                        pv_TableID = pv_SheetName

                # Create a Pandas Data Frame object.
                df = pandas_util.create_data_frame_from_excel(file_absolute, pv_SheetName)

                # Create a Table and add it to the geoprocessor's Tables list.
                table_obj = Table(pv_TableID, df, file_absolute)
                self.command_processor.add_table(table_obj)

            # Raise an exception if an unexpected error occurs during the process.
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error reading Table {} from Excel file {}.".format(pv_TableID, pv_File)
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
