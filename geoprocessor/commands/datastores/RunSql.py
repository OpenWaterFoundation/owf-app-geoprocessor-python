# RunSql - command to run an SQL statement on a datastore
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

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validator_util

import logging


class RunSql(AbstractCommand):
    """
    Executes a Structured Query Language (SQL) statement on a DataStore.

    Command Parameters
    * DataStoreID (str, required): the DataStore identifier to run the SQL statement on.  ${Property} notation enabled.
    * Sql (str, optional): The SQL statement text that will be executed, optionally using ${Property} notation to
        insert processor property values. If specified, do not specify SqlFile or DataStoreProcedure.
    * SqlFile (str, optional): The name of the file containing an SQL statement to execute, optionally using
        ${Property} notation in the SQL file contents to insert processor property values. If specified,
        do not specify Sql or DataStoreProcedure.
    * DataStoreProcedure (str, optional): The name of the database procedure to run. Currently, only procedures that
        do not require parameters can be run. If specified, do not specify Sql or SqlFile.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("DataStoreID", type("")),
        CommandParameterMetadata("Sql", type("")),
        CommandParameterMetadata("SqlFile", type("")),
        CommandParameterMetadata("DataStoreProcedure", type(""))]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "RunSql"
        self.command_parameter_metadata = self.__command_parameter_metadata

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

        # Check that the DataStoreID is a non-empty, non-None string.
        # noinspection PyPep8Naming
        pv_DataStoreID = self.get_parameter_value(parameter_name="DataStoreID", command_parameters=command_parameters)

        if not validator_util.validate_string(pv_DataStoreID, False, False):
            message = "DataStoreID parameter has no value."
            recommendation = "Specify a valid DataStore ID."
            warning += "\n" + message
            self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that one (and only one) sql method is a non-empty and non-None string.
        is_string_list = []
        sql_method_parameter_list = ["Sql", "SqlFile", "DataStoreProcedure"]

        for parameter in sql_method_parameter_list:
            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)
            is_string_list.append(validator_util.validate_string(parameter_value, False, False))

        if not is_string_list.count(True) == 1:
            message = "Must enable one (and ONLY one) of the following parameters: {}".format(sql_method_parameter_list)
            recommendation = "Specify the value for one (and ONLY one) of the following parameters: {}".format(
                sql_method_parameter_list)
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # TEMPORARY CHECK: Check that the DataStoreProcedure method is not being used. Currently disabled until future
        # development. Once developed, this check can be removed.
        else:
            # noinspection PyPep8Naming
            pv_DataStoreProcedure = self.get_parameter_value(parameter_name="DataStoreProcedure",
                                                             command_parameters=command_parameters)

            if validator_util.validate_string(pv_DataStoreProcedure, none_allowed=False, empty_string_allowed=False):
                message = "DataStoreProcedure is not currently enabled."
                recommendation = "Specify the Sql method or the SqlFile method. "
                warning += "\n" + message
                self.command_status.add_to_log(
                    CommandPhaseType.INITIALIZATION,
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

    def __should_run_sql(self, datastore_id: str) -> bool:
        """
        Checks the following:
            * the DataStore ID is an existing DataStore ID

        Args:
            datastore_id (str): the ID of the DataStore to close

        Returns:
             Boolean. If TRUE, the  process should be run. If FALSE, it should not be run.
       """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = list()

        # If the DataStore ID is not an existing DataStore ID, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsDataStoreIdExisting", "DataStoreID", datastore_id,
                                                           "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Execute the Sql statement on the DataStore.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values. The DatabasePort parameter value will be obtained later in the code.
        # noinspection PyPep8Naming
        pv_DataStoreID = self.get_parameter_value("DataStoreID")
        # noinspection PyPep8Naming
        pv_Sql = self.get_parameter_value("Sql")
        # noinspection PyPep8Naming
        pv_SqlFile = self.get_parameter_value("SqlFile")
        # TODO smalers 2020-01-15 need to enable procedures similar to Java
        # noinspection PyPep8Naming
        # pv_DataStoreProcedure = self.get_parameter_value("DataStoreProcedure")

        # Expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_DataStoreID = self.command_processor.expand_parameter_value(pv_DataStoreID, self)
        # noinspection PyPep8Naming
        pv_Sql = self.command_processor.expand_parameter_value(pv_Sql, self)
        if pv_SqlFile:
            # noinspection PyPep8Naming
            pv_SqlFile = io_util.verify_path_for_os(io_util.to_absolute_path(
                                                    self.command_processor.get_property('WorkingDir'),
                                                    self.command_processor.expand_parameter_value(pv_SqlFile, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_run_sql(pv_DataStoreID):
            # noinspection PyBroadException
            try:

                # Get the DataStore object
                datastore_obj = self.command_processor.get_datastore(pv_DataStoreID)

                # If using the Sql method, the sql_statement is the user-provided sql statement.
                if pv_Sql:
                    sql_statement = pv_Sql

                # If using the SqlFile method, the sql_statement in read from the provided file.
                elif pv_SqlFile:

                    # Get the SQL statement from the file.
                    f = open(pv_SqlFile, 'r')
                    sql_statement = f.read().strip()

                # If using the DataStoreProcedure method, ... .
                else:
                    sql_statement = None

                # Execute and commit the SQL statement.
                datastore_obj.run_sql(sql_statement)

            # Raise an exception if an unexpected error occurs during the process
            except Exception:
                self.warning_count += 1
                message = "Unexpected error executing the Sql statement on the {} DataStore.".format(pv_DataStoreID)
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
