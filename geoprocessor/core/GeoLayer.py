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

    def __init__(self, geolayer_id: str,
                 geolayer_qgs_layer: QgsMapLayer = None,
                 geolayer_source_path: str = None, properties: dict = None) -> None:
        """
        Initialize a new GeoLayer instance.

        Args:
            geolayer_id (str):
                String that is the GeoLayer's reference ID. This ID is used to access the GeoLayer from the
                GeoProcessor for manipulation.
            geolayer_qgs_layer (QgsVectorLayer or QgsRasterLayer instance via those class __init__() function):
                Object created by the QGIS processor. All GeoLayer spatial manipulations are
                performed on the GeoLayer's qgs_vector_layer.
            geolayer_source_path (str):
                The full pathname to the original spatial data file on the user's local computer. If the geolayer was
                made in memory from the GeoProcessor, this value is set to `MEMORY`.
            properties ({}):
                A dictionary of user (non-built-in) properties that can be assigned to the layer.
                These properties facilitate processing.
        """

        # "id" is a string that is the GeoLayer's reference ID. This ID is used to access the GeoLayer from the
        # GeoProcessor for manipulation.
        self.id = geolayer_id

        # "qgs_layer" is a QgsVectorLayer or QgsRasterLayer object created by the QGIS processor.
        # All spatial manipulations are performed on the GeoLayer's qgs_layer.
        self.qgs_layer = geolayer_qgs_layer

        # "source_path" (str) is the full pathname to the original spatial data file on the user's local computer
        self.source_path = geolayer_source_path

        # "qgs_id" (str) is the GeoLayer's id in the Qgs environment (this is automatically assigned by the QGIS
        # GeoProcessor when a GeoLayer is originally created)
        self.qgs_id = geolayer_qgs_layer.id()

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

    def deepcopy(self, copied_geolayer_id: str) -> GeoLayer:
        """
        Create a copy of the GeoLayer.

        Args:
            copied_geolayer_id(str): The ID of the output copied GeoLayer.

        Returns:
            The copied GeoLayer object.
        """
        raise RuntimeError("deepcopy() function should be implemented in derived class.")

    def get_crs(self) -> str:
        """
        Returns the coordinate reference system (str, EPSG code) of a GeoLayer.
        """

        # "crs" (str) is the GeoLayer's coordinate reference system in
        # <EPSG format 'http://spatialreference.org/ref/epsg/'>_. Return the crs variable.
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
