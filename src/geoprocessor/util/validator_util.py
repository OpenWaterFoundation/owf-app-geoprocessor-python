# validator_util - utility functions to validate command data
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

"""
Functions that provide validation for primitive data values.
These functions are typically called from the check_command_parameters function
of commands to validate a parameter value.
More specific validation is provided by 'command_util.validate*' functions.
"""
import os

# Import the QGIS version utilities first so that the version can be checked for imports below.
import geoprocessor.util.qgis_version_util as qgis_version_util

if (qgis_version_util.get_qgis_version_int(1) >= 3) and (qgis_version_util.get_qgis_version_int(2) <= 10):
    #  Works for QGIS 3.10
    import ogr
elif (qgis_version_util.get_qgis_version_int(1) >= 3) and (qgis_version_util.get_qgis_version_int(2) > 10):
    #  Works for QGIS 3.22.16 - QGIS 3.22.16/apps/Python39/Lib/site-packages/osgeo/ogr.py
    import osgeo.ogr as ogr

from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType
from geoprocessor.core.CommandLogRecord import CommandLogRecord

import geoprocessor.util.io_util as io_util
import geoprocessor.util.pandas_util as pandas_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.zip_util as zip_util

from urllib.request import urlopen


# TODO smalers 2020-03-16 legacy code that needs to be transferred to individual check functions.
def run_check(command, condition: str, parameter_name: str, parameter_value: str or int, fail_response: str or None,
              other_values: [object] = None) -> bool:
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
        command: the command being checked
        condition: the condition statement (or name) of the check that is to be run
        parameter_name: the command parameter being checked (the name, not the value)
        parameter_value: the command parameter value being checked (the value, not the name)
        fail_response: the action that occurs if the check fails. The available options are as follows:
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

    # Boolean to determine if the data are valid. Set to True until check indicates invalid.
    is_valid = True

    condition_upper = condition.upper()
    if condition_upper == "DOATTRIBUTESEXIST":
        # Check whether the attributes in a list exist in a GeoLayer based off of its attribute name.
        geolayer_id = other_values[0]

        # Get the GeoLayer.
        input_geolayer = command.command_processor.get_geolayer(geolayer_id)

        # Get the existing attribute names of the input GeoLayer.
        list_of_existing_attributes = input_geolayer.get_attribute_field_names()

        # Create a list of invalid input attribute names. An invalid attribute name is an input attribute name
        # that is not matching any of the existing attribute names of the GeoLayer.
        invalid_attrs = []
        for attr in parameter_value:
            if attr not in list_of_existing_attributes:
                invalid_attrs.append(attr)

        # If there are invalid attributes, the check failed.
        if invalid_attrs:
            message = "The following attributes ({}) of the {} parameter do" \
                      " not exist within the GeoLayer ({}).".format(invalid_attrs, parameter_name, geolayer_id)
            recommendation = "Specify valid attribute names."
            is_valid = False

    elif condition_upper == "DOESFILEPATHHAVEAVALIDFOLDER":
        # Check whether the parameter value (absolute file path) has a valid and existing folder.
        output_folder = os.path.dirname(parameter_value)
        if not os.path.isdir(output_folder):
            message = 'The folder of the {} ({}) is not a valid folder.'.format(parameter_name, output_folder)
            recommendation = "Specify a valid folder for the {} parameter.".format(parameter_name)
            is_valid = False

    elif condition_upper == "DOESGEOLAYERIDHAVECORRECTGEOMETRY":
        # Check whether the GeoLayer of the parameter value (GeoLayer ID) has the correct geometry type.
        desired_geom_type_list = [item.upper() for item in other_values[0]]
        if not command.command_processor.get_geolayer(parameter_value).get_geometry().upper() in desired_geom_type_list:
            message = 'The {} ({}) does not have geometry in the correct ' \
                      'format ({}).'.format(parameter_name, parameter_value, desired_geom_type_list)
            recommendation = 'Specify a GeoLayerID of a GeoLayer with geometry in' \
                             ' correct format ({}).'.format(desired_geom_type_list)
            is_valid = False

    elif condition_upper == "DOGEOLAYERIDSHAVEMATCHINGCRS":
        # Check whether the GeoLayer of the parameter value (GeoLayer ID) has a different CRS than another GeoLayer
        # (referenced by its GeoLayer ID)
        second_parameter_name = other_values[0]
        second_parameter_value = other_values[1]

        input_crs = command.command_processor.get_geolayer(parameter_value).get_crs()
        second_crs = command.command_processor.get_geolayer(second_parameter_value).get_crs()

        if not input_crs == second_crs:
            message = 'The {} ({}) and the {} ({}) do not have the same coordinate reference' \
                      ' system.'.format(parameter_name, parameter_value, second_parameter_name, second_parameter_value)
            recommendation = 'Specify GeoLayers that have the same coordinate reference system.'
            is_valid = False

    elif condition_upper == "ISCRSCODEVALID":
        # Check whether the parameter value (crs code)is a valid CRS code usable in the QGIS environment.
        if qgis_util.parse_qgs_crs(parameter_value) is None:
            message = 'The {} ({}) is not a valid CRS code.'.format(parameter_name, parameter_value)
            recommendation =\
                'Specify a valid CRS code (EPSG codes are an approved format).  See:  https://spatialreference.org/'
            is_valid = False

    elif condition_upper == "ISDATASTOREIDEXISTING":
        # Check whether the parameter value (DataStoreID) is an existing DataStoreID.
        if not command.command_processor.get_datastore(parameter_value):
            message = 'The {} ({}) is not a valid DataStore ID.'.format(parameter_name, parameter_value)
            recommendation = 'Specify a valid DataStore ID.'
            is_valid = False

    elif condition_upper == "ISDATASTOREIDUNIQUE":
        # Check whether the parameter value (DataStore ID) is a unique DataStoreID.
        if command.command_processor.get_geolayer(parameter_value):
            message = 'The {} ({}) value is already in use as a DataStore ID.'.format(parameter_name, parameter_value)
            recommendation = 'Specify a new {}.'.format(parameter_name)
            is_valid = False

            # noinspection PyPep8Naming
            pv_IfDataStoreIDExists = command.get_parameter_value("IfDataStoreIDExists", default_value="Replace")

            if pv_IfDataStoreIDExists.upper() == "REPLACEANDWARN":
                fail_response = "WARN"
            elif pv_IfDataStoreIDExists.upper() == "WARN":
                fail_response = "WARNBUTDONOTRUN"
            elif pv_IfDataStoreIDExists.upper() == "FAIL":
                fail_response = "FAIL"
            elif pv_IfDataStoreIDExists.upper() == "OPEN":
                is_valid = True
            elif pv_IfDataStoreIDExists.upper() == "REPLACE":
                is_valid = True

    elif condition_upper == "ISDATASTORETABLEUNIQUE":
        # Check whether the parameter value (Table Name) is unique within the DataStore.
        data_store_id = other_values[0]
        data_store_obj = command.command_processor.get_datastore(data_store_id)
        list_of_tables = data_store_obj.return_table_names()
        if parameter_value in list_of_tables:
            message = "The {} ({}) value is already an existing table in the {} DataStore.".format(parameter_name,
                                                                                                   parameter_value,
                                                                                                   data_store_id)
            recommendation = "Specify a unique {} value.".format(parameter_name)
            is_valid = False

    elif condition_upper == "ISDELIMITEDFILECOLUMNNAMEVALID":
        # Check whether the parameter value (column name) is a valid column name of a delimited file.
        delimited_file_abs = other_values[0]
        delimiter = other_values[1]
        if parameter_value not in io_util.get_col_names_from_delimited_file(delimited_file_abs, delimiter):
            message = "The {} ({}) is not a valid column name in the delimited file ({}).".format(parameter_name,
                                                                                                  parameter_value,
                                                                                                  delimited_file_abs)
            recommendation = "Specify an existing and valid {}.".format(parameter_name)
            is_valid = False

    elif condition_upper == "ISEXCELSHEETNAMEVALID":
        # Check whether the parameter value (sheet name) is a valid sheet name of an excel file.
        excel_file_abs = other_values[0]
        excel_workbook_obj = pandas_util.create_excel_workbook_obj(excel_file_abs)
        excel_worksheet_list = excel_workbook_obj.sheet_names
        if parameter_value not in excel_worksheet_list:
            message = "The {} ({}) is not a valid excel worksheet name in the excel file ({}).".format(parameter_name,
                                                                                                       parameter_value,
                                                                                                       excel_file_abs)
            recommendation = "Specify an existing and valid {}.".format(parameter_name)
            is_valid = False

    elif condition_upper == "ISFEATURECLASSINFGDB":
        # Check whether the parameter value (feature class) is within a file geodatabase.
        file_gdb_path_abs = other_values[0]
        ogr.UseExceptions()
        driver = ogr.GetDriverByName("OpenFileGDB")
        gdb = driver.Open(file_gdb_path_abs)
        feature_class_list = []
        for feature_class_idx in range(gdb.GetLayerCount()):
            feature_class = gdb.GetLayerByIndex(feature_class_idx)
            feature_class_list.append(feature_class.GetName())

        if parameter_value not in feature_class_list:
            message = "The {} ({}) is not a valid feature class in the file geodatabase ({}).".format(parameter_name,
                                                                                                      parameter_value,
                                                                                                      file_gdb_path_abs)
            recommendation = "Specify an existing and valid {}.".format(parameter_name)
            is_valid = False

    elif condition_upper == "ISFILEPATHVALID":
        # Check whether the parameter value (absolute file path) is a valid and existing file.

        if not os.path.isfile(parameter_value):
            message = "The {} ({}) is not a valid file.".format(parameter_name, parameter_value)
            recommendation = "Specify a valid file for the {} parameter.".format(parameter_name)
            is_valid = False

    elif condition_upper == "ISFOLDERAFGDB":
        # Check whether the parameter value (absolute folder path) is a valid file geodatabase.
        ogr.UseExceptions()
        driver = ogr.GetDriverByName("OpenFileGDB")
        if driver.Open(parameter_value) is None:
            message = "The {} ({}) is not a valid file geodatabase.".format(parameter_name, parameter_value)
            recommendation = "Specify a valid file geodatabase for the {} parameter.".format(parameter_name)
            is_valid = False

    elif condition_upper == "ISFOLDERPATHVALID":
        # Check whether the parameter value (absolute folder path) is a valid and existing folder.
        if not os.path.isdir(parameter_value):
            message = "The {} ({}) is not a valid folder.".format(parameter_name, parameter_value)
            recommendation = "Specify a valid folder for the {} parameter.".format(parameter_name)
            is_valid = False

    elif condition_upper == "ISGEOLAYERIDEXISTING":
        # Check whether the parameter value (GeoLayerID) is an existing GeoLayerID.
        if not command.command_processor.get_geolayer(parameter_value):
            message = 'The {} ({}) is not a valid GeoLayer ID (was not matched).'.format(parameter_name, parameter_value)
            recommendation = 'Specify a valid GeoLayer ID.'
            is_valid = False

    elif condition_upper == "ISGEOLAYERIDUNIQUE":
        # Check whether the parameter value (GeoLayer ID) is a unique GeoLayerID.
        if command.command_processor.get_geolayer(parameter_value):
            message = 'The {} ({}) value is already in use as a GeoLayer ID.'.format(parameter_name, parameter_value)
            recommendation = 'Specify a new {}.'.format(parameter_name)
            is_valid = False
            # noinspection PyPep8Naming
            pv_IfGeoLayerIDExists = command.get_parameter_value("IfGeoLayerIDExists", default_value="Replace")

            if pv_IfGeoLayerIDExists.upper() == "REPLACEANDWARN":
                fail_response = "WARN"
            elif pv_IfGeoLayerIDExists.upper() == "WARN":
                fail_response = "WARNBUTDONOTRUN"
            elif pv_IfGeoLayerIDExists.upper() == "FAIL":
                fail_response = "FAIL"
            else:
                is_valid = True

    elif condition_upper == "ISGEOLAYERVIEWGROUPIDEXISTING":
        # Check whether the parameter value (GeoLayerViewGroupID) is an existing GeoLayerViewGroupID.
        if not command.command_processor.get_geolayerviewgroup(parameter_value):
            message = 'The {} ({}) is not a valid GeoLayerViewGroupID.'.format(parameter_name, parameter_value)
            recommendation = 'Specify a valid GeoLayerViewGroupID.'
            is_valid = False

    elif condition_upper == "ISGEOMAPIDUNIQUE":
        # Check whether the parameter value (GeoMapID) is a unique GeoMapID.
        if command.command_processor.get_geomap(parameter_value):
            message = 'The {} ({}) value is already in use as a GeoMapID.'.format(parameter_name, parameter_value)
            recommendation = 'Specify a new {}.'.format(parameter_name)
            is_valid = False
            # noinspection PyPep8Naming
            pv_IfGeoLayerIDExists = command.get_parameter_value("IfGeoMapIDExists", default_value="Replace")

            if pv_IfGeoLayerIDExists.upper() == "REPLACEANDWARN":
                fail_response = "WARN"
            elif pv_IfGeoLayerIDExists.upper() == "WARN":
                fail_response = "WARNBUTDONOTRUN"
            elif pv_IfGeoLayerIDExists.upper() == "FAIL":
                fail_response = "FAIL"
            else:
                is_valid = True

    elif condition_upper == "ISGEOMAPIDEXISTING":
        # Check whether the parameter value (GeoMapID) is an existing GeoMapID.
        if not command.command_processor.get_geomap(parameter_value):
            message = 'The {} ({}) is not a valid GeoMap ID.'.format(parameter_name, parameter_value)
            recommendation = 'Specify a valid GeoMap ID.'
            is_valid = False

    elif condition_upper == "ISGEOMAPPROJECTIDEXISTING":
        # Check whether the parameter value (GeoMapProjectID) is an existing GeoMapProjectID.
        if not command.command_processor.get_geomapproject(parameter_value):
            message = 'The {} ({}) is not a valid GeoMapProject ID.'.format(parameter_name, parameter_value)
            recommendation = 'Specify a valid GeoMapProject ID.'
            is_valid = False

    elif condition_upper == "ISGEOMAPPROJECTIDUNIQUE":
        # Check whether the parameter value (GeoMapProjectID) is a unique GeoMapProjectID.
        if command.command_processor.get_geomap(parameter_value):
            message = 'The {} ({}) value is already in use as a GeoMapProjectID.'.format(
                parameter_name, parameter_value)
            recommendation = 'Specify a new {}.'.format(parameter_name)
            is_valid = False
            # noinspection PyPep8Naming
            pv_IfGeoMapProjectIDExists =\
                command.get_parameter_value("IfGeoMapProjectIDExists",
                                            default_value=command.parameter_input_metadata[
                                                'IfGeoMapProjectIDExists.Value.Default'])

            if pv_IfGeoMapProjectIDExists.upper() == "REPLACEANDWARN":
                fail_response = "WARN"
            elif pv_IfGeoMapProjectIDExists.upper() == "WARN":
                fail_response = "WARNBUTDONOTRUN"
            elif pv_IfGeoMapProjectIDExists.upper() == "FAIL":
                fail_response = "FAIL"
            else:
                is_valid = True

    elif condition_upper == "ISINTBETWEENRANGE":
        # Check whether the parameter value (integer) is between or at two values/numbers.
        int_min = other_values[0]
        int_max = other_values[1]

        if not validate_int_in_range(parameter_value, int_min, int_max, False, False):
            message = 'The {} ({}) must be at or between {} & {}'.format(parameter_name, parameter_value, int_min,
                                                                         int_max)
            recommendation = 'Specify a valid {} value.'.format(parameter_name)
            is_valid = False

    elif condition_upper == "ISLISTLENGTHCORRECT":
        # Check whether the length of a list is correct.
        delimiter = other_values[0]
        correct_length = other_values[1]

        # Convert the string into a list.
        list_of_strings = string_util.delimited_string_to_list(parameter_value, delimiter)
        if len(list_of_strings) != correct_length:
            message = 'The {} ({}) must have {} number of items.'.format(parameter_name, parameter_value,
                                                                         correct_length)
            recommendation = 'Specify a list of {} items for the {} parameter.'.format(correct_length, parameter_name)
            is_valid = False

    elif condition_upper == "ISPROPERTYUNIQUE":
        # Check whether the property name is a unique property name
        if command.command_processor.get_property(parameter_value):
            message = 'The {} ({}) value is already in use.'.format(parameter_name, parameter_value)
            recommendation = 'Specify a new {}.'.format(parameter_name)
            is_valid = False
            # noinspection PyPep8Naming
            pv_IfPropertyExists = command.get_parameter_value("IfPropertyExists", default_value="Replace")

            if pv_IfPropertyExists.upper() == "REPLACEANDWARN":
                fail_response = "WARN"
            elif pv_IfPropertyExists.upper() == "WARN":
                fail_response = "WARNBUTDONOTRUN"
            elif pv_IfPropertyExists.upper() == "FAIL":
                fail_response = "FAIL"
            else:
                is_valid = True

    elif condition_upper == "ISQGSEXPRESSIONVALID":
        # Check whether the input string is a valid QGSExpression.
        if qgis_util.parse_qgs_expression(parameter_value) is None:
            message = "{} ({}) is not a valid QgsExpression.".format(parameter_name, parameter_value)
            recommendation = "Specify a valid QgsExpression for {}.".format(parameter_name)
            is_valid = False

    elif condition_upper == "ISSTRINGLENGTHCORRECT":
        # Check whether the input string is the correct length.
        correct_length = other_values[0]

        # Convert the string into a list.
        if len(parameter_value) != correct_length:
            message = 'The {} ({}) must have exactly {} character(s).'.format(parameter_name, parameter_value,
                                                                              correct_length)
            recommendation = 'Specify a string with {} characters for the {} parameter.'.format(correct_length,
                                                                                                parameter_name)
            is_valid = False

    elif condition_upper == "ISTABLEIDEXISTING":
        # Check whether the parameter value (Table ID) is an existing Table ID.
        if not command.command_processor.get_table(parameter_value):
            message = 'The {} ({}) is not a valid Table ID.'.format(parameter_name, parameter_value)
            recommendation = 'Specify a valid Table ID.'
            is_valid = False

    elif condition_upper == "ISTABLEIDUNIQUE":
        # Check whether the parameter value (Table ID) is a unique TableID.
        if command.command_processor.get_table(parameter_value):
            message = 'The {} ({}) value is already in use as a Table ID.'.format(parameter_name, parameter_value)
            recommendation = 'Specify a new {}.'.format(parameter_name)
            is_valid = False
            # noinspection PyPep8Naming
            pv_IfTableIDExists = command.get_parameter_value("IfTableIDExists", default_value="Replace")

            if pv_IfTableIDExists.upper() == "REPLACEANDWARN":
                fail_response = "WARN"
            elif pv_IfTableIDExists.upper() == "WARN":
                fail_response = "WARNBUTDONOTRUN"
            elif pv_IfTableIDExists.upper() == "FAIL":
                fail_response = "FAIL"
            else:
                is_valid = True

    elif condition_upper == "ISTABLEINDATASTORE":
        # Check whether the parameter value (Table Name) is a table within the DataStore.
        data_store_id = other_values[0]
        data_store_obj = command.command_processor.get_datastore(data_store_id)
        list_of_tables = data_store_obj.return_table_names()
        if parameter_value not in list_of_tables:
            message = "{} ({}) is not an existing table in the {} DataStore.".format(parameter_name, parameter_value,
                                                                                     data_store_id)
            recommendation = "Specify a valid {} value.".format(parameter_name)
            is_valid = False

    elif condition_upper == "ISTARFILE":
        # Check whether the file is a valid tar file.
        if not zip_util.is_tar_file(parameter_value):
            message = "{} ({}) is not a valid TAR file.".format(parameter_name, parameter_value)
            recommendation = "Specify a valid TAR file for {}.".format(parameter_name)
            is_valid = False

    elif condition_upper == "ISURLVALID":
        # Check whether the input string is a valid URL.
        # noinspection PyBroadException
        try:
            urlopen(parameter_value)
        except Exception:
            message = "{} ({}) is not a valid URL.".format(parameter_name, parameter_value)
            recommendation = "Specify a valid URL for {}.".format(parameter_name)
            is_valid = False

    elif condition_upper == "ISZIPFILE":
        # Check whether the file is a valid zip file.
        if not zip_util.is_zip_file(parameter_value):
            message = "{} ({}) is not a valid ZIP file.".format(parameter_name, parameter_value)
            recommendation = "Specify a valid ZIP file for {}.".format(parameter_name)
            is_valid = False

    else:
        message = "Check {} is not a valid check in the validators.".format(condition)
        recommendation = "Contact the maintainers of the GeoProcessor software."
        is_valid = False
        fail_response = "FAIL"

    # If the data is not valid, increase the warning count of the command instance by one.
    run_the_command = None
    if not is_valid:
        command.warning_count += 1

        fail_response_upper = fail_response.upper()
        if fail_response_upper == "FAIL":
            # If configured, log a FAILURE message about the failed check. Set the run_the_command boolean to False.
            command.logger.warning(message)
            command.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.FAILURE,
                                                                                     message, recommendation))
            run_the_command = False

        elif fail_response_upper == "WARN":
            # If configured, log a WARNING message about the failed check. Set the run_the_command boolean to True.
            command.logger.warning(message)
            command.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.WARNING,
                                                                                     message, recommendation))
            run_the_command = True

        elif fail_response_upper == "WARNBUTDONOTRUN":
            # If configured, log a WARNING message about the failed check. Set the run_the_command boolean to False.
            command.logger.warning(message)
            command.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.WARNING,
                                                                                     message, recommendation))
            run_the_command = False

    else:
        # If the check passed, set the run_the_command boolean to True.
        run_the_command = True

    # Return the run_the_command boolean.
    return run_the_command


def validate_bool(bool_value: bool or str, none_allowed: bool, empty_string_allowed: bool) -> bool:
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


def validate_float(float_value: float or str,
                   none_allowed: bool = False,
                   empty_string_allowed: bool = False,
                   zero_allowed: bool = True) -> bool:
    """
    Validate that a floating point value is valid.

    Args:
        float_value: Floating point value to check, can be string or floating point (float) type.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.
        zero_allowed: If a zero is allowed, OK.

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
            f = float(float_value)
            # Check for zero
            if not zero_allowed:
                if f == 0.0:
                    # Zero is not allowed
                    return False
        except ValueError:
            return False
    else:
        # May do more checks later but for now above should be sufficient
        pass
    return True


def validate_int(int_value: str or int,
                 none_allowed: bool,
                 empty_string_allowed: bool,
                 zero_allowed: bool = True) -> bool:
    """
    Validate that an integer value is valid.

    Args:
        int_value: Integer value to check, can be string or integer (int) type.
        none_allowed: If the value is None, OK.
        empty_string_allowed: If the value is an empty string, OK.
        zero_allowed: If a zero is allowed, OK.

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
            i = int(int_value)
            # Check for zero
            if not zero_allowed:
                if i == 0:
                    # Zero is not allowed
                    return False
        except ValueError:
            return False
    else:
        # May do more checks later but for now above should be sufficient
        pass
    return True


def validate_list_has_one_value(object_list: [object], allow_more_than_one: bool = False) -> bool:
    """
    Validate that a list has only one value that is not None and not empty string.

    Args:
        object_list ([object]): List of objects.
        allow_more_than_one (bool):  If True, allow more than one value result to be True.
            If False, exactly one value must be in the list.

    Returns:
        True if the list has required number of items item, False if not.
    """

    non_missing_count = 0
    for o in object_list:
        if o is not None:
            non_missing_count += 1
        else:
            if isinstance(o,str) and (len(str(o)) > 0):
                # Non-empty string
                non_missing_count += 1

    if not allow_more_than_one:
        # More restrictive case, so consider first.
        # Exactly one value must be non-missing
        if non_missing_count == 1:
            return True
        else:
            return False
    else:
        # At least one value must be non-missing.
        if non_missing_count >= 1:
            return True
        else:
            return False


def validate_int_in_range(int_value: int, int_min: int, int_max: int, none_allowed: bool,
                          empty_string_allowed: bool) -> bool:
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


def validate_number(number_value: object, none_allowed: bool, empty_string_allowed: bool) -> bool:
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


def validate_string(string_value: str, none_allowed: bool, empty_string_allowed: bool) -> bool:
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


def validate_string_in_list(string_value: str, string_list: [str], none_allowed: bool = False,
                            empty_string_allowed: bool = False, ignore_case: bool = False) -> bool:
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
def validate_list(list_value: [], none_allowed: bool, empty_string_allowed: bool,
                  brackets_required: bool = True) -> bool:
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
