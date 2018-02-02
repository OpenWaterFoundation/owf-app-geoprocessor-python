# ReadGeoLayerFromDelimitedFile

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.commandUtil as command_util
import geoprocessor.util.qgisUtil as qgis_util
import geoprocessor.util.ioUtil as io_util
import geoprocessor.util.validatorsUtil as validators

import logging


class ReadGeoLayerFromDelimitedFile(AbstractCommand):

    """
    Reads a GeoLayer from a delimited spatial data file.

    This command reads a layer from a delimited file and creates a GeoLayer object within the
    geoprocessor. The GeoLayer can then be accessed in the geoprocessor by its identifier and further processed.

    GeoLayers read from a delimited file hold point features. It is required that the delimited file has a column
     representing each feature's x coordinates and a column representing each feature's y coordinates. The other
     columns within the delimited file, if any, are included in the GeoLayer's attribute table as individual attributes.

    In order for the geoprocessor to use and manipulate spatial data files, GeoLayers are instantiated as
    `QgsVectorLayer <https://qgis.org/api/classQgsVectorLayer.html>`_ objects.

    Command Parameters
    * DelimitedFile (str, required): The path (relative or absolute) to the delimited file to be read.
    * Delimiter (str, required): The delimiter symbol used in the delimited file. Often times a comma.
    * XColumnName (str, optional): The name of the delimited file column that holds the x coordinate data.
    * YColumnName(str, optional): The name of the delimited file column that holds the y coordinate data.
    * WKTColumnName(str, optional): The name of the delimited file column that holds teh WKT formatted geometries.
    * CRS (str, required): The coordinate reference system associated with the X and Y coordinates (in EPSG code).
    * GeoLayerID (str, optional): the GeoLayer identifier. If None, the spatial data filename (without the .geojson
        extension) will be used as the GeoLayer identifier. For example: If GeoLayerID is None and the absolute
        pathname to the spatial data file is C:/Desktop/Example/example_file.geojson, then the GeoLayerID will be
        `example_file`.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the CopiedGeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("DelimitedFile", type("")),
        CommandParameterMetadata("Delimiter", type("")),
        CommandParameterMetadata("GeometryType", type("")),
        CommandParameterMetadata("XColumnName", type("")),
        CommandParameterMetadata("YColumnName", type("")),
        CommandParameterMetadata("WKTColumnName", type("")),
        CommandParameterMetadata("CRS", type("")),
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super(ReadGeoLayerFromDelimitedFile, self).__init__()
        self.command_name = "ReadGeoLayerFromDelimitedFile"
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
        for parameter in ['DelimitedFile', 'Delimiter', 'CRS', 'GeoLayerID']:

            # Get the parameter value.
            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)

            # Check that the parameter value is a non-empty, non-None string. If not, raise a FAILURE.
            if not validators.validate_string(parameter_value, False, False):

                message = "{} parameter has no value.".format(parameter)
                recommendation = "Specify the {} parameter.".format(parameter)
                warning += "\n" + message
                self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that the GeometryType is either `XY` or `WKT`.
        pv_GeometryType = self.get_parameter_value(parameter_name="GeometryType", command_parameters=command_parameters)
        acceptable_values = ["WKT", "XY"]

        if not validators.validate_string_in_list(pv_GeometryType, acceptable_values, none_allowed=False,
                                                  empty_string_allowed=False, ignore_case=True):

            message = "GeometryType parameter value ({}) is not recognized.".format(pv_GeometryType)
            recommendation = "Specify one of the acceptable values ({}) for the GeometryType parameter.".format(
                acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                           CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that the correct ColumnName variables are correct.
        else:

            # If the pv_GeometryType is "WKT" then check that the WKTColumnName has a string value.
            if pv_GeometryType is not None and pv_GeometryType.upper() == "WKT":

                # Check that the parameter value is a non-None string. If not, raise a FAILURE.
                if not validators.validate_string("WKTColumnName", False, True):
                    message = "WKTColumnName parameter has no value."
                    recommendation = "Specify the WKTColumnName parameter."
                    warning += "\n" + message
                    self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                                   CommandLogRecord(command_status_type.FAILURE, message,
                                                                    recommendation))

            else:

                # Check that the appropriate parameters have a string value.
                for parameter in ['XColumnName', 'YColumnName']:

                    # Get the parameter value.
                    parameter_value = self.get_parameter_value(parameter_name=parameter,
                                                               command_parameters=command_parameters)

                    # Check that the parameter value is a non-None string. If not, raise a FAILURE.
                    if not validators.validate_string(parameter_value, False, True):
                        message = "{} parameter has no value.".format(parameter)
                        recommendation = "Specify the {} parameter.".format(parameter)
                        warning += "\n" + message
                        self.command_status.add_to_log(command_phase_type.INITIALIZATION,
                                                       CommandLogRecord(command_status_type.FAILURE, message,
                                                                        recommendation))

        # Check that optional parameter IfGeoLayerIDExists is either `Replace`, `ReplaceAndWarn`, `Warn`, `Fail`, None.
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        acceptable_values = ["Replace", "ReplaceAndWarn", "Warn", "Fail"]
        if not validators.validate_string_in_list(pv_IfGeoLayerIDExists, acceptable_values, none_allowed=True,
                                                  empty_string_allowed=True, ignore_case=True):

            message = "IfGeoLayerIDExists parameter value ({}) is not recognized.".format(pv_IfGeoLayerIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfGeoLayerIDExists parameter.".format(
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
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def __should_read_geolayer(self, delimited_file_abs, delimiter, geom_type, x_col_name, y_col_name, wkt_col_name,
                               crs_code, geolayer_id):

        """
        Checks the following:
        * the DelimitedFile (absolute) is a valid file
        * if the CSV is using XY coordinates
        * -- > the XColumnName is an actual field name
        * -- > the YColumnName is an actual field name
        * if the CSV if using WKT geometries
        * -- > the WKTColumnName is an actual field name
        * the CRS code is a valid code
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)

        Args:
            * delimited_file_abs (str, required): The absolute path to the delimited file to be read.
            * delimiter (str, required): The delimiter symbol used in the delimited file. Often times a comma.
            * x_col_name (str, required): The name of the delimited file column that holds the x coordinate data.
            * y_col_name (str, required): The name of the delimited file column that holds the y coordinate data.
            * crs_code (str, EPSG format, required): The coordinate reference system code associated with the X and
                Y coordinates.
            * geolayer_id (str, optional): the GeoLayer identifier.

        Returns:
            run_read: Boolean. If TRUE, the read process should be run. If FALSE, the read process should not be run.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the 
        # test confirms that the command should be run. 
        should_run_command = []

        # If the input DelimitedFile is not a valid file path, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsFilePathValid", "DelimitedFile", delimited_file_abs,
                                                       "FAIL"))

        # If the Delimited File exists, continue with the following checks.
        if should_run_command[0] is True:

            # If the geometry type is "XY", continue.
            if geom_type.upper() == "XY":

                # If the XColumnName is not an existing column name in the delimited file, raise a FAILURE.
                should_run_command.append(validators.run_check(self, "IsDelimitedFileColumnNameValid",
                                                               "XColumnName", x_col_name, "FAIL", 
                                                               other_values=[delimited_file_abs, delimiter]))

                # If the YColumnName is not an existing column name in the delimited file, raise a FAILURE.
                should_run_command.append(validators.run_check(self, "IsDelimitedFileColumnNameValid",
                                                               "YColumnName", y_col_name, "FAIL",
                                                               other_values=[delimited_file_abs, delimiter]))

            # If the geometry type is "WKT", continue.
            else:

                # If the WKTColumnName is not an existing column name in the delimited file, raise a FAILURE.
                should_run_command.append(validators.run_check(self, "IsDelimitedFileColumnNameValid",
                                                               "WKTColumnName", wkt_col_name, "FAIL",
                                                               other_values=[delimited_file_abs, delimiter]))

        # If the input CRS code is not a valid coordinate reference code, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsCrsCodeValid", "CRS", crs_code, "FAIL"))

        # If the GeoLayer ID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE (depends on the
        # value of the IfGeoLayerIDExists parameter.) The required, the IfGeoLayerIDExists parameter value is retrieved
        # inside run_check function.
        should_run_command.append(validators.run_check(self, "IsGeoLayerIdUnique", "GeoLayerID", geolayer_id, None))

        # Return the Boolean to determine if the process should be run. 
        if False in should_run_command:
            return False
        else:
            return True

    def run_command(self):
        """
        Run the command. Read the layer file from a delimited file, create a GeoLayer object, and add to the
        GeoProcessor's geolayer list.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_DelimitedFile = self.get_parameter_value("DelimitedFile")
        pv_Delimiter = self.get_parameter_value("Delimiter")
        pv_GeometryType = self.get_parameter_value("GeometryType")
        pv_XColumnName = self.get_parameter_value("XColumnName", default_value=None)
        pv_YColumnName = self.get_parameter_value("YColumnName", default_value=None)
        pv_WKTColunName = self.get_parameter_value("WKTColumnName", default_value=None)
        pv_CRS = self.get_parameter_value("CRS")
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID", default_value='%f')

        # Convert the DelimitedFile parameter value relative path to an absolute path and expand for ${Property}
        # syntax
        delimited_file_absolute = io_util.verify_path_for_os(io_util.to_absolute_path(
            self.command_processor.get_property('WorkingDir'),
            self.command_processor.expand_parameter_value(pv_DelimitedFile, self)))

        # If the pv_GeoLayerID is a valid %-formatter, assign the pv_GeoLayerID the corresponding value.
        if pv_GeoLayerID in ['%f', '%F', '%E', '%P', '%p']:
            pv_GeoLayerID = io_util.expand_formatter(delimited_file_absolute, pv_GeoLayerID)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_read_geolayer(delimited_file_absolute, pv_Delimiter, pv_GeometryType, pv_XColumnName,
                                       pv_YColumnName, pv_WKTColunName, pv_CRS, pv_GeoLayerID):

            try:

                if pv_GeometryType.upper() == "XY":

                    # Create a QGSVectorLayer object with the delimited file.
                    qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_delimited_file_xy(delimited_file_absolute,
                                                                                            pv_Delimiter, pv_CRS,
                                                                                            pv_XColumnName,
                                                                                            pv_YColumnName)

                else:

                    # Create a QGSVectorLayer object with the delimited file.
                    qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_delimited_file_wkt(delimited_file_absolute,
                                                                                             pv_Delimiter, pv_CRS,
                                                                                             pv_WKTColunName)

                # Create a GeoLayer and add it to the geoprocessor's GeoLayers list.
                geolayer_obj = GeoLayer(pv_GeoLayerID, qgs_vector_layer, delimited_file_absolute)
                self.command_processor.add_geolayer(geolayer_obj)

            # Raise an exception if an unexpected error occurs during the process.
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error reading GeoLayer {} from delimited file {}.".format(pv_GeoLayerID,
                                                                                                pv_DelimitedFile)
                recommendation = "Check the log file for details."
                self.logger.exception(message, e)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
