# qgis_util - utility functions related to QGIS and requires imports from QGIS libraries
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

from datetime import datetime

import logging
import os

from qgis.core import QgsApplication, QgsCoordinateReferenceSystem, QgsExpression, QgsFeature, QgsField
from qgis.core import QgsGeometry, QgsMapLayer, QgsRasterLayer, QgsRectangle, QgsVectorFileWriter, QgsVectorLayer
from qgis.core import QgsExpressionContext, QgsExpressionContextScope
from qgis import processing
from PyQt5 import QtWidgets

from qgis.analysis import QgsNativeAlgorithms

import qgis.utils
import sys
from typing import Any

from plugins.processing.core import Processing

import geoprocessor.util.app_util as app_util
import geoprocessor.util.os_util as os_util
import geoprocessor.util.string_util as string_util

from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5 import QtCore

"""
This module contains functions that perform spatial data processing using QGIS library functions.
The code in this file should NOT have knowledge about the GeoProcessor, to allow updates to QGIS and also to
allow implementing a similar ArcGIS Pro version of these functions.
"""

# TODO smalers 2018-01-28 Evaluate whether to make this private via Pythonic underscore naming
# QGIS application environment instance
# "qgs" is used to match QGIS conventions (rather than "qgis")
qgs = None

# Developer QGIS version - the version of QGIS used by the developer to create the GeoProcessor. This must be
# manually updated as the GeoProcessor is developed with newer versions of QGIS. If updated accurately, GitHub will
# memorialize the developer QGIS version used at any time within the history of the GeoProcessor. Must be a string.
# Must be in the following format: "[major release].[minor release].[bug fix release]". Do not pad numbers.
dev_qgis_version = "3.4.3"

# The QgsApplication instance opened with initialize_qgis(), used to simplify application management
qgs_app = None


def add_feature_to_qgsvectorlayer(qgsvectorlayer: QgsVectorLayer, qgsgeometry: QgsGeometry) -> None:
    """
    Add a feature to the input QgsVectorLayer.
    * Adds the geometry of the feature with the QgsGeometry object.
    * Can add feature ID (not yet built into this function).
    * Can add attributes (not yet built into this function).

    Args:
        qgsvectorlayer (QgsVectorLayer): the QgsVectorLayer object that the feature will be added to
        qgsgeometry (QgsGeometry): the QgsGeometry of the feature to be added

    Returns:
        None
    """

    # Get the data provider of the QgsVectorLayer object.
    provider = qgsvectorlayer.dataProvider()

    # Instantiate a new QgsFeature object.
    new_feature = QgsFeature()

    # Set the geometry of the new QgsFeature object with the QgsGeometry object.
    new_feature.setGeometry(qgsgeometry)

    # Add the new feature to the QgsVectorLayer. Update the extent of the QgsVectorLayer.
    provider.addFeatures([new_feature])
    qgsvectorlayer.updateExtents()


def add_qgsvectorlayer_attribute(qgsvectorlayer: QgsVectorLayer, attribute_name: str, attribute_type: str) -> None:
    """
    Add an attribute to a QgsVectorLayer object.
    If the attribute does not exist, it is added.
    If it exists, an exception is thrown.

    Args:
        qgsvectorlayer (QgsVectorLayer): a QgsVectorLayer object to be updated
        attribute_name (str): the name of the attribute to set
        attribute_type (str): the attribute field type: int (integer), double (real number), string (text) or date.

    Return:
        None.

    Raises:
        ValueError:  If the input is an invalid attribute type or the attribute already exists.
    """
    logger = logging.getLogger(__name__)

    # Start the data provider (QgsVectorDataProvider) for the input QgsVectorLayer.
    qgsvectorlayer_data = qgsvectorlayer.dataProvider()

    # Check that the attribute name is not already a name in the QgsVectorLayer.
    if attribute_name not in [attribute.name() for attribute in qgsvectorlayer_data.fields()]:

        # Add the attribute field to the GeoLater
        added = False
        if attribute_type.upper() == "INT":
            status = qgsvectorlayer_data.addAttributes([QgsField(attribute_name, QVariant.Int)])
        elif attribute_type.upper() == "DOUBLE":
            status = qgsvectorlayer_data.addAttributes([QgsField(attribute_name, QVariant.Double)])
        elif attribute_type.upper() == "STRING":
            status = qgsvectorlayer_data.addAttributes([QgsField(attribute_name, QVariant.String)])
        elif attribute_type.upper() == "DATE":
            status = qgsvectorlayer_data.addAttributes([QgsField(attribute_name, QVariant.Date)])
        else:
            valid_attribute_types = ["int", "double", "string", "date"]
            message = "The attribute_type ({}) is not a valid attribute type. Valid attribute types are: {}".format(
                attribute_type, valid_attribute_types)
            logger.warning(message)
            raise ValueError(message)

        if status:
            # Success.
            # If here can update the layer fields
            qgsvectorlayer.updateFields()
            logger.info("Added attribute '{}' of type '{}'".format(attribute_name, attribute_type))
        else:
            # Error.
            message = "Error adding attribute ({})".format(attribute_name)
            logger.warning(message)
            # TODO smalers 2020-11-16 need a more appropriate exception type.
            raise ValueError(message)

    else:
        # Print a warning message if the input attribute name is already an existing attribute name.
        logger = logging.getLogger(__name__)
        message = "The attribute_name ({}) is an existing attribute name.".format(attribute_name)
        logger.warning(message)
        raise ValueError(message)


def create_qgsgeometry(geometry_format: str, geometry_input_as_string: str) -> QgsGeometry or None:
    """
    Create a QGSGeometry object from input data. Can create an object from data in well-known text (WKT) and
    well-known binary (WKB). REF: https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/geometry.html

    Args:
        geometry_format (str): the type of geometry that the data is in. Can be either of the following:
            WKT: well-known text
            WKB: well-known binary
        geometry_input_as_string (str): the geometry data to convert to QGSGeometry object.
            Data must match the correct syntax for the geometry format value.

    Returns:
        - QgsGeometry object if geometry_format is valid,
        - None if the geometry is invalid.
    """
    debug = False
    if debug:
        logger = logging.getLogger(__name__)
    if geometry_format.upper() == "WKT":
        # Well-known text
        if debug:
            logger.debug("Creating geometry from WKT:  {}".format(geometry_input_as_string))
        geometry = QgsGeometry.fromWkt(geometry_input_as_string)
        return geometry

    elif geometry_format.upper() == "WKB":
        # Well-known binary

        # Convert the WKB string into a a binary input. Return the corresponding QgsGeometry object.
        # This feature is only available for Python 3. See reference below:
        # https://stackoverflow.com/questions/5901706/the-bytes-type-in-python-2-7-and-pep-358
        if debug:
            logger.debug("Creating geometry from WKB:  {}".format(geometry_input_as_string))
        wkb = bytes.fromhex(geometry_input_as_string)
        if debug:
            if wkb is None:
                logger.debug("WKB bytes is None.")
        geometry = QgsGeometry().fromWkb(wkb)
        if debug:
            if geometry is None:
                logger.debug("Geometry from WKB is None.")
        return geometry

    else:
        # Unknown geometry format, return None.
        return None


def create_qgsrasterlayer(geometry: str, crs_code: str, layer_name: str) -> QgsVectorLayer:
    """
    Creates a new QgsRasterLayer from scratch (in memory QgsRasterLayer object).

    Args:
        geometry (str): the geometry type of the new QgsVectorLayer. Can be `Point`, `Polygon` or `LineString`
        crs_code (str): a coordinate reference system code (EpsgCrsId, WKT or Proj4 codes).
        layer_name (str): the name of the new QgsVectorLayer (this is not the GeoLayer ID)

    Raises:
        ValueError if the input to create the layer is invalid.

    Return:
        - QgsVectorLayer object if the new QgsVectorLayer object is valid
        - None if input is not valid
    """

    # Create the QgsRasterLayer object with the geometry, the CRS and the layer name information.
    # See, for example:  https://qgis.org/pyqgis/3.10/core/QgsRasterLayer.html#qgis.core.QgsRasterLayer
    # uri = "point?crs=epsg:4326&field=id:integer"
    # layer_name
    uri = "{}?crs={}".format(geometry, crs_code)
    options = "memory"
    # #layer = QgsRasterLayer(uri, layer_name, "memory")
    # layer = QgsRasterLayer(path_to_file, layer_name)

    # If the QgsRasterLayer object is valid, return it.
    if layer.isValid():
        return layer
    else:
        message = 'Error creating raster layer "' + str(layer_name) + '"'
        logger = logging.getLogger(__name__)
        logger.warning(message)
        raise ValueError(message)


def create_qgsvectorlayer(geometry: str, crs_code: str, layer_name: str) -> QgsVectorLayer:
    """
    Creates a new QgsVectorLayer from scratch (in memory QgsVectorLayer object).

    Args:
        geometry (str): the geometry type of the new QgsVectorLayer. Can be `Point`, `Polygon` or `LineString`
        crs_code (str): a coordinate reference system code (EpsgCrsId, WKT or Proj4 codes).
        layer_name (str): the name of the new QgsVectorLayer (this is not the GeoLayer ID)

    Raises:
        ValueError if the input to create the layer is invalid.

    Return:
        - QgsVectorLayer object if the new QgsVectorLayer object is valid
        - None if input is not valid
    """

    # Create the QgsVectorLayer object with the geometry, the CRS and the layer name information.
    # See, for example:  https://qgis.org/pyqgis/3.10/core/QgsVectorLayer.html#qgis.core.QgsVectorLayer
    # uri = "point?crs=epsg:4326&field=id:integer"
    # layer_name
    uri = "{}?crs={}".format(geometry, crs_code)
    options = "memory"
    layer = QgsVectorLayer(uri, layer_name, options)

    # If the QgsVectorLayer object is valid, return it.
    if layer.isValid():
        return layer
    else:
        message = 'Error creating layer "' + str(layer_name) + '"'
        logger = logging.getLogger(__name__)
        logger.warning(message)
        raise ValueError(message)


def deepcopy_qqsvectorlayer(qgsvectorlayer: QgsVectorLayer) -> QgsVectorLayer:
    """
    Creates a deep copy (separate instance) of a QgsVectorLayer object. Spatial features, attributes, and the
    coordinate reference system from the input QgsVectorLayer object will be retained in the output copied
    QgsVectorLayer object.

    Args:
        qgsvectorlayer (QgsVectorLayer): the QgsVectorLayer object to deep copy.

    Returns:
        The deep copied QgsVectorLater object.
    """

    # REF: https://gis.stackexchange.com/questions/205947/duplicating-layer-in-memory-using-pyqgis
    # acceptable geometry values: Point, LineString, Polygon, MultiLineString, MultiPolygon

    # Get the features of the input QgsVectorLayer.
    feats = [feat for feat in qgsvectorlayer.getFeatures()]

    # Get the geometry of the input QgsVectorLayer (qgis format).
    qgis_geometry = get_geometrytype_qgis(qgsvectorlayer)

    # Get the coordinate reference system of teh input QgsVectorLayer (string epsg code).
    crs = qgsvectorlayer.crs().authid()

    # Get the now_id: a string of numbers representing the current date and time. This is used to uniquely define the
    # layer name of the copied QgsVectorLayer (otherwise errors could occur).
    now = datetime.now()
    now_id = "{}{}{}{}{}{}{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond)

    # Create a new in-memory QgsVectorLayer with same feature geometry type and CRS as the input QgsVectorLayer.
    copied_qgsvectorlayer = QgsVectorLayer("{}?crs={}".format(qgis_geometry, crs), "layer_{}".format(now_id), "memory")

    # Start the data provider for the in-memory copied QgsVectorLayer.
    copied_qgsvectorlayer_data = copied_qgsvectorlayer.dataProvider()

    # Get a list of the input QgsVectorLayer's attributes.
    attr = qgsvectorlayer.dataProvider().fields().toList()

    # Add the attributes of the input QgsVectorLayer to the copied QgsVectorLayer.
    copied_qgsvectorlayer_data.addAttributes(attr)
    copied_qgsvectorlayer.updateFields()

    # Add the features of the input QgsVectorLayer to the copied QgsVectorLayer.
    copied_qgsvectorlayer_data.addFeatures(feats)

    # Return the deep copied QgsVectorLayer.
    return copied_qgsvectorlayer


def exit_qgis() -> None:
    """
    Exit QGIS environment.
    This is expected to be called once when an application exits.

    Returns:
        None.
    """
    if qgs is not None:
        qgs.exit()


def get_extent_from_geolayers(selected_geolayers: [QgsMapLayer], buffer_fraction: float = None) -> QgsRectangle:
    """
    Return the maximum extent for a list of geolayers.
    If a single point, add +1.0 in each coordinate direction.

    Args:
        selected_geolayers ([QgsMapLayer]): list of map layers to display
        buffer_fraction (float): buffer distance as a fraction (0 to 1.0) to add to the extent on each edge,
            to ensure that symbols are not truncated

    Returns:
        QgsRectangle for the extent

    """
    xmin = float("inf")
    xmax = -float("inf")
    ymin = float("inf")
    ymax = -float("inf")
    for layer in selected_geolayers:
        if layer is None:
            logger = logging.getLogger(__name__)
            logger.warning("Layer is None")
        extent = layer.extent()
        if extent.xMinimum() < xmin:
            xmin = extent.xMinimum()
        if extent.xMaximum() > xmax:
            xmax = extent.xMaximum()
        if extent.yMinimum() < ymin:
            ymin = extent.yMinimum()
        if extent.yMaximum() > ymax:
            ymax = extent.yMaximum()

    # Check if extent is a single point
    if xmin == xmax:
        xmin -= 1.0
        xmax += 1.0
    else:
        # Add buffer
        if buffer_fraction is not None:
            buffer_dist = abs(xmax - xmin)*buffer_fraction
            xmin -= buffer_dist
            xmax += buffer_dist

    if ymin == ymax:
        ymin -= 1.0
        ymax += 1.0
    else:
        # Add buffer
        if buffer_fraction is not None:
            buffer_dist = abs(ymax - ymin)*buffer_fraction
            ymin -= buffer_dist
            ymax += buffer_dist

    return qgis.core.QgsRectangle(xmin, ymin, xmax, ymax)


def get_features_matching_expression(qgsvectorlayer: QgsVectorLayer, qgs_expression: QgsExpression) -> [QgsFeature]:
    """
    Returns the QgsFeature objects of the features that match the input QgsExpression.

    Args:
        qgsvectorlayer (QgsVectorLayer): the QgsVectorLayer object to evaluate.
        qgs_expression (QgsExpression): the QgsExpression object to filter the QgsVectorLayer's features.

    Returns:
        - A list of QgsFeature objects of features that match the input qgs_expression.
        - Empty list if no features match the input expression.
    """

    # A list to hold the QgsFeature objects that match the QgsExpression.
    matching_features = []

    # These variables are used to increase the speed that the evaluation takes to run when evaluating multiple features
    # of a QgsVectorLayer.
    # REF: https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/expressions.html
    # REF: https://gis.stackexchange.com/questions/244068/pyqgis-gives-typeerror-qgsexpression-prepare-argument-1-
    #      has-unexpected-type/244088#244088
    context = QgsExpressionContext()
    scope = QgsExpressionContextScope()

    # Iterate over the features of the QgsVectorLayer
    for feature in qgsvectorlayer.getFeatures():

        # Set the scope to the current feature.
        scope.setFeature(feature)
        context.appendScope(scope)

        # If the evaluation of the feature is TRUE, append the feature to the matching_features list.
        if qgs_expression.evaluate(context) == 1:
            matching_features.append(feature)

    # Return the list of QgsFeatures that match the input QgsExpression.
    return matching_features


def get_features_not_matching_expression(qgsvectorlayer: QgsVectorLayer, qgs_expression: QgsExpression) -> [QgsFeature]:
    """
    Returns the QgsFeature objects of the features that do not match the input QgsExpression.

    Args:
        qgsvectorlayer (QgsVectorLayer): the QgsVectorLayer object to evaluate.
        qgs_expression (QgsExpression): the QgsExpression object to filter the QgsVectorLayer's features.

    Returns:
        A list of QgsFeature objects of features that do not match the input qgs_expression.
        Return an empty list if all features match the input expression.
    """

    # A list to hold the QgsFeature objects that do not match the QgsExpression.
    non_matching_features = []

    # These variables are used to increase the speed that the evaluation takes to run when evaluating multiple features
    # of a QgsVectorLayer.
    # REF: https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/expressions.html
    # REF: https://gis.stackexchange.com/questions/244068/pyqgis-gives-typeerror-qgsexpression-prepare-argument-1-
    #      has-unexpected-type/244088#244088
    context = QgsExpressionContext()
    scope = QgsExpressionContextScope()

    # Iterate over the features of the QgsVectorLayer
    for feature in qgsvectorlayer.getFeatures():

        # Set the scope to the current feature.
        scope.setFeature(feature)
        context.appendScope(scope)

        # If the evaluation of the feature is FALSE, append the feature to the non_matching_features list.
        if qgs_expression.evaluate(context) == 0:
            non_matching_features.append(feature)

    # Return the list of QgsFeatures that do not match the input QgsExpression.
    return non_matching_features


def get_geometrytype_qgis(qgsvectorlayer: QgsVectorLayer) -> str:
    """
    Returns the input QgsVectorLayer's geometry in QGIS format (returns text, not enumerator).
    REF: https://qgis.org/api/1.8/classQGis.html

    Args:
        qgsvectorlayer (QgsVectorLayer): a QgsVectorLayer object

    Returns:
        Appropriate geometry in QGIS format (returns text, not enumerator).
    """
    debug = False  # Use to troubleshoot
    if debug:
        logger = logging.getLogger(__name__)

    # The QGIS geometry type enumerator dictionary.
    enumerator_dic = {0: "Point",
                      1: "LineString",
                      2: "Polygon",
                      3: "Unknown",
                      4: "NoGeometry"}

    # Return the QGIS geometry type (in text form) of the input QgsVectorLayer.
    if qgsvectorlayer is None:
        if debug:
            logger.info("QgsLayer is None.  Can't determine geometry type.  Returning Unknown")
        return 'Unknown'
    else:
        try:
            geometry_type = enumerator_dic[qgsvectorlayer.geometryType()]
            if debug:
                logger.info("QgsLayer geometry type {} is {}".format(qgsvectorlayer.geometryType(), geometry_type))
            return geometry_type
        except KeyError:
            if debug:
                logger.info("QgsLayer geometry type is not recognized.  Returning Unknown.")
            return 'Unknown'


def get_geometrytype_qgis_from_wkt(wkt_string: str) -> str:
    """
    Returns the QGIS geometry equivalent of the WKT geometry provided by a Well Known Text string.

    Args:
        wkt_string (str): a Well-Known Text string
        See https://en.wikipedia.org/wiki/Well-known_text

    Returns:
        - the QGIS geometry equivalent if the WKT geometry is recognized.
        - None if input is not recognized
    """

    # A dictionary of QGIS geometry types and their corresponding WKT geometry types.
    # Key: the QGIS geometry types
    # Value: a list of corresponding WKT geometry types (all uppercase)
    qgis_wkt_geom_conversion_dic = {"Point": ["POINT", "MULTIPOINT"],
                                    "Polygon": ["POLYGON", "MULTIPOLYGON"],
                                    "LineString": ["LINESTRING", "MULTILINESTRING"]}

    # Get the WKT geometry type from a Well-Known Text string. Capitalize the characters of the geometry type.
    wkt_geometry_type = (wkt_string.split('(')[0]).strip().upper()

    # Iterate over the entries in the QGIS/WKT geometry type conversion dictionary (QGIS_WKT_geom_conversion_dic).
    for qgis_geometry_type, wkt_geometry_types in qgis_wkt_geom_conversion_dic.items():

        # If the WKT geometry of the input WKT string is recognized, return the equivalent QGIS geometry.
        if wkt_geometry_type in wkt_geometry_types:
            return qgis_geometry_type


def get_geometrytype_wkb(qgsvectorlayer: QgsVectorLayer) -> str:
    """
    Returns the input QgsVectorLayer's geometry in WKB format (returns text, not enumerator).
    REF: https://qgis.org/api/1.8/classQGis.html
    TODO smalers 2020-08-17 Not even sure if it makes sense to use this since text version is easier to work with.

    Args:
        qgsvectorlayer (QgsVectorLayer): a QgsVectorLayer object

    Returns:
        Appropriate geometry in WKB format (returns text, not enumerator).
    """

    # The WKB geometry type enumerator dictionary.
    # See:  https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry
    enumerator_dic = {0: "Unknown",
                      1: "Point",
                      1001: "Point",
                      2001: "Point",
                      3001: "Point",
                      2: "LineString",
                      1002: "LineString",
                      2002: "LineString",
                      3002: "LineString",
                      3: "Polygon",
                      1003: "Polygon",
                      2003: "Polygon",
                      3003: "Polygon",
                      4: "MultiPoint",
                      1004: "MultiPoint",
                      2004: "MultiPoint",
                      3004: "MultiPoint",
                      5: "MultiLineString",
                      1005: "MultiLineString",
                      2005: "MultiLineString",
                      3005: "MultiLineString",
                      6: "MultiPolygon",
                      1006: "MultiPolygon",
                      2006: "MultiPolygon",
                      3006: "MultiPolygon",
                      7: "GeometryCollection",
                      1007: "GeometryCollection",
                      2007: "GeometryCollection",
                      3007: "GeometryCollection",
                      # The following indicate whether Z, and M are used
                      100: "NoGeometry",
                      0x80000001: "Point",
                      0x80000002: "LineString",
                      0x80000003: "Polygon",
                      0x80000004: "MultiPoint",
                      0x80000005: "MultiLineString",
                      0x80000006: "MultiPolygon",
                      -2147483643: "Unknown"}

    # Return the WKB geometry type (in text form) of the input QgsVectorLayer.
    if qgsvectorlayer is None:
        return "Unknown"
    else:
        try:
            return enumerator_dic[qgsvectorlayer.wkbType()]
        except KeyError:
            return "Unknown"


# TODO smalers 2020-08-24 Evaluate returning a tuple with "2D", "Z", "M", or "ZM"
def get_geometrytype_wkt(qgsvectorlayer: QgsVectorLayer) -> str:
    """
    Returns the input QgsVectorLayer's geometry in WKT format (returns text, not enumerator):
    "Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", "MultiPoint",
    based on the QGSVectorLayer wkbType().

    Currently this returns the same as get_geometrytype_wkb().

    Args:
        qgsvectorlayer (QgsVectorLayer): a QgsVectorLayer object

    Returns:
        Appropriate geometry in WKT format (returns text, not enumerator).
    """

    # The WKB geometry type enumerator dictionary.
    # - See:  https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry

    # Return the WKT geometry type (in text form) of the input QgsVectorLayer.
    if qgsvectorlayer is None:
        return "Unknown"
    else:
        try:
            # logger = logging.getLogger(__name__)
            # logger.info("Trying to get WKT geometry for type: {}".format(qgsvectorlayer.wkbType()))
            return get_geometrytype_qgis(qgsvectorlayer)
        except KeyError:
            return "Unknown"


def get_qgis_version_developer(int_version: bool = True) -> str:
    """
    Returns the version of the QGIS software used to develop the GeoProcessor.
    Can return the int version (ex: 21809) or the string version (ex:2.18.09).

    Args:
        int_version (boolean): If TRUE, the developer QGIS version will be returned as an integer.
            If FALSE, the developer QGIS version will be returned as a string.

    Returns:
        The developer QGIS version.
    """

    # Convert the string version of the developer QGIS version into an int. The minor release version and the bug fix
    # release version must be padded to two digits.
    major, minor, bug_fix = dev_qgis_version.split('.')

    # Pad the minor release if not already two digits.
    if len(minor) == 1:
        minor = "0" + minor

    # Pad the bug release if not already two digits.
    if len(bug_fix) == 1:
        bug_fix = "0" + bug_fix

    # If configured, return the integer version (5 digit integer).
    if int_version:
        return "{}{}{}".format(major, minor, bug_fix)
    else:
        return "{}.{}.{}".format(major, minor, bug_fix)


def get_qgis_version_int() -> int:
    """
    Returns the version (int) of the initiated QGIS software.

    Example:
        21809

    Returns:
        The QGIS version (int).
    """

    # TODO smalers 2018-05-28 the following was version 2
    # return qgis.utils.QGis.QGIS_VERSION_INT
    return qgis.utils.Qgis.QGIS_VERSION_INT


def get_qgis_version_name() -> str:
    """
    Returns the version name of the initiated QGIS software.

    Example:
        Las Palmas

    Returns:
        The QGIS version name (string).
    """

    # TODO smalers 2018-05-28 the following was version 2
    # return qgis.utils.QGis.QGIS_RELEASE_NAME
    return qgis.utils.Qgis.QGIS_RELEASE_NAME


def get_qgis_version_str() -> str:
    """
    Returns the version (string) of the initiated QGIS software.

    Example:
        "2.18.9"

    Returns:
        The QGIS version (string).
    """

    # TODO smalers 2018-05-28 the following was version 2
    # return qgis.utils.QGis.QGIS_VERSION
    return qgis.utils.Qgis.QGIS_VERSION


def get_qgscoordinatereferencesystem_obj(crs_code: str) -> QgsCoordinateReferenceSystem or None:
    """
    Checks if the crs_code create a valid and usable QgsCoordinateReferenceSystem object. If so, return
    the QgsCoordinateReferenceSystem object. If not, return None.
    See: https://qgis.org/pyqgis/master/core/QgsCoordinateReferenceSystem.html

    Args:
        crs_code (str): a coordinate reference system code (EpsgCrsId, WKT or Proj4 codes).

    Returns:
        The QgsCoordinateReferenceSystem object. If not valid, returns None.
    """

    # logger = logging.getLogger(__name__)
    # logger.debug("Getting CRS for '" + crs_code + "'")
    if QgsCoordinateReferenceSystem(crs_code).isValid():
        # Check if the crs_code is valid. If so, return the QgsCoordinateReferenceSystem object.
        # logger.debug("CRS is valid.")
        return QgsCoordinateReferenceSystem(crs_code)
    else:
        # Not valid, return None.
        # logger.debug("CRS is not valid.")
        return None


def get_qgsexpression_obj(expression_as_string: str) -> QgsExpression or None:
    """
    Checks if the expression_as_string creates a valid and usable QgsExpression object. If so, return
    the QgsExpression object. If not, return None.
    REF: https://qgis.org/api/2.18/classQgsExpression.html#a16dd130caadca19158673b8a8c1ea251

    Args:
        expression_as_string (str): a string representing a QgsExpression
        See https://docs.qgis.org/2.8/en/docs/user_manual/working_with_vector/expression.html

    Returns:
        - QgsExpression object, if valid.
        - None if not valid.
  """

    # Check if the expression_as_string is valid. If so, return the QgsExpression object.
    if QgsExpression(expression_as_string).isValid():
        return QgsExpression(expression_as_string)

    # If not, return None.
    else:
        return None


def initialize_qgis(qt_stylesheet_file: str = None) -> QgsApplication:
    """
    Initialize the QGIS environment.  This typically needs to be done only once when the application starts.
    This is expected to be called once when an application starts, before any geoprocessing tasks.

    qt_stylesheet_file:
        Path to Qt stylesheet.  If not specified, it will be the software installation folder:
        geoprocess/resources/qt-stylesheets/gp.qss

    Returns:
        None
    """
    logger = logging.getLogger(__name__)
    # Open QGIS environment
    # REF: https://github.com/OSGeo/homebrew-osgeo4mac/issues/197
    global qgs_app
    # A warning like similar to the following may be shown unless the following line of code is added.
    # - See https://bugreports.qt.io/browse/QTBUG-51379
    # -------
    # Qt WebEngine seems to be initialized from a plugin. Please set Qt::AA_ShareOpenGLContexts using
    #   QCoreApplication::setAttribute before constructing QGuiApplication
    # -------
    # noinspection PyBroadException
    try:
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    except Exception:
        # This happens when the current development Python packages are different than runtime
        print("Error calling QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)")
        print("- possibly due to Python API version issue")
        print("- ignoring exception and starting the application")
    qgs_app = QgsApplication([], False)

    # First set the application appropriately
    qt_style = qgs_app.style().metaObject().className()
    logger.info('Available Qt styles are: ' + str(QtWidgets.QStyleFactory.keys()))
    logger.info("Qt is using style " + str(qt_style))
    if os_util.is_windows_os():
        if qt_style.upper().index('VISTA') > 0:
            # 'windowsvista' (QWindowsVistaStyle) style is kind of ugly
            # - reset to QWindowsStyle, need to use 'Windows'
            logger.info("Resetting style to 'Windows'")
            qgs_app.setStyle("Windows")
            qt_style = qgs_app.style().metaObject().className()
            logger.info("After setting style to 'Windows', Qt is using style " + str(qt_style))

    # Next set the Qt style sheet to modify default styles
    # 'ProgramHome' is location of app, which is geoprocessor/app
    # - therefore need to go up one level to find the resources
    if qt_stylesheet_file is not None:
        path_to_style_sheet = qt_stylesheet_file
    else:
        path_to_style_sheet = os.path.join(app_util.get_property('ProgramHome'),
                                           "../resources/qt-stylesheets/gp.qss").replace("\\","/")
    if path_to_style_sheet is None:
        logger.info("Qt stylesheet file is None - not using.")
    elif not os.path.exists(path_to_style_sheet):
        logger.info("Qt stylesheet file does not exist: " + path_to_style_sheet)
    else:
        # Style sheet is loaded from a string, not filename, so first read the file into a string.
        logger.info("Setting Qt stylesheet file: " + path_to_style_sheet)
        f = open(path_to_style_sheet,"r")
        qss_string = f.read()
        # print("Qt stylesheet contents: " + qss_string)
        f.close()
        qgs_app.setStyleSheet(qss_string)

    # Initialize the QGIS environment
    qgs_app.initQgis()
    return qgs_app


def initialize_qgis_processing() -> processing:
    """
    Initialize the QGIS processing environment (to call and run QGIS algorithms).

    Returns:
        The initialized qgis processing object.
    """

    pr = processing.processing
    return pr


# TODO smalers 2020-07-20 why did Emma/Justing use this instead of lowercase processing?
def initialize_qgis_processor() -> Processing:
    """
    Initialize the QGIS processor environment (to call and run QGIS algorithms).

    Returns:
        The initialized qgis processor object.
    """

    pr = Processing.Processing()
    pr.initialize()

    # Allows the GeoProcessor to use the native algorithms
    # REF: https://gis.stackexchange.com/questions/279874/
    #   using-qgis3-processing-algorithms-from-standalone-pyqgis-scripts-outside-of-gui/279937
    QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

    return pr


def read_qgsrasterlayer_from_file(spatial_data_file_abs: str) -> QgsRasterLayer:
    """
    Reads the full pathname of spatial data file and returns a QGSRasterLayer object.

    Args:
        spatial_data_file_abs (str): the full pathname to a spatial data file

    Raises:
        IOError if the file is invalid.

    Returns:
        A QGSRasterLayer object containing the data from the input spatial data file.
    """

    # Get the filename and basename of the input raster file.
    file_info = QFileInfo(spatial_data_file_abs)
    path = file_info.filePath()
    base_name = file_info.baseName()

    # Create the QgsRasterLayer object.
    qgs_raster_layer_obj = QgsRasterLayer(path, base_name)

    # Return the QgsRasterLayer if it is valid.
    if qgs_raster_layer_obj.isValid():
        return qgs_raster_layer_obj

    # If the created QGSRasterLayer object is invalid, print a warning message and return None.
    else:
        message = 'The QGSRasterLayer for file "{}" is invalid.'.format(spatial_data_file_abs)
        logger = logging.getLogger(__name__)
        logger.warning(message)
        raise IOError(message)


def read_qgsvectorlayer_from_delimited_file_wkt(delimited_file_abs: str,
                                                delimiter: str,
                                                crs_code: str,
                                                wkt_col_name: str) -> QgsVectorLayer:
    """
    Reads a delimited file (with WKT column) and returns a QGSVectorLayerObject.

    Args:
        delimited_file_abs (str): the full pathname to a delimited file
        delimiter (str): the delimiter symbol (often times is a comma)
        crs_code (str): the coordinate reference system (in EPSG code)
        wkt_col_name (str): the name of the field/column containing the WKT geometry data

    Raises:
        IOError if the file is invalid.

    Returns:
        - A QGSVectorLayer object containing the data from the input delimited file.
    """

    # Instantiate the QGSVectorLayer object. Must include the following:
    #   (1) full path to the delimited file
    #   (2) the delimiter symbol
    #   (3) the coordinate reference system (EPSG code)
    #   (4) the name of the field containing the wkt geometry data
    # REF: https://docs.qgis.org/2.14/en/docs/pyqgis_developer_cookbook/loadlayer.html
    uri = "file:///{}?delimiter={}&crs={}&wktField={}".format(delimited_file_abs, delimiter, crs_code, wkt_col_name)
    qgsvectorlayer = QgsVectorLayer(uri, os.path.basename(delimited_file_abs), "delimitedtext")

    # If the QgsVectorLayer is valid, return it.  Otherwise return None.
    if qgsvectorlayer.isValid():
        return qgsvectorlayer
    else:
        logger = logging.getLogger(__name__)
        message = 'The QGSVectorLayer object for delimited file "{}" is invalid.'.format(delimited_file_abs)
        logger.warning(message)
        raise IOError(message)


def read_qgsvectorlayer_from_delimited_file_xy(delimited_file_abs: str, delimiter: str, crs_code: str,
                                               x_col_name: str, y_col_name: str) -> QgsVectorLayer:
    """
    Reads a delimited file (with X and Y coordinates) and returns a QGSVectorLayerObject.

    Args:
        delimited_file_abs (str): the full pathname to a delimited file
        delimiter (str): the delimiter symbol (often times is a comma)
        crs_code (str): the coordinate reference system (in EPSG code)
        x_col_name (str): the name of the field containing the x coordinates
        y_col_name(str): the name of the filed containing the y coordinates

    Raises:
        IOError if the file is invalid.

    Returns:
        A QGSVectorLayer object containing the data from the input delimited file. If the QgsVectorLayer is not
         valid, return None.
    """

    # Instantiate the QGSVectorLayer object. Must include the following:
    #   (1) full path to the delimited file
    #   (2) the delimiter symbol
    #   (3) the coordinate reference system (EPSG code)
    #   (4) the name of the field containing the x coordinates
    #   (5) the name of the field containing the y coordinates
    # REF: https://docs.qgis.org/2.14/en/docs/pyqgis_developer_cookbook/loadlayer.html
    uri = "file:///{}?delimiter={}&crs={}&xField={}&yField={}".format(delimited_file_abs,
                                                                      delimiter, crs_code, x_col_name, y_col_name)
    qgsvectorlayer = QgsVectorLayer(uri, os.path.basename(delimited_file_abs), "delimitedtext")

    # If the QgsVectorLayer is valid, return it. Otherwise return None.
    if qgsvectorlayer.isValid():
        return qgsvectorlayer
    else:
        logger = logging.getLogger(__name__)
        message = 'The QGSVectorLayer object for file "{}" is invalid.'.format(delimited_file_abs)
        logger.warning(message)
        raise IOError(message)


def read_qgsvectorlayer_from_excel_worksheet(excel_workbook_abs: str, worksheet_index: int = 0) -> QgsVectorLayer:
    """
    Reads an Excel worksheet and returns a QGSVectorLayerObject.

    Args:
        excel_workbook_abs (str): the full pathname to an excel workbook
        worksheet_index (str or int): the index of the worksheet to read. First is 0, second is 1 ...

    Raises:
        IOError if the file is invalid.

    Returns:
        A QGSVectorLayer object containing the data from the input excel worksheet (tables). If the QgsVectorLayer is
         not valid, return None.
    """

    # Instantiate the QGSVectorLayer object. Must include the following:
    #   (1) full path to the delimited file
    #   (2) the index of the worksheet to be read

    uri = r"{}|layerid={}".format(excel_workbook_abs, str(worksheet_index))
    qgsvectorlayer = QgsVectorLayer(uri, os.path.basename(excel_workbook_abs), "ogr")

    # If the QgsVectorLayer is valid, return it. Otherwise return None.
    if qgsvectorlayer.isValid():
        return qgsvectorlayer
    else:
        message = 'The QGSVectorLayer for Excel file "{}" worksheet {} is invalid.'.format(
                  excel_workbook_abs, str(worksheet_index))
        logger = logging.getLogger(__name__)
        logger.warning(message)
        raise IOError(message)


def read_qgsvectorlayer_from_feature_class(file_gdb_path_abs: str,
                                           feature_class: str,
                                           query: str = None) -> QgsVectorLayer:
    """
    Reads a feature class in an Esri file geodatabase and returns a QGSVectorLayerObject.

    Raises:
        IOError if the geodatabase layer is invalid.

    Args:
        file_gdb_path_abs (str): the full pathname to a file geodatabase
        feature_class (str): the name of the feature class to read
        query (str): SQL query string to use for a subset of the full layer (applied after reading the full layer)

    Returns:
        A QGSVectorLayer object containing the data from the input feature class.
    """

    # Instantiate the QGSVectorLayer object.
    # In order for this to work, you must configure ESRI FileGDB Driver in QGIS Installation.
    # Follow instructions from GetSpatial's post in below reference
    # REF: https://gis.stackexchange.com/questions/26285/file-geodatabase-gdb-support-in-qgishttps:
    # //gis.stackexchange.com/questions/26285/file-geodatabase-gdb-support-in-qgis
    # Must follow file geodatabase input annotation. Follow instructions from nanguna's post in
    # below reference
    # REF: https://gis.stackexchange.com/questions/122205/
    # how-to-add-mdb-geodatabase-layer-feature-class-to-qgis-project-using-python
    qgs_vector_layer_obj = QgsVectorLayer(str(file_gdb_path_abs) + "|layername=" + feature_class, feature_class, 'ogr')

    # A QgsVectorLayer object is almost always created even if it is invalid.
    # From
    # `QGIS documentation <https://docs.qgis.org/2.14/en/docs/pyqgis_developer_cookbook/loadlayer.html>`_
    #   "It is important to check whether the layer has been loaded successfully. If it was not, an invalid
    #   layer instance is returned."
    # Check that the newly created QgsVectorLayer object is valid. If so, create a GeoLayer object within
    # the geoprocessor and add the GeoLayer object to the geoprocessor's GeoLayers list.
    if qgs_vector_layer_obj.isValid():
        # Subset the layer
        if query is not None and query != '':
            logger = logging.getLogger(__name__)
            logger.info("Setting subset string to filter layer features: {}".format(query))
            qgs_vector_layer_obj.setSubsetString(query)
        return qgs_vector_layer_obj

    # If the created QGSVectorLayer object is invalid, print a warning message and return None.
    else:
        message = 'The QGSVectorLayer from file geodatabase "{}" feature class "{}" is invalid.'.format(
                   file_gdb_path_abs, feature_class)
        logger = logging.getLogger(__name__)
        logger.warning(message)
        raise IOError(message)


def read_qgsvectorlayer_from_file(spatial_data_file_abs: str, layer_name: str = None) -> QgsVectorLayer:
    """
    General function to read a QGSVectorLayer object using OGR drivers.
    The OGR driver is determined from the filename extension.

    Args:
        spatial_data_file_abs (str): the full pathname to a spatial data file
        layer_name (str):
            layer name to read from the file, needed when the format supports multiple layer names.
            It will be added after the data source using '|layername=...'.

    Raises:
        IOError if the geodatabase layer is invalid.

    Returns:
        A QGSVectorLayer object containing the data from the input spatial data file.
    """

    # Instantiate the QGSVectorLayer object.
    # From `QGIS documentation <https://docs.qgis.org/2.14/en/docs/pyqgis_developer_cookbook/loadlayer.html>`_
    # to create a QGSVectorLayer object, the following parameters must be entered:
    #   data_source (first argument): string full path the the spatial data file
    #   layer_name (second argument): string layer name that will be used in the QGIS layer list widget
    #       -- in this function the layer name is defaulted to the spatial data filename (with extension)
    #   provider_name (third argument): string indicating the data provider (defaulted within this function to 'ogr')
    if layer_name is None or layer_name == "":
        # No layer name specified, just use the file path and extension to tell OGR what to read
        qgs_vector_layer_obj = QgsVectorLayer(spatial_data_file_abs, os.path.basename(spatial_data_file_abs), 'ogr')
    else:
        # Layer name is requested
        data_source = "{}|layername={}".format(spatial_data_file_abs, layer_name)
        qgs_vector_layer_obj = QgsVectorLayer(data_source, os.path.basename(spatial_data_file_abs), 'ogr')

    # A QgsVectorLayer object is almost always created even if it is invalid.
    # From `QGIS documentation <https://docs.qgis.org/2.14/en/docs/pyqgis_developer_cookbook/loadlayer.html>`_
    #   "It is important to check whether the layer has been loaded successfully. If it was not, an invalid
    #   layer instance is returned."
    # Check that the newly created QgsVectorLayer object is valid. If so, create a GeoLayer object within the
    # geoprocessor and add the GeoLayer object to the geoprocessor's GeoLayers list.
    if qgs_vector_layer_obj.isValid():
        return qgs_vector_layer_obj

    # If the created QGSVectorLayer object is invalid, print a warning message and return None.
    else:
        message = 'The QGSVectorLayer for file "{}" is invalid.'.format(spatial_data_file_abs)
        logger = logging.getLogger(__name__)
        logger.warning(message)
        raise IOError(message)


def read_qgsvectorlayer_from_geopackage(geopackage_file_path_abs: str,
                                        layer_name: str,
                                        layer_description: str) -> QgsVectorLayer:
    """
    Read a layer from a GeoPackage file and returns a QGSVectorLayerObject.

    Raises:
        IOError if the GeoPackage layer is invalid.

    Args:
        geopackage_file_path_abs (str): the full path to a GeoPackage file
        layer_name (str): the name of the layer to read (a sub-layer in the main layer)
        layer_description (str): the layer description to assign

    Returns:
        A QGSVectorLayer object containing the layer.
    """

    # Instantiate the QGSVectorLayer object.
    qgs_vector_layer_obj = QgsVectorLayer(str(geopackage_file_path_abs) + "|layername=" + layer_name,
                                          layer_description, 'ogr')

    # A QgsVectorLayer object is almost always created even if it is invalid.
    # From
    # `QGIS documentation <https://docs.qgis.org/2.14/en/docs/pyqgis_developer_cookbook/loadlayer.html>`_
    #   "It is important to check whether the layer has been loaded successfully. If it was not, an invalid
    #   layer instance is returned."
    # Check that the newly created QgsVectorLayer object is valid. If so, create a GeoLayer object within
    # the geoprocessor and add the GeoLayer object to the geoprocessor's GeoLayers list.
    if qgs_vector_layer_obj.isValid():
        return qgs_vector_layer_obj

    else:
        # If the created QGSVectorLayer object is invalid, print a warning message and return None.
        message = 'The QGSVectorLayer from GeoPackage file "{}" layer name "{}" is invalid.'.format(
            geopackage_file_path_abs, layer_name)
        logger = logging.getLogger(__name__)
        logger.warning(message)
        raise IOError(message)


def remove_qgsvectorlayer_attribute(qgsvectorlayer: QgsVectorLayer, attribute_name: str) -> None:
    """
    Deletes an attribute of a QgsVectorLayer object.

    Args:
        qgsvectorlayer (QgsVectorLayer): a QgsVectorLayer object
        attribute_name (str): the name of the attribute to delete

    Returns:
        None
    """

    # Iterate over the attributes in the QgsVectorLayer object.
    for attribute in qgsvectorlayer.fields():

        # If the QgsVectorLayer attribute name matches the parameter attribute_name, continue.
        if attribute.name().upper() == attribute_name.upper():

            # Get the index of the attribute to be deleted.
            index = qgsvectorlayer.fields().lookupField(attribute.name())

            # Delete the attribute.
            qgsvectorlayer.dataProvider().deleteAttributes([index])

            # Update the layer's fields.
            qgsvectorlayer.updateFields()


def remove_qgsvectorlayer_attributes(qgsvectorlayer: QgsVectorLayer,
                                     keep_patterns: [str], remove_patterns: [str]) -> None:
    """
    Deletes attributes of a QgsVectorLayer object depending on the keep and remove patterns.

    Args:
        qgsvectorlayer (QgsVectorLayer): a QgsVectorLayer object
        keep_patterns (list): a list of glob-style patterns of attributes to keep (will not be removed)
        remove_patterns (list): a list of glob-style patterns of attributes to remove

    Return:
        None
    """

    # Get a list of all of the attributes of the Qgs Vector Layer.
    orig_attribute_field_names = [attr_field.name() for attr_field in qgsvectorlayer.fields()]

    # Sort the list to create a second list that only includes the attributes that should be removed.
    attrs_to_remove = string_util.filter_list_of_strings(orig_attribute_field_names, keep_patterns, remove_patterns,
                                                         return_inclusions=False)

    # Iterate over each attribute to be removed and delete it.
    for attr_to_remove in attrs_to_remove:
        remove_qgsvectorlayer_attribute(qgsvectorlayer, attr_to_remove)


def remove_qgsvectorlayer_features(qgsvectorlayer: QgsVectorLayer, list_of_feature_ids: [int]) -> None:
    """
    Removes features from a QgsVectorLayer.

    Args:
        qgsvectorlayer (QgsVectorLayer): a QgsVectorLayer object
        list_of_feature_ids (list of ints): a list of ids of the features to remove

    Returns:
        None
    """

    # Delete the features from the QgsVectorLayer object.
    qgsvectorlayer.dataProvider().deleteFeatures(list_of_feature_ids)


def rename_qgsvectorlayer_attribute(qgsvectorlayer: QgsVectorLayer, attribute_name: str,
                                    new_attribute_name: str) -> None:
    # TODO egiles 2018-01-18 Create a warning if the new_attribute_name is longer than 10 characters but do not raise
    # an exception
    """
    Renames an attribute of a QgsVectorLayer object.

    Args:
        qgsvectorlayer (QgsVectorLayer): a QgsVectorLayer object
        attribute_name (str): the original attribute name to change
        new_attribute_name (str): the new attribute name to rename

    Returns:
        None.
    """

    # Iterate over the attributes in the Qgs Vector Layer object.
    for attribute in qgsvectorlayer.fields():

        # If the Qgs Vector Layer attribute name matches the parameter attribute_name, continue.
        if attribute.name().upper() == attribute_name.upper():

            # Start an editing session within QGIS environment.
            qgsvectorlayer.startEditing()

            # Get the index of the attribute to be renamed.
            index = qgsvectorlayer.fields().lookupField(attribute.name())

            # Rename the attribute with the new name (string).
            qgsvectorlayer.renameAttribute(index, str(new_attribute_name))

            # Commit the changes made to the qgsvectorlayer
            qgsvectorlayer.commitChanges()


def set_qgsvectorlayer_attribute(qgsvectorlayer: QgsVectorLayer, attribute_name: str,
                                 attribute_value: str or None) -> int:
    """
    Set an attribute of a QgsVectorLayer with a single attribute value. If the attribute already has a value,
    the value will be overwritten with the new input attribute value. All features will have the same attribute value.

    Args:
        qgsvectorlayer (QgsVectorLayer): a QgsVectorLayer object
        attribute_name (str): the name of the attribute to set
        attribute_value (str): the object to set as the attribute's value (will be set for each matched feature)

    Returns:
        The number of features that had the attribute set.
    """

    logger = logging.getLogger(__name__)
    debug = False

    # Get the index of the attribute to set.
    # - fields() returns a QgsFields, which is a container for the list of QgsField
    # - lookupField() returns an int position of the field
    # - attribute_index is 0-reference
    attribute_index = qgsvectorlayer.fields().lookupField(attribute_name)
    if debug:
        logger.info("Layer attribute '{}' is at index {}.".format(attribute_name, attribute_index))

    if attribute_index >= 0:
        # Create an attribute dictionary.
        # Key: the index of the attribute to populate
        # Value: the string to populate as the attribute's values
        attribute = {attribute_index: attribute_value}

        # Iterate over the features of the QgsVectorLayer
        set_count = 0
        # QgsVectorDataProvider
        data_provider = qgsvectorlayer.dataProvider()
        for feature in qgsvectorlayer.getFeatures():
            # Set the feature's attribute with the attribute value.
            status = data_provider.changeAttributeValues({feature.id(): attribute})
            if status:
                # Success
                if debug:
                    logger.info("Success setting feature ID {} attribute '{}' to {}".format(
                        feature.id(), attribute_name, attribute_value))
                set_count += 1
            else:
                logger.warning("Error setting feature attribute '{}' to {}".format(attribute_name, attribute_value))

    return set_count


def split_qgsvectorlayer_by_attribute(processor: Processing, qgsvectorlayer: QgsVectorLayer, attribute_name: str,
                                      output_qgsvectorlayers: [QgsVectorLayer]) -> None:
    """
    Split the QgsVectorLayer object into multiple vector layers based on an attribute's unique values.

    REF: QGIS User Manual
    <https://docs.qgis.org/2.8/en/docs/user_manual/processing_algs/qgis/vector_general_tools.html#split-vector-layer>

    Args:
        processing (Processing): QGIS processor to use to run algorithm
        qgsvectorlayer (QgsVectorLayer): the QGSVectorLayer object
        attribute_name (str):  the name of the attribute that splits the qgsvectorlayer into multiple layers
        output_qgsvectorlayers (QgsVectorLayer): the QgsVectorLayer objects that are created by the split

    Returns:
        [QgsVectorLayers]  The number of layers is based on the number of unique values of the selected attribute.
    """

    # Split the QgsVectorLayer by the chosen attribute.  Output QgsVectorLayer names should be automatically generated??
    # QGIS 2?
    #processing.run('qgis:splitvectorlayer', qgsvectorlayer, attribute_name, output_qgsvectorlayers)
    processor.runAlgorithm('qgis:splitvectorlayer', qgsvectorlayer, attribute_name, output_qgsvectorlayers)


def write_algorithm_help ( output_file_absolute: str, list_algorithms: bool, algorithm_ids: [str]) -> None:
    """
    Write QGIS algorithm list and or help to a file.

    Args:
        output_file_absolute (str): Path to the output file.
        list_algorithms (bool): Whether to list algorithms.
        algorithm_ids ([str]): List of algorithms to print output.

    Returns:
        None
    """
    logger = logging.getLogger(__name__)
    fout = None
    # noinspection PyBroadException
    try:
        # Open the output file.
        if output_file_absolute is None:
            fout = sys.stdout
        else:
            fout = open(output_file_absolute, "w")
        nl = os.linesep  # newline character for operating system
        fout.write("QGIS Algorithm Information{}{}".format(nl, nl))
        # If requested, list the algorithms
        if list_algorithms:
            fout.write("QGIS Algorithm List:{}{}".format(nl, nl))
            # Loop through once to get the identifier length to format the columns
            id_len_max = 0
            for alg in QgsApplication.processingRegistry().algorithms():
                id_len = len(alg.id())
                if id_len > id_len_max:
                    id_len_max = id_len
            # Loop through again to output the list
            id_format = "{0:<" + str(id_len_max) + "} {1:}{2:}"
            fout.write(id_format.format("AlgorithmID", "Algorithm Name", nl))
            for alg in QgsApplication.processingRegistry().algorithms():
                fout.write(id_format.format(alg.id(), alg.displayName(), nl))

        if len(algorithm_ids) > 0:
            # List the specific algorithm help
            fout.write("{}QGIS Algorithm Help{}".format(nl, nl))
            for algorithm_id in algorithm_ids:
                fout.write(nl)
                # noinspection PyBroadException
                try:
                    # TODO smalers 2020-07-12 need to write to the output file
                    fout.write("QGIS algorithm {} help was written to console window.{}{}".format(algorithm_id, nl, nl))
                    processing.algorithmHelp(algorithm_id)
                except Exception:
                    logger.info("Error writing help for algorithm: {}".format(algorithm_id))

    except Exception:
        message = 'Error writing QGIS algorithm help to file "' + output_file_absolute + '.'
        logger.warning(message, exc_info=True)
    finally:
        if output_file_absolute is not None:
            if fout is not None:
                fout.close()


def write_qgsvectorlayer_to_delimited_file(qgsvectorlayer: QgsVectorLayer,
                                           output_file: str,
                                           crs_code: str,
                                           geometry_type: str,
                                           separator: str = "COMMA") -> None:
    """
    Write the QgsVectorLayer object to a spatial data file in CSV format.
    REF: QGIS API Documentation <https://qgis.org/api/classQgsVectorFileWriter.html>

    To use the QgsVectorFileWriter.writeAsVectorFormat tool, the following sequential arguments are defined:
        1. vectorFileName: the QGSVectorLayer object that is to be written to a spatial data format
        2. path to new file: the full pathname (including filename) of the output file
        3. output text encoding: always set to "utf-8"
        4. destination coordinate reference system
        5. driver name for the output file
        6. optional layerOptions (specific to driver name) REF: http://www.gdal.org/drv_csv.html

    Args:
        qgsvectorlayer (QgsVectorLayer): the QGSVectorLayer object
        output_file (str): the full pathname to the output file (do not include .csv extension)
        crs_code (str): the output coordinate reference system in EPSG code
        geometry_type (str): the type of geometry to export ( `AS_WKT`, `AS_XYZ`, `AS_XY` or `AS_YX`)
        separator (str): the symbol to use as the delimiter of the output delimited file (`COMMA`, `SEMICOLON`,
           `TAB` or `SPACE`)

    Returns:
        None
    """

    # Write the QgsVectorLayer object to a spatial data file in CSV format.
    # Note to developers: IGNORE `Unexpected Argument` error for layerOptions. This value is appropriate and
    #   functions properly.
    QgsVectorFileWriter.writeAsVectorFormat(qgsvectorlayer,
                                            output_file,
                                            "utf-8",
                                            QgsCoordinateReferenceSystem(crs_code),
                                            "CSV",
                                            layerOptions=['GEOMETRY=AS_{}'.format(geometry_type),
                                                          'SEPARATOR={}'.format(separator)])


# TODO smalers 2020-03-30 need to enable more properties without breaking default options for testing
def write_qgsvectorlayer_to_geojson(qgsvectorlayer: QgsVectorLayer,
                                    output_file_full: str,
                                    crs_code: str,
                                    precision: int) -> None:
    """
    Write the QgsVectorLayer object to a spatial data file in GeoJSON format.
    REF: `QGIS API Documentation <https://qgis.org/api/classQgsVectorFileWriter.html>_`

    To use the QgsVectorFileWriter.writeAsVectorFormat tool, the following sequential arguments are defined:
        1. vectorFileName: the QGSVectorLayer object that is to be written to a spatial data format
        2. path to new file: the full pathname (including filename) of the output file
        3. output text encoding: always set to "utf-8"
        4. destination coordinate reference system
        5. driver name for the output file
        6. optional layerOptions (specific to driver name) : for GeoJSON, coordinate precision is defined
        See:  https://gdal.org/drivers/vector/geojson.html
        Use minimal defaults suitable for automated testing.

    Args:
        qgsvectorlayer (QgsVectorLayer): the QgsVectorLayer object
        output_file_full (str): the full pathname to the output file
        crs_code (str): the output coordinate reference system code in EPSG code
        precision (int): a integer at or between 0 and 15 that determines the number of decimal places to include
            in the output geometry

    Returns:
        None
    """

    # Write the QgsVectorLayer object to a spatial data file in GeoJSON format.
    # Note to developers:
    #   IGNORE `Unexpected Argument` error for layerOptions. This value is appropriate and functions properly.
    layer_options = ['COORDINATE_PRECISION={}'.format(precision),
                     'RFC7946=YES',
                     'WRITE_NAME=NO']
    # 'WRITE_BBOX=YES',
    QgsVectorFileWriter.writeAsVectorFormat(layer=qgsvectorlayer,
                                            fileName=output_file_full,
                                            fileEncoding="utf-8",
                                            destCRS=QgsCoordinateReferenceSystem(crs_code),
                                            driverName="GeoJSON",
                                            layerOptions=layer_options)


def write_qgsvectorlayer_to_kml(qgsvectorlayer: QgsVectorLayer,
                                output_file_full: str,
                                crs_code: str,
                                name_field: str,
                                desc_field: str,
                                altitude_mode: str) -> None:
    """
    Write the QgsVectorLayer object to a spatial data file in KML format.
    REF: `QGIS API Documentation <https://qgis.org/api/classQgsVectorFileWriter.html>_`
    REF: `KML GDAL Specifications <http://www.gdal.org/drv_kml.html>_`

    To use the QgsVectorFileWriter.writeAsVectorFormat tool, the following sequential arguments are defined:
        1. vectorFileName: the QGSVectorLayer object that is to be written to a spatial data format
        2. path to new file: the full pathname (including filename) of the output file
        3. output text encoding: always set to "utf-8"
        4. destination coordinate reference system
        5. driver name for the output file
        6. optional layerOptions (specific to driver name): for KML, the following are defined
            a. NameField: Allows you to specify the field to use for the KML <name> element.
            b. DescriptionField: Allows you to specify the field to use for the KML <description> element.
            c. AltitudeMode: Allows you to specify the AltitudeMode to use for KML geometries. This will only affect
            3D geometries and must be one of the valid KML options.

    Args:
        qgsvectorlayer (QgsVectorLayer): the QgsVectorLayer object
        output_file_full (str): the full pathname to the output file (do not include .shp extension)
        crs_code (str): the output coordinate reference system in EPSG code
        name_field (str): the name field
        desc_field (str): the description field
        altitude_mode (str): the altitude mode

    Returns:
        None
    """

    # Write the QgsVectorLayer object to a spatial data file in Shapefile format.
    # Note to developers:
    #   IGNORE `Unexpected Argument` error for datasourceOptions. This value is appropriate and functions properly.
    QgsVectorFileWriter.writeAsVectorFormat(qgsvectorlayer,
                                            output_file_full,
                                            "utf-8",
                                            QgsCoordinateReferenceSystem(crs_code),
                                            "KML",
                                            datasourceOptions=['NameField={}'.format(name_field),
                                                               'DescriptionField={}'.format(desc_field),
                                                               'AltitudeMode={}'.format(altitude_mode)])


def write_qgsvectorlayer_to_shapefile(qgsvectorlayer: QgsVectorLayer,
                                      output_file_full: str,
                                      crs_code: str) -> None:
    """
    Write the QgsVectorLayer object to a spatial data file in Esri Shapefile format.
    REF: `QGIS API Documentation <https://qgis.org/api/classQgsVectorFileWriter.html>_`

    To use the QgsVectorFileWriter.writeAsVectorFormat tool, the following sequential arguments are defined:
        1. vectorFileName: the QGSVectorLayer object that is to be written to a spatial data format
        2. path to new file: the full pathname (including filename) of the output file
        3. output text encoding: always set to "utf-8"
        4. destination coordinate reference system
        5. driver name for the output file

    Args:
        qgsvectorlayer (QgsVectorLayer): the QgsVectorLayer object
        output_file_full (str): the full pathname to the output file (do not include .shp extension)
        crs_code (str): the output coordinate reference system in EPSG code

    Returns:
        None
    """

    # Write the QgsVectorLayer object to a spatial data file in Shapefile format.
    QgsVectorFileWriter.writeAsVectorFormat(qgsvectorlayer,
                                            output_file_full,
                                            "utf-8",
                                            QgsCoordinateReferenceSystem(crs_code),
                                            "ESRI Shapefile")
