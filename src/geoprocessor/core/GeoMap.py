# GeoMap- class for map
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
import logging

from qgis.core import QgsCoordinateReferenceSystem

from geoprocessor.core.GeoLayer import GeoLayer
from geoprocessor.core.GeoLayerView import GeoLayerView
from geoprocessor.core.GeoLayerViewGroup import GeoLayerViewGroup

import geoprocessor.util.qgis_util as qgis_util


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

    # Default CRS code.
    default_crs_code = "EPSG:4326"

    def __init__(self,
                 geomap_id: str,
                 name: str = "",
                 description: str = "",
                 data_path: str = ".",
                 crs_code: str = default_crs_code) -> None:
        """
        Create a new GeoMap.

        Args:
            geomap_id (str): Unique identifier for the GeoMap.
            name (str): Name for the GeoMap.
            description (str): Description for the GeoMap.
            crs_code (str): CRS code such as "EPSG:4326"
        """

        # Identifier for GeoMap.
        self.id = geomap_id

        # Name for the GeoMap.
        self.name = name

        # Description for the GeoMap.
        self.description = description

        # Coordinate Reference System (CRS) for the map:
        # - this will be set to None if CRS is not found
        self.crs: QgsCoordinateReferenceSystem or None = qgis_util.parse_qgs_crs(crs_code)

        # Data path for the GeoMap, folders or URL path to look for data:
        # - geolayer file name will be relative to this, if not specified as absolute path
        self.data_path: str = data_path

        # Dictionary of general map properties.
        self.properties = dict()

        # Array of GeoLayer objects, which supply data for the layer views.
        self.geolayers = []

        # Array of GeoLayerViewGroup.
        self.geolayerviewgroups = []

    def add_geolayer(self, geolayer: GeoLayer) -> None:
        """
        Add a GeoLayer object to the geolayers list. If a geolayer already exists with the same GeoLayer ID,
        the existing GeoLayer will be replaced with the input GeoLayer.
        The GeoLayer can be either a VectorGeoLayer or RasterGeoLayer.

        Args:
            geolayer: instance of a GeoLayer object

        Returns:
            None
        """

        # Iterate over the existing GeoLayers.
        for existing_geolayer in self.geolayers:
            # If an existing GeoLayer has the same ID as the input GeoLayer, remove the existing GeoLayer from the
            # geolayers list.
            if existing_geolayer.id == geolayer.id:
                self.free_geolayer(existing_geolayer)

        # Add the input GeoLayer to the geolayers list.
        self.geolayers.append(geolayer)

    def add_geolayerview_to_geolayerviewgroup(self, geolayerview: GeoLayerView,
                                              geolayerviewgroup: GeoLayerViewGroup or str,
                                              insert_position: str = None,
                                              insert_before: str = None,
                                              insert_after: str = None) -> None:
        """
        Add a GeoLayerView object to the geolayers list. If a geolayer already exists with the same GeoLayer ID,
        the existing GeoLayer will be replaced with the input GeoLayer.
        The GeoLayer can be either a VectorGeoLayer or RasterGeoLayer.

        Args:
            geolayerview (GeoLayer): instance of a GeoLayerView - with the GeoLayer already assigned
            geolayerviewgroup (GeoLayerViewGroup): instance of a GeoLayerViewGroup or GeoLayerViewGroupID
            insert_position (str): 'Bottom' or 'Top' to indicate general insert position
            insert_before (str):  GeoLayerView to insert before
            insert_after (str):  GeoLayerView to insert after

        Returns:
            None
        """

        # First insert the GeoLayer for complete list of layers associated with the GeoMap:
        # - this is done in case any downstream technologies can utilize shared layers
        # - the order is not important since position is handled in the GeoLayerViewGroup
        if geolayerview.geolayer is None:
            raise ValueError("GeoLayerView '{}' GeoLayer is not set.  Can't add GeoLayerView".format(geolayerview.id))
        else:
            self.add_geolayer(geolayerview.geolayer)

        # If the geolayerviewgroup is a string, get the object that corresponds to the given identifier.
        if isinstance(geolayerviewgroup, str):
            # Get the geolayerviewgroup using its ID.
            geolayerviewgroup_id = geolayerviewgroup
            geolayerviewgroup = self.get_geolayerviewgroup(geolayerviewgroup_id)
            if geolayerviewgroup is None:
                raise ValueError(
                    "GeoLayerViewGroup with ID '{}' does not exist.  Cannot add GeoLayer to GeoMap.".format(
                        geolayerviewgroup_id))
        # Else the GeoLayerViewGroup instance was passed in.

        # Add the GeoLayerView to the GeoLayerViewGroup.

        # Iterate over the existing GeoLayerView and if found, remove the previous instance.
        for existing_geolayerview in geolayerviewgroup.geolayerviews:
            # If an existing GeoLayerView has the same ID as the input GeoLayerView,
            # remove the existing GeoLayerView from the geolayerviews list.
            if existing_geolayerview.id == geolayerview.id:
                geolayerviewgroup.free_geolayerview(existing_geolayerview)

        # Add the input GeoLayerView to the geolayerviews list.
        if insert_before is not None and (insert_before != ""):
            # Insert before the specified GeoLayerViewID
            insert_index = -1
            for geolayerview in geolayerviewgroup.geolayerviews:
                insert_index += 1
                if geolayerview.id == insert_before:
                    # Found the insert position.
                    geolayerviewgroup.geolayerviews.insert(insert_index, geolayerview)
            if insert_index < 0:
                raise ValueError("GeoLayerViewID '" + insert_before + "' does not exist - can't insert '" +
                                 geolayerview.id + "'")
        elif insert_after is not None and (insert_after != ""):
            # Insert after the specified GeoLayerViewID.
            insert_index = -1
            for geolayerview in geolayerviewgroup.geolayerviews:
                insert_index += 1
                if geolayerview.id == insert_after:
                    geolayerviewgroup.geolayerviews.insert((insert_index + 1), geolayerview)
            if insert_index < 0:
                raise ValueError("GeoLayerViewID '" + insert_after + "' does not exist - can't insert '" +
                                 geolayerview.id + "'")
        elif insert_position is not None and (insert_position != ""):
            # Insert using a general position.
            insert_position_upper = insert_position.upper()
            if insert_position_upper == 'TOP':
                if len(geolayerviewgroup.geolayerviews) == 0:
                    # Nothing in the list so just append.
                    geolayerviewgroup.geolayerviews.append(geolayerview)
                else:
                    # Insert at the front of the list.
                    geolayerviewgroup.geolayerviews.insert(0, geolayerview)
            elif insert_position_upper == 'BOTTOM':
                # Insert at the end of the list.
                geolayerviewgroup.geolayerviews.append(geolayerview)
        else:
            # Insert at the end.
            geolayerviewgroup.geolayerviews.append(geolayerview)

    def add_geolayerviewgroup(self,
                              geolayerviewgroup: GeoLayerViewGroup,
                              insert_position: str = None,
                              insert_before: str = None,
                              insert_after: str = None) -> None:
        """
        Add a GeoLayerViewGroup object to the geolayergroupviews list.
        If a GeoLayerViewGroup already exists with the same GeoLayer ID,
        the existing GeoLayer will be replaced with the input GeoLayer.
        The GeoLayer can be either a VectorGeoLayer or RasterGeoLayer.

        Args:
            geolayerviewgroup (GeoLayerViewGroup): instance of a GeoLayerViewGroup object to add or string
                identifier to look up instance
            insert_position (str): 'Bottom' or 'Top' to indicate general insert position
            insert_before (str):  GeoLayerViewGroupID to insert before
            insert_after (str):  GeoLayerViewGroupID to insert after

        Returns:
            None

        Raises:
            ValueError if the insert position is invalid.
        """
        debug = True
        logger = None
        if debug:
            logger = logging.getLogger(__name__)

        # Iterate over the existing GeoLayerViewGroups and if found, remove the previous instance.
        for existing_geolayerviewgroup in self.geolayerviewgroups:
            # If an existing GeoLayerViewGroup has the same ID as the input GeoLayerViewGroup,
            # remove the existing GeoLayerLayerView from the # geolayerviewgroups list.
            if existing_geolayerviewgroup.id == geolayerviewgroup.id:
                self.free_geolayerviewgroup(existing_geolayerviewgroup)

        # Add the input GeoLayerViewGroup to the geolayerviewgroups list.
        if insert_before is not None and (insert_before != ""):
            # Insert before the specified GeoLayerViewGroupID.
            insert_index = -1
            for geolayerviewgroup in self.geolayerviewgroups:
                insert_index += 1
                if geolayerviewgroup.id == insert_before:
                    # Found the insert position.
                    self.geolayerviewgroups.insert(insert_index, geolayerviewgroup)
                    if debug:
                        logger.info("Inserting GeoLayerViewGroup {} at position [{}].".format(
                            geolayerviewgroup.id, insert_index))
                    break
            if insert_index < 0:
                raise ValueError("GeoLayerViewGroupID '" + insert_before + "' does not exist - can't insert '" +
                                 geolayerviewgroup.id + "'")
        elif insert_after is not None and (insert_after != ""):
            # Insert after the specified GeoLayerViewGroupID.
            insert_index = -1
            for geolayerviewgroup in self.geolayerviewgroups:
                insert_index += 1
                if geolayerviewgroup.id == insert_after:
                    self.geolayerviewgroups.insert((insert_index + 1), geolayerviewgroup)
                    if debug:
                        logger.info("Inserting GeoLayerViewGroup {} at position [{}].".format(
                            geolayerviewgroup.id, (insert_index + 1)))
                    break
            if insert_index < 0:
                raise ValueError("GeoLayerViewGroupID '" + insert_after + "' does not exist - can't insert '" +
                                 geolayerviewgroup.id + "'")
        elif insert_position is not None and (insert_position != ""):
            # Insert using a general position.
            insert_position_upper = insert_position.upper()
            if insert_position_upper == 'TOP':
                if len(self.geolayerviewgroups) == 0:
                    # Nothing in the list so just append.
                    self.geolayerviewgroups.append(geolayerviewgroup)
                    if debug:
                        logger.info("Inserting GeoLayerViewGroup {} at position [0].".format(geolayerviewgroup.id))
                else:
                    # Insert at the front of the list.
                    self.geolayerviewgroups.insert(0, geolayerviewgroup)
                    if debug:
                        logger.info("Inserting GeoLayerViewGroup {} at position [0].".format(geolayerviewgroup.id))
            elif insert_position_upper == 'BOTTOM':
                # Insert at the end of the list.
                self.geolayerviewgroups.append(geolayerviewgroup)
                if debug:
                    logger.info("Inserting GeoLayerViewGroup {} at bottom.".format(geolayerviewgroup.id))
        else:
            # Insert at the end.
            self.geolayerviewgroups.append(geolayerviewgroup)
            if debug:
                logger.info("Inserting GeoLayerViewGroup {} at end.".format(geolayerviewgroup.id))

    def free_geolayer(self, geolayer: GeoLayer) -> None:
        """
        Removes a GeoLayer object from the geolayers list.

        Args:
            geolayer: instance of a GeoLayer object

        Return:
            None
        """
        self.geolayers.remove(geolayer)

    def free_geolayerviewgroup(self, geolayerviewgroup: GeoLayerViewGroup) -> None:
        """
        Removes a GeoLayerViewGroup object from the geolayerviewgroups list.

        Args:
            geolayerviewgroup: instance of a GeoLayerViewGroup object

        Return:
            None
        """
        self.geolayerviewgroups.remove(geolayerviewgroup)

    def get_crs_code(self) -> str:
        """
        Returns the coordinate reference system (str, EPSG code) of a GeoMap.

        Returns:
            CRS as str.
        """
        # <EPSG format 'http://spatialreference.org/ref/epsg/'>_. Return the crs variable.
        return self.crs.authid()

    def get_geolayer(self, geolayer_id: str) -> GeoLayer or None:
        """
        Return the GeoLayer that matches the requested ID.

        Args:
            geolayer_id (str):  GeoLayer ID string.

        Returns:
            The GeoLayer that matches the requested ID, or None if not found.
        """
        for geolayer in self.geolayers:
            if geolayer is not None:
                if geolayer.id == geolayer_id:
                    # Found the requested identifier.
                    return geolayer
        # Did not find the requested identifier so return None.
        return None

    def get_geolayerviewgroup(self, geolayerviewgroup_id: str) -> GeoLayerViewGroup or None:
        """
        Return the GeoLayerViewGroup that matches the requested ID.

        Args:
            geolayerviewgroup_id (str):  GeoLayerViewGroup ID string.

        Returns:
            The GeoLayerViewGroup that matches the requested ID, or None if not found.
        """
        for geolayerviewgroup in self.geolayerviewgroups:
            if geolayerviewgroup is not None:
                if geolayerviewgroup.id == geolayerviewgroup_id:
                    # Found the requested identifier.
                    return geolayerviewgroup
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
        Return dictionary of class data to support JSON serialization using Python 'json' package.
        """
        use_dict = False
        if use_dict:
            # Just return the dictionary since it is equivalent to the other option.
            return self.__dict__
        else:
            # Return a dictionary with JSON objects:
            # - this remaps the names to camelcase, which is is more consistent with JSON standards
            return {
                "geoMapId": self.id,
                "name": self.name,
                "description": self.description,
                "dataPath": self.data_path,
                "crs": self.get_crs_code(),
                "properties": self.properties,
                "geoLayers": self.geolayers,
                "geoLayerViewGroups": self.geolayerviewgroups
            }
