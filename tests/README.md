# tests #

This folder contains the
[pytest](https://docs.pytest.org/en/latest/) unit test files for testing
`owf-app-geoprocessor-python` code.
Unit tests focus on utility code and other low-level code that can be tested
with python unit tests with a straightforward approach.
Functional tests are defined in the
[owf-app-geoprocessor-python-test](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test)
repository and test the full software stack by running the GeoProcessor software.

* [Tests Folder Structure](#tests-folder-structure)
* [Installing Testing Software on Windows](#installing-testing-software-on-windows)
* [Run Tests](#run-tests)

--------------

## Tests Folder Structure ##

The structure of the tests folder is directly correlated to the geoprocessor top level folder.
Naming conventions for test files starts with `test_file_to_test.py`.
Naming convention for functions in test files follows similarly `test_function_to_test()`.

```
├── tests/
|   ├── geoprocessor/
|   |   ├── util
|   |   |   ├── test_io_util.py
|   |   |   ├── test_os_util.py
|   |   |   ├── test_string_util.py
|   |   |   ├── test_zip_util.py
```

## Installing Testing Software on Windows ##

Unit tests are implemented using the `pytest` Python package.
Install the `pytest` package using the OSGeo4W shell so that `pytest` is recognized by the QGIS version of Python:

1. Run the OSGeo4W Shell (see ***Start / OSGeo4W / OSGeo4W Shell*** menu).
2. To confirm that the OSGeo4W version of python is running, run `where python3`.
Output should indicate that python3 is found as `C:\OSGeo4W64\bin\python3.exe`.
2. Run `C:\OSGeo4W64\bin\py3_env.bat` to configure the Python3 environment
(this may not be necessary in the future but is currently necessary).
3. Run `python3 -m pip install pytest`

## Run Tests ##

The `tests\run-pytest.bat` batch file configures the environment and runs `pytest -ra`,
which prints a summary that emphasizes only non-passing tests.

### Parameters: ###

The script `run-pytest.bat` is hard-coded to use the flag `-ra`.
The `-r` flag can be used to display a “short test summary info” at the end of the test session,
making it easy in large test suites to get a clear picture of all failures, skips, xfails, etc.
The `-r` options accepts a number of characters after it, with `a` used above meaning “all except passes”.

Some other flags that have come in useful in development:  

* `-s` - Allows print statements to be printed to console when tests are run.
* `-vv` - Shows additional details for tests. Useful when dealing with failing tests.

## Temp Folders ##

For testing purposes there may be scenarios where it is necessary to create,
edit, and delete files. For these tests there is a PyTest standard of moving
files into the users temporary directory.  
`C:\Users\{User}\AppData\Local\Temp\pytest-of-{User}`

Each time a test is run it creates a new folder in this path:  

```
├── pytest-of-{User}/
|   ├── pytest-1/
|   ├── pytest-2/
|   ├── pytest-3/
```

As more tests are run PyTest keeps track of the last 3 tests in this folder.
If PyTest is run 4 times then `pytest-1/` would be removed and `pytest-4/` would be added to the folder.

Within each of these folders, PyTest will create a new subfolder for each
separate function using the `tempdir` variable, for example:  

```
├── pytest-of-{User}/
|   ├── pytest-1/
|   |   ├── test_expand_formatter_extensio0
|   |   ├── test_expand_formatter_filename0
|   |   ├── test_expand_formatter_ful_pat0
```

In the development process it is a question of whether to leave the files as they
are so users can go look back at the files or to remove them once the tests have been completed.
It is also a question of moving these folders out of the user's temporary directory and
potentially into a local data folder in the same level as the tests themselves.

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
