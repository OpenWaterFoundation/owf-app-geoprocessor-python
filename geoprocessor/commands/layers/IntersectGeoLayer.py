# IntersectGeoLayer - command to intersect GeoLayers
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2019 Open Water Foundation
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
from geoprocessor.core.GeoLayer import GeoLayer

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validators
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.string_util as string_util

import logging
import os

from plugins.processing.tools import general


class IntersectGeoLayer(AbstractCommand):

    """
    Intersects the input GeoLayer with an intersecting GeoLayer.

    This command intersects an input GeoLayer by the boundary of the intersect GeoLayer. The features of the input
    GeoLayer are retained in the output GeoLayer if they intersect with the intersect GeoLayer. The output intersected
    layer will become a new GeoLayer. The attribute fields and values of the input GeoLayer are retained within the
    output intersected GeoLayer. The features of the input GeoLayer are retained within the output intersected
    GeoLayer. The attributes fields and values of the intersect GeoLayer are appended to the output intersected
    GeoLayer. The features of the intersect GeoLayer are NOT retained within the output intersected GeoLayer.

    Command Parameters

    * GeoLayerID (str, required): the ID of the input GeoLayer, the layer to be intersected
    * IntersectGeoLayerID (str, required): the ID of the intersect GeoLayer.
    * IncludeIntersectAttributes (str, optional): A list of glob-style patterns to determine the intersect GeoLayer
        attributes to include in the output intersected GeoLayer. Default: * (All attributes are included in the output
        GeoLayer).
    * ExcludeIntersectAttributes (str, optional): A list of glob-style patterns to determine the intersect GeoLayer
        attributes to exclude in the output intersected GeoLayer. Default: '' (All attributes are included in the
        output GeoLayer).
    * OutputGeoLayerID (str, optional): the ID of the GeoLayer created as the output intersected layer. By default the
        GeoLayerID of the output layer will be {}_intersectedBy_{} where the first variable is the GeoLayerID and
        the second variable is the IntersectGeoLayerID.
    * IfGeoLayerIDExists (str, optional): This parameter determines the action that occurs if the OutputGeoLayerID
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("GeoLayerID", type("")),
        CommandParameterMetadata("IntersectGeoLayerID", type("")),       
        CommandParameterMetadata("IncludeIntersectAttributes", type("")),
        CommandParameterMetadata("ExcludeIntersectAttributes", type("")),
        CommandParameterMetadata("OutputGeoLayerID", type("")),
        CommandParameterMetadata("IfGeoLayerIDExists", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        self.command_name = "IntersectGeoLayer"
        self.command_parameter_metadata = self.__command_parameter_metadata

        self.command_metadata = dict()
        self.command_metadata['Description'] =\
            "Extract the overlapping portions of features in the input GeoLayer and the intersect GeoLayer."
        self.command_metadata['EditorType'] = "Simple"

        # Command Parameter Metadata
        self.parameter_input_metadata = dict()
        # GeoLayerID
        self.parameter_input_metadata['GeoLayerID.Description'] = "the ID of the input GeoLayer"
        self.parameter_input_metadata['GeoLayerID.Label'] = "GeoLayerID"
        self.parameter_input_metadata['GeoLayerID.Required'] = True
        self.parameter_input_metadata['GeoLayerId.Tooltip'] = "The ID of the input GeoLayer that will be intersected."
        # IntersectGeoLayerID
        self.parameter_input_metadata['IntersectGeoLayerID.Description'] = "the ID of the intersect GeoLayer"
        self.parameter_input_metadata['IntersectGeoLayerID.Label'] = "Intersect GeoLayerID"
        self.parameter_input_metadata['IntersectGeoLayerID.Required'] = True
        self.parameter_input_metadata['IntersectGeoLayerID.Tooltip'] = "The ID of the intersect GeoLayer."
        # IncludeIntersectAttributes
        self.parameter_input_metadata['IncludeIntersectAttributes.Description'] = \
            "intersect layer attributes to include"
        self.parameter_input_metadata['IncludeIntersectAttributes.Label'] = "Include intersect attributes"
        self.parameter_input_metadata['IncludeIntersectAttributes.Tooltip'] = (
            "A comma-separated list of the glob-style patterns filtering which attributes "
            "from the intersect GeoLayer to include in the output GeoLayer.")
        # ExcludeIntersectAttributes
        self.parameter_input_metadata['ExcludeIntersectAttributes.Description'] =\
            "intersect layer attributes to exclude"
        self.parameter_input_metadata['ExcludeIntersectAttributes.Label'] = "Exclude intersect attributes"
        self.parameter_input_metadata['ExcludeIntersectAttributes.Tooltip'] = (
            "A comma-separated list of the glob-style patterns filtering which attributes" \
            "from the intersect Geolayer to exclude in the output GeoLayer. ")
        # OutputGeoLayerID
        self.parameter_input_metadata['OutputGeoLayerID.Description'] = "the ID of the intersected GeoLayer"
        self.parameter_input_metadata['OutputGeoLayerID.Label'] = "Output GeoLayerID"
        self.parameter_input_metadata['OutputGeoLayerID.Tooltip'] = "The ID of the intersected GeoLayer."
        self.parameter_input_metadata['OutputGeoLayerID.Value.Default.Description'] =\
            "GeoLayerId_intersectedBy_IntersectGeoLayerID."
        # IfGeoLayerIDExists
        self.parameter_input_metadata['IfGeoLayerIDExists.Description'] = "action if output layer exists"
        self.parameter_input_metadata['IfGeoLayerIDExists.Label'] = "If GeoLayerID exists"
        self.parameter_input_metadata['IfGeoLayerIDExists.Tooltip'] = (
            "The action that occurs if the OutputGeoLayerID already exists within the GeoProcessor.\n"
            "Replace : The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer. "
            "No warning is logged.\n"
            "ReplaceAndWarn: The existing GeoLayer within the GeoProcessor is overwritten with the new GeoLayer."
            "A warning is logged.\n"
            "Warn : The new GeoLayer is not created. A warning is logged.\n"
            "Fail : The new GeoLayer is not created. A fail message is logged.")
        self.parameter_input_metadata['IfGeoLayerIDExists.Values'] = ["", "Replace", "ReplaceAndWarn", "Warn", "Fail"]
        self.parameter_input_metadata['IfGeoLayerIDExists.Value.Default'] = "Replace"

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            Nothing.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning = ""

        # Check that parameter GeoLayerID is a non-empty, non-None string.
        pv_GeoLayerID = self.get_parameter_value(parameter_name='GeoLayerID',
                                                      command_parameters=command_parameters)

        if not validators.validate_string(pv_GeoLayerID, False, False):
            message = "GeoLayerID parameter has no value."
            recommendation = "Specify the GeoLayerID parameter to indicate the input GeoLayer."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that parameter IntersectGeoLayerID is a non-empty, non-None string.
        pv_IntersectGeoLayerID = self.get_parameter_value(parameter_name='IntersectGeoLayerID',
                                                          command_parameters=command_parameters)

        if not validators.validate_string(pv_IntersectGeoLayerID, False, False):

            message = "IntersectGeoLayerID parameter has no value."
            recommendation = "Specify the IntersectGeoLayerID parameter to indicate the clipping GeoLayer."
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that opt parameter OutputFormat is either `SingleSingle`, `SingleMultiple`, `MulipleSingle` or None.
        pv_OutputFormat = self.get_parameter_value(parameter_name="OutputFormat", command_parameters=command_parameters)
        acceptable_values = ["SingleSingle", "SingleMultiple", "MulipleSingle"]
        if not validators.validate_string_in_list(pv_OutputFormat, acceptable_values, none_allowed=True,
                                                  empty_string_allowed=True, ignore_case=True):
            message = "OutputFormat parameter value ({}) is not recognized.".format(pv_OutputFormat)
            recommendation = "Specify one of the acceptable values ({}) for the OutputFormat parameter.".format(
                acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(
                CommandPhaseType.INITIALIZATION,
                CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that optional parameter IfGeoLayerIDExists is either `Replace`, `Warn`, `Fail` or None.
        pv_IfGeoLayerIDExists = self.get_parameter_value(parameter_name="IfGeoLayerIDExists",
                                                         command_parameters=command_parameters)
        acceptable_values = ["Replace", "Warn", "Fail", "ReplaceAndWarn"]
        if not validators.validate_string_in_list(pv_IfGeoLayerIDExists, acceptable_values, none_allowed=True,
                                                  empty_string_allowed=True, ignore_case=True):
            message = "IfGeoLayerIDExists parameter value ({}) is not recognized.".format(pv_IfGeoLayerIDExists)
            recommendation = "Specify one of the acceptable values ({}) for the IfGeoLayerIDExists parameter.".format(
                acceptable_values)
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
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def __should_intersect_geolayer(self, input_geolayer_id, intersect_geolayer_id, output_geolayer_id):
        """
        Checks the following:
        * the ID of the input GeoLayer is an existing GeoLayer ID
        * the ID of the intersect GeoLayer is an existing GeoLayer ID
        * the ID of the output GeoLayer is unique (not an existing GeoLayer ID)
        * the input GeoLayer and the intersect GeoLayer are in the same CRS (warning but no failure)
        * the intersect GeoLayer is a POLYGON if the input GeoLayer is a POLYGON
        * the intersect GeoLayer is either a POLYGON or a LINE if the input GeoLayer is a LINE

        Args:
            input_geolayer_id: the ID of the input GeoLayer
            intersect_geolayer_id: the ID of the intersect GeoLayer
            output_geolayer_id: the ID of the output, clipped GeoLayer

        Returns:
             Boolean. If TRUE, the GeoLayer should be intersected. If FALSE, at least one check failed and the GeoLayer
                should not be intersected.
        """

        # List of Boolean values. The Boolean values correspond to the results of the following tests. If TRUE, the
        # test confirms that the command should be run.
        should_run_command = []

        # If the input GeoLayerID is not an existing GeoLayerID, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsGeoLayerIDExisting", "GeoLayerID",
                                                       input_geolayer_id, "FAIL"))

        # If the intersect GeoLayer ID is not an existing GeoLayer ID, raise a FAILURE.
        should_run_command.append(validators.run_check(self, "IsGeoLayerIDExisting", "IntersectGeoLayerID",
                                                       intersect_geolayer_id, "FAIL"))

        # If the input GeoLayer and the intersect GeoLayer both exist, continue with the checks.
        if False not in should_run_command:

            # If the input GeoLayer and the clipping GeoLayer do not have the same CRS, raise a WARNING.
            should_run_command.append(validators.run_check(self, "DoGeoLayerIDsHaveMatchingCRS", "GeoLayerID",
                                                           input_geolayer_id, "WARN",
                                                           other_values=["IntersectGeoLayerID", intersect_geolayer_id]))

            # Get the geometry of the Input GeoLayer.
            input_geolayer = self.command_processor.get_geolayer(input_geolayer_id)
            input_geolayer_geom_qgis = input_geolayer.get_geometry()

            # If the InputGeoLayer is a polygon and the IntersectGeoLayer is a line or point, raise a FAILURE.
            if input_geolayer_geom_qgis == "Polygon":

                should_run_command.append(validators.run_check(self, "DoesGeoLayerIdHaveCorrectGeometry",
                                                               "IntersectGeoLayerID", intersect_geolayer_id,
                                                               "FAIL", other_values=[["Polygon"]]))

            # If the InputGeoLayer is a line and the IntersectGeoLayer is a point, raise a FAILURE.
            if input_geolayer_geom_qgis == "LineString":
                should_run_command.append(validators.run_check(self, "DoesGeoLayerIdHaveCorrectGeometry",
                                                               "IntersectGeoLayerID", intersect_geolayer_id,
                                                               "FAIL", other_values=[["LineString", "Polygon"]]))

        # If the OutputGeoLayerID is the same as an already-existing GeoLayerID, raise a WARNING or FAILURE (depends
        # on the value of the IfGeoLayerIDExists parameter.)
        should_run_command.append(validators.run_check(self, "IsGeoLayerIdUnique", "OutputGeoLayerID",
                                                       output_geolayer_id, None))

        # Return the Boolean to determine if the process should be run.
        if False in should_run_command:
            return False
        else:
            return True

    def __single_feature_and_attribute_method(self, input_geolayer, pv_OutputGeoLayerID, intersect_geolayer_copy):
        """This is an under-construction intersection method designed by Open Water Foundation Emma Giles. It is not
         in use within the command yet because its implementation is under discussion. This intersect method will not
         clip input features that overlap multiple intersect features. Note that in the QGIS_method, the input features
         that overlap the intersect features are clipped. With the "single feature single attribute method" the
         attribute values of the output features that were overlapping multiple intersect features are a combination
        of the overlapping intersect features.

        For example, an input line feature overlaps two polygon features. The intersect polygon layer has a string
        attribute called "Name". The first overlapping intersect polygon has the "Name" attribute value of "Hill" and
        the other has the name attribute value of "Moon". The "Name" attribute field in the output intersected line
        layer would be "Hill, Moon". For integer values, a summary statistic of mean, min, max or sum can be applied."""

        # Command variables
        within_target_feats = {}
        intersecting_target_feats = {}

        target_geolayer = input_geolayer.deepcopy(pv_OutputGeoLayerID)
        target_layer = target_geolayer.qgs_vector_layer
        intersect_geolayer = intersect_geolayer_copy
        intersect_layer = intersect_geolayer.qgs_vector_layer
        attributes_to_join = intersect_geolayer_copy.get_attribute_field_names()
        statistic_summary = "mean"

        # Iterate over the target features.
        for target_feat in target_layer.getFeatures():

            # Iterate over the intersect features.
            for intersect_feat in intersect_layer.getFeatures():

                # Get the geometries of the target feature and the intersect feature.
                target_geom = target_feat.geometry()
                intersect_geom = intersect_feat.geometry()

                # Determine if the target feature is within/intersects the intersect feature.
                is_within = target_geom.within(intersect_geom)
                does_intersect = target_geom.intersects(intersect_geom)

                # If the target feature is within the intersecting feature, add an entry to the within dictionary where the
                # key is the target feature and the value is the intersect feature.
                if is_within:
                    within_target_feats[target_feat] = intersect_feat

                # Otherwise if the target feature is intersecting the intersect feature, continue.
                elif does_intersect:

                    # If the target feature (the key) is already registered in the dictionary, add the intersecting feature to
                    # the list of intersecting features (the value).
                    if target_feat in intersecting_target_feats.keys():
                        curr_dic_value = intersecting_target_feats[target_feat]
                        curr_dic_value.append(intersect_feat)

                    # If the target feature has not yet been registered in the dictionary, add an entry to the intersect
                    # dictionary where the key is the target feature and the value is a list of the intersect features.
                    else:
                        intersecting_target_feats[target_feat] = [intersect_feat]

        # Move the appropriate entries within the intersecting dictionary to the within dictionary.
        to_delete = []
        for target_feature, intersect_feature_list in intersecting_target_feats.items():

            # If the dictionary entry only has one intersect feature, continue.
            if len(list(set(intersect_feature_list))) == 1:
                # Add the entry to the within dictionary.
                within_target_feats[target_feature] = intersect_feature_list[0]

                # Add the key to the to_delete list to remove the entry from the intersecting dictionary.
                to_delete.append(target_feature)

        # Delete the entries in the intersect dictionary if they have been moved to the within dictionary.
        for item in to_delete:
            del intersecting_target_feats[item]

        # Get the intersect layer's attributes to add as indexes.
        intersect_layer_attrs_to_add_idx = []
        for input_attr in attributes_to_join:
            intersect_layer_attrs_to_add_idx.append(intersect_layer.fieldNameIndex(input_attr))

        # Iterate over the intersect layer's attributes to add as indexes.
        for intersect_attr_to_add_idx in intersect_layer_attrs_to_add_idx:

            # Get a field object of the intersect attribute.
            field = intersect_layer.pendingFields()[intersect_attr_to_add_idx]

            # Get a list of the existing attribute names in the target layer.
            existing_target_layer_attrs = [attr_field.name() for attr_field in target_layer.pendingFields()]

            # Add the intersect layer's attribute to add to the target layer (if it does not already exist).
            if field.name() not in existing_target_layer_attrs:
                # Add the new attributes to the target layer.
                typeName_attrType_dic = {"Integer": "int", "String": "string"}
                qgis_util.add_qgsvectorlayer_attribute(target_layer, field.name(),
                                                       typeName_attrType_dic[field.typeName()])

            # Get the index of the target feature that matches the intersect attribute name.
            target_attr_idx = target_layer.fieldNameIndex(field.name())

            # Iterate over the within dictionary.
            for target_feat, intersect_feat in within_target_feats.items():
                # Get the intersect attribute value.
                intersect_feat_value = intersect_feat.attributes()[intersect_attr_to_add_idx]

                # Create an an attribute dictionary. KEY: target attribute index VALUE: new attribute value
                attr_dic = {target_attr_idx: intersect_feat_value}

                # Add the correct attribute value to the target layer.
                target_layer.dataProvider().changeAttributeValues(({target_feat.id(): attr_dic}))

            # Iterate over the intersect dictionary.
            for target_feat, intersect_feats in intersecting_target_feats.items():

                list_of_intersect_attr_values = []

                # Iterate over the intersection features and add the attribute values to the list_of_intersect_attr_values.
                for intersect_feat in intersect_feats:
                    list_of_intersect_attr_values.append(
                        intersect_feat.attributes()[intersect_attr_to_add_idx])

                # If the attribute is type String, continue.
                if field.typeName() == "String":

                    intersect_feat_value_updated = ",".join(list_of_intersect_attr_values)

                # If the attribute is type Integer, continue.
                elif field.typeName() == "Integer":

                    if statistic_summary.upper() == "SUM":
                        intersect_feat_value_updated = sum(list_of_intersect_attr_values)
                    elif statistic_summary.upper() == "MEAN":
                        intersect_feat_value_updated = sum(list_of_intersect_attr_values) / len(
                            list_of_intersect_attr_values)
                    elif statistic_summary.upper() == "MIN":
                        intersect_feat_value_updated = min(list_of_intersect_attr_values)
                    elif statistic_summary.upper() == "MAX":
                        intersect_feat_value_updated = max(list_of_intersect_attr_values)

                # Create an an attribute dictionary. KEY: target attribute index VALUE: new attribute value
                attr_dic = {target_attr_idx: intersect_feat_value_updated}

                # Add the correct attribute value to the target layer.
                target_layer.dataProvider().changeAttributeValues(({target_feat.id(): attr_dic}))

        # Create a new GeoLayer and add it to the GeoProcessor's geolayers list.
        # intersected_output["OUTPUT"] returns the full file pathname of the memory output layer (saved
        # in a QGIS temporary folder)
        self.command_processor.add_geolayer(target_geolayer)

    def run_command(self):
        """
        Run the command. Intersect the input GeoLayer by the intersect GeoLayer. Create a new GeoLayer with the
        intersected output layer.

        Returns: None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Obtain the parameter values.
        pv_GeoLayerID = self.get_parameter_value("GeoLayerID")
        pv_IntersectGeoLayerID = self.get_parameter_value("IntersectGeoLayerID")
        pv_OutputGeoLayerID = self.get_parameter_value("OutputGeoLayerID", default_value="{}_intersectedBy_{}".format(
            pv_GeoLayerID, pv_IntersectGeoLayerID))
        pv_IncludeIntersectAttributes = self.get_parameter_value("IncludeIntersectAttributes", default_value="*")
        pv_ExcludeIntersectAttributes = self.get_parameter_value("ExcludeIntersectAttributes", default_value="''")

        # Set the method used for the command. The IntersectGeoLayer methodology can be completed in many different
        # ways. Currently there are two designs:
        #   1. QGIS_method: use "qgis: intersect" algorithm where input features that overlap multiple
        #   intersecting features, are clipped.
        #   2. OWF_method: owf-design in progress where input features that overlap multiple
        #   intersecting features retain their geometry but the output attribute is a combination of the attributes of
        #   the overlapping intersect features
        # Because the second method is not complete and is still in debate at OWF, the code is memorialized under the
        # __single_feature_and_attribute_method function. The function is never called and the QGIS_method is always
        # used (until further notice).
        QGIS_method = True
        OWF_method = False

        # Convert the IncludeIntersectAttributes and ExcludeIntersectAttributes to lists.
        attrs_to_include = string_util.delimited_string_to_list(pv_IncludeIntersectAttributes)
        attrs_to_exclude = string_util.delimited_string_to_list(pv_ExcludeIntersectAttributes)

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.__should_intersect_geolayer(pv_GeoLayerID, pv_IntersectGeoLayerID, pv_OutputGeoLayerID):

            try:

                # Get the Input GeoLayer and the Intersect GeoLayer.
                input_geolayer = self.command_processor.get_geolayer(pv_GeoLayerID)
                intersect_geolayer = self.command_processor.get_geolayer(pv_IntersectGeoLayerID)

                # Make a copy of the intersect GeoLayer - manipulations will occur on this layer and the original
                # should not be affected.
                intersect_geolayer_copy = intersect_geolayer.deepcopy("intersect_geolayer_copy")

                # Remove the attributes of the input intersect GeoLayer if configured to be excluded in the output
                # intersected GeoLayer.
                intersect_geolayer_copy.remove_attributes(attrs_to_include, attrs_to_exclude)

                # If the input GeoLayer is an in-memory GeoLayer, make it an on-disk GeoLayer.
                if input_geolayer.source_path is None or input_geolayer.source_path.upper() in ["", "MEMORY"]:

                    # Get the absolute path of the GeoLayer to write to disk.
                    geolayer_disk_abs_path = os.path.join(self.command_processor.get_property('TempDir'),
                                                          input_geolayer.id)

                    # Write the GeoLayer to disk. Overwrite the (memory) GeoLayer in the geoprocessor with the
                    # on-disk GeoLayer.
                    input_geolayer = input_geolayer.write_to_disk(geolayer_disk_abs_path)
                    self.command_processor.add_geolayer(input_geolayer)

                # If the intersect GeoLayer is an in-memory GeoLayer, make it an on-disk GeoLayer.
                if intersect_geolayer_copy.source_path is None or intersect_geolayer_copy.source_path.upper() in \
                        ["", "MEMORY"]:
                    #  Get the absolute path of the GeoLayer to write to disk.
                    geolayer_disk_abs_path = os.path.join(self.command_processor.get_property('TempDir'),
                                                          intersect_geolayer_copy.id)

                    # Write the GeoLayer to disk. Overwrite the (memory) GeoLayer in the geoprocessor with the
                    # on-disk GeoLayer.
                    intersect_geolayer_copy = intersect_geolayer_copy.write_to_disk(geolayer_disk_abs_path)
                    self.command_processor.add_geolayer(intersect_geolayer_copy)

                # If using QGIS version of intersect. Set to TRUE always until later notice.
                if QGIS_method:

                    # Perform the QGIS intersection function. Refer to the reference below for parameter descriptions.
                    # REF: https://docs.qgis.org/2.18/en/docs/user_manual/processing_algs/qgis/
                    # vector_overlay_tools.html#intersection
                    alg_parameters = {"INPUT": input_geolayer.qgs_vector_layer,
                                      "OVERLAY": intersect_geolayer_copy.qgs_vector_layer,
                                      "OUTPUT": "memory:"}
                    intersected_output = self.command_processor.qgis_processor.runAlgorithm("qgis:intersection",
                                                                                            alg_parameters)

                    # Create a new GeoLayer and add it to the GeoProcessor's geolayers list.
                    # in QGIS3, intersected_output["OUTPUT"] returns the returns the QGS vector layer object
                    # see ClipGeoLayer.py for information about value in QGIS2 environment
                    new_geolayer = GeoLayer(pv_OutputGeoLayerID, intersected_output["OUTPUT"], "MEMORY")
                    self.command_processor.add_geolayer(new_geolayer)

                # If using OWF version of intersect. Set to FALSE always until later notice.
                elif OWF_method:

                    self.__single_feature_and_attribute_method(pv_GeoLayerID, pv_IntersectGeoLayerID,
                                                               pv_OutputGeoLayerID)

                # Remove the copied intersect GeoLayer from the GeoProcessor's geolayers list. Delete the GeoLayer.
                index = self.command_processor.geolayers.index(intersect_geolayer_copy)
                del self.command_processor.geolayers[index]
                del intersect_geolayer_copy

            # Raise an exception if an unexpected error occurs during the process
            except Exception as e:
                self.warning_count += 1
                message = "Unexpected error intersecting GeoLayer {} with GeoLayer {}.".format(
                    pv_GeoLayerID, pv_IntersectGeoLayerID)
                recommendation = "Check the log file for details."
                self.logger.error(message, exc_info=True)
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
