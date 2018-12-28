@echo off
rem gpui.bat
rem _________________________________________________________________NoticeStart_
rem GeoProcessor
rem Copyright (C) 2017-2019 Open Water Foundation
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
rem Simple Windows batch file to run the Open Water Foundation GeoProcessor application
rem user interface.
rem - If it does not work, make sure that gp.bat works.

rem Call the GeoProcessor in UI mode.
call gp --ui

rem Exit with the error level of the gp.bat command
exit /b %ERRORLEVEL%
