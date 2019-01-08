#!/bin/sh -x
(set -o igncr) 2>/dev/null && set -o igncr; # this comment is required
# The above line ensures that the script can be run on Cygwin/Linux even with Windows CRNL
#
# Copy the Windows gp installer the software.openwaterfoundation.org/geoprocessor folder.
# - replace all the files on the web with local files
# - must specify Amazon profile as argument to the script
# - this is a brute force approach that will be replaced with a more integrated approach similar to Cygwin and Linux

# Set --dryrun to test before actually doing
dryrun=""
#dryrun="--dryrun"
s3Folder="s3://software.openwaterfoundation.org/geoprocessor"

# Make sure that this is being run from the build-util folder
pwd=`pwd`
dirname=`basename ${pwd}`
if [ ! ${dirname} = "build-util" ]
        then
        echo "Must run from build-util folder"
        exit 1
fi

if [ "$1" == "" ]
	then
	echo ""
	echo "Usage:  $0 AmazonConfigProfile"
	echo ""
	echo "Copy the installer to the Amazon S3 static website folder:  $s3Folder"
	echo ""
	exit 0
fi

awsProfile="$1"

# Now copy the local file up to Amazon S3
aws s3 cp venv-tmp/gp-1.2.0dev-win-venv.zip ${s3Folder}/1.2.0dev/gp-1.2.0dev-win-venv.zip ${dryrun} --profile "$awsProfile"

exit $?
