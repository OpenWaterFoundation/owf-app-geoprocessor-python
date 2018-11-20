#!/bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL
#
# git-clone-all-gp - clone all GeoProcessor repositories for new development environment setup
# - this script calls the general git utilities script

# Get the location where this script is located since it may have been run from any folder
scriptFolder=`cd $(dirname "$0") && pwd`

# GeoProcessor product home is relative to the user's files in a standard OWF development files location
# - $HOME/${productHome}
productHome="owf-dev/GeoProcessor"

# GeoProcessor GitHub repo URL root
githubRootUrl="https://github.com/OpenWaterFoundation"

# Main GeoProcessor repository
mainRepo="cdss-app-geoprocessor-python"

# Run the general script
${scriptFolder}/git-util/git-clone-all.sh -m "${mainRepo}" -p "${productHome}" -u "${githubRootUrl}" $@
