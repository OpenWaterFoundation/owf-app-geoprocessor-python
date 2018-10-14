#!/bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL
#
# git-check-gp - check the GeoProcessor repositories for status
# - this script calls the general git utilities script

# GeoProcessor product home is relative to the user's files in a standard OWF development files location
# - $HOME/${productHome}
productHome="owf-dev/GeoProcessor"

# Main GeoProcessor repository
mainRepo="owf-app-geoprocessor-python"

# TODO smalers 2018-10-12 The following may need to be made absolute to run from any folder
git-util/git-check.sh -m "${mainRepo}" -p "${productHome}" $@
