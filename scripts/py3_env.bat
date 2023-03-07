rem This is the setup script that was distributed with QGIS 3.10 but is not included in recent QGIS versions.
rem Run it if necessary to set up the GeoProcessor environment.
rem The script has been updated to be more robust checking for the Python version.
rem Echo formatting is indented to work with calling scripts.

echo [INFO]     Start of GeoProcessor py3_env.bat
echo [INFO]       Checking for Python versions with newest being used if found.

rem Use the most recent Python that is found.
rem - could do this in a loop but use brute force for now

if [] == [%OSGEO4W_ROOT%] (
  echo [ERROR]      The OSGEO4W_ROOT environment variable is not set.
  goto exit1
)

rem Check from newest to oldest version of Python:
rem - should find the newest since newer QGIS should be used
echo [INFO]       Checking for Python in: %OSGEO4W_ROOT%\apps\Python39
if exist %OSGEO4W_ROOT%\apps\Python39 (
  SET PYTHONHOME=%OSGEO4W_ROOT%\apps\Python39
  goto okToSet
)
echo [INFO]       Checking for Python in: %OSGEO4W_ROOT%\apps\Python38
if exist %OSGEO4W_ROOT%\apps\Python38 (
  SET PYTHONHOME=%OSGEO4W_ROOT%\apps\Python38
  goto okToSet
)
echo [INFO]       Checking for Python in: %OSGEO4W_ROOT%\apps\Python37
if exist %OSGEO4W_ROOT%\apps\Python37 (
  SET PYTHONHOME=%OSGEO4W_ROOT%\apps\Python37
  goto okToSet
)

echo [ERROR]      QGIS Python could not be found.
goto exit1

:okToSet

rem If here can set the PYTHONPATH and PATH to find Python scripts.
rem This is the main code from the original QGIS setup script.
SET PYTHONPATH=%PYTHONHOME%;%PYTHONHOME%\Scripts
PATH %PYTHONPATH%;%PATH%
echo [INFO]       py3_env.bat set:
echo [INFO]         PYTHONPATH = %PYTHONHOME%
echo [INFO]         PATH = %PATH%

:exit0
echo [INFO]     End of GeoProcessor py3_env.bat.  Exiting with status 0.
exit /b 0

:exit1
echo [INFO]     End of GeoProcessor py3_env.bat.  Exiting with status 1.
exit /b 1
