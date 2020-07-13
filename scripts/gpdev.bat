@echo off
rem gpdev.bat - run the GeoProcessor in the development environment
rem _________________________________________________________________NoticeStart_
rem GeoProcessor
rem Copyright (C) 2017-2020 Open Water Foundation
rem  
rem GeoProcessor is free software:  you can redistribute it and/or modify
rem     it under the terms of the GNU General Public License as published by
rem     the Free Software Foundation, either version 3 of the License, or
rem     (at your option) any later version.
rem 
rem     GeoProcessor is distributed in the hope that it will be useful,
rem     but WITHOUT ANY WARRANTY; without even the implied warranty of
rem     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
rem     GNU General Public License for more details.
rem 
rem     You should have received a copy of the GNU General Public License
rem     along with GeoProcessor.  If not, see <https://www.gnu.org/licenses/>.
rem _________________________________________________________________NoticeEnd___
rem
rem Windows batch file to run the Open Water Foundation GeoProcessor application for QGIS
rem - Run in the development environment
rem - This script is similar to gp.bat except that development virtual environment is used.
rem - The default is to start the interpreter but can run gpuidev.bat to run the UI, for if gpuidev.bat -ui is run.
rem - This batch file is used with Python3/QGIS3 (older QGIS LTR is not used)
rem - This batch file handles:
rem     - stand-alone QGIS installation used for typical users
rem     - OSGeo4W64 QGIS, wihch may be used by developers
rem - Checks are done for Python 3.6 and 3.7, with latest used, to accomodate QGIS versions.
rem - The current focus is to run on a Windows 10 development environment.
rem - This batch file uses the QGIS Python as the interpreter, but development geoprocessor module via PYTHONPATH.
rem - This batch file should be installed in the scripts folder in the GeoProcessor code repository.
rem - Paths to virtual environment used in development are assumed based on standard OWF development environment.

rem Set the Python environment to find the correct run-time libraries
rem - The GEOPROCESSOR_ENV_SETUP environment variable is set to YES
rem   to indicate that setup has been done.
rem - This causes setup to occur only once if rerunning this batch file.

rem Turn on delayed expansion so that loops work
rem - Seems crazy but see:  https://ss64.com/nt/delayedexpansion.html
rem - Otherwise, for loops and ( ) blocks don't work because variables are not set as expected
rem - Such variables must be surrounded by ! !, rather than % %
setlocal EnableDelayedExpansion

rem Determine the folder that the script exists in
rem - used to provide path relative to the GeoProcessor files
set scriptFolder=%~dp0
rem Remove trailing \ from scriptFolder
set scriptFolder=%scriptFolder:~0,-1%
set scriptName=%~nx0
rem Have to get parent folder using Windows for loop approach
for %%i in (%scriptFolder%) do set installFolder=%%~dpi
rem Remove trailing \ from installFolder
set installFolder=%installFolder:~0,-1%

echo Batch file name is: %scriptName%
echo gpdev.bat is located in folder: %scriptFolder%
echo GeoProcessor software is located in folder: %installFolder%

rem The script version can be different from the GeoProcessor Python version
rem - this version is just used to help track changes to this script
set gpdevBatVersion=1.2.0
set gpdevBatVersionDate=2020-07-07

rem Evaluate command options, using Windows-style options
rem - have to check %1% and %2% because may be called from another file such as from gpuidev.bat using -ui
rem - the / options are handled here, consistent with Windows
rem - the dash options will be handled by the called Python program
rem - the /o option will only try to run the OSGeo4W QGIS install,
rem   useful for development and troubleshooting
rem - the /s option will only try to run the standalone QGIS install,
rem   useful for development and troubleshooting
if "%1%"=="/h" goto printUsage
if "%2%"=="/h" goto printUsage
if "%1%"=="/?" goto printUsage
if "%2%"=="/?" goto printUsage

set doPrintEnv=no
if "%1%"=="/printenv" (
  set doPrintEnv=yes
)
if "%2%"=="/printenv" (
   set doPrintEnv=yes
)
if "%3%"=="/printenv" (
   set doPrintEnv=yes
)

if "%1%"=="/o" goto runOsgeoQgis
if "%2%"=="/o" goto runOsgeoQgis
if "%3%"=="/o" goto runOsgeoQgis

rem Run Python directly, useful to run "processing.alghelp()" and other functions. 
rem - set up the environment as if running GeoProcessor but just run Python
set runPython=no
if "%1%"=="/python" (
  set runPython=yes
)
if "%2%"=="/python" (
   set runPython=yes
)
if "%3%"=="/python" (
   set runPython=yes
)

if "%1%"=="/s" goto runStandaloneQgis
if "%2%"=="/s" goto runStandaloneQgis
if "%3%"=="/s" goto runStandaloneQgis

if "%1%"=="/v" goto printVersion
if "%2%"=="/v" goto printVersion
if "%3%"=="/v" goto printVersion

rem Options that specify the standalone QGIS version to use.
rem - the requested version will be confirmed below when file existence is checked
rem echo Before QGIS version for loop
set qgisVersion=unknown
for %%G in (3.4 3.10 3.12) do (
  rem Set a local variable to make code easier to understand
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
  rem Same logic but for %3
  if "%3%"=="/s!qgisVersion!" (
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

:runOsgeoQgis

rem Run the OSGeo4W64 version of QGIS
echo.
echo Using OSGeo4W64 version of QGIS.

rem TODO smalers 2020-03-30 re-enable if needed but for now the code has not been updated to standalone level
echo.
echo OSGeo4W64 GIS version of GeoProcessor is currently disabled.  Use with standalone QGIS.
goto exit1

if "%targetQgisVersion%"=="unknown" (
  echo.
  echo Target OSGeo4W QGIS version is unknown.  Run with /s or /o option.
  rem List available standalone versions on all drives, not elegant but OK for now
  echo Available standalone QGIS versions:
  for %%Y in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    set driveLetter=%%Y
    rem debug...
    rem echo Checking for existence of:  !driveLetter!:\Program Files\
    if exist "!driveLetter!:\Program Files\" (
      dir /b "!driveLetter!:\Program Files\QGIS*"
    )
  )
  goto printUsage
)

if "%GP_DEV_ENV_SETUP%"=="YES" (
  echo Environment is already set up to use OSGeo4W GQIS from previous run.  Skipping to run step...
  goto runOsgeoQgis2
)
rem ===================================================================================
rem If here do the setup one time first time batch file is run in a command shell
echo Start defining QGIS GeoProcessor environment (done once per command shell window)...

rem Where QGIS is installed
SET QGIS_INSTALL_HOME=C:\OSGeo4W64
SET OSGEO4W_ROOT=%QGIS_INSTALL_HOME%
if not exist %OSGEO4W_ROOT% GOTO noOsgeoQgis
echo OSGeo4W QGIS is installed in:  %QGIS_INSTALL_HOME%

rem Set the QGIS environment by calling the setup batch files that are distributed with QGIS
rem - the following will reset the PATH and then add QGIS folders to path
rem - therefore other programs that were found before may not be found
rem - this effectively isolates QGIS from the system
echo Calling QGIS setup batch file:  %OSGEO4W_ROOT%\bin\o4w_env.bat
call "%OSGEO4W_ROOT%\bin\o4w_env.bat"
rem The following sets a number of QT environment variables (QT is used in the UI)
echo Calling QGIS Qt setup batch file:  %OSGEO4W_ROOT%\bin\qt5_env.bat
call "%OSGEO4W_ROOT%\bin\qt5_env.bat"
rem The following sets:
rem - PYTHONHOME to Python shipped with QGIS
rem - Clears PYTHONPATH
rem - PATH to include Python shipped with QGIS and Python scripts folder
echo Calling QGIS Python 3 setup batch file:  %OSGEO4W_ROOT%\bin\py3_env.bat
call %OSGEO4W_ROOT%\bin\py3_env.bat

rem Name of QGIS version to run (**for running OWF GeoProcessor don't run QGIS but need to use correct QGIS components**).
rem Run the latest release of the OSGeo4W QGIS by setting value to `qgis`.
rem Using the long-term release of the OSGeo4W QGIS by setting value to `qgis-ltr` is not supported.
set QGISNAME=qgis
echo QGISNAME is %QGISNAME%

rem Add QGIS to the PATH environment variable so that all QGIS, GDAL, OGR, etc. programs are found.
set PATH=%OSGEO4W_ROOT%\bin;%PATH% 
set PATH=%PATH%;%OSGEO4W_ROOT%\apps\%QGISNAME%\bin

set QGIS_PREFIX_PATH=%OSGEO4W_ROOT%\apps\%QGISNAME%
set GDAL_FILENAME_IS_UTF8=YES
rem --
rem Set VSI cache to be used as buffer, see https://issues.qgis.org/issues/6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
rem --

set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\%QGISNAME%\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins

rem Add pyQGIS libraries to the PYTHONPATH so that they are found by Python
set PYTHONPATH=%OSGEO4W_ROOT%\apps\%QGISNAME%\python;%PYTHONPATH%
rem See https://anitagraser.com/2018/01/28/porting-processing-scripts-to-qgis3/
set PYTHONPATH=%OSGEO4W_ROOT%\apps\%QGISNAME%\python\plugins;%PYTHONPATH%

rem List the following in order so most recent is found first.
rem Could not get else if to work!
if exist "%OSGEO4W_ROOT%\apps\Python37" (
  echo Adding QGIS Python37 site-packages to PYTHONPATH
  set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python37\lib\site-packages;%PYTHONPATH%
  goto runOsgeoQgis1
)
if exist "%OSGEO4W_ROOT%\apps\Python36" (
  echo Adding QGIS Python36 site-packages to PYTHONPATH
  set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python36\lib\site-packages;%PYTHONPATH%
  goto runOsgeoQgis1
)
rem No suitable Python found for OSGeo4W version
echo Python 3.6-3.7 version not found in %OSGEO4W_ROOT%\apps.  Exiting.
goto exit1

:runOsgeoQgis1

rem  Set the PYTHONPATH to include the geoprocessor/ folder in source files
rem  - This is used in the development environment because the package has not been installed in Python Lib/site-packages
rem  - OK to put at the front of PYTHONPATH because the folder ONLY contains GeoProcessor code, no third party packages
set GEOPROCESSOR_HOME=%installFolder%
set PYTHONPATH=%GEOPROCESSOR_HOME%;%PYTHONPATH%

rem Indicate that the setup has been completed
rem - this will ensure that the script when run again does not repeat setup
rem   and keep appending to environment variables
set GP_DEV_ENV_SETUP=YES

rem Set the window title to indicate how configured so as to avoid confusion
title GeoProcessor OSGeo4W QGIS development environment to run gpdev.bat and gpuidev.bat (don't run gp.bat or gpui.bat)
echo ...done defining QGIS GeoProcessor environment (done once per command shell window)
goto runOsgeoQgis2

rem ========== END GeoProcessor setup steps to be done once ===========================
rem ===================================================================================

:noOsgeoQgis

rem QGIS install folder was not found
echo OSGeo4W64 QGIS standard installation folder was not found:  %OSGEO4W_ROOT%
goto exit1

:runOsgeoQgis2

rem If here then the environment has been configured.
rem Echo environment variables for troubleshooting
echo.
echo Using OSGeo4W Python3/QGIS3 for development GeoProcessor.
echo Environment for Python/GeoProcessor:
echo PATH=%PATH%
echo PYTHONHOME=%PYTHONHOME%
echo PYTHONPATH=%PYTHONPATH%
echo QGIS_PREFIX_PATH=%QGIS_PREFIX_PATH%
echo QT_PLUGIN_PATH=%QT_PLUGIN_PATH%
echo.

rem Set the window title again because running commands in the window resets the title
title GeoProcessor OSGeo4W QGIS development environment to run gpdev.bat and gpuidev.bat (don't run gp.bat or gpui.bat)

rem Run QGIS Python with the geoprocessor module found using PYTHONPATH set above.
rem - Must use Python 3.6 compatible with QGIS
rem - Pass command line arguments that were passed to this bat file.
rem "%PYTHONHOME%\python" %*
rem Use -v to see verbose list of modules that are loaded.
echo Running:  %PYTHONHOME%\python -m geoprocessor.app.gp %*
"%PYTHONHOME%\python" -m geoprocessor.app.gp %*

rem Run the following to use the environment but be able to do imports, etc. to find modules
rem "%PYTHONHOME%\python" -v

rem Exit with the error level of the Python command
exit /b %ERRORLEVEL%

:runStandaloneQgis

rem Run the standalone version of QGIS
echo.
echo Using standalone version of QGIS.

echo Target standalone QGIS version = %targetQgisVersion%
if "%targetQgisVersion%"=="unknown" (
  echo.
  echo Target standalone QGIS version is unknown.  Run with /s or /o option.
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

if "%SA_GP_ENV_SETUP%"=="YES" (
  echo Environment is already set up for standalone QGIS from previous run.
  goto runStandaloneQgis2
)
rem ===================================================================================
rem If here do the setup one time first time batch file is run in a command shell
echo Start defining standalone QGIS GeoProcessor environment...

rem This code is similar to the initial check at the top of the batch file.
for %%D in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
  echo Checking for existence of %%D:\Program Files\QGIS %targetQgisVersion%
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

SET QGIS_SA_ROOT=%QGIS_SA_INSTALL_HOME%
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
echo Calling QGIS Qt setup batch file:  %QGIS_SA_ROOT%\bin\qt5_env.bat
call "%QGIS_SA_ROOT%\bin\qt5_env.bat"
rem The following sets:
rem - PYTHONHOME to Python shipped with QGIS install
rem - Clears PYTHONPATH
rem - PATH to include Python shipped with QGIS and Python scripts folder
rem - same batch file name as for OSGeo4W install
echo Calling QGIS Python 3 setup batch file:  %QGIS_SA_ROOT%\bin\py3_env.bat
call "%QGIS_SA_ROOT%\bin\py3_env.bat"

rem Name of QGIS version to run (**for running GeoProcessor don't run QGIS but need to use correct QGIS components**).
rem - if long term release is used, the name will be replaced with 'qgis-ltr' as needed below
SET QGISNAME=qgis
echo QGISNAME is %QGISNAME%, some variables will use 'qgis-ltr' if long term release is detected

rem Add QGIS to the PATH environment variable so that all QGIS, GDAL, OGR, etc. programs are found.
set PATH=%QGIS_SA_ROOT%\bin;%PATH%

set GDAL_FILENAME_IS_UTF8=YES
rem --
rem Set VSI cache to be used as buffer, see https://issues.qgis.org/issues/6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
rem --

rem Add QGIS Python and plugins to the PYTHONPATH
rem - Old version of this batch file used %QGISNAME%, which was typically 'qgis';
rem   however, it could be 'qgis-ltr` for long term release or 'qgis-dev' for development.
rem   Therefore, the following now checks for multiple release types.
rem   See:  https://docs.qgis.org/3.4/pdf/en/QGIS-3.4-PyQGISDeveloperCookbook-en.pdf
rem - The qgis-ltr folder needs to be checked first because for a long term release
rem   the qgis-ltr/python and qgis/python folders each exist, but qgis/python is empty.
rem - 'qgis-ltr' is used in several environment variables.
echo PATH after QGIS setup:  %PATH%
echo PYTHONHOME after QGIS setup:  %PYTHONHOME%
echo PYTHONPATH after QGIS setup:  !PYTHONPATH!
for %%Q in (qgis-ltr qgis qgis-dev) do (
  if exist %QGIS_SA_ROOT%\apps\%%Q\python (
    set PATH=%PATH%;%QGIS_SA_ROOT%\apps\%%Q\bin
    set QGIS_PREFIX_PATH=%QGIS_SA_ROOT%\apps\%%Q
    set QT_PLUGIN_PATH=%QGIS_SA_ROOT%\apps\%%Q\qtplugins;%QGIS_SA_ROOT%\apps\qt5\plugins

    set PYTHONPATH_QGIS_PYTHON=%QGIS_SA_ROOT%\apps\%%Q\python
    echo Adding standalone QGIS Python to front of PYTHONPATH: !PYTHONPATH_QGIS_PYTHON!
    set PYTHONPATH=!PYTHONPATH_QGIS_PYTHON!;!PYTHONPATH!

    rem See https://anitagraser.com/2018/01/28/porting-processing-scripts-to-qgis3/
    rem set PYTHONPATH_QGIS_PLUGINS=%QGIS_SA_ROOT%\apps\%%Q\plugins
    rem The following is is "python/plugins", not just "plugins"
    set PYTHONPATH_QGIS_PLUGINS=%QGIS_SA_ROOT%\apps\%%Q\python\plugins
    echo Adding standalone QGIS plugins to front of PYTHONPATH: !PYTHONPATH_QGIS_PLUGINS!
    set PYTHONPATH=!PYTHONPATH_QGIS_PLUGINS!;!PYTHONPATH!

    goto standalonePathSet
  )
)

:standalonePathSet
rem If here the PYTHONPATH was set above

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
    echo Adding standalone QGIS Python%%V site-packages to front of PYTHONPATH: !PYTHONPATH_QGIS_SITEPACKAGES!
    set PYTHONPATH=!PYTHONPATH_QGIS_SITEPACKAGES!;!PYTHONPATH!
    goto standalonePathSet2
  )
)
rem Warning because could not find QGIS Python
echo Error: could not find Python37 or Python36 in %QGIS_SA_ROOT%\apps for site-packages
goto exit1

:standalonePathSet2

rem Add additional packages to PYTHONPATH, located in PyCharm development venv
rem TODO smalers 2020-03-30 this should just use the Python version from PYTHONHOME
rem List the following in order so most recent Python for target version is found first.
rem - cannot get if else if to work so use goto
for %%T in (37 36) do (
  echo Checking for existence of %installFolder%\venv\venv-qgis-!targetQgisVersion!-python%%T
  if exist %installFolder%\venv\venv-qgis-!targetQgisVersion!-python%%T\ (
    set PYTHONPATH_PYCHARM_SITEPACKAGES=%installFolder%\venv\venv-qgis-!targetQgisVersion!-python%%T\Lib\site-packages
    echo Adding PyCharm Python%%T site-packages to front of PYTHONPATH: !PYTHONPATH_PYCHARM_SITEPACKAGES!
    set PYTHONPATH=!PYTHONPATH_PYCHARM_SITEPACKAGES!;!PYTHONPATH!
    goto setupStandalone2
  )
)
rem Warning because could not find PyCharm venv Python
echo Error: could not find Python37 or Python36 in %installFolder%\venv\venv-qgis-!targetQgisVersion! for site-packages
goto exit1

:setupStandalone2

rem Add the GeoProcessor to the PYTHONPATH
rem - OK to put at the front because geoprocessor should not conflict with anything else
set GEOPROCESSOR_HOME=%installFolder%
echo Adding GeoProcessor Python developer code to start of PYTHONPATH:  %GEOPROCESSOR_HOME%
set PYTHONPATH=%GEOPROCESSOR_HOME%;!PYTHONPATH!

rem Indicate that the setup has been completed
rem - this will ensure that the script when run again does not repeat setup
rem   and keep appending to environment variables
set SA_GP_ENV_SETUP=YES

rem Set the window title to indicate how configured so as to avoid confusion
title GeoProcessor standalone QGIS development environment to run gpdev.bat and gpuidev.bat (don't run gp.bat or gpui.bat)
echo ...done defining QGIS GeoProcessor environment
goto runStandaloneQgis2

rem ========== END GeoProcessor setup steps to be done once ===========================
rem ===================================================================================

:noStandaloneQgis

rem QGIS install folder was not found
echo QGIS standard installation folder was not found:  %QGIS_SA_INSTALL_HOME%
goto exit1

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
title GeoProcessor standalone QGIS development environment to run gpdev.bat and gpuidev.bat (don't run gp.bat or gpui.bat)

if "!doPrintEnv!"=="yes" (
  rem Run the geoprocessor.app.printenv program, useful for troubleshooting
  "!PYTHONHOME!\python.exe" -m geoprocessor.app.printenv %*
)

rem Run QGIS Python with the geoprocessor module found using PYTHONPATH set above.
rem - The Python version is compatible with QGIS.
rem - Pass command line arguments that were passed to this bat file.
rem Use -v to see verbose list of modules that are loaded.
if "!runPython!"=="yes" (
  rem Run Python with the GeoProcessor environment but not the GeoProcessor.

  rem Run the following to use the environment but be able to do imports, etc. to find modules
  echo Running Python directly in GeoProcessor environment.
  echo Use Python language syntax at the prompt.
  echo.
  rem "%PYTHONHOME%\python" -v %*
  rem Don't pass command line options because Python tries to interpret.
  "%PYTHONHOME%\python.exe"
) else (
  echo.
  echo Running:  "%PYTHONHOME%\python" -m geoprocessor.app.gp %*
  echo If errors result due to missing packages,
  echo install those packages in the PyCharm venv and report to developers.
  echo Start-up may be slow if virus scanner needs to check.
  echo.
  rem Run the full GeoProcessor.
  "%PYTHONHOME%\python.exe" -m geoprocessor.app.gp %*
  rem "%PYTHONHOME%\python" -m geoprocessor.app.gp %*

  rem Use the following for troubleshooting
  rem "%PYTHONHOME%\python" -m geoprocessor.app.printenv %*
)

rem Exit with the error level of the Python command
echo Exiting gpdev.bat with exit code %ERRORLEVEL%
exit /b %ERRORLEVEL%

rem =======================================================================
rem Below here are one-off goto targets that each end with exit

:printUsage
rem Print the program usage
echo.
echo Usage:  gpdev.bat [options]
echo.
echo Run the GeoProcessor in the development environment on Windows.
echo This batch file sets up the development environment and calls the Python GeoProcessor.
echo All command line options for the batch file are also passed to the GeoProcessor.
echo.
echo /h         Print usage of this gpdev.bat batch file.
echo /o         Use the OSGeo4W version of QGIS.
echo /python    Run Python in the GeoProcessor environment.
echo /printenv  Print the environment in addition to running the GeoProcessor.
echo /s         Use the standalone version of QGIS - default rather than /o.
echo /sN.N      Use the standalone version N.N of QGIS, for example 3.10
echo /v         Print version of this gpdev.bat batch file.
echo.
echo The following are understood by the GeoProcessor software:
echo.
echo --commands CommandFile.gp      Process a command file in batch mode.
echo --help                         Print usage for Python GeoProcessor.
echo --http                         Run GeoProcessor in HTTP server mode - under development.
echo -p PropertyName=PropertyValue  Set a processor string property.
echo --ui                           Run GeoProcessor user interface (UI).
echo -v, --version                  Print GeoProcessor version information.
echo.
got exit0

:printVersion
rem Print the program version
echo.
echo gpdev.bat version: %gpdevBatVersion% %gpdevBatVersionDate%
echo.
got exit0

:exit0
rem Exit with normal (0) exit code
rem - put this at the end of the batch file
echo Success.  Exiting with status 0.
exit /b 0

:exit1
rem Exit with general error (1) exit code
rem - put this at the end of the batch file
echo Error.  An error of some type occurred [see previous messages].  Exiting with status 1.
exit /b 1
