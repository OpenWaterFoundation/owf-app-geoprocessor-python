# GeoProcessor / Development Tasks / Adding a New Command #

Adding a new command is one of the common development activities.
The following explains how to add a new built-in command,
meaning that the code is "hard-linked" by reference.
In the future plugin commands will be implemented that can be developed in files parallel to the `geoprocessor` files.
The order of the following steps can vary depending on activities and development approach.
For example, adding a repository issue could occur first.

* [Confirm that a Command does not Already Exist and Draft Requirements](#confirm-that-a-command-does-not-already-exist-and-draft-requirements)
* [Select a Command Name](#select-a-command-name)
* [Add a Repository Issue](#add-a-repository-issue)
* [Create a Branch for Development](#create-a-branch-for-development)
* [Modify Code](#modify-code)
	+ [Add Command Class](#add-command-class)
	+ [Add to Command Factory](#add-to-command-factory)
	+ [Add to GeoProcessorUI](#add-to-geoprocessorui)
	+ [Add Code to Other Modules](#add-code-to-other-modules)
* [Define Tests](#define-tests)
* [Add Documentation](#add-documentation)

------------------

## Confirm that a Command does not Already Exist and Draft Requirements ##

The functionality of an envisioned new command may already be present in an existing command,
or could be added to an existing command by adding parameters to that command.
A balance should be struck between keeping existing commands focused on a specific function...
but not adding so many simple commands that the software becomes overwhelmed with a large number of commands.

If an existing command does exist that can be modified, a recommendation can be made to update its functionality,
for example by editing the command documentation to highlight the new functionality.

If no existing command exists, then the functionality of the new command should be described in enough detail
to explain functional requirements. Copying and modifying the documentation for a similar command is one
way to define functionality for developers.

In any case, any changes that are recommended will be coordinated by the development team.

## Select a Command Name ##

Command names in the GeoProcessor follow a number of conventions and new commands should adhere to these conventions:

1. Commands fall into broad functional type, such as reading, manipulating, and writing data.
Command names should include important words like `Read`.
2. Commands should perform one singular task.
Commands can be combined with other commands in a command file.
Therefore, the command name should include an clear action, subject of the action, and modifiers.
For example Action=Read, subject=GeoLayer, modifier=FromXxxx would give a command `ReadGeoLayerFromXxxx`.
3. Use mixed case to make it easier to read words together without spaces.
4. Be careful with plural.  This can be a point of negotiation depending on whether it makes sense for
a command to operate on multiple output objects such as GeoLayers.

## Add a Repository Issue ##

A repository issue can be added once there is enough information to describe the new command.
The draft requirements can be defined in the issue text, or attach a document.

The repository issue can be used to track progress on new development.

## Create a Branch for Development ##

The development of a new command should occur in a repository using normal protocols.
For example, name the branch with the issue number and new command name, for example `10-eadgeolayerfromxxx`.
Use of `10-feature...` or similar is OK but can lead to long branch names.

## Modify Code ##

The command is added by modifying several code files described below.

### Add Command Class ###

A command class should be added similar to other commands.
Decide on the folder where the command should exist in `geoprocessor/commands` and copy an existing similar command.
Then update the command accordingly:

1. Make sure the command name and other metadata in the file are accurate.
2. Update the `check_command_parameters` function to perform appropriate validation on input.
3. Update the `run_command` function to implement the required functionality.
Refer to the [Software Design](../software-design/software-design.md) documentation for guidelines.

### Add to Command Factory ###

In order for the GeoProcessor to recognize the command as a built-in command, update the
`geoprocessor/core/GeoProcessorCommandFactory.py` code to add the command, similar to other commands.

1. The `registered_commands` data is not currently used but may be used in the future to facilitate dynamic loading of
commands, including plugin commands.  Therefore, add the new command to the dictionary.
2. Update the `new_command` function to add the command.
Make sure the commands are alphabetized unless this would cause ambiguity due to a shorter command name
always being matched and ignoring a longer name.

### Add to GeoProcessorUI ###

The command must be added to the `geoprocessor/ui/app/GeoProcessorUI` class in order to show the
user a menu for a new command:

1. Determine where the command should be inserted in UI menus by running the GeoProcessor and
examining existing menus.
2. Edit the `GeoProcessorUI` class and search for the nearest command determined above.
Add code similar to other code.
3. If necessary, add a new menu for the command.

In the future commands may be added to menus based on data in the command class.

### Add Code to Other Modules ###

The computational code for some commands is contained entirely within the command,
in which case the `run_command` function should be updated with the necessary logic.
If necessary, add additional functions in the command class, such as private, class-level, and static functions.

Some commands rely on code that is shared and therefore computational code
should be placed in a file (module) different from the command class file.
For example, QGIS-related computational code is often placed in the `geoprocessor/util/qgis_util.py` file.
This allows such code to be isolated from other code and simplifies stripping the code out for the `gptest` variation of the GeoProcessor.
If necessary, additional QGIS code files can be added,
for example to separate vector and raster operations and to keep the files from becoming too long.

Conversion of the computational code to the ArcGIS Pro version of the GeoProcessor can then mainly focus on converting `qgis_util.py` from
QGIS (PyQGIS) to ArcGIS Pro (ArcPy) library calls.

Code can also be added to other utility modules and classes as necessary.

## Define Tests ##

The `owf-app-geoprocessor-python-test` repository contains automated functional tests.
New commands should be tested by implementing tests similar to other commands.

* See the [README](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test)
* See the [Development Tasks / Testing](testing.md) documentation.

Unit tests using `punit` can also be defined, for example to test stand-alone functions.
Where unit tests are difficult to code, use the functional tests.

## Add Documentation ##

Documentation for the new command should be added to the `owf-app-geoprocessor-python-doc-user` repository.

* See the [README](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-doc-user)
* See the [Development Tasks / Documenting](documenting.md) documentation.
