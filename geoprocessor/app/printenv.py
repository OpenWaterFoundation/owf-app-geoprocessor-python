# printenv - simple program to print environment variables for Python
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
Simple main program to print Python environment information and object attributes,
helpful for troubleshooting PyCharm.
"""

import sys
from PyQt5 import QtWidgets
import qgis.utils

if __name__ == '__main__':
    """
    Entry point for the OWF GeoProcessor application.
    """
    print("Python properties:")

    TAB = "    ";
    for item in sys.path:
        # Replace newlines in system version
        system_version = sys.version.replace("\r\n", " ").replace("\n", " ")
        system_path = ''
        for line in sys.path[1:]:
            system_path += str(line) + '\n' + TAB + TAB

        print("Python Properties:\n" +
              TAB + 'Python executable (.executable): ' + str(sys.executable) + "\n" +
              TAB + 'Python Version (sys.version): ' + system_version + "\n" +
              TAB + 'Python Path (sys.path):\n' +
              TAB + TAB + system_path + "\n")
