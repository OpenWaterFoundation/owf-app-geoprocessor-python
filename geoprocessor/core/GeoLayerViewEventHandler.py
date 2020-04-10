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


class GeoLayerViewEventHandler(object):
    """
    The GeoLayerViewEventHandler class represents a handler for UI event that should be implemented to
    interact with the layer view.
    """
    def __init__(self,
                 event_type: str,
                 name: str = "",
                 description: str = "",
                 properties: dict = None) -> None:
        """
        Construct a new GeoLayerViewEventHandler, which represents a UI event handler that should be implemented
        in application code.

        Args:
            event_type (str): Event type, need to standardize.
            name (str): Event name.
            description (str): Event description.
            properties (dict): Properties for the event handler.
        """
        # Name for the event
        self.name = name

        # Description for the event
        self.description = description

        # Event type
        self.event_type = event_type

        # Properties for the event
        if properties is None:
            # Initialize an empty dictionary
            self.properties = {}
        else:
            # Use the dictionary that was passed in
            self.properties = properties

    def to_json(self):
        """
        Return dictionary of class data to support JSON serialization using json package.
        """
        return {
            "eventType": self.event_type,
            "name": self.name,
            "description": self.description,
            "properties": self.properties
        }
