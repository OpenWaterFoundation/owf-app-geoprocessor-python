#!/bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL
# 
# 2-create-gp-venv.sh
#
# Create the Python virtualenv installers for the GeoProcessor
# - Creates the virtualenv for cygwin gptest environment, others to be created later

# Supporting functions, alphabetized

# Check whether proper Cygwin packages are installed in development environment
# - some packages (e.g., python-devel) will only be used by pip during compiles, which use system include files and libraries
# - other packages (e.g., python-pyqt5) will be copied from the system Python to virtual environment by this script
checkCygwinDevEnv()
{	# First check for Cygwin install packages
	cygwinMissingPackageCount=0
	# There may be more requirements but installing major component like python-pyqt5
	# generally install needed dependencies.
	cygwinRequiredPackages="gcc-core gcc-fortran python3-devel libffi-devel libpq-devel openssl-devel python3-pip python3-pyqt5 python3-sip"
	echo "Checking that the Cygwin setup program installed:  $cygwinRequiredPackages"
	for requiredPackage in $cygwinRequiredPackages; do
		installedCount1=`cygcheck -c ${requiredPackage} | grep OK | wc -l`
		if [ "$installedCount1" -ne "1" ]; then
			${echo2} "${failColor}$requiredPackage does not appear to be installed as a Cygwin package.${endColor}"
			${echo2} "${failColor}Check by running the following (OK is needed):  cygcheck -c $requiredPackage${endColor}"
			${echo2} "${failColor}Install $requiredPackage using the Cygwin setup installer.${endColor}"
			${echo2} "${failColor}If the status is Incomplete, reinstall the software package in the Cygwin setup program.${endColor}"
			${echo2} "${failColor}See:  http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-dev/dev-env/dev-env/#cygwin${endColor}"
			cygwinMissingPackageCount=`expr $cygwinMissingPackageCount + 1`
		fi
	done
	# If any errors occurred exit here and fix
	if [ $cygwinMissingPackageCount -ne "0" ]; then
		${echo2} "${failColor}Required Cygwin packages are missing.  See above for information.${endColor}"
		exit 1
	fi

	# Also check for pip installed packages in system Python
	cygwinMissingPackageCount=0
	cygwinRequiredPackages="pip virtualenv"
	echo "Checking that system Python pip3 packages are installed:  $cygwinRequiredPackages"
	for requiredPackage in $cygwinRequiredPackages; do
		installedCount1=`pip3 list | grep $requiredPackage | wc -l`
		if [ "$installedCount1" -ne "1" ]; then
			${echo2} "${failColor}$requiredPackage does not appear to be installed as system pip3 package.${endColor}"
			${echo2} "${failColor}Install $requiredPackage using: pip3 install ${requiredPackage}${endColor}"
			${echo2} "${failColor}See:  http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-dev/dev-env/dev-env/#cygwin${endColor}"
			cygwinMissingPackageCount=`expr $cygwinMissingPackageCount + 1`
		fi
	done
	# If any errors occurred exit here and fix
	if [ $cygwinMissingPackageCount -ne "0" ]; then
		${echo2} "${failColor}Required pip3 packages are missing.  See above for information.${endColor}"
		exit 1
	fi
}

# Check whether proper Linux packages are installed in development environment
# - some packages (e.g., python-dev) will only be used by pip during compiles, which use system include files and libraries
# - other packages (e.g., python-pyqt5) will be copied from the system Python to virtual environment by this script
checkLinuxDevEnv()
{	# First check for Linux install packages
	linuxMissingPackageCount=0
	# There may be more requirements but installing major component like python-pyqt5
	# generally install needed dependencies.
	# - maybe need openssl or openssl-dev, but don't see the latter
	linuxRequiredPackages="gcc gfortran python3-dev libffi-dev libpq-dev python3-pandas python3-pip python3-pyqt5 python3-sip"
	for requiredPackage in $linuxRequiredPackages; do
		missingCount1=`dpkg-query -l $requiredPackage | grep 'no packages' | wc -l`
		if [ "$missingCount1" -ne "0" ]; then
			${echo2} "${failColor}$requiredPackage does not appear to be installed as an apt package.${endColor}"
			${echo2} "${failColor}Install $requiredPackage using:  sudo apt-get install ${requiredPackage}${endColor}"
			${echo2} "${failColor}See:  http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-dev/dev-env/dev-env/#linux${endColor}"
			linuxMissingPackageCount=`expr $linuxMissingPackageCount + 1`
		fi
	done
	# If any errors occurred exit here and fix
	if [ $linuxMissingPackageCount -ne "0" ]; then
		${echo2} "${failColor}Required Linux packages are missing.  See above for information.${endColor}"
		exit 1
	fi

	# Also check for pip installed packages in system Python
	linuxMissingPackageCount=0
	linuxRequiredPackages="pip virtualenv"
	echo "Checking that system Python pip3 packages are installed:  $linuxRequiredPackages"
	for requiredPackage in $linuxRequiredPackages; do
		installedCount1=`pip3 list | grep $requiredPackage | wc -l`
		if [ "$installedCount1" -ne "1" ]; then
			${echo2} "${failColor}$requiredPackage does not appear to be installed as system pip3 package.${endColor}"
			${echo2} "${failColor}Install $requiredPackage using: pip3 install ${requiredPackage}${endColor}"
			${echo2} "${failColor}See:  http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-dev/dev-env/dev-env/#linux${endColor}"
			linuxMissingPackageCount=`expr $linuxMissingPackageCount + 1`
		fi
	done
	# If any errors occurred exit here and fix
	if [ $linuxMissingPackageCount -ne "0" ]; then
		${echo2} "${failColor}Required pip3 packages are missing.  See above for information.${endColor}"
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

# Check whether Python3 is installed
checkPythonConfig() {
	# Make sure that python3 is found
	#--------------------------------
	output=`python3 -c 'print("python3 found")'`
	if [ "$output" != "python3 found" ]; then
		echo "python3 not found.  Make sure to install python3 in Cygwin.  Exiting."
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
		$echo2 "${failColor}Length ($lenFirstLine) of first line of ${pip3Script} is > 127 chars.  Exiting.${endColor}"
		$echo2 "May need to shorten path of development environment such as use GP instead of GeoProcessor."
		exit 1
	fi
}

# Copy GeoProcessor Python and other files for gptest
# - this is run when updating the virtual environment (-u option specified for this script)
# - files are copied from build-util/tmp* because these files are stripped of QGIS runtime references
copyGeoProcessorPackageToVenv () {
	# Top destination folder
	virtualEnvFolder="gptest-${version}-${operatingSystemShort}-venv"
	virtualEnvFolderPath="${virtualenvTmpFolder}/${virtualEnvFolder}"
	if [ ${operatingSystem} = "cygwin" ] || [ ${operatingSystem} = "linux" ]; then
		# Determine the specific site-packages destination folder to receive source geoprocessor folder
		# - on Debian Linux will be something like:  venv-tmp/gptest-1.1.0-lin-venv/lib/python3.4
		pythonLibWithVersion=`ls -1 ${virtualEnvFolderPath}/lib`
		pythonLibWithVersion=`basename ${pythonLibWithVersion}`
		sitepackagesFolder="${virtualEnvFolderPath}/lib/${pythonLibWithVersion}/site-packages"
		if [ ! -d "${sitepackagesFolder}" ]; then
			echo "Site packages folder ${sitepackagesFolder} does not exist.  Exiting."
			exit 1
		fi
		# Source files are in the build-tmp/... folder
		sourceGpFolder="${buildTmpFolder}/tmp-gptest-${version}/geoprocessor"
		echo "Copying source GeoProcessor Python files to virtual environment:"
		echo "  Source:  ${sourceGpFolder}"
		echo "  Destination:  ${sitepackagesFolder}"
		cp -rf ${sourceGpFolder} ${sitepackagesFolder}
		errorCode=$?
		if [ "$errorCode" -ne 0 ]; then
			echo ""
			echo "Error copying GeoProcessor folder ${sourceGpFolder}"
		fi
	else
		echo "[Error] operating system ${operatingSystem} is not supported for GeoProcessor copy."
		exit 1
	fi
}

# Copy original GeoProcessor source scripts into temporary virtual environment for gptest
# - OK to copy original because scripts work as is whether QGIS or not
# - this is run when the -u option is used with this script
copyGeoProcessorScriptsToVenv () {
	echo "Copying GeoProcessor scripts to virtual environment..."
	# Destination folder
	virtualEnvFolder="gptest-${version}-${operatingSystemShort}-venv"
	virtualEnvFolderPath="${virtualenvTmpFolder}/${virtualEnvFolder}"
	virtualEnvScriptsFolder="$virtualEnvFolderPath/scripts"
	echo "  Source:  ${repoFolder}/scripts"
	echo "  Destination:  ${virtualEnvScriptsFolder}"
	if [ ${operatingSystem} = "cygwin" ] || [ ${operatingSystem} = "linux" ]; then
		if [ ! -d "${virtualEnvScriptsFolder}" ]; then
			echo "Scripts folder ${virtualEnvScriptsFolder} does not exist.  Exiting."
			exit 1
		fi
		cp ${repoFolder}/scripts/gptest ${virtualEnvScriptsFolder}
		cp ${repoFolder}/scripts/gptestui ${virtualEnvScriptsFolder}
		cp ${buildUtilFolder}/install/install-gp-venv.sh ${virtualEnvScriptsFolder}
	else
		echo "[Error] operating system ${operatingSystem} is not supported for GeoProcessor copy."
		exit 1
	fi
}

# Create the Cygwin and Linux virtual environment for gptest
# - if updateBuildTmp="true", only copy *.py files to the existing venv
createGptestVirtualenvCygwinAndLinux() {
	echo "Creating virtualenv for gptest for Cygwin"
	# Check to make sure that the proper packages are installed in Cygwin
	if [ ${operatingSystem} = "cygwin" ]; then
		checkCygwinDevEnv
	elif [ ${operatingSystem} = "linux" ]; then
		checkLinuxDevEnv
	fi
	# First change to the folder in which to create the virtual environment
	echo "Changing to ${virtualenvTmpFolder}"
	cd ${virtualenvTmpFolder}
	virtualEnvFolder="gptest-${version}-${operatingSystemShort}-venv"
	virtualEnvFolderPath="${virtualenvTmpFolder}/${virtualEnvFolder}"
	# Remove the previous virtual environment for the GeoProcessor version
	if [ -d "${virtualEnvFolderPath}" ]; then
		echo "Removing existing ${virtualEnvFolderPath}"
		rm -rf ${virtualEnvFolderPath}
	fi
	# Create the virtualenv using the Cygwin python3
	echo "Creating virtualenv folder ${virtualEnvFolderPath}"
	#mkdir ${virtualEnvFolderPath}
	# --system-site-packages gives the virtual environment access to the global site-packages,
	# possibly necessary to install PyQt5 that was installed by Cygwin but is unavailable via pip
	# However, this is bad because it mixes the environments.
	# And, trying it gave an error on Cygwin with numpy, which stack overflow indicates is due to multiple
	# numpy installations, probably caused by --system-site-packages.
	# See:  https://virtualenv.pypa.io/en/stable/reference/#options
	# -v is verbose (use for troubleshooting temporarily but do not deploy)
	# -p specifies the Python to copy
	# Works on Cygwin and Linux
	echo "Creating virtual environment with: virtualenv -v -p /usr/bin/python3 ${virtualEnvFolderPath}"
	virtualenv -p /usr/bin/python3 ${virtualEnvFolderPath}
	# Activate the virtual environment, making it the active Python
	echo "Activating virtual environment with:  . ${virtualEnvFolderPath}/bin/activate"
	. ${virtualEnvFolderPath}/bin/activate
	# Check to make sure needed tools are installed
	# Need to upgrade the setuptools on Linux for some packages
	# - works ok on linux with the update
	if [ "${operatingSystem}" = "linux" ]; then
		pip3 install --upgrade setuptools
	fi
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
	pythonLibWithVersion=`ls -1 ${virtualEnvFolderPath}/lib`
	pythonLibWithVersion=`basename ${pythonLibWithVersion}`
	sitepackagesFolder="${virtualEnvFolderPath}/lib/${pythonLibWithVersion}/site-packages"
	if [ ! -d "${sitepackagesFolder}" ]; then
		echo "Site packages folder does not exist:  ${sitepackagesFolder}"
		echo "Aborting virtual environment setup."
		return
	fi
	echo "Changing directory to ${sitepackagesFolder}"
	cd "${sitepackagesFolder}"
	echo "Installing geoprocessor package files"
	tar -xzvf ${buildTmpFolder}/gptest-${version}-site-package.tar.gz
	# Install the necessary Python packages, alphabetically
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
	if [ "${operatingSystem}" = "cygwin" ]; then
		# Cygwin Python can install most packages with pip, but the following
		# must be installed in Cygwin via the setup program because no pip version.
		#	python3-pyqt5
		pipPackages='openpyxl pandas requests[security] SQLAlchemy xlwt'
	elif [ "${operatingSystem}" = "linux" ]; then
		# Linux Python can install most packages with pip, but the following
		# must be installed via apt-get because no pip version.
		#	apt-get install python3-pyqt5
		#	apt-get install python3-pandas
		pipPackages='openpyxl requests[security] SQLAlchemy xlwt'
	fi
	for pipPackage in $pipPackages; do
		echo "Installing package ${pipPackage}"
		# Possible options
		# --no-cache-dir - use if need to force new download for latest
		# --only-binary all
		# --prefer-binary (not available on linux version of python3)
		if [ "${operatingSystem}" = "linux" ]; then
			echo "------------------------------------------------------"
			echo "Running:  pip3 install $pipPackage"
			echo "------------------------------------------------------"
			pip3 install $pipPackage
		else
			# Cygwin and others
			echo "------------------------------------------------------"
			echo "Running:  pip3 install $pipPackage --prefer-binary"
			echo "------------------------------------------------------"
			pip3 install $pipPackage --prefer-binary
		fi
	done

	# Experience has shown that some packages are not available or involve long pip compile processes.
	# Therefore, the following are assumed to have been installed in the system Python.
	if [ "$operatingSystem" = "cygwin" ]; then
		# Manual copy of Cygwin-installed packages
		# PyQt5
		installedCount=`cygcheck -c python3-pyqt5 | grep OK | wc -l`
		if [ $installedCount -ne "1" ]; then
			${echo} "${warnColor}PyQt5 does not appear to be installed as a Cygwin package.${endColor}"
			${echo} "${warnColor}Install python3-pyqt5 from the Cygwin installer.${endColor}"
		else
			# Appears to be installed, but check the folder
			pyQt5Folder="/usr/lib/${pythonLibWithVersion}/site-packages/PyQt5"
			if [ ! -d "${pyQt5Folder}" ]; then
				${echo2} "${warnColor}PyQt5 does not appear to be installed in the Cygwin system Python3:  ${pyQt5Folder}${endColor}"
				${echo2} "${warnColor}Install python3-pyqt5 from the Cygwin installer.${endColor}"
			else
				echo "Copying Cygwin-installed ${pyQt5Folder} to site-packagses"
				cp -r ${pyQt5Folder} ${sitepackagesFolder}
			fi
		fi
		# SIP software
		installedCount=`cygcheck -c python3-sip | grep OK | wc -l`
		if [ $installedCount -ne "1" ]; then
			${echo2} "${warnColor}SIP does not appear to be installed as a Cygwin package.${endColor}"
			${echo2} "${warnColor}Install python3-sip from the Cygwin installer.${endColor}"
		else
			sipFile="/usr/lib/${pythonLibWithVersion}/site-packages/sipconfig.py"
			sipFolder="/usr/lib/${pythonLibWithVersion}/site-packages/sip*"
			if [ ! -f "${sipFile}" ]; then
				${echo2} "${warnColor}SIP does not appear to be installed in the Cygwin system Python3: ${sipFolder}${endColor}"
				${echo2} "${warnColor}Install python3-sip from the Cygwin installer.${endColor}"
			else
				echo "Copying Cygwin-installed sip* to site-packagses"
				cp ${sipFolder} ${sitepackagesFolder}
			fi
		fi
	elif [ "$operatingSystem" = "linux" ]; then
		# apt-get install python3-sip
		# apt-get install python3-pyqt5
		# apt-get install python3-pandas
		# See:  https://pandas.pydata.org/pandas-docs/stable/install.html
		#
		# Pandas also installs the following on Debian Jessie 64-bit, which indicate folders to copy...
		# Get:1 http://ftp.us.debian.org/debian/ jessie/main libhdf5-8 amd64 1.8.13+docs-15+deb8u1 [1,061 kB]
		# Get:2 http://ftp.us.debian.org/debian/ jessie/main libtcl8.6 amd64 8.6.2+dfsg-2 [978 kB]
		# Get:3 http://ftp.us.debian.org/debian/ jessie/main libtk8.6 amd64 8.6.2-1 [771 kB]
		# Get:4 http://ftp.us.debian.org/debian/ jessie/main liblz4-1 amd64 0.0~r122-2 [17.0 kB]
		# Get:5 http://ftp.us.debian.org/debian/ jessie/main tk8.6-blt2.5 amd64 2.5.3+dfsg-1 [586 kB]
		# Get:6 http://ftp.us.debian.org/debian/ jessie/main blt amd64 2.5.3+dfsg-1 [14.3 kB]
		# Get:7 http://ftp.us.debian.org/debian/ jessie/main fonts-lyx all 2.1.2-2 [176 kB]
		# Get:8 http://ftp.us.debian.org/debian/ jessie/main libjs-jquery-ui all 1.10.1+dfsg-1 [499 kB]
		# Get:9 http://ftp.us.debian.org/debian/ jessie/main python-matplotlib-data all 1.4.2-3.1 [3,041 kB]
		# Get:10 http://ftp.us.debian.org/debian/ jessie/main python-tables-data all 3.1.1-3 [48.5 kB]
		# Get:11 http://ftp.us.debian.org/debian/ jessie/main python3-bs4 all 4.3.2-2 [77.6 kB]
		# Get:12 http://ftp.us.debian.org/debian/ jessie/main python3-dateutil all 2.2-2 [33.2 kB]
		# Get:13 http://ftp.us.debian.org/debian/ jessie/main python3-decorator all 3.4.0-2 [22.5 kB]
		# Get:14 http://ftp.us.debian.org/debian/ jessie/main python3-lxml amd64 3.4.0-1 [742 kB]
		# Get:15 http://ftp.us.debian.org/debian/ jessie/main python3-pyparsing all 2.0.3+dfsg1-1 [64.1 kB]
		# Get:16 http://ftp.us.debian.org/debian/ jessie/main python3-tz all 2012c+dfsg-0.1 [25.4 kB]
		# Get:17 http://ftp.us.debian.org/debian/ jessie/main python3-numpy amd64 1:1.8.2-2 [1,628 kB]
		# Get:18 http://ftp.us.debian.org/debian/ jessie/main python3-nose all 1.3.4-1 [131 kB]
		# Get:19 http://ftp.us.debian.org/debian/ jessie/main python3-matplotlib amd64 1.4.2-3.1 [3,743 kB]
		# Get:20 http://ftp.us.debian.org/debian/ jessie/main python3-numexpr amd64 2.4-1 [129 kB]
		# Get:21 http://ftp.us.debian.org/debian/ jessie/main python3-pandas-lib amd64 0.14.1-2 [1,273 kB]
		# Get:22 http://ftp.us.debian.org/debian/ jessie/main python3-pandas all 0.14.1-2 [1,249 kB]
		# Get:23 http://ftp.us.debian.org/debian/ jessie/main python3-pil amd64 2.6.1-2+deb8u3 [304 kB]
		# Get:24 http://ftp.us.debian.org/debian/ jessie/main libsnappy1 amd64 1.1.2-3 [40.4 kB]
		# Get:25 http://ftp.us.debian.org/debian/ jessie/main python3-tables-lib amd64 3.1.1-3+b1 [341 kB]
		# Get:26 http://ftp.us.debian.org/debian/ jessie/main python3-tables all 3.1.1-3 [329 kB]
		# Get:27 http://ftp.us.debian.org/debian/ jessie/main python3-tk amd64 3.4.2-1+b1 [25.2 kB]
		# Get:28 http://ftp.us.debian.org/debian/ jessie/main python3-scipy amd64 0.14.0-2 [7,771 kB]
		#
		# Debian uses dist-packages instead of site-packages and seems to install into
		# /usr/lib/python3, not, for example /usr/lib/python3.4
		# pandas and dependencies
		installedCount=`dpkg-query -l python3-pandas | grep -v 'no packages' | wc -l`
		if [ $installedCount -eq "1" ]; then
			${echo2} "${warnColor}Pandas does not appear to be installed as an apt-get package.${endColor}"
			${echo2} "${warnColor}Install python3-pandas using:  sudo apt-get install python3-pandas.${endColor}"
		else
			echo "Copying apt-get-installed /usr/lib/python3/dist-packages/pandas (and related) to ${sitepackagesFolder}"
			#cp -r /usr/lib/python3/dist-packages/blt ${sitepackagesFolder}
			cp -r /usr/lib/python3/dist-packages/bs4 ${sitepackagesFolder}
			cp -r /usr/lib/python3/dist-packages/dateutil ${sitepackagesFolder}
			cp -r /usr/lib/python3/dist-packages/decorator.py ${sitepackagesFolder}
			#cp -r /usr/lib/python3/dist-packages/fonts-lyx ${sitepackagesFolder}
			#cp -r /usr/lib/python3/dist-packages/libjs-jquery-ui ${sitepackagesFolder}
			#cp -r /usr/lib/python3/dist-packages/libhdf5-8 ${sitepackagesFolder}
			#cp -r /usr/lib/python3/dist-packages/libtcl8.6 ${sitepackagesFolder}
			#cp -r /usr/lib/python3/dist-packages/libtk8.6 ${sitepackagesFolder}
			#cp -r /usr/lib/python3/dist-packages/libtk8.6-blt2.5 ${sitepackagesFolder}
			#cp -r /usr/lib/python3/dist-packages/liblz4-1 ${sitepackagesFolder}
			#cp -r /usr/lib/python3/dist-packages/libsnappy1 ${sitepackagesFolder}
			cp -r /usr/lib/python3/dist-packages/lxml ${sitepackagesFolder}
			cp -r /usr/lib/python3/dist-packages/matplotlib ${sitepackagesFolder}
			cp -r /usr/lib/python3/dist-packages/mpl_toolkits ${sitepackagesFolder}
			cp -r /usr/lib/python3/dist-packages/nose ${sitepackagesFolder}
			cp -r /usr/lib/python3/dist-packages/numexpr ${sitepackagesFolder}
			cp -r /usr/lib/python3/dist-packages/numpy ${sitepackagesFolder}
			cp -r /usr/lib/python3/dist-packages/pandas ${sitepackagesFolder}
			#cp -r /usr/lib/python3/dist-packages/pandas-lib ${sitepackagesFolder}
			#cp -r /usr/lib/python3/dist-packages/pyparsing ${sitepackagesFolder}
			#cp -r /usr/lib/python3/dist-packages/python-matplotlib-data ${sitepackagesFolder}
			# From pandas-pil?
			cp -r /usr/lib/python3/dist-packages/PIL ${sitepackagesFolder}
			#cp -r /usr/lib/python3/dist-packages/python-tables ${sitepackagesFolder}
			cp -r /usr/lib/python3/dist-packages/scipy ${sitepackagesFolder}
			cp -r /usr/lib/python3/dist-packages/tables ${sitepackagesFolder}
			#cp -r /usr/lib/python3/dist-packages/tables-lib ${sitepackagesFolder}
			#cp -r /usr/lib/python3/dist-packages/tk ${sitepackagesFolder}
			cp -r /usr/lib/python3/dist-packages/pytz ${sitepackagesFolder}
		fi
		# PyQt5
		# TODO smalers 2018-11-25 make the following work on Linux for apt-get installs
		installedCount=`dpkg-query -l python3-pyqt5 | grep -v 'no packages' | wc -l`
		if [ $installedCount -eq "1" ]; then
			${echo2} "${warnColor}PyQt5 does not appear to be installed as an apt-get package.${endColor}"
			${echo2} "${warnColor}Install python3-pyqt5 using:  sudo apt-get install python3-pyqt5.${endColor}"
		else
			pyQt5Folder="/usr/lib/python3/dist-packages/PyQt5"
			if [ ! -d "${pyQt5Folder}" ]; then
				${echo2} "${warnColor}PyQt5 does not appear to be installed in the system Python3:  ${pyQt5Folder}${endColor}"
				${echo2} "${warnColor}Install with:  sudo apt-get install python3-pyqt5.${endColor}"
			else
				echo "Copying apt-get-installed /usr/lib/python3/dist-packages/PyQt5 to ${sitepackagesFolder}"
				cp -r ${pyQt5Folder} ${sitepackagesFolder}
			fi
		fi
		# sip
		installedCount=`dpkg-query -l python3-sip | grep -v 'no packages' | wc -l`
		if [ $installedCount -eq "1" ]; then
			${echo2} "${warnColor}SIP does not appear to be installed as a Linux package.${endColor}"
			${echo2} "${warnColor}Install python3-sip using:  sudo apt-get install python3-sip.${endColor}"
		else
			sipFile="/usr/lib/python3/dist-packages/sipconfig.py"
			sipFolder="/usr/lib/python3/dist-packages/sip*"
			if [ ! -f "${sipFile}" ]; then
				${echo2} "${warnColor}SIP does not appear to be installed in the system Python3 folder.${endColor}"
				${echo2} "${warnColor}Install python3-sip using:  sudo apt-get install python3-sip.${endColor}"
			else
				echo "Copying apt-get-installed ${sipFolder} to ${sitepackagesFolder}"
				cp ${sipFolder} ${sitepackagesFolder}
			fi
		fi
	else
		${echo2} "${warnColor}[Error] operating system ${operatingSystem} is not supported for package copy.${endColor}"
	fi

	# Copy GeoProcessor scripts for gptest
	if [ ${operatingSystem} = "cygwin" ] || [ ${operatingSystem} = "linux" ]; then
		virtualenvScriptsFolder="${virtualEnvFolderPath}/scripts"
		mkdir ${virtualenvScriptsFolder}
		buildTmpGptestFolder="${buildTmpFolder}/tmp-gptest-${version}"
		cp ${buildTmpGptestFolder}/scripts/gptest ${virtualenvScriptsFolder}
		cp ${buildTmpGptestFolder}/scripts/gptestui ${virtualenvScriptsFolder}
		cp ${buildTmpGptestFolder}/scripts/install-gp-venv.sh ${virtualenvScriptsFolder}
	else
		echo "[Error] operating system ${operatingSystem} is not supported for GeoProcessor copy."
	fi

	# Finally, create a tar file of the virtual environment, for distribution to deployed user environment
	echo "--------------------------------------------------------"
	echo "Creating tar.gz file for virtual environment"
	echo "--------------------------------------------------------"
	echo "Changing to ${virtualenvTmpFolder}"
	cd ${virtualenvTmpFolder}
	gptestTargzFile="gptest-${version}-${operatingSystemShort}-venv.tar.gz"
	echo "Creating file to distribute virtual environment:  ${gptestTargzFile}"
	virtualenvFolderBasename=`basename ${virtualEnvFolderPath}`
	tar -czvf ${gptestTargzFile} ${virtualenvFolderBasename}
}

# Parse the command parameters
parseCommandLine() {
	local OPTIND opt h u v
	optstring=":huv"
	while getopts $optstring opt; do
		#echo "Command line option is ${opt}"
		case $opt in
			h) # -h  Print the usage
				printUsage
				exit 0
				;;
			u) # -u  Update the build-tmp folder with *.py files
				updateBuildTmp="true"
				;;
			v) # version
				printVersion
				exit 0
				;;
			\?)
				echo ""
				echo "Invalid option:  -$OPTARG" >&2
				printUsage
				exit 1
				;;
			:)
				echo ""
				echo "Option -$OPTARG requires an argument" >&2
				printUsage
				exit 1
				;;
		esac
	done
}

# Print the script usage
printUsage() {
	echo ""
	echo "Usage:  2-create-gp-venv.sh [options]"
	echo ""
	echo "Create/update a Python virtual environment."
	echo ""
	echo "Example to do full virtual environment creation:"
	echo '  2-create-gp-env.sh'
	echo ""
	echo "Example to update virtual environment with latest GeoProcessor *.py and scripts:"
	echo '  2-create-gp-env.sh -u'
	echo ""
	echo "-u  Copy the GeoProcessor *.py and scripts to existing virtual environment."
	echo "-h  Print the usage."
	echo "-v  Print the version."
	echo ""
}

# Print the program version
printVersion() {
	echo ""
	echo "2-create-gp-venv.sh version ${programVersion} ${programVersionDate}"
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
	boldColor='\e[0;01m' # warning - user needs to do something, 01=bold
	warnColor='\e[0;40;33m' # warning - user needs to do something, 40=background black, 33=yellow
	criticalColor='\e[0;40;31m' # critical issue - could be fatal, 40=background black, 31=red
	failColor="$criticalColor" # because it is easy to forget these color names
	okColor='\e[0;40;32m' # status is good, 40=background black, 32=green
	endColor='\e[0m' # To switch back to default color
}

# Entry point into script

programVersion="1.3.0"
programVersionDate="2019-01-03"

# Initialize variables
# - QGIS Python version is set by checkQgisPythonVersion
qgisPythonVersion="unknown"
qgisPythonFolder="unknown"
# - Operating system python version is set by checkOperatingSystemPythonVersion
osPythonVersion="unknown"
osPythonFolder="unknown"
# Echo command is the default but check below with setupEcho function
echo2="echo"
# Default is to do full venv creation (-u will set to "true)
updateBuildTmp="false"

# Setup the echo command for color text output
setupEcho

#------------------------------------------------------------------------------------------
# Step 0. Setup.
# Get the location where this script is located since it may have been run from any folder
scriptFolder=`cd $(dirname "$0") && pwd`

# Parse the command line
parseCommandLine "$@"

# Check the operating system
checkOperatingSystem

# Check the QGIS and operating system Python versions
# - to help ensure compatibility in testing and deployed versions
checkQgisPythonVersion
checkOperatingSystemPythonVersion

if [ "$updateBuildTmp" = true ]; then
	echo ""
	echo "Updating GeoProcessor virtual environment by copying files (-u command option detected)..."
else
	echo ""
	echo "Creating GeoProcessor virtual environment (no -u command option detected)..."
fi

# Define top-level folders - everything is relative to this below to avoid confusion
buildUtilFolder=${scriptFolder}
repoFolder=`dirname ${buildUtilFolder}`
buildTmpFolder="${buildUtilFolder}/build-tmp"
# Name of the parent folder for virtual environments
# - the following is apparently too long - sh-bang lines have limit of 127 characters
#   virtualenvTmpFolder="${buildUtilFolder}/virtualenv-tmp"
# - if this does not work, shorten the development environment folder from GeoProcessor to GP
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
if [ ${operatingSystem} = "cygwin" -o ${operatingSystem} = "linux" ]; then
	echo "Detected operating system $operatingSystem"
	if [ "$updateBuildTmp" = "true" ]; then
		# This copies original source into the virtual environment
		echo "Copying GeoProcessor Python source package files and scripts to venv"
		copyGeoProcessorPackageToVenv
		copyGeoProcessorScriptsToVenv
	else
		# This uses files in the build-tmp copy of the GeoProcessor (tar.gz)
		# TODO smalers 2018-12-28 Need to also build venv for full gp distribution
		# - add another command line option
		echo "Creating gptest virtual environment for $operatingSystem"
		createGptestVirtualenvCygwinAndLinux
	fi
else
	echo "Unsupported operating system ${operatingSystem}.  Exiting."
	exit 1
fi

errorOccurred="no"

#------------------------------------------------------------------------------------------
# Final comment to software developer

if [ "${errorOccurred}" = "yes" ]
	then
	${echo2} ""
	${echo2} "A warning or failure error occurred creating the virtual environment.  Check messages above."
	${echo2} "- Partial results may have been created, such as tar.gz but not .zip"
	${echo2} "- Maybe need to use another shell (Cygwin, Git Bash, Windows Bash, Linux)."
	${echo2} "- Sometimes Cygwin processes die so just rerun."
	${echo2} ""
fi

# Print information useful after this script is run.

if [ "$updateBuildTmp]" = "false" ]; then
	# The Python virtual environment was created
	echo ""
	echo "Python virtual environment(s) were created in venv-tmp folder:"
	echo ""
	echo "  ${virtualEnvFolderPath}"
	echo ""
	echo "Next steps are to do one or more of the following:"
	echo "- Run the software locally in the venv before deploying by running scripts in:  "
	echo "  ${virtualEnvFolderPath}/scripts"
	echo "- If source is modified, run build-util/2-update-gp-venv.sh to update above venv files."
	echo "- Run build-util/install/install-gp.sh to install from tar.gz file to test venv before deploying."
	echo "- Run build-util/3-copy-gp-to-amazon-s3.sh to deploy the installer to OWF Amazon S3 site."
	echo "  Then download, install, and test in the deployed venv by running scripts."
	echo ""
else
	# The Python virtual environment was updated
	echo ""
	echo "Python virtual environment(s) was updated in venv-tmp folder:"
	echo ""
	echo "  ${virtualEnvFolderPath}"
	echo ""
	echo "Next steps are to do one or more of the following:"
	echo "- Run the software locally in the venv before deploying by running scripts in:  "
	echo "  ${virtualEnvFolderPath}/scripts"
	echo "- If source is modified, run build-util/2-update-gp-venv.sh again to update above venv files."
	echo "- Run build-util/install/install-gp.sh to install from tar.gz file to test venv before deploying."
	echo "- Run build-util/3-copy-gp-to-amazon-s3.sh to deploy the installer to OWF Amazon S3 site."
	echo "  Then download, install, and test in the deployed venv by running scripts."
	echo ""
	${echo2} "${boldColor}It is recommended to run build-util/2-create-gp-venv.sh to do a clean create before deployment.${endColor}"
	echo ""
fi

if [ ! "$qgisPythonVersion" = "osPythonVersion" ]; then
	$echo2 "${warnColor}- QGIS Python version $qgisPythonVersion is different than venv version ${osPythonVersion}.${endColor}"
	$echo2 "${warnColor}  - May be OK if close enough but may need to take action to create a compatible virtual environment.${endColor}"
	$echo2 "${warnColor}  - Use automated testing to validate the venv Python version.${endColor}"
	$echo2 "${warnColor}  - QGIS Python folder is $qgisPythonFolder${endColor}"
fi

# Exit with appropriate error status
if [ "${errorOccurred}" = "yes" ]
	then
	exit 1
else
	exit 0
fi
