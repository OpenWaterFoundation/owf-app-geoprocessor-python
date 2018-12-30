# printenv - simple program to print environment variables
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2019 Open Water Foundation
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

"""
Simple main program to print environment information and object attributes,
helpful for troubleshooting PyCharm.
"""

import sys
from PyQt5 import QtWidgets
import qgis.utils

if __name__ == '__main__':
    """
    Entry point for the OWF GeoProcessor application.
    """
    print("PYTHONPATH items:")
    for item in sys.path:
        print(item)

    # Use code similar to the following to figure out object attributes
    print("QApplication attributes...")
    qtapp = QtWidgets.QApplication(sys.argv)
    # Print application properties
    for item in dir(qtapp):
        print(item)

    print("qgis.utils attributes...")
    u = qgis.utils;
    for item in dir(u):
        print(item)

    print("qgis.utils.QGis attributes...")
    qgis = qgis.utils.Qgis;
    for item in dir(qgis):
        print(item)
