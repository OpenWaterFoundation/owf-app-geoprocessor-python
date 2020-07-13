#!/bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL
# 
# 2-update-gp-venv.sh
#
# Update the Python virtualenv for the GeoProcessor
# - Copies GeoProcessor *.py, scripts, etc. to the virtual environment but does not:
#   - create the virtual environment
#   - package in installer
#   This is suitable for development environment such as Linux for gptest

# Determine staring folder in order to get absolute path
scriptFolder=`cd $(dirname "$0") && pwd`

# Create the temporary copy of the build
# - this is necessary to strip out QGIS for gptest
${scriptFolder}/1-create-gp-tar.sh

# Copy the source files from the temporary version to the venv
# - ensures that stripped files are used
${scriptFolder}/2-create-gp-venv.sh -u

# Exit with the status of the above
exit $?
