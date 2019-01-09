#!/bin/sh
#
# Copy the gp installer contents to the software.openwaterfoundation.org website
# - replace the installer file on the web with local files
# - also update the catalog file that lists available GeoProcessor downloaders
# - must specify Amazon profile as argument to the script
# - DO NOT FORGET TO CHANGE THE programVersion and programVersionDate when making changes

# Supporting functions, alphabetized

# Check input
# - make sure that the Amazon profile was specified
checkInput() {
	if [ -z "$awsProfile" ]; then
		echo ""
		echo "Amazon profile to use for upload was not specified with -a option.  Exiting."
		printUsage
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
			operatingSystem="mingw"
			operatingSystemShort="min"
			;;
	esac
	echo ""
	echo "Detected operatingSystem=$operatingSystem operatingSystemShort=$operatingSystemShort"
	echo ""
}

# Parse the command parameters
# - use the getopt command line program so long options can be handled
parseCommandLine() {
	# Special case when no options are specified (-a is required)
	if [ "$#" -eq 0 ]; then
		printUsage
		exit 0
	fi
	# Single character options
	optstring="a:hv"
	# Long options
	optstringLong="help,include-cygwin::,include-mingw::,include-windows::,version"
	# Parse the options using getopt command
	GETOPT_OUT=$(getopt --options $optstring --longoptions $optstringLong -- "$@")
	exitCode=$?
	if [ $exitCode -ne 0 ]; then
		echo ""
		printUsage
		exit 1
	fi
	# The following constructs the command by concatenating arguments
	eval set -- "$GETOPT_OUT"
	# Loop over the options
	while true; do
		#echo "Command line option is ${opt}"
		case "$1" in
			-a) # -a awsProfile  Specify Amazon web service profile file
				awsProfile=$2
				shift 2
				;;
			-h|--help) # -h or --help  Print the program usage
				printUsage
				exit 0
				;;
			--include-cygwin) # --include-cygwin=yes|no  Include the Cygwin installer for upload
				case "$2" in
					"") # Nothing specified so default to yes
						includeCygwin="yes"
						shift 2
						;;
					*) # yes or no has been specified
						includeCygwin=$2
						shift 2
						;;
				esac
				;;
			--include-mingw) # --include-mingw=yes|no  Include the MinGW installer for upload
				case "$2" in
					"") # Nothing specified so default to yes
						includeMingw="yes"
						shift 2
						;;
					*) # yes or no has been specified
						includeMingw=$2
						shift 2
						;;
				esac
				;;
			--include-windows) # --include-windows=yes|no  Include the Windows installer for upload (not just Cygwin)
				case "$2" in
					"") # Nothing specified so default to yes
						includeWindows="yes"
						shift 2
						;;
					*) # yes or no has been specified
						includeWindows=$2
						shift 2
						;;
				esac
				;;
			-v|--version) # -v or --version  Print the program version
				printVersion
				exit 0
				;;
			--) # No more arguments
				shift
				break
				;;
			*) # Unknown option
				echo "" 
				echo "Invalid option $1." >&2
				printUsage
				exit 1
				;;
		esac
	done
}

# Print the program usage
printUsage() {
	echo ""
	echo "Usage:  $programName -a awsProfile"
	echo ""
	echo "Copy the GeoProcessor installer files to the Amazon S3 static website folder:"
	echo "  $s3FolderUrl"
	echo ""
	echo "-a awsProfile         Specify the Amazon profile to use for the upload."
	echo "-h or --help          Print the usage."
	echo "--include-cygwin=no   Turn off Cygwin upload (default is include)."
	echo "--include-mingw=no    Turn off MinGW upload (default is include)."
	echo "--include-window=no   Turn off Windows upload (default is include)."
	echo "-v or --version       Print the version and copyright/license notice."
	echo ""
}

# Print the script version and copyright/license notices
# - calling code must exist with appropriate code
printVersion() {
	echo ""
	echo "$programName version $programVersion ${programVrsionDate}"
	echo ""
	echo "GeoProcessor"
	echo "Copyright 2017-2018 Open Water Foundation."
	echo ""
	echo "License GPLv3+:  GNU GPL version 3 or later"
	echo ""
	echo "There is ABSOLUTELY NO WARRANTY; for details see the"
	echo "'Disclaimer of Warranty' section of the GPLv3 license in the LICENSE file."
	echo "This is free software: you are free to change and redistribute it"
	echo "under the conditions of the GPLv3 license in the LICENSE file."
	echo ""
}

# Upload the index.html file for the download static website
# - this is basic at the moment but can be improved in the future such as
#   software.openwaterfoundation.org page, but for only one product, with list of variants and versions
uploadIndexHtmlFile() {
	# Create an index.html file for upload
	indexHtmlTmpFile="/tmp/$USER-gp-index.html"
	s3IndexHtmlUrl="${s3FolderUrl}/index.html"
	echo '<!DOCTYPE html>' > $indexHtmlTmpFile
	echo '<head>' >> $indexHtmlTmpFile
	echo '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />' >> $indexHtmlTmpFile
	echo '<meta http-equiv="Pragma" content="no-cache" />' >> $indexHtmlTmpFile
	echo '<meta http-equiv="Expires" content="0" />' >> $indexHtmlTmpFile
	echo '<meta charset="utf-8"/>' >> $indexHtmlTmpFile
	echo '<style>' >> $indexHtmlTmpFile
	echo '   body { font-family: "Trebuchet MS", Helvetica, sans-serif !important; }' >> $indexHtmlTmpFile
	echo '   table { border-collapse: collapse; }' >> $indexHtmlTmpFile
	echo '   tr { border: none; }' >> $indexHtmlTmpFile
	echo '   th {' >> $indexHtmlTmpFile
	echo '     border-right: solid 1px;' >> $indexHtmlTmpFile
	echo '     border-left: solid 1px;' >> $indexHtmlTmpFile
	echo '     border-bottom: solid 1px;' >> $indexHtmlTmpFile
	echo '   }' >> $indexHtmlTmpFile
	echo '   td {' >> $indexHtmlTmpFile
	echo '     border-right: solid 1px;' >> $indexHtmlTmpFile
	echo '     border-left: solid 1px;' >> $indexHtmlTmpFile
	echo '   }' >> $indexHtmlTmpFile
	echo '</style>' >> $indexHtmlTmpFile
	echo '<title>GeoProcessor Downloads</title>' >> $indexHtmlTmpFile
	echo '</head>' >> $indexHtmlTmpFile
	echo '<body>' >> $indexHtmlTmpFile
	echo '<h1>Open Water Foundation GeoProcessor Software Downloads</h1>' >> $indexHtmlTmpFile
	echo '<p>' >> $indexHtmlTmpFile
	echo 'The GeoProcessor software is available for Cygwin, Linux, and Windows.' >> $indexHtmlTmpFile
	echo 'See the <a href="http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/appendix-install/install/">GeoProcessor installation documentation</a> for detailed installation information.' >> $indexHtmlTmpFile
	echo '</p>' >> $indexHtmlTmpFile
	echo '<p>' >> $indexHtmlTmpFile
	echo '<ul>' >> $indexHtmlTmpFile
	echo '<li>Multiple versions of the GeoProcessor can be installed on a computer to facilitate testing and version migration.' >> $indexHtmlTmpFile
	echo '<li>The <code>gp</code> downloads require that QGIS is also installed.  The <code>gptest</code> downloads do not require QGIS.</li>' >> $indexHtmlTmpFile
	echo '    <ul>' >> $indexHtmlTmpFile
	echo '    <li>When using the GeoProcessor with QGIS, the QGIS standalone installer is recommended because it installs versions in separate folders and menus.</li>' >> $indexHtmlTmpFile
	echo '    <li>Typically the latest QGIS 3 release is used (do not install the old long-term standalone 2.x release).</li>' >> $indexHtmlTmpFile
	echo '    <li>See <a href="https://qgis.org/en/site/forusers/download.html">Download QGIS</a>.</li>' >> $indexHtmlTmpFile
	echo '    <li>See <a href="http://learn.openwaterfoundation.org/owf-learn-qgis/install-qgis/install-qgis/">OWF Learn QGIS</a> documentation for additional information about installing QGIS.</li>' >> $indexHtmlTmpFile
	echo '    </ul>' >> $indexHtmlTmpFile
	echo '<li>Download files that include <code>dev</code> in the version are development versions that can be installed to see the latest features and bug fixes that are under development.</li>' >> $indexHtmlTmpFile
	echo '<li>Download files that include <code>cyg</code> in the filename are for Cygwin, <code>lin</code> are for Linux, and <code>win</code> are for Windows.</li>' >> $indexHtmlTmpFile
	echo '<li><b>If clicking on a file download link does not download the file, right-click on the link and use "Save link as..." (or similar).</b></li>' >> $indexHtmlTmpFile
	echo '</ul>' >> $indexHtmlTmpFile

	echo '<hr>' >> $indexHtmlTmpFile
	echo '<h2>Windows Download</h2>' >> $indexHtmlTmpFile
	echo '<p>' >> $indexHtmlTmpFile
	echo 'Install the GeoProcessor on Windows by downloading a zip file and extracting to a folder in user files such as <code>C:\Users\user\gp-1.1.0-venv</code> or <code>C:\Users\user\gp-venv</code>.' >> $indexHtmlTmpFile
	echo 'Then run <code>Scripts\gpui.bat</code> in an Windows command prompt window to start the GeoProcessor.' >> $indexHtmlTmpFile
	echo '</p>' >> $indexHtmlTmpFile
	# Generate a table of available versions for Windows
	uploadIndexHtmlFile_Table win

	echo '<hr>' >> $indexHtmlTmpFile
	echo '<h2>Linux Download</h2>' >> $indexHtmlTmpFile
	echo '<p>' >> $indexHtmlTmpFile
	echo 'Install the GeoProcessor on Linux by downloading the <a href="download-gp.sh">download-gp.sh script</a> and running it in a shell window.' >> $indexHtmlTmpFile
	echo 'You will be prompted for options for where to install the software.' >> $indexHtmlTmpFile
	echo 'Once installed, run the GeoProcessor using scripts in the <code>scripts</code> folder under the install folder.' >> $indexHtmlTmpFile
	echo '<b>Do not download directly using files below (the list is provided as information).</b>' >> $indexHtmlTmpFile
	echo '</p>' >> $indexHtmlTmpFile
	# Generate a table of available versions for Linux
	uploadIndexHtmlFile_Table lin

	echo '<hr>' >> $indexHtmlTmpFile
	echo '<h2>Cygwin Download</h2>' >> $indexHtmlTmpFile
	echo '<p>' >> $indexHtmlTmpFile
	echo 'Install the GeoProcessor on Cygwin by downloading the <a href="download-gp.sh">download-gp.sh script</a> and running it in a shell window.' >> $indexHtmlTmpFile
	echo 'You will be prompted for options for where to install the software.' >> $indexHtmlTmpFile
	echo 'Once installed, run the GeoProcessor using scripts in the <code>scripts</code> folder under the install folder.' >> $indexHtmlTmpFile
	echo '<b>Do not download directly using files below (the list is provided as information).</b>' >> $indexHtmlTmpFile
	echo '</p>' >> $indexHtmlTmpFile
	# Generate a table of available versions for Cygwin
	uploadIndexHtmlFile_Table cyg

	echo '</body>' >> $indexHtmlTmpFile
	echo '</html>' >> $indexHtmlTmpFile
	# set -x
	aws s3 cp $indexHtmlTmpFile $s3IndexHtmlUrl ${dryrun} --profile "$awsProfile" ; errorCode=$?
	# { set +x; } 2> /dev/null
	if [ $errorCode -ne 0 ]; then
		echo ""
		echo "[Error] Error uploading index.html file."
		exit 1
	fi
}

# Create a table of downloads for an operating system to be used in the index.html file.
uploadIndexHtmlFile_Table() {
	# Operating system is passed in as the required first argument
	downloadOs=$1
	echo '<table>' >> $indexHtmlTmpFile
	# List the available download files
	# Listing local files does not show all available files on Amazon but may be useful for testing
	catalogSource="aws"  # "aws" or "local"
	if [ "$catalogSource" = "aws" ]; then
		# Use AWS list from catalog file for the index.html file download file list, with format like
		# the following (no space at beginning of the line):
		#
		# 2018-12-04 16:17:19   46281975 geoprocessor/1.0.0/gptest-1.0.0-lin-venv.tar.gz
		#
		# awk by default allows multiple spaces to be used.
		echo '<tr><th>Download File</th><th>Product</th><th>Version</th><th>File Timestamp</th><th>Operating System</th></tr>' >> $indexHtmlTmpFile
		cat "${tmpS3CatalogPath}" | grep "${downloadOs}-" | sort -r | awk '
			{
				# Download file is the full line
				downloadFileDate = $1
				downloadFileTime = $2
				downloadFileSize = $3
				downloadFilePath = $4
				# Split the download file path into parts to get the download file without path
				split(downloadFilePath,downloadFilePathParts,"/")
				downloadFile = downloadFilePathParts[3]
				# Split the download file into parts to get other information
				split(downloadFile,downloadFileParts,"-")
				downloadFileProduct=downloadFileParts[1]
				downloadFileVersion=downloadFileParts[2]
				downloadFileOs=downloadFileParts[3]
				if ( downloadFileOs == "cyg" ) {
					downloadFileOs = "Cygwin"
				}
				else if ( downloadFileOs == "lin" ) {
					downloadFileOs = "Linux"
				}
				else if ( downloadFileOs == "win" ) {
					downloadFileOs = "Windows"
				}
				printf "<tr><td><a href=\"%s/%s\"><code>%s</code></a></td><td>%s</td><td>%s</td><td>%s %s</td><td>%s</td></tr>", downloadFileVersion, downloadFile, downloadFile, downloadFileProduct, downloadFileVersion, downloadFileDate, downloadFileTime, downloadFileOs
			}' >> $indexHtmlTmpFile
	else
		# List local files in the index.html file download file list
		# Change to the folder where *.zip and *.tar.gz files are and list, with names like:
		#     gp-1.2.0dev-win-venv.zip
		#     gptest-1.0.0-cyg-venv.tar.gz
		cd ${virtualenvTmpFolder}
		echo '<tr><th>Download File</th><th>Product</th><th>Version</th><th>Operating System</th></tr>' >> $indexHtmlTmpFile
		ls -1 *.zip *.tar.gz | grep "${downloadOs}-" | sort -r | awk '
			{
				# Download file is the full line
				downloadFile = $1
				# Version is the second part of he download file, dash-delimited
				split(downloadFile,downloadFileParts,"-")
				downloadFileProduct=downloadFileParts[1]
				downloadFileVersion=downloadFileParts[2]
				downloadFileOs=downloadFileParts[3]
				printf "<tr><td><a href=\"%s/%s\"><code>%s</code></a></td><td>%s</td><td>%s</td><td>%s</td></tr>", downloadFileVersion, downloadFile, downloadFile, downloadFileProduct, downloadFileVersion, downloadFileOs
			}' >> $indexHtmlTmpFile
	fi
	echo '</table>' >> $indexHtmlTmpFile
}

# Upload local installer files to Amazon S3
# - includes the tar.gz and .zip files and catalog file used by download-gp.sh
# - for Linux variants upload gptest, for windows upload gp
uploadInstaller() {
	# The location of the installer is
	# ===========================================================================
	# Step 1. Upload the installer file for the current version
	#         - use copy to force upload
	# The following handles Cygwin, Linux, and MinGW uploads
	includeNix="yes"
	if [ "$operatingSystem" = "cygwin" ]; then
		# On Cygwin, can turn off
		includeNix=$installCygwin
	elif [ "$operatingSystem" = "linux" ]; then
		# On Linux, can turn off
		includeNix="$installLinux"
	elif [ "$operatingSystem" = "mingw" ]; then
		# On MinGW, can turn off
		includeNix="$installMingw"
	fi
	if [ "$includeNix" = "yes" ]; then
		echo "Uploading GeoProcessor installation file for $operatingSystem"
		# set -x
		s3virtualenvGptestTargzUrl="${s3FolderUrl}/$gpVersion/$virtualenvGptestTargzFile"
		if [ ! -f "$virtualenvGptestTargzPath" ]; then
			echo ""
			echo "Installer file does not exist:  $virtualenvGptestTargzPath"
			exit 1
		fi
		aws s3 cp $virtualenvGptestTargzPath $s3virtualenvGptestTargzUrl ${dryrun} --profile "$awsProfile" ; errorCode=$?
		# { set +x; } 2> /dev/null
		if [ $errorCode -ne 0 ]; then
			echo ""
			echo "[Error] Error uploading GeoProcessor installer file for $operatingSystem."
			echo "        Use --include-${operatingSystemShort}=no to ignore installer upload for $operatingSystem."
			exit 1
		fi
	else
		echo "Skip uploading GeoProcessor installation file for $operatingSystem"
		sleep 1
	fi
	# The following handles Windows upload when run on Cygwin
	if [ "$includeWindows" = "yes" ]; then
		echo "Uploading GeoProcessor installation file for Windows"
		# set -x
		s3virtualenvGpZipUrl="${s3FolderUrl}/$gpVersion/$virtualenvGpZipFile"
		if [ ! -f "$virtualenvGpZipPath" ]; then
			echo ""
			echo "Installer file does not exist:  $virtualenvGpZipPath"
			exit 1
		fi
		aws s3 cp $virtualenvGpZipPath $s3virtualenvGpZipUrl ${dryrun} --profile "$awsProfile" ; errorCode=$?
		# { set +x; } 2> /dev/null
		if [ $errorCode -ne 0 ]; then
			echo ""
			echo "[Error] Error uploading GeoProcessor installer file for Windows."
			echo "        Use --include-win=no to ignore Windows installer for upload."
			exit 1
		fi
	else
		echo "Skip uploading GeoProcessor installation file for Windows"
		sleep 1
	fi
	# ===========================================================================
	# Step 2. List files on Amazon S3 and create a catalog file
	# - output of aws ls is similar to:
	#   2018-12-04 16:16:22          0 geoprocessor/
	#   2018-12-04 16:16:37          0 geoprocessor/1.0.0/
	#   2018-12-04 16:17:19   46281975 geoprocessor/1.0.0/gptest-1.0.0-lin-venv.tar.gz
	echo "Creating catalog file from contents of Amazon S3 files"
	# For debugging...
	#set -x
	aws s3 ls "$s3FolderUrl" --profile "$awsProfile" --recursive > $tmpS3ListingPath; errorCode=$?
	#{ set +x; } 2> /dev/null
	if [ $errorCode -ne 0 ]; then
		echo ""
		echo "[Error] Error listing GeoProcessor download files to create catalog."
		exit 1
	fi
	# Pull out the installers available for all platforms since the catalog
	# is used to download to all platforms
	echo "Available GeoProcessor installers are:"
	tmpS3CatalogPath="/tmp/$USER-gp-catalog-ls-installers.txt"
	cat $tmpS3ListingPath | grep -E 'gp.*tar\.gz|gp.*.zip' > ${tmpS3CatalogPath}
	cat $tmpS3CatalogPath
	#
	# ===========================================================================
	# Step 3. Upload the catalog file so download software can use
	#         - for now upload in same format as generated by aws s3 ls command
	echo "Uploading catalog file"
	s3CatalogTxtFileUrl="${s3FolderUrl}/catalog.txt"
	# set -x
	aws s3 cp $tmpS3CatalogPath $s3CatalogTxtFileUrl ${dryrun} --profile "$awsProfile" ; errorCode=$?
	# { set +x; } 2> /dev/null
	if [ $errorCode -ne 0 ]; then
		echo ""
		echo "[Error] Error uploading GeoProcessor catalog file."
		exit 1
	fi
	#
	# ===========================================================================
	# Step 4. Upload the download-gp.sh script, which is needed to download
	echo "Uploading download-gp.sh script"
	s3DownloadScriptUrl="${s3FolderUrl}/download-gp.sh"
	# set -x
	aws s3 cp $buildUtilFolder/install/download-gp.sh $s3DownloadScriptUrl ${dryrun} --profile "$awsProfile" ; errorCode=$?
	# { set +x; } 2> /dev/null
	if [ $errorCode -ne 0 ]; then
		echo ""
		echo "[Error] Error uploading download-gp.sh script file."
		exit 1
	fi
	#
	# ===========================================================================
	# Step 5. Upload the index.html file, which provides a way to navigate downloads
	#         - for now do a very simple html file but in the future may do vue.js
	#           similar to software.openwaterfoundation.org website
	echo "Uploading index.html script"
	uploadIndexHtmlFile
}

# Entry point into script

# Get the location where this script is located since it may have been run from any folder
programName=$(basename $0)
programVersion="1.3.0"
programVersionDate="2019-01-09"

# Check the operating system
# - used to make logic decisions and for some file/folder names so do first
checkOperatingSystem

# Define top-level folders - everything is relative to this below to avoid confusion
scriptFolder=`cd $(dirname "$0") && pwd`
buildUtilFolder=${scriptFolder}
repoFolder=`dirname ${buildUtilFolder}`
buildTmpFolder="${buildUtilFolder}/build-tmp"
# Get the current software version number from development environment files
# The geoprocessor/app/version.py file contains:
# app_version = "1.0.0"
# app_version_date = "2018-07-24"
gpVersionFile="${repoFolder}/geoprocessor/app/version.py"
gpVersion=`cat ${gpVersionFile} | grep app_version -m 1 | cut -d '=' -f 2 | tr -d " " | tr -d '"'`
# Folder for the virtual environment installer
virtualenvTmpFolder="${buildUtilFolder}/venv-tmp"
# File for the tar.gz file (Linux variants)
virtualenvGptestTargzPath="$virtualenvTmpFolder/gptest-${gpVersion}-${operatingSystemShort}-venv.tar.gz"
virtualenvGptestTargzFile=$(basename $virtualenvGptestTargzPath)
# File for the zip file (Windows)
virtualenvGpZipPath="$virtualenvTmpFolder/gp-${gpVersion}-win-venv.zip"
virtualenvGpZipFile=$(basename $virtualenvGpZipPath)
# TODO smalers 2018-12-26 enable QGIS and ArcGIS Pro GP installer
#virtualenvGpTargzFile="$virtualenvTmpFolder/gp-$gpVersion.tar.gz"

# Initialize data
# Set --dryrun to test before actually doing
dryrun=""
#dryrun="--dryrun"
# Root location where files are to be uploaded
s3FolderUrl="s3://software.openwaterfoundation.org/geoprocessor"
gpDownloadUrl="http://software.openwaterfoundation.org/geoprocessor"
# Specify the following with -a
awsProfile=""
# Defaults for whether operating systems are included in upload
# - default is to upload all but change when Windows is not involved
includeCygwin="yes"
includeLinux="yes"
includeMingw="yes"
includeWindows="yes"
if [ $operatingSystem = "yes" ]; then
	includeWindows="no"
fi

# File that contains output of `aws ls`, used to create catalog
user=
tmpS3ListingPath="/tmp/$USER-gp-catalog-ls.txt"

# Parse the command line
parseCommandLine "$@"

# Check input
# - check that Amazon profile was specified
checkInput

# Upload the installer file to Amazon S3
uploadInstaller

# Print useful information to use after running the script
echo ""
echo "Python virtual environment(s) were uploaded to Amazon S3 location:"
echo ""
echo "  ${s3FolderUrl}"
echo "  ${gpDownloadUrl}"
echo ""
echo "Next steps are to do the following:"
echo "  -Visit the following folder to download the GeoProcessor:"
echo "     ${gpDownloadUrl}/index.html"
echo "  -Use the above download site to download the download-gp.sh script to install the GeoProcessor."
echo ""

exit $?
