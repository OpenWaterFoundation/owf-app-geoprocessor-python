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
#tmpTargzFilePath="/tmp/$tmpTargzFile"
#tmpTargzFile=$(basename $gpVersionTargzUrl)

# Catalog file as URL and temporary file
gpCatalogTxtUrl="http://software.openwaterfoundation.org/geoprocessor/catalog.txt"
tmpCatalogTxtFile="gp-catalog.txt"
tmpCatalogTxtPath="/tmp/$tmpCatalogTxtFile"

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
			operatingSystemShort="cyg"
			;;
		LINUX*)
			operatingSystem="linux"
			operatingSystemShort="lin"
			;;
		MINGW*)
			operatingSystem="mingw"
			operatingSystemShort="min"
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
	# Not needed yet but may use for catalog file
	needJq="no"
	if [ "needJq" = "yes" ]; then
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
	fi
}

# Download the installer and save to the /tmp folder
# selectedInstallerVersion was set previously
# selectedInstallerFile was set previously
downloadInstaller() {
	# Select which installer to download
	# - for now hard-code but need to check a catalog of available versions
	gpVersionTargzUrl="http://software.openwaterfoundation.org/geoprocessor/${selectedInstallerVersion}/${selectedInstallerFile}"
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
	if [ ! -d "/tmp/$USER" ]; then
		mkdir /tmp/$USER
	fi
	tmpTargzFile=$(basename $gpVersionTargzUrl)
	tmpTargzFilePath="/tmp/$USER/$selectedInstallerFile"
	set -x
	curl --fail -o $tmpTargzFilePath $gpVersionTargzUrl ; set errorCode=$?
	{ set +x; } 2> /dev/null
	if [ $errorCode -ne 0 ]; then
		echo ""
		echo "[Error] Error downloading GeoProcessor installer $gpVersionTargzUrl"
		exit 1
	fi
}

# Extract the install-gp-venv.sh script to a temporary location
# - then it can be run to move the tar.gz contents to final location
# - the file to be extracted is similar to:
#   gptest-1.0.0-cyg-venv/scripts/install-gp-venv.sh
extractInstallGpVenv() {
	echo "Extracting install-gp-venv.sh script to /tmp"
	# Does not appear that -C /tmp or --directory /tmp works
	#tar -xzvf $tmpTargzFilePath --wildcards '*/scripts/install-gp-venv.sh' -C /tmp; errorCode=$?
	set -x
	mkdir -p /tmp/$USER
	cd /tmp/$USER
	tar -xzvf $tmpTargzFilePath --wildcards '*/scripts/install-gp-venv.sh'; errorCode=$?
	{ set +x; } 2> /dev/null
	if [ $errorCode -ne 0 ]; then
		echo ""
		echo "[Error] Unable to extract install-gp-venv.sh script from $tmpTargzFilePath"
		exit 1
	fi
}

# Install the GeoProcessor venv to the final location
# - this moves to the indicated location and updates venv scripts to use that location
installVenv() {
	venvInstallFolder="$HOME/gptest-venv"
	echo ""
	echo "Installing the GeoProcesor virtual environment to user-specified folder."
	# The following is currently interactive
	# - need to add way to specify destination on command line
	# - install under user's home folder so it can be used in more than one project?
	# - or specific to a repo?
	cd "$scriptFolder"
	/tmp/$USER/gptest-$selectedInstallerVersion-$operatingSystemShort-venv/scripts/install-gp-venv.sh -i $tmpTargzFilePath
	if [ $? -ne 0 ]; then
		echo ""
		echo "[Error] Error installing GeoProcessor venv in final location"
		exit 1
	fi
}

# Prompt for the installer file to download
# - retrieve the catalog file from the public website to list installers
promptForInstaller() {
	# Retrieve the catalog file from the download website
	# - file contents look like:
	#   1 2018-12-27 01:16:36   58799278 geoprocessor/1.0.0/gptest-1.0.0-cyg-venv.tar.gz
	echo ""
	echo "Downloading the GeoProcessor catalog file..."
	#set -x
	curl --fail -o $tmpCatalogTxtPath $gpCatalogTxtUrl; errorCode=$?
	#{ set +x; } 2> /dev/null
	if [ $errorCode -ne 0 ]; then
		echo ""
		echo "[Error] Error downloading GeoProcessor product catalog file $gpCatalogTxtUrl."
		exit 1
	fi
	# Display the catalog, filtered by short operating system
	echo "-----------------------------------------------------------------------"
	echo "Select the GeoProcessor version to install from the following by specifying the line number:"
	tmpCatalogForOsTxtFile="gp-catalog-for-os.txt"
	tmpCatalogForOsTxtPath="/tmp/$USER-$tmpCatalogForOsTxtFile"
	cat $tmpCatalogTxtPath | grep $operatingSystemShort | awk 'BEGIN {line=0} { ++line; printf("%d %s\n",line,$0) }' > $tmpCatalogForOsTxtPath
	if [ ! -s "$tmpCatalogForOsTxtPath" ]; then
		# File does not exist or is zero length
		echo ""
		echo "No GeoProcessor installers are available for operating system.  Exiting."
		exit 1
	else
		echo ""
		cat $tmpCatalogForOsTxtPath
		echo ""
	fi
	read -p "Specify installer number (leftmost number) to install [q to quit]  " answer
	if [ -z "$answer" -o "$answer" = "q" -o "$answer" = "Q" ]; then
		# Quit
		echo "Exiting GeoProcessor download and installation."
		exit 0
	else
		# Figure out the installer from the line number
		# - first get the line number matching the requested
		# - then grab the column of interest, first squeezing multiple spaces into one
		installerLine=$(cat $tmpCatalogForOsTxtPath | grep "^$answer ")
		echo "installerLine=$installerLine"
		selectedInstallerVersion=$(echo $installerLine | tr -s ' ' | cut -d ' ' -f 5 | cut -d '/' -f 2)
		echo "selectedInstallerVersion=$selectedInstallerVersion"
		selectedInstallerFile=$(echo $installerLine | tr -s ' ' | cut -d ' ' -f 5 | cut -d '/' -f 3)
		echo "selectedInstallerFile=$selectedInstallerFile"
	fi
}

# Entry point into main script
# - functions are called below

# Check the operating system
# - necessary to branch logic for Cygdrive, Linux
checkOperatingSystem

# Check for required software needed to run this script
# - for example curl
checkRequiredSoftware

# Prompt user for GeoProcessor version to download
# - the catalog.txt file must have been uploaded to the download site
promptForInstaller

# Download the installer into /tmp
downloadInstaller

# Extract the install-gp-venv.sh script from the tar.gz file
# - this is the script that will install the tar.gz file to the final location
extractInstallGpVenv

# Unzip and move the Python venv to the desired install location
installVenv

# Exit with success status
exit 0
