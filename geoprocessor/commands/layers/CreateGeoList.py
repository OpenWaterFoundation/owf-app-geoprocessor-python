# CreateGeoList command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.GeoListMetadata import GeoListMetadata

import geoprocessor.util.command as command_util
import geoprocessor.util.geo as geo_util
import geoprocessor.util.validators as validators

import logging


# Inherit from AbstractCommand
class CreateGeoList(AbstractCommand):

    """Creates a GeoList within the geoprocessor.

    A GeoList is a collection of registered GeoLayers. GeoLists are useful when iterating over a group of GeoLayers in
    a for loop. This command takes a list of GeoLayer ids and GeoList ids and adds all of the relevant GeoLayer ids to
    the GeoList.

    If the item in the GeoIdList is a GeoLayer id, then that GeoLayer id is added to the newly created GeoList.
    If the item in the GeoIdList is a GeoList id, then all of the GeoLayer ids within that GeoList are added to the
    newly created GeoList.

    Args:
        GeoIdList (list): a list of registered GeoLayer ids and registered GeoList ids. The related GeoLayers will be
        included in the newly-created GeoList (explained above).
        GeoListId (str): a unique id that will be used to identify the GeoList"""

    def __init__(self):
        """Initialize the command"""

        super(CreateGeoList, self).__init__()
        self.command_name = "CreateGeoList"
        self.command_parameter_metadata = [
            CommandParameterMetadata("GeoIdList", type([])),
            CommandParameterMetadata("GeoListId", type("")),
            CommandParameterMetadata("CommandStatus", type(""))
        ]

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            Nothing.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """

        warning = ""
        logger = logging.getLogger(__name__)

        # Check that parameter GeoIdList is a non-empty, non-None string.
        pv_GeoIdList = self.get_parameter_value(parameter_name='GeoIdList', command_parameters=command_parameters)
        if not validators.validate_string(pv_GeoIdList, False, False):
            message = "GeoIdList parameter has no value."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify text for the GeoIdList parameter."))
            logger.warning(warning)

        # Check that parameter GeoIdList is a string that can be converted into a list.
        if not validators.validate_list(pv_GeoIdList, False, False):
            message = "GeoIdList parameter is not a valid list."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify list for the GeoIdList parameter."))
            logger.warning(warning)

        # Check that parameter GeoListId is a non-empty, non-None string.
        pv_GeoListId = self.get_parameter_value(parameter_name='GeoListId', command_parameters=command_parameters)
        if not validators.validate_string(pv_GeoListId, False, False):
            message = "GeoListId parameter has no value."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify text for the GeoListId parameter."))
            logger.warning(warning)

        # Check that parameter CommandStatus is one of the valid Command Status Types.
        pv_CommandStatus = self.get_parameter_value(parameter_name='CommandStatus',
                                                    command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_CommandStatus,
                                                  command_status_type.get_command_status_types(), True, True):
            message = 'The requested command status "' + pv_CommandStatus + '"" is invalid.'
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify a valid command status."))
            logger.warning(warning)

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception
        if len(warning) > 0:
            logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def run_command(self):
        """
        Run the command. Create a GeoList and register it in the GeoProcessor. Print the message to the log file.

        Returns:
            Nothing
        """
        logger = logging.getLogger(__name__)
        warning_count = 0

        # Get the GeoIdList in string format. Convert the GeoIdList parameter value to list format.
        pv_GeoIdList = self.get_parameter_value("GeoIdList")
        pv_GeoIdList = command_util.to_correct_format(pv_GeoIdList)

        # Get the GeoListId in string format.
        pv_GeoListId = self.get_parameter_value("GeoListId")

        # A list that will hold the id of each GeoLayer to be included in the newly create GeoList.
        list_of_GeoLayers_to_include = []

        # Iterate through the user-defined GeoIds (can be GeoLayer or GeoList id).
        for GeoId in pv_GeoIdList:

            # If the id is a GeoLayer id, add that GeoLayer id to the list_of_GeoLayers_to_include list.
            if geo_util.is_geolayer_id(self, GeoId):

                list_of_GeoLayers_to_include.append(GeoId)

            # If the id is a GeoList id, add the GeoLayer ids within that GeoList to the list_of_GeoLayers_to_include
            # list.
            elif geo_util.is_geolist_id(self, GeoId):

                GeoLayer_ids = geo_util.return_geolayer_ids_from_geolist_id(self, GeoId)
                list_of_GeoLayers_to_include.extend(GeoLayer_ids)

            # If the id is not a registered GeoLayer id or a registered GeoList id, raise an error and mark
            # error_occurred flag as TRUE.
            else:

                warning_count += 1
                warning = "ID ({}) is not a valid GeoLayer id or valid GeoList id.".format(GeoId)
                raise ValueError(warning)

        # If no error occurred and there is at least one GeoLayer id to include in the new GeoList, create a GeoList
        # object and add it to the GeoProcessor's GeoLists list. Else, throw an error.
        if warning_count == 0 and list_of_GeoLayers_to_include:

            newGeoList = GeoListMetadata(geolist_id=pv_GeoListId, geolayer_id_list=list_of_GeoLayers_to_include)
            self.command_processor.GeoLists.append(newGeoList)
            logger.info("CreateGeoList command was successfully run without any warnings. GeoList {} created.".format(
                pv_GeoListId))

        else:
            warning = "There were {} warnings processing the command.".format(warning_count)
            logger.warning(warning)
            raise RuntimeError(warning)
