@echo off
rem Batch file to set the environment for running PyCharm consistent with QGIS 3 environment
rem - Use QGIS Python and libraries
rem - Start PyCharm with the configured environment
rem - TODO smalers 2017-12-22 Could update the batch file to
rem   intelligently figure out the correct PyCharm to run based on what is installed

rem The following seems to be more relevant.
rem See:  http://spatialgalaxy.com/2014/10/09/a-quick-guide-to-getting-started-with-pyqgis-on-windows/
rem The following provides useful background but seems incomplete.
rem See:  http://planet.qgis.org/planet/tag/pycharm/

rem Set an environment variable to indicate that the environment is setup.
rem - this ensures that setup is done once
rem - then PyCharm can be restarted in the same window without reconfiguring the environment

if "%PYCHARM_GEOPROCESSOR_ENV_SETUP%"=="YES" GOTO run
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
rem Set the absolute path to PyCharm program 
SET PYCHARM="C:\Program Files\JetBrains\PyCharm Community Edition 2018.2.4\bin\pycharm64.exe"
if not exist %PYCHARM% goto nopycharm

rem Add QGIS to the PATH environment variable so that all QGIS, GDAL, OGR, etc. programs are found
SET PATH=%PATH%;%QGIS%\bin
SET PATH=%PATH%;%OSGEO4W_ROOT%\apps\Qt5\bin

rem Add pyQGIS libraries to the PYTHONPATH so that they are found by Python
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python\plugins
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\Python36\lib\site-packages

rem Set the environment variable that lets this batch file know that the environment is set up
set PYCHARM_GEOPROCESSOR_ENV_SETUP=YES

:run

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
echo Starting PyCharm using %PYCHARM% - prompt will display and PyCharm may take a few seconds to start.
start "PyCharm aware of QGIS" /B %PYCHARM% %*
goto end

:nopycharm

rem Expected PyCharm was not found
echo PyCharm was not found:  %PYCHARM%
echo Try running a different run script.
exit /b 1

:noqgisbat

rem qgis.bat was not found
echo QGIS batch file not found:  %OSGEO4W_ROOT%/bin/qgis.bat
exit /b 1

:end
