# SetGeoLayerCRS - command to set GeoLayer coordinate reference system (CRS)
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

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandError import CommandError
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType
from geoprocessor.core.GeoLayer import GeoLayer
from geoprocessor.core.QGISAlgorithmProcessingFeedbackHandler import QgisAlgorithmProcessingFeedbackHandler
from geoprocessor.core.VectorGeoLayer import VectorGeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.validator_util as validator_util

import logging

# from plugins.processing.tools import general


class SetGeoLayerCRS(AbstractCommand):
    """
    Sets a GeoLayer's coordinate reference system (CRS).

    * If the GeoLayer already has a CRS, this command will reset the GeoLayer's CRS to the new CRS.

    Command Parameters:

    * GeoLayerID (str, required): the ID of the input GeoLayer, the layer to set the CRS.
    * CRS (str, EPSG/ESRI code, required): the CRS to set for the GeoLayer.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("CRS", type(""))]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = "Set the coordinate reference system (CRS) of a GeoLayer."
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()
    # GeoLayerID
    __parameter_input_metadata['GeoLayerID.Description'] = "GeoLayer identifier"
    __parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
    __parameter_input_metadata['GeoLayerID.Required'] = True
    __parameter_input_metadata['GeoLayerID.Tooltip'] = "The ID of the GeoLayer."
    # CRS
    __parameter_input_metadata['CRS.Description'] = "coordinate references system"
    __parameter_input_metadata['CRS.Label'] = "CRS"
    __parameter_input_metadata['CRS.Required'] = True
    __parameter_input_metadata['CRS.Tooltip'] = (
        "The coordinate reference system of the GeoLayer. "
        "EPSG or ESRI code format required (e.g. EPSG:4326, EPSG:26913, ESRI:102003).")

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data.
        super().__init__()
        self.command_name = "SetGeoLayerCRS"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display.
        self.command_metadata = self.__command_metadata

        # Command Parameter Metadata.
        self.parameter_input_metadata = self.__parameter_input_metadata

        # Class data.
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters: dict) -> None:
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns: None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning_message = ""

        # Check that required parameters are non-empty, non-None strings.
        required_parameters = command_util.get_required_parameter_names(self)
        for parameter in required_parameters:
            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)
            if not validator_util.validate_string(parameter_value, False, False):
                message = "Required {} parameter has no value.".format(parameter)
                recommendation = "Specify the {} parameter.".format(parameter)
                warning_message += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            self.logger.warning(warning_message)
            raise CommandParameterError(warning_message)
        else:
            # Refresh the phase severity.
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, geolayer_id: str, crs_code: str) -> bool:
        """
        Checks the following:
         * The ID of the input GeoLayer is an actual GeoLayer (if not, log an error message & do not continue.)
         * The CRS is a valid coordinate reference system code.
         * The CRS is difference than the GeoLayer's CRS.

        Args:
            geolayer_id (str): the ID of the GeoLayer to add the new attribute
            crs_code (str): the CRS to set for the GeoLayer (EPSG or ESRI code)

        Returns:
            set_crs: Boolean. If TRUE, the CRS should be set. If FALSE, a check has failed & the CRS should not be set.
        """

        # Boolean to determine if the CRS should be set. Set to TRUE until one or many checks fail.
        set_crs = True

        # Boolean to determine if the input GeoLayer id is a valid GeoLayer ID. Set to TRUE until proved False.
        input_geolayer_exists = True

        if self.command_processor.get_geolayer(geolayer_id) is None:
            # If the input GeoLayer does not exist, FAILURE.
            set_crs = False
            input_geolayer_exists = False
            self.warning_count += 1
            message = 'The input GeoLayer ID ({}) does not exist.'.format(geolayer_id)
            recommendation = 'Specify a valid GeoLayerID.'
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        if qgis_util.parse_qgs_crs(crs_code) is None:
            # If the input CRS code is not a valid code, FAILURE.
            set_crs = False
            self.warning_count += 1
            message = 'The input CRS ({}) is not a valid CRS code.'.format(crs_code)
            recommendation = 'Specify a valid CRS code (EPSG codes are an approved format).'
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN,
                                           CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # If the input CRS code is that same as the GeoLayer's current CRS, raise a WARNING.
        if input_geolayer_exists and self.command_processor.get_geolayer(geolayer_id).get_crs_code():
            if crs_code.upper() == self.command_processor.get_geolayer(geolayer_id).get_crs_code().upper():
                set_crs = False
                self.warning_count += 1
                message = 'The input GeoLayer ({}) already is projected to the input' \
                          ' CRS ({}).'.format(geolayer_id, crs_code)
                recommendation = 'The SetGeoLayerCRS command will not run. Specify a different CRS code.'
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING, message, recommendation))

        # Return the Boolean to determine if the crs should be set. If TRUE, all checks passed.
        # If FALSE, one or many checks failed.
        return set_crs

    def run_command(self) -> None:
        """
        Run the command. Set the GeoLayer coordinate reference system.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        # noinspection PyPep8Naming
        pv_CRS = self.get_parameter_value("CRS")

        # Convert the pv_GeoLayerID parameter to expand for ${Property} syntax.
        # noinspection PyPep8Naming
        pv_GeoLayerID = self.command_processor.expand_parameter_value(pv_GeoLayerID, self)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(pv_GeoLayerID, pv_CRS):
            # Run the process.
            # noinspection PyBroadException
            try:
                # Get the input GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Check if the input GeoLayer already has an assigned CRS.
                if input_geolayer.get_crs_code():
                    # Reproject the GeoLayer.
                    alg_parameters = {
                        "INPUT": input_geolayer.qgs_layer,
                        "TARGET_CRS": pv_CRS,
                        "OUTPUT": "memory:"
                    }
                    feedback_handler = QgisAlgorithmProcessingFeedbackHandler(self)
                    reprojected_output = qgis_util.run_processing(processor=self.command_processor.qgis_processor,
                                                                  algorithm="qgis:reprojectlayer",
                                                                  algorithm_parameters=alg_parameters,
                                                                  feedback_handler=feedback_handler)
                    self.warning_count += feedback_handler.get_warning_count()

                    # Create a new GeoLayer and add it to the GeoProcessor's geolayers list.

                    # In QGIS 2 the reprojected["OUTPUT"] returned the full file pathname of the memory output layer
                    # (saved in a QGIS temporary folder)
                    # qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_file(reprojected["OUTPUT"])
                    # new_geolayer = VectorGeoLayer(input_geolayer.id, qgs_vector_layer, GeoLayer.SOURCE_MEMORY)

                    # In QGIS 3 the reprojected["OUTPUT"] returns the QGS vector layer object:
                    # - use the same name and description as the original
                    new_geolayer = VectorGeoLayer(geolayer_id=input_geolayer.id,
                                                  qgs_vector_layer=reprojected_output["OUTPUT"],
                                                  name=input_geolayer.name,
                                                  description=input_geolayer.description,
                                                  input_path_full=GeoLayer.SOURCE_MEMORY,
                                                  input_path=GeoLayer.SOURCE_MEMORY)
                    self.command_processor.add_geolayer(new_geolayer)

                else:
                    alg_parameters = {
                        "INPUT": input_geolayer.qgs_vector_layer,
                        "CRS": pv_CRS
                    }
                    feedback_handler = QgisAlgorithmProcessingFeedbackHandler(self)
                    reprojected_output = qgis_util.run_processing(processor=self.command_processor.qgis_processor,
                                                                  algorithm="qgis:definecurrentprojection",
                                                                  algorithm_parameters=alg_parameters,
                                                                  feedback_handler=feedback_handler)
                    self.warning_count += feedback_handler.get_warning_count()

            except Exception:
                # Raise an exception if an unexpected error occurs during the process.
                self.warning_count += 1
                message = "Unexpected error setting CRS ({}) of GeoLayer ({})".format(pv_CRS, pv_GeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred.
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
