# Application data
# - allows use of application-specific data by other modules

# Dictionary containing program properties
program_properties = {}


def get_property(property_name):
    """
    Retrieve an application property by name.
    This provides encapsulation and more flexibility than hard-coded variable access,
    given that property names might change as the application is developed.

    Args:
        property_name:  Name of property to retrieve.

    Returns:  String property value for given property name, or None if not found.
    """
    # If dictionary is empty, initialize it
    if len(program_properties) == 0:
        init_properties()
    try:
        return program_properties[property_name]
    except KeyError as e:
        return None


def init_properties():
    """
    Initialize the properties to empty strings.

    Returns:  None
    """
    # Program copyright text, e.g., "Copyright 2016-2018, Organization"
    program_properties['ProgramCopyright'] = ""
    # Program icon, full path
    # - Used by UI components
    program_properties['ProgramIconPath'] = ""
    # Program home, full path
    program_properties['ProgramHome'] = ""
    # Program license text, e.g., "GPL 3.0"
    program_properties['ProgramLicense'] = ""
    # Program name
    program_properties['ProgramName'] = ""
    # Program organization name
    program_properties['ProgramOrganization'] = ""
    # Program organization name URL
    program_properties['ProgramOrganizationUrl'] = ""
    # Program resources folder
    program_properties['ProgramResourcesPath'] = ""
    # Program user documentation
    program_properties['ProgramUserDocumentationUrl'] = ""
    # Program version, for example 1.2.3
    program_properties['ProgramVersion'] = ""
    # Program version, for example YYYY-MM-DD
    program_properties['ProgramVersionDate'] = ""


def set_property(property_name, property_value):
    """
    Set a property for the application.

    Args:
        property_name:  Property name.
        property_value:  Property value as string.

    Returns:  None.
    """
    if len(program_properties) == 0:
        init_properties()
    program_properties[property_name] = property_value
