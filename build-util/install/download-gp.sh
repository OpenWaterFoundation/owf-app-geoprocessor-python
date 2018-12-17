#!/bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL
#
# download-gp - download the gp installer from Open Water Foundation website

# URL where the product is found
# - include the user ID in the extracted working folder
# - TODO might need to make /tmp files unique using process ID or timestamp
#   but it is unlikely that two installs will be run at the same time by the same user
gpUrl="http://software.openwaterfoundation.org/geoprocessor"
gpVersionUrl="http://software.openwaterfoundation.org/geoprocessor/1.0.0"
gpVersionTargzUrl="http://software.openwaterfoundation.org/geoprocessor/1.0.0/gptest-1.0.0-lin-venv.tar.gz"
tmpTargzFile=$(basename $gpVersionTargzUrl)
tmpTargzFilePath="/tmp/$tmpTargzFile"

# Get the location where this script is located since it may have been run from any folder
scriptFolder=`cd $(dirname "$0") && pwd`

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

# Check for required software that if missing would break this script
# - If not, provide guidance and exit
# - If the result of checks is an empty string, the program was not found
# - OK to see standard error message from the following to help figure out issue
# - If the first character of the 'which` output is a / then assume the program was found
checkRequiredSoftware() {
	# Check for curl
	curlProgramPath1=""
	curlProgramPath=$(which curl)
	if [ ! -z "${curlProgramPath}" ]; then
        	curlProgramPath1=$(echo $curlProgramPath | cut -c1)
	fi
	if [ "${curlProgramPath1}" != "/" ]; then
		echo ""
		echo "[ERROR] curl program is not found.  Cannot download GeoProcessor software."
		if [ "${operatingSystem}" = "linux" ]; then
			echo ""
			echo "To install, run: [sudo] apt-get install curl"
			echo ""
		fi
		exit 1
	fi
	# Check for jq
	jqProgramPath1=""
	jqProgramPath=$(which jq)
	if [ ! -z "${jqProgramPath}" ]; then
        	jqProgramPath1=$(echo $jqProgramPath | cut -c1)
	fi
	if [ "${jqProgramPath1}" != "/" ]; then
		echo ""
		echo "[ERROR] jq program is not found.  Cannot download GeoProcessor software."
		if [ "${operatingSystem}" = "linux" ]; then
			echo ""
			echo "To install, run: [sudo] apt-get install jq"
			echo ""
		fi
		exit 1
	fi
}

# Download the installer and save to the /tmp folder
downloadInstaller() {
	# Select which installer to download
	# - for now hard-code but need to check a catalog of available versions
	echo ""
	echo "Select the GeoProcessor version to install"
	echo "Currently this is hard-coded to version 1.1.0 - will allow selecting in the future."
	read -p "Continue?  [Y/n]  " answer
	if [ -z "$answer" -o "$answer" = "y" -o "$answer" = "Y" ]; then
		# OK to continue
		: # do nothing
	else
		echo "Exiting GeoProcessor download and installation."
		exit 0
	fi

	echo "Downloading the GeoProcessor installer from ${gpVersionTargzUrl}..."
	# Don't check for existence, does not seem to work as shown below
	checkFirst="no"
	if [ $checkFirst = "yes" ]; then
		# First check for file existence, could be used to probe multiple sites or versions, etc.
		# - see:  https://stackoverflow.com/questions/12199059/how-to-check-if-an-url-exists-with-the-shell-and-probably-curl
		# - retrieve only the first byte
		# - this does not seem to work
		if curl --output /dev/null --fail -r 0-0 "$gpVersionTargzUrl"; then
			echo ""
			echo "[Error] GeoProcessor download file does not exist: $gpVersionTargzUrl"
			echo ""
			exit 1
		fi
	fi
	# Try the full download
	echo ""
	echo "Downloading the GeoProcessor software..."
	set -x
	curl --fail -o $tmpTargzFilePath $gpVersionTargzUrl
	{ set +x; } 2> /dev/null
	if [ $? -ne 0 ]; then
		echo ""
		echo "[Error] Error downloading GeoProcessor installer."
		exit 1
	fi
}

# Install the GeoProcessor venv to the final location
# - this moves to the indicated location and updates venv scripts to use that location
installVenv() {
	venvInstallFolder="$HOME/gptest-venv"
	echo ""
	echo "Installing the GeoProcesor virtual environment to $venvInstallFolder"
	echo "Use the following to specify the tar.gz file: $tmpTargzFilePath"
	# The following is currently interactive
	# - need to add way to specify destination on command line
	# - install under users home folder so it can be used in more than one project?
	# - or specific to a repo?
	cd "$scriptFolder"
	../3-install-gp-venv-for-user.sh
	if [ $? -ne 0 ]; then
		echo ""
		echo "[Error] Error installing GeoProcessor venv in final location"
		exit 1
	fi
}

# Unzip the venv.tar.gz file in /tmp
# - NOT CURRENTLY NEEDED OR USED
unzipInstaller() {
	echo ""
	echo "Unzipping into folder $tmpExtractedPath"
	if [ -d "${tmpExtractedPath}" ]; then
		echo "Removing existing ${tmpExtractedPath}"
		# Extra precaution, make sure the extracted path starts with /tmp
		extractedFileBasename=$(basename ${tmpExtractedPath})
		if [ "$extractedFileBasename" = "/tmp" ]; then
			echo ""
			echo "[ERROR] Folder to extract to is not in /tmp.  Exiting."
			exit 1
		fi
		rm -rf ${tmpExtractedPath}
		if [ $? -ne 0 ]; then
			echo ""
			echo "[ERROR] removing existing ${tmpExtractedPath}.  Exiting."
			exit 1
		fi
	fi
	# Create the extracted folder
	mkdir ${tmpExtractedPath}
	if [ $? -ne 0 ]; then
		echo ""
		echo "[ERROR] could not create ${tmpExtractedPath}.  Exiting."
		exit 1
	fi
	# Now unzip
	cd ${tmpExtractedPath}
	tar -xzvf "$tmpTargzFilePath"
	if [ $? -ne 0 ]; then
		echo ""
		echo "[ERROR] extracting GeoProcessor to ${tmpExtractedPath}.  Exiting."
		exit 1
	fi
}

# Entry point into main script
# - functions are called below

# Check the operating system
checkOperatingSystem

# Check for required software
checkRequiredSoftware

# Download the installer into /tmp
downloadInstaller

# Unzip and move the Python venv to the desired install location
installVenv

# Exit with success status
exit 0
