rem @echo off
rem Modified version of: C:\Program Files\QGIS 3.22.16\bin\python-qgis-ltr.bat
rem Original...
rem call "%~dp0\o4w_env.bat"
call "C:\Program Files\QGIS 3.22.16\bin\o4w_env.bat"
rem @echo off
path %OSGEO4W_ROOT%\apps\qgis-ltr\bin;%PATH%
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis-ltr
set GDAL_FILENAME_IS_UTF8=YES
rem Set VSI cache to be used as buffer, see #6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis-ltr\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
rem Original...
rem set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%PYTHONPATH%
rem New...
rem scriptFoler has \ at the end
set scriptFolder=%~dp0
rem Remove trailing \ from 'scriptFolder'.
set scriptFolder=%scriptFolder:~0,-1%
set GEOPROCESSOR=%scriptFolder%\..\src;%scriptFolder%\..\venv\venv-qgis-3.22.16-python39\Lib\site-packages
set PYTHONPATH=%OSGEO4W_ROOT%\apps\qgis-ltr\python;%OSGEO4W_ROOT%\apps\qgis-ltr\python\plugins;%GEOPROCESSOR%;%PYTHONPATH%
rem Original...
rem python %*
python -m geoprocessor.app.gp %*

