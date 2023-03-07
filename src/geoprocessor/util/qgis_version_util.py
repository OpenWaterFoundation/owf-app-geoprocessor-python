# qgis_version_util - utility functions related to QGIS version
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

"""
This module contains functions that deal with checking the QGIS version.
The functions can be called to determine which modules to import.
"""

from qgis.core import Qgis


def get_qgis_version_int(part: int = 0) -> int:
    """
    Returns the version (int) of the initiated QGIS software.
    If the part is not specified the entire version is returned as an integer.

    Example:
        21809

    Args:
        part The part of the version to return (0=full integer, 1=major, 2=minor, 3=patch)

    Returns:
        The QGIS version (int).
    """

    # TODO smalers 2018-05-28 the following was version 2.
    # return qgis.utils.QGis.QGIS_VERSION_INT

    # Version 3 uses the following.
    if part == 0:
        return Qgis.QGIS_VERSION_INT
    else:
        return int(get_qgis_version_str().split(".")[part - 1])


def get_qgis_version_name() -> str:
    """
    Returns the version name of the initiated QGIS software.

    Example:
        Las Palmas

    Returns:
        The QGIS version name (string).
    """

    # TODO smalers 2018-05-28 the following was version 2.
    # return qgis.utils.QGis.QGIS_RELEASE_NAME
    return Qgis.QGIS_RELEASE_NAME


def get_qgis_version_str() -> str:
    """
    Returns the version (string) of the initiated QGIS software.

    Example:
        "3.26.3"

    Returns:
        The QGIS version (string).
    """

    # TODO smalers 2018-05-28 the following was version 2.
    # return qgis.utils.QGis.QGIS_VERSION

    # The following is for version 3.
    return Qgis.version()
