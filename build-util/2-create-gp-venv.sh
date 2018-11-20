#!/bin/bash
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL
# 
# 2-create-gp-venv.sh
#
# Create the Python virtualenv installers for the GeoProcessor
# - Creates the virtualenv for cygwin gptest environment, others to be created later

# Supporting functions

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
			operatingSystem="min"
			operatingSystemShort="min"
			;;
	esac
	echo "Detected operatingSystem=$operatingSystem"
}

# Check whether Python3 is installed
checkPythonConfig() {
	# Make sure that python3 is found
	#--------------------------------
	output=`python3 -c 'print("python3 found")'`
	if [ "$output" != "python3 found" ]; then
		echo "python3 not found.  Make sure to instally python3 in Cygwin.  Exiting."
		exit 1
	fi
	# Make sure it is a Cygwin/Linux version
	output=`which python3`
	if [ "$output" != "/usr/bin/python3" ]; then
		echo "/usr/bin/python3 not found.  Make sure to install python3 in Cygwin.  Exiting."
		exit 1
	else
		echo "python3 found in expected location /usr/bin/python3"
	fi
	# Make sure that pip3 is found and is the right version
	# -----------------------------------------------------
	output=`which pip3`
	if [ "$output" != "/usr/bin/pip3" ]; then
		echo "/usr/bin/pip3 not found.  Make sure to run 'python3 -m ensurepip' as Administrator in Cygwin.  Exiting."
		exit 1
	else
		echo "pip3 found in expected location /usr/bin/pip3"
	fi
	# Make sure that virtualenv is found and is the right version
	# -----------------------------------------------------------
	output=`which virtualenv`
	if [ "$output" != "/usr/bin/virtualenv" ]; then
		echo "/usr/bin/virtualenv not found.  Make sure to run 'pip3 install virtualenv' as Administrator in Cygwin.  Exiting."
		exit 1
	else
		echo "virtualenv found in expected location /usr/bin/virtualenv"
	fi
}

# Check that the Python configuration in the virtual environment is good.
# - Script first lines must be < 128 characters
checkVenvPythonConfig () {
	# Check that the shbang #! line of the python scripts are not too long
	# - generally cannot be longer than 127 characters
	# - see: https://stackoverflow.com/questions/10813538/shebang-line-limit-in-bash-and-linux-kernel
	# - depends on scriptPath being set
	pip3Script="${VIRTUAL_ENV}/bin/pip3"
	lenFirstLine=`head -n1 "${pip3Script}" | wc -c`
	if [ "$lenFirstLine" -gt 127 ]; then
		echo "Length ($lenFirstLine) of first line of ${pip3Script} is > 127 chars.  Exiting."
		exit 1
	fi
}

# Create the Cygwin virtual environment for gptest
createGptestVirtualenvCygwin() {
	echo "Creating virtualenv for gptest for Cygwin"
	# First change to the folder in which to create the virtual environment
	echo "Changing to ${virtualenvTmpFolder}"
	cd ${virtualenvTmpFolder}
	virtualEnvFolder="gptest-${version}-${operatingSystemShort}-venv"
	virtualenvFolderPath="${virtualenvTmpFolder}/${virtualEnvFolder}"
	# Remove the previous virtual environment for the GeoProcessor version
	if [ -d "${virtualenvFolderPath}" ]; then
		echo "Removing existing ${virtualenvFolderPath}"
		rm -rf ${virtualenvFolderPath}
	fi
	# Create the virtualenv using the Cygwin python3
	echo "Creating virtualenv folder ${virtualenvFolderPath}"
	mkdir ${virtualenvFolderPath}
	# --system-site-packages gives the virtual environment access to the global site-packages,
	# possibly necessary to install PyQt5 that was installed by Cygwin but is unavailable via pip
	# However, this is bad because it mixes the environments.
	# And, trying it gave an error on Cygwin with numpy, which stack overflow indicates is due to multiple
	# numpy installations, probably caused by --system-site-packages.
	# See:  https://virtualenv.pypa.io/en/stable/reference/#options
	# -v is verbose
	# -p specifies the Python to copy
	if [ "${operatingSystem}" = "linux" ]; then
		# Try the following without the leading path to Python because
		# behavior seemed to not be correct
		echo "Creating virtual environment with: virtualenv -v -p python3 ${virtualenvFolderPath}"
		virtualenv -v -p python3 ${virtualenvFolderPath}
	else
		# The following worked for Cygwin but maybe should not use path?
		echo "Creating virtual environment with: virtualenv -v -p /usr/bin/python3 ${virtualenvFolderPath}"
		virtualenv -v -p /usr/bin/python3 ${virtualenvFolderPath}
	fi
	# Activate the virtual environment, making it the active Python
	echo "Activating virtual environment with:  . ${virtualenvFolderPath}/bin/activate"
	. ${virtualenvFolderPath}/bin/activate
	# Print the following to verify that activation took effect
	echo "VIRTUAL_ENV=$VIRTUAL_ENV"
	echo "Running which python3 to confirm virtualenv activation"
	which python3
	echo "Running which pip3 to confirm virtualenv activation"
	which pip3
	echo "Running which pip to confirm virtualenv activation"
	which pip
	# Further check the Python configuration
	checkVenvPythonConfig
	# Install the GeoProcessor files created by the create-gp-installer.sh script.
	# - should be something like lib/python3.6/site-packages
	pythonLibWithVersion=`ls -1 ${virtualenvFolderPath}/lib`
	pythonLibWithVersion=`basename ${pythonLibWithVersion}`
	sitepackagesFolder="${virtualenvFolderPath}/lib/${pythonLibWithVersion}/site-packages"
	if [ ! -d "${sitepackagesFolder}" ]; then
		echo "Site packages folder does not exist:  ${sitepackagesFolder}"
		echo "Aborting virtual environment setup."
		return
	fi
	echo "Changing directory to ${sitepackagesFolder}"
	cd "${sitepackagesFolder}"
	echo "Installing geoprocessor package files"
	tar -xzvf ${buildTmpFolder}/gptest-${version}-site-package.tar.gz
	# Copy the GeoProcessor scripts
	# Install the necessary Python packages, alphabetically except for python-dev
	# openpyxl - read/write Excel files
	# pandas - statistics
	# psycopg2-binary - PostegreSQL driver    (binary is needed because otherwise will try to compile the install)
	# pyqt5 - Qt5 UI components
	# requests[security] - http library
	# SQLAlchemy - SQL database toolkit
	# xlwt - create Excel spreadsheet files
	echo "Installing required Python packages using pip"
	# Full list
	#pipPackages='openpyxl pandas PyQt5 requests[security] SQLAlchemy xlwt'
	# Leave out PyQt5 because could not find a pip version that compiled/installed
	if [ "${operatingSystem}" = "cygwin" ]; then
		pipPackages='openpyxl pandas requests[security] SQLAlchemy xlwt'
	elif [ "${operatingSystem}" = "linux" ]; then
		# Leave out pandas for now until troubleshoot
		pipPackages='openpyxl requests[security] SQLAlchemy xlwt'
	fi
	for pipPackage in $pipPackages; do
		echo "Installing package ${pipPackage}"
		# Possible options
		# --no-cache-dir - use if need to force new download for latest
		# --only-binary all
		# --prefer-binary (not available on linux version of python3)
		if [ "${operatingSystem}" = "linux" ]; then
			echo "Running:  pip3 install $pipPackage"
			pip3 install $pipPackage
		else
			echo "Running:  pip3 install $pipPackage --prefer-binary"
			pip3 install $pipPackage --prefer-binary
		fi
	done
	# Manual copy of Cygwin-installed packages
	if [ "$operatingSystem" = "linux" ]; then
		echo "[ERROR] Linux install of PyQt5 and sep not yet implemented"
	else
		# Windows variant such as Cygwin
		echo "Copying Cygwin-installed /usr/lib/${pythonLibWithVersion}/site-packages/PyQt5 to site-packagses"
		cp -r /usr/lib/${pythonLibWithVersion}/site-packages/PyQt5 ${sitepackagesFolder}
		echo "Copying Cygwin-installed /usr/lib/${pythonLibWithVersion}/site-packages/sip* to site-packagses"
		cp /usr/lib/${pythonLibWithVersion}/site-packages/sip* ${sitepackagesFolder}
	fi

	# Copy scripts
	virtualenvScriptsFolder="${virtualenvFolderPath}/scripts"
	mkdir ${virtualenvScriptsFolder}
	buildTmpGptestFolder="${buildTmpFolder}/tmp-gptest-${version}"
	cp ${buildTmpGptestFolder}/scripts/gptest ${virtualenvScriptsFolder}
	cp ${buildTmpGptestFolder}/scripts/gptestui ${virtualenvScriptsFolder}
}

# Entry point into script

#------------------------------------------------------------------------------------------
# Step 0. Setup.
# Get the location where this script is located since it may have been run from any folder
scriptFolder=`cd $(dirname "$0") && pwd`

# Check the operating system
checkOperatingSystem

# Define top-level folders - everything is relative to this below to avoid confusion
buildUtilFolder=${scriptFolder}
repoFolder=`dirname ${buildUtilFolder}`
buildTmpFolder="${buildUtilFolder}/build-tmp"
#virtualenvTmpFolder="${buildUtilFolder}/virtualenv-tmp"
virtualenvTmpFolder="${buildUtilFolder}/venv-tmp"
# Get the software version number
versionFile="${repoFolder}/geoprocessor/app/version.py"
version=`cat ${versionFile} | grep app_version -m 1 | cut -d '=' -f 2 | tr -d " " | tr -d '"'`

# Echo information 
echo "Project (main) folder is ${repoFolder}"
echo "build-util folder is ${buildUtilFolder}"
echo "build-tmp folder is ${buildTmpFolder}"
echo "virtualenv-tmp folder is ${virtualenvTmpFolder}"
echo "GeoProcessor version (from ${versionFile}) is ${version}"

# Check to see if folders exist.  If not, something is probably wrong so don't continue.
if [ ! -d ${repoFolder} ]
	then
	echo "Something is wrong.  Repository folder does not exist:  ${repoFolder}"
	exit 1
fi
if [ ! -d ${buildUtilFolder} ]
	then
	echo "Something is wrong.  build-util folder does not exist:  ${buildUtilFolder}"
	exit 1
fi
if [ ! -d ${buildTmpFolder} ]
	then
	echo "Something is wrong.  build-tmp folder does not exist:  ${buildTmpFolder}"
	exit 1
fi
if [ ! -d ${virtualenvTmpFolder} ]
	then
	echo "Something is wrong.  virtualenv-tmp folder does not exist:  ${virtualenvTmpFolder}"
	exit 1
fi

# Check that needed software is available, will exit if a problem
checkPythonConfig

# Create the virtual environment for Cygwin
createGptestVirtualenvCygwin

errorOccurred="no"

#------------------------------------------------------------------------------------------
# Final comment to software developer

if [ "${errorOccurred}" = "yes" ]
	then
	echo ""
	echo "An error occurred creating the virtual environment.  Check messages above."
	echo "- Partial results may have been created, such as tar.gz but not .zip"
	echo "- Maybe need to use another shell (Cygwin, Git Bash, Windows Bash, Linux)."
	echo "- Sometimes Cygwin drops processes so just rerun."
	echo ""
fi

echo ""
echo "Python virtual environments  were created in virtualenv-tmp folder"
echo ""

# Exit with appropriate error status
if [ "${errorOccurred}" = "yes" ]
	then
	exit 1
else
	exit 0
fi
