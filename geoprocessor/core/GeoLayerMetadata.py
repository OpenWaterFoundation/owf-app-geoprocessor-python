class GeoLayerMetadata(object):

    """
    Metadata for the GeoLayers, a list of which is maintained as GeoProcessor.GeoLayers.
    This class is used to hold GeoLayer properties for each registered GeoLayer.
    """

    def __init__(self, geolayer_id, geolayer_qgs_object, geolayer_source_path):

        # "id" is a string that is the GeoLayer's reference ID. This ID is used to call the GeoLayer into the
        # GeoProcessor for manipulation.
        self.id = geolayer_id

        # "qgs_object" is a QGSVectorLayer object create by the QGIS processor. All spatial manipulations are performed
        # on the GeoLayer's qgs_object
        self.qgs_object = geolayer_qgs_object

        # "source_path" is a string that represents the full pathname to the original spatial data file on the user's
        # local computer
        self.source_path = geolayer_source_path

        # "geom_type" is a string that represents the GeoLayer's geometry type. The QGIS environment has an enumerator
        # system for each geometry type. The return_geometry_type_from_wkbtype function converts the enumerator with
        # the name of the geometry type.
        self.geom_type = GeoLayerMetadata.return_geometry_type_from_wkbtype(geolayer_qgs_object.wkbType())

        # "feature_count" is an int that represents the number of features within the GeoLayer
        self.feature_count = geolayer_qgs_object.featureCount()

        # "field_names" is a string that represents each of the GeoLayer's field names (each separtated by a comma)
        self.field_names = ', '.join([field.name() for field in geolayer_qgs_object.pendingFields()])

        # "qgs_id" is a string that represents the GeoLayer's id in the QGS environment (this is automatically assigned
        # by the QGIS GeoProcessor when a GeoLayer is originally created)
        self.qgs_id = geolayer_qgs_object.id()

        #"crs" is a string that represents the GeoLayer's coordinate reference systems in EPSG format
        self.crs = geolayer_qgs_object.crs().authid()

    @staticmethod
    def return_geometry_type_from_wkbtype(wkb_type):
        """

        Converts the hard-to-understand wkbType id into a more readable string.

        Args:
            wkbType (str or int): the wkbType id.

        Returns:
            The corresponding geometry type in easy-to-read terminology."""

        # TODO egiles 2018-01-02 Need to research how to handle (correct naming convention) for WKBType -2147483643
        wkb_type_dic = {"0": "WKBUnknown", "1": "WKBPoint", "2": "WKBLineString", "3": "WKBPolygon",
                        "4": "WKBMultiPoint", "5": "WKBMultiLineString", "6": "WKBMultiPolygon",
                        "100": "WKBNoGeometry",
                        "0x80000001": "WKBPoint25D", "0x80000002": "WKBLineString25D",
                        "0x80000003": "WKBPolygon25D",
                        "0x80000004": "WKBMultiPoint25D", "0x80000005": "WKBMultiLineString25D",
                        "0x80000006": "WKBMultiPolygon25D", "-2147483643": "WKBUnknown"}


       # Only return geometry type (in string format) if the input wkb_type exists in the dictionary. Else return None.
        if wkb_type in list(wkb_type_dic.keys()):
            return wkb_type_dic[str(wkb_type)]
        else:
            return None
