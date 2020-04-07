#!/bin/bash
#
# Create the GeoProcessor product 'index.html' page on Amazon S3,
# which serves as the main download page for the product.
# The installers that are listed are determined by listing the S3 bucket contents.
# The following files are created on the S3 bucket:
#
# software.openwaterfoundation.org/geoprocessor/index.html
# software.openwaterfoundation.org/geoprocessor/index.csv
#

# Supporting functions, alphabetized...

# Determine the operating system that is running the script
# - sets the variable operatingSystem to 'cygwin', 'linux', or 'mingw' (Git Bash)
# - sets the variable operatingSystemShort to 'cyg', 'lin', or 'min' (Git Bash)
checkOperatingSystem() {
  if [ ! -z "${operatingSystem}" ]; then
    # Have already checked operating system so return
    return
  fi
  operatingSystem="unknown"
  os=$(uname | tr [a-z] [A-Z])
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
  logInfo ""
  logInfo "Detected operatingSystem=$operatingSystem operatingSystemShort=$operatingSystemShort"
  logInfo ""
}

# Create a local catalog file by listing the S3 bucket contents
# - this is used to create the index.html
#
# 'aws ls' output similar to:
#   2018-12-04 16:16:22          0 geoprocessor/
#   2018-12-04 16:16:37          0 geoprocessor/1.0.0/
#   2018-12-04 16:17:19   46281975 geoprocessor/1.0.0/gptest-1.0.0-lin-venv.tar.gz
createCatalogFile() {
  logInfo "Creating catalog file from contents of Amazon S3 files"
  # For debugging...
  #set -x
  logInfo "Listing AWS S3 installers with:"
  logInfo "  aws s3 ls \"${s3FolderUrl}\" --profile \"${awsProfile}\" --recursive > ${tmpS3ListingPath}"
  aws s3 ls "${s3FolderUrl}" --profile "${awsProfile}" --recursive > ${tmpS3ListingPath}; errorCode=$?
  #{ set +x; } 2> /dev/null
  if [ ${errorCode} -ne 0 ]; then
    logError ""
    logError "Error listing GeoProcessor download files to create catalog (maybe missing --aws-profile)?"
    exit 1
  fi
  # Pull out the installers available for all platforms since the catalog
  # is used to download to all platforms.
  # - search for tar.gz and zip files
  tmpS3CatalogPath="/tmp/$USER-gp-catalog-ls-installers.txt"
  # Indicate whether current installer name spec, should be used
  # - use "no" to test creating all the index.html sections
  # - use "yes" once tested out and only want current standard used
  doCurrentSpec="no"
  if [ "${doCurrentSpec}" = "yes" ]; then
    # List all installers
    cat ${tmpS3ListingPath} | grep -E 'gp.*tar\.gz|gp.*.zip' | grep 'qgis-' > ${tmpS3CatalogPath}
    logInfo "Available GeoProcessor installers (current installer filename spec):"
  else
    # Only list installers that match the current download filename specification
    cat ${tmpS3ListingPath} | grep -E 'gp.*tar\.gz|gp.*.zip' > ${tmpS3CatalogPath}
    logInfo "Available GeoProcessor installers (all installers, even old filename spec):"
  fi
  cat ${tmpS3CatalogPath}
}

# Upload the index.html file for the download static website
# - this is basic at the moment but can be improved in the future such as
#   software.openwaterfoundation.org page, but for only one product, with list of variants and versions
createIndexHtmlFiles() {
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
  echo '   table {' >> $indexHtmlTmpFile
  echo '     border-collapse: collapse;' >> $indexHtmlTmpFile
  echo '     padding: 3px;' >> $indexHtmlTmpFile
  echo '   }' >> $indexHtmlTmpFile
  echo '   tr { border: none; }' >> $indexHtmlTmpFile
  echo '   th {' >> $indexHtmlTmpFile
  echo '     border-right: solid 1px;' >> $indexHtmlTmpFile
  echo '     border-left: solid 1px;' >> $indexHtmlTmpFile
  echo '     border-bottom: solid 1px;' >> $indexHtmlTmpFile
  echo '     padding: 3px;' >> $indexHtmlTmpFile
  echo '   }' >> $indexHtmlTmpFile
  echo '   td {' >> $indexHtmlTmpFile
  echo '     border-right: solid 1px;' >> $indexHtmlTmpFile
  echo '     border-left: solid 1px;' >> $indexHtmlTmpFile
  echo '     padding: 3px;' >> $indexHtmlTmpFile
  echo '   }' >> $indexHtmlTmpFile
  echo '</style>' >> $indexHtmlTmpFile
  echo '<title>GeoProcessor Downloads</title>' >> $indexHtmlTmpFile
  echo '</head>' >> $indexHtmlTmpFile
  echo '<body>' >> $indexHtmlTmpFile
  echo '<h1>Open Water Foundation GeoProcessor Software Downloads</h1>' >> $indexHtmlTmpFile
  echo '<p>' >> $indexHtmlTmpFile
  echo 'The GeoProcessor software is available for Windows, Cygwin and Linux, with primary focus currently on Windows.' >> $indexHtmlTmpFile
  echo 'See the latest <a href="http://software.openwaterfoundation.org/geoprocessor/latest/doc-user/appendix-install/install/">GeoProcessor installation documentation</a> for installation information (or follow a link below for specific version documentation).' >> $indexHtmlTmpFile
  echo '</p>' >> $indexHtmlTmpFile
  echo '<p>' >> $indexHtmlTmpFile
  echo '<ul>' >> $indexHtmlTmpFile
  echo '<li>Multiple versions of the GeoProcessor can be installed on a computer.' >> $indexHtmlTmpFile
  echo '<li>The GeoProcessor requires that QGIS is also installed:</li>' >> $indexHtmlTmpFile
  echo '    <ul>' >> $indexHtmlTmpFile
  echo '    <li>QGIS standalone installer is recommended because it installs versions in separate folders and menus.</li>' >> $indexHtmlTmpFile
  echo '    <li>The GeoProcessor installer name and table below indicates the QGIS version that is required for compatibility.</li>' >> $indexHtmlTmpFile
  echo '    <li>See <a href="https://qgis.org/en/site/forusers/download.html">Download QGIS</a>.</li>' >> $indexHtmlTmpFile
  echo '    <li>See <a href="http://learn.openwaterfoundation.org/owf-learn-qgis/install-qgis/install-qgis/">OWF Learn QGIS</a> documentation for additional information about installing QGIS.</li>' >> $indexHtmlTmpFile
  echo '    </ul>' >> $indexHtmlTmpFile
  echo '<li>Download files that include <code>dev</code> in the version are development versions that can be installed to see the latest features and bug fixes that are under development.</li>' >> $indexHtmlTmpFile
  echo '<li>Download files that include <code>cyg</code> in the filename are for Cygwin, <code>lin</code> are for Linux, and <code>win</code> are for Windows.</li>' >> $indexHtmlTmpFile
  echo '<li><b>If clicking on a file download link does not download the file, right-click on the link and use "Save link as..." (or similar).</b></li>' >> $indexHtmlTmpFile
  echo '</ul>' >> $indexHtmlTmpFile

  echo '<hr>' >> $indexHtmlTmpFile
  echo '<h2>Windows Download</h2>' >> $indexHtmlTmpFile
  echo '<p><b>The Windows version is under active development to implement major updates.  Older versions are listed for developers but will likely be removed when the latest Windows version is released.</b></p>' >> $indexHtmlTmpFile
  echo '<p><ol><li>Install the GeoProcessor on Windows by downloading a zip file and extracting to a folder in user files such as <code>C:\Users\user\gp-1.3.0-win-qgis-3.10-venv</code>.</li>' >> $indexHtmlTmpFile
  echo '<li>Then run <code>Scripts\gpui.bat</code> in a Windows command prompt window to start the GeoProcessor.</li></ol></p>' >> $indexHtmlTmpFile

  # Generate a table of available versions for Windows
  createIndexHtmlFile_Table win

  echo '<hr>' >> $indexHtmlTmpFile
  echo '<h2>Linux Download</h2>' >> $indexHtmlTmpFile
  echo '<p><b>Linux versions of GeoProcesor are currently not actively developed, pending finalizing the latest Windows release.</b></p>' >> $indexHtmlTmpFile
  echo '<p><ol><li>Install the GeoProcessor on Linux by downloading the <a href="download-gp.sh">download-gp.sh script</a> and running it in a shell window.' >> $indexHtmlTmpFile
  echo 'You will be prompted for options for where to install the software.</li>' >> $indexHtmlTmpFile
  echo '<li>Once installed, run the GeoProcessor using the <code>scripts/gpui</code> script in the install folder.</li></ol></p>' >> $indexHtmlTmpFile
  echo '<p><b>Do not download directly using files below (the list is provided as information and for developers).</b></p>' >> $indexHtmlTmpFile

  # Generate a table of available versions for Linux
  createIndexHtmlFile_Table lin

  echo '<hr>' >> $indexHtmlTmpFile
  echo '<h2>Cygwin Download</h2>' >> $indexHtmlTmpFile
  echo '<p><b>Cygwin versions of GeoProcesor are currently not actively developed, pending finalizing the latest Windows release.  Use the Windows version.</b></p>' >> $indexHtmlTmpFile
  echo '<p><ol><li>Install the GeoProcessor on Cygwin by downloading the <a href="download-gp.sh">download-gp.sh script</a> and running it in a shell window.' >> $indexHtmlTmpFile
  echo 'You will be prompted for options for where to install the software.</li>' >> $indexHtmlTmpFile
  echo '<li>Once installed, run the GeoProcessor using the <code>scripts/gpui</code> script in the install folder.</li></ol></p>' >> $indexHtmlTmpFile
  echo '<p><b>Do not download directly using files below (the list is provided as information and for developers).</b></p>' >> $indexHtmlTmpFile

  # Generate a table of available versions for Cygwin
  createIndexHtmlFile_Table cyg

  echo '</body>' >> $indexHtmlTmpFile
  echo '</html>' >> $indexHtmlTmpFile

  if [ "${operatingSystem}" = "cygwin" ]; then
    logInfo "On Cygwin, index.html file is:  ${indexHtmlTmpFile}"
    cygwinIndexHtmlTmpFile="C:\\cygwin64$(echo ${indexHtmlTmpFile} | tr '/' '\\')"
    # TODO smalers 2020-04-06 the Windows path is not guaranteed
    # - need to figure out how to run Windows program to check for existence
    logInfo "On Windows, index.html file is:  ${cygwinIndexHtmlTmpFile}"
  fi
}

# Create a table of downloads for an operating system to be used in the index.html file.
createIndexHtmlFile_Table() {
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
    # Use awk below to print the line with single space between tokens.
    # awk by default allows multiple spaces to be used.
    # Replace normal version to have -zzz at end and "dev" version to be "-dev" so that sort is correct,
    #   then change back to previous strings for output.
    # The use space as the delimiter and sort on the 3rd token.
    echo '<tr><th>Download File</th><th>Product</th><th>Version</th><th>File Timestamp (UTC)</th><th>Size (KB)</th><th>Operating System</th><th>QGIS Version</th><th>User Doc</th><th>Dev Doc</th></tr>' >> $indexHtmlTmpFile
    # Version before sort...
    # cat "${tmpS3CatalogPath}" | grep "${downloadOs}-" | sort -r | awk '
    cat "${tmpS3CatalogPath}" | grep "${downloadOs}-" | awk '{ printf "%s %s %s %s\n", $1, $2, $3, $4 }' | sed -E 's|([0-9][0-9]/)|\1-zzz|g' | sed 's|/-zzz|-zzz|g' | sed 's|dev|-dev|g' | sort -r -k4,4 | sed 's|-zzz||g' | sed 's|-dev|dev|g'  | awk '
      {
        # Download file is the full line
        downloadFileDate = $1
        downloadFileTime = $2
        downloadFileSize = $3
        downloadFilePath = $4
        # Split the download file path into parts to get the download file without path
        split(downloadFilePath,downloadFilePathParts,"/")
        # Split the download file into parts to get other information
        # - first determine the filename specification based on whether it contains "-qgis-" or not
        indexOfQgis = index(downloadFilePath, "-qgis-")
        fileSpecVersion = 2
        if ( indexOfQgis == 0 ) {
          # Does not contain "-qgis-" so assume version 1
          filenameSpecVersion = 1
        }
        downloadFile=""                   # Only the filename part of the file
        downloadFileProduct=""            # The product name (e.g., GeoProcessor)
        downloadFileOs=""                 # Operating system
        downloadFileQgisVersion="NA"      # QGIS version
        docUserUrl=""                     # User documentation URL
        docDevUrl=""                      # Developer documentation URL
        if ( filenameSpecVersion = 2 ) {
          # Second generation filename spec of format:  geoprocessor/1.3.0.dev/software/gp-1.3.0.dev-win-qgis-3.10-venv.zip
          # - has 'software' folder
          # - has '-qgis-version' for QGIS version
          downloadFile=downloadFilePathParts[4]
          # Split the download file into parts
          split(downloadFile,downloadFileParts,"-")
          downloadFileProduct=downloadFileParts[1]
          downloadFileVersion=downloadFileParts[2]
          downloadFileOs=downloadFileParts[3]
          downloadFileQgisVersion=downloadFileParts[5]
        }
        else if ( filenameSpecVersion = 1 ) {
          # First generation filename spec of format:  geoprocessor/1.2.0/gp-1.2.0-win-venv.zip
          # - no 'software' folder
          # - no '-qgis-version' for QGIS version
          downloadFile=downloadFilePathParts[3]
          # Split the download file into parts
          split(downloadFile,downloadFileParts,"-")
          downloadFileProduct=downloadFileParts[1]
          downloadFileVersion=downloadFileParts[2]
          downloadFileOs=downloadFileParts[3]
          downloadFileQgisVersion="NA"
        }
        # Set the URL to the download file
        downloadFileUrl=sprintf("http://software.openwaterfoundation.org/geoprocessor/%s/software/%s", downloadFileVersion, downloadFile)
        # Reset the short product name to full name
        product = ""
        if ( downloadFileProduct == "gp" ) {
          product = "GeoProcessor"
        }
        else if ( downloadFileProduct == "GP Test" ) {
          product = "GeoProcessor"
        }
        if ( downloadFileOs == "cyg" ) {
          downloadFileOs = "Cygwin"
        }
        else if ( downloadFileOs == "lin" ) {
          downloadFileOs = "Linux"
        }
        else if ( downloadFileOs == "win" ) {
          downloadFileOs = "Windows"
        }
        # Documentation URLs are based on the GeoProcessor version.
        # Documentation links for development and user documentation are only shown if exist
        # - the file returned by curl is actually the index.html file
        docDevUrl=sprintf("http://software.openwaterfoundation.org/geoprocessor/%s/doc-dev",downloadFileVersion)
        docDevCurl=sprintf("curl --output /dev/null --silent --head --fail \"%s\"",docDevUrl)
        returnStatus=system(docDevCurl)
        if ( returnStatus == 0 ) {
          docDevHtml=sprintf("<a href=\"%s\">View</a>",docDevUrl)
        }
        else {
          docDevHtml=""
        }
        docUserUrl=sprintf("http://software.openwaterfoundation.org/geoprocessor/%s/doc-user",downloadFileVersion)
        docDevCurl=sprintf("curl --output /dev/null --silent --head --fail \"%s\"",docUserUrl)
        returnStatus=system(docDevCurl)
        if ( returnStatus == 0 ) {
          docUserHtml=sprintf("<a href=\"%s\">View</a>",docUserUrl)
        }
        else {
          docUserHtml=""
        }
        # Old..
        # printf "<tr><td><a href=\"%s\"><code>%s</code></a></td><td>%s</td><td>%s</td><td>%s %s</td><td>%s</td></tr>", downloadFileUrl, downloadFile, downloadFileProduct, downloadFileVersion, downloadFileDate, downloadFileTime, downloadFileOs
        printf "<tr><td><a href=\"%s\"><code>%s</code></a></td><td>%s</td><td>%s</td><td>%s %s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>", downloadFileUrl, downloadFile, product, downloadFileVersion, downloadFileDate, downloadFileTime, downloadFileSize, downloadFileOs, downloadFileQgisVersion, docUserHtml, docDevHtml
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
        printf "<tr><td><a href=\"%s/%s\"><code>%s</code></a></td><td>%s</td><td>%s</td><td>%s</td></tr>", downloadFileUrl, downloadFile, downloadFile, downloadFileProduct, downloadFileVersion, downloadFileOs
      }' >> $indexHtmlTmpFile
  fi
  echo '</table>' >> $indexHtmlTmpFile
}

# Get the user's login.
# - Git Bash apparently does not set $USER environment variable, not an issue on Cygwin
# - Set USER as script variable only if environment variable is not already set
# - See: https://unix.stackexchange.com/questions/76354/who-sets-user-and-username-environment-variables
getUserLogin() {
  if [ -z "$USER" ]; then
    if [ ! -z "$LOGNAME" ]; then
      USER=$LOGNAME
    fi
  fi
  if [ -z "$USER" ]; then
    USER=$(logname)
  fi
  # Else - not critical since used for temporary files
}

# Echo to stderr
echoStderr() {
  # - if necessary, quote the string to be printed
  echo "$@" 1>&2
}

# Print a DEBUG message, currently prints to stderr.
logDebug() {
   echoStderr "[DEBUG] $@"
}

# Print an ERROR message, currently prints to stderr.
logError() {
   echoStderr "[ERROR] $@"
}

# Print an INFO message, currently prints to stderr.
logInfo() {
   echoStderr "[INFO] $@"
}

# Print an WARNING message, currently prints to stderr.
logWarning() {
   echoStderr "[WARNING] $@"
}

# Parse the command parameters
# - use the getopt command line program so long options can be handled
parseCommandLine() {
  # Single character options
  optstring="hv"
  # Long options
  optstringLong="aws-profile::,dryrun,help,noupload,version"
  # Parse the options using getopt command
  GETOPT_OUT=$(getopt --options $optstring --longoptions $optstringLong -- "$@")
  exitCode=$?
  if [ $exitCode -ne 0 ]; then
    # Error parsing the parameters such as unrecognized parameter
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
      --aws-profile) # --aws-profile=profile  Specify the AWS profile (use default)
        case "$2" in
          "") # Nothing specified so error
            logError "--aws-profile=profile is missing profile name"
            exit 1
            ;;
          *) # profile has been specified
            awsProfile=$2
            shift 2
            ;;
        esac
        ;;
      --dryrun) # --dryrun  Indicate to AWS commands to do a dryrun but not actually upload.
        logInfo "--dryrun dectected - will not change files on S3"
        dryrun="--dryrun"
        shift 1
        ;;
      -h|--help) # -h or --help  Print the program usage
        printUsage
        exit 0
        ;;
      --noupload) # --noupload  Indicate not upload to S3, just create the local files
        logInfo "--noupload dectected - will create local files but not change files on S3"
        doUpload="no"
        shift 1
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

# Print the usage to stderr
printUsage() {
  echoStderr ""
  echoStderr "Usage:  $scriptName"
  echoStderr ""
  echoStderr "Create the software.openwaterfoundation.org/geoprocessor/index.html and related files."
  echoStderr "This script can be run independent of a software installer upload."
  echoStderr "The installers that are listed in the index are those that exist on the S3 bucket."
  echoStderr ""
  echoStderr "--aws-profile=profile   Specify the Amazon profile to use for AWS credentials."
  echoStderr "--dryrun                Dry run (do not overwrite files on S3)."
  echoStderr "-h                      Print usage."
  echoStderr "--noupload              Create the index files but do not upload to S3."
  echoStderr "-v                      Print version."
  echoStderr ""
}

# Print the version to stderr
printVersion() {
  echoStderr ""
  echoStderr ${scriptName} ${scriptVersion} ${scriptVersionDate}
  echoStderr ""
  echoStderr "GeoProcessor"
  echoStderr "Copyright 2017-2020 Open Water Foundation."
  echoStderr ""
  echoStderr "License GPLv3+:  GNU GPL version 3 or later"
  echoStderr ""
  echoStderr "There is ABSOLUTELY NO WARRANTY; for details see the"
  echoStderr "'Disclaimer of Warranty' section of the GPLv3 license in the LICENSE file."
  echoStderr "This is free software: you are free to change and redistribute it"
  echoStderr "under the conditions of the GPLv3 license in the LICENSE file."
  echoStderr ""
}

# Upload index and related files between local and S3 locations
# - index.html
# - catalog.txt?
# - gp-download.sh
uploadIndexFiles() {
  # ===========================================================================
  # Step 1. Create and upload installer files
  #  - was done by 3-copy-gp-to-amazon.sh script and exist on S3
  logInfo "Assuming that GeoProcessor installer files were previously uploaded to S3."

  # ===========================================================================
  # Step 3. Upload the catalog file so download software can use
  #         - for now upload in same format as generated by aws s3 ls command
  logInfo "Uploading catalog file"
  s3CatalogTxtFileUrl="${s3FolderUrl}/catalog.txt"
  if [ -f "${s3CatalogTxtFileUrl}" ]; then
    # set -x
    aws s3 cp $tmpS3CatalogPath $s3CatalogTxtFileUrl ${dryrun} --profile "$awsProfile" ; errorCode=$?
    # { set +x; } 2> /dev/null
    if [ $errorCode -ne 0 ]; then
      logError ""
      logError "Error uploading GeoProcessor catalog file."
      # Not fatal
    fi
  else
    logWarning ""
    logWarning "Catalog file to upload does not exist:  ${tmpS3CatalogPath}"
    # Not fatal
  fi
 
  # ===========================================================================
  # Step 4. Upload the download-gp.sh script, which is needed to download
  logInfo "Uploading download-gp.sh script"
  s3DownloadScriptUrl="${s3FolderUrl}/download-gp.sh"
  if [ -f "${s3DownloadScriptUrl}" ]; then
    # set -x
    aws s3 cp $buildUtilFolder/install/download-gp.sh $s3DownloadScriptUrl ${dryrun} --profile "$awsProfile" ; errorCode=$?
    # { set +x; } 2> /dev/null
    if [ $errorCode -ne 0 ]; then
      logError ""
      logError "Error uploading download-gp.sh script file."
      # Not fatal
    fi
  else
    logWarning ""
    logWarning "Download script file to upload does not exist:  ${s3DownloadScriptUrl}"
    # Not fatal
  fi

  # ===========================================================================
  # Step 5. Upload the index.html file, which provides a way to navigate downloads
  #         - for now do a very simple html file but in the future may do vue.js
  #           similar to software.openwaterfoundation.org website
  logInfo "Uploading index.html script"
  if [ -f "${indexHtmlTmpFile}" ]; then
    # set -x
    aws s3 cp $indexHtmlTmpFile $s3IndexHtmlUrl ${dryrun} --profile "$awsProfile" ; errorCode=$?
    # { set +x; } 2> /dev/null
    if [ $errorCode -ne 0 ]; then
      logError ""
      logError "Error uploading index.html file."
      exit 1
    fi
  else
    logError ""
    logError "index.html file to upload does not exist:  ${indexHtmlFile}"
    exit 1
  fi
}

# Entry point for the script

# Get the location where this script is located since it may have been run from any folder
scriptFolder=$(cd $(dirname "$0") && pwd)
scriptName=$(basename $0)
repoFolder=$(dirname "${scriptFolder}")
scriptsFolder="${repoFolder}/scripts"
buildTmpFolder="${buildUtilFolder}/build-tmp"
# Get the current software version number from development environment files
# The geoprocessor/app/version.py file contains the version in parts so use 'gpversion' to extract.
# - format is like: 1.0.0
#                   1.0.0.dev
gpVersion=$(${scriptsFolder}/gpversion)
# Folder for the virtual environment installer
virtualenvTmpFolder="${buildUtilFolder}/venv-tmp"

scriptVersion="1.0.0"
scriptVersionDate="2020-04-06"

# Control debugging
debug=false

if [ "$debug" = "true" ]; then
  echo "scriptFolder=${scriptFolder}"
  echo "repoFolder=${repoFolder}"
  echo "srcFolder=${srcFolder}"
fi

# Default is not to do 'aws' dry run
# - override with --dryrun
dryrun=""

# Default is to upload
# - override with --noupload
doUpload="yes"

# Root AWS S3 location where files are to be uploaded
s3FolderUrl="s3://software.openwaterfoundation.org/geoprocessor"
gpDownloadUrl="http://software.openwaterfoundation.org/geoprocessor"

# File that contains output of `aws ls`, used to create catalog
# - user ID is used to help create more unique temporary files
user=""
tmpS3ListingPath="/tmp/$USER-gp-catalog-ls.txt"

# Parse the command line.
parseCommandLine "$@"

# Check the operating system
checkOperatingSystem

# This ensures that a user login is set, used to create unique temporary file names.
getUserLogin

# Create a list of available installers
createCatalogFile

# Create the 'index.html' and related files.
# TODO smalers 2020-04-06 disable for now
createIndexHtmlFiles

# Upload the 'index.html' and related files
# TODO smalers 2020-04-06 disable for now
doUpload="yes"
if [ "${doUpload}" = "yes" ]; then
  uploadIndexFiles
fi

exit $?
