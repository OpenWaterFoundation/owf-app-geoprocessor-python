class GeoLayerList(object):

    """
    Metadata for the GeoLayerLists, a list of which is maintained as GeoProcessor.GeoLayerLists
    This class is used to hold GeoLayerList properties for each registered GeoLayerList.
    """

    def __init__(self, geolist_id, geolayer_id_list):

        # "id" is a string that is the GeoLayerList's reference ID. This ID is used to call the GeoLayerList into the
        # GeoProcessor for manipulation.
        self.id = geolist_id

        # "geolayers" is a list of strings. The strings are the ids of the GeoLayer objects that are included in the
        # GeoLayerList.
        self.geolayers = geolayer_id_list
