# printenv - simple program to print environment variables for Python
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
#     MERCHANtabILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with GeoProcessor.  If not, see <https://www.gnu.org/licenses/>.
# ________________________________________________________________NoticeEnd___

"""
Simple main program to print Python environment information, helpful for troubleshooting PyCharm.
"""

import os
import sys

if __name__ == '__main__':
    """
    Entry point into program to print Python enivironment information, helpful to troubleshoot Python.
    For example, problems are typically due to the PYTHONPATH, PATH, and environment variables.
    """
    print("\nUseful Environment Information for Troubleshooting\n")

    tab = "    "
    tab2 = tab + tab
    # Replace newlines in system version
    system_version = sys.version.replace("\r\n", " ").replace("\n", " ")

    print("Python Properties:\n" +
          tab + 'Python executable (.executable): ' + str(sys.executable) + "\n" +
          tab + 'Python Version (sys.version): ' + system_version + "\n")

    system_path = ''
    print(tab + 'Python Path (sys.path), unsorted, which indicates import search order:')
    for path_item in sys.path:
        print(tab2 + path_item)

    print('\n' + tab + 'Python Path (sys.path), sorted, useful to compare search path locations:')
    for path_item in sorted(sys.path):
        print(tab2 + path_item)

    print("\nSystem Information:")
    print("\n" + tab + "Environment variables:")
    for env_var in os.environ.keys():
        print("{}{}={}".format(tab2, env_var, os.environ[env_var]))

    print("\nPATH Environment Variable, unsorted:")

    # Add unsorted path, each part on a separate line
    path = ''
    for path_item in os.environ['PATH'].split(os.pathsep):
        print("{}{}".format(tab2, path_item))

    print("\nPATH Environment Variable, sorted:")

    # Add sorted path, each part on a separate line
    path_sorted = ''
    for path_item in os.environ['PATH'].split(os.pathsep):
        print("{}{}".format(tab2, path_item))
