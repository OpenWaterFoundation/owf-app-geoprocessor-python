#!/bin/sh
#
# Create the installers for the GeoProcessor
# - Create installer for production "gp"
# - Create installer for the "gptest" version used for functional testing
# - This approach does not yet use setup.py given some packaging complexities and need
#   to learn how to use setup.py

#------------------------------------------------------------------------------------------
# Step 0. Setup.
# Make sure that this script is being run from the build-util folder
pwd=`pwd`
dirname=`basename ${pwd}`
if [ ! "${dirname}" = "build-util" ]
	then
	echo "Must run from build-util folder"
	exit 1
fi
# Define top-level folders - everything is relative to this below to avoid confusion
projectFolder=`dirname ${pwd}`
buildUtilFolder="${pwd}"
buildFolder="${projectFolder}/build"
echo "Project (main) folder is ${projectFolder}"
echo "build-util folder is ${buildUtilFolder}"
echo "build folder is ${buildFolder}"

# Check to see if folders exist.  If not, something is probably wrong so don't continue.
if [ ! -d ${projectFolder} ]
	then
	echo "Something is wrong.  Project folder does not exist:  ${projecFolder}"
	exit 1
fi
if [ ! -d ${buildUtilFolder} ]
	then
	echo "Something is wrong.  build-util folder does not exist:  ${buildUtilFolder}"
	exit 1
fi
if [ ! -d ${buildFolder} ]
	then
	echo "Something is wrong.  build folder does not exist:  ${buildFolder}"
	exit 1
fi

#------------------------------------------------------------------------------------------
# These steps build the tar.gz installer for gptest,
# which is used for functional testing but has no QGIS code enabled.
#------------------------------------------------------------------------------------------
# Step 1. Copy all files to be distributed to a temporary folder

buildTmpGptestFolder="${buildFolder}/tmp-gptest"
if [ -d "${buildTmpGptestFolder}" ]
	then
	echo "Removing contents of temporary build temporary folder ${buildTmpGptestFolder} ..."
	rm -rf ${buildTmpGptestFolder}
fi

# Recreate the temporary folder

echo "Creating temporary build temporary folder ${buildTmpGptestFolder} ..."
mkdir ${buildTmpGptestFolder}

#------------------------------------------------------------------------------------------
# Step 2.  Copy GeoProcessor files to the temporary folder

echo "Copying GeoProcessor files to ${buildTmpGptestFolder} ..."
cp -rp ${projectFolder}/geoprocessor ${buildTmpGptestFolder}
cp -rp ${projectFolder}/scripts ${buildTmpGptestFolder}

#------------------------------------------------------------------------------------------
# Step 3. Update the temporary files to translate from full GeoProcessor to testing version
# - move the GeoProcessorCommandFactoryMin.py to GeoProcessorCommandFactory,
#   which will comment out QGIS imports and other command references
echo "Updating GeoProcessorCommandFactory.py file to version with QGIS commands commented out ..."
# Use sed instead of the class
#mv ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactoryMin.py ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
# Comment out the QGIS imports...
sed -i 's/^from geoprocessor.commands.layers/# from geoprocessor.commands.layers/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
# Comment out the QGIS commands in the registered_commands dictionary...
sed -i 's/"ADDGEOLAYERATTRIBUTE": /# "ADDGEOLAYERATTRIBUTE": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"CLIPGEOLAYER": /# "CLIPGEOLAYER": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"COPYGEOLAYER": /# "COPYGEOLAYER": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"CREATEGEOLAYERFROMGEOMETRY": /# "CREATEGEOLAYERFROMGEOMETRY": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"FREEGEOLAYER":/# "FREEGEOLAYER": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"MERGEGEOLAYERS": /# "MERGEGEOLAYERS": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"READGEOLAYERFROMDELIMITEDFILE": /# "READGEOLAYERFROMDELIMITEDFILE": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"READGEOLAYERFROMGEOJSON": /# "READGEOLAYERFROMGEOJSON": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"READGEOLAYERFROMSHAPEFILE": /# "READGEOLAYERFROMSHAPEFILE": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"READGEOLAYERSFROMFGDB": /# "READGEOLAYERSFROMFGDB": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"READGEOLAYERSFROMFOLDER": /# "READGEOLAYERSFROMFOLDER": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"REMOVEGEOLAYERATTRIBUTES": /# "REMOVEGEOLAYERATTRIBUTES": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"RENAMEGEOLAYERATTRIBUTE": /# "RENAMEGEOLAYERATTRIBUTE": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"SETGEOLAYERCRS": /# "SETGEOLAYERCRS": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"SETGEOLAYERPROPERTY": /# "SETGEOLAYERPROPERTY": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"SETPROPERTYFROMGEOLAYER": /# "SETPROPERTYFROMGEOLAYER": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"SIMPLIFYGEOLAYERGEOMETRY": /# "SIMPLIFYGEOLAYERGEOMETRY": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"WRITEGEOLAYERPROPERTIESTOFILE": /# "WRITEGEOLAYERPROPERTIESTOFILE": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"WRITEGEOLAYERTODELIMITEDFILE": /# "WRITEGEOLAYERTODELIMITEDFILE": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"WRITEGEOLAYERTOGEOJSON": /# "WRITEGEOLAYERTOGEOJSON": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/"WRITEGEOLAYERTOSHAPEFILE": /# "WRITEGEOLAYERTOSHAPEFILE": /g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
# Replace the QGIS command construction with pass...
sed -i 's/return AddGeoLayerAttribute/pass  # return AddGeoLayerAttribute/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return ClipGeoLayer/pass  # return ClipGeoLayer/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return CopyGeoLayer/pass  # return CopyGeoLayer/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return CreateGeoLayerFromGeometry/pass  # return CreateGeoLayerFromGeometry/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return FreeGeoLayer/pass  # return FreeGeoLayer/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return MergeGeoLayers/pass  # return MergeGeoLayers/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return ReadGeoLayerFromDelimitedFile/pass  # return ReadGeoLayerFromDelimitedFile/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return ReadGeoLayerFromGeoJSON/pass  # return ReadGeoLayerFromGeoJSON/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return ReadGeoLayerFromShapefile/pass  # return ReadGeoLayerFromShapefile/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return ReadGeoLayersFromFGDB/pass  # return ReadGeoLayersFromFGDB/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return ReadGeoLayersFromFolder/pass  # return ReadGeoLayersFromFolder/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return RemoveGeoLayerAttributes/pass  # return RemoveGeoLayerAttributes/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return RenameGeoLayerAttribute/pass  # return RenameGeoLayerAttribute/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return SetGeoLayerCRS/pass  # return SetGeoLayerCRS/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return SetGeoLayerProperty/pass  # return SetGeoLayerProperty/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return SetPropertyFromGeoLayer/pass  # return SetPropertyFromGeoLayer/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return SimplifyGeoLayerGeometry/pass  # return SimplifyGeoLayerGeometry/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return WriteGeoLayerPropertiesToFile/pass  # return WriteGeoLayerPropertiesToFile/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return WriteGeoLayerToDelimitedFile/pass  # return WriteGeoLayerToDelimitedFile/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return WriteGeoLayerToGeoJSON/pass  # return WriteGeoLayerToGeoJSON/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py
sed -i 's/return WriteGeoLayerToShapefile/pass  # return WriteGeoLayerToShapefile/g' ${buildTmpGptestFolder}/geoprocessor/core/GeoProcessorCommandFactory.py

# Update the geoprocessor/util/qgis_util.py module:
# - comment out lines that contain "from qgis.core import"
# - comment out lines that contain "from processing.core.Processing import""
# - comment out lines that contain "from PyQt4.QtCore import""
# - Could do on one line with chained sed commands but separate lines is more readable and can test separately.
echo "Updating geoprocessor/util/qgis_util.py to comment out QGIS module imports ..."
sed -i 's/^from qgis.core import/# from qgis.core import/g' ${buildTmpGptestFolder}/geoprocessor/util/qgis_util.py
sed -i 's/^from processing.core.Processing import/# from processing.core.Processing import/g' ${buildTmpGptestFolder}/geoprocessor/util/qgis_util.py
sed -i 's/^from PyQt4.QtCore import/# from PyQt4.QtCore import/g' ${buildTmpGptestFolder}/geoprocessor/util/qgis_util.py

# Update the geoprocessor/app/gp.py module:
# - comment out the call to qgis_util.initialize_qgis(...)
# - comment out the call to qgis_util.exit_qgis(...)
echo "Updating geoprocessor/app/gp.py to comment out QGIS initialize/stop calls ..."
sed -i 's/qgis_util.initialize_qgis/# qgis_util.initialize_qgis/g' ${buildTmpGptestFolder}/geoprocessor/app/gp.py
sed -i 's/qgis_util.exit_qgis/# qgis_util.exit_qgis/g' ${buildTmpGptestFolder}/geoprocessor/app/gp.py

#------------------------------------------------------------------------------------------
# Step 4. Tar up all the *.py files in the geoprocessor folder

gptestSitePackageBuildFile="${buildFolder}/gptest-site-package.tar"
gptestSitePackageBuildFileZ="${buildFolder}/gptest-site-package.tar.gz"

if [ -e "${gptestSitePackageBuildFileZ}" ]
	then
	echo "Removing existing build file ${gptestSitePackageBuildFileZ}"
	rm ${gptestSitePackageBuildFileZ}
fi

echo "Creating tar file containing *.py files ..."
cd "${buildTmpGptestFolder}"
find geoprocessor -name '*.py' -exec tar -rvf ${gptestSitePackageBuildFile} {} \;
if [ "$?" -ne 0 ]
	then
	echo "Error in script.  Exiting."
	exit $?
fi
echo "Zipping file ${gptestSitePackageBuildFile} into ${gptestSitePackageBuildFileZ}"
gzip ${gptestSitePackageBuildFile}
if [ "$?" -ne 0 ]
	then
	echo "Error in script.  Exiting."
	exit $?
fi

#------------------------------------------------------------------------------------------
# These steps build the tar.gz installer for gp, which is used for full QGIS integration.
#------------------------------------------------------------------------------------------
# Step 1. Copy all files to be distributed to a temporary folder

buildTmpGpFolder="${buildFolder}/tmp-gp"
if [ -d "${buildTmpGpFolder}" ]
	then
	echo "Removing contents of temporary build temporary folder ${buildTmpGpFolder} ..."
	rm -rf ${buildTmpGpFolder}
fi

# Recreate the temporary folder

echo "Creating temporary build temporary folder ${buildTmpGpFolder} ..."
mkdir ${buildTmpGpFolder}

#------------------------------------------------------------------------------------------
# Step 2.  Copy GeoProcessor files to the temporary folder

echo "Copying GeoProcessor files to ${buildTmpGpFolder} ..."
cp -rp ${projectFolder}/geoprocessor ${buildTmpGpFolder}
cp -rp ${projectFolder}/scripts ${buildTmpGpFolder}

#------------------------------------------------------------------------------------------
# Step 3. Update the temporary files for packaging
# - Unlike gptest, don't need to do anything since it is a full distribution

#------------------------------------------------------------------------------------------
# Step 4. Tar up all the *.py files in the geoprocessor folder

gpSitePackageBuildFile="${buildFolder}/gp-site-package.tar"
gpSitePackageBuildFileZ="${buildFolder}/gp-site-package.tar.gz"

if [ -e "${gpSitePackageBuildFileZ}" ]
	then
	echo "Removing existing build file ${gpSitePackageBuildFileZ}"
	rm ${gpSitePackageBuildFileZ}
fi

echo "Creating tar file containing *.py files ..."
cd "${buildTmpGpFolder}"
find geoprocessor -name '*.py' -exec tar -rvf ${gpSitePackageBuildFile} {} \;
if [ "$?" -ne 0 ]
	then
	echo "Error in script.  Exiting."
	exit $?
fi
echo "Zipping file ${gpSitePackageBuildFile} into ${gpSitePackageBuildFileZ}"
gzip ${gpSitePackageBuildFile}
if [ "$?" -ne 0 ]
	then
	echo "Error in script.  Exiting."
	exit $?
fi

echo "Install the files in the site-packages folder of the target Python 2.7 environment"
echo "- Remove the existing folder before installing to make sure the latest files are installed."

exit 0
