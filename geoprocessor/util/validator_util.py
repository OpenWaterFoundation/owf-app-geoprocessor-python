"""
Functions that provide validation for data values, in particular command parameters.
These functions are typically called from the check_command_parameters function
of commands to validate a parameter value.
Multiple functions may be called if necessary, although as many validator functions
as necessary can be defined.
"""
import os

import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.CommandLogRecord import CommandLogRecord

import geoprocessor.util.io_util as io_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.qgis_util as qgis_util

import urllib2

def run_check(self, condition, parameter_name, parameter_value, fail_response, other_values=None):
    """
    The run_check utility function is used to store all of the checks done within the command classes. There are
    many types of checks that are performed on the command parameter values before a command can be run. Initially,
    the GeoProcessor was designed in a way that the checks for each command class (including messages and
    recommendations) were within each command class. This new design allows for all of the messages and recommendations
    (quite clunky and ugly code) to be pulled away from the command class and placed in this utility function.

    A benefit to this design is that popular checks that are called on many commands (for example: is the CRS_code, the
    coordinate reference code, valid) are only written out once. Then the same check can be called from however many
    command classes necessary. If the message and recommendation strings are changed for a given check, those messages
    only have to be changed once here in this utility command rather than in multiple command classes.

    Each check has a name called the condition. The checks are alphabetized below by their condition statement. In
    the developer documentation there is explanation for each available check. This way, when there are additional
    parameters required (entered by the other_values parameter), the developer knows exactly what the check requires.
    Before utilizing a check in the command class, it is highly recommended that the developer documentation for that
    check if read.

    Each check condition statement is written in a way that answers YES (or TRUE) if the check passes. This makes it
    easy for checks to be written and standardized by multiple developers.

    Args:
        self: the class object of the command being checked
        condition: the condition statement (or name) of the check that is to be run
        parameter_name: the command parameter being checked (the name, not the value)
        parameter_value: the command parameter value being checked (the value, not the name)
        fail_responses: the action that occurs if the check fails. The available options are as follows:
            (1) FAIL: a FAIL message is logged and the function returns FALSE for run_the_command Boolean
            (2) WARN: a WARN message is logged and the function returns TRUE for run_the_command Boolean
            (3) WARNBUTDONOTRUN: a WARN message is logged and the function returns FALSE for run_the_command Boolean
        other_values: an optional argument that allows the checks to take in more than one parameter_value for the check
            refer to the developer documentation for each individual check to determine if the other_values argument is
            used for that check.

    Returns:
        run_the_command: Boolean. If True, the check has determined that it is ok for the command to run. If False, the
        check has determined that it is not ok for the command to run.
    """

    # Boolean to determine if the check failed. Set to FALSE until the check FAILS.
    check_failed = False

    # Check if the attributes in a list exist in a GeoLayer based off of its attribute name.
    if condition.upper() == "DOATTRIBUTESEXIST":
        geolayer_id = other_values[0]

        # Get the GeoLayer.
        input_geolayer = self.command_processor.get_geolayer(geolayer_id)

        # Get the existing attribute names of the input GeoLayer.
        list_of_existing_attributes = input_geolayer.get_attribute_field_names()

        # Create a list of invalid input attribute names. An invalid attribute name is an input attribute name
        # that is not matching any of the existing attribute names of the GeoLayer.
        invalid_attrs = []
        for attr in parameter_value:
            if attr not in list_of_existing_attributes:
                invalid_attrs.append(attr)

        # The message is dependent on the invalid_attrs varaible. Assign message AFTER invalid_attrs variable has been
        # created.
        message = "The following attributes ({}) of the {} parameter do" \
                  " not exist within the GeoLayer ({}).".format(invalid_attrs, parameter_name, geolayer_id)
        recommendation = "Specify valid attribute names."

        # If there are invalid attributes, the check failed.
        if invalid_attrs:
            check_failed = True

    # Check if the parameter value (absolute file path) has a valid and existing folder.
    elif condition.upper() == "DOESFILEPATHHAVEAVALIDFOLDER":

        message = 'The folder of the {} ({}) is not a valid folder.'.format(parameter_name, parameter_value)
        recommendation = "Specify a valid folder for the {} parameter.".format(parameter_name)

        output_folder = os.path.dirname(parameter_value)
        if not os.path.isdir(output_folder):
            check_failed = True

    # Check if the GeoLayer of the parameter value (GeoLayer ID) has the correct geometry type.
    elif condition.upper() == "DOESGEOLAYERIDHAVECORRECTGEOMETRY":
        desired_geom_type_list = [item.upper() for item in other_values[0]]

        message = 'The {} ({}) does not have geometry in the correct ' \
                  'format ({}).'.format(parameter_name, parameter_value, desired_geom_type_list)
        recommendation = 'Specify a GeoLayerID of a GeoLayer with geometry in' \
                         ' correct format ({}).'.format(desired_geom_type_list)

        if not self.command_processor.get_geolayer(parameter_value).get_geometry().upper() in desired_geom_type_list:
            check_failed = True

    # Check if the GeoLayer of the parameter value (GeoLayer ID) has a different CRS than another GeoLayer (referenced
    # by its GeoLayer ID)
    elif condition.upper() == "DOGEOLAYERIDSHAVEMATCHINGCRS":
        second_parameter_name = other_values[0]
        second_parameter_value = other_values[1]

        message = 'The {} ({}) and the {} ({}) do not have the same coordinate reference' \
                  ' system.'.format(parameter_name, parameter_value, second_parameter_name, second_parameter_value)
        recommendation = 'Specify GeoLayers that have the same coordinate reference system.'

        input_crs = self.command_processor.get_geolayer(parameter_value).get_crs()
        second_crs = self.command_processor.get_geolayer(second_parameter_value).get_crs()

        if not input_crs == second_crs:
            check_failed = True

    # Check if the parameter value (column name) is a valid column name of a delimited file.
    elif condition.upper() == "ISDELIMITEDFILECOLUMNNAMEVALID":

        delimited_file_abs = other_values[0]
        delimiter = other_values[1]

        message = "The {} ({}) is not a valid column name in the delimited file ({}).".format(parameter_name,
                                                                                              parameter_value,
                                                                                              delimited_file_abs)
        recommendation = "Specify an existing and valid {}.".format(parameter_name)

        if parameter_value not in io_util.get_col_names_from_delimited_file(delimited_file_abs, delimiter):
            check_failed = True

    # Check if the parameter value (crs code)is a valid CRS code usable in the QGIS environment.
    elif condition.upper() == "ISCRSCODEVALID":

        message = 'The {} ({}) is not a valid CRS code.'.format(parameter_name, parameter_value)
        recommendation = 'Specify a valid CRS code (EPSG codes are an approved format).'

        if qgis_util.get_qgscoordinatereferencesystem_obj(parameter_value) is None:
            check_failed = True

    # Check if the parameter value (absolute file path) is a valid and existing file.
    elif condition.upper() == "ISFILEPATHVALID":

        message = "The {} ({}) is not a valid file.".format(parameter_name, parameter_value)
        recommendation = "Specify a valid file for the {} parameter.".format(parameter_name)

        if not os.path.isfile(parameter_value):
            check_failed = True

    # Check if the parameter value (absolute folder path) is a valid and existing folder.
    elif condition.upper() == "ISFOLDERPATHVALID":

        message = "The {} ({}) is not a valid folder.".format(parameter_name, parameter_value)
        recommendation = "Specify a valid folder for the {} parameter.".format(parameter_name)

        if not os.path.isdir(parameter_value):
            check_failed = True

    # Check if the parameter value (GeoLayerID) is an existing GeoLayerID.
    elif condition.upper() == "ISGEOLAYERIDEXISTING":

        message = 'The {} ({}) is not a valid GeoLayer ID.'.format(parameter_name, parameter_value)
        recommendation = 'Specify a valid GeoLayer ID.'

        if not self.command_processor.get_geolayer(parameter_value):
            check_failed = True

    # Check if the parameter value (GeoLayer ID) is a unique GeoLayerID.
    elif condition.upper() == "ISGEOLAYERIDUNIQUE":
        message = 'The {} ({}) value is already in use as a GeoLayer ID.'.format(parameter_name, parameter_value)
        recommendation = 'Specify a new {}.'.format(parameter_name)

        if self.command_processor.get_geolayer(parameter_value):
            check_failed = True
            pv_IfGeoLayerIDExists = self.get_parameter_value("IfGeoLayerIDExists", default_value="Replace")

            if pv_IfGeoLayerIDExists.upper() == "REPLACEANDWARN":
                fail_response = "WARN"
            elif pv_IfGeoLayerIDExists.upper() == "WARN":
                fail_response = "WARNBUTDONOTRUN"
            elif pv_IfGeoLayerIDExists.upper() == "FAIL":
                fail_response = "FAIL"
            else:
                check_failed = False

    # Check if the parameter value (integer) is between or at two values/numbers.
    elif condition.upper() == "ISINTBETWEENRANGE":
        int_min = other_values[0]
        int_max = other_values[1]

        message = 'The {} ({}) must be at or between {} & {}'.format(parameter_name, parameter_value, int_min, int_max)
        recommendation = 'Specify a valid {} value.'.format(parameter_name)

        if not validate_int_in_range(parameter_value, int_min, int_max, False, False):
            check_failed = True

    # Check if the length of a list is correct.
    elif condition.upper() == "ISLISTLENGTHCORRECT":
        delimiter = other_values[0]
        correct_length = other_values[1]

        message = 'The {} ({}) must have {} number of items.'.format(parameter_name, parameter_value, correct_length)
        recommendation = 'Specify a list of {} items for the {} parameter.'.format(correct_length, parameter_name)

        # Convert the string into a list.
        list = string_util.delimited_string_to_list(parameter_value, delimiter)
        if len(list) != correct_length:
            check_failed = True

    # Check if the property name is a unique property name
    elif condition.upper() == "ISPROPERTYUNIQUE":

        message = 'The {} ({}) value is already in use.'.format(parameter_name, parameter_value)
        recommendation = 'Specify a new {}.'.format(parameter_name)

        if self.command_processor.get_property(parameter_value):
            check_failed = True
            pv_IfPropertyExists = self.get_parameter_value("IfPropertyExists", default_value="Replace")

            if pv_IfPropertyExists.upper() == "REPLACEANDWARN":
                fail_response = "WARN"
            elif pv_IfPropertyExists.upper() == "WARN":
                fail_response = "WARNBUTDONOTRUN"
            elif pv_IfPropertyExists.upper() == "FAIL":
                fail_response = "FAIL"
            else:
                check_failed = False

    # Check if the input string is a valid QGSExpression.
    elif condition.upper() == "ISQGSEXPRESSIONVALID":

        message = "{} ({}) is not a valid QgsExpression.".format(parameter_name, parameter_value)
        recommendation = "Specify a valid QgsExpression for {}.".format(parameter_name)

        if qgis_util.get_qgsexpression_obj(parameter_value) is None:
            check_failed = True

    # Check if the input string is a valid URL.
    elif condition.upper() == "ISURLVALID":

        message = "{} ({}) is not a valid URL.".format(parameter_name, parameter_value)
        recommendation = "Specify a valid URL for {}.".format(parameter_name)

        try:
            urllib2.urlopen(parameter_value)
        except:
            check_failed = True

    else:

        message = "Check {} is not a valid check in the validators library.".format(condition)
        recommendation = "Contact the maintainers of the GeoProcessor software."
        check_failed = True
        fail_response = "FAIL"

    # If the check failed, increase the warning count of the command instance by one.
    if check_failed:
        self.warning_count += 1

        # If configured, log a FAILURE message about the failed check. Set the run_the_command boolean to False.
        if fail_response.upper() == "FAIL":
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                    message, recommendation))
            run_the_command = False

        # If configured, log a WARNING message about the failed check. Set the run_the_command boolean to True.
        elif fail_response.upper() == "WARN":

            self.logger.warning(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.WARNING,
                                                            message, recommendation))
            run_the_command = True

        # If configured, log a WARNING message about the failed check. Set the run_the_command boolean to False.
        elif fail_response.upper() == "WARNBUTDONOTRUN":

            self.logger.warning(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.WARNING,
                                                            message, recommendation))
            run_the_command = False

    # If the check passed, set the run_the_command boolean to True.
    else:
        run_the_command = True

    # Return the run_the_command boolean.
    return run_the_command


def validate_bool(bool_value, none_allowed, empty_string_allowed):
    """
    Validate that a boolean value is True or False.

    Args:
        bool_value: Boolean value to check, can be string or bool type.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.

    Returns:
        True if bool value is valid, False if invalid.
    """
    # First check some specific cases
    if bool_value is None:
        if none_allowed:
            return True
        else:
            return False
    if isinstance(bool_value, str):
        if bool_value == "":
            if empty_string_allowed:
                return True
            else:
                return False
        # Reassign the value as a bool to check
        # Dangerous to use bool(bool_value) because True is returned for all sorts of things.
        # Therefore do a bit more work.
        bool_value_upper = bool_value.upper()
        if bool_value_upper == 'TRUE' or bool_value_upper == 'FALSE':
            return True
        else:
            return False

    # By definition bool can only be None, True, or False so all cases are handled above.
    return True


def validate_float(float_value, none_allowed, empty_string_allowed):
    """
    Validate that a floating point value is valid.

    Args:
        float_value: Floating point value to check, can be string or floating point (float) type.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.

    Returns:
        True if float value is valid, False if invalid.
    """
    # First check some specific cases
    if float_value is None:
        if none_allowed:
            return True
        else:
            return False
    if isinstance(float_value, str):
        if float_value == "":
            if empty_string_allowed:
                return True
            else:
                return False
        # Reassign the value as a float to check
        try:
            float(float_value)
        except ValueError:
            return False
    else:
        # May do more checks later but for now above should be sufficient
        pass
    return True


def validate_int(int_value, none_allowed, empty_string_allowed):
    """
    Validate that an integer value is valid.

    Args:
        int_value: Integer value to check, can be string or integer (int) type.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.

    Returns:
        True if integer value is valid, False if invalid.
    """
    # First check some specific cases
    if int_value is None:
        if none_allowed:
            return True
        else:
            return False
    if isinstance(int_value, str):
        if int_value == "":
            if empty_string_allowed:
                return True
            else:
                return False
        # Reassign the value as an integer to check
        try:
            int(int_value)
        except ValueError:
            return False
    else:
        # May do more checks later but for now above should be sufficient
        pass
    return True


def validate_int_in_range(int_value, int_min, int_max, none_allowed, empty_string_allowed):
    """
    Validate that an integer value is in a range.

    Args:
        int_value: Integer value to check, can be string or int type.
        int_min: Minimum acceptable value.
        int_max: Maximum acceptable value.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.

    Returns:
        True if integer value is valid, False if invalid.
    """
    # First check some specific cases
    if int_value is None:
        if none_allowed:
            return True
        else:
            return False
    if isinstance(int_value, str):
        if int_value == "":
            if empty_string_allowed:
                return True
            else:
                return False
        # Reassign the value as an integer to check
        try:
            int_value = int(int_value)
        except ValueError:
            return False

    # Now check the range
    if int_min <= int_value <= int_max:
        return True
    else:
        return False


def validate_number(number_value, none_allowed, empty_string_allowed):
    """
    Validate that a number value is valid.

    Args:
        number_value: Number value to check, can be string or number (int or float) type.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.

    Returns:
        True if number value is valid, False if invalid.
    """
    # First check some specific cases
    if number_value is None:
        if none_allowed:
            return True
        else:
            return False
    if isinstance(number_value, str):
        if number_value == "":
            if empty_string_allowed:
                return True
            else:
                return False
        # Reassign the value as a number to check - use float since it includes int values
        try:
            float(number_value)
        except ValueError:
            return False
    else:
        # May do more checks later but for now above should be sufficient
        pass
    return True


def validate_string(string_value, none_allowed, empty_string_allowed):
    """
    Validate that a string value is specified.
    This is a basic test just to make sure that a value has been provided.

    Args:
        string_value: String value to check, must be string type.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.

    Returns:
        True if string value is valid, False if invalid.
    """
    # First check some specific cases
    if string_value is None:
        if none_allowed:
            return True
        else:
            return False
    if string_value == "":
        if empty_string_allowed:
            return True
        else:
            return False
    # If special cases pass then any string value is valid.
    return True


def validate_string_in_list(string_value, string_list, none_allowed=False,
                            empty_string_allowed=False, ignore_case=False):
    """
    Validate that a string value is in a list of allowed string values.

    Args:
        string_value (str): String value to check, must be string type.
        string_list: List of allowed strings.
        none_allowed (bool): If the value is None, OK.
        empty_string_allowed (bool): If the value is an empty string, OK.
        ignore_case (bool): If True, then string comparisons will ignore case.  If False, case is important.

    Returns:
        True if string value is valid, False if invalid.
    """
    # First check some specific cases
    if string_value is None:
        if none_allowed:
            return True
        else:
            return False
    if string_value == "":
        if empty_string_allowed:
            return True
        else:
            return False

    # Now to see if the string is in the list
    string_value_upper = None
    if ignore_case:
        string_value_upper = string_value.upper()
    for s in string_list:
        if ignore_case:
            if s.upper() == string_value_upper:
                return True
        else:
            if s == string_value:
                return True
    # No string in the list was matched
    return False


# TODO smaler 2018-02-18 The following needs work
# - it allows brackets anywhere in the string
# - it does not actually check for comma-separated values
def validate_list(list_value, none_allowed, empty_string_allowed, brackets_required=True):
    """
    Validate that a list value is a list.

    The list_value can either be a list type or a string that can be converted into a list (checks that the string
    contains both the '[' and the ']' symbols).

    Args:
        list_value: List value to check, can be string or list type.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.
        brackets_required: If the value requires open and close brackets ([]), validate that the brackets exist

    Returns:
        True if list value is valid, False if invalid.
    """
    # First check some specific cases
    if list_value is None:
        if none_allowed:
            return True
        else:
            return False

    if isinstance(list_value, str):
        if list_value == "":
            if empty_string_allowed:
                return True
            else:
                return False
        else:
            if brackets_required:
                if '[' in list_value and ']' in list_value:
                    return True
                else:
                    return False
            else:
                return True

    elif type(list_value) == 'list':
        return True

    else:
        return False
