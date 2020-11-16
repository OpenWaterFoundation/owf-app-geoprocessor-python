# VectorFormatType - vector file format types
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

# Vector format types used with GeoLayer.input_format and GeoLayer.output_format
# This is mainly used in cases where a GeoMapProject is written and other code such as InfoMapper needs to
# know the input format in order to branch logic reading the layer.
# See:  https://gdal.org/drivers/vector/index.html

CSV = 'CSV'  # Comma separated value
ESRIShapefile = 'ESRIShapefile'  # Esri shapefile
FileGDB = 'FileGDB'  # Esri file geodatabase
GeoJSON = 'GeoJSON'  # GeoJSON
KML = 'KML'  # KML
OpenFileGDB = 'OpenFileGDB'  # Esri file geodatabase, read-only, built-in, no third party libraries, better than FileGDB
WFS = 'WFS'  # OGC web feature service

# List of formats, used when providing a list such as in a command editor
vector_formats = [
    CSV,
    ESRIShapefile,
    FileGDB,
    GeoJSON,
    KML,
    OpenFileGDB,
    WFS
]
