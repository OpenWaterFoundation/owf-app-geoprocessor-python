# RasterFormatType - raster file format types
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

# Raster format types used with GeoLayer.input_format and GeoLayer.output_format
# This is mainly used in cases where a GeoMapProject is written and other code such as InfoMapper needs to
# know the input format in order to branch logic reading the layer.
# See:  https://gdal.org/drivers/vector/index.html

GTiff = 'GTiff'  # GeoTiff
WMS = 'WMS'  # Web Map Services
WMTS = 'WMTS'  # OGC Web Map Tile Service

# List of formats, used when providing a list such as in a command editor
raster_formats = [
    GTiff,
    WMS,
    WMTS
]


def get_format_from_extension(ext: str):
    """
    Determine a format from file extension.

    Args:
        ext (str): file extension

    Returns:
        (str) format from the extension or None if cannot be determined.
    """
    # For now this is not streamlined.  Could initialize data with list of tuples to hold recognized extensions.
    ext_upper = ext.upper()
    if ext_upper == "tiff" or ext_upper == "tif":
        return GTiff
    else:
        return None
