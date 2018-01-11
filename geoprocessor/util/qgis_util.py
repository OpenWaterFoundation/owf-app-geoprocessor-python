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
        spatial_data_file_abs (string): the full pathname to a spatial data file that exsists on the local computer

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
