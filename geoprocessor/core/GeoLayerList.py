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

    def get_property(self, property_name, if_not_found_val=None, if_not_found_except=False):
        """
        Get a GeoLayerList property, case-specific.

        Args:
            property_name (str):  Name of the property for which a value is retrieved.
            if_not_found_val (object):  If the property is not found, return this value (None is default).
            if_not_found_except (bool):  If the property is not found, raise a KeyError exception.
                This is by default False in preference to if_not_found_val being used.
                However, if the value is True, this will throw an exception rather than using the default value.
                This is expected to be used when it is really not OK to default the returned value.

        Returns:
            The object for the requested property name, or if not found the value of if_not_found_val.

        Raises:
            KeyError if if_not_found_exept=True and the property name is not found.
        """
        try:
            return self.properties[property_name]
        except KeyError:
            if if_not_found_except is True:
                # Let the exception from not finding a key in the dictionary be raised
                # print('Property not found so throwing exception')
                raise
            else:
                return if_not_found_val

    def get_geolayeridlist(self, geolayerlist_id):
        """
        Returns a list of GeoLayer ids that are inside the specified GeoLayerList.

        Args:
            self (obj): the GeoProcessor instance
            geolayerlist_id (string): the identifier of the GeoLayerList to read

        Return:
            A list of strings. Each string represents the identifier of each GeoLayer within the GeoLayerList.

        Raises:
            Value Error if the geolayerlist_id is not a valid GeoLayerListID.
        """

        # Check that the input GeoLayerList is a registered GeoLayerList within the GeoProcessor.
        if is_geolayerlist_id(self, geolayerlist_id):

            # Get the appropriate GeoLayerList
            geolayerlist = self.command_processor.get_geolayerlist(self, geolayerlist_id)

            # Return the GeoLayerLists's list of GeoLayer IDs
            return geolayerlist.get_property("geolayer_id_list")

        else:
            raise ValueError
