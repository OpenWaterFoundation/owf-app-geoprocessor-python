# GeoProcessor / Software Design #

**This section needs to be reviewed once the UI command editors are implemented.**

The GeoProcessor software design leverages Python features and best practices
while incorporating TSTool design elements.

* [GeoProcessor Design Background](#geoprocessor-design-background) - general background
* [Command File and Command Syntax](#command-file-and-command-syntax) - the user-facing representation of commands and workflow
* [QGIS Environment](#qgis-environment) - provides access to QGIS geoprocessing features
* [GeoProcessor Class](#geoprocessor-class) - the core class that runs GeoProcessor command workflows
* [GeoProcessorCommandFactory Class](#geoprocessorcommandfactory-class) - creates command instances from text command
* [AbstractCommand Class and Command Classes](#abstractcommand-class-and-command-classes) - classes that perform specific processing
* [CommandStatus Class](#commandstatus-class) - used to track issues with commands
* [Utility Modules](#utility-modules) - utility code
* [Logging](#logging) - logging processing progress
* [GeoLayer Class](#geolayer-class) - main class for storing vector layers
* [gp Application](#gp-application) - application to manage using GeoProcessor instance in different run modes
* [User Interface](#user-interface) - user interface
* [User Interface (Old)](#user-interface-old) - user interface (old)
* [Built-in Test Framework](#built-in-test-framework) - used to run functional tests
* [Future Design Elements](#future-design-elements) - as-yet implemented features

----------------------

## GeoProcessor Design Background ##

This GeoProcessor software leverages the Python geoprocessing libraries from QGIS
while implementing the command/workflow feature
design developed in the [TSTool time series processing software](http://openwaterfoundation.org/software-tools/tstool).
Many lessons were learned developing TSTool that have been applied to the GeoProcessor.

The GeoProcessor is written for Python 3 because current QGIS libraries use Python 3.

TSTool is written in Java and is being moved to an open source project.
Java is object-oriented and the time series processor design is modular.
Although Python provides object-oriented features via classes,
there are differences between Java and Python, in particular:

* Java does not support multiple inheritance and Python does.
* Java supports interfaces and Python does not (natively).
* Java provides enumerations and Python 2 does not (Python 3 does).
* Java provides private and public levels whereas Python sometimes relies on convention,
such as using `__` prefix on data and functions to indicate private data.
* Java concepts of static classes is paralleled by Python `@classmethod`, `@staticmethod` and module functions.

Consequently, the TSTool design has been adapted from Java to Python.
In many cases, the Java code has been simplified in order to streamline GeoProcessor development
and to evaluate options to improve/simplify the original Java design.  For example, simplifications include:

* Specific exceptions in Java code have been simplified to use built-in Python `ValueError` for checking input
and `RuntimeError` for run-time errors.
Additional exception classes may be used but a simple design that works will win out.
* Java class setter/getter methods have been omitted in favor of Pythonic direct-access to data
(exceptions are cases when more robust error checks are needed).
Class constructors with instance data are used to create object instances.

The following sections describe specific components by explaining GeoProcessor classes.
Links to code on the master branch of the repository are provided.
Right-click on the link and view in a separate window to facilitate review
of the documentation and code at the same time.

## Command File and Command Syntax ##

The GeoProcessor performs its work by interpreting a workflow of commands.
A command file is text file containing lines with one command per line.
For example, see any of the command files with names ending in `.gp` in the
[automated tests](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/tree/master/test/commands).

The command file lines include:

* One-line comments starting with `#` character.
* Indentation is OK.
* Blank lines.
* Control commands including `For` and `If`.
* Commands that follow syntax:

```text
CommandName(Parameter1="Value1",Parameter2="Value2",...)
```

Conventions for commands and command files are described in the
[GeoProcessor user documentation](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/).

## QGIS Environment ##

The GeoProcessor relies on the QGIS environment and Python libraries.
In particular, the following are used:

* QGIS runtime environment, initialized before running applications such as the [gp application](#gp-application) (discussed below).
* QGIS Python processing algorithms and plugins, used in [Command classes](#abstractcommand-class-and-command-classes) (discussed below).
* QGIS user interface features, used in the [Graphical User Interface](#graphical-user-interface) (discussed below).

In order to use the QGIS environment in the deployed environment (including `gp` application),
the GeoProcessor runs the Python software distributed with QGIS,
with `PYTHONPATH` configured to find GeoProcessor modules.
In the PyCharm development environment, PyCharm uses the project Python interpreter and
relies on `PYTHONPATH` to find QGIS libraries.
**The following configuration scripts have been created for initial prototyping and will
be made more robust for general use.**

* Configuration in the developer environment is accomplished by running a setup script,
for example [run-pycharm2018.2.4-for-qgis.bat](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/build-util/run-pycharm-ce-for-qgis.bat).
	+ This script runs the QGIS `ow4_env.bat` batch file and performs additional configuration.
* Configuration in the runtime environment is accomplished by running the
[`gp.bat`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gp.bat) batch file on Windows
or [`gp.sh`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gp.sh) script on Linux.
Each of these start Python and run the
[`geoprocessor/app/gp.py`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/app/gp.py)
module as the entry-point into the Python GeoProcessor environment.
The script runs similar setup steps as the develop environment script.
This script can be used to run GeoProcessor command files in the test framework.
For example, see the test runner that has been manually created:
[`run-tests-steve.bat`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/blob/master/test/suites/run/run-tests-steve.bat).
The automated test framework that uses `RunCommands` commands, similar to TSTool, is also available and is
described in [Development Tasks / Testing](../dev-tasks/testing.md).

## GeoProcessor Class ##

The
[`geoprocessor.core.GeoProcessor`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/core/GeoProcessor.py)
class forms the core of the GeoProcessor package.
The GeoProcessor provides the following design elements and functionality:

* An instance is created to maintain a list of commands and run the commands.
* Important data members:
	+ a list of command class objects, which are expected to extend from `AbstractCommand` class
	+ a dictionary of properties (objects) for use by the processor, for example
	string that contains the working directory
	+ a list of `GeoLayer` objects, which are created by the processor
	(these objects are accessed by commands via a unique identifier)
* Functions:
	+ the `read_command_file` function reads a command file and instantiates command objects
	+ the `run_commands` function runs the commands in the processor list (or a subset)
	+ the `expand_parameter_value` function processes command parameter strings that include `${Property}`
	syntax into expanded strings, using the list of processor properties - this
	supports dynamic processing features such as for loops and parameters that reflect shared properties
	+ the `get_property` function returns a processor property and also gracefully
	handles missing properties so that calling code can be more direct
	+ the `set_property` function is a utility function to set a property in the dictionary

A GeoProcessor instance can be created to run a command file in batch mode,
for example when using the
[`CommandFileRunner`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/core/CommandFileRunner.py) class.
An instance is also be used by the user interface to interactively edit and run commands,
which can also be saved to a command file. 

## GeoProcessorCommandFactory Class ##

The
[`GeoProcessorCommandFactory`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/core/GeoProcessorCommandFactory.py)
class examines a command string and instantiates a corresponding command class of the proper type.
This occurs through a simple lookup to identify the proper command and then calling the
constructor (`__init__()` function is called as per normal Python object initialization) for the matching command,
for example:

```text
elif command_name_upper == "SETPROPERTY":
    return SetProperty()

```

The returned command is not fully parsed by the command factory - that step occurs as necessary in other code,
for example the `read_command_file` function in the GeoProcessor instance,
or in the user interface after a command string has been created via a command editor.

## AbstractCommand Class and Command Classes ##

The
[`AbstractCommand`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/commands/abstract/AbstractCommand.py)
class provides common command features.  All commands are expected to extend this class.
Design elements of this class include:

* An instance is created for each command in a command file.
* Important data members:
	+ `command_string` is the full command string, including leading indentation.
	+ `command_name` is the command name, the command string before the left-most `(`.
	+ `command_processor` is the GeoProcessor instance that is managing the command - this allows
	the command to retrieve processor data such as GeoLayers, for processing within the command,
	and to save data back to the processor
	+ `command_parameters` is a dictionary of command parameters
		- the key matches the parameter name
		- values are the parameter value **as a string (not parsed object type)**
		- strings are used to ensure clean conversion between edited values and command file values,
		and to allow use of `${Property}` notation for all parameter value types
		- strings are converted to necessary object representations when running commands
	+ `command_parameter_metadata` is a list of
	[`CommandParameterMetadata`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/core/CommandParameterMetadata.py),
	which provides information that allows checking for valid parameter names and types, shared between class instances.
	+ `command_status` is an instance of `CommandStatus`, which maintains a list of `CommandLogRecord`,
	used to track issues in initializing and running commands (see discussion below).
* Important functions: 
	+ `check_command_parameters` - is expected to be defined in child command class to validate
	command parameter values during command initialization
	+ `get_parameter_metadata` - is a utility function to return the metadata for a parameter name
	+ `get_parameter_value` - is a utility function to return a parameter string value from the parameter dictionary,
	gracefully handles missing parameters (which is OK because default values will be used at runtime)
	+ `initialize_command` - utility function that is called to
		- set the GeoProcessor instance
		- set the command string
		- optionally parse the command string into parameter string dictionary
	+ `parse_command` - utility function to parse the command string into parameter string dictionary
	+ `run_command` - is expected to be defined in child command class to run the command
	+ `to_string` - utility function to convert the internal parameter string dictionary
	into the single-line command string

The `AbstractCommand` class is the parent class from which all other commands are derived.
Specific commands are organized in groups under the `geoprocessor.commands` package,
for example, the `geoprocessor.commands.running` package contains commands that are associated with
controlling running commands.

* See the [Command Reference Overview](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/command-ref/overview/)

Command class design considerations include:

* One class is stored per source file and the name of the file matches the class name
* Instances are created for each line in a command file
	+ [`UnknownCommand`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/commands/util/UnknownCommand.py)
	is used when the command name is not recognized by the `GeoProcessorCommandFactory`
	+ [`Blank`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/commands/util/Blank.py)
	is used as a place-holder for blank lines
	+ [`Comment`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/commands/util/Comment.py)
	is used for `#` comments
* Data
	+ Private data values should be defined as needed; however, in most cases data local to functions may be adequate
	because the GeoProcessor instance maintains primate data like the list of GeoLayers
	+ `command_name` from `AbstractCommand` is set to the command name
	+ `command_parameter_metadata` from `AbstractCommand` is set to the command parameter metadata 
* Functions
	+ `check_command_parameters` - checks command parameter values at initialization for valid values
		- required parameters must be defined
		- parameter string values are checked for validity using `geoprocessor.util.validators` module functions.
		- adds `CommandStatus` messages for `command_phase_type.INITIALIZATION` run phase
		- **DOES NOT** do checks at runtime
	+ `run_command` - executes the functionality of the command
		- file/folder parameters are converted to absolute paths using the processor `WorkingDir` property
		using `geoprocessor.util.io.to_absolute_path` function
		- parameters containing `${Property}` notation are expanded to full values prior to use using the
		GeoProcessor `expand_parameter_value` function.
		- converts string parameter dictionary values into object types needed for run-time, raising `ValueError` if any issues
		- performs run-time parameter checks to reflect that parameter values and data are dynamic
		(see for example the check functions found in the `run_command` method in
		[`CopyGeoLayer`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/commands/layers/CopyGeoLayer.py) command).
		- performs the processing
		- saves results back to the GeoProcessor if appropriate
		- raises `RuntimeError` if an error
		- adds `CommandStatus` messages for `command_phase_type.RUN` run phase

## CommandStatus Class ##

The
[`AbstractCommand`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/commands/abstract/AbstractCommand.py)
class includes the `command_status` data object, which is an instance of
[`CommandStatus`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/core/CommandStatus.py).
This object maintains a list of 
[`CommandLogRecord`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/core/CommandLogRecord.py),
which allows tracking issues with command initialization and running.
Populating log messages at a command level is key to providing pinpoint diagnostics used in the UI and
creating command file run reports with
[`WriteCommandSummaryToFile`](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/command-ref/WriteCommandSummaryToFile/WriteCommandSummaryToFile).

The resulting messages can be output to a file to pinpoint command issues during troubleshooting and
can also be displayed by the user interface.

The following is an example of setting the command status in the `check_command_parameters` function via
the `add_to_log` function:

```python
pv_PropertyType = self.get_parameter_value(parameter_name='PropertyType', command_parameters=command_parameters)
property_types = ["bool", "float", "int", "long", "str"]
if not validators.validate_string_in_list(pv_PropertyType, property_types, False, False):
    message = 'The requested property type "' + pv_PropertyType + '"" is invalid.'
    warning += "\n" + message
    self.command_status.add_to_log(
        command_phase_type.INITIALIZATION,
        CommandLogRecord(command_status_type.FAILURE, message, "Specify a valid property type:  " +
                         str(property_types)))
```

The following is an example of setting the command status in the `run_command` function:

```python
except Exception as e:
    ++warning_count
    message = 'Unexpected error setting property "' + pv_PropertyName + '"'
    logger.exception(message, e)
    self.command_status.add_to_log(
        command_phase_type.RUN,
        CommandLogRecord(command_status_type.FAILURE, message,
                         "Check the log file for details."))
```

## Utility Modules ##

The `geoprocessor.util` package includes utility modules with functions that can be called from
classes and other code to perform useful tasks:

* [`app_util`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/util/app_util.py) - application global data
* [`command_util`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/util/command_util.py) - command parsing, etc.
* [`file_util`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/util/file_util.py) - file handling (**May need to combine with `io_util`**)
* [`io_util`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/util/io_util.py) - input/output
* [`log_util`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/util/log_util.py) - log file handling
* [`qgis_util`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/util/qgis_util.py) - code specific to QGIS
* [`string_util`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/util/string_util.py) - string processing
* [`validator_util`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/util/validator_util.py) - validators for command parameters

These modules and additional utility modules will be enhanced over time.

## Logging ##

The GeoProcessor modules uses standard Python `logging` module features
in order to support troubleshooting.
However, the log file is not simple for users to interpret and the final software user interface
will provide features to view command status using the
[`CommandStatus`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/core/CommandStatus.py) data.
Additional guidance on logging topics is provided below.

### Log File ###

The `geoprocessor.app.gp` module contains a main program to run the GeoProcessor.
This program starts an initial log file at `INFO` level in the user's home folder,
for example on Windows `C:\Users\user\.owf-gp\log\gp_user.log`.

The [`StartLog`](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/command-ref/StartLog/StartLog)
command restarts the log file using a specified file.
For example, a log file in the same folder as the command file is typically used
to record processing progress.

The [`geoprocessor.util.log_util`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/util/log_util.py)
module contains functions that start the initial log file and reset.
The logging handler is setup with name `geoprocessor` so as to be in effect for all subpackages.

### Log Messages ###

GeoProcessor code modules call Python logging functions using standard Python conventions,
for example:

```python
        logger = logging.getLogger(__name__)

        logger.debug(...)
        logger.info(...)
        logger.warning(...)
        logger.error(...)
        logger.critical(...)
```

The formatter for log messages provides useful data for troubleshooting.

Care should be taken to minimize logging once initial development is complete
so that the log file size is kept as small as possible.

### Logger Exception Handling ###

Python exception handling can be painful given transition of the language in implementing
specific exception classes, and lack of exceptions that might be expected, such as FileNotFoundException.
Python 3 provides more exception classes.
The following illustrates how to catch exceptions and log the trace stack to the log file
(note the use of `exc_info=True`):

```python
try:
    # Some code here...
except Exception as e:
    warning_count += 1
    message = 'Unexpected error writing file "' + pv_OutputFile_absolute + '"'
    logger.error(message, exc_info=True)
    self.command_status.add_to_log(
        command_phase_type.RUN,
        CommandLogRecord(command_status_type.FAILURE, message,
                         "See the log file for details."))
```

PyCharm will complain that generic Exception is being caught but this is the only way to
ensure catching all exceptions as a fall-through.
More specific exceptions can also be caught and handled.

## GeoLayer Class ##

The [`geoprocessor.core.GeoLayer`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/core/GeoLayer.py)
class is used to store spatial data layers.
Design elements of the class include:

* `id` (GeoLayerID) provide a unique identifier for the layer, used by commands to retrieve layers from the GeoProcessor for processing
* `qgs_vector_layer` - QGISVectorLayer instance
* `source_path` - path to file on operating system, if file is read (not used for in-memory layers)
* `qgs_id` - QGIS layer identifier
* `properties` - dictionary of properties, similar to GeoProcessor properties, but for the specific layer, used to transfer data and control processing logic

## gp Application ##

The
[`geoprocessor.app.gp`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/app/gp.py)
module contains a main program to run the GeoProcessor in multiple modes:

* batch mode via `--commands command-file.gp` command parameters
* interactive command shell, when no command parameters are given
* user interface mode (to be developed)
* http server (future feature to support web service functionality)

This module is expected to be enhanced over time and serve as the primary tool for running the GeoProcessor.
The Python module is run using one of the following command-line scripts:

* [gp.bat](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gp.bat) - Windows batch file
* [gp.sh](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/scripts/gp.sh) - Linux shell script

## User Interface ##

The user interface (UI) for the GeoProcessor allows users to edit and run command workflows.
The UI is run from the `run_ui` function in the `geoprocessor/app/gp` module.
See the [UI Design](../ui-design/ui-design.md) section.

## User Interface (Old) ##

**This is the old documentation.**

The user interface (UI) for the GeoProcessor allows users to edit and run command workflows.
The UI is run from the `run_ui` function in the `geoprocessor/app/gp` module.
See the [UI Design](../ui-design-old/ui-design-old.md) section.

## Built-in Test Framework ##

The GeoProcessor provides a built-in test framework similar to TSTool,
which facilitates implementing functional tests.
The benefit of this approach is that tests validate the software using test cases
comparable to those of users and tests can be added in the operational environment.
Developers and users can therefore add tests.

The separate repository [owf-app-geoprocessor-python-test](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test)
is used to maintain functional tests.
This allows persons other than software developers to create tests.

GeoProcessor software developers should clone the above repository parallel to the GeoProcessor code repository.
Tests can be added with a test editor (and in the future the user interface).
The tests can then be run one at a time with a script, similar to:

* [run-tests-steve.bat](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/blob/master/test/suites/run/run-tests-steve.bat)

Tests can also be run run by creating a test suite, similar to TSTool (see [Development Tasks / Testing](../dev-tasks/testing.md)).

Dynamic test files should not be committed to the repository.

Tests should be created by following the standards documented in the test repository main
[README](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test) file
and [Development Tasks / Testing](../dev-tasks/testing.md).

## Future Design Elements ##

The following are design elements that are envisioned for future implementation:

* Implement discovery run mode similar to TSTool to allow commands to be partially
run when loaded in to the user interface.
This allows information such as GeoLayer identifiers in earlier commands to be
provided in editors for later commands, to streamline command parameter
selection and provide improved user experience.
* Add a variety of useful commands comparable to TSTool.
* Add fully-functional table data objects to facilitate data manipulation.
* Implement unit tests via `pytest` to test at the function level.
* Implement functional tests for all commands.
