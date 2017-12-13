import os
import ogr
from qgis.core import QgsVectorLayer
from commandprocessor.util import abstractcommand

class CreateLayerList(abstractcommand.AbstractCommand):

    name = "Create Layer List"
    description = "Creates and initializes a layer list."
    parameter_names = ["input_layers", "layer_list_id"]
    parameter_values = {"input_layers": None, "layer_list_id": None}

    def __init__(self, parameter_values):

        self.populate_parameter_values_dic(parameter_values, self.parameter_names, self.parameter_values)

    # Helper function to convert a spatial data file (full pathname) to a QgsVectorLayer object
    @staticmethod
    def convert_file_to_v_layer(file_pathname):
        """A helper function that envelops a spatial data file into a QgsVectorLayer object. The QgsVectorLayer object
        is returned as the first item of a list. The second item contains the full pathname to the spatial data file.

        Argument: file_pathname (str): the full pathname to a spatial data file"""

        # retrieve the name of the file without the extension
        file_wo_ext = os.path.basename(file_pathname).split('.')[0]

        # envelop the spatial data file as a QGSVectorLayer
        v_layer = QgsVectorLayer(file_pathname, file_wo_ext, 'ogr')

        # if the QGSVectorLayer is valid, return a list with the QgsVectorLayer as the first item and the source
        # pathname as the second item. otherwise, return None with an error message.
        if v_layer.isValid():
            return [v_layer, file_pathname]
        else:
            print "Vector file from file ({}) is invalid".format(file_pathname)
            return None

    def run_command(self):

        input_list = self.parameter_values["input_layers"]
        layer_list_id = self.parameter_values["layer_list_id"]

        # a list that holds all of the spatial data layers successfully converted to QgsVectorLayer objects
        v_layer_list = []

        # iterate over the spatial data file sources
        for input_item in input_list:

            # if the spatial data file source is a file, then convert the file into a QgsVectorLayer object
            if os.path.isfile(input_item):

                v_layer = CreateLayerList.convert_file_to_v_layer(input_item)

                # if the QgsVectorLayer object is valid, append it to the v_layer_list
                if v_layer:
                    v_layer_list.append(v_layer)

            # if the spatial data file source is a directory, then iterate over each file in the directory
            elif os.path.isdir(input_item) and not input_item.endswith('.gdb'):

                for input_file in os.listdir(input_item):

                    # if the file is a spatial data file, convert the file into a QgsVectorLayer object
                    if input_file.endswith(".geojson") or input_file.endswith(".shp"):

                        v_layer = CreateLayerList.convert_file_to_v_layer(os.path.join(input_item, input_file))

                        # if the QgsVectorLayer object is valid, append it to the v_layer_list
                        if v_layer:
                            v_layer_list.append(v_layer)

            # if the spatial data file source is a file geodatabase
            # TODO research the best way to include the source code for a file geodatabase layer
            elif os.path.isdir(input_item) and input_item.endswith('.gdb'):

                # the file geodatabase will be read and each feature class will be added to the feature_class_list
                feature_class_list = []

                # REF: https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html|
                # "Get all layers in an Esri File GeoDataBase"
                ogr.UseExceptions()
                driver = ogr.GetDriverByName("OpenFileGDB")
                gdb = driver.Open(input_item)
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
                    v_layer = [QgsVectorLayer(str(input_item) + "|layername=" + str(feature_class), feature_class,
                                              'ogr'), os.path.join(input_item, str(feature_class))]

                    # if the QgsVectorLayer object is valid, append it to the v_layer_list
                    if v_layer:
                        v_layer_list.append(v_layer)


            # if the spatial data file source is not a file or directory, print an error message

            else:
                print "The input method ({}) is invalid. Enter the full pathname to a spatial data file or a " \
                      "directory containing spatial data files.".format(input_item)

        # add the new layer list to the global dictionary variable session_layer_lists
        abstractcommand.AbstractCommand.session_layer_lists[layer_list_id] = v_layer_list
