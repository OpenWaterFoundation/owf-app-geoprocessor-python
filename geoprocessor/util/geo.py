# Utility functions related to GeoProcessor Geo commands
import os


def is_geolayer_id(self, id):
    """
    Checks if the id is a registered GeoLayer id. Returns TRUE, if it is is and FALSE, if not.
    """

    # Get list of all registered GeoLayer ids.
    list_of_geolayer_ids = []
    for geolayer_obj in self.command_processor.geolayers:
        list_of_geolayer_ids.append(geolayer_obj.id)

    # Check if the input id is one of the registered GeoLayer ids
    if id in list_of_geolayer_ids:
        return True
    else:
        return False


def is_geolist_id(self, id):
    """
    Checks if the id is a registered GeoList id. Returns TRUE, if it is is and FALSE, if not.
    """

    # Get list of all registered GeoList ids.
    list_of_geolist_ids = []
    for geolist_obj in self.command_processor.geolayerlists:
        list_of_geolist_ids.append(geolist_obj.id)

    # Check if the input id is one of the registered GeoList ids
    if id in list_of_geolist_ids:
        return True
    else:
        return False


def return_geolayer_ids_from_geolist_id(self, geolist_id):
    """
    Returns a list of GeoLayer ids that are inside the specified GeoList.
    """

    # Check that the provided GeoList ID is a registered GeoList ID. Only continue, if True. Otherwise print error
    # message and return None.
    if is_geolist_id(self, geolist_id):

        # Iterate through each of the registered GeoList objects. Only continue if the GeoList object's id is the same
        # as the provided GeoList ID. Return the GeoList object's geolayer_id_list property.
        for geolist_obj in self.command_processor.GeoLists:
            if geolist_obj.id == geolist_id:

                return geolist_obj.geolayer_id_list
    else:
        print "GeoList ID ({}) is not a registered GeoList id.".format(geolist_id)
        return None


def get_qgsvectorlayer_from_geolayer(self, geolayer_id):

    # Check that the input GeoLayer is a registered GeoLayer within the GeoProcessor.
    if is_geolayer_id(self, geolayer_id):

        # Iterate over the GeoLayers registered within the GeoProcessor.
        for geolayer in self.command_processor.GeoLayers:

            # If the "input" GeoLayer ID is the same as the "registered" GeoLayer ID, return the qgs_vector_layer
            # property of the "registered" GeoLayer ID. The qgs_vector_layer property holds the QGSVectorLayer object
            # of the "registered" GeoLayer.
            if geolayer_id == geolayer.id:

                return geolayer.qgs_vector_layer

    else:

        return None


def expand_formatter(absolute_path, formatter):

    path_without_ext, extension = os.path.splitext(absolute_path)
    filename = os.path.basename(path_without_ext)

    if formatter == '%F':

        if extension == '':
            print "Warning: There is no file extension for the input file ({})".format(absolute_path)
        if filename == '':
            print "Warning: There is no filename for the input file ({})".format(absolute_path)
        return "{}{}".format(filename, extension)

    elif formatter == '%f':

        if filename == '':
            print "Warning: There is no filename for the input file ({})".format(absolute_path)
        return filename

    elif formatter == '%E':

        if extension == '':
            print "Warning: There is no file extension for the input file ({})".format(absolute_path)
        return extension

    else:

        print "The formatter ({}) is not an option."
        return None
