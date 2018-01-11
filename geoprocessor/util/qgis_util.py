# Utility functions related to QGIS and requires imports from QGIS libraries

import os
from qgis.core import QgsVectorLayer

def get_geometry_type_from_wkbtype(wkb_type):
    """

    Converts the hard-to-understand wkbType id into a more readable string.

    Args:
        wkb_type (str or int): the wkbType id.

    Returns:
        The corresponding geometry type in easy-to-read terminology.

    """

    # TODO egiles 2018-01-02 Need to research how to handle (correct naming convention) for WKBType -2147483643
    wkb_type_dic = {"0": "WKBUnknown",
                    "1": "WKBPoint",
                    "2": "WKBLineString",
                    "3": "WKBPolygon",
                    "4": "WKBMultiPoint",
                    "5": "WKBMultiLineString",
                    "6": "WKBMultiPolygon",
                    "100": "WKBNoGeometry",
                    "0x80000001": "WKBPoint25D",
                    "0x80000002": "WKBLineString25D",
                    "0x80000003": "WKBPolygon25D",
                    "0x80000004": "WKBMultiPoint25D",
                    "0x80000005": "WKBMultiLineString25D",
                    "0x80000006": "WKBMultiPolygon25D",
                    "-2147483643": "WKBUnknown"}

    # Only return geometry type (in string format) if the input wkb_type exists in the dictionary. Else return None.
    if wkb_type in list(wkb_type_dic.keys()):
        return wkb_type_dic[str(wkb_type)]
    else:
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
