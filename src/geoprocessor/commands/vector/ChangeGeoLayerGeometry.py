# ChangeGeoLayerGeometry - command to change a GeoLayer's geometry to new geometry
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


class ChangeGeoLayerGeometry(AbstractCommand):
    """
    Change a VectorGeoLayer's geometry to a new geometry.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("InputGeoLayerID", str),
        CommandParameterMetadata("OutputGeometry", str),
        CommandParameterMetadata("OutputGeoLayerID", str),
        CommandParameterMetadata("IfGeoLayerIDExists", str),
        CommandParameterMetadata("TemporaryFolder", str)]

    # Command metadata for command editor display.
    __command_metadata = dict()
    __command_metadata['Description'] = (
        "Change a GeoLayer's geometry to new geometry and create a new layer.\n"
        "For example, change line (polyline) layer to polygon layer."
    )
    __command_metadata['EditorType'] = "Simple"

    # Command Parameter Metadata.
    __parameter_input_metadata = dict()

    # InputGeoLayerID
    __parameter_input_metadata['InputGeoLayerID.Description'] = 'input GeoLayer identifier'
    __parameter_input_metadata['InputGeoLayerID.Label'] = "Input GeoLayerID"
    __parameter_input_metadata['InputGeoLayerID.Required'] = True
    __parameter_input_metadata['InputGeoLayerID.Tooltip'] = "Input GeoLayer identifier."

    # OutputGeometry
    __parameter_input_metadata['OutputGeometry.Description'] = "output geometry type"
    __parameter_input_metadata['OutputGeometry.Label'] = "Output geometry"
    __parameter_input_metadata['OutputGeometry.Required'] = True
    __parameter_input_metadata['OutputGeometry.Tooltip'] = "The geometry type for the output GeoLayer."
    __parameter_input_metadata['OutputGeometry.Values'] = ["", "Point", "LineString", "Polygon"]

    # OutputGeoLayerID
    __parameter_input_metadata['OutputGeoLayerID.Description'] = "the output GeoLayerID"
    __parameter_input_metadata['OutputGeoLayerID.Label'] = "Output GeoLayerID"
    __parameter_input_metadata['OutputGeoLayerID.Required'] = True
    __parameter_input_metadata['OutputGeoLayerID.Tooltip'] = "The output GeoLayerID."

    # IfGeoLayerIDExists
    __parameter_input_metadata['IfGeoLayerIDExists.Description'] = "action if output layer exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID exists"
    __parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = (
        "The action that occurs if the GeoLayerID already exists within the GeoProcessor.\n"
        "Replace : The existing GeoLayer within the GeoProcessor is overwritten with the new"
        "GeoLayer. No warning is logged.\n"
        "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new "
        "GeoLayer. A warning is logged. \n"
        "Warn : The new GeoLayer is not created. A warning is logged. \n"
        "Fail : The new GeoLayer is not created. A fail message is logged.")
    __parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
    __parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"

    # TemporaryFolder
    __parameter_input_metadata['TemporaryFolder.Description'] = "temporary location for output files"
    __parameter_input_metadata['TemporaryFolder.Label'] = "Temporary files folder"
    __parameter_input_metadata['TemporaryFolder.Tooltip'] = \
        "Folder for temporary output layer files, useful for troubleshooting. See the documentation."
    __parameter_input_metadata['TemporaryFolder.Value.Default'] = "default temporary folder directory"
    __parameter_input_metadata['TemporaryFolder.FileSelector.Title'] = \
        "Select the folder for temporary files"
    __parameter_input_metadata['TemporaryFolder.FileSelector.SelectFolder'] = True
    __parameter_input_metadata['TemporaryFolder.FileSelector.Type'] = "Write"

    # TODO smalers 2020-07-07 evaluate whether to enable the parameter:
    #  - by default leave temporary files so they can be reviewed.
    # RemoveTemporaryFiles
    # self.parameter_input_metadata['RemoveTemporaryFiles.Description'] = "remove temporary files"
    # self.parameter_input_metadata['RemoveTemporaryFiles.Label'] = "Remove temporary files"
    # self.parameter_input_metadata['RemoveTemporaryFiles.Tooltip'] = \
    #     "True (default): remove the temporary files created behind the scenes.\n" \
    #     "False: leave the files so that they can be reviewed."
    # self.parameter_input_metadata['RemoveTemporaryFiles.Value.Default'] = "True"
    # self.parameter_input_metadata['RemoveTemporaryFiles.Values'] = ["", "True", "False"]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data.
        super().__init__()
        self.command_name = "ChangeGeoLayerGeometry"
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
        Returns:
            None.
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

        # Check that optional parameter IfGeoLayerIDExists is either `Replace`, `Warn`, `Fail` or None.
        # noinspection PyPep8Naming
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        acceptable_values = ["Replace", "Warn", "Fail", "ReplaceAndWarn"]
        if not validator_util.validate_string_in_list(pv_IfGeoLayerIDExists, acceptable_values, none_allowed=True,
                                                      empty_string_allowed=True, ignore_case=True):
            message = "IfGeoLayerIDExists parameter value ({}) is not recognized.".format(pv_IfGeoLayerIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfGeoLayerIDExists parameter.".format(
                acceptable_values)
            warning_message += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
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

    def check_runtime_data(self, input_geolayer_id: str) -> bool:
        """
        Checks the following:
        * the ID of the input GeoLayer is an existing GeoLayer ID
        Args:
            input_geolayer_id: the ID of the input GeoLayer
        Returns:
             Boolean. If TRUE, the GeoLayer should be split. If FALSE, at least one check failed and the GeoLayer
                should not be split.
        """

        logger = logging.getLogger(__name__)
        # List of Boolean values. The Boolean values correspond to the results of the following tests.
        # If TRUE, the test confirms that the command should be run.
        should_run_command = list()

        # If the input GeoLayerID is not an existing GeoLayerID, raise a FAILURE.
        should_run_command.append(validator_util.run_check(self, "IsGeoLayerIDExisting", "InputGeoLayerID",
                                                           input_geolayer_id, "FAIL"))

        # If the input GeoLayer exists, continue with the checks.
        if False not in should_run_command:

            # Get the input GeoLayer object.
            input_geolayer = self.command_processor.get_geolayer(input_geolayer_id)

            # Get the attribute names of the input GeoLayer.
            list_of_attributes = input_geolayer.get_attribute_field_names()
            for i_attribute_name in list_of_attributes:
                logger.info('Input layer has attribute "' + str(i_attribute_name) + '"')

            # Return the Boolean to determine if the process should be run.
            if False in should_run_command:
                return False
            else:
                return True
        else:
            logger.info('Process can be run')
            return True

    def run_command(self) -> None:
        """
        Run the command.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values.

        # Get the 'Input GeoLayerID' parameter.
        # noinspection PyPep8Naming
        pv_InputGeoLayerID = self.get_parameter_value("InputGeoLayerID")
        # noinspection PyPep8Naming
        pv_OutputGeoLayerID = self.get_parameter_value("OutputGeoLayerID")
        # noinspection PyPep8Naming
        pv_OutputGeometry = self.get_parameter_value("OutputGeometry")
        output_geometry_upper = pv_OutputGeometry.upper()
        # noinspection PyPep8Naming
        pv_TemporaryFolder = self.get_parameter_value("TemporaryFolder")

        # TODO smalers 2020-11-17 evaluate whether need to deal with temporary files.
        # Get the temporary folder based on TemporaryFolder parameter.
        # if pv_TemporaryFolder is not None and pv_TemporaryFolder != "":
        #     # Convert the TemporaryFolder parameter value to an absolute path and expand for ${Property} syntax.
        #     temp_folder_absolute = io_util.verify_path_for_os(
        #         io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
        #                                  self.command_processor.expand_parameter_value(
        #                                      pv_TemporaryFolder, self)))
        # else:
        #     # If using the default temp directory from environment variables create a temp folder.
        #     temp_folder_absolute = tempfile.gettempdir()
        #     temp_folder_absolute += "/geoprocessor-outputfiles"

        # Create logger
        logger = logging.getLogger(__name__)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(pv_InputGeoLayerID):
            # noinspection PyBroadException
            try:
                # Get the Input GeoLayer and geometry.

                input_geolayer = self.command_processor.get_geolayer(pv_InputGeoLayerID)
                input_geometry = input_geolayer.get_geometry()
                input_geometry_upper = input_geometry.upper()
                logger.info("Input geometry for {} layer is {}.".format(pv_InputGeoLayerID, input_geometry))

                # Run the necessary QGIS algorithm.
                # REF: https://docs.qgis.org/
                # 2.8/en/docs/user_manual/processing_algs/qgis/vector_general_tools.html#split-vector-layer
                # TODO smalers 2020-07-07 the QGIS documentation is bad.

                # See:
                # https://www.geodose.com/2019/10/pyqgis-tutorial-geometry-conversion.html

                algorithm = None
                algorithm_parameters = {}
                if input_geometry_upper == "POINT":
                    # Input geometry is point.
                    if output_geometry_upper == "LINESTRING":
                        # Change points to lines.
                        algorithm = "qgis:pointstopath"
                        # algorithm_parameters = {'INPUT': input_file, 'ORDER_FIELD': 'fid', OUTPUT: output_file}

                        self.warning_count += 1
                        message = "Changing GeoLayer {} from {} geometry to {} geometry is not supported.".format(
                            pv_InputGeoLayerID, input_geometry, pv_OutputGeometry)
                        recommendation = "Software needs to be updated."
                        self.logger.warning(message, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                        recommendation))
                    elif output_geometry_upper == "POLYGON":
                        # Change points to polygons - is this possible?
                        self.warning_count += 1
                        message = "Changing GeoLayer {} from {} geometry to {} geometry is not supported.".format(
                            pv_InputGeoLayerID, input_geometry, pv_OutputGeometry)
                        recommendation = "Software needs to be updated."
                        self.logger.warning(message, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                        recommendation))
                    else:
                        # Unhandled.
                        self.warning_count += 1
                        message = "Changing GeoLayer {} from {} geometry to {} geometry is not supported.".format(
                            pv_InputGeoLayerID, input_geometry, pv_OutputGeometry)
                        recommendation = "Software needs to be updated."
                        self.logger.warning(message, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                        recommendation))
                elif input_geometry_upper == "LINESTRING":
                    # Input geometry is line.
                    if output_geometry_upper == "POINT":
                        # Change lines to point.
                        algorithm = "saga:convertlinestopoints"
                        # algorithm_parameters = {"LINES":input_file, "POINTS": output_file}

                        self.warning_count += 1
                        message = "Changing GeoLayer {} from {} geometry to {} geometry is not supported.".format(
                            pv_InputGeoLayerID, input_geolayer, pv_OutputGeometry)
                        recommendation = "Software needs to be updated."
                        self.logger.warning(message, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                        recommendation))
                    elif output_geometry_upper == "POLYGON":
                        # Change lines to polygons:
                        # - a simple example using polygonize did not work so need more evaluation
                        alg_to_use = 1
                        if alg_to_use == 1:
                            # https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/
                            #     vectorgeometry.html#lines-to-polygons
                            algorithm = "qgis:linestopolygons"
                            algorithm_parameters = {
                                'INPUT': input_geolayer.qgs_layer,
                                'OUTPUT': "memory:"
                            }
                        elif alg_to_use == 2:
                            # https://docs.qgis.org/3.16/en/docs/user_manual/processing_algs/qgis/
                            #     vectorgeometry.html#polygonize
                            # TODO smalers 2020-11-17 the following does not seem to work?
                            algorithm = "qgis:polygonize"
                            algorithm_parameters = {
                                'INPUT': input_geolayer.qgs_layer,
                                'KEEP_FIELDS': True,
                                'OUTPUT': "memory:"
                            }
                    else:
                        # Unhandled.
                        self.warning_count += 1
                        message = "Changing GeoLayer {} from {} geometry to {} geometry is not supported.".format(
                            pv_InputGeoLayerID, input_geometry, pv_OutputGeometry)
                        recommendation = "Software needs to be updated."
                        self.logger.warning(message, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                        recommendation))
                elif input_geometry_upper == "POLYGON":
                    # Input geometry is polygon.
                    if output_geometry_upper == "POINT":
                        # Change polygons to points.

                        self.warning_count += 1
                        message = "Changing GeoLayer {} from {} geometry to {} geometry is not supported.".format(
                            pv_InputGeoLayerID, input_geometry, pv_OutputGeometry)
                        recommendation = "Software needs to be updated."
                        self.logger.warning(message, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                        recommendation))
                    elif output_geometry_upper == "LINESTRING":
                        # Change polygons to lines.

                        self.warning_count += 1
                        message = "Changing GeoLayer {} from {} geometry to {} geometry is not supported.".format(
                            pv_InputGeoLayerID, input_geometry, pv_OutputGeometry)
                        recommendation = "Software needs to be updated."
                        self.logger.warning(message, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                        recommendation))
                    else:
                        # Unhandled.
                        self.warning_count += 1
                        message = "Changing GeoLayer {} from {} geometry to {} geometry is not supported.".format(
                            pv_InputGeoLayerID, input_geometry, pv_OutputGeometry)
                        recommendation = "Software needs to be updated."
                        self.logger.warning(message, exc_info=True)
                        self.command_status.add_to_log(CommandPhaseType.RUN,
                                                       CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                        recommendation))
                else:
                    # Not handled.
                    self.warning_count += 1
                    message = "Changing GeoLayer {} from {} geometry to {} geometry is not supported.".format(
                        pv_InputGeoLayerID, input_geometry, pv_OutputGeometry)
                    recommendation = "Software needs to be updated."
                    self.logger.warning(message, exc_info=True)
                    self.command_status.add_to_log(CommandPhaseType.RUN,
                                                   CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                    recommendation))

                if algorithm is not None:
                    # Call runAlgorithm with the input from above.
                    # This should result in output GeoLayer file written to the OUTPUT directory.
                    # TODO smalers 2020-11-17 evaluate:
                    #  feedback=self)
                    logger.info("Changing '{}' layer geometry using algorithm '{}' and parameters '{}'".format(
                        pv_InputGeoLayerID, algorithm, algorithm_parameters))
                    feedback_handler = QgisAlgorithmProcessingFeedbackHandler(self)
                    converted_output = qgis_util.run_processing(processor=self.command_processor.qgis_processor,
                                                                algorithm=algorithm,
                                                                algorithm_parameters=algorithm_parameters,
                                                                feedback_handler=feedback_handler)
                    self.warning_count += feedback_handler.get_warning_count()
                    output_qgs_layer = converted_output['OUTPUT']

                    # noinspection PyBroadException
                    # Use the ID for the name until more control is added.
                    # Currently only support default output GeoLayerID.
                    new_geolayer = VectorGeoLayer(geolayer_id=pv_OutputGeoLayerID,
                                                  qgs_vector_layer=output_qgs_layer,
                                                  name=pv_OutputGeoLayerID,
                                                  description=pv_OutputGeoLayerID,
                                                  input_path_full=GeoLayer.SOURCE_MEMORY,
                                                  input_path=GeoLayer.SOURCE_MEMORY)
                    self.command_processor.add_geolayer(new_geolayer)

                    # TODO smalers 2020-07-12 need to enable removing the temporary split files,
                    # but workflow will neeed to copy or read/write to another location.
                    # @jurentie
                    # Remove files if specified in parameters.
                    # TODO @jurentie figure out how to delete files after using them...
                    # remove_files = self.get_parameter_value("RemoveTemporaryFiles")
                    # files = glob.glob(temp_directory + "/*")
                    # print(files)
                    # if remove_files == None:
                    #     # Remove all files from directory.
                    #     for f in files:
                    #         os.remove(f)
                    #     os.rmdir(temp_directory)

                    # Do some final checks to help confirm that the conversion was successful.

                    if input_geometry_upper == "LINESTRING":
                        if output_geometry_upper == "POLYGON":
                            num_input_features = qgis_util.get_layer_feature_count(input_geolayer.qgs_layer)
                            num_output_features = qgis_util.get_layer_feature_count(output_qgs_layer)
                            if num_input_features != num_output_features:
                                self.warning_count += 1
                                message = "Input layer {} has {} features but output layer {} has {} features.  " \
                                          "Expecting the same number of features".format(
                                              pv_InputGeoLayerID, num_input_features, pv_OutputGeoLayerID,
                                              num_output_features)
                                recommendation =\
                                    "Check the log file for details.  May be an algorithm functionality issue."
                                self.logger.warning(message, exc_info=True)
                                self.command_status.add_to_log(CommandPhaseType.RUN,
                                                               CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                                recommendation))

            except Exception:
                # Raise an exception if an unexpected error occurs during the process.
                self.warning_count += 1
                message = "Unexpected converting GeoLayer {} geometry.".format(pv_InputGeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred.
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        else:
            # Set command status type as SUCCESS if there are no errors.
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
