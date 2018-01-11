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


def is_geolayer_id(self, input_id):

    """
    Checks if the id is a registered GeoLayer id (within the GeoProcessor's geolayers list).

    Args:
        self (obj): the GeoProcessor instance
        input_id (string): the identifier of the GeoLayer that is being checked for existence

    Returns:
        Boolean. Returns TRUE if the input GeoLayer id is already registered within the GeoProcessor. Returns FALSE if
            the input GeoLayer id is not registered within the GeoProcessor.
    """

    # Get the GeoLayer associated with the input_id
    geolayer = self.command_processor.get_geolayer(self, input_id)

    # If the geolayer variable is None, then the input_id is not a valid GeoLayerID
    if geolayer:
        return True
    else:
        "ID ({}) is not a valid GeoLayer ID.".format(input_id)
        return False


def is_geolayerlist_id(self, input_id):

    """
    Checks if the id is a registered GeoLayerList id (within the GeoProcessor's geolayerlists list).

    Args:
        self (obj): the GeoProcessor instance
        input_id (string): the identifier of the GeoLayerList that is being checked for existence

    Return:
        Boolean. Returns TRUE if the input GeoLayerList id is already registered within the GeoProcessor. Returns FALSE
            if the input GeoLayerList id is not registered within the GeoProcessor.
    """

    # Get the GeoLayerList associated with the input_id
    geolayerlist = self.command_processor.get_geolayerlist(self, input_id)

    # If the geolayerlist variable is None, then the input_id is not a valid GeoLayerListID
    if geolayerlist:
        return True
    else:
        "ID ({}) is not a valid GeoLayerList ID.".format(input_id)
        return False


def return_geolayer_ids_from_geolayerlist_id(self, geolayerlist_id):

    """
    Returns a list of GeoLayer ids that are inside the specified GeoLayerList.

    Args:
        self (obj): the GeoProcessor instance
        geolayerlist_id (string): the identifier of the GeoLayerList to read

    Return:
        A list of strings. Each string represents the identifier of each GeoLayer within the GeoLayerList.
    """

    # Check that the input GeoLayerList is a registered GeoLayerList within the GeoProcessor.
    if is_geolayerlist_id(self, geolayerlist_id):

        # Get the appropriate GeoLayerList
        geolayerlist = self.command_processor.get_geolayerlist(self, geolayerlist_id)

        # Return the GeoLayerLists's list of GeoLayer IDs
        return geolayerlist.geolayer_id_list

    # If the provided GeoLayerList ID is not registered within the GeoProcessor, return None and print a message.
    else:
        print "GeoLayerList ID ({}) is not a registered GeoLayerList ID.".format(geolayerlist_id)
        return None
