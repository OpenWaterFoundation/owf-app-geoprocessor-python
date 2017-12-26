# Main GeoProcessor application
# - this is a prototype to explore the design
# - functionality is stubbed in

import geoprocessor.core.GeoProcessor as GeoProcessor

if __name__ == '__main__':
    # Simulate case where a command file is opened via the command line.
    # First declare a processor.
    geoprocessor = GeoProcessor.GeoProcessor()
    # Set a property to show how properties work.
    geoprocessor.set_property("User","GeoProcessor user")
    # For initial development hard-code a command file in memory.
    # TODO smalers 2017-12-23 need to enable testing with command files
    command_file_strings = [
        'Message(Message="Start command file")',
        '# SetProperty(PropertyName="Property1",PropertyType="String",PropertyValue="test property")',
        '# For(Name="for_outer")',
        '#     Message(Message="message in outer loop")',
        '#     For(Name="for_inner")',
        '#         Message(Message="message in inner loop")',
        '#     EndFor(Name="for_inner")',
        '# EndFor(Name="for_outer")',
        '# If(Name="if1")',
        '#     JunkXXX()',
        '# EndIf(Name="if1")',
        'Message(Message="End command file")']
    geoprocessor.set_command_strings(command_file_strings)
    # Run the commands
    geoprocessor.run_commands()