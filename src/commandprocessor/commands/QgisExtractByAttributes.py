import os
from processing.tools import general
from commandprocessor.util import abstractcommand
from commandprocessor.commands import CreateLayerList

class QgisExtractByAttributes(abstractcommand.AbstractCommand):

    name = "Qgis: Extract By Attribute"
    description = "Extracts features from the layers of a layer list by the given expressions."
    parameter_names = ["layer_list_id", "expression"]
    parameter_values = {"layer_list_id": None, "expression": None}

    def __init__(self, parameter_values):
        self.populate_parameter_values_dic(parameter_values, self.parameter_names, self.parameter_values)

    def run_command(self):

        layer_list_id = self.parameter_values["layer_list_id"]
        expression = self.parameter_values['expression']

        # holds a list of all simplified output layers - these are temp files
        temp_output_file_list = []

        # iterate over each v_layer_item in the desired v_layer_list
        for v_layer_item in abstractcommand.AbstractCommand.session_layer_lists[layer_list_id]:

            # parse the layer list item's properties
            v_layer_object, v_layer_source_path, v_layer_source_name = abstractcommand.AbstractCommand.return_layer_item_properties(v_layer_item)

            # parse the expression's properties
            field = expression.split(',')[0]
            operator = int(expression.split(',')[1])
            value = expression.split(',')[2]

            output_fullpath = os.path.join(abstractcommand.AbstractCommand.temp_folder, "{}_extracted.geojson".format(
                v_layer_source_name))
            extract_attr_temp = general.runalg("qgis:extractbyattribute", v_layer_object,
                                               field, operator, value, output_fullpath)
            temp_output_file_list.append(extract_attr_temp['OUTPUT'])

        # create a new layer list with layer list id (temp_extract_a) to hold the simplified output products
        CreateLayerList.CreateLayerList([temp_output_file_list, 'temp_extract_a']).run_command()
