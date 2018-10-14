# Learn GeoProcessor (Dev) / Development Tasks #

This documentation describes common development tasks:

* [Editing Code](#editing-code)
* [Creating Developer Documentation](#creating-developer-documentation)
* [Creating User Documentation](#creating-user-documentation)
* [Testing](#testing)
	+ [Functional Tests](#functional-tests)
	+ [Unit Tests](#unit-tests)
* [Creating Installer](#creating-installer)

--------------------

## Editing Code ##

Code should be edited in an appropriate development tool.
The Open Water Foundation has settled on PyCharm Community Edition for development.
The following guidelines are recommended for using PyCharm:

* As much as possible, follow the [Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/),
with GeoProcessor conventions:
	+ Module and function naming:
		+ Package names are generally lowercase (e.g., `geoprocessor.core`)
		+ Class names are MixedCase (e.g, `GeoProcessor` in file `geoprocessor/core/GeoProcessor.py`)
		+ Non-class module names are lowercase
		+ Function names are lowercase and use underscores to separate words, as needed
	+ Module file contents:
		+ Each class has its own file (`ClassName.py` for class named `ClassName`).
		+ Other modules contain functions grouped by functionality.
		For example `geoprocessor.util.string_util.py` contains utility functions that process strings.
* Respond to PyCharm PEP warnings to fix style issues so that each file receives a check-off.

## Creating Developer Documentation ##

Developer documentation uses the MkDocs software.
See the [developer documentation in the main code repository](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/doc-dev-mkdocs-project/README.md).
The developer documentation is maintained with the code since it needs to be kept consistent with changes in the code.

## Creating User Documentation ##

User documentation uses the MkDocs software.
See the [user documentation repository](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-doc-user).
The user documentation is maintained in a separate repository because contributions may be submitted by non-programmers.

## Testing ##

The GeoProcessor is designed to facilitate automated testing.
Each command and workflows involving multiple commands can be tested.

### Functional Tests ###

Functional tests run the GeoProcessor software in the development or installed (deployed) environment and
test the internal code, environment, operational tools, and workflow.
Anything that breaks in the technology stack or test configuration will result in a test failure,
which effectively implements tests at a larger scope than code unit tests.
The GeoProcessor testing framework can also be used to test other software,
for example by using
[`RunProgram`](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/command-ref/RunProgram/RunProgram/)
commands.

See the [functional testing repository](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test)
for examples of functional test workflows.
Functional tests are maintained in a separate repository because contributions may be submitted by non-programmers,
and to limit the size of the code repository.

Functional tests stored in the above repository are generally run one of two ways:

1. **Run individual tests (useful when working on a specific workflow/test)**:
	1. **Create** a script to run individual test:
		1. ![Windows](../images/windows-32.png) Windows: For example:
		[run-tests-steve.bat](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/blob/master/test/suites/run/run-tests-steve.bat).
		This example uses the
		[`gpdev.bat`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gpdev.bat)
		batch file to run the GeoProcessor, which is typical during GeoProcessor software develoment.
		2. ![Linux](../images/linux-32.png) Linux: For example:
		[run-tests-steve.sh](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/blob/master/test/suites/run/run-tests-steve.sh).
		This example uses the
		[`gptest.sh`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gptest.sh)
		shell script to run the GeoProcessor, which is typical when using the GeoProcessor as as functional testing framework for other software.
	2. **Run** the above:
		1. ![Windows](../images/windows-32.png) Windows:  run in a windows command prompt window.
		2. ![Linux](../images/linux-32.png) Linux: run in a Linux shell window.
	3. **Review** the log file created by the batch file (if redirected to a log file)
	and command file that was run (if the `StartLog` command was used).  Fix issues and run again.
2. **Run auto-generated test suite (useful when testing all software features before software release):**
	1. **Create** the command file to run tests, using files in the
	[`test/suite/create`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/tree/master/test/suites/create)
	folder in repository working files.  The following command walks the folder tree in
	[`test/commands`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/tree/master/test/commands)
	and creates a command
	file with [`RunCommands`](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/command-ref/RunCommands/RunCommands/)
	commands for each test to run,
	plus some additional testing commands for reporting.
		1. ![Windows](../images/windows-32.png) Windows:  Use the GeoProcessor to run the
		command file in a command shell window to auto-generate the full GeoProcessor test suite:
		[create-test-command-file-dev.bat](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/blob/master/test/suites/create/create-test-command-file-dev.bat)
		(to test with development environment GeoProcessor) or
		[create-test-command-file.bat](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/blob/master/test/suites/create/create-test-command-file.bat)
		(to test with deployed environment GeoProcessor).
		This runs the command file
		[create-regression-test-command-file.gp](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/blob/master/test/suites/create/create-regression-test-command-file.gp).
		2. ![Linux](../images/linux-32.png) Linux:  Use the GeoProcessor to run the
		command file in a terminal window to  auto-generate the full GeoProcessor test suite:
		[create-test-command-file.sh](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/blob/master/test/suites/create/create-test-command-file.sh)
		(to test with deployed environment test GeoProcessor).
		This runs the command file
		[create-regression-test-command-file.gp](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/blob/master/test/suites/create/create-regression-test-command-file.gp).
		**GeoProcessor development currently occurs on Windows but better support for Linux development will be added in the future.
		Running the script described here defaults to using the
		[`gptest.sh`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gptest.sh)
		script.  Other script variations can be defined as needed.**
	2. **Run** the command file created in the previous step:
		1. ![Windows](../images/windows-32.png) Windows:  In a Windows command prompt window, run the test suite from the previous step:
		[run-geoprocessor-tests.bat](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/blob/master/test/suites/run/run-geoprocessor-tests.bat).
		This currently uses the
		[`gpdev.bat`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gpdev.bat)
		batch file to run.
		2. ![Linux](../images/linux-32.png) Linux: In a Linux terminal window, run the test suite from the previous step:
		[run-geoprocessor-tests.sh](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/blob/master/test/suites/run/run-geoprocessor-tests.sh)
		This currently uses the
		[`gptest.sh`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gptest.sh)
		batch file to run.
	3. **Review** test results:
		1. Review the log file created by the previous step and command files that were run
		(from `StartLog` commands used in tests).
		2. Review the test summary file (`geoprocessor-tests-out.gp.txt`) that was generated by the test suite command file.
		This has one line per test indicating whether the test passed, and a summary at the bottom.
		Use a text editor to search for failures.
		See example below.
		3. Review the command summary file (`geoprocessor-tests.gp.summary.html`) that was generated by the test suite command file
		This file contains a summary of all command log messages in a color-coded HTML file,
		which provide specifics for failed tests.
		View the file in a web browser.
		See example below.
		4. Fix issues in the software and test and run again.

Example command file `create-regression-test-command-file.gp` for automated test suite
(this file is dynamically-created and is not saved in the repository):

```text
# File generated by...
# program:      gp.py 0.0.1
# user:         sam
# date:         2018-01-30T01:33:40.672000
# host:         colorado
# directory:    
# command line: gp.py
#  C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python\geoprocessor\app\gp.py
# #             --commands create-regression-test-command-file.gp
# -----------------------------------------------------------------------
#
# The following 68 test cases will be run to compare results with expected results.
# Individual log files are generally created for each test.
StartRegressionTestResultsReport(OutputFile="C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python-test\test\suites\run\geoprocessor-tests.gp.out.txt")
RunCommands(CommandFile="..\..\..\test\commands\AddGeoLayerAttribute\test-AddGeoLayerAttribute-Line-Memory.gp")
...other similar commands...
WriteCommandSummaryToFile(OutputFile="C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python-test\test\suites\run\geoprocessor-tests.gp.summary.html")
```

Example of `geoprocessor-tests-out.gp.txt` file (this file is dynamically-created and is not saved in the repository):

```text
# File generated by...
# program:      gp.py 0.0.1
# user:         sam
# date:         2018-02-18T06:47:05.871000
# host:         colorado
# directory:    
# command line: gp.py
# 
# #             C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python\geoprocessor\app\gp.py
# #             --commands geoprocessor-tests.gp
# -----------------------------------------------------------------------
#
# Command file regression test report from StartRegressionTestResultsReport() and RunCommands()
#
# Explanation of columns:
#
# Num: count of the tests
# Enabled: TRUE if test enabled or FALSE if "#@enabled false" in command file
# Run Time: run time in milliseconds
# Test Pass/Fail:
#    The test status below may be PASS or FAIL (or blank if disabled).
#    A test will pass if the command file actual status matches the expected status.
#    Disabled tests are not run and do not count as PASS or FAIL.
#    Search for *FAIL* to find failed tests.
# Commands Expected Status:
#    Default is assumed to be SUCCESS.
#    "#@expectedStatus Warning|Failure" comment in command file overrides default.
# Commands Actual Status:
#    The most severe status (Success|Warning|Failure) for each command file.
#
#    |       |Test  |Command   |Command    |
#    |       |Pass/ |Expected  |Actual     |
# Num|Enabled|Fail  |Status    |Status     |Command File
#----+-------+------+----------+-----------+---------------------------------------------------------------------------------------------
00001|TRUE   | PASS |SUCCESS   |SUCCESS    |C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python-test\test\commands\AddGeoLayerAttribute\test-AddGeoLayerAttribute-Line-Memory.gp
00002|TRUE   | PASS |SUCCESS   |SUCCESS    |C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python-test\test\commands\AddGeoLayerAttribute\test-AddGeoLayerAttribute-Line-OnDisk.gp
00003|TRUE   | PASS |SUCCESS   |SUCCESS    |C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python-test\test\commands\AddGeoLayerAttribute\test-AddGeoLayerAttribute-Point-Memory.gp
00004|TRUE   | PASS |SUCCESS   |SUCCESS    |C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python-test\test\commands\AddGeoLayerAttribute\test-AddGeoLayerAttribute-Point-OnDisk.gp
...
...
#----+-------+-------+------+----------+-----------+---------------------------------------------------------------------------------------------
FAIL count     = 21, 21.000%
PASS count     = 78, 78.000%
Disabled count = 1, 1.000%
#--------------------------------
Total          = 100
#----+-------+-------+------+----------+-----------+---------------------------------------------------------------------------------------------
FAIL count     = 21, 21.000%
PASS count     = 78, 78.000%
Disabled count = 1, 1.000%
#--------------------------------
Total          = 100
```

Example of `geoprocessor-tests.gp.summary.html` file
(this file is dynamically-created and is not saved in the repository):

![summary](images/geoprocessor-tests.gp.summary.html.png)

### Unit Tests ###

The GeoProcessor does not currently utilize unit tests such a pytest.
However, units tests will be added in the future.
The majority of testing currently uses the functional test framework in order to test full functionality and user experience.

## Creating Installer ##

The GeoProcessor is not yet packaged via a `pip` or `pipenv` installer.
Instead, zip files (Windows) and tar.gz files (Linux) are created containing the `geoprocessor` package.
These files can be unzipped in the `site-packages` (or similar) folder in the deployed Python environment
so that they are found when Python runs.
Use the following to check the target Python environment to see which folders are searched for modules.
The GeoProcessor package can be installed in one of the indicated folders or
the run script (`gp.bat`, `gp.sh`, `gptest.bat`, or `gptest.sh`) will need to set the `PYTHONPATH`
to include the folder where the files are installed.
**This needs to be updated for Python 3.**

```
python2
>>> import sys
>>> print(sys.path)
['', '/usr/lib/python2.7/site-packages/logilab_common-0.62.0-py2.7.egg', '/usr/lib/python27.zip', '/usr/lib/python2.7', '/usr/lib/python2.7/plat-cygwin', '/usr/lib/python2.7/lib-tk', '/usr/lib/python2.7/lib-old', '/usr/lib/python2.7/lib-dynload', '/usr/lib/python2.7/site-packages']
>>> quit()
```
Another useful technique to use during troubleshooting is to run `python -v`
to print out verbose information about which folder
modules were loaded from, given the above choices.
This may require editing the standard `gp.bat` and similar files.
This approach can be used if the `geoprocessor` files are installed in more than one place
and old files are being used instead of an updated version.

Windows batch files (`gp.bat` and `gptest.bat`) and Linux shell script (`gp.sh` and `gptest.sh`)
files are used to run the GeoProcessor software,
and can be installed in an appropriate location.
These files will be stored in a standard software folder and accessed via operating system "start" menu
once the user interface for the GeoProcessor is implemented.

Use the following process to create the installer packages in the developer environment.
The following currently creates .tar.gz and .zip versions of the files and therefore the
`tar`, `gzip`, and `zip` programs must be available to completely process the installer
(error messages are printed to help diagnose issues).

1. Open a Linux shell window:
	1. ![Cygwin](../images/cygwin-32.png) Cygwin terminal (verified method used by developers)
	2. ![Git Bash](../images/git-bash-32.png) Git Bash (**should work but not yet verified**)
	3. ![Windows](../images/windows-32.png) Windows Subsystem for Linux Bash (**should work but not yet verified**)
	3. ![Linux](../images/linux-32.png) Linux terminal (**should work but not yet verified**)
2. Change directories to the `build-util` folder in the repository working files.
3. Run the following script:  `create-gp-installer.sh`
	1. This will create files in the `build` folder in the repository working files.
	2. See the [`build/README.md`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/build/README.md)
	file for more information about folder contents.
	3. If an error is shown, follow instructions.
		1. One issue is that may occur is that if the code was checked out with Git Bash (for example)
		and the script is run with Cygwin, there may be newline issues.
		Run `dos2unix` on the script if necessary (Git may want to commit, but `.gitattributes` will cause the commit to be ignored).

The GeoProcessor software can then be installed as per the
[User Documentation](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/install/).
