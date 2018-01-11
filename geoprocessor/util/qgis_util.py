# Utility functions related to QGIS and requires imports from QGIS libraries

import os
import geoprocessor.util.geo as geo_util
from qgis.core import QgsVectorLayer


def get_attribute_field_names(self, geolayer_id):
    """

    Returns the a list of attribute field names within a GeoLayer.

    Args:
        self (obj): the GeoProcessor instance
        geolayer_id (string): the identifier for the GeoLayer of interest

    Returns:
         Returns a list of all attribute field names (list of strings) within the appropriate GeoLayer.

    Raises:
        Value Error if the geolayer_id is not a valid GeoLayerID.

    """

    # Check that the input GeoLayer is a registered GeoLayer within the GeoProcessor.
    if geo_util.is_geolayer_id(self, geolayer_id):

        # Get the appropriate GeoLayer
        geolayer = self.command_processor.get_geolayer(self, geolayer_id)

        # Get the QgsVectorLayer object of the GeoLayer
        qgs_vector_layer = geolayer.get_property("qgs_vector_layer")

        # Create an empty list that will hold each attribute field name (string).
        attribute_field_names = []

        # Iterate over the attribute fields of the GeoLayer.
        for attr_field in qgs_vector_layer.pendingFields():

            # Append the name of the attribute field to the attribute_field_names list.
            attribute_field_names.append(attr_field.name())

        # "attribute_field_names" (list of strings) is a list of the GeoLayer's attribute field names. Return the
        # attribute_field_names variable.
        return attribute_field_names

    else:
        raise ValueError


def get_crs(self, geolayer_id):

    """

    Returns the coordinate reference system of a GeoLayer.

    Args:
        self (obj): the GeoProcessor instance
        geolayer_id (string): the identifier for the GeoLayer of interest

    Returns:
        Returns the coordinate reference system (string, EPSG code) for the appropriate GeoLayer.

    Raises:
        Value Error if the geolayer_id is not a valid GeoLayerID.
    """

    # Check that the input GeoLayer is a registered GeoLayer within the GeoProcessor.
    if geo_util.is_geolayer_id(self, geolayer_id):

        # Get the appropriate GeoLayer
        geolayer = self.command_processor.get_geolayer(self, geolayer_id)

        # Get the QgsVectorLayer object of the GeoLayer
        qgs_vector_layer = geolayer.get_property("qgs_vector_layer")

        # "crs" (string) is the GeoLayer's coordinate reference system in
        # <EPSG format 'http://spatialreference.org/ref/epsg/'>_. Return the crs variable.
        crs = qgs_vector_layer.crs().authid()
        return crs

    else:
        raise ValueError


def get_feature_count(self, geolayer_id):

    """

    Returns the number of features within a GeoLayer.

    Args:
        self (obj): the GeoProcessor instance
        geolayer_id (string): the identifier for the GeoLayer of interest

    Returns:
        Returns the number of features (int) for the appropriate GeoLayer.

    Raises:
        Value Error if the geolayer_id is not a valid GeoLayerID.

    """

    # Check that the input GeoLayer is a registered GeoLayer within the GeoProcessor.
    if geo_util.is_geolayer_id(self, geolayer_id):

        # Get the appropriate GeoLayer
        geolayer = self.command_processor.get_geolayer(self, geolayer_id)

        # Get the QgsVectorLayer object of the GeoLayer
        qgs_vector_layer = geolayer.get_property("qgs_vector_layer")

        # "feature_count" (int) is the number of features within the GeoLayer. Return the feature_count variable.
        feature_count = qgs_vector_layer.featureCount()
        return feature_count

    else:
        raise ValueError


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


def read_qgsvectorlayer_from_spatial_data_file(spatial_data_file_abs):

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
