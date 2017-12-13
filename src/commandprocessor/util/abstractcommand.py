from abc import ABCMeta, abstractmethod, abstractproperty
import os

# AbstractCommand holds the abstract structure of each command called within the spatial processor. This class defines
# the required elements of a spatial processor command.
class AbstractCommand:
    """The abstract structure of each spatial processor command. Python uses the ABCMeta class to define an Abstract
    Base Class (ABC). An ABC cannot be initialized because it is an abstract set of structural rules. These rules are
    explained in detail below:

        ALL command classes SHARE:
        (1) session_layer_lists: A dictionary, contains all of the layer lists created in the current session. The
        layer list value is the layer list id given to the layer list in the owf_commands.CreateLayerList command.
        (2) temp_folder: A string, the full pathname to a folder on the local machine. Intermediate files are written
        to this folder while a session is running. After a session has been completed, all files in this directory are
        deleted. (eventually this setting will be configured within a SPTool configuration file.)

        EACH command class REQUIRES the following PROPERTIES:
        (1) name: A string, the name of the command
        (2) description: A string, a brief description of the command's functionality
        (3) parameter_names: A list, a list of the required and optional parameter names in order expected to be
        entered from the user
        (4) parameter_values: A dictionary, a key-value object that links each parameter name (dictionary key) to the
        set parameter value (dictionary value). All values are set to None until the command is initialized.

        EACH command class REQUIRES the following METHODS:
        (1) run_command: reads the parameter values and executes the designed command task

        EACH command CAN utilize the following METHODS:
        (1) populate_parameter_values_dic: given input parameter values from the user, this function will assign those
        parameter values to the appropriate parameter name in the parameter values dictionary and return the parameter
        values dictionary to be assigned to the class instance
        (2) return_layer_item_properties: given a layer list item, this function will return the QgsVectorLayer Object,
        the full pathname to the source spatial data file and the name of the spatial data file (without the path or
        extension)"""

    __metaclass__ = ABCMeta

    session_layer_lists = {}
    temp_folder = r"C:\Users\intern1\Desktop\temp"

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def description(self):
        pass

    @abstractproperty
    def parameter_names(self):
        pass

    @abstractproperty
    def parameter_values(self):
        pass

    @abstractmethod
    def run_command(self):
        pass

    @staticmethod
    def populate_parameter_values_dic(input_parameter_values, parameter_names,  parameter_values):
        """Given input parameter values from the user, this function will assign those parameter values to the
        appropriate parameter name in the parameter values dictionary and return the parameter values dictionary to be
        assigned to the class instance.

            :param input_paramater_values: A list, an instance variable for the specific command that lists the input
            parameters issued by the user
            :param parameter_names: A list, a class variable for the specific command that lists the parameter names
            :param parameter_values: A dictionary, an instance variable for the specific command that maps the command's
            parameter names to the user's input parameter values. Dictionary values defaulted to None until this
            command is run. """

        # iterate over the users input parameter values
        for parameter_value_pos in range(0, len(input_parameter_values)):

            # get the associated parameter name for the input parameter value
            parameter_name = parameter_names[parameter_value_pos]

            # assign the input parameter value to the value of the parameter value dictionary given the parameter name
            # as the dictionary key
            input_parameter_value = input_parameter_values[parameter_value_pos]
            parameter_values[parameter_name] = input_parameter_value

            # move to the next input parameter value
            parameter_value_pos += 1

        # return the populated parameter_values dictionary t
        return parameter_values

    @staticmethod
    def return_layer_item_properties(layer_list_item):
        """Given a layer list item, this function will return the QgsVectorLayer Object, the full pathname to the
        source spatial data file and the name of the spatial data file (without the path or extension)"""

        # the QGSVectorLayer object is stored as the first entry of the layer list item
        v_layer_object = layer_list_item[0]

        # the source pathname is stored as the second entry of the layer list item
        v_layer_source_path = layer_list_item[1]
        v_layer_source_name = (os.path.basename(v_layer_source_path)).rsplit('.', 1)[0]

        # return the QgsVectorLayer Object, the full pathname to the source spatial data file and the name of the
        # spatial data file (without the path or extension)
        return v_layer_object, v_layer_source_path, v_layer_source_name






