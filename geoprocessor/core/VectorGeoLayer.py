# VectorGeoLayer - class for VectorGeoLayer (vector spatial data layer)
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2020 Open Water Foundation
# 
# GeoProcessor is free software:  you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     GeoProcessor is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with GeoProcessor.  If not, see <https://www.gnu.org/licenses/>.
# ________________________________________________________________NoticeEnd___

# The following is needed to allow type hinting -> GeoLayer, and requires Python 3.7+
# See:  https://stackoverflow.com/questions/33533148/
#         how-do-i-specify-that-the-return-type-of-a-method-is-the-same-as-the-class-itsel
from __future__ import annotations

import geoprocessor.util.qgis_util as qgis_util
from geoprocessor.core.GeoLayer import GeoLayer
from qgis.core import QgsVectorLayer
import os


class VectorGeoLayer(GeoLayer):
    """
    The VectorGeoLayer class stores geometry and identifier data for a vector spatial data layer.
    The core layer data are stored in GeoLayer base class.
    Internally, a QgsVectorLayer object is used in order to leverage the QGIS data model and functionality.
    Additional data members are used to store data that are not part of QgsVectorLayer objects and are required by the
    GeoProcessor, such as source filename and identifier used by the GeoProcessor.

    A list of registered GeoLayer instances are maintained in the GeoProcessor's self.geolayers property (type: list).
    The GeoProcessor's commands retrieve in-memory GeoLayer instances from the GeoProcessor's self.geolayers property
    using the GeoProcessor.get_geolayer() function. New GeoLayer instances are added to the GeoProcessor list using the
    add_geolayer() function.

    There are a number of properties associated with each GeoLayer (id, coordinate reference system, feature count,
    etc.) The GeoLayer properties stored within each GeoLayer instance are the STATIC properties that will never change
    (ids, QgsVectorLayer object, and source path). The DYNAMIC GeoLayer properties (coordinate reference
    system, feature count, etc.) are created when needed by accessing class functions.

    GeoLayers can be made in memory from within the GeoProcessor. This occurs when a command is called that, by design,
    creates a new GeoLayer (example: Clip). When this occurs, the in-memory GeoLayer is assigned a geolayer_id from
    within the command, the geolayer_qgs_vector_layer is created from within the command and the geolayer_source_path
    is set to 'MEMORY'.
    """

    def __init__(self, geolayer_id: str,
                 geolayer_qgs_vector_layer: QgsVectorLayer = None,
                 geolayer_source_path: str = None, properties: dict = None) -> None:
        """
        Initialize a new GeoLayer instance.

        Args:
            geolayer_id (str):
                String that is the GeoLayer's reference ID. This ID is used to access the GeoLayer from the
                GeoProcessor for manipulation.
            geolayer_qgs_vector_layer (QgsVectorLayer)
                Object created by the QGIS processor. All GeoLayer spatial manipulations are
                performed on the GeoLayer's qgs_layer.
            geolayer_source_path (str):
                The full pathname to the original spatial data file on the user's local computer. If the geolayer was
                made in memory from the GeoProcessor, this value is set to `MEMORY`.
            properties ({}):
                A dictionary of user (non-built-in) properties that can be assigned to the layer.
                These properties facilitate processing.
        """

        # GeoLayer data
        # - the layer is stored in the parent class using QGIS QgsLayer
        super().__init__(geolayer_id=geolayer_id, geolayer_qgs_layer=geolayer_qgs_vector_layer,
                         geolayer_source_path=geolayer_source_path, properties=properties)

        # All other differences are implemented through behavior with additional methods below.

    def add_attribute(self, attribute_name: str, attribute_type: str) -> None:
        """
        Adds an attribute to the GeoLayer.

        Args:
            attribute_name (str): the name of the attribute to add.
            attribute_type (str): the attribute field type.
                Can be int (int), double (real number), string (text) or date.

        Returns:
            None.
        """

        # Run processing in the qgis utility function.
        qgis_util.add_qgsvectorlayer_attribute(self.qgs_layer, attribute_name, attribute_type)

    def deepcopy(self, copied_geolayer_id: str) -> VectorGeoLayer:
        """
        Create a copy of the GeoLayer.

        Args:
            copied_geolayer_id(str): The ID of the output copied GeoLayer.

        Returns:
            The copied GeoLayer object.
        """

        # Create a deep copy of the qgs vecotor layer.
        duplicate_qgs_vector_layer = qgis_util.deepcopy_qqsvectorlayer(self.qgs_layer)

        # Update the layer's fields.
        self.qgs_layer.updateFields()

        # Create and return a new GeoLayer object with the copied qgs vector layer. The source will be an empty string.
        # The GeoLayer ID is provided by the argument parameter `copied_geolayer_id`.
        return VectorGeoLayer(copied_geolayer_id, duplicate_qgs_vector_layer, "")

    def get_attribute_field_names(self) -> [str]:
        """
        Returns the a list of attribute field names (list of strings) within the GeoLayer.
        """

        # Get the attribute field names of the GeoLayer
        # "attribute_field_names" (list of strings) is a list of the GeoLayer's attribute field names. Return the
        # attribute_field_names variable.
        attribute_field_names = [attr_field.name() for attr_field in self.qgs_layer.fields()]
        return attribute_field_names

    def get_feature_count(self) -> int:
        """
        Returns the number of features (int) within a GeoLayer.
        """

        # "feature_count" (int) is the number of features within the GeoLayer. Return the feature_count variable.
        return self.qgs_layer.featureCount()

    def get_geometry(self, geom_format: str = "qgis") -> str:
        """
        Returns the GeoLayer's geometry in desired format.

        Args:
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
                return qgis_util.get_geometrytype_qgis(self.qgs_layer)

            # Otherwise return the geometry in WKB format
            else:
                return qgis_util.get_geometrytype_wkb(self.qgs_layer)

        # The geometry is not a valid format. Raise ValueError
        else:
            raise ValueError("Geom_format ({}) is not a valid geometry format. Valid geometry formats are:"
                             " {}".format(geom_format, valid_geom_formats))

    def is_raster(self) -> bool:
        """
        Indicate whether a raster layer, False always.

        Returns:
            False always.
        """
        return False

    def is_vector(self) -> bool:
        """
        Indicate whether a vector layer, True always.

        Returns:
            True always.
        """
        return True

    # TODO egiles 2018-01-29 Add sophistication to this function.
    def populate_attribute(self, attribute_name: str, attribute_value: object) -> None:
        """
        Populates the attribute of all features with a common attribute value (string value).

        Args:
            attribute_name: the name of the attribute to populate.
            attribute_value: the string to populate as the attributes' values

        Returns:
            None
        """

        # Run processing in the qgis utility function.
        qgis_util.populate_qgsvectorlayer_attribute(self.qgs_layer, attribute_name, attribute_value)

    def remove_attribute(self, attribute_name: str) -> None:
        """
        Removes an attribute of the GeoLayer.

        Args:
            attribute_name: the name of the attribute to remove.

        Returns:
            None
        """

        # Run processing in the qgis utility function.
        qgis_util.remove_qgsvectorlayer_attribute(self.qgs_layer, attribute_name)

    def remove_attributes(self, keep_pattern: list = None, remove_pattern: list = None) -> None:
        """
        Removes attributes of the GeoLayer depending on the glob-style input patterns

        Args:
            keep_pattern (list): a list of glob-style patterns of attributes to keep (will not be removed)
                Default: None. All attributes will be kept (if remove_pattern is default).
            remove_pattern (list): a list of glob-style patterns of attributes to remove
                Default: None. All attributes will be kept.

        Returns:
            None
        """

        # Run processing in the qgis utility function.
        qgis_util.remove_qgsvectorlayer_attributes(self.qgs_layer, keep_pattern, remove_pattern)

    def rename_attribute(self, attribute_name: str, new_attribute_name: str) -> None:
        """
        Renames an attribute.

        Args:
            attribute_name (str):  The original attribute name.
            new_attribute_name (str): The new attribute name.

        Returns:
            None
        """

        # Run processing in the qgis utility function.
        qgis_util.rename_qgsvectorlayer_attribute(self.qgs_layer, attribute_name, new_attribute_name)

    def split_by_attribute(self, attribute_name: str, output_qgsvectorlayers: str) -> None:
        """
        Splits a GeoLayer by a selected attribute.

        Args:
            attribute_name (str): the name of the attribute to split on.
            output_qgsvectorlayers (str): the names of the output GeoLayers.

        Returns:
            multiple GeoLayers.  The number of layers is based on the number of unique values of the selected attribute.
        """

        # Run processing in the qgis utility function.
        qgis_util.split_qgsvectorlayer_by_attribute(self.qgs_layer, attribute_name, output_qgsvectorlayers)

    def write_to_disk(self, output_file_absolute: str) -> GeoLayer:
        """
        Write the GeoLayer to a file on disk. The in-memory GeoLayer will be replaced by the on-disk GeoLayer. This
        utility method is useful when running a command that requires the input of a source path rather than a
        QgsVectorLayer object. For example, the "qgis:mergevectorlayers" requires source paths as inputs.

        Args:
            output_file_absolute: the full file path for the on-disk GeoLayer

        Returns:
            geolayer_on_disk: GeoLayer object of on-disk file. The id of the returned GeoLayer in the same as the
            current GeoLayer.
        """

        # Remove the shapefile (with its component files) from the temporary directory if it already exists. This
        # block of code was developed to see if it would fix the issue of tests failing when running under suite mode
        # and passing when running as a single test.
        if os.path.exists(output_file_absolute + '.shp'):

            # Iterate over the possible extensions of a shapefile.
            for extension in ['.shx', '.shp', '.qpj', '.prj', '.dbf', '.cpg', '.sbn', '.sbx', '.shp.xml']:

                # Get the full pathname of the shapefile component file.
                output_file_full_path = os.path.join(output_file_absolute + extension)

                # If the shapefile component file exists, add it' s absolute path to the files_to_archive list. Note that not
                # all shapefile component files are required -- some may not exist.
                if os.path.exists(output_file_full_path):
                    os.remove(output_file_full_path)

        # Write the GeoLayer (generally an in-memory GeoLayer) to a GeoJSON on disk (with the input absolute path).
        qgis_util.write_qgsvectorlayer_to_shapefile(self.qgs_layer, output_file_absolute, self.get_crs())

        # Read a QgsVectorLayer object from the on disk spatial data file (GeoJSON)
        qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_file(output_file_absolute + ".shp")

        # Create a new GeoLayer object with the same ID as the current object. The data however is not written to disk.
        # Return the new on-disk GeoLayer object.
        geolayer_on_disk = VectorGeoLayer(geolayer_id=self.id,
                                          geolayer_qgs_vector_layer=qgs_vector_layer,
                                          geolayer_source_path=output_file_absolute + ".shp")
        return geolayer_on_disk
