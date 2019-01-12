# Scripts #

This folder contains scripts used to run the GeoProcessor in various environments.
The "gptest" version has the QGIS references stripped out so that the test framework can be used in a general way.
Use the `/h` option with any `.bat` file to see the usage of the batch file.
See the `build-util` folder in the `owf-app-geoprocessor-python` repository files
for scripts used in the development environment to build the software.

* Windows:
	+ Development environment:
		+ `gpdev.bat` - batch file to run the GeoProcessor application in the development environment,
		starts the command interpreter
		+ `gpuidev.bat` - batch file to run the GeoProcessor application in the development environment,
		starts the user interface
	+ Deployed environment:
		- `gp.bat` - batch file to run the GeoProcessor application in deployed environment,
		starts the command interpreter
		+ `gpui.bat` - batch file to run the GeoProcessor application in deployed environment,
		starts the user interface
* Linux/Cygwin:
	+ Development environment:
		- `gpdev` - shell script file to run the GeoProcessor application in the development environment,
		starts the command interpreter
		- `gpuidev` - shell script file to run the GeoProcessor application in the development environment,
		starts the user interface
	+ Deployed environment:
		- `gp` - shell script to run the GeoProcessor application in deployed environment,
		starts the command interpreter
		- `gpui` - shell script to run the GeoProcessor application in deployed environment,
		starts the user interface
		- `gptest` - shell script to run the GeoProcessor application as a test framework in deployed environment,
		starts the command interpreter (QGIS code is stubbed out)
		- `gptestui` - shell script to run the GeoProcessor application as a test framework in deployed environment,
		starts the user interface (QGIS code is stubbed out)
