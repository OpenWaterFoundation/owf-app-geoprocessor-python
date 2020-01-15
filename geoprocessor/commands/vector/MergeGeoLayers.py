# MergeGeoLayers - command to merge GeoLayers
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2020 Open Water Foundation
# 
# GeoProcessor is free software:  you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     GeoProcessor is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with GeoProcessor.  If not, see <https://www.gnu.org/licenses/>.
# ________________________________________________________________NoticeEnd___

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType
from geoprocessor.core.VectorGeoLayer import VectorGeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validator_util

import logging
import os

from plugins.processing.tools import general


class MergeGeoLayers(AbstractCommand):
    """
    Merges GeoLayers with the same geometry into one output GeoLayer.

    * All features from the input GeoLayers are retained within the output GeoLayer.
    * The attributes of the input GeoLayers are retained within the output GeoLayer attribute tables.
    * Attributes that share the same name will be converged in the output GeoLayer attribute tables.
    * Attributes that are unique to an input GeoLayer are included in the output GeoLayer attribute tables - features
        from GeoLayers that don't have that unique attribute will have an attribute value of '0' for that unique field.
    * Attributes from different input GeoLayers (with different names) that are meant to be converged in the output
        GeoLayer can be managed with the AttributeMap.

    Command Parameters
    * GeoLayerIDs (list of strings, required): a list of the IDs of the GeoLayers to be merged. Can be '*' where all
        registered GeoLayers within the GeoProcessor are merged.
    * OutputGeoLayerID (string, required): the ID of the output GeoLayer, the merged GeoLayer.
    * AttributeMap (string, optional): a string that can convert to a list. Each item is separated by a comma.
        Each item is an entry pair separated by a ':'.
        The key of the pair is the old attribute name to be renamed.
        The value of the pair is the new name that the old attribute will be mapped to in the merged output GeoLayer.
        Default = ""
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the OutputGeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("GeoLayerIDs", type([])),
        CommandParameterMetadata("OutputGeoLayerID", type("")),
        CommandParameterMetadata("AttributeMap", type({})),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "MergeGeoLayers"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = dict()
        self.command_metadata['Description'] = "Merge two or more GeoLayers into one GeoLayer."
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # GeoLayerIDs
        self.parameter_input_metadata['GeoLayerIDs.Description'] =\
            "comma-separated list of identifiers for GeoLayers to merge"
        self.parameter_input_metadata['GeoLayerIDs.Label'] = "GeoLayersIDs"
        self.parameter_input_metadata['GeoLayerIDs.Required'] = True
        self.parameter_input_metadata['GeoLayerIDs.Tooltip'] = (
            "A comma-separated list of the identifiers of the GeoLayers to merge. \n\n"
            "GeoLayerID1, GeoLayerID2, ... \n\n"
            "Can also be * where all GeoLayers registered within the GeoProcessor are merged. "
            "${Property} syntax is recognized.")
        # OutputGeoLayerID
        self.parameter_input_metadata['OutputGeoLayerID.Description'] = "output GeoLayerID"
        self.parameter_input_metadata['OutputGeoLayerID.Label'] = "Output GeoLayerID"
        self.parameter_input_metadata['OutputGeoLayerID.Required'] = True
        self.parameter_input_metadata['OutputGeoLayerID.Tooltip'] = "A GeoLayer identifier for the output GeoLayer."
        # AttributeMap
        self.parameter_input_metadata['AttributeMap.Description'] = "new names for the output geolayer attributes"
        self.parameter_input_metadata['AttributeMap.Label'] = "Attribute map"
        self.parameter_input_metadata['AttributeMap.Tooltip'] = (
            "Specify new names for the output geolayer attributes.\n\n"
            "OriginalAttributeName1:MergedAttributeName1, \n"
            "OriginalAttributeName2:MergedAttributeName2 \n\n"
            "See the Attribute Map section for more information.")
        self.parameter_input_metadata['AttributeMap.Value.Default.Description'] = "original attribute names"
        # IfGeoLayerIDExists
        self.parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID exists"
        self.parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = (
            "The action that occurs if the OutputGeoLayerID already exists within the GeoProcessor. \n"
            "Replace : The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer. "
            "No warning is logged. \n"
            "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer. "
            "A warning is logged. \n"
            "Warn : The new GeoLayer is not created. A warning is logged. \n"
            "Fail : The new GeoLayer is not created. A fail message is logged.")
        self.parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
        self.parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters: dict) -> None:
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns: None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """

        warning = ""

        # Check that parameter GeoLayerIDs is a non-empty, non-None string.
        pv_GeoLayerIDs = self.get_parameter_value(parameter_name='GeoLayerIDs', command_parameters=command_parameters)

        if not validator_util.validate_string(pv_GeoLayerIDs, False, False):
            message = "GeoLayerIDs parameter has no value."
            recommendation = "Specify the GeoLayerIDs parameter to indicate the GeoLayers to merge."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that parameter OutputGeoLayerID is a non-empty, non-None string.
        pv_OutputGeoLayerID = self.get_parameter_value(parameter_name='OutputGeoLayerID',
                                                       command_parameters=command_parameters)

        if not validator_util.validate_string(pv_OutputGeoLayerID, False, False):
            message = "OutputGeoLayerID parameter has no value."
            recommendation = "Specify the OutputGeoLayerID parameter to indicate the ID of the merged GeoLayer."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            self.logger.warning(warning)
            raise ValueError(warning)

        # Refresh the phase severity
        self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def __should_merge(self, geolayer_id_list: [str], output_geolayer_id: str) -> bool:
        """
        Checks the following:
        * the input GeoLayer IDs are existing GeoLayer IDs
        * the input GeoLayers are all the same CRS (warning)
        * the input GeoLayers are all the same geometry.
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)

       Args:
           geolayer_id_list (list of strings): a list of the input GeoLayer IDs, the GeoLayers to merge
           output_geolayer_id (str): the ID of the output GeoLayer, the merged GeoLayer.

       Returns:
           run_merge: Boolean. If TRUE, the merge process should be run. If FALSE, it should not be run.
       """

        # Boolean to determine if the merge process should be run. Set to true until an error occurs.
        run_merge = True

        # Boolean to determine if all of the input GeoLayers exist within the GeoProcessor. TRUE until proven FALSE.
        input_geolayers_exist = True

        # Iterate over the input GeoLayer IDs
        for geolayer_id in geolayer_id_list:

            # If the GeoLayer ID is not an existing GeoLayer ID, raise a FAILURE.
            if not self.command_processor.get_geolayer(geolayer_id):

                run_merge = False
                input_geolayers_exist = False
                self.warning_count += 1
                message = 'The GeoLayerID ({}) is not a valid GeoLayer ID.'.format(geolayer_id)
                recommendation = 'Specify a valid GeoLayerID.'
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # If all of the input GeoLayers exist, check that the they have the same CRS and the same geometry.
        if input_geolayers_exist:

            # A list of the GeoLayer's geometries and a list of teh GeoLayer's CRS.
            geom_list = []
            crs_list = []

            # Iterate over the input GeoLayers.
            for geolayer_id in geolayer_id_list:

                # Get the GeoLayer.
                geolayer = self.command_processor.get_geolayer(geolayer_id)

                # Get the GeoLayer's geometry.
                geom_list.append(geolayer.get_geometry())

                # Get the GeoLayer's CRS.
                crs_list.append(geolayer.get_crs())

            # If the input GeoLayers have different geometries, raise a FAILURE.
            if len(set(geom_list)) > 1:

                run_merge = False
                self.warning_count += 1
                message = 'The input GeoLayers ({}) have different geometries ({}).'.format(geolayer_id_list, geom_list)
                recommendation = 'Specify input GeoLayers that have the same geometry.'
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

            # If the input GeoLayers have different CRS, raise a WARNING.
            if len(set(crs_list)) > 1:

                self.warning_count += 1
                message = 'The input GeoLayers ({}) have different coordinate' \
                          ' reference systems ({}).'.format(geolayer_id_list, geom_list)
                recommendation = 'Specify input GeoLayers that have the same CRS.'
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING, message, recommendation))

        # If the output_geolayer_id is the same as an already-registered GeoLayerID, react according to the
        # pv_IfGeoLayerIDExists value.
        elif self.command_processor.get_geolayer(output_geolayer_id):

            # Get the IfGeoLayerIDExists parameter value.
            pv_IfGeoLayerIDExists = self.get_parameter_value("IfGeoLayerIDExists", default_value="Replace")

            # Warnings/recommendations if the geolayer_id is the same as a registered GeoLayerID
            message = 'The GeoLayer ID ({}) value is already in use as a GeoLayer ID.'.format(output_geolayer_id)
            recommendation = 'Specify a new GeoLayerID.'

            # The registered GeoLayer should be replaced with the new GeoLayer (with warnings).
            if pv_IfGeoLayerIDExists.upper() == "REPLACEANDWARN":

                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING, message, recommendation))

            # The registered GeoLayer should not be replaces. A warning should be logged.
            if pv_IfGeoLayerIDExists.upper() == "WARN":

                run_merge = False
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.WARNING, message, recommendation))

            # The matching IDs should cause a FAILURE.
            elif pv_IfGeoLayerIDExists.upper() == "FAIL":

                run_merge = False
                self.warning_count += 1
                self.logger.warning(message)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Return the Boolean to determine if the merge process should be run. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return run_merge

    @ staticmethod
    def __create_attribute_dictionary(geolayer: VectorGeoLayer, attribute_map: dict) -> dict:
        """
        Create an attribute dictionary for the GeoLayer.

        * An attribute dictionary is a dictionary of entries that determines how/if the attribute names should be
         renamed.
            Each entry represents one of the GeoLayer's attributes.
            Key: the name of the existing GeoLayer attribute.
            Value: the name that the GeoLayer attribute should be renamed to.
        * The values of the attribute dictionary are determined by the logic within the attribute_map.
        * The attribute map is a user-defined dictionary that determines how the input GeoLayers' attributes
         should be manipulated in the merged output GeoLayer.
            Each entry represents one of the output GeoLayer's attributes.
            Key: the name of the attribute in output GeoLayer
            Value: a list of existing input GeoLayer attributes that should be renamed to the corresponding key

        Args:
            geolayer (object): the input GeoLayer
            attribute_map (dictionary): a dictionary of how/if the input GeoLayer's attributes should be renamed

        Returns:
            attribute_dictionary (dictionary). Read description above.
        """

        # Get a list of the GeoLayer's existing attribute names.
        existing_attribute_names = geolayer.get_attribute_field_names()

        # A dictionary of entries that determines how/if the existing attribute names should be renamed.
        attribute_dictionary = {}

        # Iterate over each of GeoLayer's existing attributes.
        for existing_attribute_name in existing_attribute_names:

            # Boolean to determine if the existing_attribute_name should be renamed. Set to FALSE until proven TRUE.
            should_be_renamed = False

            # Iterate over the attribute map.
            for new_attr_name, list_of_existing_attr_names_to_rename in attribute_map.items():

                # If the existing attribute name should be renamed then return the new name.
                if existing_attribute_name in list_of_existing_attr_names_to_rename:
                    should_be_renamed = True
                    output_attribute_name = new_attr_name
                    break

            # If the existing attribute name should not be renamed, return the existing attribute name.
            if not should_be_renamed:
                output_attribute_name = existing_attribute_name

            # Add the key, value pair to the attribute dictionary.
            attribute_dictionary[existing_attribute_name] = output_attribute_name

        # Return the attribute dictionary.
        return attribute_dictionary

    def run_command(self) -> None:

        # Get the command parameter values.
        pv_GeoLayerIDs = self.get_parameter_value("GeoLayerIDs")
        pv_OutputGeoLayerID = self.get_parameter_value("OutputGeoLayerID")
        pv_AttributeMap = self.get_parameter_value("AttributeMap", default_value="")

        # Expand for ${Property} syntax.
        pv_GeoLayerIDs = self.command_processor.expand_parameter_value(pv_GeoLayerIDs, self)

        # Convert the AttributeMap parameter from string to a list of mapping entries.
        attribute_map_entry_list = string_util.delimited_string_to_list(pv_AttributeMap, delimiter=',')

        # The attribute map dictionary contains the attributes of the output merged GeoLayer and the corresponding
        # attributes of the input GeoLayers.
        # key (str): an attribute of the output, merged GeoLayer
        # value (list): a list of attributes from the input GeoLayers that should be mapped to the output attribute
        attribute_map_dic = {}

        # Iterate over each attribute mapping entry.
        for attribute_map_entry in attribute_map_entry_list:

            # Get a list of the keys (merged attributes) currently in the attribute map dictionary.
            curr_merged_attributes = list(attribute_map_dic.keys())

            # If the attribute map entry has the correct format, continue.
            if ':' in attribute_map_entry:

                # Get the output merged attribute name from the entry.
                merged_attr = attribute_map_entry.split(':')[1].strip()

                # Get the input attribute name from the entry.
                input_attr = attribute_map_entry.split(':')[0].strip()

            # If the attribute map entry does has the correct format, the merged_attr and the input_attr variables
            # are set to empty strings.
            else:
                merged_attr = ''
                input_attr = ''

            # If the merged attribute name is already registered in the attribute mapping dictionary.
            if merged_attr in curr_merged_attributes:

                # Add the input attribute to the list of input attributes within the dictionary (associated with
                # the corresponding merged_attribute).
                curr_input_attrs = attribute_map_dic[merged_attr]
                curr_input_attrs.append(input_attr)
                attribute_map_dic[merged_attr] = curr_input_attrs

            # If the merged attribute is not already registered in the attribute mapping dictionary, add the input
            # attribute (as a one-item list) to the dictionary (associated with the corresponding merged_attribute).
            else:
                attribute_map_dic[merged_attr] = [input_attr]

        # Convert the GeoLayerIDs parameter from string to list format.
        # If configured, list all of the registered GeoLayer IDs.
        if pv_GeoLayerIDs == "*":
            list_of_geolayer_ids = []

            # Iterate over each GeoLayer registered within the GeoProcessor. Add each GeoLayer's ID to the list.
            for geolayer_obj in self.command_processor.geolayers:
                list_of_geolayer_ids.append(geolayer_obj.id)

        # If specific GeoLayer IDs are listed, convert the string into list format.
        else:
            list_of_geolayer_ids = string_util.delimited_string_to_list(pv_GeoLayerIDs)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_merge(list_of_geolayer_ids, pv_OutputGeoLayerID):

            try:

                # A list to hold the GeoLayer IDs of the copied GeoLayers. Copied GeoLayers are only required for this
                # command. They will be removed from the GeoProcessor (to save processing space and speed) after the
                # processing has been completed. This list will be used to remove the copied GeoLayers.
                copied_geolayer_ids = []

                # A list to hold the full pathname of the copied GeoLayers (written to disk). The
                # qgis:mergevectorlayers requires that the QGSVectorLayer objects are not in memory. This list will be
                # used as an input to the qgis:mergevectorlayers algorithm.
                copied_geolayer_sourcepath = []

                first_geolayer = self.command_processor.get_geolayer(list_of_geolayer_ids[0])
                first_crs = first_geolayer.get_crs()

                # Iterate over the GeoLayers to be merged.
                for geolayer_id in list_of_geolayer_ids:

                    # Get the appropriate GeoLayer based on the GeoLayer ID.
                    geolayer = self.command_processor.get_geolayer(geolayer_id)

                    # Get an attribute dictionary mapping the GeoLayer attributes that are to be renamed.
                    # Key: Existing attribute name. Value: New attribute name.
                    attribute_dictionary = self.__create_attribute_dictionary(geolayer, attribute_map_dic)

                    # Make a copy of the GeoLayer and add it to the GeoProcessor. Renaming of attributes will occur on
                    # a copy of the GeoLayer so that the original GeoLayer's attribute values are not affected.
                    copied_geolayer = geolayer.deepcopy("{}_copyForMerge".format(geolayer_id))
                    self.command_processor.add_geolayer(copied_geolayer)

                    # Add the copied GeoLayer ID to the master list.
                    copied_geolayer_ids.append(copied_geolayer.id)

                    # Iterate over the GeoLayer's attribute dictionary.
                    for existing_attr_name, new_attr_name in attribute_dictionary.items():

                        # If the attribute should be renamed, then rename the attribute in the copied GeoLayer.
                        if not (existing_attr_name == new_attr_name):
                            copied_geolayer.rename_attribute(existing_attr_name, new_attr_name)

                    # Write copied GeoLayer (memory) to the temporary directory (written to disk).
                    output_file_absolute = os.path.join(self.command_processor.get_property('TempDir'),
                                                        copied_geolayer.id)
                    on_disk_geolayer = copied_geolayer.write_to_disk(output_file_absolute)

                    # Overwrite the copied (memory) GeoLayer in the geoprocessor with the on-disk GeoLayer.
                    self.command_processor.add_geolayer(on_disk_geolayer)

                    # Add the source path of the copied on-disk GeoLayer to the master list.
                    copied_geolayer_sourcepath.append(on_disk_geolayer.source_path)

                # Merge all of the copied GeoLayers (the GeoLayers with the new attribute names).
                # Using QGIS algorithm but can also use saga:mergelayers algorithm.
                # saga:mergelayers documentation at http://www.saga-gis.org/saga_tool_doc/2.3.0/shapes_tools_2.html
                alg_parameters = {"LAYERS": copied_geolayer_sourcepath,
                                  "CRS": first_crs,
                                  "OUTPUT": "memory:"}
                merged_output = self.command_processor.qgis_processor.runAlgorithm("qgis:mergevectorlayers",
                                                                                   alg_parameters)

                # Create a new GeoLayer and add it to the GeoProcessor's geolayers list.
                # in QGIS3, merged_output["OUTPUT"] returns the returns the QGS vector layer object
                # see ClipGeoLayer.py for information about value in QGIS2 environment
                self.command_processor.add_geolayer(VectorGeoLayer(geolayer_id=pv_OutputGeoLayerID,
                                                                   geolayer_qgs_vector_layer=merged_output["OUTPUT"],
                                                                   geolayer_source_path="MEMORY"))

                # Release the copied GeoLayers from the GeoProcessor.
                for copied_geolayer_id in copied_geolayer_ids:

                    # Get the copied GeoLayer based on the GeoLayer ID.
                    copied_geolayer = self.command_processor.get_geolayer(copied_geolayer_id)

                    # Remove the copied GeoLayer from the GeoProcessor
                    self.command_processor.free_geolayer(copied_geolayer)

            # Raise an exception if an unexpected error occurs during the process
            except Exception:
                self.warning_count += 1
                message = "Unexpected error merging the following GeoLayers {}.".format(pv_GeoLayerIDs)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN,
                                               CommandLogRecord(CommandStatusType.FAILURE, message,
                                                                recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(self.warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
