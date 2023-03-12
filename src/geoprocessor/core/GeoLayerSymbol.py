# GeoLayerSymbol - base class to hold a layer's symbology
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

from geoprocessor.core.GeoLayerSymbolClassificationType import GeoLayerSymbolClassificationType


class GeoLayerSymbol(object):
    """
    The GeoLayerSymbol class is the base class for GeoLayer symbolization.
    Specific symbols should be defined using GeoLayerSingleSymbol, GeoLayerGraduatedSymbol, and
    GeoLayerCategorizedSymbol classes.
    """

    def __init__(self, classification_type: GeoLayerSymbolClassificationType, classification_attribute: str,
                 properties: dict, name: str, description: str = "") -> None:
        # Name for the symbol.
        self.name: str = name

        # Description for symbol.
        self.description: str = description

        # Type of symbol.
        self.classification_type: GeoLayerSymbolClassificationType = classification_type

        # Classification attribute.
        self.classification_attribute: str = classification_attribute

        # Properties that define the symbol, different for each classification type.
        self.properties: dict = properties

    def to_json(self):
        """
        Return dictionary of class data to support JSON serialization using json package.
        This should be overridden in child classes.
        """
        use_dict = False
        if use_dict:
            # Dictionary has too much information but is useful to illustrate what objects need to be handled.
            return self.__dict__
        else:
            classification_type = self.classification_type.to_json_string()
            return {
                "name": self.name,
                "description": self.description,
                "classificationType": classification_type,
                "classificationAttribute": self.classification_attribute,
                "properties": self.properties
            }
