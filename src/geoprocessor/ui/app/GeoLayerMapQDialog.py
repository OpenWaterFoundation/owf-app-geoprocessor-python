# GeoLayerMapQDialog - class for map dialog
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

from PyQt5 import QtCore, QtGui, QtWidgets

from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.ui.util.qt_util as qt_util
import geoprocessor.util.app_util as app_util
import geoprocessor.util.qgis_util as qgis_util

import logging

import qgis.utils
import qgis.gui


class GeoLayerMapQDialog(QtWidgets.QDialog):
    """
    Dialog to display a map drawn in a canvas.
    """
    def __init__(self, geolayers: [GeoLayer]) -> None:

        super(GeoLayerMapQDialog, self).__init__()

        # Layers to be displayed in the map.
        self.geolayers: [GeoLayer] = geolayers

        self.canvas: qgis.gui.QgsMapCanvas or None = None
        self.map_window_widget: QtWidgets.QWidget or None = None
        self.map_toolbar: QtWidgets.QToolBar or None = None
        self.map_window_layout: QtWidgets.QVBoxLayout or None = None

        self.toolPan: qgis.gui.QgsMapToolPan or None = None
        self.toolZoomIn: qgis.gui.QgsMapToolZoom or None = None
        self.toolZoomOut: qgis.gui.QgsMapToolZoom or None = None

        self.actionZoomIn: QtWidgets.QAction or None = None
        self.actionZoomOut: QtWidgets.QAction or None = None
        self.actionPan: QtWidgets.QAction or None = None

        self.init_ui()

    def init_ui(self) -> None:
        """
        Initialize the user interface.

        Returns:
            None
        """

        logger = logging.getLogger(__name__)
        # noinspection PyBroadException
        try:
            self.resize(800, 500)
            self.setWindowTitle("Map")
            self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
            # Add icon.
            icon_path = app_util.get_property("ProgramIconPath").replace('\\', '/')
            self.setWindowIcon(QtGui.QIcon(icon_path))

            # Create a vertical layout for the map window.
            self.map_window_layout = QtWidgets.QVBoxLayout(self)
            self.map_window_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
            self.map_window_layout.setObjectName(qt_util.from_utf8("mapVerticalLayout"))

            # Add toolbar to map window.
            self.map_toolbar = QtWidgets.QToolBar()
            self.map_window_layout.addWidget(self.map_toolbar)

            # Create a widget for the canvas and add it to map_window in the map_window_layout.
            self.map_window_widget = QtWidgets.QWidget()
            self.map_window_layout.addWidget(self.map_window_widget)
            self.map_window_widget.setGeometry(QtCore.QRect(25, 20, 750, 450))
            # Create canvas and add it to the previously added widget.
            self.canvas = qgis.gui.QgsMapCanvas(self.map_window_widget)
            self.canvas.setCanvasColor(QtCore.Qt.white)
            self.canvas.resize(750, 400)

            # Get the extent for all the layers by calling qgis_util.
            logger.info("Have {} selected layers.".format(len(self.geolayers)))
            extent = qgis_util.get_extent_from_geolayers(self.geolayers, buffer_fraction=.05)
            self.canvas.setExtent(extent)
            self.canvas.setLayers(self.geolayers)

            # Add tools for map canvas.
            self.actionZoomIn = QtWidgets.QAction("Zoom in", self)
            self.actionZoomIn.setToolTip("Zoom in by clicking on a location to center on.")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm.
            # noinspection PyUnresolvedReferences
            self.actionZoomIn.triggered.connect(self.ui_action_map_zoom_in)
            self.actionZoomIn.setCheckable(True)
            self.map_toolbar.addAction(self.actionZoomIn)

            self.actionZoomOut = QtWidgets.QAction("Zoom out", self)
            self.actionZoomOut.setToolTip("Zoom out by clicking on a location to center on.")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm.
            # noinspection PyUnresolvedReferences
            self.actionZoomOut.triggered.connect(self.ui_action_map_zoom_out)
            self.actionZoomOut.setCheckable(True)
            self.map_toolbar.addAction(self.actionZoomOut)

            self.actionPan = QtWidgets.QAction("Pan", self)
            self.actionPan.setToolTip("Use mouse to drag the viewing area.")
            # Use the following because triggered.connect() is shown as unresolved reference in PyCharm.
            # noinspection PyUnresolvedReferences
            self.actionPan.triggered.connect(self.ui_action_map_pan)
            self.actionPan.setCheckable(True)
            self.map_toolbar.addAction(self.actionPan)

            # Add tools to canvas.
            self.toolPan = qgis.gui.QgsMapToolPan(self.canvas)
            self.toolPan.setAction(self.actionPan)
            self.toolZoomIn = qgis.gui.QgsMapToolZoom(self.canvas, False)  # false = in
            self.toolZoomIn.setAction(self.actionZoomIn)
            self.toolZoomOut = qgis.gui.QgsMapToolZoom(self.canvas, True)  # true = out
            self.toolZoomOut.setAction(self.actionZoomOut)

            QtCore.QMetaObject.connectSlotsByName(self)
            # Assign a resize event to resize map canvas when dialog window is resized.
            self.map_window_widget.resizeEvent = self.ui_action_map_resize
            self.show()
        except Exception:
            message = "Error opening map window.  See the log file."
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)

    def ui_action_map_pan(self) -> None:
        """
        Set GeoLayers map dialog window to allow user to pan with the mouse events.

        Returns:
            None
        """
        self.canvas.setMapTool(self.toolPan)

    def ui_action_map_resize(self, event) -> None:
        """
        Resize the GeoLayers map canvas when the dialog box is resized.

        Args:
            event: Resize event, necessary to add even though it is not being used in order
                for it to be recognized as a slot to respond to the given signal from the event.

        Returns:
            None
        """
        if event is None:
            # Use this to avoid warning about 'event' not being used.
            pass
        self.canvas.resize(self.map_window_widget.width(), self.map_window_widget.height())

    def ui_action_map_zoom_in(self) -> None:
        """
        Set the GeoLayers map window to respond to mouse events as zooming in.

        Returns:
            None
        """
        self.canvas.setMapTool(self.toolZoomIn)

    def ui_action_map_zoom_out(self) -> None:
        """
        Set the GeoLayers map window to respond to mouse events as zooming out.

        Returns:
            None
        """
        self.canvas.setMapTool(self.toolZoomOut)
