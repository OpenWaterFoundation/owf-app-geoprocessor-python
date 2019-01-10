@echo off
rem
rem 2-create-gp-venv.bat
rem
rem Create the Python virtualenv (venv) installer for the GeoProcessor
rem - creates the venv for Windows QGIS environment, also includes gptest
rem - this is less complicated than 2-create-gp-even.sh because files can be
rem   copied as is without having to strip QGIS files out

rem Get the folder where the script is located
rem - scriptFolder will have \ at the end
rem - works regardless of where the script/path is entered
set startingFolder=%CD%
set scriptFolder=%~dp0
echo scriptFolder=%scriptFolder%

rem If -z is specified, DO NOT zip the output
rem - this is used with the 2-update-gp-venv.bat
set doZip="yes"
if "%1%"=="-z" set doZip="no"
if "%2%"=="-z" set doZip="no"

rem Determine the GeoProcessor version file that includes line similar to:  app_version = "1.1.0"
rem - extract from the version.py file
rem - see useful commands:  https://www.dostips.com/DtTipsStringManipulation.php
echo.
echo Determining GeoProcessor version from version.py file
set gpTempFile=%TMP%\2-create-gp-venv.bat.tmp
rem The following will result in quoted version such as: "1.2.0dev"
findstr app_version %scriptFolder%..\geoprocessor\app\version.py | findstr /v _date > %gpTempFile%
set /p versionFullLine=<%gpTempFile%
echo versionFullLine=%versionFullLine%
rem Remove the leading app_version
set versionQuoted=%versionFullLine:app_version =%
set gpVersion=%versionQuoted:~3,-1%
echo.
echo GeoProcessor version determined to be:  %gpVersion%

rem Determine the base Python for the virtual environment
set basePython=python3

rem Set other folders
rem - need to dynamically determine the version
set venvTmpFolder=%scriptFolder%venv-tmp
set gpVenvFolderShort=gp-%gpVersion%-win-venv
set gpVenvFolder=%venvTmpFolder%\%gpVenvFolderShort%
set gpVenvSitePackagesFolder=%gpVenvFolder%\Lib\site-packages
set gpSrcFolder=%scriptFolder%..\geoprocessor
set scriptsFolder=%scriptFolder%..\Scripts
set gpVenvZipFileShort=gp-%gpVersion%-win-venv.zip

rem Running the script with -u command line option will skip the
rem virtual environment creation and just do the update
if "%1%"=="-u" goto copyGeoProcessorFiles
if "%2%"=="-u" goto copyGeoProcessorFiles

rem Create the version-specific virtual environment folder
if exist %gpVenvFolder% goto deleteGpVenvFolder
goto createGpVenv

:deleteGpVenvFolder
rem Delete the existing virtual environment folder
echo.
echo Deleting existing venv folder %gpVenvFolder%
rmdir /s/q %gpVenvFolder%
goto createGpVenv

:createGpVenvFolder
rem Create the new virtual environment folder
rem - not needed, delete when test out
echo.
echo Creating new venv folder %gpVenvFolder%
mkdir %gpVenvFolder%

:createGpVenv
rem Create the virtual environment using Python 3.7
rem - list in order of newest Python to oldest supported
echo.
echo Creating new venv in folder %gpVenvFolder%
if exist %USERPROFILE%\AppData\Local\Programs\Python\Python37\python.exe goto userPython37
if exist %USERPROFILE%\AppData\Local\Programs\Python\Python36\python.exe goto userPython36
goto noPythonForVenv
:userPython37
virtualenv -p %USERPROFILE%\AppData\Local\Programs\Python\Python37\python.exe %gpVenvFolder%
goto copyGeoProcessorFiles
:userPython36
virtualenv -p %USERPROFILE%\AppData\Local\Programs\Python\Python36\python.exe %gpVenvFolder%
goto copyGeoProcessorFiles

rem Change into the virtual environment, activate, and install packages
echo Changing to folder %gpVenvFolder%
cd "%gpVenvFolder%"
echo Activating the virtual environment
if not exist "Scripts\activate.bat" goto missingActivateScriptError
call Scripts\activate.bat
echo Installing necessary Python packages for deployed environment
pip3 install pandas
pip3 install openpyxl
pip3 install requests[security]
pip3 install SQLAlchemy
rem Deactivate the virtual environment
call Scripts\deactivate.bat

:copyGeoProcessorFiles
rem Copy the geoprocessor package files
rem - the `geoprocessor` folder is copied into the `Lib/site-packages` folder that was created above
rem - do not use * on source because the destination folder does not exist
echo.
echo Copying %gpSrcFolder% to %gpVenvSitePackagesFolder%\geoprocessor
robocopy %gpSrcFolder% %gpVenvSitePackagesFolder%\geoprocessor /E

rem Copy the scripts files
rem - the `Scripts` folder contents is copied into the `Scripts` folder that was created above
rem - copy specific Windows scripts, could be more precise but get it working
echo.
echo Copying %ScriptsFolder% to %gpVenvFolder%\Scripts
copy %scriptsFolder%\gp.bat %gpVenvFolder%\Scripts
copy %scriptsFolder%\gpui.bat %gpVenvFolder%\Scripts

rem Skip zipping if -z was specified on the command line
if %doZip%=="no" goto skipZip
rem Zip the files
rem - use 7zip.exe
echo.
echo Zipping the venv distribution...
set sevenZipExe=C:\Program Files\7-Zip\7z.exe
if exist "%sevenZipExe%" goto zipVenv
goto noSevenZip
:zipVenv
rem Zip the virtual environment folder
rem - change to the venv-tmp folder so zip will be relative
rem - also use filenames with no path to avoid issues with spaces in full path
echo.
echo Changing to folder %venvTmpFolder%
cd "%venvTmpFolder%"
rem Remove the old zip file if it exists
if exist %gpVenvZipFileShort% del /s/q %gpVenvZipFileShort%
rem Now create the new venv zip file
rem - need to be 
echo "Zipping up the virtual environment folder %gpVenvFolderShort% to create zip file %gpVenvZipFileShort%
"%sevenZipExe%" a -tzip %gpVenvZipFileShort% %gpVenvFolderShort%
rem Change back to script folder
cd "%startingFolder%"
echo.
echo Created zip file for deployment: %venvTmpFolder%\%gpVenvZipFileShort%
goto endZip
:skipZip
echo.
echo Skipping zip file creation because -z option specified.
goto endZip
:endZip
echo - Run gpui.bat in the virtual environment folder to run the GeoProcessor UI prior to deployment.
echo - Run 2-create-gp-venv.bat to fully create virtual environment and installer zip file for deployment.
echo - Run 3-copy-gp-to-amazon-s3.sh in Cygwin to upload the Windows and Cygwin installers.
exit /b 0

rem Error due to missing Scripts\activate.bat script
:missingActivateScriptError
echo.
echo "Missing %gpVenvFolder%\Scripts\activate.bat"
rem Change back to script folder
cd "%startingFolder%"
exit /b 1

rem Error conditions
rem No Python to create the virtual environment
:noPythonForVenv
echo.
echo No Python 3.6 or 3.7 was found to initialize the virtual environment
rem Change back to script folder
cd "%startingFolder%"
exit /b 1

:noSevenZip
rem No 7zip software
echo.
echo No %sevenZipExe% was found to zip the virtual environment
rem Change back to script folder
cd "%startingFolder%"
exit /b 1
