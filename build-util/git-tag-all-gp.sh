#!/bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL
#
# git-tag-all-gp - tag all GeoProcessor repositories
# - this script calls the general git utilities script

# Get the location where this script is located since it may have been run from any folder
scriptFolder=`cd $(dirname "$0") && pwd`

# Git utilities folder is relative to the user's files in a standard development files location
# - determine based on location relative to the script folder
# Specific repository folder for this repository
repoHome=$(dirname ${scriptFolder})
# Want the parent folder to the specific Git repository folder
gitReposHome=$(dirname ${repoHome})

# Main GeoProcessor repository
mainRepo="owf-app-geoprocessor-python"
mainRepoFolder="$gitReposHome/$mainRepo"

# Determine the version from the software product
# - this is used as information to help the user specify an intelligent tag name and commit message
productVersion=$(cat $mainRepoFolder/geoprocessor/app/version.py | grep 'app_version' | grep -v 'date' | cut -d '=' -f 2 | tr -d " " | tr -d '"')
productName="GeoProcessor"

# Run the generic utility script
${scriptFolder}/git-util/git-tag-all.sh -m "${mainRepo}" -g "${gitReposHome}" -N "$productName" -V "$productVersion" $@
