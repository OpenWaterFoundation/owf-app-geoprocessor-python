@echo off
rem 2-update-gp-venv.bat
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
rem Update the Windows virtual environment with current code files
rem - this way it is not necessary to recreate the virtual environment from scratch

rem Determine the folder that the script was called in
rem - includes the trailing backslash
set scriptFolder=%~dp0
rem Remove trailing \ from scriptFolder
set scriptFolder=%scriptFolder:~0,-1%

rem Call the create batch file in UI mode.
rem - use the full path because 'gp' may not be in the PATH
echo Calling: 2-create-gp-venv.bat -u --nozip
call "%scriptFolder%\2-create-gp-venv.bat" -u --nozip

rem Exit with the error level of the gp.bat command
exit /b %ERRORLEVEL%
