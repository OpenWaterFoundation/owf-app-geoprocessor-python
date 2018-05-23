@echo off

rem set the root OSGeo4W folder oath 
SET OSGEO4W_ROOT=C:\OSGeo4W64

set _qgisLTR=%OSGEO4W_ROOT%\bin\qgis-ltr.bat

rem Run LTR version if it is available.
if exist %_qgisLtr% set QGISNAME=qgis-ltr
rem Else run base/latest version if it is available.
if not exist %_qgisLtr% set QGISNAME=qgis
echo QGISNAME is %QGISNAME%


rem call the OSGeo4W-provided script to set up the 
call %OSGEO4W_ROOT%\bin\o4w_env.bat
call %OSGEO4W_ROOT%\bin\qt5_env.bat
call %OSGEO4W_ROOT%\bin\py3_env.bat
@echo off

set PATH=%OSGEO4W_ROOT%\bin;%PATH% 
set PATH=%PATH%;%OSGEO4W_ROOT%\apps\%QGISNAME%\bin

set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/%QGISNAME%
set GDAL_FILENAME_IS_UTF8=YES
rem Set VSI cache to be used as buffer, see #6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\%QGISNAME%\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
set PYTHONPATH=%OSGEO4W_ROOT%\apps\%QGISNAME%\python;%PYTHONPATH%
rem added later due to https://anitagraser.com/2018/01/28/porting-processing-scripts-to-qgis3/
set PYTHONPATH=%OSGEO4W_ROOT%\apps\%QGISNAME%\python\plugins;%PYTHONPATH%
set GEOPROCESSOR_HOME=C:\Users\%USERNAME%\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python


rem added later
set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python36\lib\site-packages;%PYTHONPATH%

set PYTHONPATH=%GEOPROCESSOR_HOME%;%PYTHONPATH%

echo %PATH%

rem "%PYTHONHOME%\python" %*
"%PYTHONHOME%\python" -m geoprocessor.app.gp %*