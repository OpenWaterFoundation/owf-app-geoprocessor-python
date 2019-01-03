#!/bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL
#
# Install the GeoProcessor Python virtual environment in deployed user environment.
# This involves searching and replacing some paths with user file location.

# For Cygwin, the software can be installed in a development environment rather
# than cloning the repository and building a virtual environment

version="1.2.0 2019-01-02"

# Get the location where this script is located since it may have been run from any folder
scriptFolder=`cd $(dirname "$0") && pwd`
pwdFolder=`pwd`

# Supporting scripts

# Install the GeoProcessor files
# - unzip the tar-gz to the output folder
installFiles() {
	# Install to the given folder
	# Check whether parent folder exists
	installParentFolder=`dirname ${installFolderAbs}`
	if [ ! -d "${installParentFolder}" ]; then
		echo "Install parent folder does not exist:  ${installParentFolder}"
	else
		while [ "1" = "1" ]; do
			if [ "$batchMode" = "no" ]; then
				echo "Will install GeoProcessor virtual env as folder:  ${installFolderAbs}"
				read -p "Continue with install [Y/n]? " answer
			else
				# Batch mode so default to continue with install
				answer="y"
			fi
			if [ "$answer" = "" -o "$answer" = "y" -o "$answer" = "Y" ]; then
				# Remove the previous install if it exists
				if [ -d "${installFolderAbs}" ]; then
					echo "Removing existing install ${installFolderAbs}"
					rm -rf "${installFolderAbs}"
				fi
				# Change to the parent of the install folder
				cd "${installParentFolder}"
				# Get the name of the top-level folder in the file
				gpTargzTopFolder=`tar -tzvf "${installerTargzFileAbs}" | head -1 | tr -s ' ' | cut -d' ' -f6`
				echo "Top level folder in installer file=$gpTargzTopFolder"
				sleep 1
				# Unzip the file
				tar -xzvf "${installerTargzFileAbs}"
				didInstall="yes"
				# Rename the top-level folder to the requested folder
				echo "Currently in folder:  $installParentFolder"
				echo "Renaming tar.gz top folder shown above from ${gpTargzTopFolder} to requested ${installFolderAbs}"
				installFolderAbsBasename=`basename ${installFolderAbs}`
				if [ -d "${gpTargzTopFolder}" ]; then
					mv ${gpTargzTopFolder} ${installFolderAbsBasename}
					#
					# Print final instructions to the user
					echo ""
					echo "Run the GeoProcessor using one of the scripts from folder:"
					echo "  $installFolderAbs/scripts"
					echo ""
					ls -1 $installFolderAbs/scripts/gp* | xargs -n 1 basename
					echo ""
					break
				else
					# Error in the script logic, should not happen
					echo "Top-level folder ${gpTargzTopFolder} from tar.gz not found"
					exit 1
				fi
			elif [ "${answer}" = "n" ]; then
				# Quit the script
				exit 0
			fi
		done
	fi
}

# Parse the command line and set variables to control logic
# - Need to use local variables, see:  https://stackoverflow.com/questions/16654607/using-getopts-inside-a-bash-function
parseCommandLine() {
	#echo "Parsing command line..."
	local OPTIND opt b h i o v
	while getopts :bhi:o:v opt; do
		#echo "Command line option is ${opt}"
		case $opt in
			b) # Run in batch mode (no prompts)
				batchMode="yes"
				;;
			h) # Usage
				printUsage
				exit 0
				;;
			i) # Installer tar.gz file
				installerTargzFile=$OPTARG
				setInstallerTargzFileAbs
				;;
			o) # Installer output folder (installed location)
				installFolder=$OPTARG
				setInstallFolderAbs
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
	echo "Usage:  install-gp-venv.sh -i gp-installer.tar.gz -o installFolder"
	echo ""
	echo "Example:"
	echo '  install-gp-venv.sh -i gp-1.0.0-lin-venv.tar.gz -o $HOME/gp-venv'
	echo '  install-gp-venv.sh -i gptest-1.0.0-lin-venv.tar.gz -o $HOME/gptest-venv'
	echo '  install-gp-venv.sh      (will prompt for input and output)'
	echo ""
	echo "-b               Run in batch mode with no prompts (missing input will result in exit)."
	echo "-h               Print the usage."
	echo "-i gp.tar.gz     Specify the installer tar.gz file."
	echo "-o outputFolder  Specify the output folder for the install."
	echo "-v               Print the version."
	echo ""
}

# Print the program version
printVersion() {
	echo ""
	echo "install-gp-venv version ${version}"
	echo ""
	echo "GeoProcessor Installer"
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

# Prompt for the filename of the distribution file, for example:  gptest-1.0.0-cyg-venv.tar.gz
# - this script might be run in the development environment to test installer or
#   when installing after a download (called by download-gp.sh).
promptForInstallerFile() {
	while [ "1" = "1" ]; do
		# List files that are candidates for installing
		# -only list folders that have some matching files
		# -no files will output something like "ls: cannot access 'xxxx': No such file or directory
		echo ""
		echo "The -i option was not specified on the command line."
		echo "Therefore, select a gp*.tar.gz file to install (use mouse copy/paste)."
		echo "Matching gp*.tar.gz files in candidate folders are listed below (if available)."
		echo "Current folder:  $scriptFolder"
		# Current folder...
		count=$(ls -1 gp*.tar.gz 2> /dev/null | grep -v 'cannot' | wc -l)
		if [ "$count" -ne 0 ]; then
			echo ""
			echo "Current folder:"
			ls -1 gp*.tar.gz
		fi
		# ${devVirtualEnvTmpFolder}, used in development environment under build-util
		if [ -d "${devVirtualEnvTmpFolder}" ]; then
			# Folder under build-util/ in development environment
			count=$(ls -1 venv-tmp/gp*.tar.gz 2> /dev/null | grep -v 'cannot' | wc -l)
			if [ "$count" -ne 0 ]; then
				echo ""
				echo "./venv-tmp folder:"
				ls -1 venv-tmp/gp*.tar.gz
			fi
		fi
		# /tmp folder, used in production to download from website
		count=$(ls -1 /tmp/gp*.tar.gz 2> /dev/null | grep -v 'cannot' | wc -l)
		if [ "$count" -ne 0 ]; then
			echo ""
			echo "/tmp folder:"
			ls -1 gp*.tar.gz
		fi
		# Installer tar.gz file has not been specified with -i command line option so prompt for it
		echo ""
		read -p "Specify the GeoProcessor tar.gz file to install (q to quit): " installerTargzFile
		if [ "${installerTargzFile}" = "q" ]; then
			# Quit the script
			exit 0
		else
			if [ ! -f "${installerTargzFile}" ]; then
				echo "File does not exist:  ${installerTargzFile}"
				# Loop and prompt again
			else
				# Get the absolute path of the install file
				setInstallerTargzFileAbs
				echo ""
				echo "Will install GeoProcessor virtual environment from:"
				echo "  ${installerTargzFileAbs}"
				break
			fi
		fi
	done
}

# Prompt for the folder to install, for example "gptest" under a product development folder.
promptForInstallFolder() {
	didInstall="no"
	exampleVersion="1.0.0"
	if [ ! -z "$installingWhatVersion" ]; then
		exampleVersion="$installingWhatVersion"
	fi
	while [ "1" = "1" ]; do
		if [ "$didInstall" = "yes" ]; then
			# Install was completed so exit the loop
			break
		fi
		echo ""
		echo "Current folder is:"
		echo "  ${pwdFolder}"
		# Check whether gp or gptest is being installed
		if [ "$installingGp" = "yes" ]; then
			# Installing gp
			echo ""
			echo "The installation folder is typically gp-venv or gp-${exampleVersion}-venv."
			echo "For example /home/$USER/gp-venv or /home/$USER/gp-${exampleVersion}-venv."
			# List the home folder as FYI
			echo "Existing /home/$USER/gp-* folders include:"
			ls -1 -d /home/$USER/gp-*
		else
			# Installing gptest
			echo "The installation folder is typically gptest-venv or gptest-${exampleVersion}-venv."
			echo "For example /home/$USER/gptest-venv or /home/$USER/gptest-${exampleVersion}-venv."
			# List the home folder as FYI
			echo "Existing /home/$USER/gptest-* folders include:"
			ls -1 -d /home/$USER/gptest-*
		fi
		echo "Specify the folder to install into, will create if does not exist."
		read -p "Specify relative to the current folder or provide an absolute path (q to quit): " installFolder
		if [ "${installFolder}" = "q" ]; then
			# Quit the script
			exit 0
		elif [ -z "${installFolder}" ]; then
			# Continue
			:
		else
			# Warn the user about overwrite
			if [ -d "${installFolder}" ]; then
				$echo2 "Install folder exists:  ${installFolder}"
				read -p "Continue with install to remove existing and then install new (y/n/q): " confirmAnswer
				if [ "${confirmAnswer}" = "q" ]; then
					# Quit the script
					exit 0
				elif [ "${confirmAnswer}" = "y" ]; then
					# Break out of loop
					break
				else
					# n or other - give a chance to pick different install folder
					:
				fi
			else
				# The install folder does not exist so break out of loop and use it
				break
			fi
		fi
	done
	setInstallFolderAbs
}

# Set the installer tar.gz file absolute path
setInstallerTargzFileAbs() {
	firstChar=`echo ${installerTargzFile} | cut -c1`
	if [ "${firstChar}" = "." ]; then
		# Assume relative to the pwdFolder
		installerTargzFileAbs="${pwdFolder}/${installerTargzFile}"
	elif [ "${firstChar}" = "/" ]; then
		# Assume absolute path
		installerTargzFileAbs="${installerTargzFile}"
	else 
		# Assume current folder
		installerTargzFileAbs="${pwdFolder}/${installerTargzFile}"
	fi
}

# Set the install folder absolute path
setInstallFolderAbs() {
	# Get the absolute path of the install file
	firstChar=`echo ${installFolder} | cut -c1`
	if [ "${firstChar}" = "." ]; then
		# Assume relative to the pwdFolder
		installFolderAbs="${pwdFolder}/${installFolder}"
	elif [ "${firstChar}" = "/" ]; then
		# Assume absolute path
		installFolderAbs="${installFolder}"
	else 
		# Assume current folder
		installFolderAbs="${pwdFolder}/${installFolder}"
	fi
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
	okColor='\e[0;40;32m' # status is good, 40=background black, 32=green
	endColor='\e[0m' # To switch back to default color
}

# Update virtual environment scripts to have installed path
updateVenvScripts() {
	# Search and replace the original virtual environment configuration to installed folder
	installFolderAbsForSed=`echo $installFolderAbs | tr '/' '\\/'`
	# bin/activate
	binActivate="${installFolderAbs}/bin/activate"
	if [ -f "${binActivate}" ]; then
		sed -i "s,^VIRTUAL_ENV=.*,VIRTUAL_ENV=\"$installFolderAbs\",g" ${binActivate}
	fi
	# bin/activate.csh
	binActivateCsh="${installFolderAbs}/bin/activate.csh"
	if [ -f "${binActivateCsh}" ]; then
		sed -i "s,^setenv VIRTUAL_ENV.*,setenv VIRTUAL_ENV \"$installFolderAbs\",g" ${binActivateCsh}
	fi
	# bin/activate.fish
	binActivateFish="${installFolderAbs}/bin/activate.fish"
	if [ -f "${binActivateFish}" ]; then
		sed -i "s,^set -gx VIRTUAL_ENV=.*,set -gx VIRTUAL_ENV \"$installFolderAbs\",g" ${binActivateFish}
	fi
	# bin/chardetect
	binChardetect="${installFolderAbs}/bin/chardetect"
	if [ -f "${binChardetect}" ]; then
		sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${binChardetect}
	fi
	# bin/easy_install
	binEasyInstall="${installFolderAbs}/bin/easy_install"
	if [ -f "${binEasyInstall}" ]; then
		sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${binEasyInstall}
	fi
	# TODO smalers 2018-11-27 brute force but need to make more intelligent
	# bin/easy_install-3.6
	binEasyInstall36="${installFolderAbs}/bin/easy_install-3.6"
	if [ -f "${binEasyInstall36}" ]; then
		sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${binEasyInstall36}
	fi
	# bin/easy_install-3.4
	binEasyInstall34="${installFolderAbs}/bin/easy_install-3.4"
	if [ -f "${binEasyInstall34}" ]; then
		sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${binEasyInstall34}
	fi
	# bin/pip
	binPip="${installFolderAbs}/bin/pip"
	if [ -f "${binPip}" ]; then
		sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${binPip}
	fi
	# bin/pip3
	binPip3="${installFolderAbs}/bin/pip3"
	if [ -f "${binPip3}" ]; then
		sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${binPip3}
	fi
	# bin/pip3.6
	binPip36="${installFolderAbs}/bin/pip3.6"
	if [ -f "${binPip36}" ]; then
		sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${binPip36}
	fi
	# bin/pip3.4
	binPip34="${installFolderAbs}/bin/pip3.4"
	if [ -f "${binPip34}" ]; then
		sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${binPip34}
	fi
	# bin/python3
	# - no need to modify versioned copes because symlinks are used rather than copies
	binPip34="${installFolderAbs}/bin/python"
	if [ -f "${binPython}" ]; then
		sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${binPython}
	fi
	# bin/python-config
	binPythonConfig="${installFolderAbs}/bin/python-config"
	if [ -f "${binPythonConfig}" ]; then
		sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${binPythonConfig}
	fi
	# bin/wheel
	binWheel="${installFolderAbs}/bin/wheel"
	if [ -f "${binWheel}" ]; then
		sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${binWheel}
	fi
}

# Main entry point into script

# Default values
# Path to installer tar.gz file
installerFile=""
# Path to installed folder
installFolder=""
# Interactive is default, meaning prompt for the tar.gz file to install
batchMode="no"
# Default echo for special characters
echo2="echo -e"

# Setup the echo for color-coded output
setupEcho

# Parse the command line.
parseCommandLine "$@"

# Define top-level folders - everything is relative to this below to avoid confusion
# - this is for the development environment
# - in development environment this script is located in build-util/install
devBuildUtilFolder=$(dirname ${scriptFolder})
# Name of the parent folder for virtual environments
devVirtualEnvTmpFolder="${devBuildUtilFolder}/venv-tmp"

# Prompt for the installer file (or use what was passed on the command line)
if [ "$batchMode" = "yes" ]; then
	# Running in batch mode, make sure that -i has been specified
	if [ -z "${installerTargzFile}" ]; then
		echo ""
		>&2 $echo2 "${warnColor}[ERROR] The installer file has not been specified with -i.${endColor}"
		printUsage
		exit 1
	fi
else
	if [ -z "${installerTargzFile}" ]; then
		promptForInstallerFile
	fi
fi

# Determine what product is being installed and what version, for use in messages
# Determine whether installing gp (installingWhat="gp") or gptest (installingWhat="gptest")
# - count the number of lines that the tar.gz file includes "gptest" should be 1 or 0
checkGptest=$(echo "$installerTargzFileAbs" | grep 'gptest' | wc -l)
installingWhat="gp"
# Determine the version so it can be used in suggestions
# - the tar file name is similar to gp-1.0.0-cyg-venv.tar.gz
#   and gptest-1.0.0-cyg-venv.tar.gz
# - use basename to make sure it is a file and not a path
installingWhatVersion=$(basename "$installerTargzFile" | cut -d '-' -f 2 )
if [ "$checkGptest" -ne 0 ]; then
	installingWhat="gptest"
fi
echo ""
echo "Installing $installingWhat version $installingWhatVersion"

# Prompt for the install (output) folder
if [ "$batchMode" = "yes" ]; then
	# Running in batch mode, make sure that -o has been specified
	if [ -z "${installFolder}" ]; then
		echo ""
		>&2 $echo2 "${warnColor}[ERROR] The install (output) folder has not been specified with -o.${endColor}"
		printUsage
		exit 1
	fi
else
	promptForInstallFolder
fi

# Check for the input and output again
if [ -z "${installerTargzFileAbs}" ]; then
	echo ""
	>&2 $echo2 "${warnColor}[ERROR] The installer file has not been specified.  Exiting.${endColor}"
	printUsage
	exit 1
fi
if [ -z "${installFolder}" ]; then
	echo ""
	>&2 $echo2 "${warnColor}[ERROR] The install (output) folder has not been specified.  Exiting.${endColor}"
	printUsage
	exit 1
fi

# Install files from the tar.gz file
installFiles

# Update Python venv scripts to use the new path
updateVenvScripts

exit 0
