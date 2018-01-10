@echo off
rem Windows batch file to run the Open Water Foundation GeoProcessor application
rem - This script should eventually work on a normal Windows 7/10 computer.
rem - The current focus is to run on a Windows 10 development environment.
rem - This is currently hard-coded to work in the development environment only,
rem   with absolute paths that work from any folder but only on development machine.
rem - The resulting environment is specific to QGIS and may not be able to be used
rem   as a general Windows command prompt.

rem Set the Python environment to find the correct run-time libraries
rem - The GEOPROCESSOR_ENV_SETUP environment variable is set to YES
rem   to indicate that setup has been done.
rem - This causes setup to occur only once if rerunning this batch file.

if "%GEOPROCESSOR_ENV_SETUP%"=="YES" GOTO run
rem ===================================================================================
rem ========== START COPY FROM run*pycharm*.bat SCRIPT WITHOUT PYCHARM ================
rem
echo Start defining QGIS/OWF GeoProcessor environment...
rem Where QGIS is installed
SET OSGEO4W_ROOT=C:\OSGeo4W64
rem Set the QGIS environment by calling the setup script that is distributed with QGIS
rem - the following will reset the PATH and then add QGIS folders to path
rem - therefore other programs that were found before may not be found
CALL %OSGEO4W_ROOT%\bin\o4w_env.bat

rem Name of QGIS program to run (**but for running OWF GeoProcessor don't need to run**)
SET QGISNAME=qgis
rem Absolute path to QGIS program to run
SET QGIS=%OSGEO4W_ROOT%\apps\%QGISNAME%
rem Not sure what the following is used for but include in case PyCharm or QGIS uses
SET QGIS_PREFIX_PATH=%QGIS%

rem Add QGIS to the PATH environmental varibale so taht all QGIS, GDAL, OGR, etc. programs are found
SET PATH=%PATH%;%QGIS%\bin

rem Add pyQGIS libraries to the PYTHONPATH so that they are found by Python
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python\plugins
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\Python27\Lib\site-packages

rem ========== END COPY FROM run*pycharm*.bat SCRIPT ==================================

rem Indicate that the setup has been completed
rem - this will ensure that the script when run again does not repeat setup
rem   and keep appending to environment variables
set GEOPROCESSOR_ENV_SETUP=YES
echo ...done defining QGIS/OWF GeoProcessor environment
rem ========== START GeoProcessor Setup Steps to be done once =========================
rem QGIS Python
set QGIS_PYTHON_EXE=%OSGEO4W_ROOT%\bin\python.exe

rem Normal Python (should be Python 2.7)
set PYTHON_EXE=python

rem  Set the PYTHONPATH to include the geoprocessor module
rem  - Folder for libraries must contain "geoprocessor" since modules being searched for will start with that.
rem GEOPROCESSOR_HOME="/cygdrive/C/Users/${USERNAME}/owf-dev/GeoProcessor/git-repos/owf-app-geoprocessor-python/geoprocessor"
set GEOPROCESSOR_HOME=C:\Users\%USERNAME%\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python

set PYTHONPATH=%GEOPROCESSOR_HOME%;%PYTHONPATH%

echo PYTHONPATH=%PYTHONPATH%

rem ========== END GeoProcessor Setup Steps to be done once ===========================
rem ========== END setup steps to be done once ========================================
rem ===================================================================================

rem Below here assumes that the above environment has been setup by running in the window previously

:run

rem  Run Python on the code
rem  - must use Python 2.7 compatible with QGIS

echo Running OWF GeoProcessor application gp...

rem QGIS Python
rem The --version run works (use for testing basic setup)
rem %QGIS_PYTHON_EXE% --version
%QGIS_PYTHON_EXE% %GEOPROCESSOR_HOME%\geoprocessor\app\gp.py %*

rem Normal Python
rem %PYTHON_EXE% %GEOPROCESSOR_HOME%\geoprocessor\app\gp.py %*
