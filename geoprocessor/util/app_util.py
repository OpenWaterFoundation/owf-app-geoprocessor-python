# app_util - application data and functions
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
# - allows use of application-specific data by other modules

import geoprocessor.util.os_util as os_util

import os
import sys

# Dictionary containing program properties
program_properties = {}


def get_property(property_name: str) -> str or None:
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
    except KeyError:
        return None


def get_qgis_install_folder() -> str or None:
    """
    Return the top-level folder where QGIS is installed for the version being used at run-time.
    This should only be called if is_qgis_osgeo() and/or is_qgis_standalone() return true.
    Currently returns the QGIS_PREFIX_PATH environment variable.

    Returns:
        - The top-level folder where QGIS is installed.
        - None if QGIS is not installed.
    """
    if is_qgis_install_osgeo():
        # TODO smalers 2020-07-20 the following may not work
        # return os.environ.get('QGIS_PREFIX_PATH')
        return os.environ.get('QGIS_INSTALL_HOME')
    elif is_qgis_install_standalone():
        # return os.environ.get('QGIS_PREFIX_PATH')
        return os.environ.get('QGIS_SA_INSTALL_HOME')
    else:
        # QGIS not installed
        return None


def init_properties() -> None:
    """
    Initialize the properties to empty strings.

    Returns:  None
    """
    # Set program information
    # Program copyright text, e.g., "Copyright 2017-2020, Organization"
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


def is_gp() -> bool:
    """
    Indicate whether running the full GeoProcessor (gp).
    This checks the Python that is being used.
    If QGIS is installed and being used, return True.

    See also:
        is_gptest()

    Returns:
        True if the application is the full GeoProcessor, or False if not.
    """
    if is_qgis_install_osgeo() or is_qgis_install_standalone():
        return True
    else:
        return False


def is_gptest() -> bool:
    """
    Indicate whether running the GeoProcessor testing framework (gptest).

    Returns:
        True if the application is the testing framework GeoProcessor, or False if not.
    """
    if is_gp():
        return False
    else:
        return True


def is_qgis_install_osgeo() -> bool:
    """
    Indicate whether running the OSGeo4W QGIS installation.
    On Windows, If Python is located in folder 'C:/OSGeo4W64', it is an OSGeo install.

    Returns:
        True if the application is the OSGeo4W QGIS installation, or False if not.
    """
    executable = str(sys.executable).upper()
    if os_util.is_windows_os():
        # Check the executable path, which may be old-style C:\OSGEO4~1, etc.
        if executable.find(r':\OSGEO4') > 0:
            # Running the Python shipped with OSGeo4W installation
            return True

    # Fall through.
    return False


def is_qgis_install_standalone() -> bool:
    """
    Indicate whether running standalone QGIS installation.
    On Windows, If Python is located in folder 'C:/Program Files/QGIS', it is a standalone install.

    See also:
        is_qgis_osgeo()

    Returns:
        True if the application is the standalone QGIS installation, or False if not.
    """
    executable = str(sys.executable).upper()
    if os_util.is_windows_os():
        # Check the executable path
        if executable.find(r'\PROGRAM FILES\QGIS') > 0:
            # Running the Python shipped with stand-alone version of QGIS
            return True
        elif (executable.find(r'\PROGRA~') > 0) and (executable.find(r'\QGIS3') > 0):
            # Running the Python shipped with stand-alone version of QGIS
            # - old-style is something like C:\PROGRA~1\QGIS3~1.4\...
            return True

    # Fall through.
    return False


def set_property(property_name: str, property_value: str) -> None:
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
