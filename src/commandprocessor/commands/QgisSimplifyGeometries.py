import os
from processing.tools import general
from commandprocessor.commands import CreateLayerList
from commandprocessor.util import abstractcommand


class QgisSimplifyGeometries(abstractcommand.AbstractCommand):

    name = "Qgis: Simplify Geometries"
    description = "Simplifies the layers of a layer list by the simplification tolerance."
    parameter_names = ["layer_list_id", "simplification_tolerance"]
    parameter_values = {"layer_list_id": None, "simplification_tolerance": None}

    def __init__(self, parameter_values):
        self.populate_parameter_values_dic(parameter_values, self.parameter_names, self.parameter_values)


    def run_command(self):

        layer_list_id = self.parameter_values["layer_list_id"]
        simplification_tolerance = self.parameter_values["simplification_tolerance"]

        # holds a list of all simplified output layers - these are temp files
        temp_output_file_list = []

        # iterate over each v_layer_item in the desired v_layer_list
        for v_layer_item in abstractcommand.AbstractCommand.session_layer_lists[layer_list_id]:
            # parse the layer list item's properties
            v_layer_object, v_layer_source_path, v_layer_source_name = abstractcommand.AbstractCommand.return_layer_item_properties(
                v_layer_item)

            # simplify the v_layer by the simplification tolerance. the output simplified product will include the name
            # of the input layer and the simplification tolerance. the output product is stored as a geojson file in
            # the temporary folder. append the simplified output layer to the temp_output_file_list
            output_fullpath = os.path.join(abstractcommand.AbstractCommand.temp_folder,
                                           "{}_{}_simplified.geojson".format(
                                               v_layer_source_name, str(simplification_tolerance)))
            simplified_temp = general.runalg("qgis:simplifygeometries", v_layer_object, simplification_tolerance,
                                             output_fullpath)
            temp_output_file_list.append(simplified_temp['OUTPUT'])

        # create a new layer list with layer list id (temp_simplify) to hold the simplified output products
        CreateLayerList.CreateLayerList([temp_output_file_list, 'temp_simplify']).run_command()
