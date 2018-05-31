# Scripts #

This folder contains scripts used to run the GeoProcessor in various environments.

* Windows:
	+ `gp.bat` - batch file to run the GeoProcessor application in deployed environment
	+ `gpdev.bat` - batch file to run the GeoProcessor application in the development environment
	+ `gptest.bat` - batch file to run the GeoProcessor application as a test framework in deployed environment
	(QGIS code is stubbed out) (**not yet developed**)
	+ Files with `2` in the name are copies of old Python2/QGIS2 scripts and are kept for archival/comparison purposes.
	They will be removed once Python3/QGIS3 code checks out.
* Linux/Cygwin:
	+ `gp.sh` - shell script to run the GeoProcessor application in deployed environment
	+ `gpdev.sh` - shell script file to run the GeoProcessor application in the development environment (**not yet developed**)
	+ `gptest.sh` - shell script to run the GeoProcessor application as a test framework in deployed environment
	(QGIS code is stubbed out)
	+ Files with `2` in the name are copies of old Python2/QGIS2 scripts and are kept for archival/comparison purposes.
	They will be removed once Python3/QGIS3 code checks out.

See the `../build-util` folder for scripts used in the development environment to build the software.
