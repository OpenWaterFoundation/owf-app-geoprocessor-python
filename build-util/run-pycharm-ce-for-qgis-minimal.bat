@echo off
rem
rem Batch file to set the environment for and run PyCharm consistent with QGIS 3 environment:
rem - this is the minimal version, with hard-coded known paths on Steve Malers' development machine
rem - this follows examples on the web but does not include all the checks in the run-pycharm-ce-for-qgis.bat
rem - the longer script is breaking so try the minimal version without the bat complexities

rem Determine the folder that the script exists in:
rem - used to provide path relative to the GeoProcessor files
set scriptFolder=%~dp0
rem Remove trailing \ from 'scriptFolder'.
set scriptFolder=%scriptFolder:~0,-1%
set scriptName=%~nx0

rem Have to get parent folder using Windows for loop approach:
rem - use 'installFolder' instead of 'repoFolder' so the naming works in the deployed environment
for %%i in (%scriptFolder%) do set installFolder=%%~dpi
rem Remove trailing \ from 'installFolder'.
set installFolder=%installFolder:~0,-1%
rem As of 2023-03-04 the code is located in the 'src' folder under the install folder.
set srcFolder=%installFolder%\src

set targetQgisVersion=3.22.16
SET QGIS_SA_INSTALL_HOME=C:\Program Files\QGIS %targetQgisVersion%
set QGIS_SA_ROOT=%QGIS_SA_INSTALL_HOME%

for %%H in ("%QGIS_SA_INSTALL_HOME%") do set QGIS_SA_INSTALL_HOME_83=%%~sH
set QGIS_SA_INSTALL_HOME=%QGIS_SA_INSTALL_HOME_83%
set QGIS_SA_ROOT=%QGIS_SA_INSTALL_HOME_83%
echo [INFO]   After conversion to 8.3 to avoid spaces in path:
echo [INFO]     Standalone install home QGIS_SA_INSTALL_HOME = %QGIS_SA_INSTALL_HOME%
echo [INFO]     Standalone install root QGIS_SA_ROOT = %QGIS_SA_ROOT%

rem Set the QGIS environment by calling the setup batch files that are distributed with QGIS:
rem
rem - the following relies on OSGEO4W_ROOT being set and will reset it to 8.3 format
rem - the 8.3 OSGEO4W_ROOT is then added to the path
rem - the path is also updated to include standard Windows programs but the previous path is lost
rem - therefore other programs that were found before may not be found
rem - this effectively isolates QGIS from the system
rem - the batch fle is the same as for OSGeo4W (non-standalone) install
echo [INFO]
echo [INFO] Setting QGIS main environment variables.
call "%QGIS_SA_ROOT%\bin\o4w_env.bat"

echo [INFO]
echo [INFO] Setting QGIS Qt environment variables.
set PATH=%QGIS_SA_ROOT%\apps\Qt5\bin;%PATH%
echo [INFO]   Calling QGIS Qt setup batch file from GeoProcessor because not found in QGIS.
echo [INFO]     %scriptFolder%\..\scripts\qt5_env.bat
call "%scriptFolder%\..\scripts\qt5_env.bat"

echo [INFO]
echo [INFO] Setting QGIS Python environment variables.
echo [INFO]   Calling QGIS Python 3 setup batch file from GeoProcessor because not found in QGIS.
echo [INFO]     %scriptFolder%\..\scripts\py3_env.bat
call %scriptFolder%\..\scripts\py3_env.bat

rem Add QGIS to the PATH environment variable so that all QGIS, GDAL, OGR, etc. programs are found.
set PATH=%QGIS_SA_ROOT%\bin;%PATH%
set GDAL_FILENAME_IS_UTF8=YES
rem --
rem Set VSI cache to be used as buffer, see https://issues.qgis.org/issues/6448
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
rem --

echo [INFO]
echo [INFO] After QGIS/Qt/Python setup:
echo [INFO]   PATH = %PATH%
echo [INFO]   PYTHONHOME = %PYTHONHOME%
echo [INFO]   PYTHONPATH = %PYTHONPATH%

rem Add QGIS 'python' and 'plugins' folders to the PYTHONPATH:
rem - old version of this batch file used %QGISNAME%, which was typically 'qgis';
rem   however, it could be 'qgis-ltr` for long term release or 'qgis-dev' for development.
rem   Therefore, the following now checks for multiple release types.
rem   See:  https://docs.qgis.org/3.4/pdf/en/QGIS-3.4-PyQGISDeveloperCookbook-en.pdf
rem - the qgis-ltr folder needs to be checked first because for a long term release
rem - the qgis-ltr/python and qgis/python folders each exist, but qgis/python is empty
rem - 'qgis-ltr' is used in several environment variables
rem The qgis-ltr is used when an LTR release was downloaded from the website:
rem - the latest release (under development) does not seem to include qgis-ltr
echo [INFO]
echo [INFO] Setting the QGIS Python app files environment variables.
set Q=qgis-ltr
    set PATH=%PATH%;%QGIS_SA_ROOT%\apps\%Q%\bin
    set QGIS_PREFIX_PATH=%QGIS_SA_ROOT%\apps\%Q%
    rem QGIS 3.22.16 uses Qt5 rather than qt5.
    set QT_PLUGIN_PATH=%QGIS_SA_ROOT%\apps\%Q%\qtplugins;%QGIS_SA_ROOT%\apps\Qt5\plugins

    rem TODO smalers 2023-03-01 The following works with QGIS 3.10:
    rem - imports must specify 'qgis' at the beginning
    set PYTHONPATH_QGIS_PYTHON=%QGIS_SA_ROOT%\apps\%Q%\python
    echo [INFO]   Adding standalone QGIS Python to front of PYTHONPATH:
    echo [INFO]     %PYTHONPATH_QGIS_PYTHON%
    set PYTHONPATH=%PYTHONPATH_QGIS_PYTHON%;%PYTHONPATH%

    rem Plugins folder does not use 'qgis-ltr'.
    rem See https://anitagraser.com/2018/01/28/porting-processing-scripts-to-qgis3/
    rem set PYTHONPATH_QGIS_PLUGINS=%QGIS_SA_ROOT%\apps\%%Q\plugins
    rem The following is "python/plugins", not just "plugins".
    set PYTHONPATH_QGIS_PLUGINS=%QGIS_SA_ROOT%\apps\%Q%\python\plugins
    echo [INFO]   Adding standalone QGIS plugins to front of PYTHONPATH:
    echo [INFO]     %PYTHONPATH_QGIS_PLUGINS%
    set PYTHONPATH=%PYTHONPATH_QGIS_PLUGINS%;%PYTHONPATH%

rem Add QGIS site-packages to PYTHONPATH.
rem TODO smalers 2020-03-30 this should just use the Python version from PYTHONHOME
rem List the following in order so most recent Python for target version is found first:
rem - cannot get 'if else if' to work so use goto
echo [INFO]
echo [INFO] Adding QGIS Python site packages.
set PythonVersion=39
    rem It appears that QGIS Python uses lowercase "lib" is used rather than "Lib", so use lowercase below:
    rem - not sure why that is done (maybe for Linux?) but make lowercase here
    rem - TODO smalers 2022-10-17 QGIS 3.22.16 and 3.26.3 uses Lib
    set PYTHONPATH_QGIS_SITEPACKAGES=%QGIS_SA_ROOT%\apps\%PythonVersion%\Lib\site-packages
    echo [INFO]   Adding standalone QGIS %PythonVersion% 'Lib\site-packages' to front of PYTHONPATH:
    echo [INFO]     %PYTHONPATH_QGIS_SITEPACKAGES%
    set PYTHONPATH=%PYTHONPATH_QGIS_SITEPACKAGES%;%PYTHONPATH%

    rem Viewing sys.path for working gpdev.bat shows 8.3 paths for some files so add again here and below.
    rem The following are listed in Python sys.path when running gpdev.bat (without specifically adding)
    rem but don't by default get added in the PyCharm environment.
    rem TODO smalers 2020-04-01 need to add.
    set PYTHONPATH_QGIS_SITE_PACKAGES_PYTHONWIN=%QGIS_SA_ROOT%\apps\%PythonVersion%\Lib\site-packages\Pythonwin
    echo [INFO]   Adding standalone QGIS %PythonVersion% 'Lib\site-packages\Pythonwin' to front of PYTHONPATH:
    echo [INFO]     %PYTHONPATH_QGIS_SITE_PACKAGES_PYTHONWIN%
    set PYTHONPATH=%PYTHONPATH_QGIS_SITE_PACKAGES_PYTHONWIN%;%PYTHONPATH%

    set PYTHONPATH_QGIS_SITE_PACKAGES_WIN32=%QGIS_SA_ROOT%\apps\%PythonVersion%\Lib\site-packages\win32
    echo [INFO]   Adding standalone QGIS %PythonVersion% 'Lib\site-packages\win32' to front of PYTHONPATH:
    echo [INFO]     %PYTHONPATH_QGIS_SITE_PACKAGES_WIN32%
    set PYTHONPATH=%PYTHONPATH_QGIS_SITE_PACKAGES_WIN32%;%PYTHONPATH%

    set PYTHONPATH_QGIS_SITE_PACKAGES_WIN32_LIB=%QGIS_SA_ROOT%\apps\%PythonVersion%\Lib\site-packages\win32\lib
    echo [INFO]   Adding standalone QGIS %PythonVersion% 'Lib\site-packages\win32\lib' to front of PYTHONPATH:
    echo [INFO]     %PYTHONPATH_QGIS_SITE_PACKAGES_WIN32_LIB%
    set PYTHONPATH=%PYTHONPATH_QGIS_SITE_PACKAGES_WIN32_LIB%;%PYTHONPATH%

    rem Similarly, the PATH needs to have additional folders to agree with working 'gpdev.bat'.
    set PATH_QGIS_SITE_PACKAGES_PYWIN32_SYSTEM32=%QGIS_SA_ROOT%\apps\%PythonVersion%\Lib\site-packages\pywin32_system32
    echo [INFO]   Adding standalone QGIS %PythonVersion% 'Lib\site-packages\win32' to front of PYTHONPATH:
    echo [INFO]     %PATH_QGIS_SITE_PACKAGES_PYWIN32_SYSTEM32%
    set PATH=%PATH%;%PATH_QGIS_SITE_PACKAGES_PYWIN32_SYSTEM32%

    set PYTHONPATH_PYCHARM_SITEPACKAGES=%installFolder%\venv\venv-qgis-%targetQgisVersion%-python%PythonVersion%\Lib\site-packages
    echo [INFO]   Adding venv PyCharm Python%%T 'Lib\site-packages' to front of PYTHONPATH:
    echo [INFO]     %PYTHONPATH_PYCHARM_SITEPACKAGES%
    set PYTHONPATH=%PYTHONPATH_PYCHARM_SITEPACKAGES%;%PYTHONPATH%

rem Add the GeoProcessor to the PYTHONPATH:
rem - OK to put at the front because geoprocessor should not conflict with anything else
rem - the Python main specifies the 'geoprocessor' folder in the module to load
set GEOPROCESSOR_HOME=%srcFolder%
  echo [INFO]   Adding GeoProcessor Python source folder code to start of PYTHONPATH:
  echo [INFO]     %GEOPROCESSOR_HOME%
  set PYTHONPATH=%GEOPROCESSOR_HOME%;%PYTHONPATH%

rem Set the window title to indicate how configured so as to avoid confusion.
title GeoProcessor standalone QGIS development environment for PyCharm

rem ========== END GeoProcessor setup steps to be done once ===========================
rem ===================================================================================

rem Echo environment variables for troubleshooting.
echo [INFO]
echo [INFO] After all setup:
echo [INFO]   Using Python3/standalone QGIS3 for GeoProcessor.
echo [INFO]   Environment for Python/GeoProcessor:
echo [INFO]     QGIS_SA_INSTALL_HOME=%QGIS_SA_INSTALL_HOME%
echo [INFO]     QGIS_SA_ROOT=%QGIS_SA_ROOT%
echo [INFO]     PATH=%PATH%
echo [INFO]     PYTHONHOME=%PYTHONHOME%
echo [INFO]     PYTHONPATH=%PYTHONPATH%
echo [INFO]     QGIS_PREFIX_PATH=%QGIS_PREFIX_PATH%
echo [INFO]     QT_PLUGIN_PATH=%QT_PLUGIN_PATH%

rem Set the window title again because running commands in the window resets the title.
title GeoProcessor standalone QGIS development environment for PyCharm

rem Start the PyCharm IDE, /B indicates to use the same windows:
rem - command line parameters passed to this script will be passed to PyCharm
rem - PyCharm will use the Python interpreter configured for the project
rem - specify the folder for the project so it does not default to some other project that was opened last
rem - the project folder is the same as the repository folder (use PyCharm exclude feature to exclude non-source folders)
rem echo [INFO] Starting PyCharm using:  start ... /B %PYCHARM% %GP_PROJECT_DIR% %*
set PYCHARM=C:\Program Files\JetBrains\PyCharm Community Edition 2022.2.3\bin\pycharm64.exe
SET GP_PROJECT_DIR=%installFolder%
echo [INFO]
echo [INFO] Starting PyCharm.
echo [INFO]   PYCHARM = %PYCHARM%
echo [INFO]   GP_PROJECT_DIR = %GP_PROJECT_DIR%
rem TODO smalers 2020-03-30 need to figure out how to strip out /s3.10, etc. from %* so PyCharm won't complain.
echo [INFO]   Starting PyCharm using:
echo [INFO]     start "Pycharm aware of QGIS" /B "%PYCHARM%" "%GP_PROJECT_DIR% %*
echo [INFO]     Command shell prompt will display and PyCharm may take a few seconds to start.
rem if exist %GP_PROJECT_DIR% start "PyCharm aware of QGIS" /B %PYCHARM% %GP_PROJECT_DIR% %*
if exist %GP_PROJECT_DIR% start "PyCharm aware of QGIS" /B "%PYCHARM%" "%GP_PROJECT_DIR%"
