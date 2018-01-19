# MergeGeoLayers

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type
from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.io as io_util

import logging

from processing.tools import general


class MergeGeoLayers(AbstractCommand):

    """
    NEED TO ADD DOCUMENTATION
    """

    # Command Parameters
    # GeoLayerIDs (list of strings, required): a list of the IDs of the GeoLayers to be merged
    # OutputGeoLayerID (str, required): the ID of the GeoLayer created as the output merged layer.
    # MappingDictionary (dictionary, optional): a dictionary containing attribute mapping information. Key: the
    #   output attribute name. Value: a list of the corresponding input attribute names. By default, the
    #   MappingDictionary is an empty dictionary {"":[]}. All of the input attribute fields will be included in the
    #   Output GeoLayer's attribute table.
    # IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the OutputGeoLayerID
    #   already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
    #   (Refer to user documentation for detailed description.) Default value is `Replace`.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerIDs", type([])),
        CommandParameterMetadata("OutputGeoLayerID", type("")),
        CommandParameterMetadata("MappingDictionary", type({})),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        super(MergeGeoLayers, self).__init__()
        self.command_name = "MergeGeoLayers"
        self.command_parameter_metadata = self.__command_parameter_metadata
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters):
        pass

    def __should_geolayer_be_created(self, geolayer_id):
        """
        Checks that the ID of the GeoLayer to be created is not an existing GeoLayerList ID or an existing GeoLayer ID.
        The GeoLayer will NOT be created if ID is the same as an existing GeoLayerList ID. Depending on the
        IfGeoLayerIDExists parameter value, the GeoLayer to be created might be created even if it has the same ID as
        an existing GeoLayer ID. (See logic or user documentation for more detailed information.)

        Args:
            geolayer_id: the id of the GeoLayer to be created

        Returns:
            create_geolayer: Boolean. If TRUE, the GeoLayer should be created. If FALSE, the GeoLayer should not be
            created.

        Raises:
            None.
        """

        # Boolean to determine if the GeoLayer should be created. Set to true until an error occurs.
        create_geolayer = True

        # If the geolayer_id is the same as as already-existing GeoLayerListID, raise a FAILURE.
        if self.command_processor.get_geolayerlist(geolayer_id):

            create_geolayer = False
            self.warning_count += 1
            message = 'The GeoLayer ID ({}) value is already in use as a GeoLayerList ID.'.format(geolayer_id)
            recommendation = 'Specifiy a new GeoLayerID.'
            self.logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN,
                                           CommandLogRecord(command_status_type.FAILURE,
                                                            message, recommendation))

        # If the geolayer_id is the same as an already-registered GeoLayerID, react according to the
        # pv_IfGeoLayerIDExists value.
        elif self.command_processor.get_geolayer(geolayer_id):

            # Get the IfGeoLayerIDExists parameter value.
            pv_IfGeoLayerIDExists = self.get_parameter_value("IfGeoLayerIDExists", default_value="Replace")

            # Warnings/recommendations if the geolayer_id is the same as a registered GeoLayerID
            message = 'The GeoLayer ID ({}) value is already in use as a GeoLayer ID.'.format(geolayer_id)
            recommendation = 'Specify a new GeoLayerID.'

            # The registered GeoLayer should be replaced with the new GeoLayer (with warnings).
            if pv_IfGeoLayerIDExists.upper() == "REPLACEANDWARN":
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.WARNING,
                                                                message, recommendation))

            # The registered GeoLayer should not be replaces. A warning should be logged.
            if pv_IfGeoLayerIDExists.upper() == "WARN":
                create_geolayer = False
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.WARNING,
                                                                message, recommendation))

            # The matching IDs should cause a FAILURE.
            elif pv_IfGeoLayerIDExists.upper() == "FAIL":
                create_geolayer = False
                self.warning_count += 1
                self.logger.error(message)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE,
                                                                message, recommendation))

        return create_geolayer

    @ staticmethod
    def __get_output_attribute(input_attribute, mapping_dictionary):

        # iterate through the mapping dictionary
        for output_attribute, input_attribute_list in mapping_dictionary.iteritems():

            # if the input attribute is in the input_attribute_list, return the corresponding output_attribute
            if input_attribute in input_attribute_list:
                return output_attribute

        # if the input attribute is not found for any of the input_attribute_lists in the mapping dictionary, return the
        # input_attribute (the attribute field does not get renamed)
        return input_attribute

    def __return_output_attributes(self, geolayer, mapping_dictionary):

        # Get a list of the geolayer's attributes
        input_attributes = geolayer.get_attribute_field_names()

        # get a list of this geolayers output attributes
        output_attributes = {}

        # iterate over the geolayer's input attributes
        for input_attribute in input_attributes:

            # get the corresponding output attribute name and type
            output_attribute_name = self.__get_output_attribute(input_attribute, mapping_dictionary)
            output_attributes[input_attribute] = output_attribute_name

        return output_attributes

    def run_command(self):

        # TODO check that the geolayers are all of the same crs
        # TODO check that the geolayers are all of the same geometry

        pv_GeoLayerIDs = self.get_parameter_value("GeoLayerIDs")
        pv_OutputGeoLayerID = self.get_parameter_value("OutputGeoLayerID")
        pv_MappingDictionary = self.get_parameter_value("MappingDictionary")

        # Convert the MappingDictionary parameter from string format to dictionary format.
        if pv_MappingDictionary:
            mapping_dictionary = io_util.string_to_dictionary(pv_MappingDictionary)
        else:
            mapping_dictionary = {"": []}

        # Convert the GeoLayerIDs parameter from string format to list format.
        list_of_geolayer_ids = io_util.string_to_list(pv_GeoLayerIDs)

        # Place holder lists
        # TODO need to explain these placeholders
        list_of_crs = []
        list_of_geom = []
        copied_geolayer_ids = []
        copied_geolayer_qgsvectorlayers = []

        # Iterate over the GeoLayers to be merged.
        for geolayer_id in list_of_geolayer_ids:

            # Check that the GeoLayerID is a valid GeoLayer ID.
            if self.command_processor.get_geolayer(geolayer_id):

                # Get the appropriate GeoLayer based on the GeoLayer ID.
                geolayer = self.command_processor.get_geolayer(geolayer_id)

                # Get the GeoLayer's coordinate reference system
                list_of_crs.append(geolayer.get_crs())

                # Get the GeoLayer's geometry
                list_of_geom.append(geolayer.get_geometry_qgis())

                # Get list of output attributes
                attribute_dictionary = self.__return_output_attributes(geolayer, mapping_dictionary)

                # Make a copy of the GeoLayer
                copied_geolayer_id = "{}_copyForMerge".format(geolayer_id)
                self.command_processor.copy_geolayer(existing_geolayer_id=geolayer_id,
                                                     copied_geolayer_id=copied_geolayer_id)

                # Add the copied GeoLayer ID to the copied geolayer list.
                copied_geolayer_ids.append(copied_geolayer_id)

                # Get the copied GeoLayer based on the GeoLayer ID.
                copied_geolayer = self.command_processor.get_geolayer(copied_geolayer_id)

                # Iterate over the attribute dictionary
                for input_attribute, output_attribute in attribute_dictionary.iteritems():

                    # If the output attribute should be different than the input attribute, rename the attribute to
                    # the output attribute.
                    if not input_attribute == output_attribute:
                        copied_geolayer.rename_attribute(input_attribute, output_attribute)

                # Add the qgsvectorlayer objects of the renamed copied GeoLayers to a master list.
                copied_geolayer_qgsvectorlayers.append(copied_geolayer.qgs_vector_layer)

        # Check if the OutputGeoLayer should be created. Continue if TRUE. Error handling dealt with inside
        # the `__should_geolayer_be_created` method.
        if self.__should_geolayer_be_created(pv_OutputGeoLayerID):

            try:
                # Merge all of the copied GeoLayers (the GeoLayers with the new attribute names)
                # saga:mergelayers documentation at http://www.saga-gis.org/saga_tool_doc/2.3.0/shapes_tools_2.html
                merged_output = general.runalg("saga:mergelayers", copied_geolayer_qgsvectorlayers, True, False, False)

                # Create a new GeoLayer and add it to the GeoProcessor's geolayers list.
                # merged_output["MERGED"] returns the full file pathname of the memory output layer (saved
                # in a QGIS temporary folder)
                qgs_vector_layer = qgis_util.read_qgsvectorlayer_from_file(merged_output["MERGED"])
                new_geolayer = GeoLayer(pv_OutputGeoLayerID, qgs_vector_layer, "MEMORY")
                self.command_processor.add_geolayer(new_geolayer)

                # Release the copied GeoLayers from the GeoProcessor's geolayers list.
                for copied_geolayer_id in copied_geolayer_ids:

                    # Get the copied GeoLayer based on the GeoLayer ID.
                    copied_geolayer = self.command_processor.get_geolayer(copied_geolayer_id)

                    # Remove the copied GeoLayer from the GeoProcessor
                    self.command_processor.free_geolayer(copied_geolayer)

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error merging the following GeoLayers {}.".format(copied_geolayer_ids)
                recommendation = "Check the log file for details."
                self.logger.exception(message, e)
                self.command_status.add_to_log(command_phase_type.RUN,
                                               CommandLogRecord(command_status_type.FAILURE, message,
                                                                recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
