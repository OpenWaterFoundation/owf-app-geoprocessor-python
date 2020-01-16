# CloseDataStore - command to close a datastore
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
import geoprocessor.util.validator_util as validator_util

import logging


class CloseDataStore(AbstractCommand):
    """
    Close an existing open database connection.

    Command Parameters
    * DataStoreID (str, required): the DataStore identifier of the DataStore to close. ${Property} syntax enabled.
    * StatusMessage (str, optional): A status message to display when the DataStore information is viewed.
        The status may be reset if the connection is automatically restored, for example when a subsequent database
        interaction occurs. Default: "Not connected. Connection has been closed." ${Property} syntax enabled.
        Note that this is a placeholder parameter ported over from the TSTool command (CloseDataStore). It currently
        has no effect of the GeoProcessor environment. In future development this message could be hooked into the
        log or the UI.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("DataStoreID", type("")),
        CommandParameterMetadata("StatusMessage", type(""))]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        # Name of command for menu and window title
        self.command_name = "CloseDataStore"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = "This command closes a DataStore connection."
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # DataStoreID
        self.parameter_input_metadata['DataStoreID.Description'] = "the identifier of the DataStore to close"
        self.parameter_input_metadata['DataStoreID.Label'] = "DataStoreID"
        self.parameter_input_metadata['DataStoreID.Required'] = True
        self.parameter_input_metadata['DataStoreID.Tooltip'] = \
            "The ID of the DataStore to close. Can be specified using ${Property}."
        # StatusMessage
        self.parameter_input_metadata['StatusMessage.Description'] = "a status message to display"
        self.parameter_input_metadata['StatusMessage.Label'] = "Status Message"
        self.parameter_input_metadata['StatusMessage.Tooltip'] = \
            "A status message to display when the datastore information is viewed.\nThe status may be reset if the " \
            "connection is automatically restored, for example when a subsequent database interaction occurs.\n" \
            "Can be specified using ${Property}."
        self.parameter_input_metadata['StatusMessage.Value.Default'] = "DataStore [DataStoreID] has been closed"

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
        pv_DataStoreID = self.get_parameter_value(parameter_name="DataStoreID",
                                                  command_parameters=command_parameters)

        if not validator_util.validate_string(pv_DataStoreID, False, False):
            message = "DataStoreID parameter has no value."
            recommendation = "Specify a valid DataStore ID."
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

    def __should_close_datastore(self, datastore_id: str) -> bool:
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
        should_run_command.append(validator_util.run_check(
            self, "IsDataStoreIdExisting", "DataStoreID", datastore_id, "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self) -> None:
        """
        Run the command. Close an existing DataStore and remove it from the GeoProcessor.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the DataStoreID parameter value and expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_DataStoreID = self.get_parameter_value("DataStoreID")
        # noinspection PyPep8Naming
        pv_DataStoreID = self.command_processor.expand_parameter_value(pv_DataStoreID, self)

        # Obtain the StatusMessage parameter value and expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_StatusMessage = self.get_parameter_value("StatusMessage")
        # noinspection PyPep8Naming
        pv_StatusMessage = self.command_processor.expand_parameter_value(pv_StatusMessage, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_close_datastore(pv_DataStoreID):

            # noinspection PyBroadException
            try:

                # Get the DataStore object
                datastore_obj = self.command_processor.get_datastore(pv_DataStoreID)

                # Close the database connection.
                datastore_obj.close_db_connection()

                # Update the DataStore's status message.
                datastore_obj.update_status_message(pv_StatusMessage)

            # Raise an exception if an unexpected error occurs during the process
            except Exception:
                self.warning_count += 1
                message = "Unexpected error closing DataStore {}.".format(pv_DataStoreID)
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
