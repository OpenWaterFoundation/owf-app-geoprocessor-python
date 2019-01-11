# qgis_util - utility functions related to QGIS and requires imports from QGIS libraries
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2019 Open Water Foundation
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
from qgis.core import QgsGeometry, QgsRasterLayer, QgsVectorFileWriter, QgsVectorLayer
from qgis.core import QgsExpressionContext, QgsExpressionContextScope

from qgis.analysis import QgsNativeAlgorithms

import qgis.utils

from plugins.processing.core import Processing

import geoprocessor.util.string_util as string_util

from PyQt5.QtCore import QVariant, QFileInfo
from PyQt5 import QtCore


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


def add_feature_to_qgsvectorlayer(qgsvectorlayer, qgsgeometry):
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


def add_qgsvectorlayer_attribute(qgsvectorlayer, attribute_name, attribute_type):
    """
    Adds an attribute to a QgsVectorLayer object.

    Args:
        qgsvectorlayer (QgsVectorLayer): a QgsVectorLayer object to be updated
        attribute_name (str): the name of the attribute to add
        attribute_type (str): the attribute field type. Can be int (integer), double (real number), string (text) or
                              date.

    Return:
        None.

    Raises:
        ValueError:  If the input is an invalid attribute type or the attribute already exists.
    """

    # Start the data provider for the input QgsVectorLayer.
    qgsvectorlayer_data = qgsvectorlayer.dataProvider()

    # Check that the attribute name is not already a name in the QgsVectorLayer.
    if attribute_name not in [attribute.name() for attribute in qgsvectorlayer_data.fields()]:

        # Add the attribute field to the GeoLater
        if attribute_type.upper() == "INT":
            qgsvectorlayer_data.addAttributes([QgsField(attribute_name, QVariant.Int)])
        elif attribute_type.upper() == "DOUBLE":
            qgsvectorlayer_data.addAttributes([QgsField(attribute_name, QVariant.Double)])
        elif attribute_type.upper() == "STRING":
            qgsvectorlayer_data.addAttributes([QgsField(attribute_name, QVariant.String)])
        elif attribute_type.upper() == "DATE":
            qgsvectorlayer_data.addAttributes([QgsField(attribute_name, QVariant.Date)])
        else:
            valid_attribute_types = ["int", "double", "string", "date"]
            message = "Error message: The attribute_type ({}) is not a valid attribute type. Valid attribute types " \
                      "include: {}".format(attribute_type, valid_attribute_types)
            logger = logging.getLogger(__name__)
            logger.error(message)
            raise ValueError(message)

        qgsvectorlayer.updateFields()

    else:
        # Print an error message if the input attribute name is already an existing attribute name.
        logger = logging.getLogger(__name__)
        message = "Error message: The attribute_name ({}) is an existing attribute name.".format(attribute_name)
        logger.error(message)
        raise ValueError(message)


def create_qgsgeometry(geometry_format, geometry_input_as_string):
    """
    Create a QGSGeometry object from input data. Can create an object from data in well-known text (WKT) and
    well-known binary (WKB). REF: https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/geometry.html

    Args:
        geometry_format (str): the type of geometry that the data is in. Can be either of the following:
            WKT: well-known text
            WKB: well-known binary
        geometry_input_as_string (str): the geometry data to convert to QGSGeometry object. Data must match the
            correct syntax for the geometry format value.

    Returns:
        - QgsGeometry object if geometry_format is valid,
        - None if the geometry is invalid.
    """

    # If the geometry format is well-known text, return the corresponding QgsGeometry object.
    if geometry_format.upper() == "WKT":
        return QgsGeometry.fromWkt(geometry_input_as_string)

    # If the geometry format is well-known binary, continue.
    elif geometry_format.upper() == "WKB":

        # Convert the WKB string into a a binary input. Return the corresponding QgsGeometry object.
        # This feature is only available for Python 3 upgrade. See reference below:
        # https://stackoverflow.com/questions/5901706/the-bytes-type-in-python-2-7-and-pep-358
        wkb = bytes.fromhex(geometry_input_as_string)
        return QgsGeometry().fromWkb(wkb)

    # If the geometry format is unknown, return None.
    else:
        return None


def create_qgsvectorlayer(geometry, crs_code, layer_name):
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
    layer = QgsVectorLayer("{}?crs={}".format(geometry, crs_code), layer_name, "memory")

    # If the QgsVectorLayer object is valid, return it.
    if layer.isValid():
        return layer
    else:
        message = 'Error creating layer "' + str(layer_name) + '"'
        logger = logging.getLogger(__name__)
        logger.warning(message)
        raise ValueError(message)


def deepcopy_qqsvectorlayer(qgsvectorlayer):
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


def exit_qgis():
    """
    Exit QGIS environment.
    This is expected to be called once when an application exits.

    Returns:
        None.
    """
    if qgs is not None:
        qgs.exit()


def get_extent_from_geolayers(selected_geolayers):
    """
    Return the maximum extent for a list of geolayers.
    If a single point, add +1.0 in the coordinate direction.

    Args:
        selected_geolayers:

    Returns:

    """
    xmin = float("inf")
    xmax = -float("inf")
    ymin = float("inf")
    ymax = -float("inf")
    for layer in selected_geolayers:
        extent = layer.extent()
        if extent.xMinimum() < xmin:
            xmin = extent.xMinimum()
        if extent.xMaximum() > xmax:
            xmax = extent.xMaximum()
        if extent.yMinimum() < ymin:
            ymin = extent.yMinimum()
        if extent.yMaximum() > ymax:
            ymax = extent.yMaximum()

    # Check if extent is single dimension
    if xmin == xmax:
        xmin -= 1.0
        xmax += 1.0

    if ymin == ymax:
        ymin -= 1.0
        ymax += 1.0

    return qgis.core.QgsRectangle(xmin, ymin, xmax, ymax)


def get_features_matching_expression(qgsvectorlayer, qgs_expression):
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


def get_features_not_matching_expression(qgsvectorlayer, qgs_expression):
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


def get_geometrytype_qgis(qgsvectorlayer):
    """
    Returns the input QgsVectorLayer's geometry in QGIS format (returns text, not enumerator).
    REF: https://qgis.org/api/1.8/classQGis.html

    Args:
        qgsvectorlayer (QgsVectorLayer): a QgsVectorLayer object

    Returns:
        Appropriate geometry in QGIS format (returns text, not enumerator).
    """

    # The QGIS geometry type enumerator dictionary.
    enumerator_dic = {0: "Point",
                      1: "LineString",
                      2: "Polygon",
                      3: "UnknownGeometry",
                      4: "NoGeometry"}

    # Return the QGIS geometry type (in text form) of the input QgsVectorLayer.
    return enumerator_dic[qgsvectorlayer.geometryType()]


def get_geometrytype_qgis_from_wkt(wkt_string):
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
    QGIS_WKT_geom_conversion_dic = {"Point": ["POINT", "MULTIPOINT"],
                                    "Polygon": ["POLYGON", "MULTIPOLYGON"],
                                    "LineString": ["LINESTRING", "MULTILINESTRING"]}

    # Get the WKT geometry type from a Well-Known Text string. Capitalize the characters of the geometry type.
    wkt_geometry_type = (wkt_string.split('(')[0]).strip().upper()

    # Iterate over the entries in the QGIS/WKT geometry type conversion dictionary (QGIS_WKT_geom_conversion_dic).
    for qgis_geometry_type, wkt_geometry_types in QGIS_WKT_geom_conversion_dic.items():

        # If the WKT geometry of the input WKT string is recognized, return the equivalent QGIS geometry.
        if wkt_geometry_type in wkt_geometry_types:
            return qgis_geometry_type


def get_geometrytype_wkb(qgsvectorlayer):
    """
    Returns the input QgsVectorLayer's geometry in WKB format (returns text, not enumerator).
    REF: https://qgis.org/api/1.8/classQGis.html

    Args:
        qgsvectorlayer (QgsVectorLayer): a QgsVectorLayer object

    Returns:
        Appropriate geometry in WKB format (returns text, not enumerator).
    """

    # The WKB geometry type enumerator dictionary.
    enumerator_dic = {0: "WKBUnknown",
                      1: "WKBPoint",
                      2: "WKBLineString",
                      3: "WKBPolygon",
                      4: "WKBMultiPoint",
                      5: "WKBMultiLineString",
                      6: "WKBMultiPolygon",
                      100: "WKBNoGeometry",
                      0x80000001: "WKBPoint25D",
                      0x80000002: "WKBLineString25D",
                      0x80000003: "WKBPolygon25D",
                      0x80000004: "WKBMultiPoint25D",
                      0x80000005: "WKBMultiLineString25D",
                      0x80000006: "WKBMultiPolygon25D",
                      -2147483643: "WKBUnknown"}

    # Return the WKB geometry type (in text form) of the input QgsVectorLayer.
    return enumerator_dic[qgsvectorlayer.wkbType()]


def get_qgis_version_developer(int_version=True):
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
        return int("{}{}{}".format(major, minor, bug_fix))
    else:
        return "{}.{}.{}".format(major, minor, bug_fix)


def get_qgis_version_int():
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


def get_qgis_version_name():
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


def get_qgis_version_str():
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


def get_qgscoordinatereferencesystem_obj(crs_code):
    """
    Checks if the crs_code create a valid and usable QgsCoordinateReferenceSystem object. If so, return
    the QgsCoordinateReferenceSystem object. If not, return None.
    REF: https://qgis.org/api/2.18/classQgsCoordinateReferenceSystem.html#aa88613351434eeefdbdfbbd77ff33025

    Args:
        crs_code (str): a coordinate reference system code (EpsgCrsId, WKT or Proj4 codes).

    Returns:
        The QgsCoordinateReferenceSystem object. If not valid, returns None.
    """

    # Check if the crs_code is valid. If so, return the QgsCoordinateReferenceSystem object.
    if QgsCoordinateReferenceSystem(crs_code).isValid():
        return QgsCoordinateReferenceSystem(crs_code)

    # If not, return None.
    else:
        return None


def get_qgsexpression_obj(expression_as_string):
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


def initialize_qgis():
    """
    Initialize the QGIS environment.  This typically needs to be done only once when the application starts.
    This is expected to be called once when an application starts, before any geoprocessing tasks.

    Returns:
        None
    """

    # Open QGIS environment
    # REF: https://github.com/OSGeo/homebrew-osgeo4mac/issues/197
    global qgs_app
    # A warning like similar to the following may be shown unless the following line of code is added.
    # - See https://bugreports.qt.io/browse/QTBUG-51379
    # -------
    # Qt WebEngine seems to be initialized from a plugin. Please set Qt::AA_ShareOpenGLContexts using
    #   QCoreApplication::setAttribute before constructing QGuiApplication
    # -------
    try:
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    except Exception as e:
        # This happens when the current development Python packages are different than runtime
        print("Error calling QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)")
        print("- possibly due to Python API version issue")
        print("- ignoring exception and starting the application")
    qgs_app = QgsApplication([], False)
    qgs_app.initQgis()
    return qgs_app


def initialize_qgis_processor():
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


def populate_qgsvectorlayer_attribute(qgsvectorlayer, attribute_name, attribute_value):
    """
    Populates an attribute of a QgsVectorLayer with a single attribute value. If the attribute already has a value,
    the value will be overwritten with the new input attribute value. All features will have the same attribute value.

    Args:
        qgsvectorlayer (QgsVectorLayer): a QgsVectorLayer object
        attribute_name (str): the name of the attribute to populate
        attribute_value (str): the string to populate as the attributes' values

    Returns:
        None
    """

    # Get the index of the attribute to populate.
    attr_index = qgsvectorlayer.fields().lookupField(attribute_name)

    # Create an attribute dictionary.
    # Key: the index of the attribute to populate
    # Value: the string to populate as the attribute's values
    attr = {attr_index: attribute_value}

    # Iterate over the features of the QgsVectorLayer
    for feature in qgsvectorlayer.getFeatures():

        # Rename/populate the features attribute with the desired input attribute value.
        qgsvectorlayer.dataProvider().changeAttributeValues({feature.id(): attr})


def read_qgsrasterlayer_from_file(spatial_data_file_abs):
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
    fileInfo = QFileInfo(spatial_data_file_abs)
    path = fileInfo.filePath()
    baseName = fileInfo.baseName()

    # Create the QgsRasterLayer object.
    qgs_raster_layer_obj = QgsRasterLayer(path, baseName)

    # Return the QgsRasterLayer if it is valid.
    if qgs_raster_layer_obj.isValid():
        return qgs_raster_layer_obj

    # If the created QGSRasterLayer object is invalid, print an error message and return None.
    else:
        message = 'The QGSRasterLayer for file "{}" is invalid.'.format(spatial_data_file_abs)
        logger = logging.getLogger(__name__)
        logger.warning(message)
        raise IOError(message)


def read_qgsvectorlayer_from_delimited_file_wkt(delimited_file_abs, delimiter, crs, wkt_col_name):
    """
    Reads a delimited file (with WKT column) and returns a QGSVectorLayerObject.

    Args:
        delimited_file_abs (str): the full pathname to a delimited file
        delimiter (str): the delimiter symbol (often times is a comma)
        crs (str): the coordinate reference system (in EPSG code)
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
    uri = "file:///{}?delimiter={}&crs={}&wktField={}".format(delimited_file_abs, delimiter, crs, wkt_col_name)
    qgsvectorlayer = QgsVectorLayer(uri, os.path.basename(delimited_file_abs), "delimitedtext")

    # If the QgsVectorLayer is valid, return it. Otherwise return None.
    if qgsvectorlayer.isValid():
        return qgsvectorlayer
    else:
        logger = logging.getLogger(__name__)
        message = 'The QGSVectorLayer object for delimited file "{}" is invalid.'.format(delimited_file_abs)
        logger.warning(message)
        raise IOError(message)


def read_qgsvectorlayer_from_delimited_file_xy(delimited_file_abs, delimiter, crs, x_col_name, y_col_name):
    """
    Reads a delimited file (with X and Y coordinates) and returns a QGSVectorLayerObject.

    Args:
        delimited_file_abs (str): the full pathname to a delimited file
        delimiter (str): the delimiter symbol (often times is a comma)
        crs (str): the coordinate reference system (in EPSG code)
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
                                                                      delimiter, crs, x_col_name, y_col_name)
    qgsvectorlayer = QgsVectorLayer(uri, os.path.basename(delimited_file_abs), "delimitedtext")

    # If the QgsVectorLayer is valid, return it. Otherwise return None.
    if qgsvectorlayer.isValid():
        return qgsvectorlayer
    else:
        logger = logging.getLogger(__name__)
        message = 'The QGSVectorLayer object for file "{}" is invalid.'.format(delimited_file_abs)
        logger.warning(message)
        raise IOError(message)


def read_qgsvectorlayer_from_excel_worksheet(excel_workbook_abs, worksheet_index=0):
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


def read_qgsvectorlayer_from_feature_class(file_gdb_path_abs, feature_class):

    """
    Reads a feature class in a file geodatabase and returns a QGSVectorLayerObject.

    Raises:
        IOError if the geodatabase layer is invalid.

    Args:
        file_gdb_path_abs (str): the full pathname to a file geodatabase
        feature_class (str): the name of the feature class to read

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
        return qgs_vector_layer_obj

    # If the created QGSVectorLayer object is invalid, print an error message and return None.
    else:
        message = 'The QGSVectorLayer from file geodatabase "{}" feature class "{}" is invalid.'.format(
                   file_gdb_path_abs, feature_class)
        logger = logging.getLogger(__name__)
        logger.warning(message)
        raise IOError(message)


def read_qgsvectorlayer_from_file(spatial_data_file_abs):

    """
    Reads the full pathname of spatial data file and returns a QGSVectorLayer object.

    Args:
        spatial_data_file_abs (str): the full pathname to a spatial data file

    Raises:
        IOError if the geodatabase layer is invalid.

    Returns:
        A QGSVectorLayer object containing the data from the input spatial data file.
    """

    # Instantiate the QGSVectorLayer object.
    # From `QGIS documentation <https://docs.qgis.org/2.14/en/docs/pyqgis_developer_cookbook/loadlayer.html>`_
    # to create a QGSVectorLayer object, the following parameters must be entered:
    #   data_source (first argument): string representing the full path the the spatial data file
    #   layer_name (second argument): string representing the layer name that will be used in the QGIS layer list widget
    #       -- in this function the layer name is defaulted to the spatial data filename (with extension)
    #   provider_name (third argument): string representing the data provider (defaulted within this function to 'ogr')
    qgs_vector_layer_obj = QgsVectorLayer(spatial_data_file_abs, os.path.basename(spatial_data_file_abs), 'ogr')

    # A QgsVectorLayer object is almost always created even if it is invalid.
    # From `QGIS documentation <https://docs.qgis.org/2.14/en/docs/pyqgis_developer_cookbook/loadlayer.html>`_
    #   "It is important to check whether the layer has been loaded successfully. If it was not, an invalid
    #   layer instance is returned."
    # Check that the newly created QgsVectorLayer object is valid. If so, create a GeoLayer object within the
    # geoprocessor and add the GeoLayer object to the geoprocessor's GeoLayers list.
    if qgs_vector_layer_obj.isValid():
        return qgs_vector_layer_obj

    # If the created QGSVectorLayer object is invalid, print an error message and return None.
    else:
        message = 'The QGSVectorLayer for file "{}" is invalid.'.format(spatial_data_file_abs)
        logger = logging.getLogger(__name__)
        logger.warning(message)
        raise IOError(message)


def remove_qgsvectorlayer_attribute(qgsvectorlayer, attribute_name):
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


def remove_qgsvectorlayer_attributes(qgsvectorlayer, keep_patterns, remove_patterns):
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


def remove_qgsvectorlayer_features(qgsvectorlayer, list_of_feature_ids):
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


def rename_qgsvectorlayer_attribute(qgsvectorlayer, attribute_name, new_attribute_name):
    # TODO egiles 2018-01-18 Create a warning if the new_attribute_name is longer than 10 characters but do not raise
    # TODO  an error
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


def write_qgsvectorlayer_to_delimited_file(qgsvectorlayer, output_file, crs, geometry_type, separator="COMMA"):
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
        crs (str): the output coordinate reference system in EPSG code
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
                                            QgsCoordinateReferenceSystem(crs),
                                            "CSV",
                                            layerOptions=['GEOMETRY=AS_{}'.format(geometry_type),
                                                          'SEPARATOR={}'.format(separator)])


def write_qgsvectorlayer_to_geojson(qgsvectorlayer, output_file, crs, precision):
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

    Args:
        qgsvectorlayer (QgsVectorLayer): the QgsVectorLayer object
        output_file (str): the full pathname to the output file (do not include .shp extension)
        crs (str): the output coordinate reference system in EPSG code
        precision (int): a integer at or between 0 and 15 that determines the number of decimal places to include
            in the output geometry

    Returns:
        None
    """

    # Write the QgsVectorLayer object to a spatial data file in Shapefile format.
    # Note to developers:
    #   IGNORE `Unexpected Argument` error for layerOptions. This value is appropriate and functions properly.
    QgsVectorFileWriter.writeAsVectorFormat(qgsvectorlayer,
                                            output_file,
                                            "utf-8",
                                            QgsCoordinateReferenceSystem(crs),
                                            "GeoJSON",
                                            layerOptions=['COORDINATE_PRECISION={}'.format(precision), 'WRITE_NAME=NO'])


def write_qgsvectorlayer_to_kml(qgsvectorlayer, output_file, crs, name_field, desc_field, altitude_mode):
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
        output_file (str): the full pathname to the output file (do not include .shp extension)
        crs (str): the output coordinate reference system in EPSG code
        name_field (str): the field holding the

    Returns:
        None
    """

    # Write the QgsVectorLayer object to a spatial data file in Shapefile format.
    # Note to developers:
    #   IGNORE `Unexpected Argument` error for datasourceOptions. This value is appropriate and functions properly.
    QgsVectorFileWriter.writeAsVectorFormat(qgsvectorlayer,
                                            output_file,
                                            "utf-8",
                                            QgsCoordinateReferenceSystem(crs),
                                            "KML",
                                            datasourceOptions=['NameField={}'.format(name_field),
                                                               'DescriptionField={}'.format(desc_field),
                                                               'AltitudeMode={}'.format(altitude_mode)])


def write_qgsvectorlayer_to_shapefile(qgsvectorlayer, output_file, crs):
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
        output_file (str): the full pathname to the output file (do not include .shp extension)
        crs (str): the output coordinate reference system in EPSG code

    Returns:
        None
    """

    # Write the QgsVectorLayer object to a spatial data file in Shapefile format.
    QgsVectorFileWriter.writeAsVectorFormat(qgsvectorlayer,
                                            output_file,
                                            "utf-8",
                                            QgsCoordinateReferenceSystem(crs),
                                            "ESRI Shapefile")
