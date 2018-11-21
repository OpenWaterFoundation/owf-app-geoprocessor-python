# Input/output functions
# - some are ported from Java IOUtil.java class

import geoprocessor.util.string_util as string_util
import geoprocessor.util.app_util as app_util

import datetime
import getpass
import logging
import os
import platform
import re
import sys


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
            print ("Warning: There is no file extension for the input file ({})".format(absolute_path))
        if filename == '':
            print ("Warning: There is no filename for the input file ({})".format(absolute_path))
        return "{}{}".format(filename, extension)

    # The %f formatter code returns the filename without the leading path and without the extension. Print warning
    # messages if the filename is non-existent. (The returned value, in that case, will not be None but will instead be
    # an empty string).
    elif formatter == '%f':

        if filename == '':
            print ("Warning: There is no filename for the input file ({})".format(absolute_path))
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
            print ("Warning: There is no file extension for the input file ({})".format(absolute_path))
        return extension

    # Print a warning message and return None if the input formatter code is not a valid code.
    else:
        print ("The formatter ({}) is not an option.")
        return None


def format_standard_file_header(comment_line_prefix='', max_width=120, is_xml=False):
    """
    Format a standard header for a text file, which is useful to understand the file creation.
    The header looks like the following:

        # File generated by
        # program:    program 2.7 (2018-01-21)
        # user:       sam
        # date:       Mon Jun 26 14:49:18 MDT 1995
        # host:       white
        # folder:     /some/path
        # command:    full command line
        #                 ... more lines if necessary...

    Args:
        comment_line_prefix (str): the string to use for the start of comment lines (default="").
            Use an empty string if the prefix character will be added by calling code.
        max_width (int): the maximum width of output lines (if whitespace is
            embedded in the header information, lines will be broken appropriately to fit
            within the specified width for readability.  Default is 120.
        is_xml (bool):  Indicates whether the header is being formatted for XML.
            XML files must be handled specifically because some characters that may be printed
            to the header may not be handled by the XML parser.  The opening and closing
            XML tags must be added before and after calling this method.
            Default is no properties.

    Returns:
        A list of strings containing the header lines.
        Newline characters are not present.
    """
    left_border = 12

    # Make sure that a valid comment string is used...

    comment_line_prefix2 = ""
    if comment_line_prefix != "":
        # Add a space to the end of the prefix so that comments are not smashed right up against
        # the line prefix - this helps with readability
        comment_line_prefix2 = comment_line_prefix + " "
    comment_len = len(comment_line_prefix2)

    # Format the comment string for the command line printout...

    comment_space0 = comment_line_prefix2
    for i in range(0, left_border):
        comment_space0 += " "
    comment_space = comment_space0

    comments = []
    # TODO smalers 2018-01-21 need to get actual values but for now dummy in what is not known
    # - need to figure out how to pass the command file name, etc.
    # progname = app_util.program_name
    progname = os.path.basename(sys.argv[0])
    progver = app_util.program_version
    user = getpass.getuser()
    now = datetime.datetime.now().isoformat()
    host = platform.node()
    working_dir = ""  # Needs to be the initial folder or command file folder if it was provided
    args = sys.argv
    command_list = []  # Used to show what workflow was run to create the file
    command_file = ""  # Need to set somehow
    comments.append(comment_line_prefix2 + "File generated by...")
    comments.append(comment_line_prefix2 + "program:      " + progname + " " + progver)
    comments.append(comment_line_prefix2 + "user:         " + user)
    comments.append(comment_line_prefix2 + "date:         " + now)
    comments.append(comment_line_prefix2 + "host:         " + host)
    comments.append(comment_line_prefix2 + "directory:    " + working_dir)
    comments.append(comment_line_prefix2 + "command line: " + progname)
    column0 = comment_len + left_border + len(progname) + 1
    column = column0  # Column position, starting at 1
    b = comment_line_prefix2
    if args is not None:
        for arg in args:
            arg_len = len(arg)
            # Need 1 to account for blank between arguments...
            if (column + 1 + arg_len) > max_width:
                # Put the argument on a new line...
                comments.append(b)
                b = ""
                b += comment_line_prefix2
                b += (comment_space + arg)
                column = column0 + arg_len
            else:
                # Put the argument on the same line...
                b += " " + arg
                column += (arg_len + 1)

    # Output the commands, with preference given to in-memory list of commands rather than command file
    comments.append(b)
    if command_list is not None:
        # Print the command list contents...
        if is_xml:
            comments.append(comment_line_prefix2)
        else:
            comments.append(comment_line_prefix2 +
                            "-----------------------------------------------------------------------")
        # Also indicate which command file on the file system
        if command_file is not None and os.access(command_file, os.R_OK):
            comments.append(comment_line_prefix2 + 'Last command file: "' + command_file + '"')
            comments.append(comment_line_prefix2)
            comments.append(comment_line_prefix2 + "Commands used to generate output:")
            comments.append(comment_line_prefix2)
            for command in command_list:
                comments.append(comment_line_prefix2 + command)

    elif os.access(command_file, os.R_OK):
        # Format the command file contents...
        if is_xml:
            comments.append(comment_line_prefix2)
        else:
            comments.append(comment_line_prefix2 +
                            "-----------------------------------------------------------------------")
        comments.append(comment_line_prefix2 + "Command file \"" + command_file + "\":")
        comments.append(comment_line_prefix2)
        error = False
        # TODO smalers 2018-01-21 need to enable
        """
        BufferedReader cfp = null;
        FileReader file = null;
        try {
            file = new FileReader ( _command_file );
            cfp = new BufferedReader ( file );
        }
        catch ( Exception e ) {
            error = true;
        }
        if ( !error ) {
            String string;
            while ( true ) {
                try {
                    string = cfp.readLine ();
                    if ( string == null ) {
                        break;
                    }
                }
                catch ( Exception e ) {
                    // End of file.
                    break;
                }
                comments.add ( comment_line_prefix2 + " " + string );
            }
        }
        """
    return comments


def get_col_names_from_delimited_file(delimited_file_abs, delimiter):
    """
    Reads a delimited file and returns the column names in list format.

    Args:
        delimited_file_abs (string): the full pathname to a delimited file to read.
        delimiter (string): the delimiter used in the delimited file.

    Returns:
        A list of strings. Each string represents a column name. If an error occurs within the function, None is
         returned.
    """

    try:

        # Open the delimited file and iterate through the lines of the file.
        with open(delimited_file_abs) as in_file:
            for lineNum, line in enumerate(in_file):

                # Return the column names of the header line in the delimited file. The column names are items of a
                # list and the column names are striped of whitespaces on either side.
                if lineNum == 0:
                    return map(str.strip, line.split(delimiter))

    # If an error occurs within the process, return None.
    except:
        return None


def get_extension(full_path):
    """
    Returns the extension of a full path.

    Args:
        full_path (str): the input full path

    Returns: The extension as a string.
    """

    filename, extension = os.path.splitext(os.path.basename(full_path))
    return extension


def get_filename(full_path):
    """
    Returns the filename of a full path (without the extension).

    Args:
        full_path (str): the input full path

    Returns: The filename as a string.
    """

    filename, extension = os.path.splitext(os.path.basename(full_path))
    return filename


def get_path(full_path):
    """
    Returns the directory path of a full path (without the filename or extension).

    Args:
        full_path (str): the input full path

    Returns: The directory path as a string.
    """

    return os.path.dirname(full_path)


def print_standard_file_header(ofp, comment_line_prefix='#', max_width=120, properties=None):
    """
    Print a standard header to a file.  See __format_standard_file_header for an example of the header.
    This is a port of the Java cdss-lib-common-java package ioutil.print_creator_header() method.

    Args:
        ofp (file): file that is being written.
        comment_line_prefix (str): the string to use for the start of comment lines (default="#").
        max_width (int): the maximum width of output lines (if whitespace is
            embedded in the header information, lines will be broken appropriately to fit
            within the specified width for readability.  Default is 120.
        properties (dict): properites used to format the header.  Currently the only
            property that is recognized is "IsXML", which can be "true" or "false".
            XML files must be handled specifically because some characters that may be printed
            to the header may not be handled by the XML parser.  The opening and closing
            XML tags must be added before and after calling this method.
            Default is no properties.

    Returns:
        None
    """
    is_xml = False
    # Figure out properties...
    if properties is not None:
        prop_value = properties["IsXML"]
        if prop_value is not None and prop_value.upper() == "TRUE":
            is_xml = True
            # If XML, do not print multiple dashes together in the comments below.

    # Get the formatted header comments...

    comments = format_standard_file_header(comment_line_prefix=comment_line_prefix, max_width=max_width, is_xml=is_xml)

    # Python 2...
    # nl = os.linesep
    # Python 3...
    nl = '\n'
    for comment in comments:
        ofp.write(comment + nl)
    # Flush to the write to make sure it is visible, such as if written to a long-writing file
    ofp.flush()


def to_relative_path(root_path, rel_path):
    """
    Convert a path "path" and an absolute directory "dir" to a relative path.
    If "dir" is at the start of "path" it is removed.  If it is not present, an
    exception is thrown.  For example, a "dir" of /a/b/c/d/e and a "path" of
    /a/b/c/x/y will result in ../../x/y.

    The strings passed in to this method should not end with a file separator
    (either "\" or "/", depending on the system).  If they have a file separator,
    the separator will be trimmed off the end.

    There are four conditions for which to check:

    1.  The directories are exactly the same ("/a/b/c" and "/a/b/c")
    2.  The second directory is farther down the same branch that the first
        directory is on ("/a/b/c/d/e" and "/a/b/c").
    3.  The second directory requires a backtracking up the branch on which the
        first directory is on ("/a/b/c/d" and "/a/b/c/e" or "/a/b/c/d" and "/g")
    4.  For Windows: the directories are on different drives.

    This function will do error checking to make sure the directories passed in
    to it are not null or empty, but apart from that does no error-checking to
    validate proper directory naming structure.  This function will fail with
    improper directory names (e.g., "C:\c:\\\\\\\\test\\\\").

    Args:
        root_path (str): the root path from which to build a relative path.
        rel_path (str) the path for which to create the relative path from the root_path.

    Returns:
        The relative path created from the two directory structures.  This
        path will NOT have a trailing directory separator (\ or /).  If both the
        root_path and rel_path are the same, for instance, the value "." will be returned.
        Plus the directory separator, this becomes ".\" or "./".

    Except:
        ValueError if the conversion cannot occur.  Most likely will occur
        in Windows when the two directories are on different drives.  Will also be thrown
        if null or empty strings are passed in as directories.
    """
    # Do some simple error checking
    if root_path is None or root_path.strip() == "":
        raise ValueError('Bad root_path "' + root_path + '"')
    if rel_path is None or rel_path.strip() == "":
        raise ValueError('Bad rel_path "' + rel_path + '"')

    sep = os.sep

    unix = True

    if sep == "\\":
        unix = False
        # Operating system is running on Windows.  Check to see if the drive letters
        # are the same for each directory -- if they aren't, the
        # second directory can't be converted to a relative directory.
        drive1 = root_path.lower()[0]
        drive2 = rel_path.lower()[0]

        if drive1 != drive2:
            raise ValueError('Cannot adjust "' + rel_path + '" to relative using folder "' + root_path + '"')

    # Always trim any trailing folder separators off the directory paths
    while len(root_path) > 1 and root_path.endswith(sep):
        root_path = root_path[0:len(root_path) - 1]

    while len(rel_path) > 1 and rel_path.endswith(sep):
        rel_path = rel_path[0:len(rel_path) - 1]

    # Check to see if the two paths are the same
    if (unix and root_path == rel_path) or (not unix and root_path.upper() == rel_path.upper()):
        return "."

    # Check to see if the rel_path dir is farther up the same branch that the root_path is on.

    if (unix and rel_path.startswith(root_path)) or (not unix and rel_path.upper().startswith(root_path.upper())):
        # At this point, it is known that rel_path is longer than root_path
        c = "" + rel_path[len(root_path)]

        if c == sep:
            higher = rel_path[len(root_path):]
            if higher.startswith(sep):
                higher = higher[1:]
            return higher

    # If none of the above were triggered, then the second folder
    # is higher up the first directory's directory branch

    # Get the final folder separator from the first folder, and
    # then start working backwards in the string to find where the
    # second folder and the first folder share folder information.
    start = root_path.rfind(sep)
    x = 0
    for i in range(start, -1, -1):  # Want to go to >= 0, hence -1 for second value
        s = root_path[i]

        if s != sep:
            # Do nothing this iteration
            pass

        elif ((unix and rel_path[0:(i+2)] == (root_path + sep)[0:(i+2)])
            or (not unix and rel_path.upper()[0:i+2] == (root_path + sep).upper()[0:i+2])):
            # A common "header" in the folder name has been found.  Count the number of separators in each
            # folder to determine how much separation lies between the two
            dir1seps = string_util.pattern_count(root_path[0:i], sep)
            dir2seps = string_util.pattern_count(root_path, sep)
            x = i + 1
            if x > len(rel_path):
                x = len(rel_path)
            uncommon = rel_path[x:len(rel_path)]
            steps = dir2seps - dir1seps
            if steps == 1:
                if uncommon.strip() == "":
                    return ".."
                else:
                    return ".." + sep + uncommon
            else:
                if uncommon.strip() == "":
                    uncommon = ".."
                else:
                    uncommon = ".." + sep + uncommon
                for j in range(1, steps):
                    uncommon = ".." + sep + uncommon
            return uncommon
    return rel_path


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
        write_mode (str):  Write mode: 'Overwrite' (default) or 'Append' (case will be ignored).
        format_type (str):  File format type: 'NameTypeValue', 'NameTypeValuePython', 'NameValue',
            as per the GeoProcessor WritePropertiesToFile command.
        sort_order (int): Sort order -1 (descending), 0 (none), 1 (ascending)
        problems ([str]):  List of strings with problem messages, use in calling code for error-handling.

    Returns:
        None.
    """
    fout = None
    logger = logging.getLogger(__name__)
    debug = True
    try:
        # Open the file...
        if write_mode.upper() == 'APPEND':
            fout = open(output_file_absolute, "a")
        else:
            fout = open(output_file_absolute, "w")
        # Get the list of all processor property names from the property dictionary
        prop_name_list = list(all_properties.keys())
        # logger.info("Have " + str(len(prop_name_list)) + " properties to write")
        if sort_order == 0:
            # Want to output in the order of the properties that were requested, not the order from the dictionary
            # Rearrange the full list to make sure the requested properties are at the front
            found_count = 0
            for i in range(0, len(include_properties)):
                for j in range(0, len(prop_name_list)):
                    if include_properties[i] == prop_name_list[j]:
                        # Move to the front of the list and remove the original
                        prop_name_list.insert(found_count, include_properties[i])
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
                    if debug:
                        logger.info('Checking property "' + prop_name + '" if matched for output "' +
                                    include_properties[i] + '"')
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
            if debug:
                logger.info('After checking, do_write=' + str(do_write))
            if do_write:
                try:
                    __write_property(fout, prop_name, all_properties[prop_name], format_type)
                except Exception as e2:
                    message = 'Error writing property "' + prop_name + '" (' + str(e2) + ').'
                    problems.append(message)
                    logger.warning(message, exc_info=True)
                except:
                    message = 'Error writing property "' + prop_name + '"'
                    problems.append(message)
                    logger.warning(message, exc_info=True)

        for i in range(0, len(include_properties_matched)):
            if not include_properties_matched[i]:
                problems.append('Unable to match property "' + include_properties[i] + '" to write.')
    except Exception as e:
        message = 'Error writing properties to file "' + output_file_absolute + '" (' + str(e) + ').'
        problems.append(message)
        logger.warning(message, e, exc_info=True)
    except:
        message = 'Error writing properties to file "' + output_file_absolute + '.'
        problems.append(message)
        logger.warning(message, exc_info=True)
    finally:
        if fout is not None:
            fout.close()
    return problems
