#!/bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL
# 
# 1-create-gp-tar.sh
#
# Create the GeoProcessor Python code tar.gz (and zip) file
# - Working folder Python code is copied to temporary folder "build-tmp"
# - The files as-is are processed into tar.gz for "gp", for installation into site-packages.
# - The files are stripped of QGIS references and are processed into tar.gz for "gptest",
#   for installation into site-packages.
# - This approach does not yet use setup.py given some packaging complexities and need
#   to learn how to use setup.py
# - .zip files are also created.

# Supporting functions, alphabetized

# Check code as follows to make sure QGIS is fully disabled, in deployed version (look for uncommented QGIS code).
# - ignore the file printenv_qt5.py since it is used for testing.
# If any issues, show an error because script needs to be fixed to ensure code will run in deployed environment
checkGptestCode() {
	echo ""
	echo "Checking gptest code for QGIS references:  ${buildTmpGptestFolder}"
	grepExclude="--exclude printenv_qt5.py"
	totalCount="0"
	count=$(grep $grepExclude -ir 'import qgis' ${buildTmpGptestFolder} | grep -v '#' | wc -l)
	totalCount=$(expr $totalCount + $count)
	if [ "$count" -ne "0" ]; then
		# Found some lines so rerun so it is visible
		grep $grepExclude -ir 'import qgis' ${buildTmpGptestFolder} | grep -v '#'
	fi
	count=$(grep $grepExclude -ir 'from qgis' ${buildTmpGptestFolder} | grep -v '#' | wc -l)
	totalCount=$(expr $totalCount + $count)
	if [ "$count" -ne "0" ]; then
		# Found some lines so rerun so it is visible
		grep $grepExclude -ir 'from qgis' ${buildTmpGptestFolder} | grep -v '#'
	fi
	# The following is the most generic...
	# Check the total count and exit if references remain
	if [ "$totalCount" -ne "0" ]; then
		echo ""
		${echo2} "${failColor}QGIS references have not been totally removed.  Need to fix.  Exiting.${endColor}"
		exit 1
	fi
}

# Determine the operating system that is running the script
# - sets the variable operatingSystem to cygwin, linux, or mingw (Git Bash)
checkOperatingSystem()
{
	if [ ! -z "${operatingSystem}" ]; then
		# Have already checked operating system so return
		return
	fi
	operatingSystem="unknown"
	os=`uname | tr [a-z] [A-Z]`
	case "${os}" in
		CYGWIN*)
			operatingSystem="cygwin"
			;;
		LINUX*)
			operatingSystem="linux"
			;;
		MINGW*)
			operatingSystem="mingw"
			;;
	esac
	echo "Detected operatingSystem=$operatingSystem"
}

# Check the Operating System Python version.
# - See comments for checkQgisPythonVersion
# - The osPythonVersion variable is set to a number like "36" or "37" (initialized to "unknown").
# - The osPythonFolder is set to the location of the Python installation (parent of sys.executable).
# - The information can be printed at the end of this script to remind if there is an incompatibility.
checkOperatingSystemPythonVersion() {
	if [ "$operatingSystem" = "cygwin" ]; then
		python3ToRun=$(which python3)
		python3ToRun1=$(echo $python3ToRun | cut -c 1)
		if [ "$python3ToRun1" = "/" ]; then
			python3ToRunBasename=$(basename $python3ToRun)
			if [ "$python3ToRunBasename" != "python3" ]; then
				echo "Operating system python3 is not found."
			else
				# Get the Python version from the runtime since install folder is not as clear as QGIS
				# python3 --version output is expected to be like:  Python 3.6.4
				osPythonVersion=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f1,2 | tr -d '.')
			fi
		else
			$echo2 "${warnColor}python3 was not found on the operating system.${endColor}"
		fi
	fi
	# TODO smalers 2019-01-02 set the osPythonFolder
	# - have to inspect the path to find the "lib" folder, etc.
}

# Check the QGIS Python version.
# - Ideally the Cygwin and Linux Python will be the same but they may be slightly
#   off, especially for the testing framework.  For example, QGIS may be Python 3.7
#   and Cygwin and Linux Python may be 3.6.
# - The qgisPythonVersion variable is set to a number like "36" or "37" (initialized to "unknown").
# - The qgisPythonFolder i
# - The information can be printed at the end of this script to remind if there is an incompatibility.
checkQgisPythonVersion() {
	if [ "$operatingSystem" = "cygwin" ]; then
		OSGeo4W64Folder='/cygdrive/C/OSGeo4W64'
	fi
	if [ -d "${OSGeo4W64Folder}" ]; then
		# Look for Python folders, should be in apps/Python36, etc.
		# - get the newest version
		qgisPythonFolderCount=$(ls -1 -d ${OSGeo4W64Folder}/apps/Python* | wc -l)
		if [ "$qgisPythonFolderCount" -ne "1" ]; then
			echo ""
			echo "Found $qgisPythonFolderCount versions of Python in ${OSGeo4W64Folder} - assume newest is used."
		fi
		qgisPythonFolder=$(ls -1 -d ${OSGeo4W64Folder}/apps/Python* | sort -r | head -1)
		qgisPythonVersion=$(basename $qgisPythonFolder | sed 's/Python//g')
	else
		$echo2 "${warnColor}$OSGeo4W64Folder was not found - no QGIS insalled?${endColor}"
	fi
}

# Parse the command line and set variables to control logic
parseCommandLine() {
	#echo "Parsing command line..."
	local OPTIND opt h v
	while getopts :hv opt; do
		#echo "Command line option is ${opt}"
		case $opt in
			h) # Usage
				printUsage
				exit 0
				;;
			v) # version
				printVersion
				exit 0
				;;
			\?)
				echo "Invalid option:  -$OPTARG" >&2
				printUsage
				exit 1
				;;
			:)
				echo "Option -$OPTARG requires an argument" >&2
				printUsage
				exit 1
				;;
		esac
	done
}

# Print the program usage
printUsage() {
	echo ""
	echo "Usage:  1-create-gp-tar.sh"
	echo ""
	echo "Create a temporary local copy of the GeoProcessor files into build-util/build-tmp."
	echo "The results are packaged into gp and gptest virtual environments."
	echo "The gptest version has QGIS code filtered out so no runtime QGIS dependency."
	echo ""
	echo "-h  Print the usage."
	echo "-v  Print the version."
	echo ""
}

# Print the program version
printVersion() {
	echo ""
	echo "1-create-gp-tar.sh version ${programVersion} ${programVersionDate}"
	echo ""
	echo "GeoProcessor build utilities"
	echo "Copyright 2017-2019 Open Water Foundation."
	echo ""
	echo "License GPLv3+:  GNU GPL version 3 or later"
	echo ""
	echo "There is ABSOLUTELY NO WARRANTY; for details see the"
	echo "'Disclaimer of Warranty' section of the GPLv3 license in the LICENSE file."
	echo "This is free software: you are free to change and redistribute it"
	echo "under the conditions of the GPLv3 license in the LICENSE file."
	echo ""
}

# Setup the echo command and colors
setupEcho() {
	# Determine which echo to use, needs to support -e to output colored text
	# - normally built-in shell echo is OK, but on Debian Linux dash is used, and it does not support -e
	echo2='echo -e'
	testEcho=`echo -e test`
	if [ "${testEcho}" = '-e test' ]; then
		# The -e option did not work as intended.
		# -using the normal /bin/echo should work
		# -printf is also an option
		echo2='/bin/echo -e'
	fi

	# Strings to change colors on output, to make it easier to indicate when actions are needed
	# - Colors in Git Bash:  https://stackoverflow.com/questions/21243172/how-to-change-rgb-colors-in-git-bash-for-windows
	# - Useful info:  http://webhome.csc.uvic.ca/~sae/seng265/fall04/tips/s265s047-tips/bash-using-colors.html
	# - See colors:  https://en.wikipedia.org/wiki/ANSI_escape_code#Unix-like_systems
	# - Set the background to black to eensure that white background window will clearly show colors contrasting on black.
	# - Yellow "33" in Linux can show as brown, see:  https://unix.stackexchange.com/questions/192660/yellow-appears-as-brown-in-konsole
	# - Tried to use RGB but could not get it to work - for now live with "yellow" as it is
	warnColor='\e[0;40;33m' # warning - user needs to do something, 40=background black, 33=yellow
	failColor='\e[0;40;31m' # critical issue - could be fatal, 40=background black, 31=red
	okColor='\e[0;40;32m' # status is good, 40=background black, 32=green
	endColor='\e[0m' # To switch back to default color
}

# Main entry point into the script
# - TODO smalers 2019-01-01 could organize more of the following code into functions.

programVersion="1.2.0"
programVersionDate="2019-01-02"

# Initialize variables
# - QGIS Python version is set by checkQgisPythonVersion
qgisPythonVersion="unknown"
qgisPythonFolder="unknown"
# - Operating system python version is set by checkOperatingSystemPythonVersion
osPythonVersion="unknown"
osPythonFolder="unknown"
# Echo command is the default but check below with setupEcho function
echo2="echo"

#------------------------------------------------------------------------------------------
# Step 0. Setup.
# Get the folder where this script is located since it may have been run from any folder
scriptFolder=`cd $(dirname "$0") && pwd`

# Setup echo command and colors
# - use colored text to highlight issues
setupEcho

# Parse the command line
parseCommandLine "$@"

# Determine the operating system
# - put this before other function calls because logic depends on operating system
checkOperatingSystem

# Check the QGIS and operating system Python versions
# - to help ensure compatibility in testing and deployed versions
checkQgisPythonVersion
checkOperatingSystemPythonVersion

# Define top-level folders - everything is relative to this below to avoid confusion
repoFolder=`dirname ${scriptFolder}`
buildUtilFolder="${scriptFolder}"
buildTmpFolder="${buildUtilFolder}/build-tmp"
# Get the software version number
versionFile="${repoFolder}/geoprocessor/app/version.py"
version=`cat ${versionFile} | grep app_version -m 1 | cut -d '=' -f 2 | tr -d " " | tr -d '"'`

# Echo information 
echo "Project (main repository) folder is ${repoFolder}"
echo "build-util folder is ${buildUtilFolder}"
echo "build-tmp folder is ${buildTmpFolder}"
echo "GeoProcessor version (from ${versionFile}) is ${version}"

# Check to see if folders exist.  If not, something is probably wrong so don't continue.
if [ ! -d ${repoFolder} ]; then
	echo "Something is wrong.  Repository folder does not exist:  ${repoFolder}"
	exit 1
fi
if [ ! -d ${buildUtilFolder} ]; then
	echo "Something is wrong.  build-util folder does not exist:  ${buildUtilFolder}"
	exit 1
fi
if [ ! -d ${buildTmpFolder} ]; then
	echo "Something is wrong.  build-tmp folder does not exist:  ${buildTmpFolder}"
	exit 1
fi

# Check to see if needed software is installed.
# - If not, developers will need to know how to do it based on the shell environment that is used.
# - If the result of checks is an empty string, the program was not found
# - OK to see standard error message from the following to help figure out issue
# - if the first character of the 'which` output is a / then assume the program was found

tarProgramPath=`which tar`
if [ ! -z "${tarProgramPath}" ]; then
	tarProgramPath1=`echo $tarProgramPath | cut -c1`
fi
gzipProgramPath=`which gzip`
if [ ! -z "${gzipProgramPath}" ]; then
	gzipProgramPath1=`echo $gzipProgramPath | cut -c1`
fi
zipProgramPath=`which zip`
if [ ! -z "${zipProgramPath}" ]; then
	zipProgramPath1=`echo $zipProgramPath | cut -c1`
fi

if [ -z "${tarProgramPath}" ] || [ "${tarProgramPath1}" != "/" ]; then
	echo "Required program 'tar' is not found.  Must install.  Exiting."
	exit 1
fi
if [ -z "${gzipProgramPath}" ] || [ "${gzipProgramPath1}" != "/" ]; then
	echo "Required program 'gzip' is not found.  Must install.  Exiting."
	exit 1
fi
if [ -z "${zipProgramPath}" ] || [ "${zipProgramPath1}" != "/" ]; then
	if [ "${operatingSystem}" != "linux" ]; then
		# Only require zip if on Windows variant operating system
		echo "Required program 'zip' is not found.  Must install.  Exiting."
		exit 1
	else
		# Set to blank so can check below
		zipProgramPath=""
	fi
fi

# Global error flag check
# - set to "yes" if any issue occurs below
# - runner can check messages to see what issue occurred and decide what to do
errorOccurred="no"

#------------------------------------------------------------------------------------------
# These steps build the tar.gz installer for gptest,
# which is used for functional testing but has no QGIS code enabled.
#------------------------------------------------------------------------------------------
# Step 1. Copy all files to be distributed to a temporary folder

buildTmpGptestFolder="${buildTmpFolder}/tmp-gptest-${version}"
if [ -d "${buildTmpGptestFolder}" ]; then
	echo "Removing contents of temporary build temporary folder ${buildTmpGptestFolder} ..."
	rm -rf ${buildTmpGptestFolder}
fi

# Recreate the temporary folder

echo "Creating temporary build temporary folder ${buildTmpGptestFolder} ..."
mkdir ${buildTmpGptestFolder}

#------------------------------------------------------------------------------------------
# Step 2.  Copy GeoProcessor files to the temporary folder

echo "Copying GeoProcessor files to ${buildTmpGptestFolder} ..."
cp -rp ${repoFolder}/geoprocessor ${buildTmpGptestFolder}
# Copy only the scripts relevant to the test framework
mkdir ${buildTmpGptestFolder}/scripts
cp ${repoFolder}/scripts/gptest ${buildTmpGptestFolder}/scripts
cp ${repoFolder}/scripts/gptestui ${buildTmpGptestFolder}/scripts
cp ${buildUtilFolder}/install/install-gp-venv.sh ${buildTmpGptestFolder}/scripts
# Make sure files are executable
chmod a+x ${buildTmpGptestFolder}/scripts/*

#------------------------------------------------------------------------------------------
# Step 3. Update the temporary files to translate from full GeoProcessor to testing version
# - comment out QGIS imports
# - comment out or use pass to ignore QGIS-related commands in the GeoProcessorCommandFactory
echo "Updating GeoProcessorCommandFactory.py file to version with QGIS commands commented out ..."
#
# GeoProcessorCommandFactory
# Comment out the QGIS imports...
sed -i 's/^from geoprocessor.commands.layers/# from geoprocessor.commands.layers/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
#
# GeoProcessorCommandFactory
# Comment out the QGIS commands in the registered_commands dictionary...
sed -i 's/"ADDGEOLAYERATTRIBUTE": /# "ADDGEOLAYERATTRIBUTE": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"CLIPGEOLAYER": /# "CLIPGEOLAYER": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"COPYGEOLAYER": /# "COPYGEOLAYER": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"CREATEGEOLAYERFROMGEOMETRY": /# "CREATEGEOLAYERFROMGEOMETRY": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"FREEGEOLAYERS": /# "FREEGEOLAYERS": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"INTERSECTGEOLAYER": /# "INTERSECTGEOLAYER": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"MERGEGEOLAYERS": /# "MERGEGEOLAYERS": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"READGEOLAYERFROMDELIMITEDFILE": /# "READGEOLAYERFROMDELIMITEDFILE": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"READGEOLAYERFROMGEOJSON": /# "READGEOLAYERFROMGEOJSON": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"READGEOLAYERFROMSHAPEFILE": /# "READGEOLAYERFROMSHAPEFILE": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"READGEOLAYERSFROMFGDB": /# "READGEOLAYERSFROMFGDB": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"READGEOLAYERSFROMFOLDER": /# "READGEOLAYERSFROMFOLDER": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"REMOVEGEOLAYERATTRIBUTES": /# "REMOVEGEOLAYERATTRIBUTES": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"RENAMEGEOLAYERATTRIBUTE": /# "RENAMEGEOLAYERATTRIBUTE": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"SETGEOLAYERCRS": /# "SETGEOLAYERCRS": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"SETGEOLAYERPROPERTY": /# "SETGEOLAYERPROPERTY": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"SETPROPERTYFROMGEOLAYER": /# "SETPROPERTYFROMGEOLAYER": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"SIMPLIFYGEOLAYERGEOMETRY": /# "SIMPLIFYGEOLAYERGEOMETRY": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"WRITEGEOLAYERPROPERTIESTOFILE": /# "WRITEGEOLAYERPROPERTIESTOFILE": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"WRITEGEOLAYERTODELIMITEDFILE": /# "WRITEGEOLAYERTODELIMITEDFILE": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"WRITEGEOLAYERTOGEOJSON": /# "WRITEGEOLAYERTOGEOJSON": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"WRITEGEOLAYERTOSHAPEFILE": /# "WRITEGEOLAYERTOSHAPEFILE": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"WRITEGEOLAYERTOKML": /# "WRITEGEOLAYERTOKML": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
#
# GeoProcessorCommandFactory
# Replace the QGIS command construction with pass...
sed -i 's/return AddGeoLayerAttribute/pass  # return AddGeoLayerAttribute/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return ClipGeoLayer/pass  # return ClipGeoLayer/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return CopyGeoLayer/pass  # return CopyGeoLayer/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return CreateGeoLayerFromGeometry/pass  # return CreateGeoLayerFromGeometry/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return FreeGeoLayers/pass  # return FreeGeoLayers/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return IntersectGeoLayer/pass  # return IntersectGeoLayer/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return MergeGeoLayers/pass  # return MergeGeoLayers/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return ReadGeoLayerFromDelimitedFile/pass  # return ReadGeoLayerFromDelimitedFile/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return ReadGeoLayerFromGeoJSON/pass  # return ReadGeoLayerFromGeoJSON/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return ReadGeoLayerFromShapefile/pass  # return ReadGeoLayerFromShapefile/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return ReadGeoLayersFromFGDB/pass  # return ReadGeoLayersFromFGDB/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return ReadGeoLayersFromFolder/pass  # return ReadGeoLayersFromFolder/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return RemoveGeoLayerAttributes/pass  # return RemoveGeoLayerAttributes/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return RenameGeoLayerAttribute/pass  # return RenameGeoLayerAttribute/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return SetGeoLayerCRS/pass  # return SetGeoLayerCRS/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return SetGeoLayerProperty/pass  # return SetGeoLayerProperty/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return SetPropertyFromGeoLayer/pass  # return SetPropertyFromGeoLayer/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return SimplifyGeoLayerGeometry/pass  # return SimplifyGeoLayerGeometry/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return WriteGeoLayerPropertiesToFile/pass  # return WriteGeoLayerPropertiesToFile/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return WriteGeoLayerToDelimitedFile/pass  # return WriteGeoLayerToDelimitedFile/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return WriteGeoLayerToGeoJSON/pass  # return WriteGeoLayerToGeoJSON/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return WriteGeoLayerToShapefile/pass  # return WriteGeoLayerToShapefile/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return WriteGeoLayerToKML/pass  # return WriteGeoLayerToKML/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
# GeoProcessorCommandFactory
# Comment out the imports of commands that rely on QGIS...
sed -i 's/^from geoprocessor.ui.commands.layers.ReadGeoLayerFromGeoJSON/# from geoprocessor.ui.commands.layers.ReadGeoLayerFromGeoJSON/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#
# GeoProcessorCommandEditorFactory
# Replace the QGIS command editor construction with pass...
# These commands will be enabled over time
#sed -i 's/return AddGeoLayerAttribute/pass  # return AddGeoLayerAttribute/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return ClipGeoLayer/pass  # return ClipGeoLayer/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return CopyGeoLayer/pass  # return CopyGeoLayer/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return CreateGeoLayerFromGeometry/pass  # return CreateGeoLayerFromGeometry/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return FreeGeoLayers/pass  # return FreeGeoLayers/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return IntersectGeoLayer/pass  # return IntersectGeoLayer/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return MergeGeoLayers/pass  # return MergeGeoLayers/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return ReadGeoLayerFromDelimitedFile/pass  # return ReadGeoLayerFromDelimitedFile/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
sed -i 's/command_editor = ReadGeoLayerFromGeoJSON_Editor/pass  # command_editor = ReadGeoLayerFromGeoJSON_Editor/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return ReadGeoLayerFromShapefile/pass  # return ReadGeoLayerFromShapefile/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return ReadGeoLayersFromFGDB/pass  # return ReadGeoLayersFromFGDB/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return ReadGeoLayersFromFolder/pass  # return ReadGeoLayersFromFolder/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return RemoveGeoLayerAttributes/pass  # return RemoveGeoLayerAttributes/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return RenameGeoLayerAttribute/pass  # return RenameGeoLayerAttribute/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return SetGeoLayerCRS/pass  # return SetGeoLayerCRS/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return SetGeoLayerProperty/pass  # return SetGeoLayerProperty/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return SetPropertyFromGeoLayer/pass  # return SetPropertyFromGeoLayer/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return SimplifyGeoLayerGeometry/pass  # return SimplifyGeoLayerGeometry/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return WriteGeoLayerPropertiesToFile/pass  # return WriteGeoLayerPropertiesToFile/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return WriteGeoLayerToDelimitedFile/pass  # return WriteGeoLayerToDelimitedFile/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return WriteGeoLayerToGeoJSON/pass  # return WriteGeoLayerToGeoJSON/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return WriteGeoLayerToShapefile/pass  # return WriteGeoLayerToShapefile/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py
#sed -i 's/return WriteGeoLayerToKML/pass  # return WriteGeoLayerToKML/g' ${buildTmpGptestFolder}/geoprocessor/ui/core/GeoProcessorCommandEditorFactory.py

# Change all directories to have permission of drwxr-xr-xr-x
echo "Changing permissions on directories..."
find ${buildTmpGptestFolder}/geoprocessor -type d -exec chmod 755 {} \;

# Change all files to have permission of -rw-r--r--
echo "Changing permissions on files..."
find ${buildTmpGptestFolder}/geoprocessor -type f -exec chmod 744 {} \;

# Update the geoprocessor/util/qgis_util.py module:
# - comment out lines that contain "import qgis.utils"
# - comment out lines that contain "from plugins.processing.core"
# - comment out lines that contain "from qgis.analysis import"
# - comment out lines that contain "from qgis.core import"
# - comment out lines that contain "from qgis.utils import"
# - comment out lines that contain "from processing.core.Processing import""
# - comment out lines that contain "from PyQt4.QtCore import""
# - Could do on one line with chained sed commands but separate lines is more readable and can test separately.
echo "Updating geoprocessor/util/qgis_util.py to comment out QGIS module imports and references..."
sed -i 's/^from plugins.processing.core/# from plugins.processing.core/g' ${buildTmpGptestFolder}/geoprocessor/util/qgis_util.py
sed -i 's/^from qgis.analysis import/# from qgis.analysis import/g' ${buildTmpGptestFolder}/geoprocessor/util/qgis_util.py
sed -i 's/^from qgis.core import/# from qgis.core import/g' ${buildTmpGptestFolder}/geoprocessor/util/qgis_util.py
sed -i 's/^from qgis.utils import/# from qgis.utils import/g' ${buildTmpGptestFolder}/geoprocessor/util/qgis_util.py
sed -i 's/^from processing.core.Processing import/# from processing.core.Processing import/g' ${buildTmpGptestFolder}/geoprocessor/util/qgis_util.py
sed -i 's/^from PyQt4.QtCore import/# from PyQt4.QtCore import/g' ${buildTmpGptestFolder}/geoprocessor/util/qgis_util.py

sed -i 's/^import qgis.utils/# import qgis.utils/g' ${buildTmpGptestFolder}/geoprocessor/util/qgis_util.py

# Update the geoprocessor/core/GeoProcessor.py module:
# - comment out line "import geoprocessor.util.qgis_util as qgis_util"
echo "Updating geoprocessor/core/GeoProcessor.py to comment out QGIS module imports and references..."
sed -i 's/^import geoprocessor.util.qgis_util as qgis_util/# import geoprocessor.util.qgis_util as qgis_util/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessor.py
sed -i 's/self.properties\["QGISVersion"\] = qgis_util.get_qgis_version_str()/# self.properties\["QGISVersion"\] = qgis_util.get_qgis_version_str()/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessor.py
sed -i 's/protected_property_names = \["InitialWorkingDir", "WorkingDir", "QGISVersion"\]/protected_property_names = \["InitialWorkingDir", "WorkingDir"\]/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessor.py
sed -i 's/self.qgis_processor = qgis_util.initialize_qgis_processor()/# self.qgis_processor = qgis_util.initialize_qgis_processor()/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessor.py

# Update the geoprocessor/ui/app/GeoProcessorUI.py module:
# - comment out lines that reference QGIS
echo "Updating geoprocessor/ui/app/GeoProcessorUI.py to comment out QGIS module imports and references..."
sed -i 's/^import geoprocessor.util.qgis_util/# import geoprocessor.util.qgis_util/g' ${buildTmpGptestFolder}/geoprocessor/ui/app/GeoProcessorUI.py
sed -i 's/^from geoprocessor.ui.commands.layers.ReadGeoLayerFromGeoJSON_Editor/# from geoprocessor.ui.commands.layers.ReadGeoLayerFromGeoJSON_Editor/g' ${buildTmpGptestFolder}/geoprocessor/ui/app/GeoProcessorUI.py
sed -i 's/^import qgis.utils/# import qgis.utils/g' ${buildTmpGptestFolder}/geoprocessor/ui/app/GeoProcessorUI.py
sed -i 's/^import qgis.gui/# import qgis.gui/g' ${buildTmpGptestFolder}/geoprocessor/ui/app/GeoProcessorUI.py
sed -i 's/qgis_version =/qgis_version = "unknown" # /g' ${buildTmpGptestFolder}/geoprocessor/ui/app/GeoProcessorUI.py
sed -i 's/self.canvas =/# self.canvas =/g' ${buildTmpGptestFolder}/geoprocessor/ui/app/GeoProcessorUI.py
sed -i 's/self.canvas.set/pass  # self.canvas.set/g' ${buildTmpGptestFolder}/geoprocessor/ui/app/GeoProcessorUI.py
sed -i 's/self.canvas.resize/pass  # self.canvas.resize/g' ${buildTmpGptestFolder}/geoprocessor/ui/app/GeoProcessorUI.py
sed -i 's/extent = qgis/# extent = qgis/g' ${buildTmpGptestFolder}/geoprocessor/ui/app/GeoProcessorUI.py
sed -i 's/self.toolPan/# self.toolPan/g' ${buildTmpGptestFolder}/geoprocessor/ui/app/GeoProcessorUI.py
sed -i 's/self.toolZoomIn/# self.toolZoomIn/g' ${buildTmpGptestFolder}/geoprocessor/ui/app/GeoProcessorUI.py
sed -i 's/self.toolZoomOut/# self.toolZoomOut/g' ${buildTmpGptestFolder}/geoprocessor/ui/app/GeoProcessorUI.py

# Update the geoprocessor/util/validator_util.py module:
# - comment out line of import geoprocessor.util.qgis_util as qgis_util
# - Could do on one line with chained sed commands but separate lines is more readable and can test separately.
echo "Updating geoprocessor/util/validator_util.py to comment out QGIS module imports and references..."
sed -i 's/^import geoprocessor.util.qgis_util as qgis_util/# import geoprocessor.util.qgis_util as qgis_util/g' ${buildTmpGptestFolder}/geoprocessor/util/validator_util.py
sed -i 's/^import ogr/# import ogr/g' ${buildTmpGptestFolder}/geoprocessor/util/validator_util.py

# Update the geoprocessor/app/gp.py module:
# - comment out the call to qgis_util.initialize_qgis(...)
# - comment out the call to qgis_util.exit_qgis(...)
echo "Updating geoprocessor/app/gp.py to comment out QGIS initialize/stop calls ..."
# Older version...
# - may need to detect and use
# sed -i 's/qgis_util.initialize_qgis/# qgis_util.initialize_qgis/g' ${buildTmpGptestFolder}/geoprocessor/app/gp.py
# New version as of GeoProcessor 1.1.0...
# The following indicates that QGIS is not enabled for application setup
sed -i 's/if qgis_util.qgs_app is None:/if None is None:  # if qgis_util.qgs_app is None:/g' ${buildTmpGptestFolder}/geoprocessor/app/gp.py
sed -i 's/sys.exit(qgis_util.qgs_app.exec_())/pass  # sys.exit(qgis_util.qgs_app.exec_())/g' ${buildTmpGptestFolder}/geoprocessor/app/gp.py
#
sed -i 's/qgs_app = qgis_util.initialize_qgis/pass  # qgs_app = qgis_util.initialize_qgis/g' ${buildTmpGptestFolder}/geoprocessor/app/gp.py
sed -i 's/qgis_util.exit_qgis/pass  # qgis_util.exit_qgis/g' ${buildTmpGptestFolder}/geoprocessor/app/gp.py
sed -i 's/^import geoprocessor.util.qgis_util as qgis_util/# import geoprocessor.util.qgis_util as qgis_util/g' ${buildTmpGptestFolder}/geoprocessor/app/gp.py

# Check the code to make sure QGIS references have been removed
checkGptestCode

#------------------------------------------------------------------------------------------
# Step 4a. Tar up all the *.py files in the geoprocessor folder for gptest distribution

gptestSitePackageBuildFile="${buildTmpFolder}/gptest-${version}-site-package.tar"
gptestSitePackageBuildFileGz="${buildTmpFolder}/gptest-${version}-site-package.tar.gz"

if [ -e "${gptestSitePackageBuildFileGz}" ]; then
	echo "Removing existing build file ${gptestSitePackageBuildFileGz}"
	rm ${gptestSitePackageBuildFileGz}
fi

echo "Creating tar file containing *.py *png *.gif files ..."
cd "${buildTmpGptestFolder}"
find geoprocessor \( -name '*.py' -o -name '*.png' -o -name '*.gif' \) -exec tar -rvf ${gptestSitePackageBuildFile} {} \;
if [ "$?" -ne 0 ]; then
	echo "Error in script.  Exiting."
	exit $?
fi
echo "Gzipping file ${gptestSitePackageBuildFile} into ${gptestSitePackageBuildFileGz}"
if [ -z ${gzipProgramPath} ]; then
	echo "[ERROR] gzip program was not found.  Unable to gzip ${gptestSitePackageBuildFile}"
		errorOccurred="yes"
else
	gzip ${gptestSitePackageBuildFile}
	if [ "$?" -ne 0 ]; then
		echo "[ERROR] Error using gzip on ${gptestSitePackageBuildFile}"
		errorOccurred="yes"
	fi
fi

#------------------------------------------------------------------------------------------
# Step 4b. Zip up all the *.py files in the geoprocessor folder for full distribution
# - skip if zip program is not installed (should generally be in path)

gptestSitePackageBuildFileZip="${buildTmpFolder}/gptest-${version}-site-package.zip"

if [ -e "${gptestSitePackageBuildFileZip}" ]; then
	echo "Removing existing build file ${gptestSitePackageBuildFileZip}"
	rm ${gptestSitePackageBuildFileZip}
fi

echo "Creating zip file containing *.py files ${gptestSitePackageBuildFileZip} ..."
cd "${buildTmpGptestFolder}"
if [ -z ${zipProgramPath} ]; then
	if [ "${operatingSystem}" != "linux" ]; then
		echo "[ERROR] zip program was not found.  Unable to create zip file ${gptestSitePackageBuildFileZip}"
		errorOccurred="yes"
	fi
else
	zip -r ${gptestSitePackageBuildFileZip} geoprocessor -x '*.pyc'
	if [ "$?" -ne 0 ]; then
		echo "[ERROR] Error using zip to create ${gptestSitePackageBuildFileZip}"
		errorOccurred="yes"
	fi
fi

#------------------------------------------------------------------------------------------
# These steps build the tar.gz installer for gp, which is used for full QGIS integration.
#------------------------------------------------------------------------------------------
# Step 1. Copy all files to be distributed to a temporary folder

buildTmpGpFolder="${buildTmpFolder}/tmp-gp-${version}"
if [ -d "${buildTmpGpFolder}" ]; then
	echo "Removing contents of temporary build temporary folder ${buildTmpGpFolder} ..."
	rm -rf ${buildTmpGpFolder}
fi

# Recreate the temporary folder

echo "Creating temporary build folder ${buildTmpGpFolder} ..."
mkdir ${buildTmpGpFolder}

#------------------------------------------------------------------------------------------
# Step 2.  Copy GeoProcessor files to the temporary folder

echo "Copying GeoProcessor files to ${buildTmpGpFolder} ..."
cp -rp ${repoFolder}/geoprocessor ${buildTmpGpFolder}
mkdir ${buildTmpGpFolder}/scripts
cp ${repoFolder}/scripts/gp ${buildTmpGpFolder}/scripts
cp ${repoFolder}/scripts/gp.bat ${buildTmpGpFolder}/scripts
cp ${repoFolder}/scripts/gptest ${buildTmpGpFolder}/scripts
cp ${repoFolder}/scripts/gptestui ${buildTmpGpFolder}/scripts
cp ${repoFolder}/scripts/gpui ${buildTmpGpFolder}/scripts
cp ${repoFolder}/scripts/gpui.bat ${buildTmpGpFolder}/scripts

#------------------------------------------------------------------------------------------
# Step 3. Update the temporary files for packaging
# - Unlike gptest, don't need to do anything since it is a full distribution

#------------------------------------------------------------------------------------------
# Step 4. Tar up all the *.py files in the geoprocessor folder

gpSitePackageBuildFile="${buildTmpFolder}/gp-${version}-site-package.tar"
gpSitePackageBuildFileGz="${buildTmpFolder}/gp-${version}-site-package.tar.gz"

if [ -e "${gpSitePackageBuildFileGz}" ]; then
	echo "Removing existing build file ${gpSitePackageBuildFileGz}"
	rm ${gpSitePackageBuildFileGz}
fi

echo "Creating tar file containing *.py *png *.gif files ..."
cd "${buildTmpGpFolder}"
find geoprocessor \( -name '*.py' -o -name '*.png' -o -name '*.gif' \) -exec tar -rvf ${gpSitePackageBuildFile} {} \;
if [ "$?" -ne 0 ]; then
	echo "Error in script.  Exiting."
	exit $?
fi
echo "Gzipping file ${gpSitePackageBuildFile} into ${gpSitePackageBuildFileGz}"
if [ -z ${gzipProgramPath} ]; then
	echo "[ERROR] gzip program was not found.  Unable to gzip ${gpSitePackageBuildFile}"
	errorOccurred="yes"
else
	gzip ${gpSitePackageBuildFile}
	if [ "$?" -ne 0 ]; then
		echo "[ERROR] Error using gzip on ${gpSitePackageBuildFile}"
		errorOccurred="yes"
	fi
fi

#------------------------------------------------------------------------------------------
# Step 4b. Zip up all the *.py files in the geoprocessor folder

gpSitePackageBuildFileZip="${buildTmpFolder}/gp-${version}-site-package.zip"

if [ -e "${gpSitePackageBuildFileZip}" ]; then
	echo "Removing existing build file ${gpSitePackageBuildFileZip}"
	rm ${gpSitePackageBuildFileZip}
fi

echo "Creating zip file containing *.py files ${gpSitePackageBuildFileZip} ..."
cd "${buildTmpGpFolder}"
if [ -z ${zipProgramPath} ]; then
	if [ "${operatingSystem}" != "linux" ]; then
		# Only an issue for Windows variant operating systems
		echo "[ERROR] zip program was not found.  Unable to create zip file ${gpSitePackageBuildFileZip}"
		errorOccurred="yes"
	fi
else
	zip -r ${gpSitePackageBuildFileZip} geoprocessor -x '*.pyc'
	if [ "$?" -ne 0 ]; then
		echo "[ERROR] Error using zip to create ${gpSitePackageBuildFileZip}"
	fi
fi

#------------------------------------------------------------------------------------------
# Final comment to software developer

if [ "${errorOccurred}" = "yes" ]; then
	echo ""
	echo "An error occurred creating installers.  Check messages above."
	echo "- Partial results may have been created, such as tar.gz but not .zip"
	echo "- Maybe need to use another shell (Cygwin, Git Bash, Windows Bash, Linux)."
	echo "- Sometimes Cygwin drops processes so just rerun."
	echo ""
fi

echo ""
echo "Install files were created in ${buildTmpFolder} folder"
echo "- Look for *.tar.gz and *.zip files"
echo "- Install the files in the site-packages folder of the target Python 3 environment"
echo "- The files are used to create the virtual environment via the 2-create-gp-venv script"
echo "- The files are also used to update the virtual environment via the 2-update-gp-venv script"
echo "- The 'geoprocessor' folder should be in a folder indicated by Python sys.path"
if [ ! "$qgisPythonVersion" = "osPythonVersion" ]; then
	$echo2 "${warnColor}- QGIS Python version $qgisPythonVersion is different than latest operating system version ${osPythonVersion}.${endColor}"
	$echo2 "${warnColor}  - May be OK if close enough but may need to take action to create a compatible virtual environment.${endColor}"
	$echo2 "${warnColor}  - QGIS Python folder is $qgisPythonFolder${endColor}"
fi
echo ""

# Exit with appropriate error status
if [ "${errorOccurred}" = "yes" ]; then
	exit 1
else
	exit 0
fi
