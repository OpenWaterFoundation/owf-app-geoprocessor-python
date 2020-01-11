@echo off
rem Batch file to set the environment for and run PyCharm consistent with QGIS 3 environment
rem - Use QGIS Python and libraries
rem - Start PyCharm with the configured environment

rem The following seems to be more relevant.
rem See:  http://spatialgalaxy.com/2014/10/09/a-quick-guide-to-getting-started-with-pyqgis-on-windows/
rem The following provides useful background but seems incomplete.
rem See:  http://planet.qgis.org/planet/tag/pycharm/

rem Get the current folder, used to specify the path to the project
rem - will have \ at the end
SET GP_CURRENT_DIR=%~dp0%
echo Script directory=%GP_CURRENT_DIR%

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
rem - sort with most recent last so that the newest version that is found is run
rem - this assumes that the developer is using the newest version installed for development
rem - include editions that have been specifically used by Open Water Foundation for development
rem 2018 editions
if exist "C:\Program Files\JetBrains\PyCharm Community Edition 2018.1.3\bin\pycharm64.exe" SET PYCHARM="C:\Program Files\JetBrains\PyCharm Community Edition 2018.1.3\bin\pycharm64.exe"
if exist "C:\Program Files\JetBrains\PyCharm Community Edition 2018.2.4\bin\pycharm64.exe" SET PYCHARM="C:\Program Files\JetBrains\PyCharm Community Edition 2018.2.4\bin\pycharm64.exe"
if exist "C:\Program Files\JetBrains\PyCharm Community Edition 2018.2.6\bin\pycharm64.exe" SET PYCHARM="C:\Program Files\JetBrains\PyCharm Community Edition 2018.2.6\bin\pycharm64.exe"
rem 2019 editions
if exist "C:\Program Files\JetBrains\PyCharm Community Edition 2019.3.1\bin\pycharm64.exe" SET PYCHARM="C:\Program Files\JetBrains\PyCharm Community Edition 2019.3.1\bin\pycharm64.exe"
if not exist %PYCHARM% goto nopycharm

echo Will use latest found Pycharm Community Edition: %PYCHARM%

rem Add QGIS to the PATH environment variable so that all QGIS, GDAL, OGR, etc. programs are found
SET PATH=%PATH%;%QGIS%\bin
SET PATH=%PATH%;%OSGEO4W_ROOT%\apps\Qt5\bin

rem Add pyQGIS libraries to the PYTHONPATH so that they are found by Python
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python\plugins

rem Set the Python to use
rem - list the following in order so most recent is at the end
rem - this assumes that one copy of OSGEO4W suite is installed and the latest should be used
if exist %OSGEO4W_ROOT%\apps\Python36 set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python36\lib\site-packages;%PYTHONPATH%
if exist %OSGEO4W_ROOT%\apps\Python37 set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python37\lib\site-packages;%PYTHONPATH%

rem Set the environment variable that lets this batch file know that the environment is set up
set PYCHARM_GEOPROCESSOR_ENV_SETUP=YES

rem This is the entry point of the script after set and if the script has been run before
rem - set the window title to indicate that the environment is configured
rem - TODO smalers 2020-01-10 need to set title if error occurred setting up the environment?
:run
title GeoProcessor development environment for PyCharm

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
SET GP_PROJECT_DIR=%GP_CURRENT_DIR%..
if exist %GP_PROJECT_DIR% start "PyCharm aware of QGIS" /B %PYCHARM% %GP_PROJECT_DIR% %*
if not exist %GP_PROJECT_DIR% goto noproject
goto endofbat

:noproject
rem No project directory (should not happen)
echo Project folder does not exist:  %GP_PROJECT_DIR%
echo Not starting PyCharm.
exit /b 1

:nopycharm
rem Expected PyCharm was not found
echo PyCharm was not found in expected location C:\Program Files\JetBrains\PyCharm Community Edition NNNN.N.N\bin\pycharm64.exe
echo May need to update this script for newer versions of PyCharm.
exit /b 1

:noqgisbat
rem qgis.bat was not found
echo QGIS batch file not found:  %OSGEO4W_ROOT%/bin/qgis.bat
exit /b 1

rem For some reason using "end" causes an error - reserved word?
:endofbat
