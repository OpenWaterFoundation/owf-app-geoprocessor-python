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
echo Setting up PyCharm environment to use QGIS Python environment
rem Where QGIS is installed
SET OSGEO4W_ROOT=C:\OSGeo4W64
rem Set the QGIS environment by calling the setup script that is distributed with QGIS 
CALL %OSGEO4W_ROOT%\bin\o4w_env.bat

rem Name of QGIS version to run (**for running OWF GeoProcessor don't run QGIS
rem but need to use correct QGIS components**).
rem Run the latest release of the OSGeo4W QGIS by setting value to `qgis`.
rem Run the long term release of the OSGeo4W QGIS by setting value to `qgis-ltr`.
rem The QGIS OSGeo4W64 installer as of February 23, 2018 installs QGIS version 3 as `qgis`, which still has issues.
rem Therefore, this script defaults to using the long-term-release version if it exists.
rem If someone is still using an older version (pre version 3), then gp-ltr.bat will not be available,
rem and `qgis` should be used.
rem The main issue will be if someone installs the new version (post February 23, 2018) and does not do the
rem advanced install to select the LTR for install, then they only get QGIS version 3,
rem which is not currently available.
rem This batch file could be updated to print an intelligent message for that case.
rem Old default:
rem SET QGISNAME=qgis
rem New default:
rem SET QGISNAME=qgis-ltr
set _qgisLTR=%OSGEO4W_ROOT%\bin\qgis-ltr.bat

rem Run LTR version if it is available.
if exist %_qgisLtr% set QGISNAME=qgis-ltr
rem Else run base/latest version if it is available.
if not exist %_qgisLtr% set QGISNAME=qgis
echo QGISNAME is %QGISNAME%

rem Absolute path to QGIS program to run 
SET QGIS=%OSGEO4W_ROOT%\apps\%QGISNAME%
rem Not sure what the following is used for but include in case PyCharm or QGIS uses 
SET QGIS_PREFIX_PATH=%QGIS%
rem Set the absolute path to PyCharm program 
rem SET PYCHARM="C:\Program Files (x86)\JetBrains\PyCharm 3.0\bin\pycharm.exe"
rem SET PYCHARM="C:\Program Files (x86)\JetBrains\PyCharm Community Edition 2016.2.3\bin\pycharm.exe"
SET PYCHARM="C:\Program Files\JetBrains\PyCharm Community Edition 2018.1.3\bin\pycharm64.exe"
if not exist %PYCHARM% goto nopycharm

rem Add QGIS to the PATH environmental variable so that all QGIS, GDAL, OGR, etc. programs are found
SET PATH=%PATH%;%QGIS%\bin

rem Add pyQGIS libraries to the PYTHONPATH so that they are found by Python
rem - Currently only QGIS 2.X with Python 2.X is supported
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python\plugins
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\Python27\Lib\site-packages

rem Set the environment variable that lets this batch file know that the environment is set up
set PYCHARM_GEOPROCESSOR_ENV_SETUP=YES

:run

echo PYTHONPATH=%PYTHONPATH%

rem Start the PyCharm IDE, /B indicates to use the same windows
rem - command line parameters passed to this script will be passed to PyCharm 
rem - PyCharm will use the Python interpreter configured for the project
echo Starting PyCharm using %PYCHARM%
start "PyCharm aware of QGIS" /B %PYCHARM% %*
goto end

:nopycharm
rem Expected PyCharm was not found
echo PyCharm was not found:  %PYCHARM%
echo Try running a different run script.
rem goto end

:end
