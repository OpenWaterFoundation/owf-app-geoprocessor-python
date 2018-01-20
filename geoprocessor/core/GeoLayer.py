import geoprocessor.util.qgis_util as qgis_util

class GeoLayer(object):

    """
    The GeoLayer class stores geometry and identifier data for a spatial data layer. The core layer data are stored in
    a QGSVectorLayer object in order to leverage the QGIS data model and functionality. Additional data members are
    used to store data that are not part of QgsVectorLayer objects and are required by the GeoProcessor, such as source
    filename and identifier used by the GeoProcessor.

    A list of registered GeoLayer instances are maintained in the GeoProcessor's self.geolayers property (type: list).
    The GeoProcessor's commands retrieve in-memory GeoLayer instances from the GeoProcessor's self.geolayers property
    using the GeoProcessor.get_geolayer() function. New GeoLayer instances are added to the GeoProcessor list using the
    set_geolayer() function.

    There are a number of properties associated with each GeoLayer (id, coordinate reference system, feature count,
    etc.) The GeoLayer properties stored within each GeoLayer instance are the STATIC properties that will never change
    (ids, QgsVectorLayer object, and source path). The DYNAMIC GeoLayer properties (coordinate reference
    system, feature count, etc.) are created when needed by accessing call functions in the geo.py utility script.

    GeoLayers can be made in memory from within the GeoProcessor. This occurs when a command is called that, by design,
    creates a new GeoLayer (example: Clip). When this occurs, the in-memory GeoLayer is assigned a geolayer_id from
    within the command, the geolayer_qgs_vector_layer is created from within the command and the geolayer_source_path
    is set to 'MEMORY'.
    """

    def __init__(self, geolayer_id, geolayer_qgs_vector_layer, geolayer_source_path, properties=None):
        """
        Initialize a new GeoLayer instance.

        Args:
            geolayer_id (str):
                String that is the GeoLayer's reference ID. This ID is used to access the GeoLayer from the
                GeoProcessor for manipulation.
            geolayer_qgs_vector_layer (QGSVectorLayer):
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

        # "qgs_vector_layer" is a QGSVectorLayer object created by the QGIS processor. All spatial manipulations are
        # performed on the GeoLayer's qgs_vector_layer
        self.qgs_vector_layer = geolayer_qgs_vector_layer

        # "source_path" (string) is the full pathname to the original spatial data file on the user's local computer
        self.source_path = geolayer_source_path

        # "qgs_id" (string) is the GeoLayer's id in the QGS environment (this is automatically assigned by the QGIS
        # GeoProcessor when a GeoLayer is originally created)
        self.qgs_id = geolayer_qgs_vector_layer.id()

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

    # TODO smalers 2018-01-20 This functionality needs to be tested out
    # - this functionality should have nothing to do with the GeoProcessor
    # - just copy the GeoLayer to a new instance
    def deepcopy(self, orig):
        """
        Create a copy of an existing GeoLayer.

        Args:
            existing_geolayer_id(str): The ID of the existing GeoLayer.
            copied_geolayer_id(str): The ID of the copied GeoLayer.

        Returns:
            None

        Raises:
            None
        """

        # Get the GeoLayer object to be copied.
        """
        geolayer_orig = self.get_geolayer(existing_geolayer_id)

        # If the GeoLayer to be copied exists, continue.
        if geolayer_orig:

            # Get the GeoLayer's geometry (in QGIS format).
            original_qgis_geom = geolayer_orig.get_geometry_qgis()

            # Get the GeoLayer's CRS (in EPSG format).
            original_crs = geolayer_orig.get_crs()

            # Create a duplicate qgs_vector_layer.
            duplicate_qgs_vector_layer = qgis_util.create_qqsvectorlayer_duplicate(geolayer_orig.qgs_vector_layer,
                                                                                   original_qgis_geom,
                                                                                   original_crs)

            # Create a new GeoLayer object with the same geometry as the original GeoLayer. The
            # source will be an empty string. Add the copied GeoLayer to the GeoProcessor's geolayers list.
            copied_geolayer = GeoLayer(copied_geolayer_id, duplicate_qgs_vector_layer, "")
            self.add_geolayer(copied_geolayer)
        """
        pass


    def get_attribute_field_names(self):
        """
        Returns the a list of attribute field names (list of strings) within the GeoLayer.
        """

        # Get the attribute field names of the GeoLayer
        # "attribute_field_names" (list of strings) is a list of the GeoLayer's attribute field names. Return the
        # attribute_field_names variable.
        attribute_field_names = [attr_field.name() for attr_field in self.qgs_vector_layer.pendingFields()]
        return attribute_field_names

    def get_crs(self):
        """
        Returns the coordinate reference system (string, EPSG code) of a GeoLayer.
        """

        # "crs" (string) is the GeoLayer's coordinate reference system in
        # <EPSG format 'http://spatialreference.org/ref/epsg/'>_. Return the crs variable.
        crs = self.qgs_vector_layer.crs().authid()
        return crs

    def get_feature_count(self):
        """
        Returns the number of features (int) within a GeoLayer.
        """

        # "feature_count" (int) is the number of features within the GeoLayer. Return the feature_count variable.
        feature_count = self.qgs_vector_layer.featureCount()
        return feature_count

    def get_geometry_qgis(self):
        """
        Returns the GeoLayer's geometry in QGIS foramat.
        """

        # Get the wkb geometry type.
        wkb_type = self.get_geometry_wkb()

        # A dictionary that relates the wkb geometry types with the qgis geometry types.
        # List of QGIS geometry types included in following REF:
        #   https://docs.qgis.org/2.14/en/docs/pyqgis_developer_cookbook/vector.html#memory-provider
        wkb_qgis_geometry_dic = {"Point": ["WKBPoint", "WKBPoint25D"],
                                 "LineString": ["WKBLineString", "WKBLineString25D"],
                                 "Polygon": ["WKBPolygon", "WKBPolygon25D"],
                                 "MultiPoint": ["WKBMultiPoint", "WKBMultiPoint25D"],
                                 "MultiLineString": ["WKBMultiLineString", "WKBMultiLineString25D"],
                                 "MultiPolygon": ["WKBMultiPolygon25D", "WKBMultiPolygon"]}

        try:

            # Iterate through the wkb-qgis geometry dictionary. If the wkb_type is in the value of an entry, return
            # the corresponding qgis geometry.
            for geom_qgis, geom_wkb in wkb_qgis_geometry_dic.iteritems():
                if wkb_type in geom_wkb:
                    return geom_qgis

        except:
            raise ValueError("WKBGeometry ({}) is not recognized in the wkb-qgis-geometry-dictionary.".format(wkb_type))

    def get_geometry_wkb(self):
        """
        Returns the GeoLayer's geometry in WKB format.
        """

        # TODO smalers 2018-01-10 Still need a reference for the values.  As a programmer, what can I expect?
        # - Can a URL or something be shown so I can see valid values.
        # - This is a general comment I have - we need to make it easy for developers to know about QGIS.
        # "geom_type" (string) is the GeoLayer's geometry type. The QGIS environment has an enumerator
        # system for each geometry type. The get_geometry_type_from_wkbtype function converts the enumerator with
        # the name of the geometry type. Return the geom_type variable.
        wkb_geometry = qgis_util.get_geometry_type_from_wkbtype(self.qgs_vector_layer.wkbType())
        return wkb_geometry

    def get_property(self, property_name, if_not_found_val=None, if_not_found_except=False):
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
            KeyError if if_not_found_exept=True and the property name is not found.
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

    def rename_attribute(self, attribute_name, new_attribute_name):


        """
        Renames an attribute.

        Arg:
            attribute_name (string): the original attribute name to change
            new_attribute_name (string): the new attribute name to rename

        Return:
            None.

        Raises:
            None.
        """

        # Get the QGSVectorLayer object of the GeoLayer
        qgs_vector_layer = self.qgs_vector_layer

        # Run processing in qgis utility function
        qgis_util.rename_qgsvectorlayer_attribute(qgs_vector_layer, attribute_name, new_attribute_name)
