#!/bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL
#
# git-clone-all-gp - clone all GeoProcessor repositories for new development environment setup
# - this script calls the general git utilities script

# GeoProcessor product home is relative to the user's files in a standard OWF development files location
# - $HOME/${productHome}
productHome="owf-dev/GeoProcessor"

# GeoProcessor GitHub repo URL root
githubRootUrl="https://github.com/OpenWaterFoundation"

# Main GeoProcessor repository
mainRepo="cdss-app-geoprocessor-python"

# TODO smalers 2018-10-12 The following may need to be made absolute to run from any folder
# - also pass the command parameters so that -h, etc. are recognized
git-util/git-clone-all.sh -m "${mainRepo}" -p "${productHome}" -g "${githubRootUrl}" $@
