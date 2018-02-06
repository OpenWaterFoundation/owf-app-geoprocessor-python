# For command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validators

import logging
import sys
import traceback


class For(AbstractCommand):
    """
    The For command starts a For block.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("Name", type("")),
        CommandParameterMetadata("IteratorProperty", type("")),
        # Use strings for sequence because could be integer, decimal, or string list.
        CommandParameterMetadata("SequenceStart", type("")),
        CommandParameterMetadata("SequenceEnd", type("")),
        CommandParameterMetadata("SequenceIncrement", type(""))
    ]

    def __init__(self):
        """
        Initialize an instance of the command.
        """
        super(For, self).__init__()
        # AbstractCommand data
        self.command_name = "For"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Local data
        self.for_initialized = False

        # Iterator core data
        self.iterator_object = None
        self.iterator_object_list_index = None
        self.iterator_property = None

        # Utility data to simplify checks for type of iteration (only one should be set to True)
        self.iterator_is_list = False
        self.iterator_is_sequence = False
        self.iterator_is_table = False

        # Used with sequence iterator
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
        logger = logging.getLogger(__name__)

        # Name is required
        pv_Name = self.get_parameter_value(parameter_name='Name', command_parameters=command_parameters)
        if not validators.validate_string(pv_Name, False, False):
            message = "A name for the For block must be specified"
            recommendation = "Specify the Name."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # SequenceStart is currently required since no other iteration types are implemented
        pv_SequenceStart = self.get_parameter_value(
            parameter_name='SequenceStart', command_parameters=command_parameters)
        if not validators.validate_number(pv_SequenceStart, False, False):
            message = "The SequenceStart value must be specified"
            recommendation = "Specify the SequenceStart as a number."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # SequenceEnd is currently required since no other iteration types are implemented
        pv_SequenceEnd = self.get_parameter_value(parameter_name='SequenceEnd', command_parameters=command_parameters)
        if not validators.validate_number(pv_SequenceEnd, False, False):
            message = "The SequenceEnd value must be specified"
            recommendation = "Specify the SequenceEnd as a number."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # SequenceIncrement is currently required since no other iteration types are implemented
        pv_SequenceIncrement = self.get_parameter_value(
            parameter_name='SequenceIncrement', command_parameters=command_parameters)
        if not validators.validate_number(pv_SequenceIncrement, False, False):
            message = "The SequenceIncrement value must be specified"
            recommendation = "Specify the SequenceIncrement as a number."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Unlike most commands, set internal data here because it is needed by next() before calls to run_command

        if pv_SequenceStart.find(".") >= 0:
            # Decimal
            self.iterator_sequence_start = float(pv_SequenceStart)
        else:
            # Assume integer
            self.iterator_sequence_start = int(pv_SequenceStart)

        if pv_SequenceEnd.find(".") >= 0:
            # Decimal
            self.iterator_sequence_end = float(pv_SequenceEnd)
        else:
            # Assume integer
            self.iterator_sequence_end = int(pv_SequenceEnd)

        if pv_SequenceIncrement.find(".") >= 0:
            # Decimal
            self.iterator_sequence_increment = float(pv_SequenceIncrement)
        else:
            # Assume integer
            self.iterator_sequence_increment = int(pv_SequenceIncrement)

        # TODO smalers 2017-12-29 for now hard code sequence
        self.iterator_is_list = False
        self.iterator_is_sequence = True
        self.iterator_is_table = False

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception
        if len(warning) > 0:
            logger.warn(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def get_name(self):
        """
        Return the name of the EndIf (will match name of corresponding For).

        Returns:
            The name of the EndIf (will match name of corresponding For).
        """
        return self.get_parameter_value("Name")

    def next(self):
        """
        Increment the loop counter.
        If called the first time, initialize.
        This may be called before run_commands() in the processor so process properties here.

        Returns:
            If the increment will go past the end, return False.  Otherwise, return True.
        """
        debug = True
        if not self.for_initialized:
            # Initialize the loop
            print("Initializing For() command")
            if self.iterator_is_list:
                # TODO smalers 2017-12-21 see TSTool command to fill out layer list
                pass
            elif self.iterator_is_sequence:
                # Iterating on a sequence
                print("Initializing For() command for a sequence.")
                # Initialize the loop
                self.__set_iterator_property_value(None)
                self.command_status.clear_log(command_phase_type.RUN)
                try:
                    self.iterator_object_list_index = 0
                    self.iterator_object = self.iterator_sequence_start
                    if self.iterator_sequence_increment is None:
                        # Default increment is 1 or 1.0
                        if type(self.iterator_sequence_start) == 'int':
                            self.iterator_sequence_increment = 1
                        elif type(self.iterator_sequence_start) == 'float':
                            self.iterator_sequence_increment = 1.0
                    self.for_initialized = True
                    # if ( Message.isDebugOn )
                    if debug:
                        # Message.printDebug(1, routine, "Initialized iterator object to: " + this.iteratorObject );
                        print("Initialized iterator object to: " + str(self.iterator_object))
                        return True
                except:
                    # message = "Error initializing For() iterator to initial value (" + e + ").";
                    message = "Error initializing For() iterator to initial value"
                    traceback.print_exc(file=sys.stdout)
                    raise ValueError(message)
            elif self.iterator_is_table:
                # TODO smalers 2017-12-21 see TSTool command to fill out table
                pass
            else:
                # TODO smalers 2017-12-21 need to throw exception
                pass
        else:
            # Increment the property and optional set properties from table columns
            if self.iterator_is_list or self.iterator_is_table:
                # TODO smalers 2017-12-21 see TSTool command to fill out layer list, table
                pass
            elif self.iterator_is_sequence:
                # If the iterator object is already at or will exceed the maximum, then
                # done iterating
                # TODO smalers 2017-12-21 verify that Python handles typing automatically for integers and doubles
                # if (((type(self.iterator_sequence_start) == 'int') &&
                if self.iterator_object >= self.iterator_sequence_end or \
                        (self.iterator_object + self.iterator_sequence_increment) > self.iterator_sequence_end:
                    print("Iterator has reached end value.  Returning False from next().")
                    return False
                else:
                    # Iterate by adding increment to iterator object
                    # TODO smalers 2017-12-21 verify that Python handles typing automatically for integers and doubles
                    self.iterator_object = self.iterator_object + self.iterator_sequence_increment
                    print("Iterator value is now " + str(self.iterator_object) + ".  Returning True from next().")
                    return True
            else:
                # Iteration type not recognized so jump out right away to avoid infinite loop
                return True

    def reset_command(self):
        """
        Reset the command to uninitialized state.
        This is needed to ensure that re-executing commands will
        restart the loop on the first call to next().
        """
        self.for_initialized = False

    def run_command(self):
        """
        Run the command.  This initializes the iterator data for use when next() is called by the processor.

        Returns:
            Nothing.
        """
        print("In For.run_command")
        pv_Name = self.get_parameter_value('Name')
        pv_IteratorProperty = self.get_parameter_value('IteratorProperty')
        if pv_IteratorProperty is None or pv_IteratorProperty == "":
            # Default to same as Name
            pv_IteratorProperty = pv_Name
        self.iterator_property = pv_IteratorProperty
        pv_SequenceStart = self.get_parameter_value('SequenceStart')
        if pv_SequenceStart.find(".") >= 0:
            # Decimal
            self.iterator_sequence_start = float(pv_SequenceStart)
        else:
            # Assume integer
            self.iterator_sequence_start = int(pv_SequenceStart)
        pv_SequenceEnd = self.get_parameter_value('SequenceEnd')
        if pv_SequenceEnd.find(".") >= 0:
            # Decimal
            self.iterator_sequence_end = float(pv_SequenceEnd)
        else:
            # Assume integer
            self.iterator_sequence_end = int(pv_SequenceEnd)
        pv_SequenceIncrement = self.get_parameter_value('SequenceIncrement')
        if pv_SequenceIncrement.find(".") >= 0:
            # Decimal
            self.iterator_sequence_increment = float(pv_SequenceIncrement)
        else:
            # Assume integer
            self.iterator_sequence_increment = int(pv_SequenceIncrement)

        # Currently the iteration is always over a sequence
        self.iterator_is_list = False
        self.iterator_is_sequence = True
        self.iterator_is_table = False

        # next() will have been called by the command processor so at this point just set the processor property.
        # Set the basic property as well as the property with 0 and 1 at end of name indicating zero and 1 offset.

        self.command_processor.set_property(pv_IteratorProperty, self.iterator_object)

    def __set_iterator_property_value(self, iterator_property_value):
        """
        Set the value of the iterator property (index), used when iterating over a list.

        Args:
            iterator_property_value:

        Returns:
            Nothing.
        """
        self.iterator_object = iterator_property_value
