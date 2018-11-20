#!/bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL
#
# install-gp-cygwin
#
# Install the GeoProcessor software on cygwin
# - Currently this works from the development environment only, to facilitate development and testing

scriptFolder=`cd $(dirname "$0") && pwd`
echo "scriptFilder=${scriptFolder}"

# Supporting functions

# Determine the operating system that is running the script
# - mainly care whether Cygwin
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

# Check whether running with the correct permissiosn
checkPermissions () {
	if [ "${operatingSystem}" = "cygwin" ]; then
		# Need to run as SystemAdmin
		if [ "$USER" != "SystemAdmin" ]; then
			echo ""
			echo "Need to run a Cygwin terminal as Administrator to install."
			echo ""
			exit 1
		fi
	fi
}

# Install a zip file of the GeoProcessor
# - first in stall the Python packages in the site-packages folder
# - then install the third-party packages
install () {
	targzFile=$1
	echo "Installing ${targzFile}"
	while [ "1" = "1" ]; do
		# Determine where the Python is installed for cygwin
		echo "Available Python 3:"
		echo ""
		ls -1 /usr/lib | grep python3 | awk '{printf("/usr/lib/%s\n",$0)}'
		echo ""
		read -p "Specify the Python 3 path to use as shown (q to quit):  " pythonUsrLibFolder
		if [ "${pythonUsrLibFolder}" = "q" ]; then
			exit 0
		else
			# Install into the provided Python 3
			echo "Selected Python installation folder ${pythonUsrLibFolder}"
			pythonSitePackagesFolder="${pythonUsrLibFolder}/site-packages"
			if [ ! -d "${pythonSitePackagesFolder}" ]; then
				echo ""
				echo "Python site-packages folder does not exist:  ${pythonSitePackagesFolder}"
				return
			else
				# Change to the site-packages folder
				cd ${pythonSitePackagesFolder}
				# Remove the old installed files
				echo "Changing to ${pythonSitePackagesFolder}"
				echo "Removing old geoprocessor package folder"
				rm -rf geoprocessor
				targzFileAbs=${buildFolder}/${targzFile}
				echo "Installing geoprocessor file from ${targzFileAbs}"
				tar -xzvf ${targzFileAbs}
				break
			fi
		fi
	done
	# Install the dependencies
	installDependencies()
	# Install scripts
	installScripts()
}

# Install additional dependencies needed by the GeoProcessor
installDependencies() {
	# If here, the geoprocessor module was installed.
	# Also install required third-party packages
	pipPackages=pandas openpyxl requests[security] SQLAlchemy
}

# Install the scripts for the GeoProcessor
# - install in /usr/bin since they will be used by all users
installScripts() {
	while [ "1" = "1" ]; do
		# Determine where the Python is installed for cygwin
		echo "The following scripts will be installed into /usr/bin:"
		echo ""
		echo "   gp -> /usr/bin/gp"
		echo "   gpui -> /usr/bin/gpui"
		echo "   gptest -> /usr/bin/gptest"
		echo "   gptestui -> /usr/bin/gptestui"
		echo ""
		read -p "Continue with install? (y or n):  " answer
		if [ "${answer}" = "q" ]; then
			return
		else
			# Copy the files
			cp ${repoFolder}/scripts/gp /usr/bin/gp
			cp ${repoFolder}/scripts/gpui /usr/bin/gpui
			cp ${repoFolder}/scripts/gptest /usr/bin/gptest
			cp ${repoFolder}/scripts/gptestui /usr/bin/gptestui
			if [ ${operatingSystem} = "cygwin" ]; then
				# Set the user consistent with Cygwin conventions
				chown SystemAdmin /usr/bin/gp
				chown SystemAdmin /usr/bin/gpui
				chown SystemAdmin /usr/bin/gptest
				chown SystemAdmin /usr/bin/gptestui
				# Set the group consistent with Cygwin conventions
				chgrp None /usr/bin/gp
				chgrp None /usr/bin/gpui
				chgrp None /usr/bin/gptest
				chgrp None /usr/bin/gptestui
				# Make sure executable for all
				chmod a+x /usr/bin/gp
				chgrp a+x /usr/bin/gpui
				chgrp a+x /usr/bin/gptest
				chgrp a+x /usr/bin/gptestui
			elif [ ${operatingSystem} = "linux" ]; then
				echo "linux is not yet supported"
			elif [ ${operatingSystem} = "mingw" ]; then
				echo "mingw (Git Bash) is not yet supported"
			fi
		fi
	done
}

# Check whether running with correct permissions
checkOperatingSystem
checkPermissions

# Define top-level folders - everything is relative to this below to avoid confusion
repoFolder=`dirname ${scriptFolder}`
buildUtilFolder="${scriptFolder}"
buildFolder="${repoFolder}/build"

# Change to the build folder.
cd ${buildFolder}

while [ "1" = "1" ]; do
	# List available files
	echo ""
	echo "Available GeoProcessor installers:"
	echo ""
	ls -1 gp-*.tar.gz | sort --reverse
	ls -1 gptest-*.tar.gz | sort --reverse

	echo ""
	read -p "Specify the file to install as shown (q to quit, c to continue to next step):  " fileToInstall
	if [ "${fileToInstall}" = "q" ]; then
		exit 0
	elif [ "${fileToInstall}" = "c" ]; then
		break
	else
		# Install the provided file
		echo ""
		install ${fileToInstall}
	fi
done
