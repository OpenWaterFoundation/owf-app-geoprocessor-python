# Scripts #

This folder contains scripts used to run the GeoProcessor in various environments.

* Windows:
	+ `gp.bat` - batch file to run the GeoProcessor application in deployed environment
	+ `gpdev.bat` - batch file to run the GeoProcessor application in the development environment
	+ `gptest.bat` - batch file to run the GeoProcessor application as a test framework in deployed environment
	(QGIS code is stubbed out) (**not yet developed**)
* Linux/Cygwin:
	+ `gp.sh` - shell script to run the GeoProcessor application in deployed environment
	+ `gpdev.sh` - shell script file to run the GeoProcessor application in the development environment (**not yet developed**)
	+ `gptest.sh` - shell script to run the GeoProcessor application as a test framework in deployed environment
	(QGIS code is stubbed out)

See the `../build-util` folder for scripts used in the development environment
to build the software.

Updated 05/23/2018 - below scripts have been created but are not final
The below files will be incorporated into the above text once the migration of the GP from QGIS2 to QGIS3 is complete. 

`gpdev3`: Most current environment setup script. **Run this script to run the GP within the QGIS3 environment.** Developed by reading resources online about setting up pyqgis for QGIS3.
`gpdev3-orig`: A test environment setup script. Very similar to the original `gpdev` script but with python3/qgis3 variable values instead of python2/qgis2 variable values. This will be deleted once the GP has been fully migrated to QGIS3.
