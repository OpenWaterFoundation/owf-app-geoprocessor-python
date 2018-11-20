@echo off
rem gpuidev.bat
rem
rem Windows batch file to run the Open Water Foundation GeoProcessor application, UI mode in developer environment
rem - if it does not work, run gpdev.bat first to troubleshoot

rem Call the main batch file
call gpdev.bat --ui

rem Exit with the error level of the above batch file
exit /b %ERRORLEVEL%
