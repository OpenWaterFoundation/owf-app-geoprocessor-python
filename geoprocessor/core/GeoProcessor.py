# OWF GeoProcessor class, which is able to process a workflow of commands described in a command file.

from geoprocessor.core.GeoProcessorCommandFactory import GeoProcessorCommandFactory
from geoprocessor.core.CommandLogRecord import CommandLogRecord
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

# Commands that need special handling (all others are handled generically and don't need to be imported)
# TODO smalers 2018-01-08 Evaluate enabling with `isinstance` syntax but could not get it to work as intended
# import geoprocessor.commands.running.For as EndFor
# import geoprocessor.commands.running.For as EndIf
# import geoprocessor.commands.running.For as For
# import geoprocessor.commands.running.For as If

import geoprocessor.util.command_util as command_util

from processing.core.Processing import Processing

# General modules
import getpass
import logging
import os
import platform
import sys
import tempfile
from time import gmtime, strftime
import traceback


class GeoProcessor(object):
    """
    Overarching class that performs the work of the geoprocessing tool
    by executing a sequence of commands.
    """

    def __init__(self):
        """
        Construct/initialize a geoprocessor.
        """

        # Command list that holds all command objects to run.
        self.commands = []

        # Property dictionary that holds all geoprocessor properties.
        self.properties = {}

        # geolayers list that holds all registered GeoLayer objects.
        self.geolayers = []

        # geolayerlists list that holds all registered GeoList objects.
        self.geolayerlists = []

        # Set properties for QGIS environment.
        # qgis_prefix_path: the full pathname to the qgis install folder (often C:\OSGeo4W\apps\qgis)
        # TODO smalers 2017-12-30 Need to rework to not hard code.
        # - Need to pass in QGIS configuration from the startup batch file or script.
        self.set_property("qgis_prefix_path", r"C:\OSGeo4W\apps\qgis")

        # Set the initial working directory properties prior to reading a command file.
        # Reading the command file should reset these properties.
        # TODO smalers 2017-12-30 need to handle "New command file" action when UI is implemented.
        cwd = os.getcwd()
        self.properties["InitialWorkingDir"] = os.path.dirname(cwd)
        self.properties["WorkingDir"] = os.path.dirname(cwd)

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

    def add_geolayer(self, geolayer):
        """
        Add a GeoLayer object to the geolayers list. If a geolayer already exists with the same GeoLayer ID, the
        existing GeoLayer will be overwritten with the input GeoLayer.

        Args:
            geolayer: instance of a GeoLayer object

        Return: None
        """

        # Iterate over the existing GeoLayers.
        for existing_geolayer in self.geolayers:

            # If an existing GeoLayer has the same ID as the input GeoLayer, remove the existing GeoLayer from the
            # geolayers list.
            if existing_geolayer.id == geolayer.id:
                self.free_geolayer(existing_geolayer)

        # Add the input GeoLayer to the geolayers list.
        self.geolayers.append(geolayer)

    @classmethod
    def __evaluate_if_stack(cls, If_command_stack):
        """
        Evaluate whether If stack evaluates to True.

        Loop through the list of If_Command and evaluate the overall condition statement.
        All conditions must be true for nested if statements to allow execution of commands in the block.

        Args:
            If_command_stack: list of If commands to check.

        Return:
            True if all the If commands evaluate to True, False otherwise.
        """
        for i_if_command in range(len(If_command_stack)):
            If_command = If_command_stack[i_if_command]
            if not If_command.get_condition_eval():
                return False
        return True

    def expand_parameter_value(self, parameter_value, command=None):
        """
        Expand a command parameter value (string) into full string.
        This function is a port of the Java TSCommandProcessorUtil.expandParameterValue() method.

        Args:
            parameter_value: Command parameter value as string to expand.
                The parameter value can include ${Property} notation to indicate a processor property.
            command:  A command instance (will be used in the future if command property syntax needs to be expanded,
                for example using syntax ${c:Property}).

        Returns:
            Expanded parameter value string.
        """
        debug = False  # For developers
        if debug:
            print('parameter_value=' + str(parameter_value))
        if parameter_value is None or len(parameter_value) == 0:
            # Just return what was provided.
            return parameter_value

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
        delim_start = "${"  # Start of property
        delim_end = "}"  # End of property
        while search_pos < len(parameter_value):
            found_pos_start = parameter_value.find(delim_start, search_pos)
            found_pos_end = parameter_value.find(delim_end, (search_pos + len(delim_start)))
            if found_pos_start < 0 and found_pos_end < 0:
                # No more $ property names, so return what have.
                return parameter_value
            # Else found the delimiter so continue with the replacement
            # Message.printStatus(2, routine, "Found " + delimStart + " at position [" + foundPos + "]")
            if debug:
                print("Found " + delim_start + " at position [" + str(found_pos_start) + "]")
            # Get the name of the property
            prop_name = parameter_value[(found_pos_start + 2):found_pos_end]
            if debug:
                print('Property name is "' + prop_name + '"')
            # Try to get the property from the processor
            # TODO smalers 2007-12-23 Evaluate whether to skip None.  For now show "None" in result.
            propval = None
            propval_string = ""
            try:
                if debug:
                    print('Getting property value for "' + prop_name + '"')
                propval = self.get_property(prop_name)
                if debug:
                    print('Property value is "' + propval + '"')
                # The following should work for all representations as long as str() does not truncate
                # TODO smalers 2017-12-28 confirm that Python shows numbers with full decimal, not scientific notation.
                propval_string = "" + str(propval)
            except Exception as e:
                # Keep the original literal value to alert user that property could not be expanded
                if debug:
                    print('Exception getting the property value from the processor')
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
                print('Expanded parameter value is "' + parameter_value +
                      '" searchpos is now ' + str(search_pos) + ' in string "' + parameter_value + '"')
        return parameter_value

    def free_geolayer(self, geolayer):
        """
        Removes a GeoLayer object from the geolayers list.

        Args:
            geolayer: instance of a GeoLayer object

        Return:
            Nothing
        """
        self.geolayers.remove(geolayer)

    def get_geolayer(self, geolayer_id):
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

    def get_geolayerlist(self, geolayerlist_id):
        """
        Return the GeoLayerList that has the requested ID.

        Args:
            geolayerlist_id (str):  GeoLayerList ID string.

        Returns:
            The GeoLayerList that has the requested ID, or None if not found.
        """
        for geolayerlist in self.geolayerlists:
            if geolayerlist is not None:
                if geolayerlist.id == geolayerlist_id:
                    # Found the requested identifier
                    return geolayerlist
        # Did not find the requested identifier so return None
        return None

    def get_property(self, property_name, if_not_found_val=None):
        """
        Get a GeoProcessor property, case-specific.

        Args:
            property_name:  Name of the property for which a value is retrieved.
            if_not_found_val:  Value to return if the property is not found
                (None is default or otherwise throw an exception).
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

    @classmethod
    def __lookup_endfor_command_index(cls, command_list, for_name):
        """
        Lookup the command index for the EndFor() command with requested name.

        Args:
            command_list: list of commands to check
            for_name: the name of the "For" name to find

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
    def __lookup_for_command_index(cls, command_list, for_name):
        """
        Lookup the command index for the For() command with requested name.

        Args:
            command_list: list of commands to check
            for_name: the name of the "For" name to find
        """
        for i_command in range(len(command_list)):
            command = command_list[i_command]
            command_class = command.__class__.__name__
            if command_class == 'For':
                if command.get_name() == for_name:
                    return i_command
        return -1

    @classmethod
    def __lookup_if_command(cls, If_command_stack, if_name):
        """
        Lookup the command for the If() command with requested name.

        Args:
            If_command_stack: list of If commands that are active.
            if_name: the name of the "If" command to find

        Returns:
            The matching If() command instance.
        """
        for c in If_command_stack:
            if c.get_name() == if_name:
                return c
        return None

    # TODO smalers 2017-12-31 Need to switch to CommandFileRunner class
    def process_command_file(self, command_file):
        """
        Reads the command file and runs the commands within the command file.

        Args:
            command_file (str): The name of the command file to read.
        """

        self.read_command_file(command_file)
        self.run_commands()

    def read_command_file(self, command_file, create_unknown_command_if_not_recognized=True,
                          append_commands=False, run_discovery_on_load=True):
        """
        Read a command file and initialize the command list in the geoprocessor.
        The processor properties "InitialWorkingDir" and "WorkingDir" are set to the command file folder,
        or the current working directory if the path to the command file is not absolute.

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
        """

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

        # Create an instance of the GeoProcessorCommandFactory.
        command_factory = GeoProcessorCommandFactory()

        # Get a list of command file strings (each line of the command file is its own item in the list).
        command_file_strings = command_util.read_file_into_string_list(command_file)

        # Iterate over each line in the command file.
        for command_file_string in command_file_strings:

            # Initialize the command object (without parameters).
            # Work is done in the GeoProcessorCommandFactory class.
            command_object = command_factory.new_command(
                command_file_string,
                create_unknown_command_if_not_recognized)

            # Initialize the parameters of the command object.
            # Work is done in the AbstractCommand class.
            command_object.initialize_command(command_file_string, self, True)

            # Append the initialized command (object with parameters) to the geoprocessor command list.
            self.commands.append(command_object)

            debug = False
            if debug:
                command_object.print_for_debug()
                print("First command debug:")
                self.commands[0].print_for_debug()

    def __reset_data_for_run_start(self, append_results=False):
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
        """
        # The following are the initial defaults...
        # TODO smalers 2017-12-30 Clear any hashtables used to increase performance, currently none
        self.properties["InputStart"] = None
        self.properties["InputEnd"] = None
        self.properties["OutputStart"] = None
        self.properties["OutputEnd"] = None
        self.properties["OutputYearType"] = None
        # Free all data from the previous run rather than append
        if append_results:
            # All in-memory lists of results, such as layers, should be cleared.
            # If a list (future design change?)...
            # del self.GeoLayers[:]
            # del self.GeoLists[:]
            # ...but currently a dictionary...
            self.geolayers.clear()
            # TODO smalers 2018-01-27 Need to decide whether to remove lists since not currently used
            self.geolayerlists.clear()

    def __reset_workflow_properties(self):
        """
        Reset the workflow global properties to defaults, necessary when a command processor is rerun.
        This function is called by the run_commands() function before processing any commands.
        This function is ported from the Java TSCommandProperties.resetWorkflowProperties() method.

        Returns:
            Nothing.
        """

        # Java code uses separate properties rather than Python using one dictionary.
        # Therefore protect the properties that should absolutely not be reset.
        # First clear properties, including user-defined properties, but protect fundamental properties that
        # should not be reset (such as properties that are difficult to reset).
        # Check size dynamically in case props are removed below
        # Because the dictionary size may change during iteration, can't do the following
        #     for property_name, property_value in self.properties.iteritems():
        # Cannot iterate through a dictionary and remove items from dictionary.
        # Therefore convert the dictionary to a list and iterate on the list
        processor_property_names = list(self.properties.keys())
        protected_property_names = ["InitialWorkingDir", "WorkingDir"]
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

    def run_commands(self, command_list=None, run_properties=None):
        """
        Run the commands that exist in the processor.

        Args:
            command_list: List of command objects to process, or None to process all commands in the processor.
                A list is typically provided when a subset of commands has been selected in the UI.
            run_properties:  Properties used to control the run.
                This function only acts on the following properties:
                    ResetWorkflowProperties:  Global properties such as run period should be reset before running.
                        The default is True.  This property is used with the RunCommands command to preserve properties.
        """
        # Logger for the processor
        logger = logging.getLogger(__name__)

        # Reset the global workflow properties if requested, used when RunCommands command calls recursively...
        # - This code is a port of Java TSCommandProcessor.runCommands().
        reset_workflow_properties = True
        if run_properties is None:
            # Reset to an empty dictionary to simplify error handling below
            run_properties = {}
        try:
            prop_value = run_properties.getValue("ResetWorkflowProperties")
            if prop_value is not None and prop_value == "False":
                reset_workflow_properties = False
        except:
            # Property not set so use default value
            pass
        if reset_workflow_properties:
            self.__reset_workflow_properties()
        # ...end reset of global workflow properties

        # The remainder of this code is a port of the Java TSEngine.processCommands() function.

        # Indicate whether results should be cleared between runs.
        # If true, do not clear results between recursive calls.
        # This is used with a master command file that runs other command files with RunCommands commands.
        append_results = False
        # Indicate whether a recursive run of the processor is being made (e.g., because RunCommands() is used).
        recursive = False
        append_results = False
        try:
            recursive_prop = run_properties["Recursive"]
            if recursive_prop == "True":
                recursive = True
                # Default for recursive runs is to NOT append results...
                append_results = False
        except:
            # Recursive property was not defined so not running in recursive mode
            recursive = False
        try:
            append_prop = run_properties["AppendResults"]
            if append_prop == "True":
                append_results = True
        except:
            # Use default value from above
            pass

        logger.info("Recursive=" + str(recursive) + " AppendResults=" + str(append_results))

        if command_list is None:
            logger.info("Running all commands")
            command_list = self.commands
        else:
            logger.info("Running specified command list")

        # Reset any properties left over from the previous run that may impact the current run.
        self.__reset_data_for_run_start()

        # Whether or no the command is within a /*   */ comment block
        in_comment = False

        # Initialize the If() command stack that is in effect, needed to nest If() commands
        If_command_stack = []

        # Initialize the For() command stack that is in effect, needed to nest For() commands
        For_command_stack = []

        # Whether the If stack evaluates to True so enclosed commands can run
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
            command.command_status.clear_log(command_phase_type.RUN)

        # Run all the commands
        # - set debug = True to turn on debug messages
        debug = False
        # Python does not allow modifying the for loop iterator variable so use a while loop
        # for i_command in range(n_commands):
        i_command = -1
        while i_command < n_commands:
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

                if not in_comment and If_stack_ok_to_run:
                    message='-> Start processing command ' + str(i_command + 1) + ' of ' + str(n_commands) + ': ' + \
                        command.command_string
                    # print(message)
                    logger.info(message)

                command_class = command.__class__.__name__

                if command_class == 'Comment':
                    # Hash-comment - TODO need to mark as processing successful - confirm when UI in place
                    continue
                elif command_class == 'CommentBlockStart':
                    # /* comment block start - TODO need to mark as processing successful - confirm when UI in place
                    in_comment = True
                    continue
                elif command_class == 'CommentBlockEnd':
                    # */ comment block end - TODO need to mark as processing successful - confirm when UI in place
                    in_comment = False
                    continue

                if in_comment:
                    # In a /* */ comment block so set status to successful
                    continue

                # TODO smalers 2017-12-21 this is in TSTool but need to confirm if really need - redundant?
                # - probably need for the UI since the processor will be re-run multiple times
                # - comment out of the geoprocessor
                # Initialize the command for running
                # - this reparses the commands and parameters
                # - this clears out previous results
                # command.initialize_command( command.command_string, self, True )

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
                        break
                    # elif isinstance(command, For):
                    elif command_class == 'For':
                        # Initialize or increment the For loop
                        logger.info('Detected For command')
                        # Use a local variable For_command for clarity
                        For_command = command
                        ok_to_run_for = False
                        try:
                            ok_to_run_for = For_command.next()
                            # print('ok_to_run_for=' + str(ok_to_run_for))
                            # If False, the For loop is done.
                            # However, need to handle the case where the for loop may be nested and need to run again...
                            if not ok_to_run_for:
                                For_command.reset_command()
                        except:
                            # This is serious and can lead to an infinite loop so generate an exception and
                            # jump to the end of the loop
                            ok_to_run_for = False
                            message = 'Error going to next iteration.'
                            logger.warning(message, exc_info=True)
                            command.command_status.add_to_log(
                                command_phase_type.RUN,
                                CommandLogRecord(
                                    command_status_type.FAILURE, message,
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
                                    command_phase_type.RUN,
                                    CommandLogRecord(command_status_type.FAILURE, message,
                                                     "Add a matching EndFor() command."))
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
                                    command_phase_type.RUN,
                                    CommandLogRecord(command_status_type.FAILURE, message,
                                                     "Add a matching EndFor() command."))
                                raise RuntimeError(message)
                    # elif isinstance(command,EndFor):
                    elif command_class == 'EndFor':
                        # Jump to the matching For()
                        EndFor_command = command
                        try:
                            For_command_stack.remove(For_command)
                        except:
                            # TODO smalers 2017-12-21 might need to log as mismatched nested loops
                            # print('Error removing For loop from stack for EndFor(Name="' +
                            #      EndFor_command.get_name() + '"...)')
                            pass
                        for_index = GeoProcessor.__lookup_for_command_index(command_list, EndFor_command.get_name())
                        i_command = for_index - 1  # Decrement by one because the main loop will increment
                        logger.debug('Jumping to commmand [' + str(i_command + 1) + '] at top of For() loop')
                        continue
                    else:
                        # A typical command - run it
                        command.run_command()
                        # If the command generated an output file, add it to the list of output files.
                        # The list is used by the UI to display results.
                        # TODO smalers 2017-12-21 - add the file list generator like TSEngine
                # if isinstance(command, If):
                if command_class == 'If':
                    # Add to the If command stack
                    If_command_stack.append(command)
                    # Re-evaluate If stack
                    If_stack_ok_to_run = GeoProcessor.__evaluate_if_stack(If_command_stack)
                # elif isinstance(command, EndIf):
                elif command_class == 'EndIf':
                    # Remove from the If command stack (generate a warning if the matching If()
                    # is not found in the stack)
                    EndIf_command = command
                    If_command = GeoProcessor.__lookup_if_command(If_command_stack, EndIf_command.get_name)
                    if If_command is None:
                        # TODO smalers 2017-12-21 need to log error
                        message = 'Unable to find matching If() command for Endif(Name="' + \
                            EndIf_command.get_name() + '")'
                        command.command_status.add_to_log(
                            command_phase_type.RUN,
                            CommandLogRecord(command_status_type.FAILURE, message,
                                             "Confirm that matching If() and EndIf() commands are specified."))
                    else:
                        # Run the command so the status is set to success
                        EndIf_command.run_command()
                        If_command_stack.remove(If_command)
                    # Reevaluate If stack
                    If_stack_ok_to_run = GeoProcessor.__evaluate_if_stack(If_command_stack)
                    logger.debug('...back from running command')
            except Exception as e:
                # TODO smalers 2017-12-21 need to expand error handling by type but for now catch generically
                # because Python exception handling uses fewer exception classes than Java dode to keep simple
                traceback.print_exc(file=sys.stdout)  # Formatting of error seems to have issue
                message = "Unexpected error processing command - unable to complete command"
                logger.error(message, e, exc_info=True)
                # Don't raise an exception because want all commands to run as best they can, each with
                # message logging, so that user can troubleshoot all at once rather than first error at a time
                command.command_status.add_to_log(
                    command_phase_type.RUN,
                        CommandLogRecord(command_status_type.FAILURE, message, "See the log file for details."))
            except:
               message = "Unexpected error processing command - unable to complete command"
               logger.error(message, exc_info=True)
               # Don't raise an exception because want all commands to run as best they can, each with
               # message logging, so that user can troubleshoot all at once rather than first error at a time
               command.command_status.add_to_log(
                   command_phase_type.RUN,
                   CommandLogRecord(command_status_type.FAILURE, message, "See the log file for details."))

        # TODO smalers 2018-01-01 Java code has multiple checks at the end for checking error counts
        # - may or may not need something similar in Python code if above error-handling is not enough
        logger.info("At end of run_commands")

    def set_command_strings(self, command_strings):
        """
        Set the command strings and initialize the command list in the geoprocessor.
        This is similar to reading the commands file a file, but instead use in-memory string list.
        TODO smalers 2017-12-30 This function may be deleted once the operational command file runner
        and test framework is in place.

        Args:
            command_strings:  List of command strings.
        """

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
                print("First command debug:")
                self.commands[0].print_for_debug()

    def set_property(self, property_name, property_value):
        """
        Set a geoprocessor property

        Args:
            property_name (str):  Property name.
            property_value (object):  Value of property, can be any built-in Python type or class instance.
        """
        self.properties[property_name] = property_value
