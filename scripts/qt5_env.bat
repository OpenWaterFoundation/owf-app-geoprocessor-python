rem @echo off
rem
rem This is the setup script that was distributed with QGIS 3.10 but is not included in more recent QGIS versions.
rem Run it if necessary to set up the GeoProcessor environment.
rem The environment variables are totally focused on Qt5, not Python setup.
rem Echo formatting is indented to work with calling scripts.

echo [INFO]     Start of GeoProcessor qt5_env.bat

if [] == [%OSGEO4W_ROOT%] (
  echo [ERROR]      The OSGEO4W_ROOT environment variable is not set.
  goto exit1
)

path %OSGEO4W_ROOT%\apps\Qt5\bin;%PATH%

set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\Qt5\plugins

rem Replace \ with / character:
rem - why is this done?
set O4W_QT_PREFIX=%OSGEO4W_ROOT:\=/%/apps/Qt5
set O4W_QT_BINARIES=%OSGEO4W_ROOT:\=/%/apps/Qt5/bin
set O4W_QT_PLUGINS=%OSGEO4W_ROOT:\=/%/apps/Qt5/plugins
set O4W_QT_LIBRARIES=%OSGEO4W_ROOT:\=/%/apps/Qt5/lib
set O4W_QT_TRANSLATIONS=%OSGEO4W_ROOT:\=/%/apps/Qt5/translations
set O4W_QT_HEADERS=%OSGEO4W_ROOT:\=/%/apps/Qt5/include
set O4W_QT_DOC=%OSGEO4W_ROOT:\=/%/apps/Qt5/doc

echo [INFO]     qt5_env.bat set:
echo [INFO]       OSGEO4W_ROOT = %OSGEO4W_ROOT%
echo [INFO]       O4W_QT_PREFIX = %O4W_QT_PREFIX%
echo [INFO]       O4W_QT_BINARIES = %O4W_QT_BINARIES%
echo [INFO]       O4W_QT_PLUGINS = %O4W_QT_PLUGINS%
echo [INFO]       O4W_QT_LIBRARIES = %O4W_QT_LIBRARIES%
echo [INFO]       O4W_QT_TRANSLATIONS = %O4W_QT_TRANSLATIONS%
echo [INFO]       O4W_QT_HEADERS = %O4W_QT_HEADERS%
echo [INFO]       O4W_QT_DOC = %O4W_QT_DOC%
echo [INFO]       QT_PLUGIN_PATH = %QT_PLUGIN_PATH%

rem Normal exit.
:exit0
echo [INFO]     End of GeoProcessor qt5_env.bat.  Exiting with status 0.
exit /b 0

:exit1
echo [INFO]     End of GeoProcessor qt5_env.bat.  Exiting with status 1.
exit /b 1
