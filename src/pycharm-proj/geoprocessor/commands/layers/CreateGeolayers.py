import geoprocessor.commands.abstract.AbstractCommand as AbstractCommand
import os
import ogr
from qgis.core import QgsVectorLayer

class CreateGeolayers(AbstractCommand.AbstractCommand):
    """Creates a geolayer within the geoprocessor. Geolayers are originally stored on a local machine as a spatial data
    file (geojson, shp, feature class, etc). In order for the geoprocessor to use and manipulate spatial data files,
    they must be incorporated into Qgs Vector Object layers. This command will take a single or a list of spatial data
    sources and incorporate the available spatial data files as geoprocessor geolayers (or QgsVectorLayer object). The
    user can declare any of the following spatial data sources:

        a file (geojson or shp): the full pathname to a spatial data file. That spatial data file will be added to the
        geoprocessor as a single geolayer

        a folder: the full pathname to a folder containing one or many spatial data files. All shapefile and geojson
        spatial data files within the specified folder will be added to the geoprocessor as individual geolayers

        a file geodatabase: the full pathname to a folder that ends in '.gdb'. All feature classes within this file
        geodatabase will be added to the geoprocessor as individual geolayers"""

    def __init__(self):
        """Initialize the command"""

        AbstractCommand.AbstractCommand.__init__(self)
        self.command_name = "CreateGeolayers"
        self.parameter_list = ["source_list", "id_list"]

    def convert_file_to_v_layer(self, file_pathname, use_filename, layer_ids, source_index):
        """A helper function that envelops a spatial data file into a QgsVectorLayer object. The QgsVectorLayer object
        is returned as the first item of a list. The second item contains the full pathname to the spatial data file.

        :param file_pathname (str): the full pathname to a spatial data file
        :param use_filename (Boolean): if TRUE, the original filename will be used as the geolayer id, if FALSE,
         the provided layer_id from the layer_ids list will be used as geolayer id
        :param layer_ids: a list of user-provided geolayer ids (these geolayer ids will be used instead of the original
         spatial data filename if the ues_filename Boolean is set to FALSE
        :param source_index: the index of the current spatial data source in reference to the source_list (see
        run_command for more information)"""

        # retrieve the name of the spatial data file without the extension
        file_wo_ext = os.path.basename(file_pathname).split('.')[0]

        # envelop the spatial data file as a QGSVectorLayer
        v_layer = QgsVectorLayer(file_pathname, file_wo_ext, 'ogr')

        # if the QGSVectorLayer is valid, return a list, otherwise return NONE
        # list item 1: the QgsVectorLayer object
        # list item 2: the source pathname as the second item
        if v_layer.isValid():

            v_layer_item = [v_layer, file_pathname]

            # define the geolayer id
            # if use_filename is TRUE, use the source filename as the geolayer id
            if use_filename:

                # get the layer id from the source file
                extension = os.path.splitext(file_pathname)[1]
                layer_id = os.path.basename(file_pathname).replace(extension, "")

            # if use_filename is FALSE, user the user-defined string as the geolayer id
            else:

                # get the geolayer id from the user input
                layer_id = layer_ids[source_index]

            # if a valid geolayer id was defined, append the geolayer to the geoprocessor geolayer list
            if layer_id:

                self.command_processor.geolayers[layer_id] = v_layer_item

            else:

                print "Vector file from file ({}) was not appended to the layer list because the geolayer id ({}) " \
                      "is invalid.".format(file_pathname, layer_id)
        else:
            print "Vector file from file ({}) is invalid".format(file_pathname)

    def run_command(self):

        # notify that this command is running
        print "Running {}".format(self.command_name)

        # get parameter values
        source_list = self.return_parameter_value_required("source_list")
        id_list = self.return_parameter_value_optional("id_list", "UseFilename")
        use_filename = False

        # if the layer_ids parameter was not set by the user than use the layers filename as the layer id
        if id_list == "UseFilename":
            use_filename = True

        # iterate over the sources
        source_index = 0
        for source in source_list:

            # if the source is a filename
            if os.path.isfile(source):

                # convert the spatial data file into a geolayer, return [QgsVectorLayer Object, source pathname]
                CreateGeolayers.convert_file_to_v_layer(self, source, use_filename, id_list, source_index)


            # if the source is a directory - the filename will ALWAYS be used as the layer ID
            elif os.path.isdir(source) and not source.endswith(".gdb"):

                # iterate over the files in the source directory, continue if the file is a spatial data file
                for file in os.listdir(source):

                    # convert the spatial data file into a geolayer, return [QgsVectorLayer Object, source pathname]
                    if file.endswith(".shp") or file.endswith(".geojson"):
                        CreateGeolayers.convert_file_to_v_layer(self, os.path.join(source, file), True, id_list, source_index)

            # if the layer_source is a file geodatabase - the feature class will ALWAYS be used as the layer ID
            elif os.path.isdir(source) and source.endswith(".gdb"):

                # the file geodatabase will be read and each feature class will be added to the feature_class_list
                feature_class_list = []

                # REF: https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html|
                # "Get all layers in an Esri File GeoDataBase"
                ogr.UseExceptions()
                driver = ogr.GetDriverByName("OpenFileGDB")
                gdb = driver.Open(source)
                for feature_class_idx in range(gdb.GetLayerCount()):
                    feature_class = gdb.GetLayerByIndex(feature_class_idx)
                    feature_class_list.append(feature_class.GetName())

                # Iterate through each feature class inside the file geodatabase
                for feature_class in feature_class_list:

                    # envelop the feature class as a QGS object vector layer.
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

                    # if the QgsVectorLayer object is valid, append it to the v_layer_list
                    if v_layer_item:
                        self.command_processor.geolayers[feature_class] = v_layer_item
            else:
                print "The source ({}) is invalid. Enter the full pathname to a spatial data file, a directory " \
                      "containing spatial data files, or a file geodatabase".format(source)

            source_index += 1
