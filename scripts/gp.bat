rem @echo off
rem gp.bat - run the GeoProcessor
rem - the default is to start the interpreter but can run gpui.bat to run UI
rem
rem _________________________________________________________________NoticeStart_
rem GeoProcessor
rem Copyright (C) 2017-2019 Open Water Foundation
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
rem - This script is for Python3/QGIS3 (QGIS LTR is not used)
rem - The script handles OSGeo4W64 or standalone installation
rem - Checks are done for Python 3.6 and 3.7, with latest used, to accommodate QGIS versions.
rem - This script should work on a normal Windows 7/10 computer.
rem - This script and GeoProcessor should be installed in a Python Virtual Machine environment.
rem
rem Determine the folder that the script was called in
rem - includes the trailing backslash
set scriptFolder=%~dp0

rem Figure out whether to run the C:\OSGeo4W64 or C:\Program Files\QGIS N.N version
rem - Ideally the most recent compatible version is used (but may be hard to code in .bat file)
rem - Ideally also allow user to indicate which QGIS version to use
rem - For now, if standalone version is OK, use it
rem - Most users will only have one or the other installed

rem Testing standalone install is more difficult because the product version is in the path
rem - Try to future-proof by checking QGIS versions that have not yet been released
if exist "C:\Program Files\QGIS 3.12" goto runStandaloneQgis
if exist "C:\Program Files\QGIS 3.11" goto runStandaloneQgis
if exist "C:\Program Files\QGIS 3.10" goto runStandaloneQgis
if exist "C:\Program Files\QGIS 3.9" goto runStandaloneQgis
if exist "C:\Program Files\QGIS 3.8" goto runStandaloneQgis
if exist "C:\Program Files\QGIS 3.7" goto runStandaloneQgis
if exist "C:\Program Files\QGIS 3.6" goto runStandaloneQgis
if exist "C:\Program Files\QGIS 3.5" goto runStandaloneQgis
if exist "C:\Program Files\QGIS 3.4" goto runStandaloneQgis

rem Easier to test OSGeo4W because no product version in path
SET QGIS_INSTALL_HOME=C:\OSGeo4W64
SET OSGEO4W_ROOT=%QGIS_INSTALL_HOME%
if exist "%OSGEO4W_ROOT%\apps\Python37" goto runOsgeoQgis
if exist "%OSGEO4W_ROOT%\apps\Python36" goto runOsgeoQgis

goto qgisVersionUnknown

:runOsgeoQgis
rem Run the OSGeo4W64 version of QGIS
echo.
echo Running OSGeo4W64 version of QGIS...

rem Set the Python environment to find the correct run-time libraries
rem - QGIS Python environment is used and add GeoProcessor to site-packages
rem - The OSGEO_GP_ENV_SETUP environment variable is set to YES
rem   to indicate that setup has been done.
rem - This causes setup to occur only once if rerunning this batch file.

if "%OSGEO_GP_ENV_SETUP%"=="YES" GOTO runOsgeoQgis2
rem ===================================================================================
rem If here do the setup one time first time batch file is run in a command shell
echo Start defining OSGeo4W QGIS GeoProcessor environment...

rem Where QGIS is installed
if not exist "%QGIS_INSTALL_HOME%" GOTO noOsgeoQgis

rem Set the QGIS environment by calling the setup batch files that are distributed with QGIS
rem - the following will reset the PATH and then add QGIS folders to path
rem - therefore other programs that were found before may not be found
rem - this effectively isolates QGIS from the system
call "%OSGEO4W_ROOT%\bin\o4w_env.bat"
rem The following sets a number of QT environment variables (QT is used in the UI)
call "%OSGEO4W_ROOT%\bin\qt5_env.bat"
rem The following sets:
rem - PYTHONHOME to Python shipped with QGIS
rem - Clears PYTHONPATH
rem - PATH to include Python shipped with QGIS and Python scripts folder
call "%OSGEO4W_ROOT%\bin\py3_env.bat"

rem Name of QGIS version to run (**for running GeoProcessor don't run QGIS but need to use correct QGIS components**).
rem Run the latest release of the OSGeo4W QGIS by setting value to `qgis`.
rem Running the long-term release of the OSGeo4W QGIS by setting value to `qgis-ltr` is not supported.
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
set PYTHONPATH=%OSGEO4W_ROOT%\apps\%QGISNAME%\python;%PYTHONPATH%
rem See https://anitagraser.com/2018/01/28/porting-processing-scripts-to-qgis3/
set PYTHONPATH=%OSGEO4W_ROOT%\apps\%QGISNAME%\python\plugins;%PYTHONPATH%

rem List the following in order so most recent is at the end
if exist "%OSGEO4W_ROOT%\apps\Python36" set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python36\lib\site-packages;%PYTHONPATH%
if exist "%OSGEO4W_ROOT%\apps\Python37" set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python37\lib\site-packages;%PYTHONPATH%

rem Add the GeoProcessor to the PYTHONPATH
rem - put at the end of PYTHONPATH because the venv includes another copy of Python and don't want conflicts with QGIS
set gpSitePackagesFolder=%scriptFolder%..\Lib\site-packages
set PYTHONPATH=%PYTHONPATH%;%gpSitePackagesFolder%

rem Indicate that the setup has been completed
rem - this will ensure that the script when run again does not repeat setup
rem   and keep appending to environment variables
set OSGEO_GP_ENV_SETUP=YES
echo ...done defining QGIS GeoProcessor environment
goto runOsgeoQgis2

rem ========== END GeoProcessor setup steps to be done once ===========================
rem ===================================================================================

:noOsgeoQgis

rem QGIS install folder was not found
echo QGIS standard installation folder was not found:  %QGIS_INSTALL_HOME%
exit /b 1

:runOsgeoQgis2

rem Echo environment variables for troubleshooting
echo.
echo Using Python3/QGIS3 for GeoProcessor
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
"%PYTHONHOME%\python" -m geoprocessor.app.gp %*

rem Run the following to use the environment but be able to do imports, etc. to find modules
rem "%PYTHONHOME%\python" -v

rem Exit with the error level of the Python command
exit /b %ERRORLEVEL%

:runStandaloneQgis
rem Run the standalone version of QGIS
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
call "%QGIS_SA_ROOT%\bin\o4w_env.bat"
rem The following sets a number of QT environment variables (QT is used in the UI)
rem - same batch file name as for OSGeo4W install
call "%QGIS_SA_ROOT%\bin\qt5_env.bat"
rem The following sets:
rem - PYTHONHOME to Python shipped with QGIS install
rem - Clears PYTHONPATH
rem - PATH to include Python shipped with QGIS and Python scripts folder
rem - same batch file name as for OSGeo4W install
call "%QGIS_SA_ROOT%\bin\py3_env.bat"

rem Name of QGIS version to run (**for running GeoProcessor don't run QGIS but need to use correct QGIS components**).
rem Run the latest release of the OSGeo4W QGIS by setting value to `qgis`.
rem Running the long-term release of the OSGeo4W QGIS by setting value to `qgis-ltr` is not supported.
SET QGIS_SA_NAME=qgis
echo QGIS_SA_NAME is %QGIS_SA_NAME%

rem Add QGIS to the PATH environment variable so that all QGIS, GDAL, OGR, etc. programs are found.
set PATH=%QGIS_SA_ROOT%\bin;%PATH%
set PATH=%PATH%;%QGIS_SA_ROOT%\apps\%QGIS_SA_NAME%\bin

set QGIS_SA_PREFIX_PATH=%QGIS_SA_ROOT%\apps\%QGIS_SA_NAME%
set GDAL_FILENAME_IS_UTF8=YES
rem --
rem Set VSI cache to be used as buffer, see https://issues.qgis.org/issues/6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
rem --

set QT_PLUGIN_PATH=%QGIS_SA_ROOT%\apps\%QGIS_SA_NAME%\qtplugins;%QGIS_SA_ROOT%\apps\qt5\plugins

rem Add pyQGIS libraries to the PYTHONPATH so that they are found by Python
set PYTHONPATH=%QGIS_SA_ROOT%\apps\%QGIS_SA_NAME%\python;%PYTHONPATH%
rem See https://anitagraser.com/2018/01/28/porting-processing-scripts-to-qgis3/
set PYTHONPATH=%QGIS_SA_ROOT%\apps\%QGIS_SA_NAME%\python\plugins;%PYTHONPATH%

rem List the following in order so most recent is at the end
if exist %QGIS_SA_ROOT%\apps\Python36 set PYTHONPATH=%QGIS_SA_ROOT%\apps\Python36\lib\site-packages;%PYTHONPATH%
if exist %QGIS_SA_ROOT%\apps\Python37 set PYTHONPATH=%QGIS_SA_ROOT%\apps\Python37\lib\site-packages;%PYTHONPATH%

rem Add the GeoProcessor to the PYTHONPATH
rem - put at the end of PYTHONPATH because the venv includes another copy of Python and don't want conflicts with QGIS
set gpSitePackagesFolder=%scriptFolder%..\Lib\site-packages
set PYTHONPATH=%PYTHONPATH%;%gpSitePackagesFolder%

rem Indicate that the setup has been completed
rem - this will ensure that the script when run again does not repeat setup
rem   and keep appending to environment variables
set SA_GP_ENV_SETUP=YES
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
"%PYTHONHOME%\python" -m geoprocessor.app.gp %*

rem Run the following to use the environment but be able to do imports, etc. to find modules
rem "%PYTHONHOME%\python" -v

rem Exit with the error level of the Python command
exit /b %ERRORLEVEL%

:qgisVersionUnknown
rem The QGIS version is not know, used by OSGeo4W and standalone QGIS
echo.
echo Don't know how to run QGIS version.
echo C:\OSGeo4W64 and C:\Program Files\QGIS *\ for Python 3.6 or 3.7 not found.
ecit /b 1
