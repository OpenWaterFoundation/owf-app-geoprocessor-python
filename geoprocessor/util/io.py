# Input/output functions
# - some are ported from Java IOUtil.java class

import os
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
