from commandprocessor.core import abstractcommand
from commandprocessor.commands import owf_commands
from processing.tools import general
import os

class QgisClip(abstractcommand.AbstractCommand):
    """Represents a QGIS: Clip Workflow Command. Clips the layers of one layer list by the layer of another layar list.
     The clipped output layers are stored in a temporary layer list (temp_clip)."""

    name = "Qgis: Clip"
    description = "Clips the layers of a layer list by the layers of another layer list."
    parameter_names = ["input_layer_list_id", "clip_layer_list_id"]
    parameter_values = {"input_layer_list_id": None, "clip_layer_list_id": None}

    def __init__(self, parameter_values):

        self.populate_parameter_values_dic(parameter_values, self.parameter_names, self.parameter_values)

    # Runs the QGIS: Clip Workflow Command
    def run_command(self):

        input_layer_list_id = self.parameter_values["input_layer_list_id"]
        clip_layer_list_id = self.parameter_values["clip_layer_list_id"]

        # holds a list of all clipped output layers - these are temp files
        temp_output_file_list = []

        # iterate over each v_layer_item in the desired v_layer_list - input
        for v_layer_item_input in abstractcommand.AbstractCommand.session_layer_lists[input_layer_list_id]:

            # parse the layer list item's properties - input
            v_layer_object_input, v_layer_source_path_input, \
            v_layer_source_name_input = abstractcommand.AbstractCommand.return_layer_item_properties(v_layer_item_input)

            # iterate over each v_layer_item in the desired v_layer_list - clip
            for v_layer_item_clip in abstractcommand.AbstractCommand.session_layer_lists[clip_layer_list_id]:
                # parse the layer list item's properties - clip
                v_layer_object_clip, v_layer_source_path_clip, \
                v_layer_source_name_clip = abstractcommand.AbstractCommand.return_layer_item_properties(v_layer_item_clip)

                # clip the input_v_layer by the clip_v_layer. the output clipped product will include the name of the
                # input layer and the clip layer. the output product is stored as a geojson file in the temporary
                # folder. append the clipped output layer to the temp_output_file_list
                output_fullpath = os.path.join(
                    abstractcommand.AbstractCommand.temp_folder, "{}_{}_clipped.geojson".format
                    (v_layer_source_name_input, v_layer_source_name_clip))
                clipped_temp = general.runalg("qgis:clip", v_layer_object_input, v_layer_object_clip, output_fullpath)
                temp_output_file_list.append(clipped_temp['OUTPUT'])

        # create a new layer list with layer list id (temp_clip) to hold the clipped output products
        owf_commands.CreateLayerList([temp_output_file_list, 'temp_clip']).run_command()

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
        owf_commands.CreateLayerList([temp_output_file_list, 'temp_simplify']).run_command()

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
        owf_commands.CreateLayerList([temp_output_file_list, 'temp_extract_a']).run_command()

