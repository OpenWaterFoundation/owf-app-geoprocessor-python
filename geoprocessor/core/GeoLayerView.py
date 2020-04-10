# GeoLayerView - Class to hold a layer and its symbology
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

from geoprocessor.core.GeoLayer import GeoLayer
from geoprocessor.core.GeoLayerSymbol import GeoLayerSymbol
from geoprocessor.core.GeoLayerViewEventHandler import GeoLayerViewEventHandler


class GeoLayerView(object):
    """
    The GeoLayerView class encapsulates a GeoLayer and a GeoLayerSymbol object used to symbolize that layer.
    """
    def __init__(self, geolayerview_id: str, geolayer: GeoLayer, name: str, description: str = "") -> None:
        # Identifier
        self.id = geolayerview_id

        # Name for the layer view
        self.name = name

        # Description for the layer view
        self.description = description

        # GeoLayer object
        self.geolayer = geolayer

        # GeoLayerSymbol object
        # - TODO smalers 2020-03-18 need to define a default based on data
        # - the symbol is expected to be set by calling a set method because it originates in a separate command
        # - specific child classes may be derived from parent class GeoLayerSymbol
        self.geolayersymbol: GeoLayerSymbol or None = None

        # Properties, currently not used
        self.properties = dict()

        # Event handlers for the GeoLayerView
        # - code that reads the map should implement handlers for the specified event types
        # - initialize to an empty list
        self.event_handlers: [GeoLayerViewEventHandler] or None = []

    def to_json(self):
        """
        Return dictionary of class data to support JSON serialization using json package.
        """
        return {
            "geoLayerViewId": self.id,
            "name": self.name,
            "description": self.description,
            # GeoLayer information is provided by reference to the main list of GeoLayer
            # - this allows sharing the layers if software allows, although Leaflet does not allow sharing
            #   layers between maps (?)
            # - TODO smalers 2020-03-20 may need a property to indicate whether sharing or not
            "geoLayerId": self.geolayer.id,
            "properties": self.properties,
            "geoLayerSymbol": self.geolayersymbol,
            "eventHandlers": self.event_handlers
        }
