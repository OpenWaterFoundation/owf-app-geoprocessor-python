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
