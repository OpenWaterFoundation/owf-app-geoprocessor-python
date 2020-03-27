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

rem Determine the folder that the script exists in
rem - used to provide path relative to the GeoProcessor files
rem - includes the trailing backslash
set scriptFolder=%~dp0
echo gpdev.bat is installed in: %scriptFolder%

rem The script version can be different from the GeoProcessor Python version
rem - this version is just used to help track changes to this script
set gpdevBatVersion=1.1.0
set gpdevBatVersionDate=2020-03-26

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

if "%1%"=="/o" goto runOsgeoQgis
if "%2%"=="/o" goto runOsgeoQgis

if "%1%"=="/s" goto runStandaloneQgis
if "%2%"=="/s" goto runStandaloneQgis

if "%1%"=="/v" goto printVersion
if "%2%"=="/v" goto printVersion

if "%1%"=="/?" goto printUsage
if "%2%"=="/?" goto printUsage

rem Options that specify the standalone QGIS version to use.
rem - the requested version will be confirmed below
if "%1%"=="/s3.10" (
  echo Command line parameter /s3.10 detected.  Will run stand-alone QGIS 3.10
  set targetQgisVersion=3.10
  goto runStandaloneQgis
)
if "%2%"=="/s3.10" (
  echo Command line parameter /s3.10 detected.  Will run stand-alone QGIS 3.10
  set targetQgisVersion=3.10
  goto runStandaloneQgis
)
if "%1%"=="/s3.4" (
  echo Command line parameter /s3.4 detected.  Will run stand-alone QGIS 3.4
  set targetQgisVersion=3.10
  goto runStandaloneQgis
)
if "%2%"=="/s3.4" (
  echo Command line parameter /s3.4 detected.  Will run stand-alone QGIS 3.4
  set targetQgisVersion=3.10
  goto runStandaloneQgis
)

rem Figure out whether to run the C:\OSGeo4W64 or C:\Program Files\QGIS N.N version
rem - Ideally the most recent compatible version is used (but may be hard to code in .bat file)
rem - Ideally also allow user to indicate which QGIS version to use
rem - For now, if standalone version is OK, use it, indicative of a deployed system
rem - Most users will only have one or the other installed

rem The gp.bat batch file, which is used with deployed software,
rem relies on GeoProcessor-QGIS-Version.txt file to indicate GQIS version to use.
rem However, for development environment, there needs to be flexibility to run with various QGIS versions.
rem The Python virtual environment exists as .gitignore'd folder in the Git repository,
rem on Windows typically something like:
rem
rem     venv-qgis-python37               Legacy - QGIS version not clear from name.
rem     venv-qgis-3.10-python37          Variation on legacy - QGIS version clear from name.
rem     venv/venv-qgis-3.10-python37     Proposed standard, QGIS version clear and folder to avoid clutter.
rem
rem However, this batch file won't know which virtual environment or QGIS version to use without guidance.
rem Therefore, for now, list available virtual environments and allow the developer to pick.
rem This includes stand-alone QGIS installations and OSGeo4W installation (only one allowed to be installed).
rem TODO smalers 2020-03-27 need to implement default for developer and command line parameter.

rem List available QGIS
rem - see: https://ss64.org/viewtopic.php?id=910
echo Installed QGIS folders:
for /d %%a in ("C:\Program Files\QGIS *") do echo %%~fa
rem dir /a "C:\Program Files\QGIS *"
if exist "C:\OSGeo4W64\" (
  echo C:\OSGeo4W64
)
echo Specify which QGIS version to use as version like 3.10 or o for OSGeo4W64 version.
set /p targetQgisVersion="Enter GQIS version: "
echo Determined target QGIS for GeoProcessor to be version:  %targetQgisVersion%
echo Will confirm that the same QGIS version is installed.

rem See if an installed QGIS version matches the target
rem - Keep code that checks for other versions in case add a command line option to use nearest version
rem - Micro QGIS versions (e.g., 3.10.1) still seem to install into minor version folder (e.g., 3.10)
set qgisPath0=C:\Program Files\QGIS
if exist "%qgisPath0% %targetQgisVersion%" (
  goto runStandaloneQgis
) else if "%targetQgisVersion%"=="o" (
    # Run OSGeo64 QGIS
    goto runOsgeoQgis
  ) else (
    rem Else did not find a known QGIS version
    goto qgisVersionUnknown
  )
 
echo Did not find installed QGIS version %targetQgisVersion% matching GeoProcessor QGIS version.
exit /b 1

:runOsgeoQgis

rem Run the OSGeo4W64 version of QGIS
echo.
echo Using OSGeo4W64 version of QGIS...

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
exit /b 1

:runOsgeoQgis1

rem  Set the PYTHONPATH to include the geoprocessor/ folder in source files
rem  - This is used in the development environment because the package has not been installed in Python Lib/site-packages
rem  - OK to put at the front of PYTHONPATH because the folder ONLY contains GeoProcessor code, no third party packages
set GEOPROCESSOR_HOME=%scriptFolder%..
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
exit /b 1

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
echo Using standalone version of QGIS...

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
if exist "%qgisPath0% %targetQgisVersion%" (
  SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS %targetQgisVersion%
) else (
  rem TODO smalers 2020-03-26 Keep old code here as a placeholder to find "nearest" version
  if exist "C:\Program Files\QGIS 3.12" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.12
  if exist "C:\Program Files\QGIS 3.11" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.11
  if exist "C:\Program Files\QGIS 3.10" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.10
  if exist "C:\Program Files\QGIS 3.9" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.9
  if exist "C:\Program Files\QGIS 3.8" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.8
  if exist "C:\Program Files\QGIS 3.7" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.7
  if exist "C:\Program Files\QGIS 3.6" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.6
  if exist "C:\Program Files\QGIS 3.5" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.5
  if exist "C:\Program Files\QGIS 3.4" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.4
)
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
set PATH=%PATH%;%QGIS_SA_ROOT%\apps\%QGISNAME%\bin

set QGIS_PREFIX_PATH=%QGIS_SA_ROOT%\apps\%QGISNAME%
set GDAL_FILENAME_IS_UTF8=YES
rem --
rem Set VSI cache to be used as buffer, see https://issues.qgis.org/issues/6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
rem --

set QT_PLUGIN_PATH=%QGIS_SA_ROOT%\apps\%QGISNAME%\qtplugins;%QGIS_SA_ROOT%\apps\qt5\plugins

rem Add pyQGIS libraries to the PYTHONPATH so that they are found by Python
echo PYTHONPATH after QGIS setup:  %PYTHONPATH%
set PYTHONPATH_QGIS_PYTHON=%QGIS_SA_ROOT%\apps\%QGISNAME%\python
echo Adding standalone QGIS Python to front of PYTHONPATH: %PYTHONPATH_QGIS_PYTHON%
set PYTHONPATH=%PYTHONPATH_QGIS_PYTHON%;%PYTHONPATH%
rem See https://anitagraser.com/2018/01/28/porting-processing-scripts-to-qgis3/
set PYTHONPATH_QGIS_PLUGINS=%QGIS_SA_ROOT%\apps\%QGISNAME%\python\plugins
echo Adding standalone QGIS plugins to front of PYTHONPATH: %PYTHONPATH_QGIS_PLUGINS%
set PYTHONPATH=%PYTHONPATH_QGIS_PLUGINS%;%PYTHONPATH%

rem List the following in order so most recent Python for target version is found first.
rem - cannot get if else if to work so use goto
if exist %QGIS_SA_ROOT%\apps\Python37 (
  set PYTHONPATH_QGIS_SITEPACKAGES=%QGIS_SA_ROOT%\apps\Python37\Lib\site-packages
  echo Adding standalone QGIS Python37 site-packages to front of PYTHONPATH: %PYTHONPATH_QGIS_SITEPACKAGES%
  set PYTHONPATH=%PYTHONPATH_QGIS_SITEPACKAGES%;%PYTHONPATH%
  goto setupStandalone2
)
if exist %QGIS_SA_ROOT%\apps\Python36 (
  set PYTHONPATH_QGIS_SITEPACKAGES=%QGIS_SA_ROOT%\apps\Python36\Lib\site-packages
  echo Adding standalone QGIS Python36 site-packages to front of PYTHONPATH: %PYTHONPATH_QGIS_SITEPACKAGES%
  set PYTHONPATH=%PYTHONPATH_QGIS_SITEPACKAGES%;%PYTHONPATH%
  goto setupStandalone2
)
rem Warning because could not find QGIS Python
echo Error: could not find Python37 or Python36 in %QGIS_SA_ROOT%\apps
exit /b 1

:setupStandalone2

rem Add the GeoProcessor to the PYTHONPATH
rem - OK to put at the front because geoprocessor should not conflict with anything else
set GEOPROCESSOR_HOME=%scriptFolder%..
echo Adding GeoProcessor Python developer code to start of PYTHONPATH:  %GEOPROCESSOR_HOME%
set PYTHONPATH=%GEOPROCESSOR_HOME%;%PYTHONPATH%

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
exit /b 1

:runStandaloneQgis2

rem Echo environment variables for troubleshooting
echo.
echo Using Python3/standalone QGIS3 for GeoProcessor
echo Environment for Python/GeoProcessor:
echo QGIS_SA_INSTALL_HOME=%QGIS_SA_INSTALL_HOME%
echo PATH=%PATH%
echo PYTHONHOME=%PYTHONHOME%
echo PYTHONPATH=%PYTHONPATH%
echo QGIS_PREFIX_PATH=%QGIS_PREFIX_PATH%
echo QT_PLUGIN_PATH=%QT_PLUGIN_PATH%
echo.

rem Set the window title again because running commands in the window resets the title
title GeoProcessor standalone QGIS development environment to run gpdev.bat and gpuidev.bat (don't run gp.bat or gpui.bat)

rem Run QGIS Python with the geoprocessor module found using PYTHONPATH set above.
rem - The Python version is compatible with QGIS.
rem - Pass command line arguments that were passed to this bat file.
rem "%PYTHONHOME%\python" %*
rem Use -v to see verbose list of modules that are loaded.
echo.
echo Running "%PYTHONHOME%\python" -m geoprocessor.app.gp %*
echo If errors result due to missing packages,
echo install those packages in the PyCharm venv.
echo Start-up may be slow if virus scanner needs to check.
echo.
"%PYTHONHOME%\python" -m geoprocessor.app.gp %*

rem Run the following to use the environment but be able to do imports, etc. to find modules
rem "%PYTHONHOME%\python" -v

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
echo /h      Print usage of this gpdev.bat batch file.
echo /o      Use the OSGeo4W version of QGIS.
echo /s      Use the standalone version of QGIS - default rather than /o.
echo /s3.4   Use the standalone version of QGIS, using QGIS version 3.4.
echo /s3.10  Use the standalone version of QGIS, using QGIS version 3.10.
echo /v      Print version of this gpdev.bat batch file.
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
exit /b 0

:printVersion
rem Print the program version
echo.
echo gpdev.bat version %gpdevBatVersion% %gpdevBatVersionDate%
echo.
exit /b 0
