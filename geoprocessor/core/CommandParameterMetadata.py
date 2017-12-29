class CommandParameterMetadata(object):
    """
    Metadata for the command parameters, a list of which is maintained as
    AbstractCommand.command_parameter_metadata.
    This information is used to output parameters in the proper order in AbstractCommand.to_string()
    and also provide basic validation data (valid parameter names, type).
    Validation requires more effort when the allowed value is an enumeration, etc.
    """

    def __init__(self,parameter_name,parameter_type,validator_function):
        # Parameter name should be in format WordWord
        self.parameter_name = parameter_name

        # Parameter type should match the output of the type(), for example type(""), type(1), type(1.0).
        # Use string for complex types that will require parsing in the command.
        self.parameter_type = parameter_type

        # Validator function to be called to validate the command parmameter
        self.validator_function = validator_function

# Functions that can be used as static functions outside of the class,
# for example to process the full list of CommandParameterMetadata objects.

def get_parameter_names ( parameter_metadata_list ):
    """
    Return the list of parameter names in a list, extracted from the metadata list.

    Args:
        parameter_metadata_list:  List of CommandParameterMetadata.
    Returns:
        List of string containing parameter names from metadata.
    """
    parameter_names = []
    if ( parameter_metadata_list != None ):
        for meta in parameter_metadata_list:
            parameter_names.append(meta.parameter_name)

    return parameter_names