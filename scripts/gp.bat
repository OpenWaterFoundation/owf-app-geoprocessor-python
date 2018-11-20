@echo off
rem gp.bat - run the GeoProcessor, default is to start the interpreter
rem
rem Windows batch file to run the Open Water Foundation GeoProcessor application for QGIS
rem - This script is for Python3/QGIS3 (QGIS LTR is not used)
rem - This script should work on a normal Windows 7/10 computer.
rem - The geoprocessor package must be installed in a normal location, such as
rem   QGIS Python site-packages folder.
rem - This script should be installed in the QGIS bin folder or other location
rem   that is in the PATH or otherwise can be executed.

rem Set the Python environment to find the correct run-time libraries
rem - The GEOPROCESSOR_ENV_SETUP environment variable is set to YES
rem   to indicate that setup has been done.
rem - This causes setup to occur only once if rerunning this batch file.

if "%GEOPROCESSOR_ENV_SETUP%"=="YES" GOTO run
rem ===================================================================================
rem If here do the setup one time first time batch file is run in a command shell
echo Start defining QGIS GeoProcessor environment...

rem Where QGIS is installed
SET QGIS_INSTALL_HOME=C:\OSGeo4W64
if not exist %QGIS_INSTALL_HOME% GOTO noqgis

rem Set the QGIS environment by calling the setup batch files that are distributed with QGIS
rem - the following will reset the PATH and then add QGIS folders to path
rem - therefore other programs that were found before may not be found
rem - this effectively isolates QGIS from the system
SET OSGEO4W_ROOT=%QGIS_INSTALL_HOME%
call %OSGEO4W_ROOT%\bin\o4w_env.bat
rem The following sets a number of QT environment variables (QT is used in the UI)
call %OSGEO4W_ROOT%\bin\qt5_env.bat
rem The following sets:
rem - PYTHONHOME to Python shipped with QGIS
rem - Clears PYTHONPATH
rem - PATH to include Python shipped with QGIS and Python scripts folder
call %OSGEO4W_ROOT%\bin\py3_env.bat

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
set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python36\lib\site-packages;%PYTHONPATH%

rem Indicate that the setup has been completed
rem - this will ensure that the script when run again does not repeat setup
rem   and keep appending to environment variables
set GEOPROCESSOR_ENV_SETUP=YES
echo ...done defining QGIS GeoProcessor environment
goto run

rem ========== END GeoProcessor setup steps to be done once ===========================
rem ===================================================================================

:noqgis

rem QGIS install folder was not found
echo QGIS standard installation folder was not found:  %QGIS_INSTALL_HOME%
exit /b 1

:run

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
