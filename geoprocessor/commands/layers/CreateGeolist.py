#CreateGeolist command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.geo as geo_util
import geoprocessor.util.validators as validators

import logging

# Inherit from AbstractCommand
class CreateGeolist(AbstractCommand):
    """Creates a geolist within the geoprocessor.

    A geolist is a collection of registered geolayers. Geolists are useful when iterating over a group of geolayers in
    a for loop. This command takes a list of geolayer ids and geolist ids and adds all of the relevant geolayer ids to
    the geolist.

    If the item in the GeoIdList is a geolayer id, then that geolayer id is added to the newly created geolist.
    If the item in the GeoIdList is a geolidy id, then all of the geolayer ids within that geolist are added to the
    newly created geolist.

    Args:
        GeoIdList (list): a list of registered geolayer ids and registered geolist ids. The relater geolayers will be
        included in the newly-created geolist (explained above).
        GeolistId (str): a unique id that will be used to identify the geolist"""

    def __init__(self):
        """Initialize the command"""

        super(CreateGeolist, self).__init__()
        self.command_name = "CreateGeolist"
        self.command_parameter_metadata = [
            CommandParameterMetadata("GeoIdList", type([]), None),
            CommandParameterMetadata("GeolistId", type(""), None),
            CommandParameterMetadata("CommandStatus", type(""), None)
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
        logger = logging.getLogger("gp")

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

        # Check that parameter GeolistId is a non-empty, non-None string.
        pv_GeolistId = self.get_parameter_value(parameter_name='GeolistId', command_parameters=command_parameters)
        if not validators.validate_string(pv_GeolistId, False, False):
            message = "GeolistId parameter has no value."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify text for the GeolistId parameter."))
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
        Run the command. Create a Geolist and register it in the GeoProcessor. Print the message to the log file.

        Returns:
            Nothing
        """
        logger = logging.getLogger(__name__)
        warning_count = 0

        # Get the GeoIdList in string format. Convert the GeoIdList parameter value to list format.
        pv_GeoIdList = self.get_parameter_value("GeoIdList")
        pv_GeoIdList = command_util.to_correct_format(pv_GeoIdList)

        # Get the GeolistId in string format.
        pv_GeolistId = self.get_parameter_value("GeolistId")

        # A list that will hold the id of each geolayer to be included in the newly create geolist.
        list_of_geolayers_to_include = []

        # Iterate through the user-defined geo_ids (can be geolayer or geolist id).
        for geo_id in pv_GeoIdList:

            # If the id is a geolayer id, add that geolayer id to the list_of_geolayers_to_include list.
            if geo_util.is_geolayer_id(self, geo_id):

                list_of_geolayers_to_include.append(geo_id)

            # If the id is a geolist id, add the geolayer ids within that geolist to the list_of_geolayers_to_include
            # list.
            elif geo_util.is_geolist_id(self, geo_id):

                geolayer_ids = geo_util.return_geolayer_ids_from_geolist_id(self, geo_id)
                list_of_geolayers_to_include.extend(geolayer_ids)

            # If the id is not a registered geolayer id or a registered geolist id, raise an error and mark
            # error_occurred flag as TRUE.
            else:

                warning_count += 1
                raise ValueError("ID ({}) is not a valid geolayer id or valid geolist id.".format(geo_id))


        # If no error occurred and there is at least one geolayer id to include in the new geolist, append the geolist
        # to the geoprocessor geolists dictionary with the user-defined geolist id as the key and the list of geolayer
        # ids as the value.
        if warning_count == 0 and list_of_geolayers_to_include:
            self.command_processor.geolists[pv_GeolistId] = list_of_geolayers_to_include
            logger.info("CreateGeolist command was successfully run without any warnings. Geolist {} created.".format(
                pv_GeolistId))

        else:
            message = "There were {} warnings processing the command.".format(warning_count)
            logger.warning(message)
            raise RuntimeError(message)
