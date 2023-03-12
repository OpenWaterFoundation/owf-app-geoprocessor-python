# RasterGeoLayer - class for RasterGeoLayer (raster spatial data layer)
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2023 Open Water Foundation
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

# The following is needed to allow type hinting -> GeoLayer, and requires Python 3.7+.
# See:  https://stackoverflow.com/questions/33533148/
#         how-do-i-specify-that-the-return-type-of-a-method-is-the-same-as-the-class-itsel
from __future__ import annotations

import geoprocessor.util.qgis_util as qgis_util
from geoprocessor.core.GeoLayer import GeoLayer
from qgis.core import QgsRasterLayer


class RasterGeoLayer(GeoLayer):
    """
    The RasterGeoLayer class stores data and provides functionality for spatial data layer.
    The core GeoProcessor layer data are stored in GeoLayer.
    Internally, a QGIS QgsVectorLayer object is used in order to leverage the QGIS data model and functionality.
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

    def __init__(self,
                 geolayer_id: str,
                 name: str,
                 description: str = "",
                 qgs_raster_layer: QgsRasterLayer = None,
                 input_format: str = GeoLayer.FORMAT_MEMORY,
                 input_path_full: str = GeoLayer.SOURCE_MEMORY,
                 input_path: str = GeoLayer.SOURCE_MEMORY,
                 properties: dict = None) -> None:
        """
        Initialize a new RasterGeoLayer instance.

        Args:
            geolayer_id (str):
                String that is the GeoLayer's reference ID. This ID is used to access the GeoLayer from the
                GeoProcessor for manipulation.
            name (str):
                Layer name, will be used in map legend, etc.
            description (str):
                Layer description, with more details.
            qgs_raster_layer (QgsRasterLayer):
                Object created by the QGIS processor.
                All GeoLayer spatial manipulations are performed on the GeoLayer's qgs_layer.
            input_format (str):
                The format of the input spatial data file on the local computer, or URL to input,
                consistent with a GeoProcessor read command before the path is expanded.
                This is used when creating a GeoMapProject file, so that code such as InfoMapper that reads
                the file knows whether a URL is for GeoJSON, WMS, WFS, etc.
                If not specified, 'MEMORY' is used, assuming the layer was created in memory.
            input_path_full (str):
                The full pathname to the input spatial data file on the local computer,
                consistent with a GeoProcessor read command after the path is expanded.
                TODO smalers 2020-03-20 evaluate whether to allow URL.
                If not specified, GeoLayer.SUMMARY_MEMORY ('MEMORY') is used, assuming the layer was created in memory.
            input_path (str):
                The pathname to the input spatial data file on the local computer,
                consistent with a GeoProcessor read command before the path is expanded.
                This is typically a relative path but could be absolute (same as 'input_path_full').
                If not specified, GeoLayer.SUMMARY_MEMORY ('MEMORY') is used, assuming the layer was created in memory.
            properties ({}):
                A dictionary of user (non-built-in) properties that can be assigned to the layer.
                These properties facilitate processing.
        """

        # GeoLayer data:
        # - the layer is stored in the parent class using QGIS QgsLayer
        super().__init__(geolayer_id=geolayer_id,
                         name=name,
                         description=description,
                         qgs_layer=qgs_raster_layer,
                         input_format=input_format,
                         input_path_full=input_path_full,
                         input_path=input_path,
                         properties=properties)

        # All other differences are implemented through behavior with additional methods below.

    def deepcopy(self, copied_geolayer_id: str) -> RasterGeoLayer:
        """
        Create a copy of the RasterGeoLayer.

        Args:
            copied_geolayer_id(str): The ID of the output copied GeoLayer.

        Returns:
            The copied GeoLayer object.
        """

        # Create a deep copy of the qgs raster layer.
        duplicate_qgs_raster_layer = qgis_util.deepcopy_qgsrasterlayer(self.qgs_layer)

        # Update the layer's fields.
        self.qgs_layer.updateFields()

        # Create and return a new RasterGeoLayer object with the copied qgs vector layer.
        # The source will be an empty string.
        # The GeoLayer ID is provided by the argument parameter `copied_geolayer_id`.
        return RasterGeoLayer(copied_geolayer_id, duplicate_qgs_raster_layer, "")

    def get_feature_count(self) -> int:
        """
        Returns the number of features (int) within a RasterGeoLayer, in this case the number of cells.
        """

        # "feature_count" (int) is the number of features within the GeoLayer, in this case the number of cells.
        # Return the feature_count variable.
        return self.qgs_layer.featureCount()

    def get_geometry(self, geom_format: str = None) -> str:
        """
        Returns the RasterGeoLayer's geometry in desired format, currently always "raster".

        Args:
            geom_format: the desired geometry format, currently ignored

        Returns:
            The RasterGeoLayer's geometry in desired format (returns text version, not enumerator version).

        Raises:
            Value Error if the geom_format is not a valid format.
        """

        # See the VectorGeoLayer class for similar functionality that is more extensive, given vector layer design.
        return "raster"

    def get_num_bands(self) -> int:
        """
        Get the number of bands for this RasterGeoLayer.

        Returns:
            Number of bands for the raster geolayer or 0 if the layer is None.
        """
        if self.qgs_layer is None:
            return 0
        else:
            return self.qgs_layer.bandCount()

    def get_num_cells(self) -> int:
        """
        Get the number of cells for the RasterGeoLayer, which is the number of rows multiplied by the number of columns.

        Returns:
            Number of cells in raster geolayer.
        """
        if self.qgs_layer is not None:
            return self.get_num_rows() * self.get_num_columns()
        else:
            return 0

    def get_num_columns(self) -> int:
        """
        Get the number of columns (width) for a RasterGeoLayer.

        Returns:
            Number of columns in raster geolayer.
        """
        if self.is_raster() and self.qgs_layer is not None:
            return self.qgs_layer.width()
        else:
            return 0

    def get_num_rows(self) -> int:
        """
        Get the number of rows (height) for a RasterGeoLayer.

        Returns:
            Number of rows in raster geolayer.
        """
        if self.is_raster() and self.qgs_layer is not None:
            return self.qgs_layer.height()
        else:
            return 0

    def is_raster(self) -> bool:
        """
        Indicate whether a raster layer, always returns True.
        layers.

        Returns:
            True, always.
        """
        return True

    def is_vector(self) -> bool:
        """
        Indicate whether a vector layer, always returns False.

        Returns:
            False, always.
        """
        return False

    # TODO smalers 2020-01-13 evaluate whether this is needed for raster.
    # def write_to_disk(self, output_file_absolute):
