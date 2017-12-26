# For command

import geoprocessor.commands.abstract.AbstractCommand as AbstractCommand
import geoprocessor.commands.abstract.command_phase_type as command_phase_type
import geoprocessor.commands.abstract.command_status_type as command_status_type
import geoprocessor.commands.abstract.CommandLogRecord as CommandLogRecord
import geoprocessor.core.CommandParameterMetadata as CommandParameterMetadata
import geoprocessor.util.command as util_command
import geoprocessor.util.validators as validators

# Inherit from AbstractCommand
class For(AbstractCommand.AbstractCommand):
    def __init__(self):
        super(For, self).__init__()
        # AbstractCommand
        self.command_name = "For"
        self.command_parameter_metadata = [
            CommandParameterMetadata.CommandParameterMetadata("Name",type(""),None),
            CommandParameterMetadata.CommandParameterMetadata("IteratorProperty",type(""),None),
            # Use strings for sequence because could be integer, decimal, or string list.
            CommandParameterMetadata.CommandParameterMetadata("SequenceStart",type(""),None),
            CommandParameterMetadata.CommandParameterMetadata("SequenceEnd",type(""),None),
            CommandParameterMetadata.CommandParameterMetadata("SequenceIncrement",type(""),None)
        ]

        # Local data
        self.for_initialized = False

        # Used with sequence iterator
        self.iterator_is_sequence = False
        self.iterator_sequence_start = None
        self.iterator_sequence_end = None
        self.iterator_sequence_increment = None

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
        # TODO smalers 2017-12-25 need to log
        pv_Name = self.get_parameter_value('Name')
        if not validators.validate_string(self.get_parameter_value('Name'),False,False):
            message = "A name for the For block must be specified"
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify the Name."))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = util_command.validate_command_parameter_names ( self, warning )

        # If any warnings were generated, throw an exception
        if len(warning > 0):
            #Message.printWarning ( warning_level,
            #    MessageUtil.formatMessageTag(command_tag, warning_level), routine, warning );
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION,command_status_type.SUCCESS)

    def get_name(self):
        '''Return the name of the EndIf (will match name of corresponding For)'''
        return self.command_parameters.get("Name", None)

    def next(self):
        '''
        Increment the loop counter.
        If called the first time, initialize.
        This may be called before run_commands() in the processor so process properties here.
        If the increment will go past the end, return false.
        '''
        if ( self.for_initialized == False ):
            # Initialize the loop
            if ( self.iterator_is_list ):
                # TODO smalers 2017-12-21 see TSTool command to fill out layer list
                pass
            elif ( self.iterator_is_sequence ):
                pass
            elif ( self.iterator_is_table ):
                # TODO smalers 2017-12-21 see TSTool command to fill out table
                pass
            else:
                # TODO smalers 2017-12-21 need to throw exception
                pass
        else:
            # Increment the property and optioanl set properties from table columns
            if ( (self.iterator_is_list == True) or (self.iterator_is_table == True) ):
                # TODO smalers 2017-12-21 see TSTool command to fill out layer list, table
                pass
            elif ( self.iterator_is_sequence == True ):
                # If the iterator object is already at or will exceed the maximum, then
                # done iterating
                # TODO smalers 2017-12-21 verify that Python handles typing automatically for integers and doubles
                #if (((type(self.iterator_sequence_start) == 'int') &&
                if ( (self.iterator_object >= self.iterator_sequence_end) or
                    (self.iteratorObject + self.iterator_sequence_increment > self.iterator_sequence_end) ):
                    return False
                else:
                    # Iterate by adding increment to iterator object
                    # TODO smalers 2017-12-21 verify that Python handles typing automatically for integers and doubles
                    self.iterator_object = self.iterator_object + self.iterator_sequency_increment;
                    return True
            else:
                # Iteration type not recognized so jump out right away to avoid infinite loop
                return True

    def reset_command(self):
        '''
        Reset the command to uninitialized state.
        This is needed to ensure that re-executing commands will
        restart the loop on the first call to next().
        '''
        self.for_initialized = False

    def run_command(self):
        print("In For.run_command")