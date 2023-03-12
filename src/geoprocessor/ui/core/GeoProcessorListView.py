# GeoProcessorListView - class to serve as derived QListView for list of Command
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

import logging

from PyQt5 import QtCore, QtGui, QtWidgets


class GeoProcessorListView(QtWidgets.QListView):
    """
    View for GeoProcessor command list.
    The model is used by the CommandListWidget's QListWidget to interact with the Command list.

    See "Model/View Programming":  https://doc.qt.io/qt-5/model-view-programming.html
    See "QListView":  https://doc.qt.io/qtforpython/PySide2/QtWidgets/QListView.html

    Useful methods on a view are:

    currentIndex() - returns a QModelIndex of the current row (one last selected)
    selectedIndexes() - returns a list of QModelIndex for selected rows
    sizeHintForRow() - get the row height size hint, useful for synchronizing parallel lists
    """

    def __init__(self, parent):
        """
        Initialize an instance of the view.
        """
        super(GeoProcessorListView, self).__init__(parent)

        # Set the selection model to ensure that selection of a cell selects the row.
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        """
        Re-implement to suppress right click from selecting items.

        Args:
            event: mouse press event

        Returns:
            None.
        """
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.RightButton:
                return
            else:
                super(GeoProcessorListView, self).mousePressEvent(event)
