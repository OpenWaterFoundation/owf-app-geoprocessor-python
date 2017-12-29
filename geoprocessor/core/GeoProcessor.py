# OWF Geoprocessing
import geoprocessor.core.GeoProcessorCommandFactory as CommandFactory
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.util.command as command_util

# QGIS Geoprocessing
from qgis.core import QgsApplication
# TODO smalers 2017-12-29 is the following QGIS or Emma's initial code?
from processing.core.Processing import Processing

# General modules
import os
import sys
import traceback

class GeoProcessor():
    """
    Overarching class that performs the work of the geoprocessing tool
    by executing a sequence of commands.
    """

    def __init__(self):
        """
        Construct/initialize a geoprocessor.
        """

        # command list: holds all command objects to run
        self.commands = []

        # property dictionary: holds all geoprocessor properties
        # temp_dir: the full pathname to the folder that will hold all temporary, intermediate files created by the
        # geoprocessor
        # qgis_prefix_path: the full pathname to the qgis install folder (often C:\OSGeo4W\apps\qgis)
        self.properties = {"temp_dir": None,
                           "qgis_prefix_path": None}

        # geolayer dictionary: holds all of the geoprocessor geolayers
        # key: geolayer id
        # value: list of geolayer properties
        # list item1: the QGSVectorLayer object, list item2: the full pathname to the original source spatial data file
        self.geolayers = {}

        # geolist dictionary: holds all of the geoprocessor geolists
        # key: geolist id
        # value: list of geolayer ids
        self.geolists = {}

        # set properties
        self.set_property("temp_dir", r"C:\Users\intern1\Desktop\OWF_spatialProcessor\temp")
        self.set_property("qgis_prefix_path", r"C:\OSGeo4W\apps\qgis")

    def __evaluate_if_stack(self, If_command_stack ):
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
            if (If_command.get_condition_eval() == False ):
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
        if parameter_value == None or len(parameter_value) == 0:
            # Just return what was provided.
            return parameter_value

        debug = False # For developers
        # First replace escaped characters.
        # TODO smalers 2017-12-25 might need to change this for Python
        parameter_value = parameter_value.replace("\\\"", "\"" )
        parameter_value = parameter_value.replace("\\'", "'" )
        # Else see if the parameter value can be expanded to replace ${} symbolic references with other values
        # Search the parameter string for $ until all processor parameters have been resolved
        search_pos = 0 # Position in the "parameter_value" string to search for ${} references
        found_pos = -1 # Position when leading "${" is found
        found_pos_end = -1 # Position when ending "}" is found
        prop_name = None # Whether a property is found that matches the "$" character
        delim_start = "${" # Start of property
        delim_end = "}" # End of property
        while search_pos < len(parameter_value):
            found_pos = parameter_value.find(delim_start, search_pos)
            found_pos_end = parameter_value.find(delim_end, (search_pos + len(delim_start)))
            if found_pos < 0 and found_pos_end < 0:
                # No more $ property names, so return what have.
                return parameter_value
            # Else found the delimiter so continue with the replacement
            # Message.printStatus(2, routine, "Found " + delimStart + " at position [" + foundPos + "]");
            if debug:
                print("Found " + delim_start + " at position [" + str(found_pos) + "]")
            # Get the name of the property
            prop_name = parameter_value[(found_pos + 2):found_pos_end]
            if debug:
                print('Property name is "' + prop_name + '"')
            # Try to get the property from the processor
            # TODO smalers 2007-12-23 Evaluate whether to skip None.  For now show "None" in result.
            propval = None
            propval_string = ""
            try:
                if debug:
                    print('Getting property value for "' + prop_name + '"')
                propval = self.get_property ( prop_name )
                if debug:
                    print('Property value is "' + propval + '"')
                # The following should work for all representations as long as str() does not truncate
                # TODO smalers 2017-12-28 confirm that Python shows numbers with full decimal, not scientific notation.
                propval_string = "" + str(propval)
            except:
                # Keep the original literal value to alert user that property could not be expanded
                if debug:
                    print('Exception getting the property value from the processor')
                propval_string = delim_start + prop_name + delim_end
            if propval == None:
                # Keep the original literal value to alert user that property could not be expanded
                propval_string = delim_start + prop_name + delim_end
            # If here have a property
            #b = new StringBuffer()
            b = ""
            # Append the start of the string
            if found_pos > 0:
                # b.append ( parameter_value[0:found_pos] )
                b = b + parameter_value[0:found_pos]
            # Now append the value of the property.
            #b.append(propval_string)
            b = b + propval_string
            # Now append the end of the original string if anything is at the end...
            if len(parameter_value) > (found_pos_end + 1):
                # b.append ( parameter_value[(found_pos_end + 1):]
                b = b + parameter_value[(found_pos_end + 1):]
            # Now reset the search position to finish evaluating whether to expand the string.
            #parameter_value = b.toString()
            parameter_value = b
            search_pos = found_pos + len(propval_string) # Expanded so no need to consider delim *
            if debug:
                #    Message.printDebug( 1, routine, "Expanded parameter value is \"" + parameter_value +
                #    "\" searchpos is now " + searchPos + " in string \"" + parameter_value + "\"" );
                print('Expanded parameter value is "' + parameter_value +
                    '" searchpos is now ' + str(search_pos) + ' in string "' + parameter_value + '"' )
        return parameter_value

    def get_property(self, property_name, if_not_found_val=None):
        """
        Get a geoprocessor property, case-specific.

        Args:
            property_name:  Name of the property for which a value is retrieved.
            if_not_found_val:  Value to return if the property is not found (None is default or otherwise throw exception).
        """
        try:
            return self.properties[property_name]
        except:
            if if_not_found_val == None:
                # Requested that None is returned if not found so do it
                #print('Property not found so returning None')
                return None
            else:
                # Let the exception from not finding a key in the dictionary be raised
                #print('Property not found so throwing exception')
                traceback.print_exc(file=sys.stdout)
                raise

    def __lookup_endfor_command_index(self, command_list, for_name ):
        """
        Lookup the command index for the EndFor() command with requested name.

        Args:
            command_list: list of commands to check
            for_name: the name of the "For" name to find

        Returns:
            The index (0+) of the EndFor() command that matches the specified name.
        """
        i = -1;
        for i_command in range(len(command_list)):
            command = command_list[i_command]
            command_class = command.__class__.__name__
            if ( command_class == 'EndFor' ):
                if ( command.get_name() == for_name ):
                    return i_command
        return -1

    def __lookup_for_command_index(self, command_list, for_name ):
        """
        Lookup the command index for the For() command with requested name.

        Args:
            command_list: list of commands to check
            for_name: the name of the "For" name to find
        """
        i = -1;
        for i_command in range(len(command_list)):
            command = command_list[i_command]
            command_class = command.__class__.__name__
            if ( command_class == 'For' ):
                if ( command.get_name() == for_name ):
                    return i_command
        return -1

    def __lookup_if_command(self, If_command_stack, if_name ):
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

    def read_command_file(self, command_file):
        """
        Read a command file and initialize the command list in the geoprocessor.

        Args:
            command_file: Name of the command file to read.
        """

        # Create an instance of the GeoProcessorCommandFactory.
        command_factory_object = CommandFactory.GeoProcessorCommandFactory()

        # Get a list of command file strings (each line of the command file is its own item in the list).
        command_file_strings = command_util.read_file_into_string_list(command_file)

        # Iterate over each line in the command file.
        for command_file_string in command_file_strings:

            # Initialize the command object (without parameters).
            # Work is done in the GeoProcessorCommandFactory class.
            command_object = command_factory_object.new_command(command_file_string, True)

            # Initialize the parameters of the command object.
            # Work is done in the AbstractCommand class.
            command_object.initialize_command(command_file_string, self, True)

            # Append the initialized command (object with parameters) to the geoprocessor command list.
            self.commands.append(command_object)

    def reset_data_for_run_start(self):
        """
        Reset the processor data prior to running the commands.
        This ensures that the command processor state from one run is isolated from the next run.
        """
        # TODO smalers 2017-12-21 see TSEngine
        pass

    def run_commands(self, command_list = None):
        """
        Run the commands that exist in the processor.

        Args:
            command_list: List of command objects to process, or None to process all commands in the processor.
        """

        # TODO smalers 2017-12-29 what happens if this is done more than once?
        # Initialize QGIS resources to utilize QGIS functionality.
        QgsApplication.setPrefixPath(self.get_property("qgis_prefix_path"), True)
        qgs = QgsApplication([], True)
        qgs.initQgis()
        Processing.initialize()

        if command_list == None:
            print("Running all commands")
            command_list = self.commands
        else:
            print("Running specified command list")

        # Reset any properties left over from the previous run that may impact the current run
        self.reset_data_for_run_start()

        # Whether or no the command is whethin a /*   */ comment block
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
            if command == None:
                continue
            command_class = command.__class__.__name__
            if command_class == 'For':
                command.reset_command()
            # Clear the command log.
            command.command_status.clear_log(command_phase_type.RUN)

        # Run all the commands
        # Set debug = True to turn on debug messages
        debug = False
        # Python does not allow modifying the for loop iterator variable so use a while loop
        #for i_command in range(n_commands):
        i_command = -1
        while i_command < n_commands:
            i_command = i_command + 1
            if i_command == n_commands:
                # Do an extra check on the index to make sure because for loops can modify the index
                # prior to the increment statement above.
                break
            command = command_list[i_command]
            if debug:
                command.print_for_debug()

            if not in_comment and If_stack_ok_to_run:
                print('-> Start processing command ' + str(i_command + 1) + ' of ' + str(n_commands) + ': ' + command.command_string)

            command_class = command.__class__.__name__
            if command_class == 'For':
                # Reset the For command
                command.reset_command

            if in_comment and If_stack_ok_to_run == True:
                pass

            if command_class == 'Comment':
                # Hash-comment - TODO need to mark as processing successful
                continue
            elif command_class == 'CommentStart':
                # /* comment block start - TODO need to mark as processing successful
                in_comment = True
                continue
            elif command_class == 'CommentEnd':
                # */ comment block end - TODO need to mark as processing successful
                in_comment = False
                continue

            if in_comment:
                # In a /* */ comment block so set status to successful
                continue

            else:
                try:
                    # TODO smalers 2017-12-21 this is in TSTool but need to confirm if really need - redundant?
                    # - comment out of the geoprocessor
                    # Initialize the command for running
                    # - this reparses the commands and parameters
                    # - this clears out previous results
                    #command.initialize_command( command.command_string, self, True )

                    # Check the command parameters
                    # - this is called when editing the command but also need to check here when running
                    # - the list of parameters is passed because the code is reused with editors that check
                    #   parameters before saving the edits
                    command.check_command_parameters( command.command_parameters )

                    # Check to see whether the If stack evaluates to True and can run the command
                    # - evaluation of the stack only occurs when an If() is encountered
                    if If_stack_ok_to_run:
                        # Run the command
                        if ( command_class == 'Exit'):
                            # Exit command causes hard exit - following commands are ignored
                            break
                        elif ( command_class == 'For'):
                            # Initialize or increment the For loop
                            print('Detected For command')
                            # Use a local variable For_command for clarity
                            For_command = command
                            ok_to_run_for = False
                            try:
                                ok_to_run_for = For_command.next()
                                print('ok_to_run_for=' + str(ok_to_run_for))
                                # If False, the For loop is done.
                                # However, need to handle the case where the for loop may be nested and need to run again...
                                if not ok_to_run_for:
                                    For_command.reset_command()
                            except:
                                # This is serious and can lead to an infinite loop so generate an exception and jump to the
                                # end of the loop
                                ok_to_run_for = False
                                traceback.print_exc(file=sys.stdout)
                                print('Error going to next iteration.  Check For() command iteration data.')
                                # Same logic as ending the loop...
                                end_for_index = self.__lookup_endfor_command_index(command_list,For_command.get_name())
                                if ( end_for_index >= 0 ):
                                    i_command = end_for_index # OK because don't want to trigger EndFor() going back to the top
                                    continue
                                else:
                                    # Did not match the end of the For() so generate an error and exit
                                    need_to_interrupt = True
                                    raise Exception('Unable to match For loop name "' + For_command.get_name() + '" in EndFor() commands.')
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
                                end_for_index = self.__lookup_endfor_command_index(command_list,For_command.get_name())
                                # Modify the main command loop index and continue - the command after the end will be executed (or done)
                                if ( end_for_index >= 0 ):
                                    i_command = end_for_index # Loop will increment so EndFor will be skipped, which is OK - otherwise infinite loop
                                    continue
                                else:
                                    # Did not match the end of the For() so generate an error and exit
                                    need_to_interrupt = True
                                    raise Exception('Unable to match For loop name "' + For_command.get_name() + '" in EndFor() commands.')
                        elif ( command_class == 'EndFor' ):
                            # Jump to the matching For()
                            EndFor_command = command;
                            try:
                                For_command_stack.remove(For_command)
                            except:
                                # TODO smalers 2017-12-21 might need to log as mismatched nested loops
                                print('Error removing For loop from stack for EndFor(Name="' + EndFor_command.get_name() + '"...)')
                            for_index = self.__lookup_for_command_index(command_list,EndFor_command.get_name())
                            i_command = for_index - 1 # Decrement by one because the main loop will increment
                            print('Jumping to commmand [' + str(i_command + 1) + '] at top of For() loop')
                            continue
                        else:
                            # A typical command - run it
                            command.run_command()
                            # If the command generated an output file, add it to the list of output files.
                            # The list is used by the UI to display results.
                            # TODO smalers 2017-12-21 - add the file list generator like TSEngine
                    if ( command_class == 'If' ):
                        # Add to the If command stack
                        If_command_stack.append(command)
                        # Re-evaluate If stack
                        If_stack_ok_to_run = self.__evaluate_if_stack(If_command_stack)
                    elif ( command_class == 'EndIf' ):
                        # Remove from the If command stack (generate a warning if the matching If() is not found in the stack
                        EndIf_command = command
                        If_command = self.__lookup_if_command ( If_command_stack, EndIf_command.get_name )
                        if ( If_command == None ):
                            # TODO smalers 2017-12-21 need to log error
                            pass
                        else:
                            # Run the command so the status is set to success
                            EndIf_command.run_command()
                            If_command_stack.remove(If_command)
                        # Reevaluate If stack
                        If_stack_ok_to_run = self.__evaluate_if_stack(If_command_stack)
                        print('...back from running command')
                except:
                    # TODO smalers 2017-12-21 need to expand on error handling
                    traceback.print_exc(file=sys.stdout)
                    raise Exception('Error running command ' + command.command_name )

        # Close QGIS resources
        qgs.exit()

    def process_command_file(self, command_file):
        """
        Reads the command file and runs the commands within the command file.

        Args:
            command_file The name of the command file to read.
        """

        self.read_command_file(command_file)
        self.run_commands()

    def set_command_strings(self, command_strings):
        """
        Set the command strings and initialize the command list in the geoprocessor.
        This is similar to reading the commands file a file, but instead use in-memory string list

        Args:
            command_strings:  List of command strings.
        """

        # Create an instance of the GeoProcessorCommandFactory.
        command_factory_object = CommandFactory.GeoProcessorCommandFactory()

        # Iterate over command string.
        for command_string in command_strings:

            # Initialize the command object (without parameters) - still have to parse to fully initialize.
            # Work is done in the GeoProcessorCommandFactory class.
            command_object = command_factory_object.new_command(command_string, True)

            # Initialize the parameters of the command object.
            # Work is done in the AbstractCommand class.
            command_object.initialize_command(command_string, self, True)

            # Append the initialized command (object with parameters) to the geoprocessor command list.
            self.commands.append(command_object)

            debug = True
            if debug:
                command_object.print_for_debug()
                print("First command debug:")
                self.commands[0].print_for_debug()

    def set_property(self, property_name, property_value):
        """
        Set a geoprocessor property

        Args:
            property_name:  Property name.
            property_value:  Value of property, can be any object type.
        """
        self.properties[property_name] = property_value

####################### WORKING ENVIRONMENT ###############################
#if __name__ == "__main__":

#    cmdFileDir = (os.path.dirname(os.path.realpath(__file__))).replace("core", "command_files")
#    processor = GeoProcessor()
#    processor.process_command_file(os.path.join(cmdFileDir, "create_layers_test.txt"))
