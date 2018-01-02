# CreateGeoLayers command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.validators as validators

import os
import ogr

from qgis.core import QgsVectorLayer

import logging


# Inherit from AbstractCommand
class CreateGeoLayers(AbstractCommand):
    """Creates (a) GeoLayer(s) within the geoprocessor.

    GeoLayers are originally stored on a local machine as a spatial data file (geojson, shp, feature class, etc). In
    order for the geoprocessor to use and manipulate spatial data files, they must be incorporated into Qgs Vector
    Object layers. This command will take a single or a list of spatial data sources and incorporate the available
    spatial data files as geoprocessor GeoLayers (or QgsVectorLayer object). The user can declare any of the following
    spatial data sources:

        a file (geojson or shp): the full pathname to a spatial data file. That spatial data file will be added to the
        geoprocessor as a single GeoLayer

        a folder: the full pathname to a folder containing one or many spatial data files. All shapefile and geojson
        spatial data files within the specified folder will be added to the geoprocessor as individual GeoLayers

        a file geodatabase: the full pathname to a folder that ends in '.gdb'. All feature classes within this file
        geodatabase will be added to the geoprocessor as individual GeoLayers

    Args:
        SourceList: a list of source files, explained above, that will be added to the GeoProcessor as GeoLayers"""

    def __init__(self):
        """Initialize the command"""

        super(CreateGeoLayers, self).__init__()
        self.command_name = "CreateGeoLayers"
        self.command_parameter_metadata = [
            CommandParameterMetadata("SourceList", type([])),
            CommandParameterMetadata("CommandStatus", type(""))
        ]

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            Nothing.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning = ""
        logger = logging.getLogger("gp")

        # Check that parameter SourceList is a non-empty, non-None string.
        pv_SourceList = self.get_parameter_value(parameter_name='SourceList', command_parameters=command_parameters)
        if not validators.validate_string(pv_SourceList, False, False):
            message = "SourceList parameter has no value."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify text for the SourceList parameter."))
            logger.warning(message)

        # Check that parameter SourceList is a string that can be converted into a list.
        if not validators.validate_list(pv_SourceList, False, False):
            message = "SourceList parameter is not a valid list."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify list for the SourceList parameter."))
            logger.warning(message)

        # Check that parameter CommandStatus is one of the valid Command Status Types.
        pv_CommandStatus = self.get_parameter_value(parameter_name='CommandStatus',
                                                    command_parameters=command_parameters)
        if not validators.validate_string_in_list(pv_CommandStatus,
                                                  command_status_type.get_command_status_types(), True, True):
            message = 'The requested command status "' + pv_CommandStatus + '"" is invalid.'
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, "Specify a valid command status."))
            logger.warning(message)

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty
        # triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception
        if len(warning) > 0:
            logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    def convert_file_to_v_layer(self, file_pathname, use_filename=True):
        """
            Convert a spatial data file into a Qgs Vector Object layer.

            Args:
                file_pathname (str): the full pathname to the spatial data file that will be converted into a Qgs
                Vector Layer object
                use_filename (bool): if True, the filename of the spatial data file will be used (default). as of now,
                the use_filename is always set to True

            Returns:
                Nothing.

            Raises:
                ValueError if the layer ID is None.
                IOError if the created QGSVectorLayer Object is invalid. If this is the case, the QgsVectorLayer
                Object will not be appended to the GeoProcessor's GeoLayer list
            """

        # Get the name of the spatial data file wihtout the extension.
        file_wo_ext = os.path.basename(file_pathname).split('.')[0]

        # Envelop the spatial data file as a QGSVectorLayer object.
        v_layer = QgsVectorLayer(file_pathname, file_wo_ext, 'ogr')

        # If the QGSVectorLayer is valid, return a list, otherwise throw an exception.
        # In future versions of this software, the QgsVectorLayer will be a class object and the items in the list
        # (described below) will be properties of that instance
        # list item 1: the QgsVectorLayer object
        # list item 2: the source pathname as the second item
        if v_layer.isValid():

            v_layer_item = [v_layer, file_pathname]

            # Define the unique GeoLayer ID.
            # If use_filename is TRUE, use the source filename as the GeoLayer id.
            if use_filename:

                # get the layer id from the source file
                extension = os.path.splitext(file_pathname)[1]
                layer_id = os.path.basename(file_pathname).replace(extension, "")

            else:
                layer_id = None

            # If a valid GeoLayer ID was defined, append the GeoLayer to the geoprocessor GeoLayer list. Else, raise
            # an error.
            if layer_id:
                self.command_processor.GeoLayers[layer_id] = v_layer_item

            else:
                raise ValueError("Vector file from file ({}) was not appended to the layer list because the GeoLayer "
                                 "id ({}) is invalid.".format(file_pathname, layer_id))
        else:
            raise IOError("Vector file from file ({}) is invalid".format(file_pathname))

    def run_command(self):
        """
        Run the command. Create (a) GeoLayer(s) and register in the GeoProcessor. Print the message to the log file.

        Returns:
            Nothing
        """
        logger = logging.getLogger(__name__)
        warning_count = 0

        # Get the SourceList parameter value in string format. Convert the SourceList paramter value to list format.
        pv_SourceList = self.get_parameter_value("SourceList")
        pv_SourceList = command_util.to_correct_format(pv_SourceList)

        # For now, use_filename is always set to TRUE. This means that in every scenario, the spatial data file's
        # filename is used as the GeoLayer's ID.
        use_filename = True

        # Iterate over the sources of the pv_SourceList.
        for source in pv_SourceList:

            # If the source is a full path to a spatial data file, continue.
            if os.path.isfile(source):

                # Convert the spatial data file into a GeoLayer and append the GeoLayer object to the GeoProcessor's
                # GeoLayer list.
                CreateGeoLayers.convert_file_to_v_layer(self, source, use_filename)

            # If the source is a full path to a directory, continue. In this scenario, the filename will ALWAYS be used
            # as the layer ID.
            elif os.path.isdir(source) and not source.endswith(".gdb"):

                # Iterate over the files in the source directory, continue if the file is a spatial data file (geojson
                # or shp extension).
                for source_file in os.listdir(source):
                    if source_file.endswith(".shp") or source_file.endswith(".geojson"):

                        # Convert the spatial data file into a GeoLayer and append the GeoLayer object to the
                        # GeoProcessor's GeoLayer list.
                        CreateGeoLayers.convert_file_to_v_layer(self, os.path.join(source, source_file), True)

            # If the source is a full path to a file geodatabase, continue. In this scenario, the filename will ALWAYS
            # be used as the layer ID.
            elif os.path.isdir(source) and source.endswith(".gdb"):

                # The file geodatabase will be read and each feature class will be added to the feature_class_list.
                feature_class_list = []

                # Append each feature class in the Esri File Geodatabase to the feature_class_list.
                # REF: https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html|
                # "Get all layers in an Esri File GeoDataBase"
                ogr.UseExceptions()
                driver = ogr.GetDriverByName("OpenFileGDB")
                gdb = driver.Open(source)
                for feature_class_idx in range(gdb.GetLayerCount()):
                    feature_class = gdb.GetLayerByIndex(feature_class_idx)
                    feature_class_list.append(feature_class.GetName())

                # Iterate through each feature class inside the file geodatabase.
                for feature_class in feature_class_list:

                    # Envelop the feature class as a QGS object vector layer.
                    # In order for this to work, you must configure ESRI FileGDB Driver in QGIS Installation.
                    # Follow instructions from GetSpatial's post in below reference
                    # REF: https://gis.stackexchange.com/questions/26285/file-geodatabase-gdb-support-in-qgishttps:
                    # //gis.stackexchange.com/questions/26285/file-geodatabase-gdb-support-in-qgis
                    # Must follow file geodatabase input annotation. Follow instructions from nanguna's post in
                    # below reference
                    # REF: https://gis.stackexchange.com/questions/122205/
                    # how-to-add-mdb-geodatabase-layer-feature-class-to-qgis-project-using-python
                    v_layer_item = [
                        QgsVectorLayer(str(source) + "|layername=" + str(feature_class), feature_class,
                                       'ogr'), os.path.join(source, str(feature_class))]

                    # If a valid GeoLayer ID was defined, append the GeoLayer to the geoprocessor GeoLayer list. Else,
                    # throw an exception.
                    if v_layer_item:
                        self.command_processor.GeoLayers[feature_class] = v_layer_item
                    else:
                        warning_count += 1
                        message = "Vector file from feature class ({}) is invalid".format(feature_class)
                        raise IOError(message)

            # Otherwise, throw a Value Error.
            else:
                warning_count += 1
                message = "The source ({}) is invalid. Enter the full pathname to a spatial data file, a directory " \
                          "containing spatial data files, or a file geodatabase".format(source)
                raise ValueError(message)

        # If no warnings were thrown, print success message to the log file. Otherwise print fail message to log file
        # and throw a RuntimeError.
        if warning_count > 0:
            message = "There were {} warnings processing the command.".format(warning_count)
            logger.warning(message)
            raise RuntimeError(message)
        else:
            logger.info("CreateGeoLayers command was successfully run without any warnings.")
