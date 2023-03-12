# GutterFrame - gutter parallel to command list, with color indicator for warning or error
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

from PyQt5 import QtGui, QtWidgets

from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

from geoprocessor.ui.core.GeoProcessorListModel import GeoProcessorListModel

import logging


class GutterFrame(QtWidgets.QFrame):
    """
    Class to implement a "gutter" to show to the right of the command list to show warnings and errors using
    a simple rectangle, similar to TSTool.
    """

    def __init__(self, gp_model: GeoProcessorListModel) -> None:
        """
        Initialize the Frame instance.

        Args:
            gp_model(GeoProcessorListModel): the list model for the main command list

        Returns:
            None
        """
        # Call the parent class.
        super().__init__()

        self.gp_model = gp_model

        self.color_outline = QtGui.QColor(0,0,0)  # Black
        self.color_failure = QtGui.QColor(255,0,0)  # Red
        self.color_warning = QtGui.QColor(255,255,0)  # Yellow

    def draw_marker_at_row(self, qp: QtGui.QPainter, row: int, status: CommandStatusType ) -> None:
        """
        Draw a warning or error marker centered on the row.

        Args:
            qp (QPainter): Painter that does the drawing.
            row (int): Row number corresponding ot command (0+).
            status (CommandStatusType): status that indicates color

        Returns:
            None.
        """
        debug = False
        if debug:
            logger = logging.getLogger(__name__)

        len_commands = len(self.gp_model.gp.commands)
        if len_commands == 0:
            y_fraction = 0.0
        else:
            y_fraction = float(row)/float(len_commands)
        gutter_height = self.height()
        gutter_width = self.width()

        marker_height = 5
        market_width = gutter_width

        # Marker is a color-filled rectangle with black outline.
        color_fill = self.color_outline  # Just in case logic below does not pick a color.
        if status is CommandStatusType.WARNING:
            # qp.setBackground(self.color_warning)
            color_fill = self.color_warning
        elif status is CommandStatusType.FAILURE:
            # qp.setBackgroundPen(self.color_failure)
            color_fill = self.color_failure

        x = 0
        height = 4  # Height of rectangle.
        height2 = height/2
        y = int(float(gutter_height)*y_fraction - height2)
        width = gutter_width
        if debug:
            logger.debug("Filling rectangle x=" + str(x) + " y=" + str(y) + " width=" + str(width) +
                         " height=" + str(height))
        # Fill the rectangle.
        qp.fillRect(x, y, width, height, color_fill)
        qp.setPen(self.color_outline)
        # Draw outline rectangle:
        # - not sure if can do in one step above
        # - decrement width so that outline is fully drawn
        qp.drawRect(x, y, (width - 1), height)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        """
        Repaint (redraw) the component.

        Returns:
            None.
        """
        debug = False
        if debug:
            logger = logging.getLogger(__name__)
            logger.debug("In paintEvent")

        if self.gp_model is None:
            # UI does not yet have commands to draw.
            return

        qp = QtGui.QPainter()
        qp.begin(self)

        # Update the numbered list and gutter with current errors and warnings.
        command_phase_type = CommandPhaseType.RUN
        for i in range(len(self.gp_model)):
            if command_phase_type is CommandPhaseType.INITIALIZATION:
                # Will be used after loading a command file, but have not run yet.
                command_status = self.gp_model.gp.commands[i].command_status.initialization_status
                if debug:
                    logger.debug("Command [" + str(i) + "] initialization status = " + str(command_status))
            elif command_phase_type is CommandPhaseType.DISCOVERY:
                command_status = self.gp_model.gp.commands[i].command_status.discovery_status
            elif command_phase_type is CommandPhaseType.RUN:
                # Will be used by default, after running commands.
                command_status = self.gp_model.gp.commands[i].command_status.run_status
                if debug:
                    logger.debug("Command [" + str(i) + "] run status = " + str(command_status))

            if command_status is CommandStatusType.FAILURE:
                self.draw_marker_at_row(qp, i, CommandStatusType.FAILURE)
            elif command_status is CommandStatusType.WARNING:
                self.draw_marker_at_row(qp, i, CommandStatusType.WARNING)

        qp.end()
