@echo off
rem gpuidev.bat
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
rem Windows batch file to run the Open Water Foundation GeoProcessor application, UI mode in developer environment:
rem - if it does not work, run gpdev.bat first to troubleshoot

rem Determine the folder that the script was called in.
set scriptFolder=%~dp0
rem Remove trailing \ from 'scriptFolder'.
set scriptFolder=%scriptFolder:~0,-1%

rem Call the GeoProcessor in UI mode for development environment:
rem - use the full path because 'gpdev' may not be in the PATH
rem - this batch file may be called with /s or /u so pass arguments to general batch file
call "%scriptFolder%\gpdev.bat" --ui %*

rem Exit with the error level of the above batch file.
exit /b %ERRORLEVEL%
