# tests #

This folder contains the
[pytest](https://docs.pytest.org/en/latest/) unit test files for testing
owf-app-geoprocessor-python code.
Unit tests focus on utility code and other low-level code that can be tested
with python unit tests with a straightforward approach.
Functional tests are defined in the
[owf-app-geoprocessor-python-test](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test)
repository and test the full software stack by running the GeoProcessor software.

* [Installing Testing Software on Windows](#installing-testing-software-on-windows)
* [Run Tests](#run-tests)

--------------

## Installing Testing Software on Windows ##

Unit tests are implemented using the `pytest` Python package.
Install the `pytest` package using the OSGeo4W shell so that `pytest` is
recognized by the QGIS version of Python:

1. Run the OSGeo4W Shell (see ***Start / OSGeo4W / OSGeo4W Shell*** menu).
2. To confirm that the OSGeo4W version of python is running, run `where python3`.
Output should indicate that python3 is found as `C:\OSGeo4W64\bin\python3.exe`.
2. Run `C:\OSGeo4W64\bin\py3_env.bat` to configure the Python3 environment
(this may not be necessary in the future but is currently necessary).
3. Run `python3 -m pip install pytest`

## Run Tests ##

The `tests\run-pytest.bat` batch file configures the environment and
runs `pytest -ra`, which prints a summary that emphasizes only non-passing tests.

### Windows Command Prompt ###

To run the tests in Windows command prompt shell:

1. Change to the `tests` folder.
2. Run the batch file `run-pytest.bat`.

### Git Bash ###

To run the tests in Git Bash shell window:

1. Change to the `tests` folder.
2. Run the batch file `./run-pytest.bat`.
This assumes that the batch file is executable, which should be the case by default
Git Bash will find the Windows QGIS Python and other files.
