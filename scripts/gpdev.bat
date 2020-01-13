@echo off
rem gpdev.bat
rem - the default is to start the interpreter but can run gpuidev.bat to run the UI
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
rem - This script is used with Python3/QGIS3
rem - This uses the QGIS Python as the interpreter, but development geoprocessor module via PYTHONPATH.
rem - Paths to files are assumed based on standard OWF development environment.
rem - The script handles OSGeo4W64 and standalone QGIS installation
rem - The current focus is to run on a Windows 7/10 development environment.

rem Set the Python environment to find the correct run-time libraries
rem - The GEOPROCESSOR_ENV_SETUP environment variable is set to YES
rem   to indicate that setup has been done.
rem - This causes setup to occur only once if rerunning this batch file.

rem Determine the folder that the script exists in
rem - used to provide path relative to the GeoProcessor files
rem - includes the trailing backslash
set scriptFolder=%~dp0

rem The script version can be different from the GeoProcessor Python version
rem - this version is just used to help track changes to this script
set gpdevBatVersion=1.0.0
set gpdevBatVersionDate=2019-01-11

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

rem Default is to run the OSGeo4W version, which should be installed by developers
rem - may enhance later similar to gp.bat to pick the most recent QGIS
:runOsgeoQgis
if "%GEOPROCESSOR_DEV_ENV_SETUP%"=="YES" GOTO runOsgeoQgis2
rem ===================================================================================
rem If here do the setup one time first time batch file is run in a command shell
echo Start defining QGIS GeoProcessor environment (done once per command shell window)...

rem Where QGIS is installed
SET OSGEO4W_ROOT=C:\OSGeo4W64
echo OSGEO4W_ROOT=%OSGEO4W_ROOT%
if not exist %OSGEO4W_ROOT% GOTO noOsgeoQgis

rem Set the QGIS environment by calling the setup batch files that are distributed with QGIS
rem - the following will reset the PATH and then add QGIS folders to path
rem - therefore other programs that were found before may not be found
rem - this effectively isolates QGIS from the system
call %OSGEO4W_ROOT%\bin\o4w_env.bat
rem The following sets a number of QT environment variables (QT is used in the UI)
call %OSGEO4W_ROOT%\bin\qt5_env.bat
rem The following sets:
rem - PYTHONHOME to Python shipped with QGIS
rem - Clears PYTHONPATH
rem - PATH to include Python shipped with QGIS and Python scripts folder
call %OSGEO4W_ROOT%\bin\py3_env.bat

rem Name of QGIS version to run (**for running OWF GeoProcessor don't run QGIS but need to use correct QGIS components**).
rem Run the latest release of the OSGeo4W QGIS by setting value to `qgis`.
rem Running the long-term release of the OSGeo4W QGIS by setting value to `qgis-ltr` is not supported.
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
rem List the following in order so most recent is at the end
if exist %OSGEO4W_ROOT%\apps\Python36 set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python36\lib\site-packages;%PYTHONPATH%
if exist %OSGEO4W_ROOT%\apps\Python37 set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python37\lib\site-packages;%PYTHONPATH%

rem  Set the PYTHONPATH to include the geoprocessor module
rem  - This is used in the development environment because the package has not been installed in site-packages
rem  - Folder for libraries must contain "geoprocessor" since modules being searched for will start with that.
set GEOPROCESSOR_HOME=%scriptFolder%..
set PYTHONPATH=%GEOPROCESSOR_HOME%;%PYTHONPATH%

rem Indicate that the setup has been completed
rem - this will ensure that the script when run again does not repeat setup
rem   and keep appending to environment variables
set GEOPROCESSOR_DEV_ENV_SETUP=YES

rem Set the window title to indicate how configured so as to avoid confusion
title GeoProcessor OSGeo4W QGIS development environment to run gpdev.bat and gpuidev.bat (don't run gp.bat or gpui.bat)
echo ...done defining QGIS GeoProcessor environment (done once per command shell window)
goto runOsgeoQgis2

rem ========== END GeoProcessor setup steps to be done once ===========================
rem ===================================================================================

:noOsgeoQgis

rem QGIS install folder was not found
echo QGIS standard installation folder was not found:  %OSGEO4W_ROOT%
exit /b 1

:runOsgeoQgis2

rem Echo environment variables for troubleshooting
echo.
echo Using OSGeo4W Python3/QGIS3 for GeoProcessor
echo PATH=%PATH%
echo PYTHONHOME=%PYTHONHOME%
echo PYTHONPATH=%PYTHONPATH%
echo QGIS_PREFIX_PATH=%QGIS_PREFIX_PATH%
echo QT_PLUGIN_PATH=%QT_PLUGIN_PATH%
echo.

rem Run QGIS Python with the geoprocessor module found using PYTHONPATH set above.
rem - Must use Python 3.6 compatible with QGIS
rem - Pass command line arguments that were passed to this bat file.
rem "%PYTHONHOME%\python" %*
rem Use -v to see verbose list of modules that are loaded.
echo Running "%PYTHONHOME%\python" -m geoprocessor.app.gp %*
"%PYTHONHOME%\python" -m geoprocessor.app.gp %*

rem Run the following to use the environment but be able to do imports, etc. to find modules
rem "%PYTHONHOME%\python" -v

rem Exit with the error level of the Python command
exit /b %ERRORLEVEL%

:runStandaloneQgis
rem Run the standalone version of QGIS
rem - TODO smalers 2019-01-11 this needs work because without setting up the venv
rem   third party packages like Pandas may not be found
echo.
echo Running standalone version of QGIS...

rem Set the Python environment to find the correct run-time libraries
rem - QGIS Python environment is used and add GeoProcessor to site-packages
rem - The SA_GP_ENV_SETUP environment variable is set to YES
rem   to indicate that setup has been done.
rem - This causes setup to occur only once if rerunning this batch file.

if "%SA_GP_ENV_SETUP%"=="YES" GOTO runStandaloneQgis2
rem ===================================================================================
rem If here do the setup one time first time batch file is run in a command shell
echo Start defining standalone QGIS GeoProcessor environment...

if exist "C:\Program Files\QGIS 3.12" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.12
if exist "C:\Program Files\QGIS 3.11" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.11
if exist "C:\Program Files\QGIS 3.10" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.10
if exist "C:\Program Files\QGIS 3.9" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.9
if exist "C:\Program Files\QGIS 3.8" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.8
if exist "C:\Program Files\QGIS 3.7" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.7
if exist "C:\Program Files\QGIS 3.6" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.6
if exist "C:\Program Files\QGIS 3.5" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.5
if exist "C:\Program Files\QGIS 3.4" SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS 3.4
SET QGIS_SA_ROOT=%QGIS_SA_INSTALL_HOME%

rem Where QGIS is installed
if not exist "%QGIS_SA_INSTALL_HOME%" GOTO noStandaloneQgis

rem Set the QGIS environment by calling the setup batch files that are distributed with QGIS
rem - the following will reset the PATH and then add QGIS folders to path
rem - therefore other programs that were found before may not be found
rem - this effectively isolates QGIS from the system
rem - same batch file name as for OSGeo4W install
rem echo Calling QGIS setup batch file:  %QGIS_SA_ROOT%\bin\o4w_env.bat
call "%QGIS_SA_ROOT%\bin\o4w_env.bat"
rem The following sets a number of QT environment variables (QT is used in the UI)
rem - same batch file name as for OSGeo4W install
rem echo Calling Qt setup batch file:  %QGIS_SA_ROOT%\bin\qt5_env.bat
call "%QGIS_SA_ROOT%\bin\qt5_env.bat"
rem The following sets:
rem - PYTHONHOME to Python shipped with QGIS install
rem - Clears PYTHONPATH
rem - PATH to include Python shipped with QGIS and Python scripts folder
rem - same batch file name as for OSGeo4W install
rem echo Calling Python 3 setup batch file:  %QGIS_SA_ROOT%\bin\py3_env.bat
call "%QGIS_SA_ROOT%\bin\py3_env.bat"

rem Name of QGIS version to run (**for running GeoProcessor don't run QGIS but need to use correct QGIS components**).
rem Run the latest release of the OSGeo4W QGIS by setting value to `qgis`.
rem Running the long-term release of the OSGeo4W QGIS by setting value to `qgis-ltr` is not supported.
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
set PYTHONPATH=%QGIS_SA_ROOT%\apps\%QGISNAME%\python;%PYTHONPATH%
rem See https://anitagraser.com/2018/01/28/porting-processing-scripts-to-qgis3/
set PYTHONPATH=%QGIS_SA_ROOT%\apps\%QGISNAME%\python\plugins;%PYTHONPATH%

rem List the following in order so most recent is at the end
if exist %QGIS_SA_ROOT%\apps\Python36 set PYTHONPATH=%QGIS_SA_ROOT%\apps\Python36\lib\site-packages;%PYTHONPATH%
if exist %QGIS_SA_ROOT%\apps\Python37 set PYTHONPATH=%QGIS_SA_ROOT%\apps\Python37\lib\site-packages;%PYTHONPATH%

rem Add the GeoProcessor to the PYTHONPATH
rem - put at the end of PYTHONPATH because the venv includes another copy of Python and don't want conflicts with QGIS
set GEOPROCESSOR_HOME=%scriptFolder%..
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
echo QGIS_SA_INSTALL_HOME=%QGIS_SA_INSTALL_HOME%
echo PATH=%PATH%
echo PYTHONHOME=%PYTHONHOME%
echo PYTHONPATH=%PYTHONPATH%
echo QGIS_PREFIX_PATH=%QGIS_PREFIX_PATH%
echo QT_PLUGIN_PATH=%QT_PLUGIN_PATH%
echo.

rem Run QGIS Python with the geoprocessor module found using PYTHONPATH set above.
rem - Must use Python 3.6+ compatible with QGIS
rem - Pass command line arguments that were passed to this bat file.
rem "%PYTHONHOME%\python" %*
rem Use -v to see verbose list of modules that are loaded.
echo Running "%PYTHONHOME%\python" -m geoprocessor.app.gp %*
echo If errors result due to missing packages, run in virtual environment created by build-util/2-create-gp-venv.bat.
echo Start-up may be slow if virus scanner needs to check.
echo.
"%PYTHONHOME%\python" -m geoprocessor.app.gp %*

rem Run the following to use the environment but be able to do imports, etc. to find modules
rem "%PYTHONHOME%\python" -v

rem Exit with the error level of the Python command
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
echo All command line options for the batch file are passed to the Python GeoProcessor.
echo.
echo -h    Print usage for Python GeoProcessor.
echo /h    Print usage of this gpdev.bat batch file.
echo /o    Run the OSGeo4W version of QGIS (even if standalone QGIS is available). The default.
echo /s    Run the standalone version of QGIS (even if OSGeo4W QGIS is available).
echo /v    Print version of this gpdev.bat batch file.
echo.
exit /b 0

:printVersion
rem Print the program version
echo.
echo gpdev.bat version %gpdevBatVersion% %gpdevBatVersionDate%
echo.
exit /b 0
