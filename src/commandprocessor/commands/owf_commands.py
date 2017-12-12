from commandprocessor.core import abstractcommand
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsCoordinateReferenceSystem
import ogr
import os

class ExportLayerList(abstractcommand.AbstractCommand):
    """Represents an Export Layer List Workflow Command. Exports the layers (QgsVectorLayer objects) of a layer list in
    either GeoJSON or Esri Shapefile format."""

    name = "Export Layer List"
    description = "Exports the layers in a layer list in the specified format."
    parameter_names = ["layer_list_id", "output_dir", "output_format", "output_crs", "output_prec"]
    parameter_values = {"layer_list_id": None,
                           "output_dir": None,
                           "output_format": None,
                           "output_crs": "EPSG:4326",
                           "output_prec": 5}


    def __init__(self, parameter_values):
        self.populate_parameter_values_dic(parameter_values, self.parameter_names, self.parameter_values)


    # Runs the Export Layer List Workflow Command
    def run_command(self):

        layer_list_id = self.parameter_values["layer_list_id"]
        output_dir = self.parameter_values["output_dir"]
        output_format = self.parameter_values["output_format"]
        output_crs = self.parameter_values["output_crs"]
        output_prec = self.parameter_values["output_prec"]

        # iterate over each v_layer_item in the desired v_layer_list
        for v_layer_item in abstractcommand.AbstractCommand.session_layer_lists[layer_list_id]:

            # parse the layer list item's properties
            v_layer_object, v_layer_source_path, v_layer_source_name = abstractcommand.AbstractCommand.return_layer_item_properties(
                v_layer_item)

            # set the full pathname of the output product to the name of the file. save in self.output_dir
            # output_fullpath = os.path.join(self.output_dir, (os.path.basename(v_layer_item[1])).split('.')[0])
            output_fullpath = os.path.join(output_dir, v_layer_source_name)

            # determine output product format. export the QgsVectorLayer object as spatial data file
            if output_format.upper() == 'S':
                QgsVectorFileWriter.writeAsVectorFormat(v_layer_object, output_fullpath, "utf-8",
                                                        QgsCoordinateReferenceSystem(output_crs), "ESRI Shapefile")
            elif output_format.upper() == 'G':
                QgsVectorFileWriter.writeAsVectorFormat(v_layer_object, output_fullpath, "utf-8",
                                                        QgsCoordinateReferenceSystem(output_crs),
                                                        "GeoJSON",
                                                        layerOptions=['COORDINATE_PRECISION={}'.format(output_prec)])
            else:
                print "The output spatial format ({}) is not a valid spatial format.".format(output_format)

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

class EditLayerList(abstractcommand.AbstractCommand):

    name = "Edit Layer List"
    description = "Edits an existing layer list."
    parameter_names = ["layer_list_id", "edit_function", "layers_affected_sourcename"]
    parameter_values = {"layer_list_id": None, "edit_function": None, "layers_affected_sourcename": None}

    def __init__(self, parameter_values):

        self.populate_parameter_values_dic(parameter_values, self.parameter_names, self.parameter_values)

    def run_command(self):

        layer_list_id = self.parameter_values['layer_list_id']
        edit_function = self.parameter_values['edit_function']
        layers_affected_sourcename = self.parameter_values['layers_affected_sourcename']

        # holds the layer list items that are to be kept in the newly edited version of the layer list
        updated_v_layer_list = []

        # iterate over each v_layer_item in the desired v_layer_list
        for v_layer_item in abstractcommand.AbstractCommand.session_layer_lists[layer_list_id]:

            # parse the layer list item's properties
            v_layer_object, v_layer_source_path, v_layer_source_name = abstractcommand.AbstractCommand.return_layer_item_properties(
                v_layer_item)

            # iterate over the affected source names
            for source_name in layers_affected_sourcename:

                # the keep function will only keep the layer list items that have the same source name as those listed
                # in the affected source name list
                if edit_function.upper() == "KEEP" and v_layer_source_name == source_name:

                    updated_v_layer_list.append(v_layer_item)

                # the exclude function will exclude the layer list items that have the same source name as those listed
                # in the affected source name list
                elif edit_function.upper() == "EXCLUDE" and not v_layer_source_name == source_name:

                    updated_v_layer_list.append(v_layer_item)

        # update the layer list in the layer list dictionary
        abstractcommand.AbstractCommand.session_layer_lists[layer_list_id] = updated_v_layer_list

class ViewLayerProperties(abstractcommand.AbstractCommand):
    """Represents a View Layer Properties Workflow Command. Prints/returns properties for each layer of a specified
    layer list. The properties are: QgsVectorLayer Object ID, the Coordinate Reference System, the Geometry Type,
    the number of Features, the Attribute Field Names, the original spatial data file source pathname."""

    name = "View Layer Properties"
    description = "Returns the properties of the layers in a layer list."
    parameter_names = ["layer_list_id"]
    parameter_values = {"layer_list_id": None}

    def __init__(self, parameter_values):

        self.populate_parameter_values_dic(parameter_values, self.parameter_names, self.parameter_values)

    # Helper function to convert a wkbType code to a user-friendly geometry type string
    @staticmethod
    def return_wkbtype_in_lamen(wkb_type):
        """Converts the hard-to-understand wkbType id into a more readable string.

        Argument: wkbType (str or int): the wkbType id."""

        wkb_type_dic = {"0": "WKBUnknown", "1": "WKBPoint", "2": "WKBLineString", "3": "WKBPolygon",
                        "4": "WKBMultiPoint", "5": "WKBMultiLineString", "6": "WKBMultiPolygon", "100": "WKBNoGeometry",
                        "0x80000001": "WKBPoint25D", "0x80000002": "WKBLineString25D", "0x80000003": "WKBPolygon25D",
                        "0x80000004": "WKBMultiPoint25D", "0x80000005": "WKBMultiLineString25D",
                        "0x80000006": "WKBMultiPolygon25D"}

        return wkb_type_dic[str(wkb_type)]

    # Runs the View Layer Properties Workflow Command
    def run_command(self):

        layer_list_id = self.parameter_values["layer_list_id"]

        # a list that holds the properties of EACH layer in the layer list
        layer_properties = []

        # iterate over each v_layer_item in the desired v_layer_list
        for v_layer_item in abstractcommand.AbstractCommand.session_layer_lists[layer_list_id]:
            # parse the layer list item's properties
            v_layer_object, v_layer_source_path, \
            v_layer_source_name = abstractcommand.AbstractCommand.return_layer_item_properties(v_layer_item)

            # print the spatial data layer's CRS, geometry type, QgsVectorObject id, and original source pathname
            geom = ViewLayerProperties.return_wkbtype_in_lamen(v_layer_object.wkbType())
            feature_count = v_layer_object.featureCount()
            field_names = ', '.join([field.name() for field in v_layer_object.pendingFields()])
            layer_info = v_layer_object.id(), v_layer_object.crs().authid(), geom, feature_count, field_names, v_layer_source_path
            layer_properties.append(layer_info)

        # print the layer properties for each layer on a separate line
        for layer_properties in layer_properties:
            print layer_properties

        # return the layer properties
        return layer_properties

class ViewLayerListProperties(abstractcommand.AbstractCommand):
    """Represents a View Layer List Properties Workflow Command. Prints/returns properties of the specified
        layer list. The properties are: Layer List ID, Number of Layers, Boolean determining if all of the layers have
        the same CRS, Boolean determining if all of the layers have the same geometry.
        TODO this function does not work when the layer originally came from a file geodatabase"""

    name = "View Layer List Properties"
    description = "Returns the properties of a layer list."
    parameter_names = ["layer_list_id"]
    parameter_values = {"layer_list_id": None}

    def __init__(self, parameter_values):

        self.populate_parameter_values_dic(parameter_values, self.parameter_names, self.parameter_values)

    # Runs the View Layer List Properties Workflow Command
    def run_command(self):

        layer_list_id = self.parameter_values["layer_list_id"]

        # crsList holds all of the CRS for each of the layers in the layer list
        # geomList holds all of the geometry types for each of the layers in the layer list
        crs_list = []
        geom_list = []

        # iterate over each v_layer_item in the desired v_layer_list
        for v_layer_item in abstractcommand.AbstractCommand.session_layer_lists[layer_list_id]:
            # parse the layer list item's properties
            v_layer_object, v_layer_source_path, v_layer_source_name = abstractcommand.AbstractCommand.return_layer_item_properties(
                v_layer_item)

            # retrieve and append the CRS and geometry type of the QgsVectorLayer object and append to the lists
            crs_list.append(v_layer_object.crs().authid())
            geom_list.append(str(v_layer_object.wkbType()))

        # determine if all of the layers in the layer list have the same CRS
        if len(list(set(crs_list))) == 1:
            consistent_crs = True
        else:
            consistent_crs = False

        # determine if all of the layers in the layer list have the same geometry
        if len(list(set(geom_list))) == 1:
            consistent_geom = True
        else:
            consistent_geom = False

        # print/return the layer list properties
        layer_list_properties = [layer_list_id, len(abstractcommand.AbstractCommand.session_layer_lists[layer_list_id]),
                                 consistent_crs, consistent_geom]
        print layer_list_properties
        return layer_list_properties
