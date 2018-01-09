import os
from qgis.core import QgsVectorLayer

def read_qgsvectorlayer_from_spatial_data_file(spatial_data_file_abs):

    # Instantiate the QGSVectorLayer object.
    # From `QGIS documentation <https://docs.qgis.org/2.14/en/docs/pyqgis_developer_cookbook/loadlayer.html>`_
    # to create a QGSVectorLayer object, the following parameters must be entered:
    #   data_source: string representing the full path the the spatial data file
    #   layer_name: string representing the layer name that will be used in the QGIS layer list widget
    #       -- in this function the layer name is defaulted to the spatial data filename (with extension)
    #   provider_name: string representing the data provider (defaulted within this function to 'ogr')
    qgs_vector_layer_obj = QgsVectorLayer(spatial_data_file_abs, os.path.basename(spatial_data_file_abs), 'ogr')

    # A QgsVectorLayer object is almost always created even if it is invalid.
    # From `QGIS documentation <https://docs.qgis.org/2.14/en/docs/pyqgis_developer_cookbook/loadlayer.html>`_
    #   "It is important to check whether the layer has been loaded successfully. If it was not, an invalid
    #   layer instance is returned."
    # Check that the newly created QgsVectorLayer object is valid. If so, create a GeoLayer object within the
    # geoprocessor and add the GeoLayer object to the geoprocessor's GeoLayers list.
    if qgs_vector_layer_obj.isValid():
        return qgs_vector_layer_obj

    else:
        print "The QGSVectorLayer object ({}) is invalid.".format(spatial_data_file_abs)
        return None

def get_feature_count(self, geolayer_id):

    # Check that the input GeoLayer is a registered GeoLayer within the GeoProcessor.
    if is_geolayer_id(self, geolayer_id):

        # Get the QgsVectorLayer object of the GeoLayer.
        qgs_vector_layer = get_qgsvectorlayer_from_geolayer(self, geolayer_id)

        # "feature_count" (int) is the number of features within the GeoLayer. Return the feature_count variable.
        feature_count = qgs_vector_layer.featureCount()
        return feature_count


def get_geometry_type(self, geolayer_id):

    # Check that the input GeoLayer is a registered GeoLayer within the GeoProcessor.
    if is_geolayer_id(self, geolayer_id):

        # Get the QgsVectorLayer object of the GeoLayer.
        qgs_vector_layer = get_qgsvectorlayer_from_geolayer(self, geolayer_id)

        # "geom_type" (string) is the GeoLayer's geometry type. The QGIS environment has an enumerator
        # system for each geometry type. The get_geometry_type_from_wkbtype function converts the enumerator with
        # the name of the geometry type. Return the geom_type variable.
        geom_type = get_geometry_type_from_wkbtype(qgs_vector_layer.wkbType())
        return geom_type


def get_crs(self, geolayer_id):

    # Check that the input GeoLayer is a registered GeoLayer within the GeoProcessor.
    if is_geolayer_id(self, geolayer_id):

        # Get the QgsVectorLayer object of the GeoLayer.
        qgs_vector_layer = get_qgsvectorlayer_from_geolayer(self, geolayer_id)

        # "crs" (string) is the GeoLayer's coordinate reference system in
        # <EPSG format 'http://spatialreference.org/ref/epsg/'>_. Return the crs variable.
        crs = qgs_vector_layer.crs().authid()
        return crs


def get_attribute_field_names(self, geolayer_id):

    # Check that the input GeoLayer is a registered GeoLayer within the GeoProcessor.
    if is_geolayer_id(self, geolayer_id):

        # Get the QgsVectorLayer object of the GeoLayer.
        qgs_vector_layer = get_qgsvectorlayer_from_geolayer(self, geolayer_id)

        # Create an empty list that will hold each attribute field name (string).
        attribute_field_names = []

        # Iterate over the attribute fields of the GeoLayer.
        for attr_field in qgs_vector_layer.pendingFields():

            # Append the name of the attribute field to the attribute_field_names list.
            attribute_field_names.append(attr_field.name())

        # "attribute_field_names" (list of strings) is a list of the GeoLayer's attribute field names. Return the
        # attribute_field_names variable.
        return attribute_field_names

def get_geometry_type_from_wkbtype(wkb_type):
    """

    Converts the hard-to-understand wkbType id into a more readable string.

    Args:
        wkb_type (str or int): the wkbType id.

    Returns:
        The corresponding geometry type in easy-to-read terminology."""

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
