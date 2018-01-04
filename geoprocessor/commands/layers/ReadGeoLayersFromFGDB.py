# ReadGeoLayersFromFGDB

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
import geoprocessor.core.GeoLayerMetadata as GeoLayerMetadata

import geoprocessor.util.command as command_util
import geoprocessor.util.geo as geo_util
import geoprocessor.util.io as io_util
import geoprocessor.util.validators as validators

from qgis.core import QgsVectorLayer

import os
import logging
import re
import ogr


# Inherit from Abstract Command
class ReadGeoLayersFromFGDB(AbstractCommand):
    # TODO egiles 2018-01-03 Add Raises section in command documentation

    """
        Reads the GeoLayers (feature classes) within a file geodatabase (FGDB).

        This command reads the GeoLayers from a file geodatabase and creates GeoLayer objects within the
        geoprocessor. The GeoLayers can then be accessed in the geoprocessor by their identifier and further processed.

        GeoLayers are stored on a computer or are available for download as a spatial data file (GeoJSON, shapefile,
        feature class in a file geodatabase, etc.). Each GeoLayer has one feature type (point, line, polygon, etc.) and
        other data (an identifier, a coordinate reference system, etc). Note that this function only reads one or many
        GeoLayers (feature classes) from within a single file geodatabase.

        In order for the geoprocessor to use and manipulate spatial data files, GeoLayers are instantiated as
        `QgsVectorLayer <https://qgis.org/api/classQgsVectorLayer.html>`_ objects. This command will read the GeoLayers
        from the feature classes within a file geodatabase and instantiate them as geoprocessor GeoLayer objects.

        Args:
            SpatialDataFolder (str, required): the relative pathname to the file geodatabase containing spatial data
                files (feature classes)
            GeoLayerID_prefix (str, optional): the GeoLayer identifier will, by default, use the name of the feature
                class that is being read. However, if a value is set for this parameter, the GeoLayerID will follow
                this format: [GeoLayerID_prefix]_[name_of_feature_class]
            Subset_Pattern (str, optional): the glob-style pattern of the feature class name to determine which feature
                classes within the file geodatabase are to be processed. More information on creating a glob pattern
                can be found at `this site <https://docs.python.org/2/library/glob.html>`_.
        """

    def __init__(self):
        """Initialize the command"""

        super(ReadGeoLayersFromFGDB, self).__init__()
        self.command_name = "ReadGeoLayersFromFGDB"
        self.command_parameter_metadata = [
            CommandParameterMetadata("SpatialDataFolder", type("")),
            CommandParameterMetadata("GeoLayerID_prefix", type("")),
            CommandParameterMetadata("Subset_Pattern", type("")),
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
        logger = logging.getLogger(__name__)

        # Check that parameter SpatialDataFolder is a non-empty, non-None string.
        pv_SpatialDataFolder = self.get_parameter_value(parameter_name='SpatialDataFolder',
                                                        command_parameters=command_parameters)

        if not validators.validate_string(pv_SpatialDataFolder, False, False):
            message = "SpatialDataFolder parameter has no value."
            recommendation = "Specify text for the SpatialDataFolder parameter."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    @staticmethod
    def glob2re(pat):
        """
            Translates a shell PATTERN to a regular expression.

            The input parameters of the ReadGeoLayersFromFolder command are the exact same as the input parameters
            of this command, ReadGeoLayersFromFGDB. This design is for user convenience so that the user only needs
            to learn the input parameters of one command and will, in turn, know the input parameters for all
            ReadGeoLayersFrom... commands.

            In the ReadGeoLayersFromFolder command, there is an optional input parameter called Subset_Pattern. Like in
            the ReadGeoLayersFromFGDB command, this parameter allows the user to select only a subset of the spatial
            data files within the source (folder, file geodatabase, etc.) to read as GeoLayers into the geoprocessor.
            This is accomplished by entering a glob-style pattern into the Subset_Pattern parameter value. In the
            ReadGeoLayerFromFolder command, the glob-style pattern is effective because the run_command code iterates
            over files on the local machine (glob is designed to find patterns in pathnames). However, in the
            ReadGeoLayersFromFGDB command, the feature classes in the file geodatabase are first written to a list. The
            list is then iterated over and only the strings that match the Subset_Pattern are processed. Feature class
            names are not file pathnames and, for that reason, the glob-style does not work.

            This function converts a glob-style pattern into a regular expression that can be used to iterate over a
            list of strings. This function was not written by Open Water Foundation but was instead copied from the
            following source: https://stackoverflow.com/questions/27726545/
            python-glob-but-against-a-list-of-strings-rather-than-the-filesystem.

            Args:
                pat (str, required): a pattern in glob-style (shell)

            Returns:
                A pattern in regular expression.

            Raises:
                Nothing.
        """

        i, n = 0, len(pat)
        res = ''
        while i < n:
            c = pat[i]
            i += 1
            if c == '*':
                # res = res + '.*'
                res += '[^/]*'
            elif c == '?':
                # res = res + '.'
                res += '[^/]'
            elif c == '[':
                j = i
                if j < n and pat[j] == '!':
                    j += 1
                if j < n and pat[j] == ']':
                    j += 1
                while j < n and pat[j] != ']':
                    j += 1
                if j >= n:
                    res += '\\['
                else:
                    stuff = pat[i:j].replace('\\', '\\\\')
                    i = j + 1
                    if stuff[0] == '!':
                        stuff = '^' + stuff[1:]
                    elif stuff[0] == '^':
                        stuff = '\\' + stuff
                    res = '%s[%s]' % (res, stuff)
            else:
                res = res + re.escape(c)
        return res + '\Z(?ms)'

    def run_command(self):

        # Obtain the required and optional parameter values
        pv_SpatialDataFolder = self.get_parameter_value("SpatialDataFolder")
        pv_Subset_Pattern = self.get_parameter_value("Subset_Pattern")
        pv_GeoLayerID_prefix = self.get_parameter_value("GeoLayerID_prefix")

        # Convert the SpatialDataFolder parameter value relative path to an absolute path
        spatialDataFolder_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_SpatialDataFolder, self)))

        # The file geodatabase will be read and each feature class will be added to the feature_class_list.
        feature_class_list = []

        # Append each feature class in the Esri File Geodatabase to the feature_class_list.
        # REF: https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html|
        # "Get all layers in an Esri File GeoDataBase"
        ogr.UseExceptions()
        driver = ogr.GetDriverByName("OpenFileGDB")
        gdb = driver.Open(spatialDataFolder_absolute)
        for feature_class_idx in range(gdb.GetLayerCount()):
            feature_class = gdb.GetLayerByIndex(feature_class_idx)
            feature_class_list.append(feature_class.GetName())

        # If a file_pattern has been included, update the feature_class_list to only include the desired files. If no
        # file pattern has been included, all feature classes within the file geodatabase will read as GeoLayers
        if pv_Subset_Pattern:
            glob_filter = (fc for fc in feature_class_list if re.match(ReadGeoLayersFromFGDB.glob2re(pv_Subset_Pattern),
                                                                       fc))
            updated_feature_class_list = list(glob_filter)
            feature_class_list = updated_feature_class_list

        # Iterate through each desired feature class inside the file geodatabase.
        for feature_class in feature_class_list:

            # Get the full pathname to the feature class
            # TODO egiles 2018-01-04 Need to research how to properly document feature class source path
            spatialDataFile_absolute = os.path.join(spatialDataFolder_absolute, str(feature_class))

            # Determine the GeoLayerID.
            # If an identifier_prefix value was provided, the GeoLayer's identifier will be in the following format:
            # [identifier_prefix]_[featureclass]. Otherwise, the identifier is set to the feature class.
            if pv_GeoLayerID_prefix:
                GeoLayerID = "{}_{}".format(pv_GeoLayerID_prefix, feature_class)
            else:
                GeoLayerID = feature_class

            # Throw a warning if the pv_GeoLayerID is not unique.
            if geo_util.is_geolist_id(self, GeoLayerID) or geo_util.is_geolayer_id(self, GeoLayerID):

                # TODO egiles 2018-01-04 Need to throw a warning
                pass

            # If the GeoLayerID is unique, create the QGSVectorLayer object and the GeoLayer object. Append the
            # GeoLayer object to the geoprocessor's GeoLayers list.
            else:

                # Envelop the feature class as a QGS object vector layer.
                # In order for this to work, you must configure ESRI FileGDB Driver in QGIS Installation.
                # Follow instructions from GetSpatial's post in below reference
                # REF: https://gis.stackexchange.com/questions/26285/file-geodatabase-gdb-support-in-qgishttps:
                # //gis.stackexchange.com/questions/26285/file-geodatabase-gdb-support-in-qgis
                # Must follow file geodatabase input annotation. Follow instructions from nanguna's post in
                # below reference
                # REF: https://gis.stackexchange.com/questions/122205/
                # how-to-add-mdb-geodatabase-layer-feature-class-to-qgis-project-using-python
                QgsVectorLayer_obj = QgsVectorLayer(str(spatialDataFolder_absolute) + "|layername=" + feature_class,
                                                    feature_class, 'ogr')

                # A QgsVectorLayer object is almost always created even if it is invalid.
                # From
                # `QGIS documentation <https://docs.qgis.org/2.14/en/docs/pyqgis_developer_cookbook/loadlayer.html>`_
                #   "It is important to check whether the layer has been loaded successfully. If it was not, an invalid
                #   layer instance is returned."
                # Check that the newly created QgsVectorLayer object is valid. If so, create a GeoLayer object within
                # the geoprocessor and add the GeoLayer object to the geoprocessor's GeoLayers list.
                if QgsVectorLayer_obj.isValid():

                    # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
                    GeoLayer = GeoLayerMetadata.GeoLayerMetadata(geolayer_id=GeoLayerID,
                                                                 geolayer_qgs_object=QgsVectorLayer_obj,
                                                                 geolayer_source_path=spatialDataFile_absolute)
                    self.command_processor.GeoLayers.append(GeoLayer)

                # The QgsVectorLayer object is invalid. Create a warning.
                else:
                    # TODO egiles 2018-01-03 crate an error handler
                    pass

        # If the SpatialDataFolder is not a file geodatabase
        else:
            # TODO egiles 2018-01-04 Need to throw a warning
            print "The SpatialDataFolder {} is not a valid file geodatabase.".format(spatialDataFolder_absolute)
