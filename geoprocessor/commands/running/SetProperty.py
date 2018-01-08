# SetProperty command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.validators as validators

import logging


class SetProperty(AbstractCommand):
    """
    The SetProperty command sets a processor property.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("PropertyName", type("")),
        CommandParameterMetadata("PropertyType", type("")),
        CommandParameterMetadata("PropertyValue", type(""))
    ]

    def __init__(self):
        """
        Initialize a command instance.
        """
        # AbstractCommand data
        super(SetProperty, self).__init__()
        self.command_name = "SetProperty"
        self.command_parameter_metadata = self.__command_parameter_metadata

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
        # TODO smalers 2017-12-25 need to log the warnings
        pv_PropertyName = self.get_parameter_value(parameter_name='PropertyName', command_parameters=command_parameters)
        if not validators.validate_string(pv_PropertyName, False, False):
            message = "PropertyName parameter has no value."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify a property name."))
            print(message)
        pv_PropertyType = self.get_parameter_value(parameter_name='PropertyType', command_parameters=command_parameters)
        property_types = ["bool", "float", "int", "long", "str"]
        if not validators.validate_string_in_list(pv_PropertyType, property_types, False, False):
            message = 'The requested property type "' + pv_PropertyType + '"" is invalid.'
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify a valid property type:  " +
                                 str(property_types)))
            print(message)
        pv_PropertyValue = self.get_parameter_value(
            parameter_name='PropertyValue', command_parameters=command_parameters)
        if not validators.validate_string(pv_PropertyValue, False, False):
            # TODO smalers 2017-12-28 add other parameters similar to TSTool to set special values
            message = "PropertyValue parameter is not specified."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify a property value."))
            print(message)

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception
        if len(warning) > 0:
            # Message.printWarning ( warning_level,
            #    MessageUtil.formatMessageTag(command_tag, warning_level), routine, warning );
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def run_command(self):
        warning_count = 0
        logger = logging.getLogger(__name__)

        pv_PropertyName = self.get_parameter_value('PropertyName')
        pv_PropertyType = self.get_parameter_value('PropertyType')
        pv_PropertyValue = self.get_parameter_value('PropertyValue')
        # Expand the property value string before converting to the requested type
        pv_PropertyValue_expanded = self.command_processor.expand_parameter_value(pv_PropertyValue)

        try:
            # Convert the property value string to the requested type
            pv_PropertyValue2 = None
            if pv_PropertyType == 'bool':
                pv_PropertyValue2 = bool(pv_PropertyValue_expanded)
            elif pv_PropertyType == 'float':
                pv_PropertyValue2 = float(pv_PropertyValue_expanded)
            elif pv_PropertyType == 'int':
                pv_PropertyValue2 = int(pv_PropertyValue_expanded)
            elif pv_PropertyType == 'str':
                pv_PropertyValue2 = str(pv_PropertyValue_expanded)
            # Now set the object as a property, will be the requested type
            if pv_PropertyValue2 is not None:
                self.command_processor.set_property(pv_PropertyName, pv_PropertyValue2)
        except Exception as e:
            warning_count += 1
            message = 'Unexpected error setting property "' + pv_PropertyName + '"'
            logger.exception(message, e)
            self.command_status.add_to_log(
                command_phase_type.RUN,
                CommandLogRecord(command_status_type.FAILURE, message,
                                 "Check the log file for details."))

        if warning_count > 0:
            message = "There were " + warning_count + " warnings processing the command."
            raise RuntimeError(message)

        self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
