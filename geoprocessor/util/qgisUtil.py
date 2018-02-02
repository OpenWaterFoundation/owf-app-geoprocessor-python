# Utility functions related to QGIS and requires imports from QGIS libraries

import os

from qgis.core import QgsApplication
from qgis.core import QgsVectorLayer, QgsField, QgsVectorFileWriter, QgsCoordinateReferenceSystem

from processing.core.Processing import Processing

from PyQt4.QtCore import QVariant

from datetime import datetime

# TODO smalers 2018-01-28 Evaluate whether to make this private via Pythonic underscore naming
# QGIS application environment instance
# "qgs" is used to match QGIS conventions (rather than "qgis")
qgs = None


def add_qgsvectorlayer_attribute(qgsvectorlayer, attribute_name, attribute_type):

    """
    Adds an attribute to a Qgs Vector Layer object.

    Args:
        qgsvectorlayer (object): a Qgs Vector Layer object
        attribute_name (string): the name of the attribute to add
        attribute_type (string): the attribute field type. Can be int (integer), double (real number), string (text) or
         date.

    Return: None.
    """

    # Start the data provider for the input QgsVectorLayer.
    qgsvectorlayer_data = qgsvectorlayer.dataProvider()

    # Check that the attribute name is not already a name in the QgsVectorLayer.
    if attribute_name not in [attribute.name() for attribute in qgsvectorlayer_data.fields()]:

        try:

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
                print "Error message: The attribute_type ({}) is not a valid attribute type. Valid attribute types " \
                      "include: {}".format(attribute_type, valid_attribute_types)

            qgsvectorlayer.updateFields()

        except:
            print "An error occurred."

    # Print an error message if the input attribute name is already an existing attribute name.
    else:
        print "Error message: The attribute_name ({}) is an already existing attribute name.".format(attribute_name)


def deepcopy_qqsvectorlayer(qgsvectorlayer):
    """
    Creates a deep copy (separate instance) of a QgsVectorLayer object. Spatial features, attributes, and the
    coordinate reference system from the input QgsVectorLayer object will be retained in the output copied
    QgsVectorLayer object.

    Args:
        qgsvectorlayer (object): the QgsVectorLayer object to deep copy.

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


def get_geometrytype_qgis(qgsvectorlayer):
    """
    Returns the input QgsVectorLayer's geometry in QGIS format (returns text, not enumerator).
    REF: https://qgis.org/api/1.8/classQGis.html

    Arg:
        qgsvectorlayer (object): a Qgs Vector Layer object

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


def get_geometrytype_wkb(qgsvectorlayer):
    """
    Returns the input QgsVectorLayer's geometry in WKB format (returns text, not enumerator).
    REF: https://qgis.org/api/1.8/classQGis.html

    Arg:
        qgsvectorlayer (object): a Qgs Vector Layer object

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


def get_qgscoordinatereferencesystem_obj(crs_code):
    """
    Checks if the crs_code create a valid and usable QgsCoordinateReferenceSystem object. If so, return
    the QgsCoordinateReferenceSystem object. If not, return None.
    REF: https://qgis.org/api/2.18/classQgsCoordinateReferenceSystem.html#aa88613351434eeefdbdfbbd77ff33025

    Args:
        crs_code (str): a coordinate reference system code (EpsgCrsId, WKT or Proj4 codes).

    Returns: The QgsCoordinateReferenceSystem object. If not valid, returns None.

    """

    # Check if the crs_code is valid. If so, return the QgsCoordinateReferenceSystem object.
    if QgsCoordinateReferenceSystem(crs_code).isValid():
        return QgsCoordinateReferenceSystem(crs_code)

    # If not, return None.
    else:
        return None


def initialize_qgis(qgis_prefix_path):
    """
    Initialize the QGIS environment.  This typically needs to be done only once when the application starts.
    This is expected to be called once when an application starts, before any geoprocessing tasks.

    Args:
        qgis_prefix_path (str) the installation folder for the QGIS that is being used.

    Returns:
        None.
    """

    # Open QGIS environment
    QgsApplication.setPrefixPath(qgis_prefix_path, True)
    qgs = QgsApplication([], True)
    qgs.initQgis()
    Processing.initialize()


def populate_qgsvectorlayer_attribute(qgsvectorlayer, attribute_name, attribute_value):

    """
    Populates an attribute of a QgsVectorLayer with a single attribute value. If the attribute already has a value,
    the value will be overwritten with the new input attribute value. All features will have the same attribute value.

    Args:
        qgsvectorlayer (object): a Qgs Vector Layer object
        attribute_name (string): the name of the attribute to populate
        attribute_value (string): the string to populate as the attributes' values

    Returns: None.
    """

    # Get the index of the attribute to populate.
    attr_index = qgsvectorlayer.fieldNameIndex(attribute_name)

    # Create an attribute dictionary.
    # Key: the index of the attribute to populate
    # Value: the string to populate as the attribute's values
    attr = {attr_index: attribute_value}

    # Iterate over the features of the QgsVectorLayer
    for feature in qgsvectorlayer.getFeatures():

        # Rename/populate the features attribute with the desired input attribute value.
        qgsvectorlayer.dataProvider().changeAttributeValues({feature.id():attr})


def read_qgsvectorlayer_from_delimited_file_wkt(delimited_file_abs, delimiter, crs, wkt_col_name):
    """
    Reads a delimited file (with WKT column) and returns a QGSVectorLayerObject.

    Args:
        delimited_file_abs (string): the full pathname to a delimited file
        delimiter (string): the delimiter symbol (often times is a comma)
        crs (string): the coordinate reference system (in EPSG code)
        wkt_col_name (string): the name of the field/column containing the WKT geometry data

    Returns:
        A QGSVectorLayer object containing the data from the input delimited file. If the QgsVectorLayer is not
         valid, return None.
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
        return None


def read_qgsvectorlayer_from_delimited_file_xy(delimited_file_abs, delimiter, crs, x_col_name, y_col_name):
    """
    Reads a delimited file (with X and Y coordinates) and returns a QGSVectorLayerObject.

    Args:
        delimited_file_abs (string): the full pathname to a delimited file
        delimiter (string): the delimiter symbol (often times is a comma)
        crs (string): the coordinate reference system (in EPSG code)
        x_col_name (string): the name of the field containing the x coordinates
        y_col_name(string): the name of the filed containing the y coordinates

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
        return None


def read_qgsvectorlayer_from_feature_class(file_gdb_path_abs, feature_class):

    """
    Reads a feature class in a file geodatabase and returns a QGSVectorLayerObject.

    Args:
        file_gdb_path_abs (string): the full pathname to a file geodatabase
        feature_class (string): the name of the feature class to read

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
        print "The QGSVectorLayer object from file geodatabse ({}) feature class ({}) is invalid.".format(
            file_gdb_path_abs, feature_class)
        return None


def read_qgsvectorlayer_from_file(spatial_data_file_abs):

    """
    Reads the full pathname of spatial data file and returns a QGSVectorLayerObject.

    Args:
        spatial_data_file_abs (string): the full pathname to a spatial data file

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
        print "The QGSVectorLayer object ({}) is invalid.".format(spatial_data_file_abs)
        return None


def remove_qgsvectorlayer_attribute(qgsvectorlayer, attribute_name):
    """
    Deletes an attribute of a Qgs Vector Layer object.

    Args:
        qgsvectorlayer (object): a Qgs Vector Layer object
        attribute_name (string): the name of the attribute to delete

    Return: None.
    """

    # Iterate over the attributes in the Qgs Vector Layer object.
    for attribute in qgsvectorlayer.fields():

        # If the Qgs Vector Layer attribute name matches the parameter attribute_name, continue.
        if attribute.name().upper() == attribute_name.upper():

            # Get the index of the attribute to be deleted.
            index = qgsvectorlayer.fieldNameIndex(attribute.name())

            # Delete the attribute.
            qgsvectorlayer.dataProvider().deleteAttributes([index])

            # Update the layer's fields.
            qgsvectorlayer.updateFields()


def rename_qgsvectorlayer_attribute(qgsvectorlayer, attribute_name, new_attribute_name):
    # TODO egiles 2018-01-18 Create a warning if the new_attribute_name is longer than 10 characters but do not raise
    # TODO  an error

    """
    Renames an attribute of a Qgs Vector Layer object.

    Args:
        qgsvectorlayer (object): a Qgs Vector Layer object
        attribute_name (string): the original attribute name to change
        new_attribute_name (string): the new attribute name to rename

    Return:
        None.
    """

    # Iterate over the attributes in the Qgs Vector Layer object.
    for attribute in qgsvectorlayer.fields():

        # If the Qgs Vector Layer attribute name matches the parameter attribute_name, continue.
        if attribute.name().upper() == attribute_name.upper():

            # Start an editing session within QGIS environment.
            qgsvectorlayer.startEditing()

            # Get the index of the attribute to be renamed.
            index = qgsvectorlayer.fieldNameIndex(attribute.name())

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
        * qgsvectorlayer (object): the QGSVectorLayer object
        * output_file (string): the full pathname to the output file (do not include .csv extension)
        * crs (string): the output coordinate reference system in EPSG code
        * geometry_type (string): the type of geometry to export ( `AS_WKT`, `AS_XYZ`, `AS_XY` or `AS_YX`)
        * separator (string): the symbol to use as the delimiter of the output delimited file (`COMMA`, `SEMICOLON`,
           `TAB` or `SPACE`)

    Returns: None
    """

    # Write the QgsVectorLayer object to a spatial data file in CSV format.
    # Note to developers: IGNORE `Unexpected Argument` error for layerOptions. This value is appropriate and
    #   functions properly.
    QgsVectorFileWriter.writeAsVectorFormat(qgsvectorlayer,
                                            output_file,
                                            "utf-8",
                                            QgsCoordinateReferenceSystem(crs),
                                            "CSV",
                                            layerOptions=['GEOMETRY={}'.format(geometry_type),
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
        * qgsvectorlayer (object): the QGSVectorLayer object
        * output_file (string): the full pathname to the output file (do not include .shp extension)
        * crs (string): the output coordinate reference system in EPSG code
        * precision (int): a integer at or between 0 and 15 that determines the number of decimal places to include
            in the output geometry

    Returns: None
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
        * qgsvectorlayer (object): the QGSVectorLayer object
        * output_file (string): the full pathname to the output file (do not include .shp extension)
        * crs (string): the output coordinate reference system in EPSG code

    Return: None
    """

    # Write the QgsVectorLayer object to a spatial data file in Shapefile format.
    QgsVectorFileWriter.writeAsVectorFormat(qgsvectorlayer,
                                            output_file,
                                            "utf-8",
                                            QgsCoordinateReferenceSystem(crs),
                                            "ESRI Shapefile")
