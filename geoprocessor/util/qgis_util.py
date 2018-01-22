# Utility functions related to QGIS and requires imports from QGIS libraries

import os
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsCoordinateReferenceSystem, QgsApplication, QgsField
from qgis.core import QgsApplication
from PyQt4.QtCore import QVariant



def deepcopy_qqsvectorlayer(qgsvetorlayer):
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
    feats = [feat for feat in qgsvetorlayer.getFeatures()]

    # Get the geometry of the input QgsVectorLayer (qgis format).
    qgis_geometry = get_geometrytype_qgis(qgsvetorlayer)

    # Get the coordinate reference system of teh input QgsVectorLayer (string epsg code).
    crs = qgsvetorlayer.crs().authid()

    # Create a new in-memory QgsVectorLayer with same feature geometry type and CRS as the input QgsVectorLayer.
    copied_qgsvectorlayer = QgsVectorLayer("{}?crs={}".format(qgis_geometry, crs), "layer", "memory")

    # Start the data provider for the in-memory copied QgsVectorLayer.
    copied_qgsvectorlayer_data = copied_qgsvectorlayer.dataProvider()

    # Get a list of the input QgsVectorLayer's attributes.
    attr = qgsvetorlayer.dataProvider().fields().toList()

    # Add the attributes of the input QgsVectorLayer to the copied QgsVectorLayer.
    copied_qgsvectorlayer_data.addAttributes(attr)
    copied_qgsvectorlayer.updateFields()

    # Add the features of the input QgsVectorLayer to the copied QgsVectorLayer.
    copied_qgsvectorlayer_data.addFeatures(feats)

    # Return the deep copied QgsVectorLayer.
    return copied_qgsvectorlayer


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


def remove_qgsvectorlayer_attribute(qgsvectorlayer, attribute_name):
    """
    Deletes an attribute of a Qgs Vector Layer object.

    Args:
        qgsvectorlayer (object): a Qgs Vector Layer object
        attribute_name (string): the name of the attribute to delete

    Return:
        None.
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


def add_qgsvectorlayer_attribute(qgsvectorlayer, attribute_name, attribute_type):
    # TODO egiles 2018-01-22 Need to create a warning if the attribute_name is longer than 10 characters but do not
    # TODO raise an error

    """
    Adds an attribute to a Qgs Vector Layer object.

    Args:
        qgsvectorlayer (object): a Qgs Vector Layer object
        attribute_name (string): the name of the attribute to add
        attribute_type (string): the attribute field type. Can be int (integer), double (real number), string (text) or
         date.

    Return:
        None.
    """

    # A dictionary that relates the input parameter (attribute_type) with the QGIS field type.
    attribute_type_dic = {"int": QVariant.Int,
                          "double": QVariant.Double,
                          "string": QVariant.String,
                          "date": QVariant.Date}

    # Check that the attribute name is not already a name in the QgsVectorLayer.
    field_names = [field.name() for field in qgsvectorlayer.pendingFields()]
    if attribute_name not in field_names:

        # Check that the attribute type is valid.
        if attribute_type in list(attribute_type_dic.keys()):

            # Add the attribute to the qgsvectorlayer.
            qgsvectorlayer.dataProvider().addAttributes([QgsField(attribute_name, attribute_type_dic[attribute_type])])
            qgsvectorlayer.updateFields()

        # Print an error message if the attribute type is not valid.
        else:
            print "Error message: The attribute_type ({}) is not a valid attribute type. Valid attribute types " \
                  "include: {}".format(attribute_type, list(attribute_type_dic.keys()))

    # Print an error message if the input attribute name is already an existing attribute name.
    else:
        print "Error message: The attribute_name ({}) is an already existing attribute name.".format(attribute_name)


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
                      1: "Line",
                      2: "Polygon",
                      3: "UnknownGeometry",
                      4: "NoGeometry"}

    # Return the QGIS geometry type (in text form) of the input QgsVectorLayer.
    return enumerator_dic[qgsvectorlayer.geometryType()]
