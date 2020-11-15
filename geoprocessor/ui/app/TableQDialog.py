# TableQDialog - class for table dialog
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

from geoprocessor.core.DataTable import DataTable

import geoprocessor.ui.util.qt_util as qt_util
import geoprocessor.util.app_util as app_util

import logging


class TableQDialog(QtWidgets.QDialog):
    """
    Dialog to display table.
    """
    def __init__(self, table: DataTable) -> None:

        super(TableQDialog, self).__init__()

        # Table that is being viewed
        self.table: DataTable = table

        self.table_window_layout: QtWidgets.QVBoxLayout or None = None
        self.table_table: QtWidgets.QTableWidget or None = None

        # Initialise the UI
        self.init_ui()

    def init_ui(self) -> None:
        """
        Initialize the dialog user interface.
        """

        logger = logging.getLogger(__name__)
        # noinspection PyBroadException
        try:
            self.resize(800, 500)
            self.setWindowTitle("Table - {}".format(self.table.id))
            self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
            # Add icon
            icon_path = app_util.get_property("ProgramIconPath").replace('\\', '/')
            self.setWindowIcon(QtGui.QIcon(icon_path))

            # Create a vertical layout for the table view window
            self.table_window_layout = QtWidgets.QVBoxLayout(self)
            self.table_window_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
            self.table_window_layout.setObjectName(qt_util.from_utf8("mapVerticalLayout"))

            # Create a table for table
            self.table_table = QtWidgets.QTableWidget()
            self.table_window_layout.addWidget(self.table_table)
            self.table_table.setColumnCount(self.table.get_number_of_columns())
            self.table_table.setRowCount(self.table.get_number_of_rows())

            # Set Column Headers
            for i, table_field in enumerate(self.table.table_fields):
                item = QtWidgets.QTableWidgetItem()
                self.table_table.setHorizontalHeaderItem(i, item)
                self.table_table.horizontalHeaderItem(i).setText(table_field.name)

            # Customize Header Row
            self.table_table.horizontalHeader().setStyleSheet("::section { background-color: #d3d3d3 }")

            # Retrieve table add them to the table
            for i, row in enumerate(self.table.table_records):
                for j, value in enumerate(row.values):
                    item = QtWidgets.QTableWidgetItem("{}".format(value))
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.table_table.setItem(i, j, item)

            self.show()
        except Exception:
            message = "Error opening table window.  See the log file."
            logger.warning(message, exc_info=True)
            qt_util.warning_message_box(message)
