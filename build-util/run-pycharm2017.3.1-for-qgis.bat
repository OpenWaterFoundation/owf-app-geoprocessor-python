@echo off
rem Batch file to set the environment for running PyCharm consistent with QGIS environment
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
@echo on
echo Setting up PyCharm environment to use QGIS Python environment
@echo off
rem Where QGIS is installed
SET OSGEO4W_ROOT=C:\OSGeo4W64
rem Set the QGIS environment by calling the setup script that is distributed with QGIS 
CALL %OSGEO4W_ROOT%\bin\o4w_env.bat

rem Name of QGIS program to run 
SET QGISNAME=qgis
rem Absolute path to QGIS program to run 
SET QGIS=%OSGEO4W_ROOT%\apps\%QGISNAME%
rem Not sure what the following is used for but include in case PyCharm or QGIS uses 
SET QGIS_PREFIX_PATH=%QGIS%
rem Set the absolute path to PyCharm program 
rem SET PYCHARM="C:\Program Files (x86)\JetBrains\PyCharm 3.0\bin\pycharm.exe"
rem SET PYCHARM="C:\Program Files (x86)\JetBrains\PyCharm Community Edition 2016.2.3\bin\pycharm.exe"
SET PYCHARM="C:\Program Files\JetBrains\PyCharm Community Edition 2017.3.1\bin\pycharm64.exe"

rem Add QGIS to the PATH environmental varibale so taht all QGIS, GDAL, OGR, etc. programs are found
SET PATH=%PATH%;%QGIS%\bin

rem Add pyQGIS libraries to the PYTHONPATH so that they are found by Python
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python\plugins
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\Python27\Lib\site-packages

rem Set the environment variable that lets this batch file know that the environment is set up
set PYCHARM_GEOPROCESSOR_ENV_SETUP=YES

:run

@echo on
echo PYTHONPATH=%PYTHONPATH%

@echo off
rem Start the PyCharm IDE, /B indicates to use the same windows
rem - command line parameters passed to this script will be passed to PyCharm 
rem - PyCharm will use the Python interpreter configured for the project
@echo on
echo Starting PyCharm using %PYCHARM%
@echo off
start "PyCharm aware of QGIS" /B %PYCHARM% %*
