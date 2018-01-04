# Learn GeoProcessor (Dev) / Software Design #

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
* [Graphical User Interface](#graphical-user-interface) - interactive interface
* [Built-in Test Framework](#built-in-test-framework) - used to run functional tests
* [Future Design Elements](#future-design-elements) - as-yet implemented features

----------------------

## GeoProcessor Design Background ##

This GeoProcessor software leverages the Python geoprocessing libraries from QGIS
while implementing the command/workflow feature
design developed in the [TSTool time series processing software](http://openwaterfoundation.org/software-tools/tstool).
Many lessons were learned developing TSTool that have been applied to the GeoProcessor.

The GeoProcessor currently is written for Python 2 because QGIS libraries use Python 2.
The GeoProcessor will be updated to use Python 3 once the QGIS Python 3 version is proven out.

TSTool is written in Java and is being moved to an open source project (not there yet, as of Jan 2018).
Java is object-oriented and the time series processor design is modular.
Although Python provides object-oriented features via classes,
there are differences between Java and Python, in particular:

* Java does not support multiple inheritance and Python does.
* Java supports interfaces and Python does not (natively).
* Java provides enumerations and Python 2 does not (Python 3 does).
* Java provides private and public levels whereas Python relies more on convention,
such as using `__` prefix on data and functions to indicate private data.

Consequently, the TSTool design has been adapted from Java to Python.
In many cases, the Java code has been simplified in order to streamline GeoProcessor development
and to evaluate options.  For example, simplifications include:

* Specific exceptions in Java code have been simplified to use built-in `ValueError` and `RuntimeError` in Python.
* Java class setter/getter methods have been omitted in favor of python direct-access to data.
Class constructors with instance data are used to create object instances.

The following sections describe specific components by explaining GeoProcessor classes.
Links to code on the master branch of the repository are provided.
Right-click on the link and view in a separate window to facilitate review
of the documentation and code at the same time.

## Command File and Command Syntax ##

The GeoProcessor performs its work by interpreting a workflow of commands.
A command file is text file containing lines with one command per line, for example:

```text
Need a good example.
```

The command file lines include:

* One-line comments starting with `#` character.
* Blank lines.
* Control commands including `For` and `If`.
* Commands that follow syntax:

```text
CommandName(Parameter1="Value1",Parameter2="Value2",...)
```

Conventions for commands and command files are described in the GeoProcessor user documentation.

## QGIS Environment ##

The GeoProcessor relies on the QGIS environment and Python libraries.
In particular, the following are used:

* QGIS runtime environment, as initialized before running applications such as the [gp application](#gp-application) (discussed below).
* QGIS processor modules, as initialized in the [GeoProcessor class](#geoprocessor-class) (discussed below).
* QGIS Python processing modules, as used in [Command classes](#abstractcommand-class-and-command-classes) (discussed below).
* QGIS user interface features, as used in the [Graphical User Interface](#graphical-user-interface) (discussed below).

In order to use the QGIS environment, the GeoProcessor runs the Python software distributed with QGIS,
with `PYTHONPATH` configured to find QGIS Python modules as well as GeoProcessor modules.
**The following configuration scripts have been created for initial prototyping and will
be made more robust for general use.**

* Configuration in the developer environment is accomplished by running a setup script,
for example [run-pycharm2017.3.1-for-qgis.bat](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/build-util/run-pycharm2017.3.1-for-qgis.bat).
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
This script will be replaced by an auto-generated command file that runs `RunCommand` commands, similar to TSTool,
 when the test framework is fully developed.

## GeoProcessor Class ##

The
[`GeoProcessor`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/core/GeoProcessor.py)
class forms the core of the GeoProcessor package.
The GeoProcessor provides the following design elements and functionality:

* An instance is created to maintain a list of commands and run the commands.
* Data members:
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
This occurs through a simple mapping exercise to identify the proper command and then calling the
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
* Data members:
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
	which provides information that allows checking for valid parameter names and types.
	+ `command_status` is an instance of `CommandStatus`, which maintains a list of `CommandLogRecord`,
	used to track issues in initializing and running commands (see discussion below).
* Functions: 
	+ `check_command_parameters` - is expected to be defined in child command class to validate
	command parameter values during command initialization
	+ `get_parameter_metadata` - is a utility function to return the metadata for a parameter name
	+ `get_parameter_value` - is a utility function to return a parameter string value from the parameter dictionary,
	gracefully handles missing parameters (which is OK because default values will be used at runtime)
	+ `initialize_command` - utility function that is called to
		- sets the GeoProcessor instance
		- sets the command string
		- optionally parses the command string into parameter string dictionary
	+ `parse_command` - utility function to parse the command string into parameter string dictionary
	+ `run_command` - is expected to be defined in child command class to run the command
	+ `to_string` - utility function to convert the internal parameter string dictionary
	into the single-line command string

The `AbstractCommand` class is the parent class from which all other commands are derived.
Specific commands are organized in groups under the `geoprocessor.commands` package,
for example, the `geoprocessor.commands.running` package contains commands that are associated with
controlling running commands.  Examples of commands are:

* [`SetProperty`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/commands/running/SetProperty.py)
* Need to add more commands that illustrate different code patterns

Command class design considerations include:

* One class is stored per source file and the name of the file matches the class name
* Instances are created for each line in a command file
	+ [`UnknownCommand`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/commands/util/UnknownCommand.py)
	is used when the command name is not recognized by the `GeoProcessorCommandFactory`
	+ [`BlankCommand`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/commands/util/BlankCommand.py)
	is used as a place-holder for blank lines
	+ [`CommentCommand`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/commands/util/CommentCommand.py)
	is used for `#` comments
* Data
	+ Private data values should be defined as needed; however, in most cases data local to functions may be adequate
	because the GeoProcessor instance maintains primate data like the list of GeoLayers
	+ `command_name` from `AbstractCommand` is set to the command name
	+ `command_parameter_metadata` from `AbstractCommand` is set to the command parameter metadata 
* Functions
	+ `check_command_parameters` - checks command parameter values for valid values
		- required parameters must be defined
		- parameter string values are checked for validity using `geoprocessor.util.validators` module functions.
		- adds `CommandStatus` messages for `command_phase_type.INITIALIZATION` run phase
	+ `run_command` - executes the functionality of the command
		- file/folder parameters are converted to absolute paths using the processor `WorkingDir` property
		using `geoprocessor.util.io.to_absolute_path` function
		- parameters containing `${Property}` notation are expanded to full values prior to use using the
		GeoProcessor `expand_parameter_value` function.
		- converts string parameter dictionary values into object types needed for run-time, raising `ValueError` if any issues
		- performs the processing
		- saves results back to the GeoProcessor if appropriate
		- raises `RuntimeError` if an error
		- adds `CommandStatus` messages for `command_phase_type.RUN` run phase

## CommandStatus Class ##

The
[`AbstractCommand`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/commands/abstract/AbstractCommand.py)
class includes the `command_status` data object, which is an instance of
[`CommandStatus`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/commands/core/CommandStatus.py).
This object maintains a list of 
[`CommandStatus`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/commands/core/CommandLogRecord.py),
which allows tracking issues with command initialization and running.

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

* `command` - command parsing, etc.
* `geo` - geoprocessing
* `io` - input/output
* `log` - log file handling
* `validators` - validators for command parameters

These modules and additional utility modules will be enhanced over time.

## Logging ##

The GeoProcessor modules uses standard Python `logging` module features
in order to support troubleshooting.
However, the log file is not simple for users to interpret and the final software user interface
will provide features to view command status using the `CommandStatus` data.

### Log File ###

The `geoprocessor.app.gp` module contains a main program to run the GeoProcessor.
This program starts an initial log file at `INFO` level in the user's home folder,
for example on Windows `C:\Users\user\.owf-gp\log\gp_user.log`.

The `StartLog` command restarts the log file using a specified file.
For example, a log file in the same folder as the command file is typically used
to record processing progress.

The [`geoprocessor.util.log`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/util/log.py)
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

## GeoLayer Class ##

The `GeoLayer` class is used to store spatial data layers.
Design elements of the class include:

* Identifier...
* GQIS layer...
* **Emma complete this.**

## gp Application ##

The
[`gp`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/geoprocessor/app/gp.py)
module contains a main program to run the GeoProcessor in multiple modes:

* batch mode via `--commands command-file.gp` command parameters
* interactive command shell, when no command parameters are given
* user interface mode (to be developed)
* http server (future feature to support web service functionality)

This module is expected to be enhanced over time and serve as the primary tool for running the GeoProcessor.

## Graphical User Interface ##

The graphical user interface for the GeoProcessor has not yet been developed.
Ideally the interface will be similar to TSTool but with features to view spatial data.

## Built-in Test Framework ##

The GeoProcessor provides a built-in test framework similar to TSTool,
which facilitates implementing functional tests.
The benefit of this approach is that tests validate the software using test cases
comparable to those of users and tests can be added in the operational environment.
Developers and users can therefore add tests.

A [separate repository (owf-app-geoprocessor-python-test)](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test)
is used to maintain functional tests.
This allows non-developers to create tests.

GeoProcessor software developers should clone the above repository parallel to the GeoProcessor code repository.
Tests can be added with a test editor (and in the future the user interface).
The tests can then be run with a script, similar to:

* [run-tests-steve.bat](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test/blob/master/test/suites/run/run-tests-steve.bat)

The test framework will be improved over time to implement features similar to TSTool.
Dynamic test files should not be committed to the repository.

Tests should be created by following the standards documented in the test repository README files.

## Future Design Elements ##

The following are design elements that are envisioned for future implementation:

* Graphical user interface with command editors.
* Implement discovery run mode similar to TSTool to allow commands to be partially
run when loaded in to the user interface.
This allows information such as GeoLayer identifiers in earlier commands to be
provided in editors for later commands, to streamline command parameter
selection and provide improved user experience.
* Add useful commands comparable to TSTool, such as `WebGet`.
* Add table data objects to facilitate data manipulation.
* Implement unit tests via `pytest`.
