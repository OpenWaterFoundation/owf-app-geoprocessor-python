# AttributesQDialog - class for attributes dialog
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

from PyQt5 import QtCore, QtGui, QtWidgets

from geoprocessor.core.VectorGeoLayer import VectorGeoLayer

import geoprocessor.ui.util.qt_util as qt_util
import geoprocessor.util.app_util as app_util

import logging


class GeoLayerAttributesQDialog(QtWidgets.QDialog):
    """
    Dialog to display GeoLayer attributes.
    """
    def __init__(self, geolayer: VectorGeoLayer) -> None:

        super(GeoLayerAttributesQDialog, self).__init__()

        # Layer that is being viewed
        self.geolayer: VectorGeoLayer = geolayer

        # Initialise the UI
        self.init_ui()

    def init_ui(self) -> None:
        """
        Initialize the dialog user interface.
        """

        logger = logging.getLogger(__name__)
        # noinspection PyBroadException
        try:
            qgs_layer = self.geolayer.qgs_layer

            self.resize(800, 500)
            self.setWindowTitle("Attributes - {}".format(self.geolayer.id))
            self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
            # Add icon
            icon_path = app_util.get_property("ProgramIconPath").replace('\\', '/')
            self.setWindowIcon(QtGui.QIcon(icon_path))

            # Create a vertical layout for the map window
            attributes_window_layout = QtWidgets.QVBoxLayout(self)
            attributes_window_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
            attributes_window_layout.setObjectName(qt_util.from_utf8("mapVerticalLayout"))

            # Get features from vector layer
            features = qgs_layer.getFeatures()
            num_features = qgs_layer.featureCount()
            # Get attribute field names
            attribute_field_names = self.geolayer.get_attribute_field_names()

            # Create a table for attributes
            attributes_table = QtWidgets.QTableWidget()
            attributes_window_layout.addWidget(attributes_table)
            attributes_table.setColumnCount(len(attribute_field_names))
            attributes_table.setRowCount(num_features)

            # Set Column Headers
            for i, attribute_field in enumerate(attribute_field_names):
                item = QtWidgets.QTableWidgetItem()
                attributes_table.setHorizontalHeaderItem(i, item)
                attributes_table.horizontalHeaderItem(i).setText(str(attribute_field))

            # Customize Header Row
            attributes_table.horizontalHeader().setStyleSheet("::section { background-color: #d3d3d3 }")

            # Retrieve attributes per feature and add them to the table
            for i, feature in enumerate(features):
                for j, attribute_field in enumerate(attribute_field_names):
                    attribute = feature[attribute_field]
                    item = QtWidgets.QTableWidgetItem(str(attribute))
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    attributes_table.setItem(i, j, item)

            self.show()
        except Exception:
            message = "Error opening attributes window.  See the log file."
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
