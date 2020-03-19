# Class to hold a group of GeoLayerView
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

from geoprocessor.core.GeoLayerView import GeoLayerView


class GeoLayerViewGroup(object):

    def __init__(self, geolayerviewgroup_id: str, name: str, description: str = ""):
        """
        Create a GeoLayerViewGroup, which contains a list of GeoLayerView.

        Args:
            geolayerview_id (str):  Identifier for the GeoLayerView, used for data manipulation.
            name (str):  Name of the GeoLayerView used to label the view group.
            description (str):  Description, used to describe the view group (default is empty string).
        """

        #
        self.id = geolayerviewgroup_id

        self.name = name

        self.description =  description

        # Additional properties for the layer view
        self.properties = dict()

        # List of GeoLayerView
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
                    # Found the requested identifier
                    return geolayerview
        # Did not find the requested identifier so return None
        return None

    def to_json(self):
        """
        Return dictionary of class data to support JSON serialization using json package.
        """
        return {
            "geoLayerViewGroupId": self.id,
            "name": self.name,
            "description": self.description,
            "properties": self.properties,
            "geoLayerViews": self.geolayerviews
        }
