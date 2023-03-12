# GeoLayerList - class to hold a list of GeoLayer
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2023 Open Water Foundation
#
# GeoProcessor is free software:  you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     GeoProcessor is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with GeoProcessor.  If not, see <https://www.gnu.org/licenses/>.
# ________________________________________________________________NoticeEnd___


class GeoLayerList(object):
    """
    Metadata for the GeoLayerLists, a list of which is maintained as GeoProcessor.GeoLayerLists.
    This class is used to hold GeoLayerList properties for each registered GeoLayerList.
    """

    def __init__(self, geolist_id: str, geolayer_id_list: [str]) -> None:

        # GeoLayerList's reference ID.
        # This ID is used to call the GeoLayerList into the GeoProcessor for manipulation.
        self.id = geolist_id

        # The ids of the GeoLayer identifiers that are included in the GeoLayerList.
        self.geolayers = geolayer_id_list

        # Properties for the layer list.
        self.properties = dict()

    def get_property(self, property_name: str, if_not_found_val: bool = None,
                     if_not_found_except: bool = False) -> object:
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
            KeyError if if_not_found_except=True and the property name is not found.
        """
        try:
            return self.properties[property_name]
        except KeyError:
            if if_not_found_except is True:
                # Let the exception from not finding a key in the dictionary be raised.
                # print('Property not found so throwing exception')
                raise
            else:
                return if_not_found_val
