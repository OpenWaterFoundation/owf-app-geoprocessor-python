# GeoLayerView - Class to hold a layer and its symbology
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


import json
import logging

import geoprocessor.util.io_util as io_util
from pathlib import Path


class GeoLayerViewEventHandler(object):
    """
    The GeoLayerViewEventHandler class represents a handler for UI event that should be implemented to
    interact with the layer view.
    """
    def __init__(self,
                 event_type: str,
                 name: str = "",
                 description: str = "",
                 properties: dict = None) -> None:
        """
        Construct a new GeoLayerViewEventHandler,
        which represents a UI event handler that should be implemented in application code.

        Args:
            event_type (str): Event type, need to standardize.
            name (str): Event name.
            description (str): Event description.
            properties (dict): Properties for the event handler.
        """
        # Name for the event.
        self.name: str = name

        # Description for the event.
        self.description: str = description

        # Event type, currently a string, may change to enumeration.
        self.event_type: str = event_type

        # Whether the event has a visualization:
        # - this is determined by examining the event configuration file and finding at least one click event action
        self.has_visualization: bool or None = None

        # Properties for the event.
        self.properties: {} = None
        if properties is None:
            # Initialize an empty dictionary.
            self.properties = {}
        else:
            # Use the dictionary that was passed in.
            self.properties = properties

    def determine_has_visualization(self, map_config_path):
        """
        Determine whether there are any visualizations enabled for click events.
        This requires reading the event configuration data file and checking for non-empty action list.

        Args:
            map_config_path (str): path to the map configuration file, needed if the event configuration
                path is relative

        Returns:
            True if any click event handlers for the layer contain visualizations, False if not.
        """
        logger = logging.getLogger(__name__)

        # Default to false.
        self.has_visualization = False

        if self.event_type.upper() != 'CLICK':
            # Not a click event so no visualization.
            logger.info("Event handler type ({}) is not 'Click' - not checking for visualizations.".format(
                self.event_type))
            return self.has_visualization
        else:
            logger.info("Event handler type ({}) is 'Click' - checking for visualization actions.".format(
                self.event_type))

        try:
            event_config_path = self.properties['eventConfigPath']
        except KeyError:
            # Property is not found:
            # - no visualization
            logger.info("Event handler has no 'eventConfigPath' property - not checking for visualizations.")
            self.has_visualization = False
            return

        # Get the absolute path for the configuration file:
        # - if relative, it is relative to the map configuration file.
        map_config_folder = Path(map_config_path).parent
        event_config_path_full = io_util.to_absolute_path(map_config_folder, event_config_path)
        logger.info("Event handler configuration file full path is: {}".format(event_config_path_full))
        # TODO smalers 2020 evaluate whether to handle exception and throw.
        # logger.info("Event configuration file '{}' is not readable.".format(event_config_path_full))
        # Read the JSON file into an object.
        event_config_path_full2 = Path(event_config_path_full)
        if event_config_path_full2.exists():
            with open(event_config_path_full) as f:
                json_data = json.load(f)
        else:
            message = "Event configuration file does not exist: {}.".format(event_config_path_full)
            logger.warning(message)
            raise FileNotFoundError(message)

        # Use the data to determine whether a visualization is enabled as an action.
        try:
            actions = json_data['actions']
            # Currently any actions are assumed to indicate a visualization.
            if len(actions) > 0:
                logger.info("Detected event actions for layer.")
                self.has_visualization = True
        except KeyError:
            # No actions in the file.
            logger.info("No event actions are configured for layer.")
            self.has_visualization = False

        # Return the final determined value.
        return self.has_visualization

    def to_json(self):
        """
        Return dictionary of class data to support JSON serialization using json package.
        """
        return {
            "eventType": self.event_type,
            "name": self.name,
            "description": self.description,
            "hasVisualization": self.has_visualization,
            "properties": self.properties
        }
