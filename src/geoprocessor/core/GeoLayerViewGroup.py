# Class to hold a group of GeoLayerView
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

from geoprocessor.core.GeoLayerView import GeoLayerView


class GeoLayerViewGroup(object):

    def __init__(self, geolayerviewgroup_id: str, name: str, description: str = ""):
        """
        Create a GeoLayerViewGroup, which contains a list of GeoLayerView.

        Args:
            geolayerviewgroup_id (str):  Identifier for the GeoLayerViewGroup, used for data manipulation.
            name (str):  Name of the GeoLayerViewGroup used to label the view group.
            description (str):  Description, used to describe the view group (default is empty string).
        """

        # Unique identifier.
        self.id = geolayerviewgroup_id

        # Name, used to display layer legend.
        self.name = name

        # Description.
        self.description = description

        # Additional properties for the layer view.
        self.properties = dict()

        # List of GeoLayerView in the group.
        self.geolayerviews = []

    def get_geolayerview(self, geolayerview_id: str) -> GeoLayerView or None:
        """
        Return the GeoLayerView that matches the requested ID.

        Args:
            geolayerview_id (str):  GeoLayerView ID string.

        Returns:
            The GeoLayerView that matches the requested ID, or None if not found.
        """
        for geolayerview in self.geolayerviews:
            if geolayerview is not None:
                if geolayerview.id == geolayerview_id:
                    # Found the requested identifier.
                    return geolayerview
        # Did not find the requested identifier so return None.
        return None

    def set_properties(self, properties: dict, clear_first: bool = False) -> None:
        """
        Set properties.  This does not replace the properties.
        It resets existing properties or resets existing properties.

        Args:
            properties (dict): properties to set.
            clear_first (bool) if True, clear the dictionary first (default is False)

        Returns:
            None
        """
        if clear_first:
            self.properties.clear()

        for key in properties:
            self.properties[key] = properties[key]

    def to_json(self):
        """
        Return dictionary of class data to support JSON serialization using json package.
        """
        use_dict = False
        if use_dict:
            # Dictionary has too much information but is useful to illustrate what objects need to be handled.
            return self.__dict__
        else:
            return {
                "geoLayerViewGroupId": self.id,
                "name": self.name,
                "description": self.description,
                "properties": self.properties,
                "geoLayerViews": self.geolayerviews
            }
