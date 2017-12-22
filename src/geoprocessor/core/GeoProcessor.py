import geoprocessor.core.GeoProcessorCommandFactory as CommandFactory
import geoprocessor.util.CommonUtil as CommonUtil
from qgis.core import QgsApplication
from processing.core.Processing import Processing
import os

class GeoProcessor():
    """Overarching class that performs the work of the geoprocessing tool."""

    def __init__(self):

        # command list: holds all command objects called from the input command file
        self.commands = []

        # property dictionary: holds all geoprocessor properties
        # temp_dir: the full pathname to the folder that will hold all temporary, intermediate files created by the
        # geoprocessor
        # qgis_prefix_path: the full pathname to the qgis install folder (often C:\OSGeo4W\apps\qgis)
        self.properties = {"temp_dir": None,
                           "qgis_prefix_path": None}

        # geolayer dictionary: holds all of the geoprocessor geolayers
        # key: geolayer id
        # value: list of geolayer properties
        # list item1: the QGSVectorLayer object, list item2: the full pathname to the original source spatial data file
        self.geolayers = {}

        # geolist dictionary: holds all of the geoprocessor geolists
        # key: geolist id
        # value: list of geolayer ids
        self.geolists = {}

        # set properties
        self.set_property("temp_dir", r"C:\Users\intern1\Desktop\OWF_spatialProcessor\temp")
        self.set_property("qgis_prefix_path", r"C:\OSGeo4W\apps\qgis")

    def get_property(self, property_name):
        """Get a geoprocessor property."""

        return self.properties[property_name]

    def read_command_file(self, command_file):
        """Read a command file and initialize the command list in the geoprocessor."""

        # start an instance of the Command Factory
        command_factory_object = CommandFactory.GeoProcessorCommandFactory()

        # get a list of command file strings (each line of the command file is its own item in the list)
        command_file_strings = CommonUtil.to_command_string_list(command_file)

        # iterate over each line in the command file
        for command_file_string in command_file_strings:

            # initialize the command object (without parameters)
            # work is done in the GeoProcessorCommandFactory class
            command_object = command_factory_object.new_command(command_file_string, True)

            # initialize the parameters of the command object
            # work is done in the AbstractCommand class
            command_object.initialize_command(command_file_string, self, True)

            # append the initialized command (object with parameters) to the geoprocessor command list
            self.commands.append(command_object)

    def run_commands(self):
        """Run the commands (object with set parameters) that exist in the processor."""

        # Initialize QGIS resources to utilize QGIS functionality.
        QgsApplication.setPrefixPath(self.get_property("qgis_prefix_path"), True)
        qgs = QgsApplication([], True)
        qgs.initQgis()
        Processing.initialize()

        # work is done in the command's class under the run_command function
        for command_object in self.commands:
            command_object.run_command()

        # Close QGIS resources
        qgs.exit()

    def process_command_file(self, command_file):
        """Reads the command file and runs the commands within the command file."""

        self.read_command_file(command_file)
        self.run_commands()

    def set_property(self, property_name, property_value):
        """Set a geoprocessor property"""
        self.properties[property_name] = property_value

####################### WORKING ENVIRONMENT ###############################
if __name__ == "__main__":

    cmdFileDir = (os.path.dirname(os.path.realpath(__file__))).replace("core", "command_files")
    processor = GeoProcessor()
    processor.process_command_file(os.path.join(cmdFileDir, "create_layers_test.txt"))
    print processor.geolayers
