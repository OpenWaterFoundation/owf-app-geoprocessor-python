# GeoMapCustomJsonEncoder - class to encode GeoMap as JSON
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

from qgis.core import QgsCoordinateReferenceSystem

import json


class GeoMapCustomJsonEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to use with GeoMap.
    See:  https://code.tutsplus.com/tutorials/serialization-and-deserialization-of-python-objects-part-1--cms-26183
    See:  https://hynek.me/articles/serialization/
    """
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            # The object has a to_json() function so use it to serialize the object.
            # The to_json() function in a class should return a dictionary of:
            # - data primitives
            # - array
            # - dictionary
            return obj.to_json()
        elif isinstance(obj, QgsCoordinateReferenceSystem):
            # Serialize as the CRS code
            return obj.authid()
        else:
            # No custom JSON encoder is provider so use default, which handles Python primitives.
            return json.JSONEncoder.default(self, obj)
