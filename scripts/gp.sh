#!/bin/sh

# Script to run the Open Water Foundation GeoProcessor application
# - This script should eventually work for Cygwin, Git Bash (MinGW), and Linux
# - Current focus is Cygwin development environment.
# - This is currently hard-coded to work in the development environment only,
#   run from the scripts folder (needs to be updated to work in deployed environment)

# Set the Python environment to find the correct run-time libraries

cygwinUname=`uname -a | grep -i cygwin`

if [ ! -z "${cygwinUname}" ]
	then
	# Shell is running on Cygwin

	OSGEO4W_ROOT="/cygdrive/C/OSGeo4W64"
	# QGIS Python
	QGIS_PYTHON_EXE="/cygdrive/C/OSGeo4W64/bin/python.exe"

	# Normal Python (should be Python 2.7)
	PYTHON_EXE="python"

	# Set the PYTHONPATH to include the geoprocessor module
	# - Folder for libraries must contain "geoprocessor" since modules being searched for will start with that.
	#GEOPROCESSOR_HOME="/cygdrive/C/Users/${USER}/owf-dev/GeoProcessor/git-repos/owf-app-geoprocessor-python/geoprocessor"
	GEOPROCESSOR_HOME="/cygdrive/C/Users/${USER}/owf-dev/GeoProcessor/git-repos/owf-app-geoprocessor-python"
	if [ -z "$PYTHONPATH" ]
		then
		# No PYTHONPATH defined so just set it
		export PYTHONPATH="${GEOPROCESSOR_HOME}"
	else
		export PYTHONPATH="${GEOPROCESSOR_HOME}:$PYTHONPATH}"
	fi

	# Add QGIS Python libraries
	export PYTHONPATH="$PYTHONPATH:$OSGEO4W_ROOT/apps/qgis/python"
	export PYTHONPATH="$PYTHONPATH:$OSGEO4W_ROOT/apps/qgis/python/plugins"
	export PYTHONPATH="$PYTHONPATH:$OSGEO4W_ROOT/apps/Python27/Lib/site-packages"

	echo "PYTHONPATH=$PYTHONPATH"

	# Also add QGIS to the PATH
	export PATH="$OSGEO4W_ROOT/apps/qgis/bin:$PATH"

	# Run Python on the code
	# - must use Python 2.7 compatible with QGIS

	# QGIS Python complained so try normal Python first
	#${QGIS_PYTHON_EXE} --version
	#${QGIS_PYTHON_EXE} -v ../geoprocessor/app/gp.py --help
	${PYTHON_EXE} ../geoprocessor/app/gp.py --help
fi
