class GeoListMetadata(object):

    """
    Metadata for the GeoLists, a list of which is maintained as GeoProcessor.GeoLists
    This class is used to hold GeoList properties for each registered GeoList.
    """

    def __init__(self, geolist_id, geolayer_id_list):

        # "id" is a string that is the GeoList's reference ID. This ID is used to call the GeoList into the GeoProcessor
        # for manipulation.
        self.id = geolist_id

        # "geolayers" is a list of strings. The strings are the ids of the GeoLayer objects that are included in the
        # GeoList.
        self.geolayers = geolayer_id_list
