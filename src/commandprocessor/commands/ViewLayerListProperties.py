from commandprocessor.util import abstractcommand

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
