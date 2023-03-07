THIS WAS SPLIT OUT OF THE SCRIPT.
ENABLE WHEN THERE IS A NEED.

if "!targetQgisVersion!"=="unknown" (
  echo.
  echo [ERROR] Target OSGeo4W QGIS version is unknown.  Run with /sN.N /sN.N.N or /o option.
  rem List available standalone versions on all drives, not elegant but OK for now.
  echo [INFO] Available standalone QGIS versions found on this computer:
  for %%Y in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    set driveLetter=%%Y
    rem Debug.
    rem echo [INFO] Checking for existence of:  !driveLetter!:\Program Files\
    if exist "!driveLetter!:\Program Files\" (
      dir /b "!driveLetter!:\Program Files\QGIS*"
    )
  )
  goto printUsage
)

if "%GP_DEV_ENV_SETUP%"=="YES" (
  echo [INFO] Environment is already set up to use OSGeo4W GQIS from previous run.  Skipping to run step...
  goto runOsgeoQgis2
)
rem ===================================================================================
rem If here do the setup one time first time batch file is run in a command shell.
echo [INFO] Start defining QGIS GeoProcessor environment (done once per command shell window)...

rem Where QGIS is installed:
rem - this logic needs to be revisited to detect the installation drive
SET QGIS_INSTALL_HOME=C:\OSGeo4W64
SET OSGEO4W_ROOT=%QGIS_INSTALL_HOME%
if not exist %OSGEO4W_ROOT% GOTO noOsgeoQgis
echo [INFO] OSGeo4W QGIS is installed in:  %QGIS_INSTALL_HOME%

rem Set the QGIS environment by calling the setup batch files that are distributed with QGIS:
rem - the following will reset the PATH and then add QGIS folders to path
rem - therefore other programs that were found before may not be found
rem - this effectively isolates QGIS from the system
echo [INFO] Calling QGIS setup batch file:  %OSGEO4W_ROOT%\bin\o4w_env.bat
call "%OSGEO4W_ROOT%\bin\o4w_env.bat"
rem The following sets a number of QT environment variables (QT is used in the UI):
rem - as of QGIS 3.20 this batch file is no longer distributed
set PATH=%OSGEO4W_ROOT%\apps\Qt5\bin;%PATH%
if exist "%OSGEO4W_ROOT%\bin\qt5_env.bat" (
  echo [INFO] Calling QGIS Qt setup batch file from QGIS:  %OSGEO4W_ROOT%\bin\qt5_env.bat
  call "%OSGEO4W_ROOT%\bin\qt5_env.bat"
  echo [INFO] Back from: qt5_env.bat
  goto pythonEnvOsGeo
)
rem If here call the script saved with the GeoProcessor.
echo [INFO] Calling QGIS Qt setup batch file from GeoProcessor:  %scriptFolder%\..\scripts\qt5_env.bat
call "%scriptFolder%\qt5_env.bat"
echo [INFO] Back from: qt5_env.bat

:pythonEnvOsGeo

rem The following sets:
rem - PYTHONHOME to Python shipped with QGIS
rem - clears PYTHONPATH
rem - PATH to include Python shipped with QGIS and Python scripts folder
if exist %OSGEO4W_ROOT%\bin\py3_env.bat (
  echo [INFO] Calling QGIS Python 3 setup batch file from QGIS:  %OSGEO4W_ROOT%\bin\py3_env.bat
  call %OSGEO4W_ROOT%\bin\py3_env.bat
  echo [INFO] Back from: py3_env.bat
  goto qgisEnvOsGeo
)
rem If here call the script saved with the GeoProcessor.
echo [INFO] Calling QGIS Python 3 setup batch file from GeoProcessor:  %scriptFolder%\py3_env.bat
call "%scriptFolder%\py3_env.bat"
echo [INFO] Back from: py3_env.bat

:qgisEnvOsGeo

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

rem Add pyQGIS libraries to the PYTHONPATH so that they are found by Python.
set PYTHONPATH=%OSGEO4W_ROOT%\apps\%QGISNAME%\python;%PYTHONPATH%
rem See https://anitagraser.com/2018/01/28/porting-processing-scripts-to-qgis3/
set PYTHONPATH=%OSGEO4W_ROOT%\apps\%QGISNAME%\python\plugins;%PYTHONPATH%

rem List the following in order so most recent is found first.
rem TODO smalers 2022-10-13 Could not get else if to work!
if exist "%OSGEO4W_ROOT%\apps\Python39" (
  echo [INFO] Adding QGIS Python39 site-packages to PYTHONPATH
  set PYTHONPATH=!OSGEO4W_ROOT!\apps\Python39\Lib\site-packages;!PYTHONPATH!
  goto runOsgeoQgis1
)
if exist "%OSGEO4W_ROOT%\apps\Python38" (
  echo [INFO] Adding QGIS Python38 site-packages to PYTHONPATH
  set PYTHONPATH=!OSGEO4W_ROOT!\apps\Python38\Lib\site-packages;!PYTHONPATH!
  goto runOsgeoQgis1
)
if exist "%OSGEO4W_ROOT%\apps\Python37" (
  echo [INFO] Adding QGIS Python37 site-packages to PYTHONPATH
  set PYTHONPATH=!OSGEO4W_ROOT!\apps\Python37\Lib\site-packages;!PYTHONPATH!
  goto runOsgeoQgis1
)
if exist "%OSGEO4W_ROOT%\apps\Python36" (
  echo [INFO] Adding QGIS Python36 site-packages to PYTHONPATH
  set PYTHONPATH=!OSGEO4W_ROOT!\apps\Python36\Lib\site-packages;!PYTHONPATH!
  goto runOsgeoQgis1
)
rem No suitable Python found for OSGeo4W version:
echo [ERROR] Python 3.6-3.9 version not found in %OSGEO4W_ROOT%\apps.  Exiting.
goto exit1

:runOsgeoQgis1

rem Set the PYTHONPATH to include the geoprocessor/ folder in source files:
rem - this is used in the development environment because the package has not been installed in Python Lib/site-packages
rem - OK to put at the front of PYTHONPATH because the folder ONLY contains GeoProcessor code, no third party packages
set GEOPROCESSOR_HOME=%installFolder%
set PYTHONPATH=%GEOPROCESSOR_HOME%;%PYTHONPATH%

rem Indicate that the setup has been completed:
rem - this will ensure that the script when run again does not repeat setup
rem   and keep appending to environment variables
set GP_DEV_ENV_SETUP=YES

rem Set the window title to indicate how configured so as to avoid confusion.
title GeoProcessor OSGeo4W QGIS development environment to run gpdev.bat and gpuidev.bat (don't run gp.bat or gpui.bat)
echo [INFO] ...done defining QGIS GeoProcessor environment (done once per command shell window).
goto runOsgeoQgis2

rem ========== END GeoProcessor setup steps to be done once ===========================
rem ===================================================================================

:noOsgeoQgis

rem QGIS install folder was not found.
echo [INFO] OSGeo4W64 QGIS standard installation folder was not found:  %OSGEO4W_ROOT%
goto exit1

:runOsgeoQgis2

rem If here then the environment has been configured.
rem [INFO] Echo environment variables for troubleshooting.
echo.
echo [INFO] Using OSGeo4W Python3/QGIS3 for development GeoProcessor.
echo [INFO] Environment for Python/GeoProcessor:
echo [INFO] PATH=%PATH%
echo [INFO] PYTHONHOME=%PYTHONHOME%
echo [INFO] PYTHONPATH=%PYTHONPATH%
echo [INFO] QGIS_PREFIX_PATH=%QGIS_PREFIX_PATH%
echo [INFO] QT_PLUGIN_PATH=%QT_PLUGIN_PATH%
echo.

rem Set the window title again because running commands in the window resets the title.
title GeoProcessor OSGeo4W QGIS development environment to run gpdev.bat and gpuidev.bat (don't run gp.bat or gpui.bat)

rem Run QGIS Python with the geoprocessor module found using PYTHONPATH set above:
rem - must use Python 3.6 compatible with QGIS
rem - pass command line arguments that were passed to this bat file
rem "%PYTHONHOME%\python" %*
rem Use -v to see verbose list of modules that are loaded.
echo [INFO] Running:  %PYTHONHOME%\python -m geoprocessor.app.gp %*
"%PYTHONHOME%\python" -m geoprocessor.app.gp %*

rem Run the following to use the environment but be able to do imports, etc. to find modules.
rem "%PYTHONHOME%\python" -v

rem Exit with the error level of the Python command.
exit /b %ERRORLEVEL%
