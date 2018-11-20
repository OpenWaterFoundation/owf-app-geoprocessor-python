@echo off
rem gpui.bat
rem
rem Simple Windows batch file to run the Open Water Foundation GeoProcessor application
rem user interface.
rem - If it does not work, make sure that gp.bat works.

rem Call the GeoProcessor in UI mode.
call gp --ui

rem Exit with the error level of the gp.bat command
exit /b %ERRORLEVEL%
