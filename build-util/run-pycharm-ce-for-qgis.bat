@echo off
rem Batch file to set the environment for and run PyCharm consistent with QGIS 3 environment
rem - Use QGIS Python and libraries
rem - Start PyCharm with the configured environment
rem - This is similar to the `gpdev.bat` script
rem - The QGIS version to be used must be specified so that proper configuration is used

rem Turn on delayed expansion so that loops work
rem - Seems crazy but see:  https://ss64.com/nt/delayedexpansion.html
rem - Otherwise, for loops and ( ) blocks don't work because variables are not set as expected
rem - Such variables must be surrounded by ! !, rather than % %
setlocal EnableDelayedExpansion

rem The following seems to be relevant.
rem See:  http://spatialgalaxy.com/2014/10/09/a-quick-guide-to-getting-started-with-pyqgis-on-windows/
rem The following provides useful background but seems incomplete.
rem See:  http://planet.qgis.org/planet/tag/pycharm/

rem This batch file version can be different from the GeoProcessor Python version
rem - this version is just used to help track changes to this batch file
set pycharmBatVersion=1.0.0
set pycharmBatVersionDate=2020-03-30

rem Get the current folder, used to specify the path to the project
SET scriptFolder=%~dp0%
rem Remove trailing \ from scriptFolder
set scriptFolder=%scriptFolder:~0,-1%
set scriptName=%~nx0
rem Have to get parent folder using Windows for loop approach
for %%i in (%scriptFolder%) do set installFolder=%%~dpi
rem Remove trailing \ from installFolder
set installFolder=%installFolder:~0,-1%

echo Batch file name is: %scriptName%
echo %scriptName% is located in folder: %scriptFolder%
echo GeoProcessor development project is located in folder: %installFolder%

rem Set the absolute path to PyCharm program 
rem - check the newest first
rem - this assumes that the developer is using the newest version installed for development
rem - include editions that have been specifically used by Open Water Foundation for GeoProcessor development
for %%P in (2019.3.1 2018.2.6 2018.2.4 2018.1.3) do (
  echo Checking for PyCharm version %%P
  if exist "C:\Program Files\JetBrains\PyCharm Community Edition %%P\bin\pycharm64.exe" (
    echo Using PyCharm version %%P
    SET PYCHARM="C:\Program Files\JetBrains\PyCharm Community Edition 2019.3.1\bin\pycharm64.exe"
    goto pyCharmExists
  )
)

rem Did not find PyCharm version that is supported
goto noPyCharm

:pyCharmExists

echo Will use latest found Pycharm Community Edition: %PYCHARM%

rem Evaluate command line parameters, using Windows-style options
rem - have to check %1% and %2% because may be called from another file such as from gpui.bat using -ui
rem - the / options are handled here, consistent with Windows
rem - the /o option will only try to run the OSGeo4W QGIS install,
rem   useful for older development and troubleshooting
rem - the /s option will only try to run the standalone QGIS install,
rem   current default for development, consistent with the deployed environment
if "%1%"=="/h" goto printUsage
if "%2%"=="/h" goto printUsage
if "%1%"=="/?" goto printUsage
if "%2%"=="/?" goto printUsage

if "%1%"=="/o" goto runOsgeoQgis
if "%2%"=="/o" goto runOsgeoQgis

if "%1%"=="/s" goto runStandaloneQgis
if "%2%"=="/s" goto runStandaloneQgis

if "%1%"=="/v" goto printVersion
if "%2%"=="/v" goto printVersion

rem Options that specify the standalone QGIS version to use.
rem - the requested version will be confirmed below when file existence is checked
rem echo Before QGIS version for loop
set targetQgisVersion=unknown
for %%G in (3.4 3.10 3.12) do (
  set qgisVersion=%%G
  echo Checking command arguments for QGIS version /s!qgisVersion!
  if "%1%"=="/s!qgisVersion!" (
    set targetQgisVersion=!qgisVersion!
    echo Command line parameter /s!qgisVersion! detected.  Will run stand-alone QGIS !targetQgisVersion!.  Python venv must be compatible.
    goto runStandaloneQgis
  )
  rem Same logic but for %2
  if "%2%"=="/s!qgisVersion!" (
    set targetQgisVersion=!qgisVersion!
    echo Command line parameter /s!qgisVersion! detected.  Will run stand-alone QGIS !targetQgisVersion!.  Python venv must be compatible.
    goto runStandaloneQgis
  )
)

rem Default is to run standalone QGIS
rem - a warning will be generated if no QGIS version
echo.
echo QGIS install type not specified - defaulting to standalone QGIS
goto runStandaloneQgis

:runOsGeoQgis
echo.
echo Using OSGeo4W64 version of QGIS.

rem TODO smalers 2020-03-30 renable if needed but for now the code has not been updated to standalone level
echo.
echo OSGeo4W64 GIS version of GeoProcessor is currently disabled.  Use with standalone QGIS.
exit /b 1

if "!targetQgisVersion!"=="unknown" (
  echo.
  echo Target QGIS version is unknown.  Run with /s or /o option.
  rem List available standalone versions on all drives, not elegant but OK for now
  echo Available standalone QGIS versions:
  for %%A in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    rem TODO smalers 2020-03-30 why does the following always seem to evaluate to true?
    echo Checking drive %%A
    if exist %%A:\Program Files\" (
      dir /b "%%A:\Program Files\QGIS*"
    )
  )
  goto printUsage
)

rem Set an environment variable to indicate that the environment is setup.
rem - this ensures that setup is done once
rem - then PyCharm can be restarted in the same window without reconfiguring the environment

if "%OSGEO_GP_PYCHARM_ENV_SETUP%"=="YES" GOTO run
echo Setting up PyCharm environment to use QGIS Python environment
rem Where QGIS is installed
SET OSGEO4W_ROOT=C:\OSGeo4W64

rem Name of QGIS version to run (**for running OWF GeoProcessor don't run QGIS
rem but need to use correct QGIS components**).
rem Run the latest release of the OSGeo4W QGIS by setting value to `qgis`.
rem The QGIS OSGeo4W64 installer as of February 23, 2018 installs QGIS version 3 as `qgis`.
SET QGISNAME=qgis
set _qgis=%OSGEO4W_ROOT%\bin\qgis.bat

if not exist %_qgis% goto noqgisbat
echo QGISNAME is %QGISNAME%

rem Set the QGIS environment by calling the setup script that is distributed with QGIS 
CALL %OSGEO4W_ROOT%\bin\o4w_env.bat
rem Set environment variables for using the Qt5-Widget library
rem REF: https://gis.stackexchange.com/questions/276902/importing-paths-for-qgis-3-standalone-scripts
CALL %OSGEO4W_ROOT%\bin\qt5_env.bat
rem Set python3 specific variables
rem REF: https://gis.stackexchange.com/questions/276902/importing-paths-for-qgis-3-standalone-scripts
CALL %OSGEO4W_ROOT%\bin\py3_env.bat

rem Add QGIS to the PATH environment variable so that all QGIS, GDAL, OGR, etc. programs are found
set PATH=%OSGEO4W_ROOT%\bin;%PATH% 
set PATH=%PATH%;%OSGEO4W_ROOT%\apps\%QGISNAME%\bin

rem Absolute path to QGIS program to run 
SET QGIS=%OSGEO4W_ROOT%\apps\%QGISNAME%
rem Not sure what the following is used for but include in case PyCharm or QGIS uses 
SET QGIS_PREFIX_PATH=%QGIS%

rem Add QGIS to the PATH environment variable so that all QGIS, GDAL, OGR, etc. programs are found
SET PATH=%PATH%;%QGIS%\bin
SET PATH=%PATH%;%OSGEO4W_ROOT%\apps\Qt5\bin

rem Add pyQGIS libraries to the PYTHONPATH so that they are found by Python
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python\plugins

rem Set the Python to use
rem - list the following in order so most recent is at the end
rem - this assumes that OSGEO4W suite is installed in the default location and the latest should be used
rem - the following uses O (oh) as the loop variable
for %%O in (39 38 37 36) do (
  echo Checking OSGeo4W for Python%%O
  if exist %OSGEO4W_ROOT%\apps\Python%%O (
    echo Will use OSGeo4W Python%%O
    set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python%%O\lib\site-packages;%PYTHONPATH%
  )
)

rem Set the environment variable that lets this batch file know that the environment is set up
set OSGEO_GP_PYCHARM_ENV_SETUP=YES

rem This is the entry point of the script after set and if the script has been run before
rem - set the window title to indicate that the environment is configured
rem - TODO smalers 2020-01-10 need to set title if error occurred setting up the environment?
:run
title GeoProcessor OSGeo4W QGIS development environment for PyCharm

rem Echo environment variables for troubleshooting
echo.
echo PATH=%PATH%
echo PYTHONHOME=%PYTHONHOME%
echo PYTHONPATH=%PYTHONPATH%
echo QGIS_PREFIX_PATH=%QGIS_PREFIX_PATH%
echo QT_PLUGIN_PATH=%QT_PLUGIN_PATH%
echo.

rem Start the PyCharm IDE, /B indicates to use the same windows
rem - command line parameters passed to this script will be passed to PyCharm 
rem - PyCharm will use the Python interpreter configured for the project
rem - Specify the folder for the project so it does not default to some other project
rem   that was opened last
echo Starting PyCharm using:  start ... /B %PYCHARM% %GP_PROJECT_DIR% %*
echo Prompt will display and PyCharm may take a few seconds to start.
SET GP_PROJECT_DIR=%insallFolder%
if exist %GP_PROJECT_DIR% start "PyCharm aware of QGIS" /B %PYCHARM% %GP_PROJECT_DIR% %*
if not exist %GP_PROJECT_DIR% goto noproject
goto endofbat

:runStandaloneQgis

rem Run the standalone version of QGIS
echo.
echo Using standalone version of QGIS.

echo Target standalone QGIS version = %targetQgisVersion%
if "%targetQgisVersion%"=="unknown" (
  echo.
  echo Target QGIS version is unknown.  Run with /s or /o option.
  rem List available standalone versions on all drives, not elegant but OK for now
  echo Available standalone QGIS versions:
  for %%Z in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    set driveLetter=%%Z
    rem debug...
    rem echo Checking for existence of:  !driveLetter!:\Program Files\
    if exist "!driveLetter!:\Program Files\" (
      dir /b "!driveLetter!:\Program Files\QGIS*"
    )
  )
  goto printUsage
)

rem Set the Python environment to find the correct run-time libraries
rem - QGIS Python environment is used and add GeoProcessor to PYTHONPATH
rem - The SA_GP_ENV_SETUP environment variable is set to YES
rem   to indicate that setup has been done.
rem - This causes setup to occur only once if rerunning this batch file.

if "%SA_PYCHARM_GP_ENV_SETUP%"=="YES" (
  echo Environment is already set up for standalone QGIS from previous run.
  goto runStandaloneQgis2
)
rem ===================================================================================
rem If here do the setup one time first time batch file is run in a command shell
echo Start defining standalone QGIS GeoProcessor environment...

rem This code is similar to the initial check at the top of the batch file.
for %%D in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
  echo Checking for existence of %%D:\Program Files\QGIS !targetQgisVersion!
  if exist "%%D:\Program Files\QGIS !targetQgisVersion!" (
    SET QGIS_SA_INSTALL_HOME=%%D:\Program Files\QGIS !targetQgisVersion!
    echo Standard QGIS exists in:  !QGIS_SA_INSTALL_HOME!
    goto setupStandalone1b
  )
)
rem TODO smalers 2020-03-26 Keep old code here as a placeholder to find "nearest" version
rem if exist "C:\Program Files\QGIS 3.12" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.12
rem if exist "C:\Program Files\QGIS 3.11" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.11
rem if exist "C:\Program Files\QGIS 3.10" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.10
rem if exist "C:\Program Files\QGIS 3.9" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.9
rem if exist "C:\Program Files\QGIS 3.8" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.8
rem if exist "C:\Program Files\QGIS 3.7" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.7
rem if exist "C:\Program Files\QGIS 3.6" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.6
rem if exist "C:\Program Files\QGIS 3.5" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.5
rem if exist "C:\Program Files\QGIS 3.4" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.4

:setupStandalone1b

rem Get the short version of the install home
echo Initial standalone install home before 8.3 conversion:  !QGIS_SA_INSTALL_HOME!
for %%H in ("!QGIS_SA_INSTALL_HOME!") do set QGIS_SA_INSTALL_HOME_83=%%~sH
rem TODO smalers 2020-04-01 Try using 8.3 names
echo Resetting standalone QGIS install home !QGIS_SA_INSTALL_HOME! to short version: !QGIS_SA_INSTALL_HOME_83!
set QGIS_SA_INSTALL_HOME=!QGIS_SA_INSTALL_HOME_83!
rem set QGIS_SA_ROOT=%QGIS_SA_INSTALL_HOME%
set QGIS_SA_ROOT=%QGIS_SA_INSTALL_HOME_83%
echo Running GeoProcessor using standalone GQGIS in:  %QGIS_SA_INSTALL_HOME%

rem Where QGIS is installed
if not exist "%QGIS_SA_INSTALL_HOME%" GOTO noStandaloneQgis

rem Set the QGIS environment by calling the setup batch files that are distributed with QGIS
rem - the following will reset the PATH and then add QGIS folders to path
rem - therefore other programs that were found before may not be found
rem - this effectively isolates QGIS from the system
rem - same batch file name as for OSGeo4W install
echo Calling QGIS setup batch file:  %QGIS_SA_ROOT%\bin\o4w_env.bat
call "%QGIS_SA_ROOT%\bin\o4w_env.bat"
rem The following sets a number of QT environment variables (QT is used in the UI)
rem - same batch file name as for OSGeo4W install
echo Calling Qt setup batch file:  %QGIS_SA_ROOT%\bin\qt5_env.bat
call "%QGIS_SA_ROOT%\bin\qt5_env.bat"
rem The following sets:
rem - PYTHONHOME to Python shipped with QGIS install
rem - Clears PYTHONPATH
rem - PATH to include Python shipped with QGIS and Python scripts folder
rem - same batch file name as for OSGeo4W install
echo Calling Python 3 setup batch file:  %QGIS_SA_ROOT%\bin\py3_env.bat
call "%QGIS_SA_ROOT%\bin\py3_env.bat"

rem Name of QGIS version to run (**for running GeoProcessor don't run QGIS but need to use correct QGIS components**).
rem Run the target release of the OSGeo4W QGIS by setting value to `qgis`.
rem Using the long-term release of the OSGeo4W QGIS by setting value to `qgis-ltr` is not supported.
SET QGISNAME=qgis
echo QGISNAME is %QGISNAME%

rem Add QGIS to the PATH environment variable so that all QGIS, GDAL, OGR, etc. programs are found.
set PATH=%QGIS_SA_ROOT%\bin;%PATH%
set GDAL_FILENAME_IS_UTF8=YES
rem --
rem Set VSI cache to be used as buffer, see https://issues.qgis.org/issues/6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
rem --

rem Add QGIS python and plugins to the PYTHONPATH
rem - Old version of this batch file used %QGISNAME%, which was typically 'qgis';
rem   however, it could be 'qgis-ltr` for long term release or 'qgis-dev' for development.
rem   Therefore, the following now checks for multiple release types.
rem   See:  https://docs.qgis.org/3.4/pdf/en/QGIS-3.4-PyQGISDeveloperCookbook-en.pdf
rem - The qgis-ltr folder needs to be checked first because for a long term release
rem   the qgis-ltr/python and qgis/python folders each exist, but qgis/python is empty.
rem - Only apps/qgis-ltr/python needs to be checked for qgis-ltr.
rem - Also get the Windows short name for QGIS install folder (troubleshooting whether this is needed)
rem for %%H in ("%PYTHONHOME%") do PYTHONHOME_83=%%~sH
echo PYTHONHOME after QGIS setup:  %PYTHONHOME%
rem echo PYTHONHOME 8.3 after QGIS setup:  %PYTHONHOME_83%
echo PYTHONPATH after QGIS setup:  !PYTHONPATH!
for %%Q in (qgis-ltr qgis qgis-dev) do (
  if exist %QGIS_SA_ROOT%\apps\%%Q\python (
    set PATH=%PATH%;%QGIS_SA_ROOT%\apps\%%Q\bin
    set QGIS_PREFIX_PATH=%QGIS_SA_ROOT%\apps\%%Q
    set QT_PLUGIN_PATH=%QGIS_SA_ROOT%\apps\%%Q\qtplugins;%QGIS_SA_ROOT%\apps\qt5\plugins

    set PYTHONPATH_QGIS_PYTHON=%QGIS_SA_ROOT%\apps\%%Q\python
    echo Adding standalone QGIS Python to front of PYTHONPATH: !PYTHONPATH_QGIS_PYTHON!
    set PYTHONPATH=!PYTHONPATH_QGIS_PYTHON!;!PYTHONPATH!

    rem Plugins folder does not use 'qgis-ltr'
    rem See https://anitagraser.com/2018/01/28/porting-processing-scripts-to-qgis3/
    rem The following is is "python/plugins", not just "plugins"
    set PYTHONPATH_QGIS_PLUGINS=%QGIS_SA_ROOT%\apps\%%Q\python\plugins
    echo Adding standalone QGIS plugins to front of PYTHONPATH: !PYTHONPATH_QGIS_PLUGINS!
    set PYTHONPATH=!PYTHONPATH_QGIS_PLUGINS!;!PYTHONPATH!

    goto standalonePathSet
  )
)

:standalonePathSet
rem If here the PYTHONPATH was set above for PyQGIS

rem Add QGIS site-packages to PYTHONPATH
rem TODO smalers 2020-03-30 this should just use the Python version from PYTHONHOME
rem List the following in order so most recent Python for target version is found first.
rem - cannot get if else if to work so use goto
for %%V in (37 36) do (
  echo Checking for existence of %QGIS_SA_ROOT%\apps\Python%%V
  if exist %QGIS_SA_ROOT%\apps\Python%%V\ (
    rem It appears that QGIS Python uses lowercase "lib" is used rather than "Lib", so use lowercase below.
    rem - not sure why that is done (maybe for Linux?) but make lowercase here
    set PYTHONPATH_QGIS_SITEPACKAGES=%QGIS_SA_ROOT%\apps\Python%%V\lib\site-packages
    echo Adding standalone QGIS Python%%V 'lib\site-packages' to front of PYTHONPATH: !PYTHONPATH_QGIS_SITEPACKAGES!
    set PYTHONPATH=!PYTHONPATH_QGIS_SITEPACKAGES!;!PYTHONPATH!

    rem Viewing sys.path for working gpdev.bat shows 8.3 paths for some files so add again here and below
    rem The following are listed in Python sys.path when running gpdev.bat (without specifically adding)
    rem but don't by default get added in the PyCharm environment.
    rem TODO smalers 2020-04-01 need to add
    set PYTHONPATH_QGIS_SITE_PACKAGES_PYTHONWIN=%QGIS_SA_ROOT%\apps\Python%%V\lib\site-packages\Pythonwin
    echo Adding standalone QGIS Python%%V 'lib\site-packages\Pythonwin' to front of PYTHONPATH: !PYTHONPATH_QGIS_SITE_PACKAGES_PYTHONWIN!
    set PYTHONPATH=!PYTHONPATH_QGIS_SITE_PACKAGES_PYTHONWIN!;!PYTHONPATH!

    set PYTHONPATH_QGIS_SITE_PACKAGES_WIN32=%QGIS_SA_ROOT%\apps\Python%%V\lib\site-packages\win32
    echo Adding standalone QGIS Python%%V 'lib\site-packages\win32' to front of PYTHONPATH: !PYTHONPATH_QGIS_SITE_PACKAGES_WIN32!
    set PYTHONPATH=!PYTHONPATH_QGIS_SITE_PACKAGES_WIN32!;!PYTHONPATH!

    set PYTHONPATH_QGIS_SITE_PACKAGES_WIN32_LIB=%QGIS_SA_ROOT%\apps\Python%%V\lib\site-packages\win32\lib
    echo Adding standalone QGIS Python%%V 'lib\site-packages\win32\lib' to front of PYTHONPATH: !PYTHONPATH_QGIS_SITE_PACKAGES_WIN32_LIB!
    set PYTHONPATH=!PYTHONPATH_QGIS_SITE_PACKAGES_WIN32_LIB!;!PYTHONPATH!

    rem Similarly, the PATH needs to have additional folders to agree with working gpdev.bat
    set PATH_QGIS_SITE_PACKAGES_PYWIN32_SYSTEM32=%QGIS_SA_ROOT%\apps\Python%%V\lib\site-packages\pywin32_system32
    echo Adding standalone QGIS Python%%V 'lib\site-packages\win32' to front of PYTHONPATH: !PATH_QGIS_SITE_PACKAGES_PYWIN32_SYSTEM32!
    set PATH=!PATH!;!PATH_QGIS_SITE_PACKAGES_PYWIN32_SYSTEM32!

    goto standalonePathSet2
  )
)
rem Warning because could not find QGIS Python
echo Error: could not find Python37 or Python36 in %QGIS_SA_ROOT%\apps for site-packages
exit /b 1

:standalonePathSet2

rem Add additional packages to PYTHONPATH, located in PyCharm development venv
rem TODO smalers 2020-03-30 this should just use the Python version from PYTHONHOME
rem List the following in order so most recent Python for target version is found first.
rem - it would seem that this should be done automatically but based on testing
for %%T in (37 36) do (
  echo Checking for existence of %installFolder%\venv\venv-qgis-!targetQgisVersion!-python%%T
  if exist %installFolder%\venv\venv-qgis-!targetQgisVersion!-python%%T\ (
    set PYTHONPATH_PYCHARM_SITEPACKAGES=%installFolder%\venv\venv-qgis-!targetQgisVersion!-python%%T\Lib\site-packages
    echo Adding PyCharm Python%%T site-packages to front of PYTHONPATH: !PYTHONPATH_PYCHARM_SITEPACKAGES!
    set PYTHONPATH=!PYTHONPATH_PYCHARM_SITEPACKAGES!;!PYTHONPATH!
    goto setupStandalone2
  )
)
rem Warning because could not find QGIS Python
echo Error: could not find Python37 or Python36 in %QGIS_SA_ROOT%\apps for site-packages
exit /b 1

:setupStandalone2

rem Add the GeoProcessor to the PYTHONPATH
rem - OK to put at the front because geoprocessor should not conflict with anything else
set GEOPROCESSOR_HOME=%installFolder%
echo Adding GeoProcessor Python developer code to start of PYTHONPATH:  %GEOPROCESSOR_HOME%
set PYTHONPATH=%GEOPROCESSOR_HOME%;!PYTHONPATH!


rem Indicate that the setup has been completed
rem - this will ensure that the script when run again does not repeat setup
rem   and keep appending to environment variables
set SA_PYCHARM_GP_ENV_SETUP=YES

rem Set the window title to indicate how configured so as to avoid confusion
title GeoProcessor standalone QGIS development environment for PyCharm
echo ...done defining QGIS GeoProcessor environment
goto runStandaloneQgis2

rem ========== END GeoProcessor setup steps to be done once ===========================
rem ===================================================================================

:noStandaloneQgis

rem QGIS install folder was not found
echo QGIS standard installation folder was not found:  %QGIS_SA_INSTALL_HOME%
exit /b 1

:runStandaloneQgis2

rem Echo environment variables for troubleshooting
echo.
echo Using Python3/standalone QGIS3 for GeoProcessor
echo Environment for Python/GeoProcessor:
echo QGIS_SA_INSTALL_HOME=%QGIS_SA_INSTALL_HOME%
echo PATH=%PATH%
echo PYTHONHOME=%PYTHONHOME%
echo PYTHONPATH=!PYTHONPATH!
echo QGIS_PREFIX_PATH=%QGIS_PREFIX_PATH%
echo QT_PLUGIN_PATH=%QT_PLUGIN_PATH%
echo.

rem Set the window title again because running commands in the window resets the title
title GeoProcessor standalone QGIS development environment for PyCharm

rem Start the PyCharm IDE, /B indicates to use the same windows
rem - command line parameters passed to this script will be passed to PyCharm 
rem - PyCharm will use the Python interpreter configured for the project
rem - Specify the folder for the project so it does not default to some other project
rem   that was opened last
rem echo Starting PyCharm using:  start ... /B %PYCHARM% %GP_PROJECT_DIR% %*
echo Starting PyCharm using:  start ... /B %PYCHARM% %GP_PROJECT_DIR%
echo Prompt will display and PyCharm may take a few seconds to start.
SET GP_PROJECT_DIR=%installFolder%
rem TODO smalers 2020-03-30 need to figure out how to strip out /s3.10, etc. so PyCharm won't complain
rem if exist %GP_PROJECT_DIR% start "PyCharm aware of QGIS" /B %PYCHARM% %GP_PROJECT_DIR% %*
if exist %GP_PROJECT_DIR% start "PyCharm aware of QGIS" /B %PYCHARM% %GP_PROJECT_DIR%
if not exist %GP_PROJECT_DIR% goto noproject
goto endofbat

rem =======================================================================
rem Below here are one-off goto targets that each end with exit

:noproject
rem No project directory (should not happen)
echo Project folder does not exist:  %GP_PROJECT_DIR%
echo Not starting PyCharm.
exit /b 1

:noPyCharm
rem Expected PyCharm was not found
echo PyCharm was not found in expected location C:\Program Files\JetBrains\PyCharm Community Edition NNNN.N.N\bin\pycharm64.exe
echo May need to update this script for newer versions of PyCharm.
exit /b 1

:noqgisbat
rem qgis.bat was not found
echo QGIS batch file not found:  %OSGEO4W_ROOT%/bin/qgis.bat
exit /b 1

:printUsage
rem Print the program usage
echo.
echo Usage:  run-pycharm-ce-for-qgis.bat [options]
echo.
echo Run PyCharm to develop the GeoProcessor.
echo This batch file sets up the development environment and calls PyCharm.
echo.
echo /h      Print usage of this gp.bat batch file.
echo /o      Use the OSGeo4W version of QGIS.
echo /s      Use the standalone version of QGIS - default rather than /o.
echo /sN.N   Use the standalone version N.N of QGIS, for example 3.10
echo /v      Print version of this gp.bat batch file.
echo.
exit /b 0

:printVersion
rem Print the program version
echo.
echo run-pycharm-ce-for-qgis.bat version: %pycharmBatVersion% %pycharmBatVersionDate%
echo.
exit /b 0

rem For some reason using "end" causes an error - reserved word?
:endofbat
