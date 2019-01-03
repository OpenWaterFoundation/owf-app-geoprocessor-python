#!/bin/sh
#
# Copy the gp installer contents to the software.openwaterfoundation.org website
# - replace the installer file on the web with local files
# - also update the catalog file that lists available GeoProcessor downloaders
# - must specify Amazon profile as argument to the script

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
	echo "Detected operatingSystem=$operatingSystem operatingSystemShort=$operatingSystemShort"
}

# Parse the command parameters
parseCommandLine() {
	local OPTIND opt a h v
	optstring=":a:hv"
	while getopts $optstring opt; do
		#echo "Command line option is ${opt}"
		case $opt in
			a) # -a awsProfile  Specify Amazon web service profile file
				awsProfile=$OPTARG
				;;
			h) # -h  Print the program usage
				printUsage
				exit 0
				;;
			v) # -v  Print the program version
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

# Print the program usage
printUsage() {
	echo ""
	echo "Usage:  $programName -a awsProfile"
	echo ""
	echo "Copy the GeoProcessor installer files to the Amazon S3 static website folder:"
	echo "  $s3FolderUrl"
	echo ""
	echo "-a awsProfile  Specify the Amazon profile to use for the upload."
	echo "-h             Print the usage."
	echo "-v             Print the version and copyright/license notice."
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
	echo '<title>GeoProcessor Downloads</title>' >> $indexHtmlTmpFile
	echo '</head>' >> $indexHtmlTmpFile
	echo '<body>' >> $indexHtmlTmpFile
	echo '<h1>Open Water Foundation GeoProcessor Software Downloads</h1>' >> $indexHtmlTmpFile
	echo '<p>' >> $indexHtmlTmpFile
	echo 'Install the GeoProcessor on Cygwin or Linux by downloading the <a href="download-gp.sh">download-gp.sh script</a> and running it in a Linux shell window.</p>' >> $indexHtmlTmpFile
	echo '<p>If clicking on the link does not download the file, right-click and use "Save link as..." (or similar).</p>' >> $indexHtmlTmpFile
	echo '</body>' >> $indexHtmlTmpFile
	echo '</html>' >> $indexHtmlTmpFile
	set -x
	aws s3 cp $indexHtmlTmpFile $s3IndexHtmlUrl ${dryrun} --profile "$awsProfile" ; errorCode=$?
	{ set +x; } 2> /dev/null
	if [ $errorCode -ne 0 ]; then
		echo ""
		echo "[Error] Error uploading index.html file."
		exit 1
	fi
}

# Upload local installer files to Amazon S3
# - includes the tar.gz file and catalog file used by download-gp.sh
uploadInstaller() {
	# The location of the installer is
	# ===========================================================================
	# Step 1. Upload the installer file for the current version
	#         - use copy to force upload
	echo "Uploading GeoProcessor installation file"
	set -x
	s3virtualenvGptestTargzUrl="${s3FolderUrl}/$gpVersion/$virtualenvGptestTargzFile"
	if [ ! -f "$virtualenvGptestTargzPath" ]; then
		echo ""
		echo "Installer file does not exist:  $virtualenvGptestTargzPath"
		exit 1
	fi
	aws s3 cp $virtualenvGptestTargzPath $s3virtualenvGptestTargzUrl ${dryrun} --profile "$awsProfile" ; errorCode=$?
	{ set +x; } 2> /dev/null
	if [ $errorCode -ne 0 ]; then
		echo ""
		echo "[Error] Error uploading GeoProcessor installer file."
		exit 1
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
	cat $tmpS3ListingPath | grep 'gp.*tar\.gz' > ${tmpS3CatalogPath}
	cat $tmpS3CatalogPath
	#
	# ===========================================================================
	# Step 3. Upload the catalog file so download software can use
	#         - for now upload in same format as generated by aws s3 ls command
	echo "Uploading catalog file"
	s3CatalogTxtFileUrl="${s3FolderUrl}/catalog.txt"
	set -x
	aws s3 cp $tmpS3CatalogPath $s3CatalogTxtFileUrl ${dryrun} --profile "$awsProfile" ; errorCode=$?
	{ set +x; } 2> /dev/null
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
	set -x
	aws s3 cp $buildUtilFolder/install/download-gp.sh $s3DownloadScriptUrl ${dryrun} --profile "$awsProfile" ; errorCode=$?
	{ set +x; } 2> /dev/null
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
programVersion="1.0.0"
programVersionDate="2018-12-26"

# Check the operating system
# - used to make logic decisions and for some file/folder names
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
# Folders for the virtual environment installer
virtualenvTmpFolder="${buildUtilFolder}/venv-tmp"
virtualenvGptestTargzPath="$virtualenvTmpFolder/gptest-${gpVersion}-${operatingSystemShort}-venv.tar.gz"
virtualenvGptestTargzFile=$(basename $virtualenvGptestTargzPath)
# TODO smalers 2018-12-26 enable QGIS and ArcGIS Pro GP installer
#virtualenvGpTargzFile="$virtualenvTmpFolder/gp-$gpVersion.tar.gz"

# Initialize data
# Set --dryrun to test before actually doing
dryrun=""
#dryrun="--dryrun"
# Root location where files are to be uploaded
s3FolderUrl="s3://software.openwaterfoundation.org/geoprocessor"
gpDownloadUrl="http://software.openwaterfoundation.org/geoprocessor"
awsProfile=""

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
