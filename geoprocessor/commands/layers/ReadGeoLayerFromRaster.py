# ReadGeoLayerFromRaster

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.gdal_util as gdal_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validators

import os
import logging
import urllib2


class ReadGeoLayerFromRaster(AbstractCommand):

    """
    Reads a GeoLayer from a raster.

    Command Parameters
    * SpatialDataFile (str, required): the relative pathname to the spatial data file (raster)
    * RasterDataAttribute (str, optional): the name of the attribute to hold the raster data values. If None, the
        attribute will not be created.
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
        CommandParameterMetadata("SpatialDataFile", type("")),
        CommandParameterMetadata("RasterDataAttribute", type("")),
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command
        """

        # AbstractCommand data
        super(ReadGeoLayerFromRaster, self).__init__()
        self.command_name = "ReadGeoLayerFromRaster"
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

        # Check that parameter SpatialDataFile is a non-empty, non-None string.
        # - existence of the file will also be checked in run_command().
        pv_SpatialDataFile = self.get_parameter_value(parameter_name='SpatialDataFile',
                                                      command_parameters=command_parameters)

        if not validators.validate_string(pv_SpatialDataFile, False, False):
            message = "SpatialDataFile parameter has no value."
            recommendation = "Specify the SpatialDataFile parameter to indicate the spatial data layer file."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

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

    def __should_read_geolayer(self, spatial_data_file_abs, geolayer_id):

        """
        Checks the following:
        * the SpatialDataFile (absolute) is a valid file
        * the SpatialDataFile (absolute) ends in .SHP (warning, not error)
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)

        Args:
            spatial_data_file_abs: the full pathname to the input spatial data file
            geolayer_id: the ID of the output GeoLayer

        Returns:
            run_read: Boolean. If TRUE, the read process should be run. If FALSE, the read process should not be run.
        """

        pass

    def run_command(self):
        """
        Run the command.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_SpatialDataFile = self.get_parameter_value("SpatialDataFile")
        pv_RasterDataAttribute = self.get_parameter_value("RasterDataAttribute")
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID", default_value='%f')

        # Convert the SpatialDataFile parameter value relative path to an absolute path and expand for ${Property}
        # syntax
        spatial_data_file_absolute = io_util.verify_path_for_os(
            io_util.to_absolute_path(self.command_processor.get_property('WorkingDir'),
                                     self.command_processor.expand_parameter_value(pv_SpatialDataFile, self)))

        # If the pv_GeoLayerID is a valid %-formatter, assign the pv_GeoLayerID the corresponding value.
        if pv_GeoLayerID in ['%f', '%F', '%E', '%P', '%p']:
            pv_GeoLayerID = io_util.expand_formatter(spatial_data_file_absolute, pv_GeoLayerID)

        # The output file is the temp directory and the input raster filename.
        output_file = os.path.join(self.command_processor.get_property('TempDir'), io_util.get_filename(spatial_data_file_absolute) + ".geojson")

        # Convert the raster to a vector.
        gdal_util.polygonize(spatial_data_file_absolute, pv_RasterDataAttribute, "GeoJSON", output_file, 4326)

        # Create a new GeoLayer and add it to the GeoProcessor's geolayers list.
        qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_file(output_file)
        new_geolayer = GeoLayer(pv_GeoLayerID, qgs_vector_layer, "MEMORY")
        self.command_processor.add_geolayer(new_geolayer)



        # # Run the checks on the parameter values. Only continue if the checks passed.
        # if self.__should_read_geolayer(spatial_data_file_absolute, pv_GeoLayerID):
        #
        #     try:
        #
        #         # Create a QGSVectorLayer object with the SpatialDataFile in Shapefile format
        #         qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_file(spatial_data_file_absolute)
        #
        #         # Create a GeoLayer and add it to the geoprocessor's GeoLayers list
        #         geolayer_obj = GeoLayer(geolayer_id=pv_GeoLayerID,
        #                                 geolayer_qgs_vector_layer=qgs_vector_layer,
        #                                 geolayer_source_path=spatial_data_file_absolute)
        #         self.command_processor.add_geolayer(geolayer_obj)
        #
        #     # Raise an exception if an unexpected error occurs during the process
        #     except Exception as e:
        #
        #         self.warning_count += 1
        #         message = "Unexpected error reading GeoLayer {} from Shapefile {}.".format(pv_GeoLayerID,
        #                                                                                    pv_SpatialDataFile)
        #         recommendation = "Check the log file for details."
        #         self.logger.error(message, exc_info=True)
        #         self.command_status.add_to_log(command_phase_type.RUN,
        #                                        CommandLogRecord(command_status_type.FAILURE, message, recommendation))
        #

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)

class ListFiles(AbstractCommand):

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("Folder", type("")),
        CommandParameterMetadata("URI", type("")),
        CommandParameterMetadata("IncludePatterns", type("")),
        CommandParameterMetadata("ExcludePatterns", type("")),
        CommandParameterMetadata("ListFiles", type("")),
        CommandParameterMetadata("ListFolders", type("")),
        CommandParameterMetadata("ListProperty", type(""))]

    def __init__(self):
        """
        Initialize the command
        """

        # AbstractCommand data
        super(ListFiles, self).__init__()
        self.command_name = "ListFiles"
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

    def should_list_files(self):
        """
        Check that either the list files or list dirs or both are set to TRUE.
        :return:
        """
        pass

    def run_command(self):

        # Obtain the parameter values.
        pv_Folder = self.get_parameter_value("Folder")
        pv_URI = self.get_parameter_value("URI")
        pv_ListFiles = self.get_parameter_value("ListFiles", default_value=True)
        pv_ListFolders = self.get_parameter_value("ListFolders", default_value=True)
        pv_ListProperty = self.get_parameter_value("ListProperty")
        pv_IncludePatterns = self.get_parameter_value("IncludePatterns", default_value="*")
        pv_ExcludePatterns = self.get_parameter_value("ExcludePatterns", default_value="")

        # Convert the IncludeAttributes and ExcludeAttributes to lists.
        to_include = string_util.delimited_string_to_list(pv_IncludePatterns)
        to_exclude = string_util.delimited_string_to_list(pv_ExcludePatterns)

        # If the input is a local folder.
        if pv_Folder:

            # Convert the Folder parameter value relative path to an absolute path and expand for ${Property} syntax.
            folder_abs = io_util.verify_path_for_os(io_util.to_absolute_path(
                self.command_processor.get_property('WorkingDir'),
                self.command_processor.expand_parameter_value(pv_Folder, self)))

        # Do check. And then continue.
        ######################################

        # If the input is a local folder.
        if pv_Folder:

            # Get a list of the files in the folder.
            files = [file for file in os.listdir(folder_abs) if os.path.isfile(os.path.join(folder_abs, file))]

            # Get a list of directories in the folder.
            dirs = [dir for dir in os.listdir(folder_abs) if os.path.isdir(os.path.join(folder_abs, dir))]

            # Join the files and dirs lists into an overall list.
            files_and_dirs = files + dirs

        # If the input is a url.
        if pv_URI:

            urlpath = urllib2.urlopen(('{}').format(pv_URI))
            string = urlpath.read().decode('utf-8')

            list = string.split("<A")


        # If configured to list files and folders, continue.
        if pv_ListFiles and pv_ListFolders:

            # Filter the list of files and folders with regards to the IIncludePatterns and ExcludePatterns parameters.
            output_filtered = string_util.filter_list_of_strings(files_and_dirs, to_include, to_exclude)

        # If configured to list files, continue.
        elif pv_ListFiles:

            # Filter the list of files with regards to the IIncludePatterns and ExcludePatterns parameters.
            output_filtered = string_util.filter_list_of_strings(files, to_include, to_exclude)

        # If configured to list folders, continue.
        else:

            # Filter the list of folders with regards to the IIncludePatterns and ExcludePatterns parameters.
            output_filtered = string_util.filter_list_of_strings(dirs, to_include, to_exclude)

        # Add the filtered list to the desired ListProperty.
        print output_filtered
        self.command_processor.set_property(pv_ListProperty, output_filtered)



def scrape_html(uri, files, dirs, include_list=['*'], exclude_list=['']):

    urlpath = urllib2.urlopen(('{}'.format(uri)))
    string = urlpath.read().decode('utf-8')
    previous_path = uri.rsplit('/', 2)[0]

    in_link = False
    dir_list = []
    file_list = []

    for i in range(len(string)):

        # print (string[i:i+8]).upper()

        if (string[i:i + 8]).upper() == "<A HREF=" and not in_link:
            in_link = True
            link_start_char = i + 9

        if (string[i:i + 2]).upper() == '">' and in_link:

            in_link = False
            link_end_char = i

            link = string[link_start_char: link_end_char]
            print link
            if link.endswith('/'):

                dir_list.append(link.split('/')[-2])

            else:

                file_list.append(link.split('/')[-1])

    if files and dirs:
        out_list = dir_list + file_list
    elif files:
        out_list = file_list
    elif dirs:
        out_list = dir_list


    for item in out_list:
        print item


    output_filtered = string_util.filter_list_of_strings(out_list, include_list, exclude_list)
    return output_filtered


geomac_url = "https://gec.cr.usgs.gov/outgoing/GeoMAC/"
date_folders = scrape_html(geomac_url, False, True, ['current*'])
for date in date_folders:

    state_folders = scrape_html(os.path.join(geomac_url,date), False, True)

    for state in state_folders:

        print state
    #
    #     fire_names = scrape_html(os.path.join(geomac_url,date,state), False, True)
    #
    #     for fire in fire_names:
    #
    #         fire_data = scrape_html(os.path.join(geomac_url, date, state, fire), True, False)
    #         if fire_data:
    #             print fire_data



# pv_URI = "https://gec.cr.usgs.gov/outgoing/GeoMAC/"
# urlpath = urllib2.urlopen(('{}'.format(pv_URI)))
# string = urlpath.read().decode('utf-8')
#
# list = string.split("<A")
#
# in_link = False
# dir_list = []
# file_list = []
# for i in range(len(string)):
#
#     # print (string[i:i+8]).upper()
#
#     if (string[i:i+8]).upper() == "<A HREF=" and not in_link:
#
#         in_link = True
#         link_start_char = i+9
#
#
#     if (string[i:i+2]).upper() == '">' and in_link:
#
#         in_link = False
#         link_end_char = i
#
#         link = string[link_start_char: link_end_char]
#         if link.endswith('/'):
#
#             dir_list.append(link.split('/')[-2])
#
#         else:
#
#             file_list.append(link.split('/')[-1])
#
#
# output_filtered = string_util.filter_list_of_strings(dir_list, ['2017*', '2016*'])
#
# for output in output_filtered:
#     new_uri = pv_URI + output
#
#
#
