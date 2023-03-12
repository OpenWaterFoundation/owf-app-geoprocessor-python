# GeoLayerGraduatedSymbol - class to hold a layer's "graduated" symbology
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

from geoprocessor.core.GeoLayerSymbol import GeoLayerSymbol
from geoprocessor.core.GeoLayerSymbolClassificationType import GeoLayerSymbolClassificationType


class GeoLayerGraduatedSymbol(GeoLayerSymbol):
    """
    Class to store GeoLayerSymbol data for graduated classification.
    This results in a color map for a GeoLayer's attribute.
    """
    def __init__(self, classification_attribute: str, properties: dict, name: str, description: str = "") -> None:
        """
        Create a GeoLayerGraduatedSymbol instance, which defined the symbol for a GeoLayer.
        A classification type of GeoLayerSymbolClassificationType.GRADUATED will be passed to the parent
        GeoLayerSymbol class.

        Args:
            classification_attribute (str):  GeoLayer attribute that is used for classification.
            properties (dict):  Properties that describe the symbol.
            name (str):  Name of the symbol.
            description (str):  Description of the symbol.
        """
        super().__init__(GeoLayerSymbolClassificationType.GRADUATED, classification_attribute=classification_attribute,
                         properties=properties, name=name, description=description)

