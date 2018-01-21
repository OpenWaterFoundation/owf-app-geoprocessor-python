# Input/output functions
# - some are ported from Java IOUtil.java class

import geoprocessor.util.string as string_util

import logging
import os
import re
import sys
import traceback


def to_absolute_path(parent_dir, path):
    """
    Convert an absolute "parent_dir" and path to an absolute path.
    If the path is already an absolute path it is returned as is.
    If the path is a relative path, it is joined to the absolute path "parent_dir" and returned.
    This is a port of the Java IOUtil.toAbsolutePath() method.

    Args:
        parent_dir (str): Directory to prepend to path, for example the current working directory.
        path (str): Path to append to parent_dir to create an absolute path.
                   If absolute, it will be returned.
                   If relative, it will be appended to parent_dir.
                   If the path includes "..", the directory will be truncated before appending the non-".."
                   part of the path.

    Returns:
        The absolute path given the provided input path parts.
    """
    if os.path.isabs(path):
        # No need to do anything else so return the path without modification
        return path

    # Loop through the "path".  For each occurrence of "..", knock a directory off the end of the "parent_dir"...

    # Always trim any trailing directory separators off the directory paths.
    while len(parent_dir) > 1 and parent_dir.endswith(os.sep):
        parent_dir = parent_dir[0:len(parent_dir) - 1]

    while len(path) > 1 and path.endswith(os.sep):
        path = path[0:len(path) - 1]

    path_length = len(path)
    sep = os.sep
    for i in range(0, path_length):
        if path.startswith("./") or path.startswith(".\\"):
            # No need for this in the result.
            # Adjust the path and evaluate again.
            path = path[2:]
            i = -1
            path_length = path_length - 2
        if path.startswith("../") or path.startswith("..\\"):
            # Remove a directory from each path.
            pos = parent_dir.rfind(sep)
            if pos >= 0:
                # This will remove the separator.
                parent_dir = parent_dir[0:pos]
            # Adjust the path and evaluate again.
            path = path[3:]
            i = -1
            path_length -= 3
        elif path == "..":
            # Remove a directory from each path.
            pos = parent_dir.rfind(sep)
            if pos >= 0:
                parent_dir = parent_dir[0:pos]
            # Adjust the path and evaluate again.
            path = path[2:]
            i = -1
            path_length -= 2

    return os.path.join(parent_dir, path)


def verify_path_for_os(path):
    """
    Verify that a path is appropriate for the operating system.
    This is a simple method that does the following:
    - If on UNIX/LINUX, replace all \ characters with /.
      WARNING - as implemented, this will convert UNC paths to forward slashes.
      Windows drive letters are not changed, so this works best with relative paths.
    - If on Windows, replace all / characters with \

    Args:
        path (str): Path to adjust.

    Returns:
        Path adjusted to be compatible with the operating system.
    """
    if path is None:
        return path

    platform = sys.platform
    if platform == 'linux' or platform == 'linux2' or platform == 'cygwin' or platform == 'darwin':
        # Convert Windows paths to Linux
        return path.replace('\\', '/')
    else:
        # Assume Windows, convert paths from Linux to Windows
        return path.replace('/', '\\')


def expand_formatter(absolute_path, formatter):

    """
    Returns the appropriate value of a parsed absolute path given the user-defined formatter code. Many of times
    the user will want the filename without the extension or just the extension from an absolute path. This function
    will return the desired parsed path given the user's input.

    Args:
        absolute_path (string): a full pathname to a file
        formatter (string): a code that references the type of return value. See available formatter codes below:
            example absolute path | C:/Users/User/Desktop/example.geojson.txt
            %F | the filename with the extension ex: example.geojson.txt
            %f | the filename without the extension ex: example.geojson
            %P | the full path (including the leading path, the filename and the extension)
               |    ex: C:/Users/User/Desktop/example.geojson.txt
            %p | the leading path without the filename or extension ex: C:/Users/User/Desktop
            %E | the extension with the '.' character ex: .txt

    Returns:
        The appropriate value of the parsed absolute path given the input formatter code.
    """

    # Get the full path without the extension and the extension
    path_without_ext, extension = os.path.splitext(absolute_path)

    # Get the filename without the extension
    filename = os.path.basename(path_without_ext)

    # The %F formatter code returns the filename with the extension and without the leading path. Print warning
    # messages if the filename or extension are non-existent. (The returned value, in those cases, will not be None
    # but will instead be an empty string).
    if formatter == '%F':

        if extension == '':
            print "Warning: There is no file extension for the input file ({})".format(absolute_path)
        if filename == '':
            print "Warning: There is no filename for the input file ({})".format(absolute_path)
        return "{}{}".format(filename, extension)

    # The %f formatter code returns the filename without the leading path and without the extension. Print warning
    # messages if the filename is non-existent. (The returned value, in that case, will not be None but will instead be
    # an empty string).
    elif formatter == '%f':

        if filename == '':
            print "Warning: There is no filename for the input file ({})".format(absolute_path)
        return filename

    # The %P formatter code returns the filename with the leading path and with the file extension.
    elif formatter == '%P':

        return absolute_path

    # The %p formatter code returns the leading path without the filename or the file extension.
    elif formatter == '%p':

        return os.path.dirname(absolute_path)

    # The %E formatter code returns the extension with the '.' character. Print warning messages if the extension is
    # non-existent. (The returned value, in that case, will not be None but will instead be an empty string).
    elif formatter == '%E':

        if extension == '':
            print "Warning: There is no file extension for the input file ({})".format(absolute_path)
        return extension

    # Print a warning message and return None if the input formatter code is not a valid code.
    else:
        print "The formatter ({}) is not an option."
        return None


# TODO smalers 2018-01-20 Need to fully move this to util.string
# - I copied and redirect to there
def string_to_list(string):
    return string_util.string_to_list(string)


def __write_property(fout, property_name, property_object, format_type):
    """
    Write a single property to the output file, called by the write_property_file() function.

    Args:
        fout:  Open file object.
        property_name:  Name of property to write.
        property_object:  Property object to write.
        format_type (str):  File format type: 'NameTypeValue', 'NameTypeValuePython', 'NameValue',
            as per the GeoProcessor WritePropertiesToFile command.

    Returns:
        None.
    """
    # Write the output...
    quote = ""
    do_date_time = False
    # Only use double quotes around String and DateTime objects
    # TODO smalers 2018-01-20 make this complete
    # if isinstance(property_object, DateTime):
    #   do_date_time = True
    if isinstance(property_object, str) or do_date_time:
        # Quote the output
        quote = '"'
    # TODO SAM 2016-09-19 Evaluate whether more complex objects should be quoted
    nl = os.linesep  # newline character for operating system
    if format_type == 'NameValue':
        fout.write(property_name + "=" + quote + str(property_object) + quote + nl)
    elif format_type == 'NameTypeValue':
        if do_date_time:
            fout.write(property_name + "=DateTime(" + quote + str(property_object) + quote + ")" + nl)
        else:
            # Same as NameValue
            fout.write(property_name + "=" + quote + str(property_object) + quote + nl)
    elif format_type == 'NameTypeValuePython':
        if do_date_time:
            pass
            # TODO smalers 2018-01-20 need to finish
            """
            DateTime dt = (DateTime)propertyObject
            StringBuffer dtBuffer = new StringBuffer()
            dtBuffer.append("" + dt.getYear() )
            if ( dt.getPrecision() <= DateTime.PRECISION_MONTH ) {
                dtBuffer.append("," + dt.getMonth() )
            if ( dt.getPrecision() <= DateTime.PRECISION_DAY ) {
                dtBuffer.append("," + dt.getDay() )
            if ( dt.getPrecision() <= DateTime.PRECISION_HOUR ) {
                dtBuffer.append("," + dt.getHour() )
            if ( dt.getPrecision() <= DateTime.PRECISION_MINUTE ) {
                dtBuffer.append("," + dt.getMinute() )
            if ( dt.getPrecision() <= DateTime.PRECISION_SECOND ) {
                dtBuffer.append("," + dt.getSecond() )
            # TODO SAM 2012-07-30 Evaluate time zone
            fout.println ( property_name + "=DateTime(" + dtBuffer + ")")
            """
        else:
            # Same as NAME_VALUE
            fout.write(property_name + "=" + quote + str(property_object) + quote + nl)


def write_property_file(output_file_absolute, all_properties,
                        include_properties, write_mode, format_type, sort_order, problems):
    """
    Write a dictionary of properties to a file, using the specified format.
    This function is useful for saving property lists for in configuration file formats,
    simple data exchange between programs, and for automated testing.

    Args:
        output_file_absolute (str):  Path for the output file.
        all_properties (dict):  Dictionary of properties to write.
        include_properties ([str]):  List of properties to write or empty list to write all.
        write_mode (str):  Write mode: 'Overwrite' (default) or 'Append'.
        format_type (str):  File format type: 'NameTypeValue', 'NameTypeValuePython', 'NameValue',
            as per the GeoProcessor WritePropertiesToFile command.
        sort_order (int): Sort order -1 (descending), 0 (none), 1 (ascending)
        problems ([String]):  List of strings with problem messages, use in calling code for error-handling.

    Returns:
        None.
    """
    fout = None
    # logger = logging.getLogger(__name__)
    try:
        # Open the file...
        if write_mode == 'Append':
            fout = open(output_file_absolute, "a")
        else:
            fout = open(output_file_absolute, "w")
        # Get the list of all processor property names from the property dictionary
        prop_name_list = all_properties.keys()
        # logger.info("Have " + str(len(prop_name_list)) + " properties to write")
        if sort_order == 0:
            # Want to output in the order of the properties that were requested, not the order from the dictionary
            # Rearrange the full list to make sure the requested properties are at the front
            found_count = 0
            for i in range(0, len(include_properties)):
                for j in range(0, len(prop_name_list)):
                    if include_properties[i] == prop_name_list[j]:
                        # Move to the front of the list and remove the original
                        prop_name_list.append(found_count, include_properties[i])
                        found_count += 1
                        del prop_name_list[j + 1]
        elif sort_order > 0:
            # Ascending
            prop_name_list = sorted(prop_name_list)
        else:
            # Descending
            prop_name_list = sorted(prop_name_list, reverse=True)

        # Loop through property names retrieved from the properties dictionary
        # - if no specific properties were requested, write them all
        # - otherwise, if property names were requested, only write those properties no
        do_write = False
        # Whether the include_properties were each matched
        include_properties_matched = [False]*len(include_properties)

        for prop_name in prop_name_list:
            do_write = False
            # logger.info('Checking property "' + prop_name + '"')
            if len(include_properties) == 0:
                # Always write
                do_write = True
            else:
                # Loop through the properties to include and see if there is a match
                for i in range(0, len(include_properties)):
                    # logger.info('Writing property "' + include_properties[i] + '"')
                    if include_properties[i].find("*") >= 0:
                        # Includes glob-style wildcards.  Check the user-specified properties
                        # - first translate the glob-style syntax that uses * to internal regex
                        # - see:  https://stackoverflow.com/questions/27726545/python-glob-but-against-a-list-of-strings-rather-than-the-filesystem
                        include_properties_regex = include_properties[i].replace("*", "[^/]*")
                        include_properties_regex_compiled = re.compile(include_properties_regex)
                        if include_properties_regex_compiled.match(prop_name):
                            do_write = True
                            include_properties_matched[i] = True
                    else:
                        # Match exactly
                        if prop_name == include_properties[i]:
                            do_write = True
                            include_properties_matched[i] = True
            # logger.info('After checking, do_write=' + str(do_write))
            if do_write:
                try:
                    __write_property(fout, prop_name, all_properties[prop_name], format_type)
                except Exception as e2:
                    problems.append('Error writing property "' + prop_name + '" (' + str(e2) + ').')
                except:
                    problems.append('Error writing property "' + prop_name + '"')

        for i in range(0, len(include_properties_matched)):
            if not include_properties_matched[i]:
                problems.append('Unable to match property "' + include_properties[i] + '" to write.')
    except Exception as e:
        problems.append('Error writing properties to file "' + output_file_absolute + '" (' + str(e) + ').')
        traceback.print_exc(file=sys.stdout)
    except:
        problems.append('Error writing properties to file "' + output_file_absolute + '.')
        traceback.print_exc(file=sys.stdout)
    finally:
        if fout is not None:
            fout.close()
    return problems
