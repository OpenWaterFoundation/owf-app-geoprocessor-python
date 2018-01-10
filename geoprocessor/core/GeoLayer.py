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
    (ids, QgsVectorLayer object, source path and geometry type). The DYNAMIC GeoLayer properties (coordinate reference
    system, feature count, etc.) are created when needed by accessing call functions in the geo.py utility script.
    """

    def __init__(self, geolayer_id, geolayer_qgs_vector_layer, geolayer_source_path):

        # "id" is a string that is the GeoLayer's reference ID. This ID is used to call the GeoLayer into the
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

        # "geom_type" (string) is the GeoLayer's geometry type. The QGIS environment has an enumerator
        # system for each geometry type. The get_geometry_type_from_wkbtype function converts the enumerator with
        # the name of the geometry type. Return the geom_type variable.
        self.geom_type = qgis_util.get_geometry_type_from_wkbtype(geolayer_qgs_vector_layer.wkbType())
