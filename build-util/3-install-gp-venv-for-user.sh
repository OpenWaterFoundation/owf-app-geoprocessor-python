#!/bin/sh
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL
#
# Install the GeoProcessor Python virtual environment in deployed user environment.
# This involves searching and replacing some paths with user file location.

# For Cygwin, the software can be installed in a development environment rather
# than cloning the repository and building a virtual environment

# Get the location where this script is located since it may have been run from any folder
scriptFolder=`cd $(dirname "$0") && pwd`
pwdFolder=`pwd`

# Prompt for the filename of the distribution file, for example:  gptest-1.0.0-cyg-venv

while [ "1" = "1" ]; do
	echo ""
	echo "tar.gz files in current folder:"
	ls -1 *.tar.gz
	if [ -d "venv-tmp" ]; then
		echo "tar.gz files in venv-tmp folder:"
		ls -1 venv-tmp/*.tar.gz
	fi
	echo ""
	read -p "Specify the GeoProcessor tar.gz file to install (q to quit): " gptargzFile
	if [ "${gptargzFile}" = "q" ]; then
		# Quit the script
		exit 0
	else
		if [ ! -f "${gptargzFile}" ]; then
			echo "File does not exist:  ${gptargzFile}"
		else
			# Get the absolute path of the install file
			firstChar=`echo ${gptargzFile} | cut -c1`
			if [ "${firstChar}" = "." ]; then
				# Assume relative to the pwdFolder
				gptargzFileAbs="${pwdFolder}/${gptargzFile}"
			elif [ "${firstChar}" = "/" ]; then
				# Assume absolute path
				gptargzFileAbs="${gptargzFile}"
			else 
				# Assume current folder
				gptargzFileAbs="${pwdFolder}/${gptargzFile}"
			fi
			echo ""
			echo "Will install GeoProcessor virtual environment from:  ${gptargzFileAbs}"
			break
		fi
	fi
done

# Prompt for the folder to install, for example "gptest" under a product development folder.

didInstall="no"
while [ "1" = "1" ]; do
	if [ "$didInstall" = "yes" ]; then
		# Install was completed so exit the loop
		break
	fi
	echo ""
	echo "Current folder is ${pwdFolder}"
	echo "Installation folder is typically gptest-venv or gptest-1.0.0-venv (specific to version)."
	read -p "Specify the folder to install in (q to quit): " installFolder
	if [ "${installFolder}" = "q" ]; then
		# Quit the script
		exit 0
	else
		# Install to the given folder
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
		# Check whether parent folder exists
		installParentFolder=`dirname ${installFolderAbs}`
		if [ ! -d "${installParentFolder}" ]; then
			echo "Install parent folder does not exist:  ${installParentFolder}"
		else
			while [ "1" = "1" ]; do
				echo "Will install GeoProcessor virtual env as folder:  ${installFolderAbs}"
				read -p "Continue with install [y/n]? " answer
				if [ "${answer}" = "y" ]; then
					# Remove the previous install if it exists
					if [ -d "${installFolderAbs}" ]; then
						echo "Removing previous install ${installFolderAbs}"
						rm -rf "${installFolderAbs}"
					fi
					# Change to the parent of the install folder
					cd "${installParentFolder}"
					# Get the name of the top-level folder in the file
					gptargzTopFolder=`tar -tzvf "${gptargzFileAbs}" | head -1 | tr -s ' ' | cut -d' ' -f6`
					# Unzip the file
					tar -xzvf "${gptargzFileAbs}"
					didInstall="yes"
					# Rename the top-level folder to the requested folder
					echo "Renaming tar.gz top folder from ${gptargzTopFolder} to ${installFolderAbs}"
					installFolderAbsBasename=`basename ${installFolderAbs}`
					if [ -d "${gptargzTopFolder}" ]; then
						mv ${gptargzTopFolder} ${installFolderAbsBasename}
					else
						echo "Top-level folder ${gptargzTopFolder} from tar.gz not found"
					fi
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
					# Attempted actions above so exit the loop...
					break
				elif [ "${answer}" = "n" ]; then
					# Quit the script
					exit 0
				fi
			done
		fi
	fi
done
