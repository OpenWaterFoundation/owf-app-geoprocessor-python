@echo off
rem
rem 2-create-gp-venv.bat
rem
rem Create the Python virtualenv (venv) installer for the GeoProcessor
rem - creates the venv for Windows QGIS environment
rem - the resulting installer can be deployed to an operational environment

rem Use the following to make sure variables have expected values when parsed, such as in 'for' and complex logic
setlocal ENABLEDELAYEDEXPANSION

rem Turn on delayed expansion so that loops work
rem - Seems crazy but see:  https://ss64.com/nt/delayedexpansion.html
rem - Otherwise, for loops and ( ) blocks don't work because variables are not set as expected
rem - Such variables must be surrounded by ! !, rather than % %
set startingFolder=%CD%

rem Get the folder where the script is located (scriptFolder) and the repository folder (repoFolder)
rem - helpful example:  https://wiert.me/2011/08/30/batch-file-to-get-parent-directory-not-the-directory-of-the-batch-file-but-the-parent-of-that-directory/
rem - scriptFolder will have \ at the end
rem - works regardless of where the script/path is entered
set scriptName=%~nx0
set scriptFolder=%~dp0
rem Remove trailing \ from scriptFolder
set scriptFolder=%scriptFolder:~0,-1%
rem Windows ugly way of getting parent folder:
for %%d in (%scriptFolder%) do set repoFolder=%%~dpd
rem Remove trailing \ from repoFolder
set repoFolder=%repoFolder:~0,-1%

echo scriptName=%scriptName%
echo scriptFolder=%scriptFolder%
echo repoFolder=%repoFolder%

set versionNum=1.2.0
set versionDate=2020-04-02

rem Check command line parameters.

if "%1%"=="-h" goto printUsage
if "%1%"=="/h" goto printUsage
if "%2%"=="-h" goto printUsage
if "%2%"=="/h" goto printUsage

if "%1%"=="-v" goto printVersion
if "%1%"=="/v" goto printVersion
if "%2%"=="-v" goto printVersion
if "%2%"=="/v" goto printVersion

rem  - if --nozip is specified, DO NOT zip the output (used with 2-update-gp-venv.bat)
set doZip=yes
if "%1%"=="--nozip" (
  echo Detected running with -nozip, will NOT create zip file.
  set doZip=no
)
if "%2%"=="--nozip" (
  echo Detected running with -nozip, will NOT create zip file.
  set doZip=no
)
if "%doZip%"=="yes" (
  echo WILL create zip file installer at the end
)

rem Running the script with -u command line option will skip creating the
rem virtual environment and just do the update from current source files.
set doUpdateFilesOnly=no
if "%1%"=="-u" (
  echo Detected running with -u, will copy current GeoProcessor files but not create venv
  set doUpdateFilesOnly=yes
)
if "%2%"=="-u" (
  echo Detected running with -u, will copy current GeoProcessor files but not create venv
  set doUpdateFilesOnly=yes
)

rem Python type to use for virtual environment
rem - default is to use QGIS
set venvPythonType=qgis
if "%1%"=="--python-dev" (
  echo Detected running with --python-dev, will use development environment Python for venv
  set venvPythonType=dev
)
if "%2%"=="--python-dev" (
  echo Detected running with --python-dev, will use development environment Python for venv
  set venvPythonType=dev
)
if "%1%"=="--python-qgis" (
  echo Detected running with --python-qgis, will use QGIS Python for venv
  set venvPythonType=qgis
)
if "%2%"=="--python-qgis" (
  echo Detected running with --python-qgis, will use QGIS Python for venv
  set venvPythonType=qgis
)
if "%1%"=="--python-sys" (
  echo Detected running with --python-sys, will use system [py] Python for venv
  set venvPythonType=sys
)
if "%2%"=="--python-sys" (
  echo Detected running with --python-sys, will use system [py] Python for venv
  set venvPythonType=sys
)

rem Virtual environment type to use for virtual environment
rem - default is to use virtualenv
set venvType=virtualenv
if "%1%"=="--venv" (
  echo Detected running with --venv, will use 'venv' module to create venv
  set venvType=venv
)
if "%2%"=="--venv" (
  echo Detected running with --venv, will use 'venv' module to create venv
  set venvType=venv
)
if "%1%"=="--virtualenv" (
  echo Detected running with --virtualenv, will use 'virtualenv' module to create venv
  set venvType=virtualenv
)
if "%2%"=="--virtualenv" (
  echo Detected running with --virtualenv, will use 'virtualenv' module to create venv
  set venvType=virtualenv
)

rem Determine the GeoProcessor version file that includes line similar to:  app_version = "1.1.0"
rem - extract from the version.py file using a Cygwin script
echo.
echo Determining GeoProcessor version from version.py file by running gpversion
set gpTempFile=%TMP%\2-create-gp-venv.bat.tmp

rem TODO smalers 2020-04-01 For now call a cygwin script to get the version
rem - need to figure out a purely-bat approach but don't have time right now
rem - for now hard code to only work if run standard GeoProcessor development environment,
rem   for example:  C:\Users\user\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python
rem Use the following to confirm file locations
rem - issue, cygwin /home is not /cygdrive/C/Users
rem TODO smalers 2020-04-01 hard-code these for now but need to have a way specify on command line and do cross checks.
rem - GeoProcessor version is determined dynamically from the current source files
set gpVersion=unknown
set qgisTargetVersion=3.10
set pythonVersion=37
C:\cygwin64\bin\bash --login -c "echo HOME=$HOME"
C:\cygwin64\bin\bash --login -c "echo USER=$USER"
C:\cygwin64\bin\bash --login -c "echo $(pwd)"
C:\cygwin64\bin\bash --login -c "/cygdrive/C/Users/%USERNAME%/owf-dev/GeoProcessor/git-repos/owf-app-geoprocessor-python/scripts/gpversion" > %gpTempFile%
set /p gpVersion=<%gpTempFile%

rem Must query the parts of the version because the full version is created from parts at runtime.
rem The following will result in quoted version such as: "1.2.0dev"
rem findstr /b app_version_major %scriptFolder%\..\geoprocessor\app\version.py > %gpTempFile%
rem set /p versionMajor=<%gpTempFile%
rem findstr /b app_version_minor %scriptFolder%\..\geoprocessor\app\version.py > %gpTempFile%
rem set /p versionMinor=<%gpTempFile%
rem findstr /b app_version_micro %scriptFolder%\..\geoprocessor\app\version.py > %gpTempFile%
rem set /p versionMicro=<%gpTempFile%
rem findstr /b app_version_mod %scriptFolder%\..\geoprocessor\app\version.py > %gpTempFile%
rem set /p versionMod=<%gpTempFile%
rem set versionFullLine=%versionMajor%.%versionMinor%.%versionMicro%.%versionMod%
rem if "%versionMod%"=="" set versionFullLine=%versionMajor%.%versionMinor%.%versionMicro%

rem echo versionFullLine=%versionFullLine%
rem rem Remove the leading app_version
rem set versionQuoted=%versionFullLine:app_version =%
rem set gpVersion=%versionQuoted:~3,-1%
echo.
echo GeoProcessor version determined to be:  %gpVersion%

rem Do some checks here to make sure that valid version information is specified
if "%gpVersion%"=="unknown" (
  echo.
  echo GeoProcessor version is unknown.  Cannot create installer.
  goto exit1
)
if "!qgisTargetVersion!"=="unknown" (
  echo.
  echo QGIS target version is unknown.  Cannot create installer.
  goto exit1
)
if "%pythonVersion%"=="unknown" (
  echo.
  echo Python version is unknown.  Cannot create installer.
  goto exit1
)

rem Set the folders for builds
rem   gpVenvTmpFolder = general work folder for builds, under which versioned builds will be created (... venv-tmp)
rem     gpVenvFolderShort = GeoProcessor installer file name (no leading path, like: gp-1.3.0-win-qgis-3.10-venv)
rem     gpVenvFolder = full path to folder for specific installer venv (... venv-tmp/gp-1.3.0-win-qgis-3.10-venv)
rem       gpVenvSitePackagesFolder = path to venv 'Lib\site-packages' folder
rem     gpVenvZipFileShort = name of installer zip file without leading path (like: gp-1.3.0-win-qgis-3.10-venv.zip)
rem     gpQgisVersionFile = filename used to store QGIS version for installer
rem
rem   devVenvFolder = path to development venv (like:  ... venv/venv-qgis-3.10-python37)
rem     devPythonExe = path to development venv exe (like:  venv/venv-qgis-3.10-python37/Scripts/python.exe)
rem   gpSrcFolder = path to source geoprocessor Python files (will be copied into venv 'Lib/site-packages' folder)
rem   scriptsFolder = path to source scripts files (will be copied into venv 'Scripts' folder)
rem
rem   qgisFolder = location where QGIS is installed (like:  C:\Program Files\QGIS 3.10)
rem   qgisPythonFolder = location of QGIS Python for venv base interpreter (like:  C:\Program Files\QGIS 3.10\apps\Python37)
rem   qgisPythonExe = location of QGIS Python executable for venv base interpreter (like:  C:\Program Files\QGIS 3.10\apps\Python37\python.exe)

rem -- venv being created --
set gpVenvTmpFolder=%scriptFolder%\venv-tmp
rem Old-style venv folder name did not have QGIS version
rem New-style venv folder includes QGIS version, which can be used to determine the Python version
rem set gpVenvFolderShort=gp-%gpVersion%-win-qgis-%qgisTargetVersion%-venv
set gpVenvFolderShort=gp-%gpVersion%-win-qgis-%qgisTargetVersion%-venv
set gpVenvFolder=%gpVenvTmpFolder%\%gpVenvFolderShort%
set gpVenvSitePackagesFolder=%gpVenvFolder%\Lib\site-packages
set gpVenvZipFileShort=gp-%gpVersion%-win-qgis-%qgisTargetVersion%-venv.zip
set gpVenvCreationLogFile=%gpVenvFolder%\venv-creation.log
set gpVenvCreationLogFile0=%gpVenvTmpFolder%\venv-creation.log
rem -- source files to copy into venv, and Python used to run 'virtualenv' and 'venv' --
set gpSrcFolder=%repoFolder%\geoprocessor
set scriptsFolder=%repoFolder%\scripts
set gpQgisVersionFileWithPath=%gpVenvFolder%\GeoProcessor-QGIS-Version.txt
set readmeWithPath=%repoFolder%\resources\runtime\README.txt
set licenseWithPath=%repoFolder%\LICENSE.md
set devVenvFolder=%repoFolder%\venv\venv-qgis-%qgisTargetVersion%-python%pythonVersion%
set devPythonExe=%devVenvFolder%\Scripts\python.exe
rem -- QGIS files for base Python interpreter --
set qgisFolder=C:\Program Files\QGIS %qgisTargetVersion%
set qgisPythonFolder=%qgisFolder%\apps\Python37
set qgisPythonExe=%qgisFolder%\apps\Python37\python.exe

echo.
echo Controlling configuration properties:
echo -- version information --
echo gpVersion=%gpVersion%
echo qgisTargetVersion=%qgisTargetVersion%
echo pythonVersion=%pythonVersion%
echo -- venv being created --
echo gpVenvTmpFolder=%gpVenvTmpFolder%
echo gpVenvFolderShort=%gpVenvFolderShort%
echo gpVenvFolder=%gpVenvFolder%
echo gpVenvSitePackagesFolder=%gpVenvSitePackagesFolder%
echo gpVenvZipFileShort=%gpVenvZipFileShort%
echo gpVenvCreationLogFile=%gpVenvCreationLogFile%
echo gpVenvCreationLogFile0=%gpVenvCreationLogFile0%
echo -- source files to copy into venv, and Python used to run 'virtualenv' and 'venv' --
echo gpSrcFolder=%gpSrcFolder%
echo scriptsFolder=%scriptsFolder%
echo gpQgisVersionFileWithPath=%gpQgisVersionFileWithPath%
echo readmeWithPath=%readmeWithPath%
echo licenseWithPath=%licenseWithPath%
echo devVenvFolder=%devVenvFolder%
echo devPythonExe=%devPythonExe%
echo -- QGIS files for base Python interpreter --
echo qgisFolder=%qgisFolder%
echo qgisPythonFolder=%qgisPythonFolder%
echo qgisPythonExe=%qgisPythonExe%
echo.
rem Prompt is different whether -u was specified on command line
if "%doUpdateFilesOnly%"=="yes" (
  set /p answer2="Continue updating existing venv [y/q]? "
) else (
  set /p answer2="Continue creating new venv [y/q]? "
)
if not "%answer2%"=="y" (
  goto exit0
)

rem Running the script with -u command line option will skip creating the
rem virtual environment and just do the update from current source files.
if "%doUpdateFilesOnly%"=="yes" (
  echo Running with -u, skipping to file copy but not creating venv
  goto copyGeoProcessorFiles
)

rem Create the version-specific virtual environment folder
if exist "%gpVenvFolder%" goto deleteGpVenvFolder
goto createGpVenv

:deleteGpVenvFolder

rem Delete the existing virtual environment folder
echo.
echo Deleting old installer venv folder:  %gpVenvFolder%
set /p answer="Delete old installer venv folder and continue [y/q]? "
if not "%answer%"=="y" (
  goto exit0
)
rmdir /s/q %gpVenvFolder%
goto createGpVenv

:createGpVenvFolder

rem Create the new virtual environment folder
rem - not needed, delete when test out
echo.
echo Creating new venv folder:  %gpVenvFolder%
mkdir %gpVenvFolder%

:createGpVenv

rem Initialize a virtual environment by using a combination that works
rem - TODO smalers 2020-04-02 for some reason, this has been an issue of late so add batch file options to test
rem - maybe it was because the batch file was using virtualenv rather than venv?

if "!venvType!"=="venv" (
  goto doVenv
) else (
    if "!venvType!"=="virtualenv" (
      goto doVirtualenv
    ) else (
        echo.
        echo Virtual environment type '!venvType!' is not recognized.  Exiting.
        goto exit1
      )
  )

:doVenv

echo.
echo Use venv to create the virtual environment.
rem   Which Python type:
rem      Dev = PyCharm development venv (Scripts\python.exe)
rem      Qgis = standalone QGIS (*:\Program Files\QGIS 3.10\aps\Python37\python.exe)
rem      User = User-installed Python (typically AppData...Scripts\python.exe)
rem
rem For logging, have to log to an initial log file and because the receiving folder does not exist.
rem Then copy this initial log below and continue writing to it.
echo The following major steps were used to create the initial Python virtual environment.>"%gpVenvCreationLogFile0%"
echo Subsequent changes to the virtual environment are not recorded here.>>"%gpVenvCreationLogFile0%"
echo Using virtual environment type:  %venvType%
echo Using virtual environment type:  %venvType%>>"%gpVenvCreationLogFile0%"
echo Using virtual environment python type:  %venvPythonType%
echo Using virtual environment python type:  %venvPythonType%>>"%gpVenvCreationLogFile0%"
if "!venvPythonType!"=="dev" (
  rem TODO smalers 2020-04-01 Use the development environment Python
  echo Creating virtual environment using development environment Python:  %devPythonExe%
  echo Creating virtual environment using development environment Python:  %devPythonExe%>>"%gpVenvCreationLogFile0%"
  echo.
  echo Checking for development venv python.exe to create new venv:  %devPythonExe%
  echo Checking for development venv python.exe to create new venv:  %devPythonExe%>>"%gpVenvCreationLogFile0%"
  if not exist "%devPythonExe%" goto noDevPythonExe
  "%devPythonExe%" -m venv "%gpVenvFolder%"
  rem Run Dev Python
  rem Update the creation log so know how the venv was created
  echo "%devPythonExe%" -m venv "%gpVenvFolder%">>"%gpVenvCreationLogFile0%"
) else (
    if "!venvPythonType!"=="qgis" (
      rem TODO smalers 2020-04-01 Use the development environment Python
      echo Creating virtual environment using QGIS Python:  %qgisPythonExe%
      echo Creating virtual environment using QGIS Python:  %qgisPythonExe%>>"%gpVenvCreationLogFile0%"
      echo.
      echo Checking for existence of QGIS Python:  %qgisPythonExe%
      echo Checking for existence of QGIS Python:  %qgisPythonExe%>>"%gpVenvCreationLogFile0%"
      if not exist "%qgisPythonExe%" goto noQgisPythonExe

      "%qgisPythonExe%" -m venv "%gpVenvFolder%"
      rem Run Dev Python
      rem Update the creation log so know how the venv was created
      echo "%qgisPythonExe%" -m venv "%gpVenvFolder%">>"%gpVenvCreationLogFile0%"
    ) else (
        if "!venvPythonType!"=="sys" (
          set pythonDotVersion=3.7
          rem Not needed
          rem set userPythonExe=%USERPROFILE%\AppData\Local\Programs\Python\Python37\python.exe
          echo Creating virtual environment using system 'py' Python.
          echo Creating virtual environment using system 'py' Python>>"%gpVenvCreationLogFile0%"

          rem Use a user Python for base interpreter, which will be used to install additional packages
          echo py -!pythonDotVersion! -m venv "%gpVenvFolder%"
          echo py -!pythonDotVersion! -m venv "%gpVenvFolder%">>"%gpVenvCreationLogFile0%"
          py -!pythonDotVersion! -m venv "%gpVenvFolder%"
        ) else (
            rem Fall through case that is not handled
            echo Requested Python type !venvPythonType! for venv is not recognized.  Unable to create virtual environment.
            echo Requested Python type !venvPythonType! for venv is not recognized.  Unable to create virtual environment.>>"%gpVenvCreationLogFile0%"
            goto exit1
          )
      )
  )
echo Done creating Python venv using 'venv' module.
echo Done creating Python venv using 'venv' module.>>"%gpVenvCreationLogFile0%"
goto copyGeoProcessorFiles

:doVirtualenv

rem Use virtualenv to create the virtual environment
echo.
rem   Which Python type:
rem      Dev = PyCharm development venv (Scripts\python.exe)
rem      Qgis = standalone QGIS (*:\Program Files\QGIS 3.10\aps\Python37\python.exe)
rem      User = User-installed Python (typically AppData...Scripts\python.exe)
rem
rem For logging, have to log to an initial log file and because the receiving folder does not exist.
rem Then copy this initial log below and continue writing to it.
echo The following major steps were used to create the initial Python virtual environment.>"%gpVenvCreationLogFile0%"
echo Subsequent changes to the virtual environment are not recorded here.>>"%gpVenvCreationLogFile0%"
echo Using virtual environment type:  %venvType%
echo Using virtual environment type:  %venvType%>>"%gpVenvCreationLogFile0%"
echo Using virtual environment python type:  %venvPythonType%
echo Using virtual environment python type:  %venvPythonType%>>"%gpVenvCreationLogFile0%"
if "!venvPythonType!"=="dev" (
  rem TODO smalers 2020-04-01 Use the development environment Python
  echo Creating virtual environment using development environment Python:  %devPythonExe%
  echo Creating virtual environment using development environment Python:  %devPythonExe%>>"%gpVenvCreationLogFile0%"
  echo.
  echo Checking for development venv python.exe to create new venv:  %devPythonExe%
  echo Checking for development venv python.exe to create new venv:  %devPythonExe%>>"%gpVenvCreationLogFile0%"
  if not exist "%devPythonExe%" goto noDevPythonExe
  echo "%devPythonExe%" -m virtualenv "%gpVenvFolder%"
  "%devPythonExe%" -m virtualenv "%gpVenvFolder%"
  rem Run Dev Python
  rem Update the creation log so know how the venv was created
  echo "%devPythonExe%" -m virtualenv "%gpVenvFolder%">>"%gpVenvCreationLogFile0%"
) else (
    if "!venvPythonType!"=="qgis" (
      rem TODO smalers 2020-04-01 Use the development environment Python
      echo Creating virtual environment using QGIS Python:  %qgisPythonExe%
      echo Creating virtual environment using QGIS Python:  %qgisPythonExe%>>"%gpVenvCreationLogFile0%"

      echo.
      echo Checking for existence of QGIS Python:  %qgisPythonExe%
      if not exist "%qgisPythonExe%" goto noQgisPythonExe
      echo "%qgisPythonExe%" -m virtualenv "%gpVenvFolder%"
      "%qgisPythonExe%" -m virtualenv "%gpVenvFolder%"
      rem Run Dev Python
      rem Update the creation log so know how the venv was created
      echo "%qgisPythonExe%" -m virtualenv "%gpVenvFolder%">>"%gpVenvCreationLogFile0%"
    ) else (
        if "!venvPythonType!"=="sys" (
          set pythonDotVersion=3.7
          rem Not needed
          rem set userPythonExe=%USERPROFILE%\AppData\Local\Programs\Python\Python37\python.exe
          echo Creating virtual environment using system 'py' Python.
          echo Creating virtual environment using system 'py' Python>>"%gpVenvCreationLogFile0%"

          rem Use a user Python for base interpreter, which will be used to install additional packages
          echo py -!pythonDotVersion! -m virtualenv "%gpVenvFolder%"
          echo py -!pythonDotVersion! -m virtualenv "%gpVenvFolder%">>"%gpVenvCreationLogFile0%"
          py -!pythonDotVersion! -m virtualenv "%gpVenvFolder%"
        ) else (
            rem Fall through case that is not handled
            echo Requested Python type !venvPythonType! for venv is not recognized.  Unable to create virtual environment.
            echo Requested Python type !venvPythonType! for venv is not recognized.  Unable to create virtual environment.>>"%gpVenvCreationLogFile0%"
            goto exit1
          )
      )
  )
echo Done creating Python venv using 'virtualenv' module.
echo Done creating Python venv using 'virtualenv' module.>>"%gpVenvCreationLogFile0%"
rem goto copyGeoProcessorFiles

:copyGeoProcessorFiles

rem Copy the geoprocessor package files
rem - the `geoprocessor` folder is copied into the `Lib/site-packages` folder that was created above
rem - do not use * on source because the destination folder does not exist
rem - do this before running pip for additional packages so that the printenv.py script can be run within
rem   activated venv environment

rem Above log messages could not write the venv folder because it did not exist.
rem Now, copy the initial log into the venv and then append to the final log file.
copy "%gpVenvCreationLogFile0%" "%gpVenvCreationLogFile%"

echo.
echo Copying GeoProcessor development files to venv
echo Copying GeoProcessor development files to venv>>"%gpVenvCreationLogFile%"
echo Copying %gpSrcFolder% to %gpVenvSitePackagesFolder%\geoprocessor
echo Copying %gpSrcFolder% to %gpVenvSitePackagesFolder%\geoprocessor>>"%gpVenvCreationLogFile%"
echo robocopy %gpSrcFolder% %gpVenvSitePackagesFolder%\geoprocessor /E
echo robocopy %gpSrcFolder% %gpVenvSitePackagesFolder%\geoprocessor /E>>"%gpVenvCreationLogFile%"
robocopy %gpSrcFolder% %gpVenvSitePackagesFolder%\geoprocessor /E

rem Copy the scripts files
rem - the `Scripts` folder contents is copied into the `Scripts` folder that was created above
rem - copy specific Windows scripts, could be more precise but get it working
echo.
echo Copying gp.bat and gpui.bat from %ScriptsFolder% to %gpVenvFolder%\Scripts
echo Copying gp.bat and gpui.bat from %ScriptsFolder% to %gpVenvFolder%\Scripts>>"%gpVenvCreationLogFile%"
copy %scriptsFolder%\gp.bat %gpVenvFolder%\Scripts
copy %scriptsFolder%\gpui.bat %gpVenvFolder%\Scripts

rem Create the file that contains the QGIS version
echo Creating version info file:  %gpQgisVersionFileWithPath%
echo Creating version info file:  %gpQgisVersionFileWithPath%>>"%gpVenvCreationLogFile%"
echo # This file is created by the GeoProcessor installer build batch file - DO NOT EDIT THIS FILE.> %gpQgisVersionFileWithPath%
echo #>> %gpQgisVersionFileWithPath%
echo # This file indicates the stand-alone QGIS version that was used to build the GeoProcessor installer.>> %gpQgisVersionFileWithPath%
echo # The GeoProcessor QGIS version should agree with the stand-alone QGIS this is available.>> %gpQgisVersionFileWithPath%
echo # The gp.bat batch files will check for this file in order to ensure that the runtime environment is correct.>> %gpQgisVersionFileWithPath%
echo # The version is the Major.Minor version corresponding to QGIS "C:\Program Files\QGIS Major.Minor" folder.>> %gpQgisVersionFileWithPath%
echo #>> %gpQgisVersionFileWithPath%
echo %qgisTargetVersion%>> %gpQgisVersionFileWithPath%

rem Copy the README file into the main venv folder
echo Copying the main README file: %readmeWithPath%
echo Copying the main README file: %readmeWithPath%>>"%gpVenvCreationLogFile%"
copy %readmeWithPath% %gpVenvFolder%

rem Copy the LICENSE file into the main venv folder
echo Copying the LICENSE file: %licenseWithPath%
echo Copying the LICENSE file: %licenseWithPath%>>"%gpVenvCreationLogFile%"
copy %licenseWithPath% %gpVenvFolder%

if "%doUpdateFilesOnly%"=="yes" (
  goto finalMessage
)

:installAdditionalPackages

rem Change into the virtual environment, activate, and install additional packages
rem - Note that the venv (and virtualenv) packages 'activate' and 'deactivate' have hard-coded
rem   lines to the path where the venv was originally created by this batch file.
rem   It needs to be changed in the operational environment if the venv is to be activated,
rem   but this NOT NEEDED to run the GeoProcessor because the gp.bat script sets its own
rem   PYTHONHOME and PYTHONPATH.
echo Changing to folder %gpVenvFolder%
echo Changing to folder %gpVenvFolder%>>"%gpVenvCreationLogFile%"
cd "%gpVenvFolder%"
echo Activating the virtual environment
echo Activating the virtual environment>>"%gpVenvCreationLogFile%"
if not exist "Scripts\activate.bat" goto missingActivateScriptError
call Scripts\activate.bat
rem Make sure that SSL libraries are available to allow pip to work
rem - they seem to not be automatically created in a new venv
rem - they exist in the development venv because pip required for additional packages
rem - seems like these live in DLLs folder in Widows Python but virtualenv does not have
rem - the dlls are removed later because they break the run-time distribution
rem - see clues:  https://github.com/numpy/numpy/issues/12667
set repoCryptoLib=%repoFolder%\resources\installer\win\ssl\libcrypto-1_1-x64.dll
set repoSslLib=%repoFolder%\resources\installer\win\ssl\libssl-1_1-x64.dll
set venvCryptoLib=%gpVenvFolder%\Scripts\libcrypto-1_1-x64.dll
set venvSslLib=%gpVenvFolder%\Scripts\libssl-1_1-x64.dll
if not exist "%gpVenvFolder%\Scripts\libcrypto-1_1-x64.dll" (
  echo Copying libcrypto-1_1-x64.dll from dev to new venv so pip SSL/TLS will work: %repoCryptoLib%
  echo Copying libcrypto-1_1-x64.dll from dev to new venv so pip SSL/TLS will work>>"%gpVenvCreationLogFile%"
  copy "%repoCryptoLib%" "%gpVenvFolder%\Scripts"
  echo copy "%repoCryptoLib%" "%gpVenvFolder%\Scripts">>"%gpVenvCreationLogFile%"
)
if not exist "%gpVenvFolder%\Scripts\libssl-1_1-x64.dll" (
  echo Copying libssl-1_1-x64.dll from dev to new venv so pip SSL/TLS will work: %repoSslLib%
  echo Copying libssl-1_1-x64.dll from dev to new venv so pip SSL/TLS will work>>"%gpVenvCreationLogFile%"
  copy "%repoSslLib%" "%gpVenvFolder%\Scripts"
  echo copy "%repoSslLib%" "%gpVenvFolder%\Scripts">>"%gpVenvCreationLogFile%"
)
rem The following use generic Python name (not py) because
rem the virtual environment uses the name generically.
echo Installing necessary Python packages in venv for deployed environment
echo - these are the same as documented in GeoProcessor new developer Python install
echo - pip packages include: pandas, openpyxl, requests[security], SQLAlchemy
echo Installing necessary Python packages in venv for deployed environment>>"%gpVenvCreationLogFile%"
echo - these are the same as documented in GeoProcessor new developer Python install>>"%gpVenvCreationLogFile%"
echo - pip packages include: pandas, openpyxl, requests[security], SQLAlchemy>>"%gpVenvCreationLogFile%"
pip3 install pandas
pip3 install openpyxl
pip3 install requests[security]
pip3 install SQLAlchemy

rem Run the Python script to print the environment, to confirm the venv environment used for pip installs
echo Environment within activated venv:
python "%gpVenvFolder%\Lib\site-packages\geoprocessor\app\printenv.py"

rem Deactivate the virtual environment
echo Deactivating the virtual environment
echo Deactivating the virtual environment>>"%gpVenvCreationLogFile%"
call Scripts\deactivate.bat

:removeDlls

rem The dlls, if left in the Scripts folder, interfere with QGIS Python
if exist "!venvCryptoLib!" (
  echo Removing DLL that was needed for pip that will break QGIS Python:  !venvCryptoLib!
  echo Removing DLL that was needed for pip that will break QGIS Python:  !venvCryptoLib!>>"%gpVenvCreationLogFile%"
  del "!venvCryptoLib!"
)
if exist "!venvSslLib!" (
  echo Removing DLL that was needed for pip that will break QGIS Python:  !venvSslLib!
  echo Removing DLL that was needed for pip that will break QGIS Python:  !venvSslLib!>>"%gpVenvCreationLogFile%"
  del "!venvSslLib!"
)

rem Skip zipping if -z was specified on the command line
if "!doZip!"=="no" goto skipZip
rem Zip the files
rem - use 7zip.exe
echo.
echo Zipping the venv distribution...
echo Zipping the venv distribution...>>"%gpVenvCreationLogFile%"
set sevenZipExe=C:\Program Files\7-Zip\7z.exe
if exist "%sevenZipExe%" goto zipVenv
goto noSevenZip

:zipVenv

rem Zip the virtual environment folder
rem - change to the venv-tmp folder so zip will be relative
rem - also use filenames with no path to avoid issues with spaces in full path
echo.
echo Changing to folder %gpVenvTmpFolder%
cd "%gpVenvTmpFolder%"
rem Remove the old zip file if it exists
if exist %gpVenvZipFileShort% (
  echo Deleting existing zip file:  %gpVenvZipFileShort%
  del /s/q %gpVenvZipFileShort%
)
rem Now create the new venv zip file
echo Zipping up the virtual environment folder %gpVenvFolderShort% to create zip file %gpVenvZipFileShort%
"%sevenZipExe%" a -tzip %gpVenvZipFileShort% %gpVenvFolderShort%
rem Change back to script folder
cd "%startingFolder%"
echo.
echo Created zip file for deployment: %gpVenvTmpFolder%\%gpVenvZipFileShort%
goto finalMessage

:skipZip

echo.
echo Skipping zip file creation because -z option specified.
goto finalMessage

:finalMessage

if "%doUpdateFilesOnly%"=="yes" (
  echo Since running !scriptName! -u:
  echo - Run gpui.bat in the virtual environment folder to run the GeoProcessor UI prior to deployment
  echo     %gpVenvFolder%
  echo - When ready, run 2-create-gp-venv.bat to fully create virtual environment and installer zip file for deployment.
) else (
  echo - Rerun 2-create-gp-venv.bat to fully create virtual environment and installer zip file for deployment.
)
echo - Run 3-copy-gp-to-amazon-s3.sh in Cygwin to upload the Windows and Cygwin installers to public cloud.
goto exit0

rem Below here are targets that perform single actions and then exit

rem Error due to missing Scripts\activate.bat script
:missingActivateScriptError
echo.
echo "Missing %gpVenvFolder%\Scripts\activate.bat"
rem Change back to script folder
cd "%startingFolder%"
goto exit1

rem No python.exe to create the virtual environment
rem:noPythonForVenv
:noDevPythonExe
echo.
rem echo No development environment venv python.exe was found to initialize the virtual environment
echo No python.exe was found to create new venv, expecting:  %devPythonExe%
rem Change back to script folder
cd "%startingFolder%"
goto exit1

rem No QGIS python.exe for venv base interpreter
:noQgisPythonExe
echo.
rem echo No QGIS python.exe was found to initialize the virtual environment
echo No QGIS Python was found for new venv base interpreter, expecting:  %qgisPythonExe%
rem Change back to script folder
cd "%startingFolder%"
goto exit1

:noSevenZip
rem No 7zip software
echo.
echo No %sevenZipExe% was found to zip the virtual environment
rem Change back to script folder
cd "%startingFolder%"
goto exit1

:printUsage
rem Print the program usage
echo.
echo Usage:  %scriptName% [options]
echo.
echo Create or update a staging Python virtual environment [venv] for GeoProcessor
echo The versioned staging virtual environment is created in 'build-util/venv-tmp'
echo for the current development environment configuration.
echo The default is to create a zip file to distribute on Windows.
echo Run periodically with -u to update the staging venv with latest development files.
echo Run with defaults to create the staging venv from the current development files.
echo Prompts will be displayed to confirm important actions.
echo.
echo -h, /h            Print usage of this %scriptName% batch file.
echo -u, /u            Only copy files from development venv to the
echo                   existing staging venv.  Do not initialize venv or create zip file.
echo -v, /v            Print version of this %scriptName% batch file.
echo --nozip, /nozi    DO NOT create the zip file (default is to create).
echo --python-dev      Use the development environment Python for the venv. 
echo --python-qgis     Use the QGIS Python for the venv (default).
echo --python-sys      Use the system Python (py) for the venv.
echo --venv            Use the venv module to create the virtual environment.
echo --virtualenv      Use the virtualenv module to create the virtual environment (default).
echo.
rem Don't call exit0 since no need to go to starting folder
exit /b 0

:printVersion
rem Print the program version
echo.
echo %scriptName% version: %versionNum% %versionDate%
echo.
rem Don't call exit0 since no need to go to starting folder
exit /b 0

:exit0
rem Exit with normal (0) exit code
rem - put this at the end of the batch file
echo Changing back to starting folder %startingFolder%
echo Success.  Exiting with status 0.
cd "%startingFolder%"
exit /b 0

:exit1
rem Exit with general error (1) exit code
rem - put this at the end of the batch file
echo Changing back to starting folder %startingFolder%
echo Error.  An error of some type occurred [see previous messages].  Exiting with status 1.
cd "%startingFolder%"
exit /b 1
