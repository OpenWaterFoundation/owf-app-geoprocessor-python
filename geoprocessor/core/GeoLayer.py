import geoprocessor.util.qgis_util as qgis_util


from qgis.core import QgsApplication, QgsVectorLayer, QgsVectorFileWriter, QgsCoordinateReferenceSystem
from copy import deepcopy


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

    def add_attribute(self, attribute_name, attribute_type):
        """
        Adds an attribute to the GeoLayer.

        Args:
            attribute_name (string): the name of the attribute to add.
            attribute_type (string): the attribute field type.
                Can be int (integer), double (real number), string (text) or date.

        Return:
            None.
        """

        # Run processing in the qgis utility function.
        qgis_util.add_qgsvectorlayer_attribute(self.qgs_vector_layer, attribute_name, attribute_type)

    def deepcopy(self, copied_geolayer_id):
        """
        Create a copy of the GeoLayer.

        Arg:
            copied_geolayer_id(str): The ID of the output copied GeoLayer.

        Returns:
            The copied GeoLayer object.
        """


        # Create a deep copy of the qgs vecotor layer.
        duplicate_qgs_vector_layer = qgis_util.deepcopy_qqsvectorlayer(self.qgs_vector_layer)

        # Create and return a new GeoLayer object with the copied qgs vector layer. The source will be an empty string.
        # The GeoLayer ID is provided by the argument parameter `copied_geolayer_id`.
        return GeoLayer(copied_geolayer_id, duplicate_qgs_vector_layer, "")

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

    def get_geometry(self, geom_format="qgis"):
        """
        Returns the GeoLayer's geometry in desired format.

        Arg:
            geom_format: the desired geometry format. QGIS format by default.

        Returns:
            The GeoLayer's geometry in desired format (returns text version, not enumerator version).

        Raises:
            Value Error if the geom_foramt is not a valid format.
        """

        # Check that the format is a valid format.
        valid_geom_formats = ["QGIS", "WKB"]
        if geom_format.upper() in valid_geom_formats:

            # Return the geometry in QGIS format.
            if geom_format.upper() == "QGIS":
                return qgis_util.get_geometrytype_qgis(self.qgs_vector_layer)

            # Otherwise return the geometry in WKB format
            else:
                return qgis_util.get_geometrytype_wkb(self.qgs_vector_layer)

        # The geometry is not a valid format. Raise ValueError
        else:
            raise ValueError("Geom_format ({}) is not a valid geometry format. Valid geometry formats are:"
                             " {}".format(geom_format, valid_geom_formats))

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

    def remove_attribute(self, attribute_name):
        """
        Removes an attribute of the GeoLayer.

        Arg:
            attribute_name: the name of the attribute to remove.

        Returns:
            None
        """

        # Run processing in the qgis utility function.
        qgis_util.remove_qgsvectorlayer_attribute(self.qgs_vector_layer, attribute_name)

    def rename_attribute(self, attribute_name, new_attribute_name):
        """
        Renames an attribute.

        Arg:
            attribute_name (str):  The original attribute name.
            new_attribute_name (str): The new attribute name.

        Returns:
            None
        """

        # Run processing in the qgis utility function.
        qgis_util.rename_qgsvectorlayer_attribute(self.qgs_vector_layer, attribute_name, new_attribute_name)

    def set_property(self, property_name, property_value):
        """
        Set a GeoLayer property

        Args:
            property_name (str):  Property name.
            property_value (object):  Value of property, can be any built-in Python type or class instance.
        """
        self.properties[property_name] = property_value
