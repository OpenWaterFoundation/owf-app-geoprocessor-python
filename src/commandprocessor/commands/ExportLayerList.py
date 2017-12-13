import os
from qgis.core import QgsVectorFileWriter, QgsCoordinateReferenceSystem
from commandprocessor.util import abstractcommand

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
