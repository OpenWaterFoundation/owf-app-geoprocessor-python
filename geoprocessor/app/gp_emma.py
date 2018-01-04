# Main GeoProcessor application
# - This is Emma's version. Eventually this Python file will be deleted and all code for the Main GeoProcessor
# application will be included in the gp.py Python file. This is just a developer test environment for Emma in order to
# interact with the code.
# - this is a prototype to explore the design
# - functionality is stubbed in

import geoprocessor.core.GeoProcessor as GeoProcessor
import os


if __name__ == "__main__":

    cmdFileDir = (os.path.dirname(os.path.realpath(__file__))).replace(r"\app", r"\command_files")
    processor = GeoProcessor.GeoProcessor()
    processor.process_command_file(os.path.join(cmdFileDir, "create_layers_test.txt"))
    print processor.GeoLayers
    print processor.GeoLists

    for GeoLayer in processor.GeoLayers:
        print GeoLayer.id, GeoLayer.source_path
