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
        'SetProperty(PropertyName="Property1",PropertyType="str",PropertyValue="test property")',
        'Message(Message="Test message with Property1=${Property1}")',
        'For(Name="for_outer",IteratorProperty="ForOuterProperty",SequenceStart="1",SequenceEnd="3",SequenceIncrement="1")',
        '  Message(Message="In outer loop, ${ForOuterProperty}")',
        '  For(Name="for_inner",IteratorProperty="ForInnerProperty",SequenceStart="10.0",SequenceEnd="11.5",SequenceIncrement=".5")',
        '    Message(Message="In inner loop")',
        '  EndFor(Name="for_inner")',
        'EndFor(Name="for_outer")',
        'If(Name="if1")',
        '  JunkXXX()',
        'EndIf(Name="if1")',
        'Message(Message="End command file")']
    geoprocessor.set_command_strings(command_file_strings)
    # Run the commands
    geoprocessor.run_commands()
    # Print some information at the end (will display in UI when that is enabled)
    # Print the processor properties
    for property_name in geoprocessor.properties:
        print('Processor property "' + property_name + '="' + str(geoprocessor.properties[property_name]) + '"')