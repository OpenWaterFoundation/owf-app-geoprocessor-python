# GeoLayer - class for GeoLayer (base class for spatial data layer)
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

# The following is needed to allow type hinting -> GeoLayer, and requires Python 3.7+
# See:  https://stackoverflow.com/questions/33533148/
#         how-do-i-specify-that-the-return-type-of-a-method-is-the-same-as-the-class-itsel
from __future__ import annotations

from qgis.core import QgsMapLayer as QgsMapLayer
from qgis.core import QgsCoordinateReferenceSystem as QgsCoordinateReferenceSystem

# import logging


class GeoLayer(object):
    """
    The GeoLayer class stores geometry and identifier data for a spatial data layer. The core layer data are stored in
    a QgsVectorLayer or QgsRasterObject instances, indicated as QgsMapLayer base class,
    in order to leverage the QGIS data model and functionality. Additional data members are
    used to store data that are not part of QgsVectorLayer objects and are required by the GeoProcessor, such as source
    filename and identifier used by the GeoProcessor.

    A list of registered GeoLayer instances are maintained in the GeoProcessor's self.geolayers property (type: list).
    The GeoProcessor's commands retrieve in-memory GeoLayer instances from the GeoProcessor's self.geolayers property
    using the GeoProcessor.get_geolayer() function. New GeoLayer instances are added to the GeoProcessor list using the
    add_geolayer() function.

    There are a number of properties associated with each GeoLayer (id, coordinate reference system, feature count,
    etc.) The GeoLayer properties stored within each GeoLayer instance are the STATIC properties that will never change
    (ids, QgsMapLayer object, and source path). The DYNAMIC GeoLayer properties (coordinate reference
    system, feature count, etc.) are created when needed by accessing class functions.

    GeoLayers can be made in memory from within the GeoProcessor. This occurs when a command is called that, by design,
    creates a new GeoLayer (example: Clip). When this occurs, the in-memory GeoLayer is assigned a geolayer_id from
    within the command, the geolayer_qgs_vector_layer is created from within the command and the geolayer_source_path
    is set to 'MEMORY'.
    """

    # Indicates that the layer source is memory, rather than being read from a file.
    # - used with input_source* and output_source* values
    SOURCE_MEMORY = 'MEMORY'

    def __init__(self, geolayer_id: str,
                 name: str,
                 description: str = "",
                 qgs_layer: QgsMapLayer = None,
                 input_path_full: str = SOURCE_MEMORY,
                 input_path: str = SOURCE_MEMORY,
                 properties: dict = None) -> None:
        """
        Initialize a new GeoLayer instance.

        Args:
            geolayer_id (str):
                String that is the GeoLayer's reference ID.
                This ID is used to access the GeoLayer from the GeoProcessor for manipulation.
            name (str):
                Layer name, will be used in map legend, etc.
            description (str):
                Layer description, with more details.
            qgs_layer (QgsVectorLayer or QgsRasterLayer instance via those class __init__() function):
                Object created by the QGIS processor.
                All GeoLayer spatial manipulations are performed on the GeoLayer's qgs_vector_layer.
            input_path_full (str):
                The full pathname to the input spatial data file on the local computer,
                consistent with a GeoProcessor read command after the path is expanded.
                TODO smalers 2020-03-20 evaluate whether to allow URL.
                If not specified, 'MEMORY' is used, assuming the layer was created in memory.
            input_path (str):
                The pathname to the input spatial data file on the local computer,
                consistent with a GeoProcessor read command before the path is expanded.
                This is typically a relative path but could be absolute (same as 'input_path_full').
                If not specified, 'MEMORY' is used, assuming the layer was created in memory.
            properties ({}):
                A dictionary of user (non-built-in) properties that can be assigned to the layer.
                These properties facilitate processing by external applications if written to map project.
        """

        # "id" is a string that is the GeoLayer's reference ID. This ID is used to access the GeoLayer from the
        # GeoProcessor for manipulation.
        self.id = geolayer_id

        # Name that will be used as a legend label
        self.name = name

        # Description that will be used as a legend label
        self.description = description

        # "qgs_layer" is a QgsVectorLayer or QgsRasterLayer object created by the QGIS processor.
        # All spatial manipulations are performed on the GeoLayer's qgs_layer.
        self.qgs_layer = qgs_layer

        # "input_path_full" (str) is the full pathname to the original spatial data file on the local computer:
        # - this is the expanded path using the working directory and command path
        self.input_path_full = input_path_full

        # "input_path" (str) is the relative pathname to the original spatial data file on the local computer:
        # - this is relative to the current working folder, typically just the filename or ../folder/filename
        # - it could also be the full path, which would be the same value as self.input__path_full
        self.input_path = input_path

        # "output_path_full" (str) is the full pathname to the output spatial data file on the local computer:
        # - this is the expanded path using the working directory and command path
        # - set by GeoProcessor write commands
        # - set to 'MEMORY' if the layer has not been written yet
        self.output_path_full = 'MEMORY'

        # "output_path" (str) is the relative pathname to the most recently written data file on the local computer:
        # - this is relative to the current working folder, typically just the filename or ../folder/filename
        # - it could also be the full path, which would be the same value as self.input_path_full
        self.output_path = 'MEMORY'

        # "qgs_id" (str) is the GeoLayer's id in the Qgs environment (this is automatically assigned by the QGIS
        # GeoProcessor when a GeoLayer is originally created)
        if qgs_layer is None:
            # This may happen if an error or map service
            self.qgs_id = ""
        else:
            self.qgs_id = qgs_layer.id()

        # History of modifications to the layer, performed by the GeoProcessor, as a list of strings.
        # - this is equivalent to the TSTool "genesis" data.
        # - it is useful to understand how data have been manipulated
        self.history: [str] = []

        # "properties" (dict) is a dictionary of user (non-built-in) properties that are assigned to the layer.
        # These properties facilitate processing and may or may not be output to to a persistent format,
        # depending on whether the format allows general properties on the layer.
        # If None an empty dictionary is created.
        # TODO smalers 2018-01-10 does the QGIS layer have such an object already that could be used without confusion?
        # - don't want a bunch of internal properties visible to the user.
        if properties is None:
            self.properties = {}
        else:
            self.properties = properties

    def append_to_history(self, history_comment: str or [str]) -> None:
        """
        Append the string to the layer history.
        Multiple lines should be appended with multiple calls rather than using newlines,
        perhaps with indent to represent related comments.
        For example, add a comment indicating the file that the layer was read, if manipulated, etc.

        Args:
            history_comment (str or [str]): history comment or list of comments

        Returns:
            None
        """
        if history_comment is None:
            return

        if isinstance(history_comment, str):
            # Single string so append
            self.history.append(history_comment)
        elif isinstance(history_comment, list):
            # List of strings or other objects
            for history_comment2 in history_comment:
                if history_comment2 is not None:
                    # Append the string representation of the object
                    self.history.append(str(history_comment2))

    def deepcopy(self, copied_geolayer_id: str) -> GeoLayer:
        """
        Create a copy of the GeoLayer.

        Args:
            copied_geolayer_id(str): The ID of the output copied GeoLayer.

        Returns:
            The copied GeoLayer object.
        """
        raise RuntimeError("deepcopy() function should be implemented in derived class.")

    def get_crs(self) -> QgsCoordinateReferenceSystem:
        """
        Returns the coordinate reference system EPSG object.
        """

        # "crs" (str) is the GeoLayer's coordinate reference system in
        # <EPSG format 'http://spatialreference.org/ref/epsg/'>_.
        return self.qgs_layer.crs()

    def get_crs_code(self) -> str or None:
        """
        Returns the coordinate reference system EPSG code of a GeoLayer.
        """

        # "crs" (str) is the GeoLayer's coordinate reference system in
        # <EPSG format 'http://spatialreference.org/ref/epsg/'>_.
        if self.qgs_layer is None:
            return None
        else:
            return self.qgs_layer.crs().authid()

    def get_feature_count(self) -> int:
        """
        Returns the number of features (int) within a GeoLayer.
        """
        raise RuntimeError("get_feature_count() function should be implemented in derived class.")

    def get_geometry(self, geom_format: str = "qgis") -> str:
        """
        Returns the GeoLayer's geometry in desired format.

        Args:
            geom_format: the desired geometry format. QGIS format by default.

        Returns:
            The GeoLayer's geometry in desired format (returns text version, not enumerator version).

        Raises:
            Value Error if the geom_foramt is not a valid format.
        """
        raise RuntimeError("get_geometry() function should be implemented in derived class.")

    def get_property(self, property_name: str, if_not_found_val: object = None,
                     if_not_found_except: bool = False) -> object:
        """
        Get a GeoLayer property, case-specific.

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
                # Let the exception from not finding a key in the dictionary be raised
                # print('Property not found so throwing exception')
                raise
            else:
                return if_not_found_val

    def is_raster(self) -> bool:
        """
        Indicate whether a raster layer.

        Returns:
            True if a raster layer, False if a vector layer.
        """
        raise RuntimeError("is_raster() function should be implemented in derived class.")

    def is_vector(self) -> bool:
        """
        Indicate whether a vector layer.

        Returns:
            True if a vector layer, False if a raster layer.
        """
        raise RuntimeError("is_vector() function should be implemented in derived class.")

    def set_property(self, property_name: str, property_value: object) -> None:
        """
        Set a GeoLayer property

        Args:
            property_name (str):  Property name.
            property_value (object):  Value of property, can be any built-in Python type or class instance.
        """
        self.properties[property_name] = property_value

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
            # - sourcePath maps to the output file because what is written serves as the path
            # - if the layer was written, then the output source path will e set and can be used;
            #   otherwise, use the input source path
            source_path = None
            if self.output_path is not None and self.output_path != GeoLayer.SOURCE_MEMORY:
                source_path = self.output_path
            elif self.input_path is not None and self.input_path != GeoLayer.SOURCE_MEMORY:
                source_path = self.input_path
            # Determine the layer type, to inform the application how to handle, especially for web services
            # - can't use isinstance() because this will result in a circular import dependency,
            #   therefore check the class name
            layerType = None
            layer_class = self.__class__.__name__
            if layer_class == 'VectorGeoLayer':
                layer_type = 'Vector'
            elif layer_class == 'RasterGeoLayer':
                layer_type = 'Raster'
            return {
                "geoLayerId": self.id,
                "name": self.name,
                "description": self.description,
                "crs": self.get_crs_code(),
                "geometryType": ("WKT:" + self.get_geometry()),
                "layerType": layer_type,
                "sourcePath": source_path,
                "properties": self.properties,
                "history:": self.history
            }
