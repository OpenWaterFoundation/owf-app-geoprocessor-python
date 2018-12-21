# WriteGeoLayerToDelimitedFile

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.validator_util as validators

import logging

import os


class WriteGeoLayerToDelimitedFile(AbstractCommand):
    """
    Writes a GeoLayer to a delimited spatial data file.

    This command writes a layer to a delimited file. The delimited file can then be viewed within a GIS, moved within
    folders on the local computer, packaged for delivery, etc. The geometry is either held in one column in
    WKT (Well Known Text) format or in multiple columns in XY(Z) format. Each attribute field of the GeoLayer is
    written to the delimited file as a column. (The column name is the attribute name). Each row of the delimited
    file represents a single feature in the GeoLayer.

    Registered GeoLayers are stored as GeoLayer objects within the geoprocessor's GeoLayers list. Each GeoLayer has one
    feature type (point, line, polygon, etc.) and other data (an identifier, a coordinate reference system, etc). This
    function only writes one single GeoLayer to a single spatial data file in delimited file format. If the GeoLayer
    is anything other than 'POINT' data, the delimited file must hold the geometry data in WKT format
    (OutputGeometryFormat = `WKT`, see below).

    Command Parameters
    * GeoLayerID (str, required): the identifier of the GeoLayer to be written to a spatial data file in CSV format.
    * OutputFile (str, required): the pathname (relative or absolute) of the output spatial data file (do not include
        the .csv extension)
    * OutputCRS (str, EPSG code, optional): the coordinate reference system that the output spatial data file will be
        projected. By default, the output spatial data file will be projected to the GeoLayer's current CRS.
    * OutputGeometryFormat (str, optional): how the geometry will be displayed in the output CSV file. Default is
        `XY`. Available options are as follows:
        (1) `WKT`: the geometry will be held in one column in its Well Known Text (WKT) representation. This format
            can represent `POINT`, `LINE` or `POLYGON` data.
        (2) `XYZ`: the geometry will be held in the X, Y and Z representation (in multiple columns). This format can
            only represent `POINT` data.
        (3) `XY`: the geometry will be held in the X, and Y representation (in multiple columns). This format can
            only represent `POINT` data. The X column is first and then the Y column.
        (4) `YX`: the geometry will be held in the X, and Y representation (in multiple columns). This format can
        only represent `POINT` data. The Y column is first and then the X column.
    * OutputDelimiter (str, optional): the delimiter of the output CSV file. Default is `COMMA`.
        Available options are as follows:
        (1) `COMMA` (2) `SEMICOLON` (3) `TAB` (4) `SPACE`
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("OutputCRS", type("")),
        CommandParameterMetadata("OutputGeometryFormat", type("")),
        CommandParameterMetadata("OutputDelimiter", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "WriteGeoLayerToDelimitedFile"
        self.command_description = "Write GeoLayer to a file in delimited file format"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns: None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """

        warning = ""

        # Check that the appropriate parameters have a string value.
        for parameter in ['GeoLayerID', 'OutputFile']:

            # Get the parameter value.
            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)

            # Check that the parameter value is a non-empty, non-None string. If not, raise a FAILURE.
            if not validators.validate_string(parameter_value, False, False):
                message = "{} parameter has no value.".format(parameter)
                recommendation = "Specify the {} parameter.".format(parameter)
                warning += "\n" + message
                self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that optional parameter OutputGeometryFormat is either `WKT`, `XYZ`, `XY`, `YX` or None.
        pv_OutputGeometryFormat = self.get_parameter_value(parameter_name="OutputGeometryFormat",
                                                     command_parameters=command_parameters)
        acceptable_values = ["WKT", "XYZ", "XY", "YZ"]
        if not validators.validate_string_in_list(pv_OutputGeometryFormat, acceptable_values, none_allowed=True,
                                                  empty_string_allowed=False, ignore_case=True):
            message = "OutputGeometryFormat parameter value ({}) is not recognized.".format(pv_OutputGeometryFormat)
            recommendation = "Specify one of the acceptable values ({}) for the OutputGeometryFormat parameter.".format(
                acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that optional parameter OutputDelimiter is either `COMMA`, `SPACE`, `TAB`, `SEMICOLON` or None.
        pv_OutputDelimiter = self.get_parameter_value(parameter_name="OutputDelimiter",
                                                      command_parameters=command_parameters)
        acceptable_values = ["COMMA", "SEMICOLON", "TAB", "SPACE"]
        if not validators.validate_string_in_list(pv_OutputDelimiter, acceptable_values, none_allowed=True,
                                                  empty_string_allowed=False, ignore_case=True):
            message = "OutputDelimiter parameter value ({}) is not recognized.".format(pv_OutputDelimiter)
            recommendation = "Specify one of the acceptable values ({}) for the OutputDelimiter parameter.".format(
                acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def __should_write_geolayer(self, geolayer_id, output_file_abs, crs, output_geom_format):
        """
        Checks the following:
        * the ID of the GeoLayer is an existing GeoLayer ID
        * the output folder is a valid folder
        * the feature geometry is "POINT" if the geometry format parameter format is not "WKT"
        * the CRS is a valid CRS code

        Args:
            geolayer_id (str): the ID of the GeoLayer to be written
            output_file_abs (str): the full pathname (absolute) to the output CSV file (without the extension)
            crs (str): the desired coordinate reference system of the output spatial data
            output_geom_format (str): the geometry format to display the spatial data into CSV format

        Returns:
             Boolean. If TRUE, the GeoLayer should be written. If FALSE, at least one check failed and the GeoLayer
                should not be written.
       """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the GeoLayer ID is not an existing GeoLayer ID, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsGeoLayerIdExisting", "GeoLayerID", geolayer_id, "FAIL"))

        # If the GeoLayerID exists, continue with the checks.
        if False not in should_run_command:

            # If the output_geometry_format is not 'WKT', continue with the checks.
            if not output_geom_format.upper() == "WKT":

                # If the GeoLayer does not have POINT geometry, raise a FAILURE.
                should_run_command.append(validators.run_check(self, "DoesGeoLayerIdHaveCorrectGeometry",
                                                               "GeoLayerID", geolayer_id,
                                                               "FAIL", other_values=[["Point"]]))

            # Get the CRS of the input GeoLayer, if the parameter value for OutputCRS is None.
            if crs is None:
                crs = self.command_processor.get_geolayer(geolayer_id).get_crs()

            # If the CRS is not a valid CRS code, raise a FAILURE.
            should_run_command.append(validators.run_check(self, "IsCRSCodeValid", "OutputCRS", crs, "FAIL"))

        # If the folder of the OutputFile file path is not a valid folder, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "DoesFilePathHaveAValidFolder", "OutputFile",
                                                       output_file_abs, "FAIL"))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self):
        """
        Run the command. Write the GeoLayer to a delimited file.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the command parameter values.
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_OutputFile = self.get_parameter_value("OutputFile")
        pv_OutputCRS = self.get_parameter_value("OutputCRS")
        pv_OutputGeometryFormat = self.get_parameter_value("OutputGeometryFormat", default_value="XY").upper()
        pv_OutputDelimiter = self.get_parameter_value("OutputDelimiter", default_value="COMMA").upper()

        # Convert the OutputFile parameter value relative path to an absolute path and expand for ${Property} syntax
        output_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_OutputFile, self)))

        # Get the filename of the OutputFile with the path but without the extension.
        path, filename= os.path.split(output_file_absolute)
        path = os.path.split(output_file_absolute)[0]
        filename_wo_ext_path = os.path.join(path, os.path.splitext(filename)[0])

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_write_geolayer(pv_GeoLayerID, filename_wo_ext_path, pv_OutputCRS, pv_OutputGeometryFormat):

            try:
                # Get the GeoLayer
                geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)

                # Get the current coordinate reference system (in EPSG code) of the current GeoLayer
                if pv_OutputCRS is None:
                    pv_OutputCRS = geolayer.get_crs()

                # Write the GeoLayer to a delimited spatial data file.
                qgis_util.write_qgsvectorlayer_to_delimited_file(geolayer.qgs_vector_layer,
                                                                 filename_wo_ext_path,
                                                                 pv_OutputCRS,
                                                                 pv_OutputGeometryFormat,
                                                                 pv_OutputDelimiter)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error writing GeoLayer {} to delimited file format.".format(pv_GeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.error(message, exc_info=True)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
