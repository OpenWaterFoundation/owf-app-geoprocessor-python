THIS CODE CAN BE INSERTED INTO THE SCRIPT IF NECESSARY.
CUT OUT FOR NOW TO MINIMIZE CONFUSION.

if "!targetQgisVersion!"=="unknown" (
  echo [ERROR] Target OsGeo4W QGIS version is unknown.  Run with /sN.N, /sN.N.N, or /o option.
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

rem Set an environment variable to indicate that the environment is setup:
rem - this ensures that setup is done once
rem - then PyCharm can be restarted in the same window without reconfiguring the environment

if "%OSGEO_GP_PYCHARM_ENV_SETUP%"=="YES" GOTO run
echo [INFO] Setting PyCharm environment to use QGIS Python environment.

rem Where QGIS is installed:
rem - this logic needs to be revisited to detect the installation drive
SET QGIS_INSTALL_HOME=C:\OSGeo4W64
SET OSGEO4W_ROOT=%QGIS_INSTALL_HOME%
if not exist %OSGEO4W_ROOT% GOTO noOsgeoQgis
echo [INFO] OSGeo4W QGIS is installed in:  %QGIS_INSTALL_HOME%

rem Name of QGIS version to run (**for running OWF GeoProcessor don't run QGIS
rem but need to use correct QGIS components**).
rem Run the latest release of the OSGeo4W QGIS by setting value to `qgis`.
rem The QGIS OSGeo4W64 installer as of February 23, 2018 installs QGIS version 3 as `qgis`.
SET QGISNAME=qgis
set _qgis=%OSGEO4W_ROOT%\bin\qgis.bat

if not exist %_qgis% goto noqgisbat
echo [INFO] QGISNAME is %QGISNAME%

rem Set the QGIS environment by calling the setup script that is distributed with QGIS.
CALL %OSGEO4W_ROOT%\bin\o4w_env.bat
rem Set environment variables for using the Qt5-Widget library.
rem REF: https://gis.stackexchange.com/questions/276902/importing-paths-for-qgis-3-standalone-scripts
if exist %OSGEO4W_ROOT%\bin\qt5_env.bat (
  echo [INFO] Calling QGIS Qt setup batch file from QGIS:  %OSGEO4W_ROOT%\bin\qt5_env.bat
  call "%OSGEO4W_ROOT%\bin\qt5_env.bat"
  echo [INFO] Back from: qt5_env.bat
  goto pythonEnvOsGeo
)
rem If here call the script saved with the GeoProcessor.
echo [INFO] Calling QGIS Qt setup batch file from GeoProcessor:  %scriptFolder%\..\scripts\qt5_env.bat
call "%scriptFolder%\..\scripts\qt5_env.bat"
echo [INFO] Back from: qt5_env.bat

:pythonEnvOsGeo

rem Set variables specific to Python3.
rem REF: https://gis.stackexchange.com/questions/276902/importing-paths-for-qgis-3-standalone-scripts
if exist %OSGEO4W_ROOT%\bin\py3_env.bat (
  echo [INFO] Calling QGIS Python 3 setup batch file:  %OSGEO4W_ROOT%\bin\py3_env.bat
  CALL %OSGEO4W_ROOT%\bin\py3_env.bat
  goto gqisEnvOsGeo
)
rem If here call the script saved with the GeoProcessor.
echo [INFO] Calling QGIS Python 3 setup batch file:  %scriptFolder%\..\scripts\py3_env.bat
call "%scriptFolder%\..\scripts\py3_env.bat"

:qgisEnvOsGeo

rem Add QGIS to the PATH environment variable so that all QGIS, GDAL, OGR, etc. programs are found.
set PATH=%OSGEO4W_ROOT%\bin;%PATH%
set PATH=%PATH%;%OSGEO4W_ROOT%\apps\%QGISNAME%\bin

rem Absolute path to QGIS program to run.
SET QGIS=%OSGEO4W_ROOT%\apps\%QGISNAME%
rem Not sure what the following is used for but include in case PyCharm or QGIS uses.
SET QGIS_PREFIX_PATH=%QGIS%

rem Add QGIS to the PATH environment variable so that all QGIS, GDAL, OGR, etc. programs are found.
SET PATH=%PATH%;%QGIS%\bin
SET PATH=%PATH%;%OSGEO4W_ROOT%\apps\Qt5\bin

rem Add pyQGIS libraries to the PYTHONPATH so that they are found by Python.
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python
set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python\plugins

rem Set the Python to use:
rem - list the following in order so most recent is at the end
rem - this assumes that OSGEO4W suite is installed in the default location and the latest should be used
rem - the following uses O (oh) as the loop variable
for %%O in (39 38 37 36) do (
  echo [INFO] Checking OSGeo4W for Python%%O
  if exist %OSGEO4W_ROOT%\apps\Python%%O (
    echo [INFO] Will use OSGeo4W Python%%O
    set PYTHONPATH=%OSGEO4W_ROOT%\apps\Python%%O\Lib\site-packages;%PYTHONPATH%
  )
)

rem Set the environment variable that lets this batch file know that the environment is set up.
set OSGEO_GP_PYCHARM_ENV_SETUP=YES

rem This is the entry point of the script after set and if the script has been run before:
rem - set the window title to indicate that the environment is configured
rem - TODO smalers 2020-01-10 need to set title if error occurred setting up the environment?
:run
title GeoProcessor OSGeo4W QGIS development environment for PyCharm

rem Echo environment variables for troubleshooting.
echo [INFO]
echo [INFO] QGIS environment variables:
echo [INFO]   PATH=%PATH%
echo [INFO]   PYTHONHOME=%PYTHONHOME%
echo [INFO]   PYTHONPATH=%PYTHONPATH%
echo [INFO]   QGIS_PREFIX_PATH=%QGIS_PREFIX_PATH%
echo [INFO]   QT_PLUGIN_PATH=%QT_PLUGIN_PATH%

rem Start the PyCharm IDE, /B indicates to use the same windows:
rem - command line parameters passed to this script will be passed to PyCharm
rem - PyCharm will use the Python interpreter configured for the project
rem - Specify the folder for the project so it does not default to some other project
rem   that was opened last
echo [INFO]
echo [INFO] Starting PyCharm using:  start ... /B %PYCHARM% %GP_PROJECT_DIR% %*
echo [INFO] Prompt will display and PyCharm may take a few seconds to start.
SET GP_PROJECT_DIR=%installFolder%
if exist %GP_PROJECT_DIR% start "PyCharm aware of QGIS" /B %PYCHARM% %GP_PROJECT_DIR% %*
if not exist %GP_PROJECT_DIR% goto noproject
goto exit1
