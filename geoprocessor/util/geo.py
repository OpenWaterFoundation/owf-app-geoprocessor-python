# Utility functions related to GeoProcessor Geo commands
import os


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
            %E | the extension with the '.' character ex: .txt

    Returns:
        The appropriate value of the parsed absolute path given the input formatter code.
    """

    # Get the full path without the extension and the extension
    path_without_ext, extension = os.path.splitext(absolute_path)

    # Get the filename without the extension
    filename = os.path.basename(path_without_ext)

    # The %F formatter code returns the filename with the extension. Print warning messages if the filename or
    # extension are non-existent. (The returned value, in those cases, will not be None but will instead be an empty
    # string).
    if formatter == '%F':

        if extension == '':
            print "Warning: There is no file extension for the input file ({})".format(absolute_path)
        if filename == '':
            print "Warning: There is no filename for the input file ({})".format(absolute_path)
        return "{}{}".format(filename, extension)

    # The %f formatter code returns the filename without the extension. Print warning messages if the filename is
    # non-existent. (The returned value, in that case, will not be None but will instead be an empty string).
    elif formatter == '%f':

        if filename == '':
            print "Warning: There is no filename for the input file ({})".format(absolute_path)
        return filename

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
