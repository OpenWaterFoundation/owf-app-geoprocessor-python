import geoprocessor.util.qgis_util as qgis_util


# TODO smalers 2018-01-10 What about in-memory GeoLayers that are not read from a file?  No file required then.
# - how is the geolayer_source_path specified in that case?
# TODO smalers 2018-01-10 If getter functions are needed to return QGIS layer data, they should be here if
# appropriate, for example the CRS
# and not in geo.py utility module since the QGIS layer is essentially a part of the GeoLayer.
# I could see how if the QGIS methods and data really esoteric that having in a separate module is OK so
# the GeoLayer design does not get cluttered, but basic data should flow through GeoLayer.
# However, the following in geo, which has "self" as a parameter is a clue that it should be here:
#    def get_qgsvectorlayer_from_geolayer(self, geolayer_id):
# Just call it:
#    def get_qgsvectorlayer(self):
# Also, why is it "qgs" and not "qgis".  That seems confusing but I guess we should stick with their names.
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
    (ids, QgsVectorLayer object, source path and geometry type). The DYNAMIC GeoLayer properties (coordinate reference
    system, feature count, etc.) are created when needed by accessing call functions in the geo.py utility script.
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
                The full pathname to the original spatial data file on the user's local computer.
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

        # TODO smalers 2018-01-10 Still need a reference for the values.  As a programmer, what can I expect?
        # - Can a URL or something be shown so I can see valid values.
        # - This is a general comment I have - we need to make it easy for developers to know about QGIS.
        # "geom_type" (string) is the GeoLayer's geometry type. The QGIS environment has an enumerator
        # system for each geometry type. The get_geometry_type_from_wkbtype function converts the enumerator with
        # the name of the geometry type. Return the geom_type variable.
        self.geom_type = qgis_util.get_geometry_type_from_wkbtype(geolayer_qgs_vector_layer.wkbType())

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
