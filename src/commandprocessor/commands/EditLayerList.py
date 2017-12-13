from commandprocessor.util import abstractcommand

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
