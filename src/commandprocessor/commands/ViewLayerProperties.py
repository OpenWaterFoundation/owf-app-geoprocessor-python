from commandprocessor.util import abstractcommand

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
