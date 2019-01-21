# GeoProcessor / Development Environment / Running the GeoProcessor #

* [Running in the Development Environment](#running-in-the-development-environment)
* [Running in the Operational Environment](#running-in-the-operational-environment)
* [Running in the Testing Framework Environment](#running-in-the-testing-framework-environment)

----------------

## Running in the Development Environment ##

The GeoProcessor is typically run in the development environment using a script that uses Python 2
and sets `PYTHONPATH` to include the development GeoProcessor files:

* ![Cygwin](../images/cygwin-32.png) Linux:
	+ `scripts/gpdev` - **Not yet developed.**
	+ Run the testing framework by deploying to Cygwin Python virtual machine to run testing framework
* ![Linux](../images/linux-32.png) Linux:
	+ `scripts/gpdev` - **Not yet developed.**
	+ Run the testing framework by deploying to Linux Python virtual machine to run testing framework
* ![Windows](../images/windows-32.png) Windows 10:
	+ [`scripts/gpdev.bat`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gpdev.bat) batch file.
	+ [`scripts/gpuidev.bat`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gpuidev.bat) batch file.

The above scripts checks to see whether the runtime environment needs to be set up.
If so it runs the QGIS setup batch file (script) similar to what is run for PyCharm environment setup
and then runs the GeoProcessor by passing command line arguments that were provided.
This approach ensures that the most recent code is being used.
It is common to run this version on [functional tests during development](../dev-tasks/testing.md#functional-tests).

## Running in the Operational Environment ##

The GeoProcessor can be run using the operational mode: 

* ![Cygwin](../images/cygwin-32.png) Linux:
	+ [`scripts/gp`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gp) shell script - **need to deploy with QGIS**
	+ [`scripts/gpui`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gpui) shell script - **need to deploy with QGIS**
* ![Linux](../images/linux-32.png) Linux:
	+ [`scripts/gp`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gp) shell script - **need to deploy with QGIS**
	+ [`scripts/gpui`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gpui) shell script - **need to deploy with QGIS**
* ![Windows](../images/windows-32.png) Windows 10:
	+ [`scripts/gp.bat`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gp.bat) batch file
	+ [`scripts/gpui.bat`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gpui.bat) batch file to run UI

The above checks to see whether the runtime environment needs to be set up.
If so it runs the QGIS setup batch file (script) similar to what is run for PyCharm environment setup
and then runs the GeoProcessor by passing command line arguments that were provided.
This approach depends on the geoprocessor being installed in a location that Python can find it.
It does not run the most recent code being edited and therefore has limited use in the development environment,
other than testing deployment (such as confirming dependencies).

## Running in the Testing Framework Environment ##

The GeoProcessor can be run in a limited test environment that does not use the QGIS software,
using a script that uses Python 3 in a Python virtual environment:

* ![Cygwin](../images/cygwin-32.png) Cygwin:
	+ [`scripts/gptest`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gptest) shell script
	+ [`scripts/gptestui`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gptestui) shell script to run UI
* ![Linux](../images/linux-32.png) Linux:
	+ [`scripts/gptest`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gptest) shell script
	+ [`scripts/gptestui`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gptestui) shell script to run UI
* ![Windows](../images/windows-32.png) Windows 10:
	+ `scripts/gptest.bat` - **Not yet developed.**

This approach can use the GeoProcessor as a functional test framework independent of QGIS.
It is common to run the testing framework to run [functional tests for a software product](../dev-tasks/testing.md#functional-tests).
