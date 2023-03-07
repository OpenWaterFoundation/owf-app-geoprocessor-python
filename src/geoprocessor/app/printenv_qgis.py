# printenv_qgis - simple program to troubleshoot qgis location
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

"""
Simple main program to print environment information and object attributes,
helpful for troubleshooting whether PyCharm PYTHONPATH is correct.
This script is the bare bones to check the environment.
See also the printenv_qt5.py program, which prints more information about Qt5.
"""

import sys
from PyQt5 import QtWidgets
import qgis


if __name__ == '__main__':
    """
    Entry point for the OWF GeoProcessor application.
    """
    print("PYTHONPATH items:")
    for item in sys.path:
        print(item)

    # Use code similar to the following to figure out object attributes.
    print("qgis attributes...")
    # Print application properties.
    q = qgis
    for item in dir(q):
        print(item)

    print("")
    print("qgis.core attributes...")
    qgis_core = qgis.core
    for item in dir(qgis_core):
        print(item)

    print("")
    print("qgis.PyQt attributes...")
    p = qgis.PyQt
    for item in dir(p):
        print(item)

    print("")
    print("qgis.utils attributes...")
    u = qgis.utils
    for item in dir(u):
        print(item)
