import os
from processing.tools import general
from commandprocessor.commands import CreateLayerList
from commandprocessor.util import abstractcommand

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
        CreateLayerList.CreateLayerList([temp_output_file_list, 'temp_clip']).run_command()
