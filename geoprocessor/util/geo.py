# Utility functions related to GeoProcessor Geo commands


def is_geolayer_id(self, layer_id):
    """
    Checks if the layer_id is a registered geolayer id. Returns TRUE, if it is is and FALSE, if not.
    """

    # Get list of all registered geolayer ids.
    list_of_geolayer_ids = list(self.command_processor.geolayers.keys())
    if layer_id in list_of_geolayer_ids:
        return True
    else:
        return False


def is_geolist_id(self, geolist_id):
    """
    Checks if the geolist_id is a registered geolist id. Returns TRUE, if it is is and FALSE, if not.
    """

    # Get list of all registered geolist ids.
    list_of_geolist_ids = list(self.command_processor.geolists.keys())
    if geolist_id in list_of_geolist_ids:
        return True
    else:
        return False


def return_geolayer_ids_from_geolist_id(self, geolist_id):
    """
    Returns a list of geolayer ids that are inside the specified geolist.
    """

    if self.is_geolist_id(geolist_id):
        return self.command_processor.geolists[geolist_id]
    else:
        print "Geolist ID ({}) is not a registered geolist id.".format(geolist_id)
        return None
