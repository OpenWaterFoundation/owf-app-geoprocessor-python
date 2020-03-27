@echo off
rem gp.bat - run the GeoProcessor
rem - the default is to start the command line interpreter but can run gpui.bat to run UI
rem
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
rem ________________________________________________________________NoticeEnd___
rem
rem Windows batch file to run the Open Water Foundation GeoProcessor application for QGIS
rem - Run in the deployed environment
rem - This batch file is used with Python3/QGIS3 (older QGIS LTR is not used)
rem - This batch file handles:
rem     - stand-alone QGIS installation used for typical users
rem     - OSGeo4W64 QGIS, which may be used by developers
rem - Checks are done for Python 3.6 and 3.7, with latest used, to accommodate QGIS versions.
rem - This batch file should work on a normal Windows 10 computer.
rem - This batch file should be installed in the Scripts folder in a
rem   GeoProcessor Python Virtual Machine environment

rem Determine the folder that this batch file exists in:
rem - used to provide path relative to the GeoProcessor files
rem - includes the trailing backslash
set scriptFolder=%~dp0
echo gp.bat is installed in: %scriptFolder%
rem TODO smalers 2020-03-27 not sure why the following does not work
rem see:  https://stackoverflow.com/questions/34942604/get-parent-directory-of-a-specific-path-in-batch-script
rem for %%a in ("%scriptFolder%") do set "installFolder=%%~dpa"
rem echo GeoProcessor is installed in: %installFolder%

rem The batch file version can be different from the GeoProcessor Python version
rem - this version is just used to help track changes to this batch file
set gpBatVersion=1.1.0
set gpBatVersionDate=2020-03-26

rem Determine which version of QGIS the GeoProcessor expects to use.
rem - for now require a match
rem - TODO smalers 2020-03-26 may add a command line option to all nearby version to be used
set targetQgisVersionFile=%scriptFolder%..\GeoProcessor-QGIS-Version.txt
if not exist "%targetQgisVersionFile%" (
  echo.
  echo Target QGIS version file does not exist:  %targetQgisVersionFile%
  echo Cannot check that the installed QGIS version is compatible with the QGIS version used by the GeoProcessor software.
  echo If necessary, create the file containing QGIS version, for example:  3.10
  echo.
  exit /b 1
)
echo Determining target QGIS version from:  %targetQgisVersionFile%
rem Get the target QGIS version from the file
rem - should be on the only non-commented line (# used for comments)
rem - assigning output of a command to a variable is UGLY in bat files
set targetQgisVersion=
set tempfile=%TEMP%\gp.temp
findstr /v # %targetQgisVersionFile% > %tempfile%
set /p targetQgisVersion=<%tempfile%
if "%targetQgisVersion%"=="" (
  echo.
  echo Unable to determine target QGIS version from file:  %targetQgisVersionFile%
  echo Cannot check that the installed QGIS version is compatible with the QGIS version used by the GeoProcessor software.
  echo If necessary, edit the file containing QGIS version, for example:  3.10
  echo.
  exit /b 1
)
echo Determined target QGIS for GeoProcessor to be version:  %targetQgisVersion%
echo Will confirm that the same QGIS version is installed.

rem Evaluate command options, using Windows-style options
rem - have to check %1% and %2% because may be called from another file such as from gpui.bat using -ui
rem - the / options are handled here, consistent with Windows
rem - the dash options will be handled by the called Python program
rem - the /o option will only try to run the OSGeo4W QGIS install,
rem   useful for development and troubleshooting
rem - the /s option will only try to run the standalone QGIS install,
rem   typically used in deployed system
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

rem Figure out whether to run the C:\OSGeo4W64 or C:\Program Files\QGIS N.N version
rem - The QGIS version should match the version used to create the virtual environment,
rem   or, use a compatible version (but this would require testing to confirm compatibility).
rem - TODO, smalers 2020-03-26 also allow user to indicate which QGIS version to use.
rem - For now, if standalone version is OK, use it, indicative of a deployed system.
rem - Most users will only have one or the other installed.

rem See if an installed QGIS version matches the target
rem - Keep code that checks for other versions in case add a command line option to use nearest version
rem - Micro QGIS versions (e.g., 3.10.1) still seem to install into minor version folder (e.g., 3.10)
set qgisPath0=C:\Program Files\QGIS
if exist "%qgisPath0% %targetQgisVersion%" (
  goto runStandaloneQgis
) else (
  rem TODO smalers 2020-03-26 Evaluate whether can find a "nearest" version that works
  rem For now this code will not match because equivalent to the above
  if "%targetQgisVersion%"=="3.4" (
    if exist "C:\Program Files\QGIS 3.4" goto runStandaloneQgis
  )
  if "%targetQgisVersion%"=="3.5" (
    if exist "C:\Program Files\QGIS 3.5" goto runStandaloneQgis
  )
  if "%targetQgisVersion%"=="3.6" (
    if exist "C:\Program Files\QGIS 3.6" goto runStandaloneQgis
  )
  if "%targetQgisVersion%"=="3.7" (
    if exist "C:\Program Files\QGIS 3.7" goto runStandaloneQgis
  )
  if "%targetQgisVersion%"=="3.8" (
    if exist "C:\Program Files\QGIS 3.8" goto runStandaloneQgis
  )
  if "%targetQgisVersion%"=="3.9" (
    if exist "C:\Program Files\QGIS 3.9" goto runStandaloneQgis
  )
  if "%targetQgisVersion%"=="3.10" (
    if exist "C:\Program Files\QGIS 3.10" goto runStandaloneQgis
  )
  if "%targetQgisVersion%"=="3.11" (
    if exist "C:\Program Files\QGIS 3.11" goto runStandaloneQgis
  )
  if "%targetQgisVersion%"=="3.12" (
    if exist "C:\Program Files\QGIS 3.12" goto runStandaloneQgis
  )
)
  
echo Did not find installed QGIS version %targetQgisVersion% matching GeoProcessor QGIS version.
echo Run with /o to check OSGeo4W for required version.
exit /b 1

rem Fall-through is the OSGeo4W installation - no product version in path
rem - Try to future-proof by checking Python versions that have not yet been released
SET QGIS_INSTALL_HOME=C:\OSGeo4W64
SET OSGEO4W_ROOT=%QGIS_INSTALL_HOME%
if exist "%OSGEO4W_ROOT%\apps\Python39" goto runOsgeoQgis
if exist "%OSGEO4W_ROOT%\apps\Python38" goto runOsgeoQgis
if exist "%OSGEO4W_ROOT%\apps\Python37" goto runOsgeoQgis
if exist "%OSGEO4W_ROOT%\apps\Python36" goto runOsgeoQgis

rem Else did not find a known QGIS version
goto qgisVersionUnknown

:runOsgeoQgis

rem Run the OSGeo4W64 version of QGIS
echo.
echo Using OSGeo4W64 version of QGIS...

rem Set the Python environment to find the correct run-time libraries
rem - QGIS Python environment is used and add GeoProcessor to site-packages
rem - The OSGEO_GP_ENV_SETUP environment variable is set to YES
rem   to indicate that setup has been done.
rem - This causes setup to occur only once if rerunning this batch file.

if "%OSGEO_GP_ENV_SETUP%"=="YES" (
  echo Environment is already set up to use OSGeo4W QGIS from previous run.  Skipping to run step...
  goto runOsgeoQgis2
)
rem ===================================================================================
rem If here do the setup one time first time batch file is run in a command shell
echo Start defining OSGeo4W QGIS GeoProcessor environment...
echo OSGeo4W QGIS is installed in:  %QGIS_INSTALL_HOME%

rem Where QGIS is installed
if not exist "%QGIS_INSTALL_HOME%" GOTO noOsgeoQgis

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
call "%OSGEO4W_ROOT%\bin\py3_env.bat"

rem Name of QGIS version to run (**for running GeoProcessor don't run QGIS but need to use correct QGIS components**).
rem Run the latest release of the OSGeo4W QGIS by setting value to `qgis`.
rem Using the long-term release of the OSGeo4W QGIS by setting value to `qgis-ltr` is not supported.
SET QGISNAME=qgis
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
echo Adding OsGeo4W QGIS apps to PYTHONPATH
set PYTHONPATH=%OSGEO4W_ROOT%\apps\%QGISNAME%\python;%PYTHONPATH%
rem See https://anitagraser.com/2018/01/28/porting-processing-scripts-to-qgis3/
echo Adding OsGeo4W QGIS plugins to PYTHONPATH
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

rem Add the GeoProcessor to the PYTHONPATH via `Lib\site-packages` (geoprocessor folder exists here)
rem - put at the end of PYTHONPATH because the venv includes another copy of Python and don't want conflicts with QGIS
echo Adding GeoProcessor Python site-packages to PYTHONPATH
set gpSitePackagesFolder=%scriptFolder%..\Lib\site-packages
set PYTHONPATH=%PYTHONPATH%;%gpSitePackagesFolder%

rem Indicate that the setup has been completed
rem - this will ensure that the batch file when run again does not repeat setup
rem   and keep appending to environment variables
set OSGEO_GP_ENV_SETUP=YES

rem Set the window title to indicate how configured so as to avoid confusion
title GeoProcessor OSGeo4W QGIS environment to run gp.bat and gpui.bat (don't run gpdev.bat or gpuidev.bat)
echo ...done defining QGIS GeoProcessor environment (done once per command shell window) 
goto runOsgeoQgis2

rem ========== END GeoProcessor setup steps to be done once ===========================
rem ===================================================================================

:noOsgeoQgis

rem QGIS install folder was not found
echo OSGeo4W64 QGIS standard installation folder was not found:  %QGIS_INSTALL_HOME%
exit /b 1

:runOsgeoQgis2

rem If here then the environment has been configured.
rem Echo environment variables for troubleshooting
echo.
echo Using OSGeo4W Python3/QGIS3 for GeoProcessor.
echo Environment for Python/GeoProcessor:
echo PATH=%PATH%
echo PYTHONHOME=%PYTHONHOME%
echo PYTHONPATH=%PYTHONPATH%
echo QGIS_PREFIX_PATH=%QGIS_PREFIX_PATH%
echo QT_PLUGIN_PATH=%QT_PLUGIN_PATH%
echo.

rem Set the window title again because running commands in the window resets the title
title GeoProcessor OSGeo4W QGIS environment to run gp.bat and gpui.bat (don't run gpdev.bat or gpuidev.bat)

rem Run QGIS Python with the geoprocessor module found using PYTHONPATH set above.
rem - Must use Python 3.6+ compatible with QGIS
rem - Pass command line arguments that were passed to this bat file.
rem "%PYTHONHOME%\python" %*
rem Use -v to see verbose list of modules that are loaded.
echo Running "%PYTHONHOME%\python" -m geoprocessor.app.gp %*
echo Startup may be slow if virus scanner needs to check.
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
rem - QGIS Python environment is used and add GeoProcessor to site-packages
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
  if exist "C:\Program Files\QGIS 3.4" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.4
  if exist "C:\Program Files\QGIS 3.5" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.5
  if exist "C:\Program Files\QGIS 3.6" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.6
  if exist "C:\Program Files\QGIS 3.7" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.7
  if exist "C:\Program Files\QGIS 3.8" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.8
  if exist "C:\Program Files\QGIS 3.9" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.9
  if exist "C:\Program Files\QGIS 3.10" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.10
  if exist "C:\Program Files\QGIS 3.11" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.11
  if exist "C:\Program Files\QGIS 3.12" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.12
)
SET QGIS_SA_ROOT=%QGIS_SA_INSTALL_HOME%
echo Running GeoProcessor using standalone GQGIS in:  %QGIS_SA_INSTALL_HOME%

rem Where QGIS is installed
if not exist "%QGIS_SA_INSTALL_HOME%" goto noStandaloneQgis

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
if exist %QGIS_SA_ROOT%\apps\Python37\ (
  set PYTHONPATH_QGIS_SITEPACKAGES=%QGIS_SA_ROOT%\apps\Python37\Lib\site-packages
  echo Adding standalone QGIS Python37 site-packages to front of PYTHONPATH: %PYTHONPATH_QGIS_SITEPACKAGES%
  set PYTHONPATH=%PYTHONPATH_QGIS_SITEPACKAGES%;%PYTHONPATH%
  goto setupStandalone2
)
if exist %QGIS_SA_ROOT%\apps\Python36\ (
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
rem - put at the end of PYTHONPATH because the venv includes another copy of Python and don't want conflicts with QGIS
rem - this may lead to duplicate ;; if PYTHONPATH is empty after QGIS configuration
set gpSitePackagesFolder=%scriptFolder%..\Lib\site-packages
echo Adding GeoProcessor Python site-packages to end of PYTHONPATH:  %gpSitePackagesFolder%
set PYTHONPATH=%PYTHONPATH%;%gpSitePackagesFolder%

rem Indicate that the setup has been completed
rem - this will ensure that the script when run again does not repeat setup
rem   and keep appending to environment variables
set SA_GP_ENV_SETUP=YES

rem Set the window title to indicate how configured so as to avoid confusion
title GeoProcessor standalone QGIS environment to run gp.bat and gpui.bat (don't run gpdev.bat or gpuidev.bat)
echo ...done defining QGIS GeoProcessor environment
goto runStandaloneQgis2

rem ========== END GeoProcessor setup steps to be done once ===========================
rem ===================================================================================

:noStandaloneQgis

rem QGIS install folder was not found
echo QGIS standalone installation folder was not found:  %QGIS_SA_INSTALL_HOME%
exit /b 1

:runStandaloneQgis2

rem Echo environment variables for troubleshooting
echo.
echo Using Python3/standalone QGIS3 for GeoProcessor.
echo Environment for Python/GeoProcessor:
echo QGIS_SA_INSTALL_HOME=%QGIS_SA_INSTALL_HOME%
echo PATH=%PATH%
echo PYTHONHOME=%PYTHONHOME%
echo PYTHONPATH=%PYTHONPATH%
echo QGIS_PREFIX_PATH=%QGIS_PREFIX_PATH%
echo QT_PLUGIN_PATH=%QT_PLUGIN_PATH%
echo.

rem Set the window title again because running commands in the window resets the title
title GeoProcessor standalone QGIS environment to run gp.bat and gpui.bat (don't run gpdev.bat or gpuidev.bat)

rem Run QGIS Python with the geoprocessor module found using PYTHONPATH set above.
rem - The Python version is compatible with QGIS.
rem - Pass command line arguments that were passed to this bat file.
rem "%PYTHONHOME%\python" %*
rem Use -v to see verbose list of modules that are loaded.
echo.
echo Running:  %PYTHONHOME%\python -m geoprocessor.app.gp %*
echo If errors result due to missing packages,
echo install those packages in the venv and report to developers.
echo Start-up may be slow if virus scanner needs to check.
echo.
"%PYTHONHOME%\python" -m geoprocessor.app.gp %*

rem Run the following to use the environment but be able to do imports, etc. to find modules
rem "%PYTHONHOME%\python" -v

rem Exit with the error level of the Python command
echo Exiting gp.bat with exit code %ERRORLEVEL%
exit /b %ERRORLEVEL%

rem =======================================================================
rem Below here are one-off goto targets that each end with exit

:printUsage
rem Print the program usage
echo.
echo Usage:  gp.bat [options]
echo.
echo Run the GeoProcessor in deployed environment on Windows.
echo This batch file sets up the deployed environment and calls the Python GeoProcessor.
echo All command line options for the batch file are also passed to the Python GeoProcessor.
echo.
echo -h    Print usage for Python GeoProcessor.
echo /h    Print usage of this gp.bat batch file.
echo /o    Use the OSGeo4W version of QGIS.
echo /s    Use the standalone version of QGIS - default rather than /o.
echo /v    Print version of this gp.bat batch file.
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
echo gp.bat version %gpBatVersion% %gpBatVersionDate%
echo.
exit /b 0

:qgisVersionUnknown
rem The QGIS version is not know, used by OSGeo4W and standalone QGIS
echo.
echo Don't know how to run QGIS version.
echo C:\OSGeo4W64 and C:\Program Files\QGIS *\ for Python 3.6 or 3.7 not found.
exit /b 1
