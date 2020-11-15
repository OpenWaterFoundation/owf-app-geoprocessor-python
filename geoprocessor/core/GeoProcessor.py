# GeoProcessor - class to process a workflow of commands
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

from geoprocessor.core.DataTable import DataTable
from geoprocessor.core.GeoLayer import GeoLayer
from geoprocessor.core.GeoMap import GeoMap
from geoprocessor.core.GeoMapProject import GeoMapProject
from geoprocessor.core.GeoProcessorCommandFactory import GeoProcessorCommandFactory
from geoprocessor.core.CommandError import CommandError
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType
from geoprocessor.core.DataStore import DataStore
from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand
from geoprocessor.commands.running.EndFor import EndFor
from geoprocessor.commands.running.If import If

import geoprocessor.util.app_util as app_util
import geoprocessor.util.os_util as os_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.command_util as command_util

# QGIS-specific code
from plugins.processing.core import Processing

# General modules
import getpass
import logging
import os
from pathlib import Path
import platform
# import sys
import tempfile
from time import gmtime, strftime


class GeoProcessor(object):
    """
    Overarching class that performs the work of the geoprocessing tool
    by executing a sequence of commands.
    """

    def __init__(self) -> None:
        """
        Construct/initialize a geoprocessor.
        """

        # The array of command processor listeners to be called
        # when the commands are running, to indicate progress.
        # - would be an interface in Java but in Python is just an object with methods:
        #   command_started() and command_completed()
        # Call sequence is:
        #   add_command_processor_listener()                                <- called by GeoProcessorUI.__init__()
        #     - adds the listener object to self.command_processor_listener_array
        #   notify_command_processor_listeners_of_command_started()         <- called by run_commands()
        #     - calls listener object command_started()
        #   notify_command_processor_listener_of_command_completed()        <- called by run_commands()
        #     - calls listener object command_completed()
        #   notify_command_processor_listener_of_command_cancelled()        <- currently not called (need UI features)
        #     - calls listener object command_completed()
        self.command_processor_listener_array: [] = []

        # Command list that holds all command objects to run.
        self.commands: [AbstractCommand] = []

        # datastores list that holds all registered DataStore objects.
        self.datastores: [DataStore] = []

        # Property dictionary that holds all geoprocessor properties.
        self.properties: dict = {}

        # Start map/project components =================================================================================
        # - these data objects are the primary objects that GeoProcessor manages when creating maps
        # - these objects are also displayed in Results in the UI
        # - other map-related objects are stored in these main objects

        # GeoLayer list that holds all registered GeoLayer objects.
        # - can contain vector and raster layers
        # - this array is updated when a layer is created or read with a command
        self.geolayers: [GeoLayer] = []

        # GeoMap list that holds all registered GeoMap objects.
        # - this array is updated when a map is created with CreateGeoMap
        self.geomaps: [GeoMap] = []

        # GeoMap list that holds all registered GeoMapProject objects.
        # - this array is updated when a project is created with CreateGeoMapProject
        self.geomapprojects: [GeoMapProject] = []

        # End map/project components ===================================================================================

        # Start tracking 'last' map objects added, to allow providing a default for commands ===========================
        # - these need to be maintained in the GeoProcessor to allow commands to access

        # Last GeoMapProject added with commands, used to help determine defaults in commands
        # - used when determining the default map project
        # - needed because the geomapprojects array may not reflect the order of commands
        # - the CreateGeoMapProject command sets this
        self.last_geomapproject_added = None

        # Last GeoMap added
        # - used when determining the default map
        # - needed because the geomaps array may not reflect the order of commands
        # - the CreateGeoMap command sets this
        self.last_geomap_added = None

        # Last GeoLayerViewGroup added
        # - used when determining the default view group
        # - needed because the geo layer view group array for a map may not reflect the order of commands
        # - the AddGeoLayerViewGroupToGeoMap command sets this
        self.last_geolayerviewgroup_added = None

        # Last GeoLayerViewGroup added
        # - used when determining the default view
        # - needed because the geo layer view array for a map may not reflect the order of commands
        # - the AddGeoLayerToGeoMap command sets this
        self.last_geolayerview_added = None

        # End tracking 'last' map tracking objects =====================================================================

        # Table list that holds all registered tables object.
        self.tables: [DataTable] = []

        # List that holds the absolute paths to the output files.
        self.output_files: [str] = []

        # Holds the initialized QGIS processor, to run processing algorithms.
        # - this uses plugins.processing.core.Processing.runAlgorithm
        # - alternatively, could use qgis.processing.processAlgorithm
        # - TODO smalers 2020-07-12 is there any real difference between the two?  Parameters seem similar.
        self.qgis_processor: Processing = qgis_util.initialize_qgis_processor()
        #self.qgis_processing: processing = qgis_util.initialize_qgis_processing()

        # qgis version
        self.properties["QGISVersion"] = qgis_util.get_qgis_version_str()

        # Set properties for QGIS environment.
        # qgis_prefix_path: the full pathname to the qgis install folder (often C:\OSGeo4W\apps\qgis)
        # TODO smalers 2017-12-30 Need to rework to not hard code.
        # - Need to pass in QGIS configuration from the startup batch file or script.
        self.set_property("qgis_prefix_path", r"C:\OSGeo4W64\apps\qgis")

        # Set the initial working directory properties prior to reading a command file.
        # Reading the command file should reset these properties.
        # TODO smalers 2017-12-30 need to handle "New command file" action when UI is implemented.
        cwd = os.getcwd()
        # These will have C:\ on Windows and / on Linux.
        # - will be reset to Python friendly version with all forward slashes when a command file is opened
        self.properties["InitialWorkingDir"] = os.path.dirname(cwd)
        self.properties["InitialWorkingDirNative"] = os.path.dirname(cwd)
        self.properties["WorkingDir"] = os.path.dirname(cwd)
        self.properties["WorkingDirNative"] = os.path.dirname(cwd)

        # TODO smalers 2017-12-30 May not need this - Python design improves on Java design
        # - remove once tested out
        # Indicate whether commands should clear their log before running.
        # Normally this is True.  However, when using For() commands it is helpful to accumulate
        # logging messages in commands within the For() loop.  Otherwise, only the log messages from
        # the last For() loop iteration will be in the log.  The command processor sets this value,
        # which is checked before running the command.
        # This check was performed in each command in the Java code but is handled in the processor
        # to simplify command class code.
        # self.__command_should_clear_run_log = True

        # Environment properties passed in from the application
        # - TODO smalers 2018-02-28 may need to be more explicit about setting.
        #   currently gets set when run_commands() is called.
        # - Should always work for RunCommands but what if nested several layers?
        self.env_properties = {}

    def __len__(self) -> int:
        """
        Return the length of the command list.

        Returns:
            Length of the command list.
        """
        if self.commands is None:
            return 0
        else:
            return len(self.commands)

    def add_command(self, command_string: str) -> None:
        """
        Add a command string to the end.

        Args:
            command_string (str):  command as string to add
        """
        command_factory = GeoProcessorCommandFactory()

        command_object = command_factory.new_command(command_string, True)

        # Initialize the parameters of the command object.
        # Work is done in the AbstractCommand class.
        command_object.initialize_command(command_string, self, True)

        self.commands.append(command_object)

        # GeoProcessorCommandFactory
        debug = False
        if debug:
            command_object.print_for_debug()
            logger = logging.getLogger(__name__)
            logger.debug("First command debug:")
            self.commands[0].print_for_debug()

    # TODO smalers 2020-03-13 evaluate removing this or inserting a Command object instead
    def add_command_at_index(self, command_string: str, index: int) -> None:
        """
        Add a command string above currently selected command in command file.

        Args:
            command_string (str): Command string to be inserted to the command file.
            index (int): Index of the currently selected command_string

        Returns:
            None
        """
        command_factory = GeoProcessorCommandFactory()

        command_object = command_factory.new_command(command_string, True)

        # Initialize the parameters of the command object.
        # Work is done in the AbstractCommand class.
        command_object.initialize_command(command_string, self, True)

        # Add command above selected command
        self.commands.insert(index, command_object)

    def add_command_processor_listener(self, listener: object) -> None:
        """
        Add a command processor listener, to be notified when commands are started,
        progress made, and completed. This is useful to allow calling software to report progress.
        If the listener has already been added, the listener will remain in the list in the original order.

        Args:
            listener: a command list model
        """

        # Use arrays to make a little simpler than Vectors to use later...
        if not listener:
            return
        # See if the listener has already been added...
        for listener_from_array in self.command_processor_listener_array:
            if listener_from_array == listener:
                return
        self.command_processor_listener_array.append(listener)

    def add_datastore(self, datastore: DataStore) -> None:
        """
        Add a DataStore object to the datastores list. If the DataStore already exists with the same DataStore ID, the
        existing DataStore will be overwritten with the input DataStore.

        Args:
            datastore: instance of a DataStore object

        Returns:
            None
        """

        # Iterate over the existing DataStores.
        for existing_datastore in self.datastores:

            # If an existing DataStore has the same ID as the input DataStore, remove the existing DataStore from the
            # datastores list.
            if existing_datastore.id == datastore.id:
                self.free_datastore(existing_datastore)

        # Add the input DataStore to the datastores list.
        self.datastores.append(datastore)

    def add_geolayer(self, geolayer: GeoLayer) -> None:
        """
        Add a GeoLayer object to the geolayers list. If a geolayer already exists with the same GeoLayer ID, the
        existing GeoLayer will be replaced with the input GeoLayer.
        The GeoLayer can be either a VectorGeoLayer or RasterGeoLayer.

        Args:
            geolayer: instance of a GeoLayer object

        Returns:
            None
        """

        # Iterate over the existing GeoLayers.
        for existing_geolayer in self.geolayers:
            # If an existing GeoLayer has the same ID as the input GeoLayer, remove the existing GeoLayer from the
            # geolayers list.
            if existing_geolayer.id == geolayer.id:
                self.free_geolayer(existing_geolayer)

        # Add the input GeoLayer to the geolayers list.
        self.geolayers.append(geolayer)

    def add_geomap(self, geomap: GeoMap) -> None:
        """
        Add a GeoMap object to the geomaps list. If a geomap already exists with the same GeoMap ID, the
        existing GeoMap will be replaced with the input GeoMap.
        The GeoMap is saved as the last added, so it can be used as default for following commands that don't
        specify a GeoMap ID.

        Args:
            geomap: instance of a GeoMap object

        Returns:
            None
        """

        # Iterate over the existing GeoMaps.
        for existing_geomap in self.geomaps:
            # If an existing GeoMap has the same ID as the input GeoMap, remove the existing GeoMap from the
            # geomaps list.
            if existing_geomap.id == geomap.id:
                self.free_geomap(existing_geomap)

        # Add the input GeoMap to the geomaps list.
        self.geomaps.append(geomap)

        # Save the last map added
        self.last_geomap_added = geomap

    def add_geomapproject(self, geomapproject: GeoMapProject) -> None:
        """
        Add a GeoMapProject object to the geomapprojects list.
        If a geomapproject already exists with the same GeoMap ID, the
        existing GeoMapProject will be replaced with the input GeoMapProject.
        The GeoMap is saved as the last added, so it can be used as default for following commands that don't
        specify a GeoMap ID.

        Args:
            geomapproject: instance of a GeoMapProject object

        Returns:
            None
        """

        # Iterate over the existing GeoMapProjects.
        for existing_geomapproject in self.geomapprojects:
            # If an existing GeoMapProject has the same ID as the input GeoMapProject,
            # remove the existing GeoMapProject from the geomapprojects list.
            if existing_geomapproject.id == geomapproject.id:
                self.free_geomapproject(existing_geomapproject)

        # Add the input GeoMap to the geomaps list.
        self.geomapprojects.append(geomapproject)

        # Save the last project added
        self.last_geomapproject_added = geomapproject

    def add_output_file(self, output_file_abs_path: str) -> None:
        """
        Add an Output File (absolute path string) to the output_path list.

        Args:
            output_file_abs_path(str): A string representing the full pathname to an output file.

        Returns:
            None
        """

        # Only add the output file path if it does not already exist within the list.
        if output_file_abs_path not in self.output_files:
            self.output_files.append(output_file_abs_path)

    def add_table(self, table: DataTable) -> None:
        """
        Add a DataTable object to the tables list. If a DataTable already exists with the same Table ID,
        the existing DataTable will be overwritten with the input Table.

        Args:
            table: instance of a Table object

        Returns:
            None
        """

        # Iterate over the existing Tables.
        for existing_table in self.tables:

            # If an existing Table has the same ID as the input Table, remove the existing Table from the tables list.
            if existing_table.id == table.id:
                self.free_table(existing_table)

        # Add the input Table to the tables list.
        self.tables.append(table)

    def convert_command_line_from_comment(self, selected_indices: [int]) -> None:
        """
        Convert a command line in the command file from a comment.

        Args:
            selected_indices (int []): Indices of command lines that should be converted from a comment.

        Returns:
            Return if not a comment
        """
        command_factory = GeoProcessorCommandFactory()

        for index in selected_indices:
            command_string = self.commands[index].command_string

            # Check to see if a # comment and if so replace with command.
            remove_count = 0
            if command_string.startswith("# "):
                # Behavior when converting a command to comment is to insert "# " so check first.
                remove_count = 2
            elif command_string.startswith("#"):
                # A command could have been manually edited and start with only "#" (not "# ") so check second.
                remove_count = 1
            if remove_count > 0:
                # Strip the comment off the front of the string.
                command_string = command_string[remove_count:]
                # Create the command from the shorter string.
                create_unknown_command_if_not_recognized = True
                command_object = command_factory.new_command(command_string,
                                                             create_unknown_command_if_not_recognized)

                # Initialize the parameters of the command object.
                # Work is done in the AbstractCommand class.
                command_object.initialize_command(command_string, self, True)

                # Reset the previous command with the new command.
                self.commands[index] = command_object
            else:
                # Not a comment so ignore
                return

    def convert_command_line_to_comment(self, selected_indices: [int]) -> None:
        """
        Convert a command line in the command file to a comment.

        Args:
            selected_indices (int []): Indices of command lines that should be converted from a comment.

        Returns:
            None
        """
        command_factory = GeoProcessorCommandFactory()

        for index in selected_indices:
            command_string = self.commands[index].command_string

            command_string = "# " + command_string

            command_object = command_factory.new_command(command_string, True)

            # Initialize the parameters of the command object.
            # Work is done in the AbstractCommand class.
            command_object.initialize_command(command_string, self, True)

            # Add command above selected command
            self.commands[index] = command_object

    def decrease_indent_command_string(self, index: int) -> None:
        """
        Remove an indent from the front of the command string. If there are multiple
        indents this only removes space representing a single indent.

        Args:
            index: The index of the command string to decrease the indent from

        Returns:
            None
        """
        current_command = self.commands[index].command_string
        front_of_string = current_command[:4]
        if front_of_string == '    ':  # indent is 4 characters
            current_command = current_command[4:]
            self.commands[index].command_string = current_command

    # noinspection PyPep8Naming
    @classmethod
    def __evaluate_if_stack(cls, If_command_stack: [If]) -> bool:
        """
        Evaluate whether If stack evaluates to True.

        Loop through the list of If_Command and evaluate the overall condition statement.
        All conditions must be true for nested if statements to allow execution of commands in the block.

        Args:
            If_command_stack (If[]): list of If commands to check.

        Returns:
            True if all the If commands evaluate to True, False otherwise.
        """
        for i_if_command in range(len(If_command_stack)):
            If_command = If_command_stack[i_if_command]
            if not If_command.get_condition_eval():
                return False
        return True

    def expand_parameter_value(self, parameter_value: str, command: AbstractCommand = None) -> str or None:
        """
        Expand a command parameter value (string) into full string.
        This function is a port of the Java TSCommandProcessorUtil.expandParameterValue() method.

        Args:
            parameter_value (str): Command parameter value as string to expand.
                The parameter value can include ${Property} notation to indicate a processor property.
            command (Command):
                A command instance (will be used in the future if command property syntax needs to be expanded,
                for example using syntax ${c:Property}).

        Returns:
            Expanded parameter value string.
        """
        debug = False  # For developers
        logger = logging.getLogger(__name__)
        if debug:
            logger.debug('parameter_value=' + str(parameter_value))
        if parameter_value is None or len(parameter_value) == 0:
            # Just return what was provided.
            return parameter_value

        if command is not None and debug:
            logger.warning("GeoProcessor.expand_parameter_value 'command' is not implemented.")

        # First replace escaped characters.
        # TODO smalers 2017-12-25 might need to change this for Python
        parameter_value = parameter_value.replace("\\\"", "\"")
        parameter_value = parameter_value.replace("\\'", "'")
        # Else see if the parameter value can be expanded to replace ${} symbolic references with other values
        # Search the parameter string for $ until all processor parameters have been resolved
        search_pos = 0  # Position in the "parameter_value" string to search for ${} references
        found_pos_start = -1  # Position when leading "${" is found
        found_pos_end = -1  # Position when ending "}" is found
        prop_name = None  # Whether a property is found that matches the "$" character
        delim_env_start = "${ENV:"  # Start of property when environment variable
        delim_start = "${"  # Start of property
        delim_start_len = 2  # Length of start delimiter for ${, will be changed if ${env:
        delim_end = "}"  # End of property
        while search_pos < len(parameter_value):
            found_pos_start = -1  # Indicates no ${ notation of any kind
            # First see if any "${env:" strings. using uppercase conversion to allow any case
            found_pos_env_start = parameter_value.upper().find(delim_env_start, search_pos)
            if found_pos_env_start >= 0:
                # Environment variable property syntax
                found_pos_start = found_pos_env_start  # Set general value for general logic below
                delim_start_len = 6  # Length of "${env:"
                delim_start = delim_env_start  # Use for general code below
            else:
                # Check general property syntax
                found_pos_start = parameter_value.find(delim_start, search_pos)
                if found_pos_start >= 0:
                    delim_start_len = 2  # Length of "${"
            # End position syntax is the same regardless of the start
            found_pos_end = parameter_value.find(delim_end, (search_pos + delim_start_len))
            # Need both start and end positions to be >= 0 to continue
            # - otherwise property syntax is not found or is malformed and can't be processed
            found_delim_count = 0
            if found_pos_start >= 0:
                found_delim_count = found_delim_count + 1
            if found_pos_end >= 0:
                # No more $ property names, so return what have.
                found_delim_count = found_delim_count + 1
            if found_delim_count < 2:
                return parameter_value
            # Else found the delimiter so continue with the replacement
            # Message.printStatus(2, routine, "Found " + delimStart + " at position [" + found_pos_start + "]")
            if debug:
                if found_pos_start >= 0:
                    logger.debug("Found " + delim_start + " at position [" + str(found_pos_start) + "]")
            # Get the name of the property
            prop_name = parameter_value[(found_pos_start + delim_start_len):found_pos_end]
            if debug:
                logger.debug('Property name is "' + prop_name + '"')
            # Try to get the property from the processor
            # TODO smalers 2007-12-23 Evaluate whether to skip None.  For now show "None" in result.
            propval = None
            propval_string = ""
            # noinspection PyBroadException
            try:
                if found_pos_env_start >= 0:
                    # Looking up an environment variable
                    if debug:
                        logger.debug('Getting property value for environment variable "' + prop_name + '"')
                    propval = os.environ[prop_name]
                else:
                    # Looking up a normal property
                    if debug:
                        logger.debug('Getting property value for "' + prop_name + '"')
                    propval = self.get_property(prop_name)
                if debug:
                    logger.debug('Property value is "' + propval + '"')
                # The following should work for all representations as long as str() does not truncate
                # TODO smalers 2017-12-28 confirm that Python shows numbers with full decimal, not scientific notation.
                propval_string = "" + str(propval)
            except Exception as e:
                # Keep the original literal value to alert user that property could not be expanded
                if debug:
                    logger.debug('Exception getting the property value from the processor')
                propval_string = delim_start + prop_name + delim_end
            if propval is None:
                # Keep the original literal value to alert user that property could not be expanded
                propval_string = delim_start + prop_name + delim_end
            # If here have a property
            # b = new StringBuffer()
            b = ""
            # Append the start of the string
            if found_pos_start > 0:
                # b.append ( parameter_value[0:found_pos] )
                b = b + parameter_value[0:found_pos_start]
            # Now append the value of the property.
            # b.append(propval_string)
            b = b + propval_string
            # Now append the end of the original string if anything is at the end...
            if len(parameter_value) > (found_pos_end + 1):
                # b.append ( parameter_value[(found_pos_end + 1):]
                b = b + parameter_value[(found_pos_end + 1):]
            # Now reset the search position to finish evaluating whether to expand the string.
            # parameter_value = b.toString()
            parameter_value = b
            search_pos = found_pos_start + len(propval_string)  # Expanded so no need to consider delim *
            if debug:
                #    Message.printDebug( 1, routine, "Expanded parameter value is \"" + parameter_value +
                #    "\" searchpos is now " + searchPos + " in string \"" + parameter_value + "\"" )
                logger.debug('Expanded parameter value is "' + parameter_value +
                             '" searchpos is now ' + str(search_pos) + ' in string "' + parameter_value + '"')
        return parameter_value

    def free_datastore(self, datastore: DataStore) -> None:
        """
        Removes a DataStore object from the datastores list.

        Args:
            datastore: instance of a DataStore object

        Returns:
            None
        """
        self.datastores.remove(datastore)

    def free_geolayer(self, geolayer: GeoLayer) -> None:
        """
        Removes a GeoLayer object from the geolayers list.

        Args:
            geolayer: instance of a GeoLayer object

        Return:
            None
        """
        self.geolayers.remove(geolayer)

    def free_geomap(self, geomap: GeoMap) -> None:
        """
        Removes a GeoMap object from the geomaps list.

        Args:
            geomap: instance of a GeoMap object

        Return:
            None
        """
        self.geomaps.remove(geomap)

    def free_geomapproject(self, geomapproject: GeoMapProject) -> None:
        """
        Removes a GeoMapProject object from the geomapprojects list.

        Args:
            geomapproject: instance of a GeoMapProject object

        Return:
            None
        """
        self.geomapprojects.remove(geomapproject)

    def free_table(self, table: DataTable) -> None:
        """
        Removes a DataTable object from the tables list.

        Args:
            table (DataTable): instance of a DataTable object

        Returns:
            None
        """
        self.tables.remove(table)

    def get_command_list(self) -> [AbstractCommand]:
        """
        Return the list of command objects from the processor

        Returns: list of commands

        """
        return self.commands

    def get_datastore(self, datastore_id: str) -> DataStore or None:
        """
        Return the DataStore that has the requested ID.

        Args:
            datastore_id (str):  DataStore ID string.

        Returns:
            The DataStore that has the requested ID, or None if not found.
        """
        for datastore in self.datastores:
            if datastore is not None:
                if datastore.id == datastore_id:
                    # Found the requested identifier
                    return datastore
        # Did not find the requested identifier so return None
        return None

    def get_datastore_id_list(self) -> [DataStore]:
        """
        Reads the DataStore objects in the datastores list and returns a list of the available DataStore ids.

        Returns:
            List of available DataStore IDS.
        """

        # An empty list to hold all of the available DataStore IDs.
        datastore_id_list = []

        # Iterate over the available DataStores in the GeoProcessor. For each DataStore, append its ID to the list.
        for datastore in self.datastores:
            datastore_id_list.append(datastore.id)

        # Return the list of the available DataStore IDs.
        return datastore_id_list

    def get_geolayer(self, geolayer_id: str) -> GeoLayer or None:
        """
        Return the GeoLayer that has the requested ID.

        Args:
            geolayer_id (str):  GeoLayer ID string.

        Returns:
            The GeoLayer that has the requested ID, or None if not found.
        """
        for geolayer in self.geolayers:
            if geolayer is not None:
                if geolayer.id == geolayer_id:
                    # Found the requested identifier
                    return geolayer
        # Did not find the requested identifier so return None
        return None

    def get_geomap(self, geomap_id: str) -> GeoMap or None:
        """
        Return the GeoMap that has the requested ID.

        Args:
            geomap_id (str):  GeoMap ID string.

        Returns:
            The GeoMap that has the requested ID, or None if not found.
        """
        for geomap in self.geomaps:
            if geomap is not None:
                if geomap.id == geomap_id:
                    # Found the requested identifier
                    return geomap
        # Did not find the requested identifier so return None
        return None

    def get_geomapproject(self, geomapproject_id: str) -> GeoMapProject or None:
        """
        Return the GeoMapProject that has the requested ID.

        Args:
            geomapproject_id (str):  GeoMapProject ID string.

        Returns:
            The GeoMapProject that has the requested ID, or None if not found.
        """
        for geomapproject in self.geomapprojects:
            if geomapproject is not None:
                if geomapproject.id == geomapproject_id:
                    # Found the requested identifier
                    return geomapproject
        # Did not find the requested identifier so return None
        return None

    def get_number_errors(self) -> int:
        """
        Return the number of errors in commands.

        Returns
            Number of errors in commands list.
        """
        num_errors = 0
        for command in self.commands:
            command_status = command.command_status.run_status
            if command_status is CommandStatusType.FAILURE:
                num_errors += 1
        return num_errors

    def get_number_warnings(self) -> int:
        """
        Return the number of errors in commands.

        Returns:
            Number of errors in commands list.
        """
        num_warnings = 0
        for command in self.commands:
            command_status = command.command_status.run_status
            if command_status is CommandStatusType.WARNING:
                num_warnings += 1
        return num_warnings

    def get_property(self, property_name: str, if_not_found_val: object = None) -> object:
        """
        Get a GeoProcessor property, case-specific.

        Args:
            property_name (str):  Name of the property for which a value is retrieved.
            if_not_found_val (object):  Value to return if the property is not found
                (None is default or otherwise throw an exception).

        Returns:
            The object matching the requested property name.
        """
        try:
            return self.properties[property_name]
        except KeyError:
            if if_not_found_val is None:
                # Requested that None is returned if not found so do it
                # print('Property not found so returning None')
                return None
            else:
                # Let the exception from not finding a key in the dictionary be raised
                # print('Property not found so throwing exception')
                raise

    def get_table(self, table_id: str) -> DataTable or None:
        """
        Return the DataTable that has the requested ID.

        Args:
            table_id (str):  Table ID string.

        Returns:
            The Table that has the requested ID, or None if not found.
        """
        for table in self.tables:
            if table is not None:
                if table.id == table_id:
                    # Found the requested identifier
                    return table
        # Did not find the requested identifier so return None
        return None

    def indent_command_string(self, index: int) -> None:
        """
        Add an indent to the front of the command string using a predetermined
        amount of white space (TAB).

        Args:
            index (int): The index of the command string to indent

        Returns:
            None
        """
        tab = "    "  # 4 characters
        current_command = self.commands[index].command_string
        current_command = tab + current_command
        self.commands[index].command_string = current_command

    @classmethod
    def __lookup_endfor_command_index(cls, command_list: [AbstractCommand], for_name: str) -> [EndFor]:
        """
        Lookup the command index for the EndFor() command with requested name.

        Args:
            command_list (Command[]): list of commands to check
            for_name (str): the name of the "For" name to find

        Returns:
            The index (0+) of the EndFor() command that matches the specified name.
        """
        for i_command in range(len(command_list)):
            command = command_list[i_command]
            command_class = command.__class__.__name__
            if command_class == 'EndFor':
                if command.get_name() == for_name:
                    return i_command
        return -1

    @classmethod
    def __lookup_for_command_index(cls, command_list: [AbstractCommand], for_name: str) -> int:
        """
        Lookup the command index for the For() command with requested name.

        Args:
            command_list (Command[]): list of commands to check
            for_name (str): the name of the "For" name to find

        Returns:
            Command if found, otherwise -1
        """
        for i_command in range(len(command_list)):
            command = command_list[i_command]
            command_class = command.__class__.__name__
            if command_class == 'For':
                if command.get_name() == for_name:
                    return i_command
        return -1

    # noinspection PyPep8Naming
    @classmethod
    def __lookup_if_command(cls, If_command_stack: [If], if_name: str) -> If or None:
        """
        Lookup the command for the If() command with requested name.

        Args:
            If_command_stack (If[]): list of If commands that are active.
            if_name (str): the name of the "If" command to find

        Returns:
            The matching If() command instance.
        """
        for c in If_command_stack:
            if c.get_name() == if_name:
                return c
        return None

    def notify_command_processor_listener_of_command_cancelled(self, icommand: int, ncommand: int,
                                                               command: AbstractCommand) -> None:
        """
        Notify registered command processor listeners about a command being cancelled.

        Args:
            icommand (int): The index (0+) of the command that is cancelled.
            ncommand (int): The number of commands being processed. This will often be the
                total number of commands but calling code may process a subset.
            command (Command): The instance of the nearest command that is being called.

        Returns:
            None
        """
        if self.command_processor_listener_array:
            for listener_from_array in self.command_processor_listener_array:
                listener_from_array.command_cancelled(icommand, ncommand, command, -1.0, "Command cancelled")

    def notify_command_processor_listener_of_command_completed(self, icommand: int, ncommand: int,
                                                               command: AbstractCommand) -> None:
        """
        Notify registered command process listeners about a command completing.

        Args:
            icommand (int): The index (0+) of the command that is completing.
            ncommand (int): The number of commands being processed. This will often be the
                total number of commands but calling code may process a subset.
            command (Command): The instance of the command that is completing.

        Returns:
            None
        """
        if self.command_processor_listener_array:
            for listener_from_array in self.command_processor_listener_array:
                listener_from_array.command_completed(icommand, ncommand, command, -1.0, "Command completed.")

    def notify_command_processor_listeners_of_command_exception(self, icommand: int, ncommand: int,
                                                                command: AbstractCommand) -> None:
        """
        Notify registered command processor listeners about a command exception.

        Args:
            icommand (int): The index (0+) of the command that is starting.
            ncommand (int): The number of commands being processed. This will often be the
                total number of commands but calling code may process a subset.
            command (Command): The instance of the command that is starting.

        Returns:
            None
        """
        if self.command_processor_listener_array:
            for listener_from_array in self.command_processor_listener_array:
                listener_from_array.command_exception(icommand, ncommand, command, -1.0, "Command exception.")

    def notify_command_processor_listeners_of_command_started(self, icommand: int, ncommand: int,
                                                              command: AbstractCommand) -> None:
        """
        Notify registered command processor listeners about a command starting.

        Args:
            icommand (int): The index (0+) of the command that is starting.
            ncommand (int): The number of commands being processed. This will often be the
                total number of commands but calling code may process a subset.
            command (Command): The instance of the command that is starting.

        Returns:
            None
        """
        if self.command_processor_listener_array:
            for listener_from_array in self.command_processor_listener_array:
                listener_from_array.command_started(icommand, ncommand, command, -1.0, "Command started.")

    # TODO smalers 2017-12-31 Need to switch to CommandFileRunner class
    def process_command_file(self, command_file: str) -> None:
        """
        Reads the command file and runs the commands within the command file.

        Args:
            command_file (str): The name of the command file to read.

        Returns:
            None
        """

        self.read_command_file(command_file)
        self.run_commands()

    def read_command_file(self, command_file: str, create_unknown_command_if_not_recognized: bool = True,
                          append_commands: bool = False, run_discovery_on_load: bool = True,
                          create_commands=True) -> int:
        """
        Read a command file and initialize the command list in the geoprocessor.
        The processor properties "InitialWorkingDir" and "WorkingDir" are set to the command file folder,
        or the current working directory if the path to the command file is not absolute.
        This is similar to TSTool TSCommandProcessor.addCommandsFromStringList()

        Args:
            command_file (str): Name of the command file to read, typically should be an absolute path as
                specified by calling code such as UI file selector or batch file runner ("gp" application).
            create_unknown_command_if_not_recognized (bool):
                If True (the default), unrecognized commands will result in UnknownCommand instances.
            append_commands (bool):  If True (False is default), append the commands to those already in the processor.
                CURRENTLY NOT ENABLED.
            run_discovery_on_load (bool): If True (the default), run discovery when commands are loaded,
                which allows other commands to benefit from information used in editing choices.
                CURRENTLY NOT ENABLED.
            create_commands (bool):  If True (the default), create the command instances,
                if False, process the file to count commands but do not create instances.

        Returns:
            The number of commands read.
        """
        logger = logging.getLogger(__name__)

        if not create_commands:
            # Just figure out how many commands would be created
            command_file_strings = command_util.read_file_into_string_list(command_file)
            return len(command_file_strings)

        if append_commands:
            logger.warning("Processor 'append_commands' is not enabled.")
        if run_discovery_on_load:
            logger.warning("Processor 'run_discovery_on_load' is not enabled.")

        # Remove all items within the geoprocessor from the previous run.
        self.commands = []
        # self.datastores remain open since opened when the software starts
        self.geolayers = []
        self.geomaps = []
        self.geomapprojects = []
        self.output_files = []
        self.properties = {}
        self.tables = []

        # Set the processor properties.
        if os.path.isabs(command_file):
            # Command file is absolute so the working directory is just the parent of the command file.
            self.properties["InitialWorkingDir"] = os.path.dirname(command_file)
            self.properties["WorkingDir"] = os.path.dirname(command_file)
        else:
            # First get the working directory.
            # Then append the command file, which may have a relative path prefix like ../../.
            # Then get the parent folder of the resulting file
            cwd = os.getcwd()
            command_file_abs = os.path.join(cwd, command_file)
            self.properties["InitialWorkingDir"] = os.path.dirname(command_file_abs)
            self.properties["WorkingDir"] = os.path.dirname(command_file_abs)

        # The command file is likely generalized such as /path on Linux and C:/path on Windows.
        # Therefore, save a native version for code that needs it such as RunProgram when running a shell.
        if os_util.is_windows_os():
            self.properties["WorkingDirNative"] = self.properties["WorkingDir"].replace("/", "\\")
            self.properties["InitialWorkingDirNative"] = self.properties["InitialWorkingDir"].replace("/", "\\")
        else:
            self.properties["WorkingDirNative"] = self.properties["WorkingDir"]
            self.properties["InitialWorkingDirNative"] = self.properties["InitialWorkingDir"]

        # Create an instance of the GeoProcessorCommandFactory.
        command_factory = GeoProcessorCommandFactory()

        # Get a list of command file strings (each line of the command file is its own item in the list).
        command_file_strings = command_util.read_file_into_string_list(command_file)

        # clear commands
        self.commands.clear()

        # Iterate over each line in the command file.
        for command_file_string in command_file_strings:
            # Initialize the command object (without parameters).
            # Work is done in the GeoProcessorCommandFactory class.
            command_object = command_factory.new_command(
                command_file_string,
                create_unknown_command_if_not_recognized)

            # Initialize the parameters of the command object.
            command_object.initialize_command(command_file_string, self, True)

            # Check the command parameters so that initialization log messages are generated
            # - this ensures that the UI will display initialization messages
            # noinspection PyBroadException
            try:
                command_object.check_command_parameters(command_object.command_parameters)
            except Exception:
                # Errors will have been added to the command log and should display in the UI
                # - TODO smalers 2020-03-22 TSTool logic does more - do simple logging here
                logger.warning("Command has errors.  See command log in UI and log file.")

            # Append the initialized command (object with parameters) to the geoprocessor command list.
            self.commands.append(command_object)

            debug = False
            if debug:
                command_object.print_for_debug()
                logger.debug("First command debug:")
                self.commands[0].print_for_debug()

        # Let the command list processor know that the commands have been read from the command file
        # TODO smalers 2020-03-09 Not sure why this is needed so comment out
        # self.notify_command_list_processor_listener_of_commands_read()

        logger.info("Read and initialized " + str(len(self.commands)) + " commands.")
        return len(self.commands)

    def read_commands_from_command_list(self, command_file_strings: [str], runtime_properties: dict) -> None:
        """
        Read the command workflow from the user interface and initialize the command list in the geoprocessor.

        Args:
            command_file_strings (list): list of strings. Each item of the list represents one command line string.
            runtime_properties (dict): dictionary of runtime properties, in particular 'WorkingDir'

        Returns:
            None
        """
        logger = logging.getLogger(__name__)

        # Remove all items within the geoprocessor from the previous run.
        self.commands = []
        self.geolayers = []
        self.geomaps = []
        self.geomapprojects = []
        self.output_files = []
        self.properties = {}
        self.tables = []

        # Set the working directory to that indicated by the properties

        # Create an instance of the GeoProcessorCommandFactory.
        command_factory = GeoProcessorCommandFactory()
        try:
            self.properties["WorkingDir"] = runtime_properties.get("WorkingDir")
        except KeyError:
            # For now swallow this because UI my not have saved the working directory
            pass
        # TODO smalers 2018-07-24 Need to evaluate whether initial folder is also needed,
        # such as for redundant calls by RunCommands()
        # self.properties["InitialWorkingDir"] = ??

        # Iterate over each line in the command file.
        for command_file_string in command_file_strings:

            command_file_string = command_file_string.strip()

            # Initialize the command object (without parameters).
            # Work is done in the GeoProcessorCommandFactory class.
            command_object = command_factory.new_command(command_file_string, True)

            # Initialize the parameters of the command object.
            # Work is done in the AbstractCommand class.
            command_object.initialize_command(command_file_string, self, True)

            # Append the initialized command (object with parameters) to the geoprocessor command list.
            self.commands.append(command_object)

            debug = False
            if debug:
                command_object.print_for_debug()
                logger.debug("First command debug:")
                self.commands[0].print_for_debug()

    def remove_all_commands(self) -> None:
        """
        Remove all the commands from the command list>

        Returns:
            None
        """
        # Remove all commands from command list
        del self.commands[:]
        # Notify the command list model that the commands list UI in CommandListWidget
        # needs to be updated to reflect changes made to commands in GeoProcessor
        # TODO smalers 2020-03-10 Not sure this is needed in current design
        # self.notify_command_list_processor_listener_update_commands()

    def remove_command(self, index: str) -> None:
        """
        Remove a command at the given index.

        Args:
            index (int): The index of the command to remove from the commands list

        Returns:
            None
        """
        del self.commands[index]
        # Notify the command list processor that the command list now needs to be updated in
        # the user interface.
        # TODO smalers 2020-03-10 Not sure this is needed in current design
        # self.notify_command_list_processor_listener_update_commands()

    def __reset_data_for_run_start(self, append_results: bool = False) -> None:
        """
        Reset the processor data prior to running the commands.
        This ensures that the command processor state from one run is isolated from the next run.
        Reset values are set to the initial defaults.
        This is used to handle calls to RunCommands() command, which results in recursive calls to the processor.
        It is not the same as the __reset_workflow_properties() function, which is called once for the
        initial command run (or outermost level when recursing).

        Args:
            append_results (bool):  Indicates whether the results from the current run should be
                appended to a previous run.

        Returns:
            None
        """
        # The following are the initial defaults...
        # TODO smalers 2017-12-30 Clear any hashtables used to increase performance, currently none
        self.properties["InputStart"] = None
        self.properties["InputEnd"] = None
        self.properties["OutputStart"] = None
        self.properties["OutputEnd"] = None
        self.properties["OutputYearType"] = None
        # Free all data from the previous run rather than append
        # - TODO smalers 2020-03-16 why is this "not append_results"?
        if append_results:
            # All in-memory lists of results, such as layers, should be cleared.
            # If a list (future design change?)...
            # del self.GeoLayers[:]
            # del self.GeoLists[:]
            # ...but currently a dictionary...
            self.geolayers.clear()
            self.geomaps.clear()
            self.geomapprojects.clear()
            self.output_files.clear()
            self.tables.clear()

    def __reset_workflow_properties(self) -> None:
        """
        Reset the workflow global properties to defaults, necessary when a command processor is rerun.
        This function is called by the run_commands() function before processing any commands.
        This function is ported from the Java TSCommandProperties.resetWorkflowProperties() method.

        Returns:
            None
        """

        # Java code uses separate properties rather than Python using one dictionary.
        # Therefore protect the properties that should absolutely not be reset.
        # First clear properties, including user-defined properties, but protect fundamental properties that
        # should not be reset (such as properties that are difficult to reset).
        # Check size dynamically in case props are removed below
        # Because the dictionary size may change during iteration, can't do the following
        #     for property_name, property_value in self.properties.items():
        # Cannot iterate through a dictionary and remove items from dictionary.
        # Therefore convert the dictionary to a list and iterate on the list
        processor_property_names = list(self.properties.keys())
        protected_property_names = ["InitialWorkingDir",
                                    "InitialWorkingDirNative",
                                    "WorkingDir",
                                    "WorkingDirNative",
                                    "QGISVersion"]
        # Loop through properties and delete all except for protected properties
        for i_parameter in range(0, len(processor_property_names)):
            property_name = processor_property_names[i_parameter]
            found_protected = False
            for protected_property_name in protected_property_names:
                if property_name == protected_property_name:
                    found_protected = True
                    break
            if not found_protected:
                del self.properties[property_name]

        # Define standard properties that are always available from the processor
        self.properties["ComputerName"] = platform.node()  # Useful for messages
        self.properties["ComputerTimezone"] = strftime("%z", gmtime())
        # Define the folder where GIS software programs are located, for use with RunGdalProgram, etc.
        qgis_install_folder = ""
        gis_bin_folder = ""
        gis_software = ""
        gdal_bin_software = ""
        if app_util.is_qgis_install_standalone():
            qgis_install_folder = app_util.get_qgis_install_folder()
            gis_bin_folder = qgis_install_folder.replace("\\", "/") + "/bin"
            gis_software = "QGIS"
            gdal_bin_folder = qgis_install_folder.replace("\\", "/") + "/bin"
        elif app_util.is_qgis_install_osgeo():
            # OSGeo shared installation folder.
            # Installation folder will be something like C:\OSGeo4W64\apps\qgis
            # but want C:\OSGeo4W64\bin.
            qgis_install_folder = app_util.get_qgis_install_folder()
            qgis_install_folder_path = Path(qgis_install_folder)
            gdal_bin_folder = qgis_install_folder_path.parent.parent.as_posix() + "/bin"
            gis_software = "QGIS"
        # TODO smalers 2020-01-16 Add support for ArcGIS Pro
        self.properties["GisSoftware"] = gis_software
        self.properties["GdalBinDir"] = gdal_bin_folder
        # TODO smalers 2017-12-30 need to figure out
        self.properties["InstallDir"] = None  # IOUtil.getApplicationHomeDir() )
        self.properties["InstallDirURL"] = None  # "file:///" + IOUtil.getApplicationHomeDir().replace("\\", "/") )
        # Temporary directory useful in some cases
        self.properties["TempDir"] = tempfile.gettempdir()
        home_dir = os.path.expanduser("~")
        self.properties["UserHomeDir"] = home_dir
        self.properties["UserHomeDirURL"] = "file:///" + home_dir.replace("\\", "/")
        self.properties["UserName"] = getpass.getuser()
        # Set the program version as a property, useful for version-dependent command logic
        # Assume the version is xxx.xxx.xxx beta (date), with at least one period
        # Save the program version as a string
        # TODO smalers 2017-12-30 need to complete...
        self.properties["ProgramVersionString"] = None  # programVersion )
        self.properties["ProgramVersionNumber"] = None  # new Double(programVersionNumber) )

    def run_commands(self, command_list: [AbstractCommand] = None, run_properties: dict = None,
                     env_properties: dict = None) -> None:
        """
        Run the commands that exist in the processor.

        Args:
            command_list: List of command objects to process, or None to process all commands in the processor.
                A list is typically provided when a subset of commands has been selected in the UI.
            run_properties:  Dictionary of properties used to control the run.
                This function only acts on the following properties:
                    ResetWorkflowProperties:  Global properties such as run period should be reset before running.
                        The default is True.  This property is used with the RunCommands command to preserve properties.
            env_properties:  Dictionary of properties passed in from the environment, such as global application
                properties.  These properties will be added to the processor properties.
                For example, pass in properties on the command line used to run the GeoProcessor in batch mode..

        Returns:
            None
        """
        # Logger for the processor
        logger = logging.getLogger(__name__)

        # Create a boolean to keep track of number of warnings, if any
        warning_count = 0

        # Remove all items within the geoprocessor from the previous run.
        # - TODO smalers 2020-03-16 evaluate how this relates to __reset_data_for_run_start
        self.geolayers = []
        self.geomaps = []
        self.geomapprojects = []
        self.output_files = []
        # Properties?
        # self.properties = {}
        self.tables = []

        # Reset the global workflow properties if requested, used when RunCommands command calls recursively...
        # - This code is a port of Java TSCommandProcessor.runCommands().
        reset_workflow_properties = True
        if run_properties is None:
            # Reset to an empty dictionary to simplify error handling below
            run_properties = {}
        try:
            prop_value = run_properties["ResetWorkflowProperties"]
            if prop_value is not None and prop_value == "False":
                reset_workflow_properties = False
        except KeyError:
            # Property not set so use default value
            pass
        if reset_workflow_properties:
            self.__reset_workflow_properties()
        # Set the environment properties in the processor
        # - These are global properties that should always be known
        self.set_properties(env_properties)
        # Also set in the environment for RunCommands to access
        self.env_properties = env_properties
        # ...end reset of global workflow properties

        # The remainder of this code is a port of the Java TSEngine.processCommands() function.

        # Indicate whether results should be cleared between runs.
        # If true, do not clear results between recursive calls.
        # This is used with a master command file that runs other command files with RunCommands commands.
        append_results = False
        # Indicate whether a recursive run of the processor is being made (e.g., because RunCommands() is used).
        recursive = False
        append_results = False
        # noinspection PyBroadException
        try:
            recursive_prop = run_properties["Recursive"]
            if recursive_prop == "True":
                recursive = True
                # Default for recursive runs is to NOT append results...
                append_results = False
        except Exception:
            # Recursive property was not defined so not running in recursive mode
            recursive = False
        # noinspection PyBroadException
        try:
            append_prop = run_properties["AppendResults"]
            if append_prop == "True":
                append_results = True
        except Exception:
            # Use default value from above
            pass

        logger.info("Recursive=" + str(recursive) + " AppendResults=" + str(append_results))

        if command_list is None:
            logger.info("Running all commands")
            command_list = self.commands
        else:
            logger.info("Running specified command list")
            # Running selected commands so reset all commands in command list
            for i_command in range(len(self.commands)):
                command = self.commands[i_command]
                command.command_status.clear_log(CommandPhaseType.RUN)

        # Reset any properties left over from the previous run that may impact the current run.
        self.__reset_data_for_run_start()

        # Whether or no the command is within a /*   */ comment block
        in_comment = False

        # Initialize the If() command stack that is in effect, needed to nest If() commands
        # noinspection PyPep8Naming
        If_command_stack = []

        # Initialize the For() command stack that is in effect, needed to nest For() commands
        # noinspection PyPep8Naming
        For_command_stack = []

        # Whether the If stack evaluates to True so enclosed commands can run
        # noinspection PyPep8Naming
        If_stack_ok_to_run = True

        # Loop through the commands and reset any For() commands to make sure they don't think they are complete.
        # Nested For() loos will be handled when processed by resetting when a For loop is totally complete.
        n_commands = len(command_list)
        for i_command in range(n_commands):
            command = command_list[i_command]
            if command is None:
                continue
            command_class = command.__class__.__name__
            if command_class == 'For':
                command.reset_command()
            # Clear the command Run log.
            command.command_status.clear_log(CommandPhaseType.RUN)

        # Run all the commands
        # - set debug = True to turn on debug messages
        debug = False
        # Python does not allow modifying the for loop iterator variable so use a while loop
        # for i_command in range(n_commands):
        i_command = -1
        command = None
        while i_command < n_commands:
            # noinspection PyBroadException
            try:
                # Catch exceptions in any command, to make sure all commands can run through
                # - hopefully nothing is amiss with main controlling commands - otherwise need to bulletproof code
                i_command = i_command + 1
                if i_command == n_commands:
                    # Do an extra check on the index to make sure because for loops can modify the index
                    # prior to the increment statement above.
                    break
                command = command_list[i_command]
                if debug:
                    command.print_for_debug()

                # if not in_comment and If_stack_ok_to_run:
                # The following message brackets any command class run_command messages that may be generated
                message = '-> Start processing command ' + str(i_command + 1) + ' of ' + str(n_commands) + ': ' + \
                    command.command_string
                # print(message)
                logger.info(message)
                # notify listener that command has started running
                self.notify_command_processor_listeners_of_command_started(i_command, n_commands, command)

                command_class = command.__class__.__name__

                if command_class == 'Comment':
                    # Hash-comment - TODO need to mark as processing successful - confirm when UI in place
                    # Run the command to update the status to success.
                    command.run_command()
                    self.notify_command_processor_listener_of_command_completed(i_command, n_commands, command)
                    continue
                elif command_class == 'CommentBlockStart':
                    # /* comment block start - TODO need to mark as processing successful - confirm when UI in place
                    in_comment = True
                    # Run the command to update the status to success.
                    command.run_command()
                    self.notify_command_processor_listener_of_command_completed(i_command, n_commands, command)
                    continue
                elif command_class == 'CommentBlockEnd':
                    # */ comment block end - TODO need to mark as processing successful - confirm when UI in place
                    in_comment = False
                    # Run the command to update the status to success.
                    command.run_command()
                    self.notify_command_processor_listener_of_command_completed(i_command, n_commands, command)
                    continue

                if in_comment:
                    # In a /* */ comment block so set status to successful
                    # - TODO smalers 2020-03-16 need to implement this
                    continue

                # Clear the log for the commands
                command.command_status.clear_log(CommandPhaseType.INITIALIZATION)
                command.command_status.clear_log(CommandPhaseType.DISCOVERY)
                # TODO smalers 2020-03-22 need to handle clearing of log in For loops - for now clear all
                # - would be nice to figure this out at the processor level, TSTool seems not optimal
                command.command_status.clear_log(CommandPhaseType.RUN)

                # Initialize the command by parsing command string, which will regenerate command log for issues
                # - need for the UI since the processor will be re-run multiple times
                command.initialize_command(command.command_string, self, True)

                # Check the command parameters
                # - this is called when editing the command but also need to check here when running
                # - the list of parameters is passed because the code is reused with editors that check
                #   parameters before saving the edits
                command.check_command_parameters(command.command_parameters)

                # Check to see whether the If stack evaluates to True and can run the command
                # - evaluation of the stack only occurs when an If() is encountered
                if If_stack_ok_to_run:
                    # Run the command
                    if command_class == 'Exit':
                        # Exit command causes hard exit from processing - following commands are ignored
                        # Do notify of the completion
                        self.notify_command_processor_listener_of_command_completed(i_command, n_commands, command)
                        break
                    # elif isinstance(command, For):
                    elif command_class == 'For':
                        # Initialize or increment the For loop
                        logger.info('Detected For command')
                        # Use a local variable For_command for clarity
                        # noinspection PyPep8Naming
                        For_command = command
                        ok_to_run_for = False
                        # noinspection PyBroadException
                        try:
                            ok_to_run_for = For_command.next()
                            # print('ok_to_run_for=' + str(ok_to_run_for))
                            # If False, the For loop is done.
                            # However, need to handle the case where the for loop may be nested and need to run again...
                            if not ok_to_run_for:
                                For_command.reset_command()
                        except Exception:
                            # This is serious and can lead to an infinite loop so generate an exception and
                            # jump to the end of the loop
                            ok_to_run_for = False
                            message = 'Error going to next iteration.'
                            logger.warning(message, exc_info=True)
                            command.command_status.add_to_log(
                                CommandPhaseType.RUN,
                                CommandLogRecord(
                                    CommandStatusType.FAILURE, message,
                                    "Check For() command iteration data."))
                            logger.warning('Error going to next iteration.  Check For() command iteration data.')
                            # Same logic as ending the loop...
                            end_for_index = GeoProcessor.__lookup_endfor_command_index(
                                command_list, For_command.get_name())
                            if end_for_index >= 0:
                                # OK because don't want to trigger EndFor() going back to the top
                                i_command = end_for_index
                                continue
                            else:
                                # Did not match the end of the For() so generate an error and exit
                                need_to_interrupt = True
                                message = 'Unable to match For loop name "' + For_command.get_name() + \
                                    '" in EndFor() commands.'
                                command.command_status.add_to_log(
                                    CommandPhaseType.RUN,
                                    CommandLogRecord(CommandStatusType.FAILURE, message,
                                                     "Add a matching EndFor() command."))
                                warning_count += 1
                                raise RuntimeError(message)
                        if ok_to_run_for:
                            # Continue running commands that are after the For() command
                            # Add to the For stack - if in any For loops, commands should by default NOT reset the
                            # command logging so that message will accumulate and help users troubleshoot errors
                            For_command_stack.append(For_command)
                            # Run the For() command to set the iterator property and then skip to the next command
                            # TODO smalers 2017-12-21 equivalent but should the following be For_command?
                            For_command.run_command()
                            continue
                        else:
                            # Done running the For() loop matching the EndFor() command
                            end_for_index = GeoProcessor.__lookup_endfor_command_index(
                                command_list, For_command.get_name())
                            # Modify the main command loop index and continue - the command after the end
                            # will be executed (or done).
                            if end_for_index >= 0:
                                # Loop will increment so EndFor will be skipped, which is OK
                                # - otherwise infinite loop
                                i_command = end_for_index
                                continue
                            else:
                                # Did not match the end of the For() so generate an error and exit
                                need_to_interrupt = True
                                message = 'Unable to match For loop name "' + For_command.get_name() + \
                                    '" in EndFor() commands.'
                                command.command_status.add_to_log(
                                    CommandPhaseType.RUN,
                                    CommandLogRecord(CommandStatusType.FAILURE, message,
                                                     "Add a matching EndFor() command."))
                                raise RuntimeError(message)
                    # elif isinstance(command,EndFor):
                    elif command_class == 'EndFor':
                        # Jump to the matching For()
                        # noinspection PyPep8Naming
                        EndFor_command = command
                        # noinspection PyBroadException
                        try:
                            For_command_stack.remove(For_command)
                        except Exception:
                            # TODO smalers 2017-12-21 might need to log as mismatched nested loops
                            # print('Error removing For loop from stack for EndFor(Name="' +
                            #      EndFor_command.get_name() + '"...)')
                            pass
                        for_index = GeoProcessor.__lookup_for_command_index(command_list, EndFor_command.get_name())
                        i_command = for_index - 1  # Decrement by one because the main loop will increment
                        logger.debug('Jumping to command [' + str(i_command + 1) + '] at top of For() loop')
                        continue
                    else:
                        # A typical command - run it
                        # - exceptions for CommandParameterError and CommandError are handled below and unexpected
                        #   errors of other types are added to the command log
                        # - this detects unknown Python coding errors
                        command.run_command()
                        # TODO smalers 2020-03-22 not sure these comments or concerns are relevant anymore
                        # If the command generated an output file, add it to the list of output files.
                        # The list is used by the UI to display results.
                        # TODO smalers 2017-12-21 - add the file list generator like TSEngine
                # if isinstance(command, If):
                if command_class == 'If':
                    # Add to the If command stack
                    If_command_stack.append(command)
                    # Re-evaluate If stack
                    # noinspection PyPep8Naming
                    If_stack_ok_to_run = GeoProcessor.__evaluate_if_stack(If_command_stack)
                # elif isinstance(command, EndIf):
                elif command_class == 'EndIf':
                    # Remove from the If command stack (generate a warning if the matching If()
                    # is not found in the stack)
                    # noinspection PyPep8Naming
                    EndIf_command = command
                    # noinspection PyPep8Naming
                    If_command = GeoProcessor.__lookup_if_command(If_command_stack, EndIf_command.get_name())
                    if If_command is None:
                        # TODO smalers 2017-12-21 need to log error
                        message = 'Unable to find matching If() command for Endif(Name="' + \
                            EndIf_command.get_name() + '")'
                        command.command_status.add_to_log(
                            CommandPhaseType.RUN,
                            CommandLogRecord(CommandStatusType.FAILURE, message,
                                             "Confirm that matching If() and EndIf() commands are specified."))
                    else:
                        # Run the command so the status is set to success
                        EndIf_command.run_command()
                        If_command_stack.remove(If_command)
                    # Reevaluate If stack
                    # noinspection PyPep8Naming
                    If_stack_ok_to_run = GeoProcessor.__evaluate_if_stack(If_command_stack)
                    logger.debug('...back from running command')
                # The following message brackets any command class run_command messages that may be generated
                message = '<- End processing command ' + str(i_command + 1) + ' of ' + str(n_commands) + ': ' + \
                          command.command_string
                logger.info(message)
                # logger.info("Notify Command Processor Listener of Command Completed")
                # Notify listeners that the command has completed
                self.notify_command_processor_listener_of_command_completed(i_command, n_commands, command)
            except CommandParameterError as cpe:
                # Will be raised by command.check_command_parameters() when parsing the command
                logger.warning("Error in command parameter(s) ({}).".format(cpe), exc_info=True)
                # Notify listeners that the command has completed
                warning_count += 1
                self.notify_command_processor_listeners_of_command_exception(i_command, n_commands, command)
            except CommandError as ce:
                # Will be raised by command.run_command() when running the command
                logger.warning("Error in running command ({}).".format(ce), exc_info=True)
                # Notify listeners that the command has completed
                warning_count += 1
                self.notify_command_processor_listeners_of_command_exception(i_command, n_commands, command)
            except Exception:
                message = "Unexpected error processing command - unable to complete command"
                logger.warning(message, exc_info=True)
                # Don't raise an exception because want all commands to run as best they can, each with
                # message logging, so that user can troubleshoot all at once rather than first error at a time
                # Do add to the command log so that the exception will be known to the software developer and user,
                # typically requiring code changes.
                command.command_status.add_to_log(
                    CommandPhaseType.RUN,
                    CommandLogRecord(CommandStatusType.FAILURE, message, "See the log file for details."))
                # Notify listeners that the command has completed
                warning_count += 1
                self.notify_command_processor_listeners_of_command_exception(i_command, n_commands, command)

        # The following checks to see if any warnings were caught in the above code.
        # If there were any warnings raise and exception.
        if warning_count > 0:
            message = "Errors found processing commands."
            logger.error(message)
            # raise RuntimeError(message)

        # TODO smalers 2020-03-09 need to evaluate how to deal with this
        # - listeners are notified when each command completes.  If the last command or Exit, the UI status is updated.
        # self.notify_command_list_processor_listener_of_all_commands_completed()

        # TODO smalers 2018-01-01 Java code has multiple checks at the end for checking error counts
        # - may or may not need something similar in Python code if above error-handling is not enough
        logger.info("At end of run_commands")

    def run_selected_commands(self, selected_indices: [int], command_list: [AbstractCommand] = None,
                              run_properties: dict = None, env_properties: dict = None) -> None:
        """
        Run only the selected commands from the command list.

        Args:
            selected_indices (int[]): The indices of the selected commands to run
            command_list (Command[]): The entire command list if necessary
            run_properties: Any run properties specified
            env_properties: Any environment properties specified

        Returns:
            None
        """
        logger = logging.getLogger(__name__)
        if command_list is not None:
            logger.warning("Processor 'command_list' is not implemented.")
        if run_properties is not None:
            logger.warning("Processor 'run_properties' is not implemented.")
        if env_properties is not None:
            logger.warning("Processor 'env_properties' is not implemented.")

        # Create a blank array of commands
        command_list = []

        # Sort the selected indices so they are run in the proper order, top - down
        selected_indices.sort()
        # Append the selected commands to the command_list array defined above
        for index in selected_indices:
            command_list.append(self.commands[index])

        # Pass the newly created command list to run_commands to run only the selected commands
        self.run_commands(command_list)

    def set_command_strings(self, command_strings: [str]) -> None:
        """
        Set the command strings and initialize the command list in the geoprocessor.
        This is similar to reading the commands file a file, but instead use in-memory string list.
        TODO smalers 2017-12-30 This function may be deleted once the operational command file runner
        and test framework is in place.

        Args:
            command_strings (str[]):  List of command strings.

        Returns:
            None
        """
        logger = logging.getLogger(__name__)

        # Create an instance of the GeoProcessorCommandFactory.
        command_factory = GeoProcessorCommandFactory()

        # Iterate over command string.
        for command_string in command_strings:

            # Initialize the command object (without parameters) - still have to parse to fully initialize.
            # Work is done in the GeoProcessorCommandFactory class.
            command_object = command_factory.new_command(command_string, True)

            # Initialize the parameters of the command object.
            # Work is done in the AbstractCommand class.
            command_object.initialize_command(command_string, self, True)

            # Append the initialized command (object with parameters) to the geoprocessor command list.
            self.commands.append(command_object)

            # TODO smalers 2017-12-30 the following included because of troubleshooting bug in
            # GeoProcessorCommandFactory
            debug = False
            if debug:
                command_object.print_for_debug()
                logger.debug("First command debug:")
                self.commands[0].print_for_debug()

    def set_properties(self, property_dict: dict) -> None:
        """
        Set geoprocessor properties from the specified dictionary.
        This is used, for example, when setting the environment properties before running.

        Args:
            property_dict (dict):  Dictionary of properties.

        Returns:
            None.
        """
        if property_dict is not None:
            for key in property_dict:
                self.properties[key] = property_dict[key]

    def set_property(self, property_name: str, property_value: None) -> None:
        """
        Set a geoprocessor property.

        Args:
            property_name (str):  Property name.
            property_value (object):  Value of property, can be any built-in Python type or class instance.

        Returns:
            None
        """
        self.properties[property_name] = property_value

    def update_command(self, index: int, command_string: str) -> None:
        """
        If the command has been edited by a command editor it must be updated in the command list.

        Args:
            index (int): the index of the command string to update
            command_string (str): The new command string to initialize a new command that will
                replace the old command in that position.

        Returns:
            None
        """
        command_factory = GeoProcessorCommandFactory()

        command_object = command_factory.new_command(command_string, True)

        # Initialize the parameters of the command object.
        # Work is done in the AbstractCommand class.
        command_object.initialize_command(command_string, self, True)

        self.commands[index] = command_object

        # GeoProcessorCommandFactory
        debug = False
        if debug:
            command_object.print_for_debug()
            logger = logging.getLogger(__name__)
            logger.debug("First command debug:")
            self.commands[0].print_for_debug()
