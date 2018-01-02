# Utility functions related to GeoProcessor Geo commands


def is_geolayer_id(self, id):
    """
    Checks if the id is a registered GeoLayer id. Returns TRUE, if it is is and FALSE, if not.
    """

    # Get list of all registered GeoLayer ids.
    list_of_geolayer_ids = list(self.command_processor.GeoLayers.keys())
    if id in list_of_geolayer_ids:
        return True
    else:
        return False


def is_geolist_id(self, id):
    """
    Checks if the id is a registered GeoList id. Returns TRUE, if it is is and FALSE, if not.
    """

    # Get list of all registered GeoList ids.
    list_of_geolist_ids = list(self.command_processor.GeoLists.keys())
    if id in list_of_geolist_ids:
        return True
    else:
        return False


def return_geolayer_ids_from_geolist_id(self, geolist_id):
    """
    Returns a list of GeoLayer ids that are inside the specified GeoList.
    """

    if self.is_geolist_id(geolist_id):
        return self.command_processor.GeoLists[geolist_id]
    else:
        print "GeoList ID ({}) is not a registered GeoList id.".format(geolist_id)
        return None
