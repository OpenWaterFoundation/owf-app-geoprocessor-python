@echo off
rem gpdev.bat - run the GeoProcessor in the development environment
rem _________________________________________________________________NoticeStart_
rem GeoProcessor
rem Copyright (C) 2017-2023 Open Water Foundation
rem
rem GeoProcessor is free software:  you can redistribute it and/or modify
rem     it under the terms of the GNU General Public License as published by
rem     the Free Software Foundation, either version 3 of the License, or
rem     (at your option) any later version.
rem
rem     GeoProcessor is distributed in the hope that it will be useful,
rem     but WITHOUT ANY WARRANTY; without even the implied warranty of
rem     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
rem     GNU General Public License for more details.
rem
rem     You should have received a copy of the GNU General Public License
rem     along with GeoProcessor.  If not, see <https://www.gnu.org/licenses/>.
rem _________________________________________________________________NoticeEnd___
rem
rem Windows batch file to run the Open Water Foundation GeoProcessor application for QGIS:
rem - run in the development environment
rem - this script is similar to gp.bat except that development virtual environment is used
rem - the default is to start the interpreter but can run gpuidev.bat to run the UI, for if gpuidev.bat -ui is run
rem - this batch file is used with Python3/QGIS3 (older QGIS LTR is not used)
rem - this batch file handles:
rem     - stand-alone QGIS installation used for typical users
rem     - OSGeo4W64 QGIS, wihch may be used by developers
rem - checks are done for Python 3.6 and 3.7, with latest used, to accommodate QGIS versions
rem - the current focus is to run on a Windows 10 development environment
rem - this batch file uses the QGIS Python as the interpreter, but development geoprocessor module via PYTHONPATH
rem - this batch file should be installed in the scripts folder in the GeoProcessor code repository
rem - paths to virtual environment used in development are assumed based on standard OWF development environment

rem Set the Python environment to find the correct run-time libraries:
rem - the GEOPROCESSOR_ENV_SETUP environment variable is set to YES
rem   to indicate that setup has been done
rem - this causes setup to occur only once if rerunning this batch file

rem The two main logic blocks start at:
rem   :runOsgeoQgis
rem   :runStandaloneQgis

rem The script version can be different from the GeoProcessor Python version:
rem - this version is just used to help track changes to this script
set gpdevBatVersion=1.4.0
set gpdevBatVersionDate=2023-03-06

rem Turn on delayed expansion so that loops work:
rem - seems crazy but see:  https://ss64.com/nt/delayedexpansion.html
rem - otherwise, for loops and ( ) blocks don't work because variables are not set as expected
rem - such variables must be surrounded by ! !, rather than % %
setlocal EnableDelayedExpansion

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

echo [INFO]
echo [INFO] Startup information:
echo [INFO]   Batch file name is:
echo [INFO]     %scriptName%
echo [INFO]   %scriptName% is located in folder:
echo [INFO]     %scriptFolder%
echo [INFO]   GeoProcessor development project is located in folder:
echo [INFO]     %installFolder%
echo [INFO]   GeoProcessor source code is located in folder:
echo [INFO]     %srcFolder%

rem Print the command line parameters.
echo [INFO] Command line parameter 1 = %1
echo [INFO] Command line parameter 2 = %2
echo [INFO] Command line parameter 3 = %3
echo [INFO] Command line parameter 4 = %4
echo [INFO] Command line parameter 5 = %5

rem Evaluate command options, using Windows-style options:
rem - have to check %1% and %2% because may be called from another file such as from gpuidev.bat using -ui
rem - the / options are handled here, consistent with Windows
rem - the dash options will be handled by the called Python program
rem - the /o option will only try to run the OSGeo4W QGIS install,
rem   useful for development and troubleshooting
rem - the /s option will only try to run the standalone QGIS install,
rem   useful for development and troubleshooting
rem - don't include -h or --help since the gp*.bat script uses that
if "%1"=="/h" goto printUsage
if "%1"=="/help" goto printUsage
if "%1"=="/?" goto printUsage
if "%2"=="/h" goto printUsage
if "%2"=="/help" goto printUsage
if "%2"=="/?" goto printUsage

rem Detect whether the environment should be printed.
set doPrintEnv=no
if "%1"=="/printenv" set doPrintEnv=yes
if "%2"=="/printenv" set doPrintEnv=yes
if "%3"=="/printenv" set doPrintEnv=yes
if "%4"=="/printenv" set doPrintEnv=yes
if "%5"=="/printenv" set doPrintEnv=yes
if "%1"=="--printenv" set doPrintEnv=yes
if "%2"=="--printenv" set doPrintEnv=yes
if "%3"=="--printenv" set doPrintEnv=yes
if "%4"=="--printenv" set doPrintEnv=yes
if "%5"=="--printenv" set doPrintEnv=yes
echo [INFO] doPrintEnv = %doPrintEnv%
if "%doPrintEnv%"=="yes" (
  echo [INFO] Will print the environment before starting the GeoProcessor.
)

rem Detect whether Python should run verbose.
set doVerbose=no
if "%1"=="/verbose" set doVerbose=yes
if "%2"=="/verbose" set doVerbose=yes
if "%3"=="/verbose" set doVerbose=yes
if "%4"=="/verbose" set doVerbose=yes
if "%5"=="/verbose" set doVerbose=yes
if "%1"=="--verbose" set doVerbose=yes
if "%2"=="--verbose" set doVerbose=yes
if "%3"=="--verbose" set doVerbose=yes
if "%4"=="--verbose" set doVerbose=yes
if "%5"=="--verbose" set doVerbose=yes
echo [INFO] doVerbose = %doVerbose%
if "%doVerbose%"=="yes" (
  echo [INFO] Will run Python with -v to show verbose output.
)

rem Case where the OSGeo version (not standalone version) is run.
if "%1"=="/o" goto runOsgeoQgis
if "%1"=="-o" goto runOsgeoQgis
if "%2"=="/o" goto runOsgeoQgis
if "%2"=="-o" goto runOsgeoQgis
if "%3"=="/o" goto runOsgeoQgis
if "%3"=="-o" goto runOsgeoQgis
if "%4"=="/o" goto runOsgeoQgis
if "%4"=="-o" goto runOsgeoQgis

rem Run Python directly, useful to run "processing.alghelp()" and other functions:
rem - set up the environment as if running GeoProcessor but just run Python
set runPython=no
if "%1"=="/python" set runPython=yes
if "%2"=="/python" set runPython=yes
if "%3"=="/python" set runPython=yes
if "%4"=="/python" set runPython=yes
if "%5"=="/python" set runPython=yes
if "%1"=="--python" set runPython=yes
if "%2"=="--python" set runPython=yes
if "%3"=="--python" set runPython=yes
if "%4"=="--python" set runPython=yes
if "%5"=="--python" set runPython=yes

rem Case where /s is specified without a QGIS version.
set qgisVersion=unknown
set targetQgisVersion=unknown
if "%1"=="/s" goto runStandaloneQgis
if "%1"=="-s" goto runStandaloneQgis
if "%2"=="/s" goto runStandaloneQgis
if "%2"=="-s" goto runStandaloneQgis
if "%3"=="/s" goto runStandaloneQgis
if "%3"=="-s" goto runStandaloneQgis
if "%4"=="/s" goto runStandaloneQgis
if "%4"=="-s" goto runStandaloneQgis

rem Print this script version:
rem - don't include -v or --version since the gp*.bat script uses that
if "%1"=="/v" goto printVersion
if "%1"=="/version" goto printVersion
if "%2"=="/v" goto printVersion
if "%2"=="/version" goto printVersion
if "%3"=="/v" goto printVersion
if "%3"=="/version" goto printVersion
if "%4"=="/v" goto printVersion
if "%4"=="/version" goto printVersion

rem If here /s was not specified but /sN.N might have been.
rem Options that specify the standalone QGIS version to use:
rem - the requested version will be confirmed below when file existence is checked
rem echo [INFO] Before QGIS version for loop.
echo [INFO]
echo [INFO] Determine the QGIS to run.
echo [INFO]   Check to see if the requested QGIS version matches known versions used with the GeoProcessor.
echo [INFO]   It is recommended to install the most recent supported long term releases (ltr).
echo [INFO]     3.26.3
echo [INFO]     3.22.16 (ltr)
echo [INFO]     3.12
echo [INFO]     3.10
echo [INFO]     3.4
echo [INFO]   If a different version of QGIS is used, need to update this script.

rem The following could be done better but trying to parse parameters in batch files is painful:
rem - the order is not important because trying to match a requested version
rem - put newest first to match faster
rem - if none are matched "unknown" will be detected
for %%G in (3.26.3 3.22.16 3.12 3.10 3.4 unknown) do (
  rem Set a local variable to make code easier to understand.
  set qgisVersion=%%G
  if "unknown"=="!qgisVersion!" (
    rem Checked all the supported versions and did not have a match.
    goto unknownStandaloneVersion
  )
  echo [INFO]   Checking command arguments for QGIS version /s!qgisVersion!
  if "%1%"=="/s!qgisVersion!" (
    set targetQgisVersion=!qgisVersion!
    echo [INFO]     Command line parameter /s!qgisVersion! detected.  Will run stand-alone QGIS !targetQgisVersion!.  Python venv must be compatible.
    goto runStandaloneQgis
  )
  rem Same logic but for second command parameter (if provided).
  if "%2%"=="/s!qgisVersion!" (
    set targetQgisVersion=!qgisVersion!
    echo [INFO]     Command line parameter /s!qgisVersion! detected.  Will run stand-alone QGIS !targetQgisVersion!.  Python venv must be compatible.
    goto runStandaloneQgis
  )
  rem Same logic but for third command parameter (if provided).
  if "%3%"=="/s!qgisVersion!" (
    set targetQgisVersion=!qgisVersion!
    echo [INFO]     Command line parameter /s!qgisVersion! detected.  Will run stand-alone QGIS !targetQgisVersion!.  Python venv must be compatible.
    goto runStandaloneQgis
  )
)

:unknownStandaloneVersion
rem Get to here if /sN.N or /sN.N.N did not match an installed QGIS in the loop above.
echo [ERROR]
echo [ERROR]  Requested unsupported QGIS version with /sN.N or /sN.N.N (or /s without version).
echo [ERROR]  Need to update this script to handle the requested QGIS version.
echo [ERROR]  Check the versions of QGIS that are installed (e.g., C:\Program Files\QGIS *).
echo [ERROR]  Make sure to run with: /sN.N or /sN.N.N
goto exit1

echo [ERROR]   Did not match /o or /sN.N so trying to run as if /s.
rem Default is to run standalone QGIS:
rem - a warning will be generated if no QGIS version
echo [ERROR]
echo [ERROR]  QGIS install type not specified with /o or /sN.N or /sN.N.N - defaulting to running the standalone QGIS found on the system.
echo [ERROR]  This is not currently handled - mus specify /sN.N or /sN.N.N.
rem goto runStandaloneQgis
goto exit1

:runOsgeoQgis

rem Run the OSGeo4W64 version of QGIS.
echo [INFO]
echo [INFO] Using OSGeo4W64 version of QGIS.

rem TODO smalers 2020-03-30 re-enable if needed but for now the code has not been updated to standalone level.
echo [ERROR]
echo [ERROR] OSGeo4W64 GIS version of GeoProcessor is currently disabled.  Use a standalone QGIS version.
echo [ERROR] Run with /sN.N or /sN.N.N for an installed QGIS version.
goto exit1

:runStandaloneQgis

rem Run the standalone version of QGIS, which is installed in a versioned folder.
echo [INFO]
echo [INFO] Using standalone version of QGIS.

echo [INFO] Requested target standalone QGIS version = %targetQgisVersion%
if "%targetQgisVersion%"=="unknown" (
  echo [ERROR]
  echo [ERROR]  Requested target standalone QGIS version is unknown.  Run with /sN.N, /sN.N.N, or /o option.
  rem List available standalone versions on all drives, not elegant but OK for now.
  echo [INFO] Available standalone QGIS versions:
  for %%Z in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    set driveLetter=%%Z
    rem debug...
    rem echo [INFO] Checking for existence of:  !driveLetter!:\Program Files\
    if exist "!driveLetter!:\Program Files\" (
      dir /b "!driveLetter!:\Program Files\QGIS*"
    )
  )
  goto printUsage
)

rem Set the Python environment to find the correct run-time libraries:
rem - QGIS Python environment is used and add GeoProcessor to PYTHONPATH
rem - the SA_GP_ENV_SETUP environment variable is set to YES to indicate that setup has been done
rem - this causes setup to occur only once if rerunning this batch file

if "%SA_GP_ENV_SETUP%"=="YES" (
  echo [INFO]
  echo [INFO] Environment is already set up for standalone QGIS from previous run.
  echo [INFO] Using the previous settings so that PATH and PYTHONPATH don't accumulate more folders.
  goto runStandaloneQgis2
)

rem ===================================================================================
rem If here do the setup one time first time batch file is run in a command shell.
echo [INFO]
echo [INFO] Start defining standalone QGIS GeoProcessor environment.

rem This code is similar to the initial check at the top of the batch file.
echo [INFO]
echo [INFO] Try to find QGIS in ?:\Program Files (may be installed on any drive C or after).
for %%D in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
  echo [INFO]   Checking for existence of %%D:\Program Files\QGIS !targetQgisVersion!
  if exist "%%D:\Program Files\QGIS !targetQgisVersion!" (
    SET QGIS_SA_INSTALL_HOME=%%D:\Program Files\QGIS !targetQgisVersion!
    echo [INFO]   Standard QGIS exists in:  !QGIS_SA_INSTALL_HOME!
    goto setupStandalone1b
  )
)
rem If here could not find QGIS.
echo [ERROR]
echo [ERROR]  Could not find QGIS on any drive in:
echo [ERROR]    ?:\Program Files\GGIS !targetQgisVersion!
echo [ERROR]  Cannot continue.
goto exit1

:setupStandalone1b

rem Get the short version of the install home:
rem - TODO smalers 2023-03-02 evaluate whether 8.3 is needed or can long paths with spaces work
echo [INFO]
echo [INFO] Setting QGIS_SA_INSTALL_HOME and QGIS_SA_ROOT.
set QGIS_SA_ROOT=!QGIS_SA_INSTALL_HOME!
echo [INFO]   Standalone install:
echo [INFO]     QGIS_SA_INSTALL_HOME = !QGIS_SA_INSTALL_HOME!
echo [INFO]     QGIS_SA_ROOT = !QGIS_SA_ROOT!

if [] == [!QGIS_SA_ROOT!] (
  echo [ERROR]
  echo [ERROR] QGIS_SA_ROOT is not defined.
  echo [ERROR] Cannot set up the QGIS environment.
  goto exit1
)
if not exist !QGIS_SA_ROOT! (
  echo [ERROR]
  echo [ERROR] QGIS root folder does not exist:
  echo [ERROR]   !QGIS_SA_ROOT!
  echo [ERROR] Cannot set up the QGIS environment.
  goto exit1
)

rem Convert important folders to 8.3 notation.
set use83Paths=true
if "%use83Paths%" == "true" (
  rem TODO smalers 2020-04-01 Try using 8.3 names.
  for %%H in ("!QGIS_SA_INSTALL_HOME!") do set QGIS_SA_INSTALL_HOME_83=%%~sH
  set QGIS_SA_INSTALL_HOME=!QGIS_SA_INSTALL_HOME_83!
  set QGIS_SA_ROOT=!QGIS_SA_INSTALL_HOME_83!
  echo [INFO]   After conversion to 8.3 to avoid spaces in path:
  echo [INFO]     Standalone install home QGIS_SA_INSTALL_HOME = !QGIS_SA_INSTALL_HOME!
  echo [INFO]     Standalone install root QGIS_SA_ROOT = !QGIS_SA_ROOT!
)

echo [INFO]
echo [INFO] Running GeoProcessor using standalone GQGIS in:  !QGIS_SA_INSTALL_HOME!

rem Where QGIS is installed.
if not exist "!QGIS_SA_INSTALL_HOME!" (
  echo [ERROR] QGIS_SA_INSTALL_HOME does not exist:
  echo [ERROR]   !QGIS_SA_INSTALL_HOME!
  goto noStandaloneQgis
)
if not exist "!QGIS_SA_ROOT!" (
  echo [ERROR] QGIS_SA_ROOT does not exist:
  echo [ERROR]   !QGIS_SA_ROOT!
  goto noStandaloneQgis
)

rem The following sets up the QGIS environment for Python:
rem - handles QGIS, Python, and Qt setup
rem - same batch file name as for OSGeo4W install

echo [INFO]
echo [INFO] Setting QGIS Python and Qt environment variables.
if exist "!scriptFolder!\python-qgis-ltr.bat" (
  echo [INFO]   Calling QGIS Python setup batch file from GeoProcessor:
  echo [INFO]     !scriptFolder!\python-qgis-ltr.bat
  call "!scriptFolder!\python-qgis-ltr.bat"
  if errorlevel 1 (
    echo [ERROR]  Error calling python-qgis-ltr.bat.  Cannot continue.
    goto exit1
  )
  goto qgisEnvStandalone
)
rem If here the python-qgis-ltr.bat file was not found, which is a major problem.
echo [ERROR]
echo [ERROR]  python-qgis-ltr.bat file was not found:
echo [ERROR]    %scriptFolder%\python-qgis-ltr.bat
echo [ERROR]  Cannot setup QGIS Python environment.
goto exit1

:qgisEnvStandalone

rem Add QGIS 'python' and 'plugins' folders to the PYTHONPATH:
rem - the qgis-ltr folder needs to be checked first because for a long term release
rem - the qgis-ltr/python and qgis/python folders each exist, but qgis/python is empty
rem - 'qgis-ltr' is used in several environment variables
rem - the latest release (under development) does not seem to include qgis-ltr
echo [INFO]
echo [INFO] Setting the QGIS Python app files environment variables.
for %%Q in (qgis-ltr qgis qgis-dev) do (
  if exist !QGIS_SA_ROOT!\apps\%%Q\python (
    echo [INFO]   Found QGIS Python application files:
    echo [INFO]     !QGIS_SA_ROOT!

    rem The following is "python/plugins", not just "plugins".
    set PYTHONPATH_QGIS_PLUGINS=!QGIS_SA_ROOT!\apps\%%Q\python\plugins
    echo [INFO]   Adding standalone QGIS plugins to front of PYTHONPATH:
    echo [INFO]     !PYTHONPATH_QGIS_PLUGINS!
    set PYTHONPATH=!PYTHONPATH_QGIS_PLUGINS!;!PYTHONPATH!

    goto standalonePathSet
  )
)
rem If here the application variables could not bet set.
echo [ERROR]
echo [ERROR]  Could not find QGIS Python files in any of the following:
echo [ERROR]    !QGIS_SA_ROOT!\apps\qgis-ltr\python
echo [ERROR]    !QGIS_SA_ROOT!\apps\qgis\python
echo [ERROR]    !QGIS_SA_ROOT!\apps\qgis-dev\python
echo [ERROR]  Cannot setup QGIS Python application environment.
goto exit1

:standalonePathSet
rem If here the PYTHONPATH was set above for PyQGIS.

rem Add additional packages to PYTHONPATH located in PyCharm development venv.
rem List the following in order so most recent Python for target version is found first:
rem - cannot get 'if else if' to work so use goto
echo [INFO]
echo [INFO] Adding venv site packages to PYTHONPATH.
for %%T in (39 38 37 36) do (
  echo [INFO]   Checking for existence of %installFolder%\venv\venv-qgis-!targetQgisVersion!-python%%T
  if exist %installFolder%\venv\venv-qgis-!targetQgisVersion!-python%%T\ (
    set PYTHONPATH_PYCHARM_SITEPACKAGES=%installFolder%\venv\venv-qgis-!targetQgisVersion!-python%%T\Lib\site-packages
    echo [INFO]   Adding venv PyCharm Python%%T 'Lib\site-packages' to front of PYTHONPATH:
    echo [INFO]     !PYTHONPATH_PYCHARM_SITEPACKAGES!
    set PYTHONPATH=!PYTHONPATH_PYCHARM_SITEPACKAGES!;!PYTHONPATH!
    goto setupStandalone2
  )
)
rem Warning because could not find PyCharm venv Python.
echo [ERROR]  Could not find venv folder for python:39, Python38, Python37, or Python36 in:
echo [ERROR]    %installFolder%\venv\venv-qgis-!targetQgisVersion! for site-packages.
goto exit1

:setupStandalone2

rem Add the GeoProcessor Python code to the PYTHONPATH:
rem - OK to put at the front because 'geoprocessor' should not conflict with anything else
rem - the Python main specifies the 'geoprocessor' folder in the module to load
set GEOPROCESSOR_HOME=%srcFolder%
echo [INFO]
echo [INFO] Adding GeoProcessor Python source folder code to PYTHONPATH.
if exist %GEOPROCESSOR_HOME% (
  echo [INFO]   Adding GeoProcessor Python source folder code to start of PYTHONPATH:
  echo [INFO]     %GEOPROCESSOR_HOME%
  set PYTHONPATH=%GEOPROCESSOR_HOME%;!PYTHONPATH!
  goto pycharmSetupComplete
)
echo [ERROR] GeoProcessor home folder does not exist:  %GEOPROCESSOR_HOME%
echo [ERROR] Cannot continue.
goto exit1

:pycharmSetupComplete

rem Indicate that the setup has been completed:
rem - this will ensure that the script when run again does not repeat setup
rem   and keep appending to environment variables
rem - not sure if this is necessary if exit /b is used because environment will be reset each time the script is run
set SA_GP_ENV_SETUP=YES

rem Set the window title to indicate how configured so as to avoid confusion.
title GeoProcessor standalone QGIS development environment to run gpdev.bat and gpuidev.bat (don't run gp.bat or gpui.bat)
echo [INFO]
echo [INFO] Done defining QGIS GeoProcessor environment.
goto runStandaloneQgis2

rem ========== END GeoProcessor setup steps to be done once ===========================
rem ===================================================================================

:noStandaloneQgis

rem QGIS install folder was not found.
echo [INFO] QGIS standard installation folder was not found:  !QGIS_SA_INSTALL_HOME!
goto exit1

:runStandaloneQgis2

rem Echo environment variables for troubleshooting.
echo [INFO]
echo [INFO] After all setup:
echo [INFO]   Using Python3/standalone QGIS3 for GeoProcessor.
echo [INFO]   Environment for Python/GeoProcessor:
echo [INFO]     QGIS_SA_INSTALL_HOME=!QGIS_SA_INSTALL_HOME!
echo [INFO]     QGIS_SA_ROOT=!QGIS_SA_ROOT!
echo [INFO]     OSGEO4W_ROOT=!OSGEO4W_ROOT!
echo [INFO]     PATH=%PATH%
echo [INFO]     PYTHONHOME=!PYTHONHOME!
echo [INFO]     PYTHONPATH=!PYTHONPATH!
echo [INFO]     QGIS_PREFIX_PATH=!QGIS_PREFIX_PATH!
echo [INFO]     QT_PLUGIN_PATH=!QT_PLUGIN_PATH!

rem Set the window title again because running commands in the window resets the title.
title GeoProcessor standalone QGIS development environment to run gpdev.bat and gpuidev.bat (don't run gp.bat or gpui.bat)

if "!doPrintEnv!"=="yes" (
  rem Run the geoprocessor.app.printenv program, useful for troubleshooting.
  rem - this can be used with other program parameters
  rem echo [INFO] Running printenv.py to print the environment.
  "!OSGEO4W_ROOT!\bin\python.exe" -m geoprocessor.app.printenv %*
)

rem Run QGIS Python with the geoprocessor module found using PYTHONPATH set above:
rem - the Python version is compatible with QGIS
rem - pass command line arguments that were passed to this bat file
rem Use -v to see verbose list of modules that are loaded
if "%doVerbose%"=="yes" (
  set verboseOpt= -v
)
if "!runPython!"=="yes" (
  rem Run Python with the GeoProcessor environment but not the GeoProcessor.

  rem Run the following to use the environment but be able to do imports, etc. to find modules.
  echo [INFO]
  echo [INFO] Running Python directly in GeoProcessor environment.
  echo [INFO] Use Python language syntax at the prompt.
  rem Don't pass command line options because Python tries to interpret.
  rem "!PYTHONHOME!\python" -v %*
  rem "!PYTHONHOME!\python" -v
  echo [INFO] Running: "!PYTHONHOME!\python" !verboseOpt! -B -d -X dev
  "!OSGEO4W_ROOT!\bin\python" !verboseOpt! -B -d -X dev
) else (
  echo [INFO]
  echo [INFO] Running:  "!PYTHONHOME!\python" !verboseOpt! -m geoprocessor.app.gp %*
  echo [INFO] If errors result due to missing packages,
  echo [INFO] install those packages in the PyCharm venv and report to developers.
  echo [INFO] Start-up may be slow if virus scanner needs to check.
  echo.
  rem Run the GeoProcessor application.
  "!OSGEO4W_ROOT!\bin\python" !verboseOpt! -m geoprocessor.app.gp %*
  rem "!OSGEO4W_ROOT!\apps\Python39\python" !verboseOpt! -m geoprocessor.app.gp %*
)

rem Exit with the error level of the Python command.
echo [INFO]
echo [INFO] Exiting gpdev.bat with the Python exit code:  %ERRORLEVEL%
exit /b %ERRORLEVEL%

rem =======================================================================
rem Below here are one-off goto targets that each end with exit.

:printUsage
rem Print the program usage.
echo.
echo Usage:  %scriptName% [options]
echo.
echo Run the GeoProcessor in the development environment on Windows.
echo This batch file sets up the development environment and calls the Python GeoProcessor.
echo All command line options for the batch file are also passed to the GeoProcessor.
echo.
echo /h         Print usage of this gpdev.bat batch file.
echo /o         Use the OSGeo4W version of QGIS, CURRENTLY DISABLED (default is versioned stand-alone).
echo /python    Run Python in the GeoProcessor environment without starting GeoProcessor.
echo /printenv  Print the environment in addition to running the GeoProcessor.
echo /s         Use the standalone version of QGIS (this is the default rather than /o).
echo /sN.N      Use the standalone version N.N of QGIS (for example 3.10).
echo /sN.N.N    Use the standalone version N.N of QGIS (for example 3.22.16).
echo /v         Print version of this gpdev.bat batch file.
echo /verbose   Run Python with the -v.
echo.
echo The following are understood by the GeoProcessor software:
echo.
echo --commands CommandFile.gp      Process a command file in batch mode.
echo --help                         Print usage for Python GeoProcessor.
echo --http                         Run GeoProcessor in HTTP server mode - under development.
echo -p PropertyName=PropertyValue  Set a processor string property.
echo --ui                           Run GeoProcessor user interface (UI).
echo -v, --version                  Print GeoProcessor version information.
echo.
goto exit0

:printVersion
rem Print the program version.
echo.
echo %scriptName% version: %gpdevBatVersion% %gpdevBatVersionDate%
echo.
goto exit0

:exit0
rem Exit with normal (0) exit code:
rem - put this at the end of the batch file
echo [INFO]
echo [INFO] Success.  Exiting with status 0.
exit /b 0

:exit1
rem Exit with general error (1) exit code:
rem - put this at the end of the batch file
echo [ERROR]
echo [ERROR] An error of some type occurred [see previous messages].  Exiting with status 1.
exit /b 1
