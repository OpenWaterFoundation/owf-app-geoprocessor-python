#!/bin/sh
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
					sed -i "s,^VIRTUAL_ENV=.*,VIRTUAL_ENV=\"$installFolderAbs\",g" ${installFolderAbs}/bin/activate
					# bin/activate.csh
					sed -i "s,^setenv VIRTUAL_ENV.*,setenv VIRTUAL_ENV \"$installFolderAbs\",g" ${installFolderAbs}/bin/activate.csh
					# bin/activate.fish
					sed -i "s,^set -gx VIRTUAL_ENV=.*,set -gx VIRTUAL_ENV \"$installFolderAbs\",g" ${installFolderAbs}/bin/activate.fish
					# bin/easy_install
					sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${installFolderAbs}/bin/easy_install
					# bin/easy_install-3.6
					sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${installFolderAbs}/bin/easy_install-3.6
					# bin/pip
					sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${installFolderAbs}/bin/pip
					# bin/pip3
					sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${installFolderAbs}/bin/pip3
					# bin/pip3.6
					sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${installFolderAbs}/bin/pip3.6
					# bin/python3
					sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${installFolderAbs}/bin/python3
					# bin/python-config
					sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${installFolderAbs}/bin/python-config
					# bin/wheel
					sed -i "s,^'''exec' .*,'''exec' $installFolderAbs/bin/python3 \"\$O\" \"\$@\",g" ${installFolderAbs}/bin/wheel
					break
				elif [ "${answer}" = "n" ]; then
					# Quit the script
					exit 0
				fi
			done
		fi
	fi
done
