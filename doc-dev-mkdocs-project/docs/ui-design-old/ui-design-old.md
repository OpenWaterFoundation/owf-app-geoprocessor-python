# GeoProcessor / User Interface (UI) Design #

**This is the old documentation - keep it for reference until the UI Design documentation is updated.**

- [Overview](#overview)
- [User Interface Terms](#user-interface-terms)
- [Folder Structure](#folder-structure)
- [The Main Window](#the-main-window)
- [The AbstractDialog class](#the-abstractcommand_editor-class)
- [The CommandDialog class](#creating-a-command-dialog-window)
- [List of Completed Command Dialog Windows](#list-of-commands-with-command-dialog-windows)
- [Resources](#resources)

------------------

## Overview

This documentation explains the current user interface design. 
The design is still in implementation phase and can be redesigned in the future if needed. 
The GeoProcessor user interface is functional but is limited.
It has the following functionality: 

- Open a command file to view in the user interface
- Save a command file from the user interface to a new output file (`Save Command File...`)
- Save a command file from the user interface to an existing file (`Save Command File As...`) 
- Add a new `ReadGeoLayerFromGeoJSON` command via a pop-up window dialog
- Edit an existing `ReadGeoLayerFromGeoJSON` command via a pop-up window dialog 
- Check that all required command parameters are specified by the user before the command is added to the `command list` ui component
- Clear a single command from the `command list` ui component (a right-click `Delete Command` action)
- Clear the selected commands from the `command list` ui component
- Clear all commands from the `command list` ui component
- Select one or more commands in the `command list` ui component
- Run the selected commands from the `command list` ui component
- Run all commands from the `command list` ui component

As mentioned above, 
the only command that is fully functional within the GeoProcessor user interface is `ReadGeoLayerFromGeoJSON`. 
However, the infrastructure to build `command dialog` windows for the other GeoProcessor commands has already 
been constructed and can be used to quickly construct the UI functionality for the other commands. 
This documentation explains the UI software infrastructure in detail and can be followed to construct the 
remaining commands within the user interface. 

Although the other commands are not fully functional within the user interface, 
those commands can still be run within the user interface.  
`"fully functional within the user interface"` only means that there is not yet a `command dialog` window created for that command. 
The reading of a command file and the running of that command file is performed within the GeoProcessor `/core` code. 
To run a command file within the UI, follow the instructions below:

1. Start the GeoProcessor user interface.
2. Click ***File / Open Command File***.
3. Browse to and select the command file of interest. 
4. The command file will appear in the `command list` ui component. 
Each line of the command file is a unique line in the `command list` ui component
5. Click the ***Run Commands*** button. 
This will read the text within the `command list` ui component and 
will pass that string to the GeoProcessor `core` code to be parsed, read and run. 
The GeoProcessor runs with a single string input. 
All parsing and running of the command occurs within the `core` code. 

The entire user interface is built within 3 main sections. 

1. [The GeoProcessor Main Application Window class](#the-main-window)
	- creates the main window user interface
	- controls the actions that take place on the main window
2. [The AbstractDialog class](#the-abstractcommand_editor-class)
	- parent class to all CommandDialog classes 
	- creates the features of the `command dialog` windows that are consistent across all `command dialog` windows 
	- controls the actions that take place consistently across all `command dialog` windows 
3. [The CommandDialog classes](#creating-a-command-dialog-window)
	- child class to the AbstractDialog class
	- one class for each GeoProcessor command
	- creates the features of the `command dialog` windows that are unique to the command
	- controls the actions that take place uniquely in the `command dialog` window of the command 
	
These main UI sections are explained in detail below. 

## User Interface Terms

|Term|Definition|Image|
|-|-|-|
|Main Window|The GeoProcessor's home window. All functionality within the GeoProcessor user interface can be accessed via this window. The `main` window is the first window to appear when the GeoProcessor is started in *ui* mode.|<a href = "images/main_window.png">![Main Window](main_window.png)</a>|
|Command Editor Window|The user interface window that allows the user to create a new command or edit an existing command. There is one `command editor` window for each GeoProcessor command. The command editor window has input fields used to enter the values for the command parameters.| <a href = "images/command_dialog_window.png">![Command Dialog Window](command_dialog_window.png)</a>|
|Command List UI Component|A subset of the GeoProcessor main window that holds the commands of the command file. There is one line within the `command list` ui component for each command of the command file.|<a href = "images/command_list_ui_component.png">![Command List UI Component](command_list_ui_component.png)</a>|

## Folder Structure

```
ui/										Contains all files relating to the UI. 
	app/								Contains all files relating to the UI main window.
    	GeoProcessorUI.py				Controls the signals/slots of the UI main window. 
        GeoProcessorUI_Design.py		Controls the window design of the UI main window. 
	commands/							Contains all files relating to the GeoProcessor commands. 
    	abstract/						Contains all files relating to the abstract command. 
			AbstractCommand_Editor.py	Controls the design and the signals/slots shared among the UI command dialog windows.
    	datastores/						Contains all files relating to the command dialog windows of the DataStore commands. 
        layers/							Contains all files relating to the command dialog windows of the GeoLayers commands.
        logging/						Contains all files relating to the command dialog windows of the logging commands.
        running/						Contains all files relating to the command dialog windows of the running commands.
        tables/							Contains all files relating to the command dialog windows of the Tables commands.
        testing/						Contains all files relating to the command dialog windows of the testing commands.
        util/							Contains all files relating to the command dialog windows of the utility commands.
    util/								Contains all UI utility files. 
        command_parameter.py			Class that holds UI information for each command parameter. 
        config.py						Class that holds global variables that change infrequently. 
```

Each GeoProcessor command should have its own `command dialog` window. 
In initial development, only a select number of the commands have a `command dialog` window.
See the [List of Commands with Command Dialog Windows](#list-of-commands-with-command-dialog-windows) 
for information about which commands already have a `command dialog` window and which commands need ui development. 
Future development must take place to create `command dialog` windows for the remaining GeoProcessor commands. 
The [List of Commands with Command Dialog Windows](#list-of-commands-with-command-dialog-windows) 
list should be updated as future development occurs. 
Once all current GeoProcessor commands have `command dialog` windows, the creation of new commands should include a ui component. 
For example, the workflow of creating commands should follow these steps:

1. Create a functional command in the core GeoProcessor code.
2. Create tests for the command.
3. Create documentation for the command.
4. Review the command with the GeoProcessor review team (Steve Malers).
5. Edit the code, tests and documentation to address concerns in the review.
6. Create a UI `command dialog` window for the command. 

## The Main Window

The code for the GeoProcessor main window user interface is held within the `ui/app` folder.
There are two scripts that make up the entire main window user interface. 


The first is the `GeoProcessorUI_Design.py` script.
This script is responsible for the main window design and structure. 
For example, if the developer wanted to add another button to the main window, 
the creation of that button would take place in the `GeoProcessorUI_Design.py` script.
Changing the size, text or any other design features for a main window object would also be completed in this script. 

The second is the `GeoProcessorUI.py` script.
This script is responsible for all of the actions and listeners that occur in the main window user interface.
This script also holds global variables that describes the current state of the GeoProcessor instance
(the number of commands in the [Command List UI Component](images/command_list_ui_component.png), the number of selected commands, etc.).
Lastly, this script interacts with the GeoProcessor object to run the commands and read the results of a processed command file. 
Any actions that take place in the main window should be configured in this script. 
For example, there is a function within the `GeoProcessorUI` class that clears all of the commands in the 
[Command List UI Component](images/command_list_ui_component.png) when the `Clear Commands` button is clicked.

## The AbstractCommand_Editor Class

The `abstract command` class is the parent class to all GeoProcessor `command_dialog` window classes. 
It holds configurations consistent among *all* GeoProcessor `command_dialog` windows. 

### Imports 

|Import Statement&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|Description|
|-|-|
|`from`<br>`PyQt5`<br>`import`<br>`QtCore`|The user interface is built on the [PyQt5](http://pyqt.sourceforge.net/Docs/PyQt5/introduction.html) library. QtCore contain functions to set the size and alignment of QtWidgets.|
|`from`<br>`PyQt5`<br>`import`<br>`QtWidgets`|The user interface is built on the [PyQt5](http://pyqt.sourceforge.net/Docs/PyQt5/introduction.html) library. QtWidgets are the building blocks for each of the items on the `command dialog` window.|
|`import`<br>`geoprocessor.ui.util.config`<br>`as`<br>`config`|The online user documentation URL reference is held as a static variable in the `config.py` script. Each `command dialog` window has a `View Documentation` button that links to the online command documentation.|
|`import`<br>`functools`|See [Python Documentation - `functools.partial`](https://docs.python.org/2/library/functools.html#functools.partial). Used to connect the QtToolButton with the action of opening a file browser.|
|`import`<br>`webbrowser`|["Provides a high-level interface to allow displaying Web-based documents to users."](https://docs.python.org/2/library/webbrowser.html). Used to open the GeoProcessor user documentation.|

### PyQt5 Predefined Translation Code

It is not known why this block of code is important. 
See the [`Command Dialog` PyQt5 Predefined Translation Code](#2-add-pyqt5-predefined-translation-code) section.

![PyQt5 Predefined Translation Code](images/pyqt5-translation.png)

### Initialization

The `UI_AbstractDialog`	class has no class variables but has many instance variables. 

|Instance variable<br>( prefaced with `self.` )|Description|Value|
|-|-|-|
|command_name|The name of the GeoProcessor command represented by the Dialog window.|`self.command_name = command_name`|
|command_description|The description of the GeoProcessor command represented by the Dialog window.|`self.command_description=command_description`|
|user_doc_url|The path to the online GeoProcessor user documentation.|`self.user_doc_url=config.user_doc_url`|
|parameter_count|The number of command parameters of the GeoProcessor command represented by the Dialog window.|`self.parameter_count=parameter_count`|
|parameters_list|A list of strings representing the command parameter names (in order) of the GeoProcessor command represented by the Dialog window.|`self.parameters_list=command_parameters`|
|input_edit_objects|A dictionary that relates each command parameter with its associated Qt Widget input field. <br><br> Key: the command parameter name <br> Value: the associated Qt Widget input field object<br><br>The dictionary is initialized as an empty dictionary. Entries are added by running the class functions.|`self.input_edit_objects={}`|
|command_parameter_current_values|A dictionary that contains the command parameters and their current values. <br><br> Key: the name of the command parameter<br>Value: the entered value of the command parameter|`self.command_parameter_current_values=current_values`|

### Configure QtWidget Functions

The `command dialog` windows are built by adding [Qt Widget objects](http://doc.qt.io/qt-5/gallery.html) 
to the `command dialog` window [QDialog](http://doc.qt.io/qt-5/qdialog.html#details) object. 
The QtWidget objects make up the command parameter labels and the command parameter input fields of the `command dialog` window. 
After a QtWidget object is created (initialized), it must be configured. 
Configuration varies depending on the type of QtWidget but can include the following:

- setting the text alignment in labels
- setting the object name
- setting the location of the object on the `command dialog` window
- setting the text 
- setting the tooltip
- and more ... 

To provide consistency among all of the GeoProcessor `command dialog` windows, 
the configurations for each QtWidget object is held within AbstractCommand_Editor functions. 
This ensures that the `command dialog` windows are designed similarly. 

Each QtWidget configuration function follows the naming convention `configure[Qt Widget Type (CamelCase)]`.
As new QtWidgets are added to the GeoProcessor, 
corresponding configuration functions must be created in the `AbstractCommand_Editor` class to configure those new QtWidgets.
Below is a table showing which QtWidgets already have a configuration function.
This table should be updated as new configuration functions are created.

|[QtWidgets](http://doc.qt.io/qt-5/qobject.html) with <br>Configuration Functions|Function Name|Configuration Settings|
|-|-|-|
|[QLabel](http://doc.qt.io/qt-5/qlabel.html#details) for command name|`configureLabel`|- [object name](http://doc.qt.io/qt-5/qobject.html#objectName-prop)<br>- [widget location](#automation-of-widget-location)<br>- [text](http://doc.qt.io/qt-5/qlabel.html#text-prop)<br>- [text alignment](http://doc.qt.io/qt-5/qlabel.html#alignment-prop)|
|[QLabel](http://doc.qt.io/qt-5/qlabel.html#details) for command description|`configureDescriptionLabel`|- [object name](http://doc.qt.io/qt-5/qobject.html#objectName-prop)<br>- [widget location](#automation-of-widget-location)<br>- [text](http://doc.qt.io/qt-5/qlabel.html#text-prop)|
|[QLineEdit](http://doc.qt.io/qt-5/qlineedit.html#details)|`configureLineEdit`|- [object name](http://doc.qt.io/qt-5/qobject.html#objectName-prop)<br>- [widget location](#automation-of-widget-location)<br>- [placeholder text](http://doc.qt.io/qt-5/qlineedit.html#placeholderText-prop)<br>- [tooltip](http://doc.qt.io/qt-5/qwidget.html#toolTip-prop)<br>- signal/slot with [Command Display](#update_command_display)<br>- add to list of [input_edit_objects](#initialization)|
|[QToolButton](http://doc.qt.io/qt-5/qtoolbutton.html#details)|`configureToolButton`|- [object name](http://doc.qt.io/qt-5/qobject.html#objectName-prop)<br>- [widget location](#automation-of-widget-location)<br>- text<br>- signal/slot with QLineEdit object|
|[QComboBox](http://doc.qt.io/qt-5/qcombobox.html#details)|`configureComboBox`|- [object name](http://doc.qt.io/qt-5/qobject.html#objectName-prop)<br>- [widget location](#automation-of-widget-location)<br>- add choices to box<br>- [tooltip](http://doc.qt.io/qt-5/qwidget.html#toolTip-prop)<br>- signal/slot with [Command Display](#update_command_display)<br>- add to list of [input_edit_objects](#initialization)|

#### Automation of Widget Location

Each QtWidget configuration function has an `parameter_name` argument. 
The `parameter name` argument is the name of the command parameter that the QtWidget is associated with. 
The row to which the widget is added to the `command dialog` window is calculated dynamically 
by determining the order of the associated command parameter with the other command parameters. 
The row will always be the index of the associated command parameter within the full list of parameters plus 2. 
The command description and view documentation button of the `command dialog` window takes up the first two rows of the window. 

### Other Shared Functions

#### `setupUi_Abstract()` 

The `setupUi_Abstract()` is triggered any time a new `command dialog` window is created. 
The `command dialog` window reads in a [QDialog](http://doc.qt.io/qt-5/qdialog.html#details) object to create the window object. 
All components of the `command dialog` window (*input fields*, *labels*, *grid layouts*, *etc.*) 
are added to the [QDialog](http://doc.qt.io/qt-5/qdialog.html#details) object

This function will: 

- set the name of the [QDialog](http://doc.qt.io/qt-5/qdialog.html#details) object to *Dialog*
- set the initial size of the QDialog object to 684 pixels x 404 pixels
- set the title of the QDialog object to the command name
- set the layout of the QDialog object to a [QGridLayout](http://doc.qt.io/qt-5/qgridlayout.html#details)
- add a [QFrame](http://doc.qt.io/qt-5/qframe.html#details) object to the QDialog object to 
hold the command description and `View Documentation` button
- set the layout of the QFrame object to a [QGridLayout](http://doc.qt.io/qt-5/qgridlayout.html#details) 
- add a [QSpacerItem](http://doc.qt.io/qt-5/qspaceritem.html#details) object to the QFrame 
object to separate the command description from the `View Documentation` button
- add a [QPushButton](http://doc.qt.io/qt-5/qpushbutton.html#details) object to the QFrame 
object to allow the users to connect to the online command documentation
- add a [QLabel](http://doc.qt.io/qt-5/qlabel.html) object to the QFrame object to display
 the command description
- set the QLabel text to the command description
- add a second [QFrame](http://doc.qt.io/qt-5/qframe.html#details) object to add a separator 
line between the command description frame and the input parameters frame
- add a [QTextEdit](http://doc.qt.io/qt-5/qtextedit.html#details) object to the QDialog 
object to dynamically display the command text as the input parameters are entered
- add a [QLabel](http://doc.qt.io/qt-5/qlabel.html) object to the QDialog object to label 
the QTextEdit field as the Command Display Text Browser
- set the QLabel text to `Command:`
- add a [QSpacerItem](http://doc.qt.io/qt-5/qspaceritem.html#details) object to the QDialog 
object to separate the input parameter fields from the QTextEdit object (the Command Display Text Browser) 
- add a [QDialogButtonBox](http://doc.qt.io/qt-5/qdialogbuttonbox.html#details) to the QDialog object 
to allow the users to accept or reject the input parameters and the addition of the command 
to the command list 
- [auto-connect the slots and signals](http://joat-programmer.blogspot.com/2012/02/pyqt-signal-and-slots-to-capture-events.html)
- [set the location](http://doc.qt.io/qt-5/qtextedit.html#details) of all the added Qt objects

#### `update_command_display()` 

The `update_command_display()` is triggered any time one of the input fields of 
the `command dialog` window is edited. 
Each `command dialog` window has a command display that shows the 
string representation of the command with the user-specified input parameters.
This function updates the text within the command display to dynamically 
display the changes in the command parameter values. 
This dynamic creation of the row allows for the command parameter QtWidgets 
to automatically display in the order that the command parameters are listed in the core command python script. 
The columns and stretch of the QtWidget are set values depending on the type 
of QtWidget that is being configured. 
For example, all command parameter name labels are in the first column of the 
`command dialog` window and only span 1 column and 1 row. 

#### `view_documentation()` 

The `view_documentation()` function is triggered when the `View Documentation` 
button is clicked from the `command dialog` window. 
The function opens the command's user documentation in the user's default browser. 
This assumes that the user has Internet access. 

#### `select_file()` 

The `select_file(qt_widget)` function is triggered when a 
[QToolButton](http://doc.qt.io/qt-5/qtoolbutton.html#details) widget is clicked next to a 
[QLineEdit](http://doc.qt.io/qt-5/qlineedit.html#details) widget of a command parameter that requires a local file path. 
The function opens a file browser window to allow a user to select a file through a Qt predefined user interface. 
The path of the selected file is entered in the provided `qt_widget`
(as of present, the only [Qt Widgets](http://doc.qt.io/qt-5/qtwidgets-module.html) that receive text from the 
`select_file()` function is a [QLineEdit](http://doc.qt.io/qt-5/qlineedit.html#details) widget). 

#### `are_required_parameters_selected()` 

The `are_required_parameters_selected()` function is triggered when the `OK` button is clicked on a `command dialog` window. 
This function checks that all of the required command parameters have entered input values. 

## Creating a `Command Dialog` Window

To develop a `command dialog` window  with the single-tab design, use the `ReadGeoLayerFromGeoJSON_Editor.py` script as a template. 

### 1. Import required modules

|Import Statement&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|Description|
|-|-|
|`from`<br>`PyQt5`<br>`import`<br>`QtWidgets`|The user interface is built on the [PyQt5](http://pyqt.sourceforge.net/Docs/PyQt5/introduction.html) library. QtWidgets are the building blocks for each of the items on the `command dialog` window.|
|`from`<br>`geoprocessor.commands.[python package].[command]`<br>`import`<br>`[command class]`|The user interface obtains information from the command's core code. |
|`from`<br>`geoprocessor.ui.commands.abstract.AbstractCommand_Editor`<br>`import`<br>`UI_AbstractDialog`|The *UI_AbstractDialog* class holds variables and functions that are consistent across all `command dialog` windows.|
|`from`<br>`geoprocessor.ui.util.command_parameter`<br>`import`<br>`Command_Parameter`|The *Command_Parameter* class is used as a building block to hold information about each of the command's parameters (specific to the user interface).|
|`from`<br>`geoprocessor.core`<br>`import`<br>`CommandParameterMetadata`|The *CommandParameterMetadata* holds information about each of the command's parameters (specific to the core processing code).|

### 2. Add PyQt5 Predefined Translation Code

It is not known why this block of code is important. 
To create the first `command dialog` window, the [Qt Designer](http://doc.qt.io/qt-5/qtdesigner-manual.html) 
program was used to automate the creation of the *.py* file.
The Qt Designer program creates a *.ui* file and then using the 
[PyQt5 pyuic5 utility](http://pyqt.sourceforge.net/Docs/PyQt5/designer.html#pyuic5) the *.ui* file is converted to a *.py* file. 
This chunk of code was in the original converted *.py* file and remains present in 
the final version of the `command dialog` window *.py* file.

![PyQt5 Predefined Translation Code](images/pyqt5-translation.png)

### 3. Create the `Command Dialog` Window Class

The class name should be the same for all `command dialog` window classes - `UiDialog`.
The `UI_AbstractDialog` class is the parent class for all `command dialog` window classes.
It contains content and functions that apply to all `command dialog` window classes.

![`Command Dialog` Window Class](images/command_dialog_window_class.png)
	
### 4. Create the Class Variables 

The class variables are the variables that are consistent across each `command dialog` window for the specific commands. 
They are static, remaining the same value throughout the time that the GeoProcessor is running. 
	
|Class variable|Description|Value <br>Example from ReadGeoLayerFromGeoJSON_Editor|
|-|-|-|
|command_obj|The instance of the command. This is imported in the import statements from the `geoprocessor.commands.[python package].[command]` module.|`[command class]()`<br><br>`ReadGeoLayerFromGeoJSON()`|
|command_name|The name of the command. This is a set parameter within the command class so the value is called from the command_obj instance.|`command_obj.command_name`<br><br>`command_obj.command_name`|
|command_parameters|A list of the command's parameters. This is retrieved by running the imported CommandParameterMetadata `get_parameter_names` function on the command class instance (command_obj). |`CommandParameterMetadata.get_parameter_names(command_obj.command_parameter_metadata)`<br><br>`CommandParameterMetadata.get_parameter_names(command_obj.command_parameter_metadata)`|
|command_description|A brief description of the command. This is displayed in the UI dialog box at the top to give the user context.|`Description as a string.`<br><br>`"The ReadGeoLayerFromGeoJSON command reads a GeoLayer from a .geojson file. Specify the GeoJSON file to read into the GeoProcessor."`|
|parameter_count|The number of command parameters. This is automatically determined by counting the items in the `command_parameters` variable.|`len(command_parameters)`<br><br>`len(command_parameters)`|
|name label for each command parameter|Each command parameter is displayed in the `command dialog` window with at least one input field and a label to give context to the user which input field belongs to which parameter. The label variable follows the `[command parameter name (CamelCase)]_Label` naming convention. For now, the label variable for each command parameter is set to None.|`[command parameter name (CamelCase)]_Label=None`<br><br>`SpatialDataFile_Label=None`<br>`GeoLayerID_Label=None`<br>`IfGeoLayerIDExists_Label=None`|
|description for each command parameter|Each command parameter (besides those that have a *long LineEdit input field widget*) has a second label that displays a description of the parameter to the user. The description variable follows the `[command parameter name (CamelCase)]_Description_Label` naming convention. For now, the description label variable for each command parameter is set to None.|`[CommandParameterName]_Description_Label`<br><br>`GeoLayerID_Description_Label=None`<br>`IfGeoLayerIDExists_Description_Label=None`|
|specification class for each command parameter|There is information about each command parameter that is displayed on the `command dialog` window. This information is help in the CommandParameter class. There is one CommandParameter class instance for each command parameter. The CommandParameter class instance follows the `cp_[command parameter name (CamelCase)]` naming convention. See the [CommandParameter Class](#commandparameter-class) section for more information.|See the [CommandParameter Class](#commandparameter-class) section for values and examples.|
|ui_commandparameters| A list of the CommandParameter class instances.|`[cp_[CommandParameter1], cp_[CommandParameter2] ... ]`<br><br> `[cp_SpatialDataFile, cp_GeoLayerID, cp_IfGeoLayerIDExists]`|
	
#### CommandParameter Class

There is one `CommandParameter` class instance for each command parameter of a command user interface class. 
The `CommandParameter` class holds the following information about a command parameter:

- the name of the command parameter
- a brief description of the command parameter
- whether the command parameter is required or optional
- the command parameter's tooltip, if applicable. A tooltip is further detail about the command parameter that appears in a pop-up bubble when the parameter is hovered over in the `command dialog` window. 
- the default value of the command parameter

The `CommandParameter` instances are *class* variables of each `command dialog` window class. 
When designing a `command dialog` window class, the developer must manually enter all of the 
above information to initialize the `CommmandParameter` class for *each* of the command's parameters. 

The `CommandParameter` instance should follow the `cp_[CommandParameterName (CamelCase)` file naming convention. 
See the following initialization of the `ReadGeoLayerFromGeoJSON` `SpatialDataFile` parameter. 

`cp_SpatialDataFile = `<br>`CommandParameter(`<br>`name="SpatialDataFile",`<br>`                     description="absolute or relative path to the input GeoJSON file",`<br>`optional=False,`<br>`tooltip="The GeoJSON file to read (relative or absolute path).\n${Property} syntax is recognized.",`<br>`default_value_description=None`<br>`)`


### 5. Create the Instance Variables

The instance variables are the variables that are unique to the specific command at hand. 
Instance variables are dynamic and can be assigned new values throughout the time that the GeoProcessor is running. 

For example, a GeoProcessor command file could include two `ReadGeoLayerFromGeoJSON` commands.
The [class variables](#4-create-the-class-variables) are *shared* between the two `ReadGeoLayerFromGeoJSON` commands.
The instance variables are *unique* to each individual `ReadGeoLayerFromGeoJSON` command.

|Instance variable<br>( prefaced with `self.` )|Description|Value <br>Example from ReadGeoLayerFromGeoJSON_Editor|
|-|-|-|
|command_parameter_values|A dictionary that holds the user-specified command parameter values. Initialized with one entry for each command parameter. The value of each entry is set to `""`.<br><br> Key: the name of the command parameter <br> Value: the command parameter value  |`self.command_parameter_values = {}`<br><br>`for command_parameter_name in UiDialog.command_parameters:`<br>`self.command_parameter_values[command_parameter_name] = ""`|
|Qt widget for each command parameter|Each command parameter is displayed in the `command dialog` window with at least one input field and a label to give context to the user which input field belongs to which parameter. The input field follows the `[command parameter name (CamelCase)]_[Qt Widget Type (CamelCase)]` naming convention. For now, the label variable for each command parameter is set to None.|`[command parameter name (CamelCase)]_[Qt Widget Type (CamelCase)]`<br><br>`self.SpatialDataFile_LineEdit=None`<br>`self.SpatialDataFile_ToolButton=None`|


### 6. Initialize the Abstract Dialog Class

The `abstract dialog` window class is a dialog class that sets the universal configurations that are shared amongst all `command dialog` windows. 
The class is initialized within the initialization function of the `command dialog` window class. 
For more information about the `abstract dialog` window class, 
see the [The AbstractCommand_Editor Class](#the-abstractcommand_editor-class) section.

### 7. Create the `setupUi` function

The construction of the `command dialog` window occurs within the `setupUi()` class function. 
The contents of the `setupUi()` function will vary for each of the different `command dialog` windows. 

First, the [Abstract Dialog Class](#the-abstractcommand_editor-class) must be set up by calling `self.setupUi_Abstract(Dialog)`.
See the [`setupUi_Abstract()`](#setupui_abstract) section for more information. 

Secondly, create and configure all of the required Qt objects for each input command parameter. 
Each command parameter is *required* to have:

- a [QLabel](http://doc.qt.io/qt-5/qlabel.html) object to specify the command parameter name
- an input Qt field widget to allow the user to enter the parameter value

There are many different types of input Qt field widgets to select from. 
Commonly used Qt field widgets for `command dialog` windows include:

- [QLineEdit](http://doc.qt.io/qt-5/qlineedit.html#details): the user enters text in a single line field
- [QComboBox](http://doc.qt.io/qt-5/qcombobox.html#details): the user selects from a set of predefined values

Each command parameter *could* have:

- a second [QLabel](http://doc.qt.io/qt-5/qlabel.html) object to provide a parameter description
- a utility object (like a [QToolButton](http://doc.qt.io/qt-5/qtoolbutton.html#details)) to aid the user in choosing a command parameter input value

For each Qt widget used for a command parameter:

1. Create the command name QLabel object and assign it to the corresponding [class variable](#4-create-the-class-variables). 

	Example: `UiDialog.SpatialDataFile_Label = QtWidgets.QLabel(Dialog)`

2. Configure the command name QLabel object. 
The configuration settings for the QLabel object has already been created within the [`AbstractCommand_Editor.py`](#the-abstractcommand_editor-class) `configure[configureLabel]()` function.  
This sets the label's placement, name, title, alignment, etc.
For more information, see the [Configure QtWidget Functions](#configure-qtwidget-functions) section. 

	Example: `self.configureLabel(UiDialog.SpatialDataFile_Label, UiDialog.cp_SpatialDataFile.name)`

3. Create the input Qt field widget instance and assign it to the corresponding [instance variable](#5-create-the-instance-variables).

	Example: `self.SpatialDataFile_LineEdit = QtWidgets.QLineEdit(Dialog)`

4. Configure the input Qt field widget object. 
The configuration settings for many of the input field Qt Widget objects have already been created within the 
[`AbstractCommand_Editor.py`](#the-abstractcommand_editor-class) `configure[WidgetName]()` function. 
These functions sets the input field's placement, name, placeholder text, tooltip, required signal/slots, etc.
For more information, see the [Configure QtWidget Functions](#configure-qtwidget-functions) section. 

	Example: `self.configureLineEdit(self.SpatialDataFile_LineEdit, UiDialog.cp_SpatialDataFile.name, long=True, placeholder_text=UiDialog.cp_SpatialDataFile.description, tooltip=UiDialog.cp_SpatialDataFile.tooltip)`

5. Create the command description QLabel object and assign it to the corresponding [class variable](#4-create-the-class-variables), if applicable.

	Example: `UiDialog.GeoLayerID_Description_Label = QtWidgets.QLabel(Dialog)`

6. Configure the command description QLabel object. 
The configuration settings for the QLabel object has already been created within the [`AbstractCommand_Editor.py`](#the-abstractcommand_editor-class) `configure[configureDescriptionLabel]()` function.  
This sets the label's placement, name, text, alignment, etc.
For more information, see the [Configure QtWidget Functions](#configure-qtwidget-functions) section. 

	Example: `self.configureDescriptionLabel(UiDialog.GeoLayerID_Description_Label, 
UiDialog.cp_GeoLayerID.name, UiDialog.cp_GeoLayerID.description)`

### 8. Create the `refresh` function

The `refresh()` function updates the `command dialog` window with the command's parameter values when the user *edits* an existing command. 
To prompt the `refresh()` function, the user right-clicks a command in the 
[Command List UI Component](images/command_list_ui_component.png) and then clicks the 
`Edit Command` option in the pop-up menu. 

1. For each command parameter, assign a static variable with the command parameter's value.
The static variable follows the `[command parameter (lowercase, no spaces)]_value` naming convention. 
To obtain the current value of the command parameter, 
access the `command_parameter_values` [instance variable](#5-create-the-instance-variables)
by looking up the dictionary entry value with the command parameter name. 

	Example: `spatialdatafile_value = self.command_parameter_values["SpatialDataFile"]`
	
2. For each command parameter, set the value of the Qt Widget to the command parameter value.
Note that the [QComboBox](http://doc.qt.io/qt-5/qcombobox.html#currentIndex-prop) 
requires an index to set rather than the text. 

	Example: `self.SpatialDataFile_LineEdit.setText(spatialdatafile_value)`	

## List of Commands with Command Dialog Windows

The List of Commands with Command Dialog Windows provides an overview about which 
commands already have a `command dialog` window and which ones still need their `command dialog` windows developed. 
An **X** in the *Command Dialog Window Completed* column demonstrates that a `command dialog` 
window has been developed for that command.
The *Recommended Dialog Window Type* column provides a suggestion about which `command dialog` 
window design to use for that command. 

Commands that have multiple modes should have a multiple tabs within its `command dialog` window - 
one tab for each mode. 
For example, the 
[For()](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/command-ref/For/For/) 
command can iterate over a list, a sequence, or a table. 
Each one of these options should be in its own tab.
Other command only have one mode so their `command dialog` windows should only have one pane (single-tab). 
For example, the 
[ReadGeoLayerFromGeoJSON()]() command can only read one GeoLayer from one GeoJSON file in one mode. 

As of *2018/07/18*, a `command dialog` window class has only been created for a single-tab command. 
Use the `ReadGeoLayerFromGeoJSON()` `command dialog` window class as a template for creating other single-tab command windows.
A `command dialog` window class needs to be created for a multi-tab command window to act as the template for the other multi-tab command windows.

Update the contents of the list as development occurs. 

|GeoProcessor Command|Recommended Dialog Window Type|Command Dialog Window Completed|
|-||:-:|
|AddGeoLayerAttribute|Single-Tab||
|Blank|Single-Tab||
|ClipGeoLayer|Single-Tab||
|CompareFiles|Single-Tab||
|CopyFile|Single-Tab||
|CopyGeoLayer|Single-Tab||
|CloseDataStore|Single-Tab||
|CreateGeoLayerFromGeometry|Multi-Tab||
|CreateRegressionTestCommandFile|Single-Tab||
|EndFor|Single-Tab||
|EndIf|Single-Tab||
|For|Multi-Tab||
|FreeGeoLayers|Single-Tab||
|If|Single-Tab||
|IntersectGeoLayer|Single-Tab||
|ListFiles|Multi-Tab||
|MergeGeoLayers|Single-Tab||
|Message|Single-Tab||
|OpenDataStore|Multi-Tab||
|ReadGeoLayerFromDelimitedFile|Multi-Tab||
|ReadGeoLayerFromGeoJSON|Single-Tab|**X**|
|ReadGeoLayerFromShapefile|Single-Tab||
|ReadGeoLayersFromFGDB|Multi-Tab||
|ReadGeoLayersFromFolder|Single-Tab||
|ReadTableFromDataStore|Multi-Tab||
|ReadTableFromDelimitedFile|Single-Tab||
|ReadTableFromExcel|Single-Tab||
|RemoveFile|Single-Tab||
|RemoveGeoLayerAttributes|Single-Tab||
|RenameGeoLayerAttribute|Single-Tab||
|RunCommands|Single-Tab||
|RunProgram|Single-Tab||
|RunSql|Single-Tab||
|SetGeoLayerCRS|Single-Tab||
|SetGeoLayerProperty|Single-Tab||
|SetProperty|Single-Tab||
|SetPropertyFromGeoLayer|Single-Tab||
|SimplifyGeoLayerGeometry|Multi-Tab||
|StartLog|Single-Tab||
|StartRegressionTestResultsReport|Single-Tab||
|UnknownCommand|Single-Tab||
|UnzipFile|Single-Tab||
|WebGet|Single-Tab||
|WriteCommandSummaryToFile|Single-Tab||
|WriteGeoLayerPropertiesToFile|Single-Tab||
|WriteGeoLayerToDelimitedFile|Single-Tab||
|WriteGeoLayerToGeoJSON|Single-Tab||
|WriteGeoLayerToKML|Single-Tab||
|WriteGeoLayerToShapefile|Single-Tab||
|WritePropertiesToFile|Single-Tab||
|WriteTableToDataStore|Multi-Tab||
|WriteTableToDelimitedFile|Single-Tab||
|WriteTableToExcel|Single-Tab||
|Comment|Single-Tab||
|CommentBlockStart|Single-Tab||
|CommentBlockEnd|Single-Tab||

## Resources

- [Qt Documentation: Qt5 Layout Management](http://doc.qt.io/qt-5/layout.html)
- [Qt Documentation: Qt Widget Classes](http://doc.qt.io/qt-5/qtwidgets-module.html)
