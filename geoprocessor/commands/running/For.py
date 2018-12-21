# For command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.string_util as string_util
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
        CommandParameterMetadata("SequenceIncrement", type("")),
        # Specify the list property to use for iteration
        CommandParameterMetadata("ListProperty", type("")),
        # Specify the following to iterate over a table.
        CommandParameterMetadata("TableID", type("")),
        CommandParameterMetadata("TableColumn", type("")),
        CommandParameterMetadata("TablePropertyMap", type("")),
    ]

    def __init__(self):
        """
        Initialize an instance of the command.
        """
        super().__init__()
        # AbstractCommand data
        self.command_name = "For"
        self.command_description = "Indicate the start of a 'For' block"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Local data
        self.for_initialized = False  # For loop is not initialized, will be initialized in first next() call

        # Iterator core data
        # - used with all iterator types
        self.iterator_object = None  # The current object for the iterator
        self.iterator_object_list_index = None  # The index in the iterator object list, 0-reference
        self.iterator_property = None  # The name of the property that set for the iterator variable

        # Utility data to simplify checks for type of iteration (only one should be set to True)
        self.iterator_is_list = False
        self.iterator_is_sequence = False
        self.iterator_is_table = False

        # Used with sequence iterator
        self.iterator_sequence_start = None
        self.iterator_sequence_end = None
        self.iterator_sequence_increment = None

        # Used with list iterator
        self.iterator_list = None  # The list of objects, typically str, being iterated over

        # Used with table iterator
        self.table = None
        self.table_column = None
        self.table_property_map = None

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning = ""
        logger = logging.getLogger(__name__)

        # Unlike most commands, set internal data here because it is needed by initial call to next()
        # before calls to run_command

        # Options for iterating, will be changed based on parameters that are set
        self.iterator_is_list = False
        self.iterator_is_sequence = False
        self.iterator_is_table = False
        option_count = 0  # How many iteration options are specified (should only be 1)

        # Name is required
        pv_Name = self.get_parameter_value(parameter_name='Name', command_parameters=command_parameters)
        if not validators.validate_string(pv_Name, False, False):
            message = "A name for the For block must be specified"
            recommendation = "Specify the Name."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # --------------------------------
        # Iterator option 1 - use a sequence
        # SequenceStart is currently required since no other iteration types are implemented
        pv_SequenceStart = self.get_parameter_value(
            parameter_name='SequenceStart', command_parameters=command_parameters)
        if pv_SequenceStart is not None and pv_SequenceStart != "":
            self.iterator_is_sequence = True  # Will be checked below to make sure only one option is used
            option_count += 1
            if not validators.validate_number(pv_SequenceStart, False, False):
                message = "The SequenceStart value must be specified as a number"
                recommendation = "Specify the SequenceStart as a number."
                warning += "\n" + message
                self.command_status.add_to_log(
                    command_phase_type.INITIALIZATION,
                    CommandLogRecord(command_status_type.FAILURE, message, recommendation))
            else:
                if pv_SequenceStart.find(".") >= 0:
                    # Decimal
                    self.iterator_sequence_start = float(pv_SequenceStart)
                else:
                    # Assume integer
                    self.iterator_sequence_start = int(pv_SequenceStart)

            # The other sequence parameters only make sense if the start is specified
            # SequenceEnd is currently required since no other iteration types are implemented
            pv_SequenceEnd = self.get_parameter_value(parameter_name='SequenceEnd', command_parameters=command_parameters)
            if not validators.validate_number(pv_SequenceEnd, False, False):
                message = "The SequenceEnd value must be specified as a number"
                recommendation = "Specify the SequenceEnd as a number."
                warning += "\n" + message
                self.command_status.add_to_log(
                    command_phase_type.INITIALIZATION,
                    CommandLogRecord(command_status_type.FAILURE, message, recommendation))
            else:
                if pv_SequenceEnd.find(".") >= 0:
                    # Decimal
                    self.iterator_sequence_end = float(pv_SequenceEnd)
                else:
                    # Assume integer
                    self.iterator_sequence_end = int(pv_SequenceEnd)

            # SequenceIncrement is currently required since no other iteration types are implemented
            pv_SequenceIncrement = self.get_parameter_value(
                parameter_name='SequenceIncrement', command_parameters=command_parameters)
            if not validators.validate_number(pv_SequenceIncrement, False, False):
                message = "The SequenceIncrement value must be specified as a number"
                recommendation = "Specify the SequenceIncrement as a number."
                warning += "\n" + message
                self.command_status.add_to_log(
                    command_phase_type.INITIALIZATION,
                    CommandLogRecord(command_status_type.FAILURE, message, recommendation))
            else:
                if pv_SequenceIncrement.find(".") >= 0:
                    # Decimal
                    self.iterator_sequence_increment = float(pv_SequenceIncrement)
                else:
                    # Assume integer
                    self.iterator_sequence_increment = int(pv_SequenceIncrement)

        # --------------------------------
        # Iterator option 2 - use a processor property that contains a list
        pv_ListProperty = self.get_parameter_value(parameter_name='ListProperty', command_parameters=command_parameters)
        if pv_ListProperty is not None and pv_ListProperty != "":
            self.iterator_is_list = True  # Will be checked below to make sure only one option is used
            option_count += 1
            # No further validation is done - ListProperty property must be defined at run time

        # --------------------------------
        # Iterator option 3 - use a table
        pv_TableID = self.get_parameter_value(parameter_name='TableID', command_parameters=command_parameters)
        if pv_TableID is not None and pv_TableID != "":
            self.iterator_is_table = True
            option_count += 1

            # TableColumn is required
            pv_TableColumn = self.get_parameter_value(parameter_name='TableColumn',
                                                      command_parameters=command_parameters)
            if not validators.validate_string(pv_TableColumn, False, False):
                message = "The TableColumn parameter must be specified"
                recommendation = "Specify the TableColumn."
                warning += "\n" + message
                self.command_status.add_to_log(
                    command_phase_type.INITIALIZATION,
                    CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # --------------------------------
        # Only allow one of the iteration properties to be specified because otherwise the command will be confused.
        if option_count > 1:
            message = "Parameters for multiple iterator types have been specified."
            recommendation = "Specify parameters for only one iteration type."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))
            # Allow multiple iteration types to be set since they will be processed in order when running
            # and the preferred approach will take precedent

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
        Return the name of the For (will match name of corresponding EndFor).

        Returns:
            The name of the For (will match name of corresponding EndFor).
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
        logger = logging.getLogger(__name__)
        if not self.for_initialized:
            # Initialize the loop
            logger.info("Initializing For() command")
            # Set the initialization here because exceptions could cause it to not get set and then
            # an infinite loop results
            self.for_initialized = True
            if self.iterator_is_list:
                logger.info("Initializing For() command for a list.")
                # Initialize the loop
                self.__set_iterator_property_value(None)
                self.command_status.clear_log(command_phase_type.RUN)
                try:
                    # This would normally be done in run_command(), but that function is not called like other commands
                    self.iterator_object_list_index = 0
                    pv_ListProperty = self.get_parameter_value('ListProperty')
                    self.iterator_list = self.command_processor.get_property(pv_ListProperty)
                    if self.iterator_list is None:
                        message = 'For command iterator list property "' + pv_ListProperty + '" is not defined.'
                        recommendation = "Confirm that the list property has values."
                        logger.warning(message)
                        self.command_status.add_to_log(
                            command_phase_type.RUN,
                            CommandLogRecord(command_status_type.FAILURE, message, recommendation))
                    else:
                        self.iterator_object = self.iterator_list[self.iterator_object_list_index]
                    # if ( Message.isDebugOn )
                    if debug:
                        logger.info("Initialized iterator object to first item in list: " + str(self.iterator_object))
                        return True
                except:
                    # message = "Error initializing For() iterator to initial value in list (" + e + ").";
                    message = "Error initializing For() iterator initial value to first item in list"
                    logger.warning(message, exc_info=True)
                    raise ValueError(message)
            elif self.iterator_is_sequence:
                # Iterating on a sequence
                logger.info("Initializing For() command for a sequence.")
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
                    # if ( Message.isDebugOn )
                    if debug:
                        logger.info("Initialized iterator object to sequence start: " + str(self.iterator_object))
                        return True
                except:
                    # message = "Error initializing For() iterator to initial value (" + e + ").";
                    message = "Error initializing For() iterator initial value to sequence start"
                    logger.warning(message, exc_info=True)
                    raise ValueError(message)
            elif self.iterator_is_table:
                # Iterating over a table
                logger.info("Initializing For() command for a table.")
                # Initialize the loop
                self.__set_iterator_property_value(None)
                self.command_status.clear_log(command_phase_type.RUN)
                try:
                    # Get TableID parameter value. If required, expand for ${Property} syntax.
                    pv_TableID = self.get_parameter_value(parameter_name='TableID')
                    pv_TableID = self.command_processor.expand_parameter_value(pv_TableID, self)
                    # Get TableColumn parameter value. If required, expand for ${Property} syntax.
                    pv_TableColumn = self.get_parameter_value(parameter_name='TableColumn')
                    pv_TableColumn = self.command_processor.expand_parameter_value(pv_TableColumn, self)
                    # Get the table pandas data frame object
                    self.table = self.command_processor.get_table(pv_TableID)
                    # Get the TablePropertyMap
                    pv_TablePropertyMap = self.get_parameter_value(parameter_name='TablePropertyMap')
                    # Assign as class variable after converting from string to dictionary
                    self.table_property_map = string_util.delimited_string_to_dictionary_one_value(pv_TablePropertyMap,
                                                                                                   entry_delimiter=",",
                                                                                                   key_value_delimiter=":",
                                                                                                   trim=False)
                    # Get the values of the input column as a list
                    self.iterator_object_list_index = 0
                    self.iterator_list = self.table.get_column_values_as_list(pv_TableColumn)


                    if self.iterator_list is None:
                        message = 'For command iterator table column "' + pv_TableColumn + '" is not defined.'
                        recommendation = "Confirm that the table column has values."
                        logger.warning(message)
                        self.command_status.add_to_log(
                            command_phase_type.RUN,
                            CommandLogRecord(command_status_type.FAILURE, message, recommendation))
                    else:
                        self.iterator_object = self.iterator_list[self.iterator_object_list_index]
                        # Set the other property values if configured.
                        if self.table_property_map:
                            self.__next_set_properties_from_table()
                    # if ( Message.isDebugOn )
                    if debug:
                        logger.info("Initialized iterator object to first item in list: " + str(self.iterator_object))
                        return True
                except:
                    # message = "Error initializing For() iterator to initial value (" + e + ").";
                    message = "Error initializing For() iterator initial value to sequence start"
                    logger.warning(message, exc_info=True)
                    raise ValueError(message)

            else:
                # TODO smalers 2017-12-21 need to throw exception
                pass
        else:
            # Increment the iterator property
            # - optionally set additional properties from other table columns (tables not yet supported)
            if self.iterator_is_list:
                # If the iterator object is already at or will exceed the list length if incremented, then done iterating
                # - len() is 1-based, index is 0-based
                if self.iterator_object_list_index >= (len(self.iterator_list) - 1):
                    logger.info("Iterator has reached list end.  Returning False from next().")
                    return False
                else:
                    # Iterate by incrementing list index and returning corresponding list object
                    self.iterator_object_list_index += 1
                    self.iterator_object = self.iterator_list[self.iterator_object_list_index]
                    logger.info("Iterator value is now " + str(self.iterator_object) + ".  Returning True from next().")
                    return True
            elif self.iterator_is_sequence:
                # If the iterator object is already at or will exceed the maximum, then done iterating
                # TODO smalers 2017-12-21 verify that Python handles typing automatically for integers and doubles
                # if (((type(self.iterator_sequence_start) == 'int') &&
                if self.iterator_object >= self.iterator_sequence_end or \
                        (self.iterator_object + self.iterator_sequence_increment) > self.iterator_sequence_end:
                    logger.info("Iterator has reached end value.  Returning False from next().")
                    return False
                else:
                    # Iterate by adding increment to iterator object
                    # TODO smalers 2017-12-21 verify that Python handles typing automatically for integers and doubles
                    self.iterator_object = self.iterator_object + self.iterator_sequence_increment
                    logger.info("Iterator value is now " + str(self.iterator_object) + ".  Returning True from next().")
                    return True
            elif self.iterator_is_table:
                # If the iterator object is already at or will exceed the list length if incremented, then done iterating
                # - len() is 1-based, index is 0-based
                if self.iterator_object_list_index >= (len(self.iterator_list) - 1):
                    logger.info("Iterator has reached list end.  Returning False from next().")
                    return False
                else:
                    # Iterate by incrementing list index and returning corresponding list object
                    self.iterator_object_list_index += 1
                    self.iterator_object = self.iterator_list[self.iterator_object_list_index]
                    logger.info("Iterator value is now " + str(self.iterator_object) + ".  Returning True from next().")
                    # Set the other property values if configured.
                    if self.table_property_map:
                        self.__next_set_properties_from_table()
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
        logger = logging.getLogger(__name__)
        self.for_initialized = False
        logger.info('Reset For loop to uninitialized')

    def run_command(self):
        """
        Run the command.  This initializes the iterator data for use when next() is called by the processor.

        Returns:
            None.
        """
        logger = logging.getLogger(__name__)
        logger.info("In For.run_command")
        pv_Name = self.get_parameter_value('Name')
        pv_IteratorProperty = self.get_parameter_value('IteratorProperty')
        if pv_IteratorProperty is None or pv_IteratorProperty == "":
            # Default to same as Name
            pv_IteratorProperty = pv_Name
        self.iterator_property = pv_IteratorProperty
        # -------------------------------------------------------------------------------
        # Properties used when iterating over a sequence of integers or decimal numbers
        # -------------------------------------------------------------------------------
        pv_SequenceStart = self.get_parameter_value('SequenceStart')
        if pv_SequenceStart is not None and pv_SequenceStart != "":
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
            if pv_SequenceIncrement is None or pv_SequenceIncrement == "":
                pv_SequenceIncrement = "1"  # Default
            if pv_SequenceIncrement.find(".") >= 0:
                # Decimal
                self.iterator_sequence_increment = float(pv_SequenceIncrement)
            else:
                # Assume integer
                self.iterator_sequence_increment = int(pv_SequenceIncrement)
            self.iterator_is_list = False
            self.iterator_is_sequence = True
            self.iterator_is_table = False
        # -------------------------------------------------------------------------------
        # Properties used when iterating over a list of values
        # - initially str is used in testing but may support list of numbers
        # -------------------------------------------------------------------------------
        pv_ListProperty = self.get_parameter_value('ListProperty')
        if pv_ListProperty is not None:
            # Iterating over a list, given by the property
            self.iterator_list = self.command_processor.get_property(pv_ListProperty)
            if self.iterator_list is None:
                message = 'For command iterator list property "' + pv_ListProperty + '" is not defined.'
                recommendation = "Confirm that the list property has values."
                logger.warning(message)
                self.command_status.add_to_log(
                    command_phase_type.RUN,
                    CommandLogRecord(command_status_type.FAILURE, message, recommendation))
            self.iterator_is_list = True
            self.iterator_is_sequence = False
            self.iterator_is_table = False
        # -------------------------------------------------------------------------------
        # Properties used when iterating over a table
        # -------------------------------------------------------------------------------

        # next() will have been called by the command processor so at this point just set the processor property.
        # Set the basic property as well as the property with 0 and 1 at end of name indicating zero and 1 offset.

        self.command_processor.set_property(pv_IteratorProperty, self.iterator_object)

    def __set_iterator_property_value(self, iterator_property_value):
        """
        Set the value of the iterator property (index), used when iterating over a list.

        Args:
            iterator_property_value:

        Returns:
            None.
        """
        self.iterator_object = iterator_property_value

    def __next_set_properties_from_table(self):

        # Get the iterator object list index
        index = self.iterator_object_list_index

        # Get the pandas data frame object for the table being iterated
        df = self.table.df

        # Get the pandas row that is currently being iterated over.
        row = df.iloc[index]

        # Iterate over the entries in the table_property_map dictionary.
        # key is the property name and value is the corresponding column name
        for column, property in self.table_property_map.items():

            # Get the value for the given column and the current row.
            property_val = row[column]

            # Assign the geoprocessor property the corresponding value.
            self.command_processor.set_property(property, property_val)

