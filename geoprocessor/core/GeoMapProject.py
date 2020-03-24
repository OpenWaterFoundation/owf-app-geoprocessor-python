# GeoMapProject- class for map project, which contains 1+ GeoMap and other data
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

from geoprocessor.core.GeoMap import GeoMap


class GeoMapProject(object):
    """
    Map project that when serialized using the json package "dump" and "dumps" functions will
    result in a JSON map project file that can be used by other tools such as Leaflet map viewer.
    The organization of objects is:

    GeoMapProject                          # File that represents 1+ map's configuration
        GeoMap []                          # File and object that represent a map's configuration
            GeoLayer []                    # Shared list of layers, if maps can share for viewing (leaflet cannot share)
            GeoLayerViewGroup []           # Groups of layer views, as per typical GIS legend
                GeoLayerView []            # A single map view that uses one or more layers
                    GeoLayer               # ID will be used in output to reference above GeoLayer []
                    GeoLayerSymbol         # Symbol configuration for the layer
    """

    def __init__(self,
                 geomapproject_id: str,
                 name: str = "",
                 description: str = "") -> None:
        """
        Create a new GeoMapProject.

        Args:
            geomapproject_id (str): Unique identifier for the GeoMapProject.
            name (str): Name for the GeoMap.
            description (str): Description for the GeoMap.
        """

        # Identifier for GeoMapProject
        self.id = geomapproject_id

        # Name for the GeoMapProject
        self.name = name

        # Description for the GeoMapProject
        self.description = description

        # Project type (dashboard, grid, story, single map, etc.)
        # - TODO smalers 2020-03-23 need to define as enumeration
        self.project_type = ""

        # Dictionary of general map properties
        # - name
        # - description
        self.properties = dict()

        # Array of GeoMap objects
        self.geomaps = []

    def add_geomap(self, geomap: GeoMap or str,
                   insert_position: str = None,
                   insert_before: str = None,
                   insert_after: str = None) -> None:
        """
        Add a GeoMap object to the geomaps list. If a geomap already exists with the same GeoMap ID, the
        existing GeoMap will be replaced with the input GeoLayer.

        Args:
            geomap: instance of a GeoMap object or GeoMapID to get the instance
            insert_position (str): 'Bottom' or 'Top' to indicate general insert position
            insert_before (str):  GeoMap to insert before
            insert_after (str):  GeoMap to insert after

        Returns:
            None
        """

        # Iterate over the existing GeoMaps.
        for existing_geomap in self.geomaps:
            # If an existing GeoMap has the same ID as the input GeoMap, remove the existing GeoMap from the
            # geomaps list.
            if existing_geomap.id == geomap.id:
                self.free_geomap(existing_geomap)

        # If the geomap is a string, get the object that corresponds to the given identifier.
        if isinstance(geomap, str):
            # Get the geolayerviewgroup using its ID
            geomap_id = geomap
            geomap = self.get_geomap(geomap_id)
            if geomap is None:
                raise ValueError(
                    "GeoMap with ID '{}' does not exist.  Cannot add GeoMap to GeoMapProject.".format(geomap_id))
        # Else the GeoLayerViewGroup instance was passed in

        # Add the input GeoMap to the geomaps list.
        if insert_before is not None and (insert_before != ""):
            # Insert before the specified GeoLayerViewID
            insert_index = -1
            for geomap in self.geomaps:
                insert_index += 1
                if geomap.id == insert_before:
                    # Found the insert position
                    self.geomaps.insert(insert_index, geomap)
            if insert_index < 0:
                raise ValueError("GeoMapID '{}' does not exist - can't insert '{}'".format(insert_before, geomap.id))
        elif insert_after is not None and (insert_after != ""):
            # Insert after the specified GeoMapID
            insert_index = -1
            for geomap in self.geomaps:
                insert_index += 1
                if geomap.id == insert_after:
                    self.geomaps.insert((insert_index + 1), geomap)
            if insert_index < 0:
                raise ValueError("GeoMapID '{}' does not exist - can't insert '{}'".format(insert_after, geomap.id))
        elif insert_position is not None and (insert_position != ""):
            # Insert using a general position
            insert_position_upper = insert_position.upper()
            if insert_position_upper == 'TOP':
                if len(self.geomaps) == 0:
                    # Nothing in the list so just append
                    self.geomaps.append(geomap)
                else:
                    # Insert at the front of the list
                    self.geomaps.insert(0, geomap)
            elif insert_position_upper == 'BOTTOM':
                # Insert at the end of the list
                self.geomaps.append(geomap)
        else:
            # Insert at the end
            self.geomaps.append(geomap)

    def free_geomap(self, geomap: GeoMap) -> None:
        """
        Removes a GeoMap object from the geomaps list.

        Args:
            geomap: instance of a GeoMap object to remove

        Return:
            None
        """
        self.geomaps.remove(geomap)

    def get_geomap(self, geomap_id: str) -> GeoMap or None:
        """
        Return the GeoMap that matches the requested ID.

        Args:
            geomap_id (str):  GeoMap ID string.

        Returns:
            The GeoMap that matches the requested ID, or None if not found.
        """
        for geomap in self.geomaps:
            if geomap is not None:
                if geomap.id == geomap_id:
                    # Found the requested identifier
                    return geomap
        # Did not find the requested identifier so return None
        return None

    def set_properties(self, properties: dict, clear_first: bool = False) -> None:
        """
        Set properties.  This does not replace the properties - it resets existing properties or resets
        existing properties.

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
        Return dictionary of class data to support JSON serialization using Python 'json' package.
        """
        use_dict = False
        if use_dict:
            # Dictionary has too much information but is useful to illustrate what objects need to be handled.
            return self.__dict__
        else:
            # Return a dictionary with JSON objects
            # - this remaps the names to camelcase, which is is more consistent with JSON standards
            return {
                "geoMapProjectId": self.id,
                "name": self.name,
                "description": self.description,
                "properties": self.properties,
                "projectType": "",
                "geoMaps": self.geomaps,
            }
