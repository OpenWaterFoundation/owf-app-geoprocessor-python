# Scripts #

This folder contains scripts used to run the GeoProcessor in various environments.
The "test" version has the QGIS references stripped out so that the test framework can be used in a general way.

* Windows:
	+ `gp.bat` - batch file to run the GeoProcessor application in deployed environment,
	starts the command interpreter
	+ `gpui.bat` - batch file to run the GeoProcessor application in deployed environment,
	starts the user interface
	+ `gpdev.bat` - batch file to run the GeoProcessor application in the development environment,
	starts the command interpreter
	+ `gpuidev.bat` - batch file to run the GeoProcessor application in the development environment,
	starts the user interface
* Linux/Cygwin:
	+ `gp` - shell script to run the GeoProcessor application in deployed environment,
	starts the command interpreter
	+ `gpui` - shell script to run the GeoProcessor application in deployed environment,
	starts the user interface
	+ `gpdev` - shell script file to run the GeoProcessor application in the development environment,
	starts the command interpreter
	(**currently not a focus because development focuses on Windows via `gpdev.bat`**)
	+ `gptest` - shell script to run the GeoProcessor application as a test framework in deployed environment,
	starts the command interpreter (QGIS code is stubbed out)
	+ `gptestui` - shell script to run the GeoProcessor application as a test framework in deployed environment,
	starts the user interface (QGIS code is stubbed out)

See the `../build-util` folder for scripts used in the development environment to build the software.
