# version - version information for the GeoProcessor application
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

# Put in separate file to minimize commits to main app.py when only version changes but no other app.py code changes
app_name = "GeoProcessor"
app_organization = "Open Water Foundation"
app_organization_url = "http://openwaterfoundation.org"
app_copyright = "Copyright 2017-2020, Open Water Foundation"
app_license = "GPL 3.0"
# The following parts are used to create a full version:
# - the strings are also used in build process scripts
app_version_major = 1
app_version_minor = 5
app_version_micro = 0
app_version_mod = ""
# Use 'str' for all because could be a number or not
if app_version_mod == "":
    app_version = "{}.{}.{}".format(app_version_major, app_version_minor, app_version_micro)
else:
    app_version = "{}.{}.{}.{}".format(app_version_major, app_version_minor, app_version_micro, app_version_mod)
app_version_date = "2020-09-23"
