# GeoMap- class for map
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2020 Open Water Foundation
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


class GeoMap(object):
    """
    Map project that when serialized using the json package "dump" and "dumps" functions will
    result in a JSON map project file that can be used by other tools such as Leaflet map viewer.
    The organization of objects is:

    GeoMap                             # File and object that represent a map's configuration
        GeoLayer []                    # Shared list of layers, if maps can share for viewing (leaflet cannot share)
        GeoLayerViewGroup []           # Groups of layer views, as per typical GIS legend
            GeoLayerView[]             # A single map view that uses one or more layers
                GeoLayer               # ID will be used in output to reference above GeoLayer []
                GeoLayerSymbol         # Symbol configuration for the layer
    """
    def __init__(self):
        # Dictionary of general map properties
        self.properties = {}

        # Array of GeoLayer objects, which supply data for the layer views
        self.layers = []

        # Array of GeoLayerViewGroup
        self.layerViewGroups = []

    def to_json(self):
        """
        Return dictionary of class data to support JSON serialization using Python 'json' package.
        """
        use_dict = True
        if use_dict:
            # Just return the dictionary since it is equivalent to the other option
            return self.__dict__
        else:
            # Return a dictionary with JSON objects
            # - included for illustration, but equivalent to the above
            return {
                "properties": self.properties,
                "layers": self.layers,
                "layerViewGroups": self.layerViewGroups
            }
