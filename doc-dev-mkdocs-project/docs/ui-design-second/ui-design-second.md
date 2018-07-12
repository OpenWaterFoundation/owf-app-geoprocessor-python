# User Interface 

## Overview

This documentation is in place to explain the current user interface design. 
The design is still in implementation phase and can be redesigned in the future if needed. 
The GeoProcessor user interface is currently in working order. 
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

As mentioned above, the only command that is fully functional within the GeoProcessor user interface is `ReadGeoLayerFromGeoJSON`. However, the infrastructure to build `command dialog` windows for the other GeoProcessor commands has already been constructed and can be used to quickly construct the UI functionality for the other commands. This documentation explains the UI software infrastructure in detail and can be followed to construct the remaining commands within the user interface. 

Although the other commands are not fully functional within the user interface, those commands can still be run within the user interface.  `"fully functional within the user interface"` only means that there is not yet a `command dialog` window created for that command. The reading of a command file and the running of that command file is performed within the GeoProcessor `/core` code. To run a command file within the UI, follow the instructions below:

1. Start the GeoProcessor user interface.
2. Click `File` > `Open Command File`.
3. Browse to and select the command file of interest. 
4. The command file will appear in the `command list` ui component. Each line of the command file is a unique line in the `command list` ui component
5. Click the `Run Commands` button. This will read the text within the `command list` ui component and will pass that string to the GeoProcessor `core` code to be parsed, read and run. The GeoProcessor runs with a single string input. All parsing and running of the command occurs within the `core` code. 

## User Interface Terms

|Term|Definition|Image|
|-|-|-|
|Main Window|The GeoProcessor's home window. All functionality within the GeoProcessor user interface can be accessed via this window. The `main` window is the first window to appear when the GeoProcessor is started in *ui* mode.|<a href = "../main_window.png">![Main Window](main_window.png)</a>|
|Command Dialog Window|The user interface window that allows the user to create a new command or edit an existing command. There is one `command dialog` window for each GeoProcessor command. The command dialog window has input fields used to enter the values for the command parameters.| <a href = "../command_dialog_window.png">![Command Dialog Window](command_dialog_window.png)</a>|
|Command List UI Component|A subset of the GeoProcessor main window that holds the commands of the command file. There is one line within the `command list` ui component for each command of the command file.|<a href = "../command_list_ui_component.png">![Command List UI Component](command_list_ui_component.png)</a>|

## Folder Structure

```
ui/
	__init__.py
	app/
    	__init__.py
        GeoProcessorUI.py
        GeoProcessorUI_Design.py
	commands/
    	__init__.py
    	datastores/
        layers/
        logging/
        running/
        tables/
        testing
        util/
    templates/
    	__init__.py
        template_cmdDialogMultiTab.ui
        template_cmdDialogOneTap.py
        template_cmdDialogOneTab.ui
        template_mainWindow.py
        template_mainWindow.ui
    util/
    	__init__.py
        AbstractCommand_Editor.py
        command_parameter.py
        config.py
```

Each GeoProcessor command should have its own `command dialog` window. 
In initial development, only a select number of the commands have a `command dialog` window.
See the [List of Commands with Command Dialog Windows](#list-of-commands-with-command-dialog-windows) for information about which commands already have a `command dialog` window and which commands need ui development. 
Future development must take place to create `command dialog` windows for the remaining GeoProcessor commands. 
The [List of Commands with Command Dialog Windows](#list-of-commands-with-command-dialog-windows) list should be updated as future development occurs. 
Once all current GeoProcessor commands have `command dialog` windows, the creation of new commands should include a ui component. 
For example, the workflow of creating commands should follow these steps:

1. Create a functional command in the core GeoProcessor code.
2. Create tests for the command.
3. Create documentation for the command.
4. Review the command with the GeoProcessor review team (Steve Malers).
5. Edit the code, tests and documentation to address concerns in the review.
6. Create a UI `command dialog` window for the commmand. 

## Creating a `Command Dialog` Window

To develop a `command dialog` window  with the single-tab design, use the `ReadGeoLayerFromGeoJSON_Editor.py` script as a template. 

1. Import required modules

	|Import Statement&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|Description|
|-|-|
|`from`<br>`PyQt5`<br>`import`<br>`QtWidgets`|The user interface is built on the [PyQt5](http://pyqt.sourceforge.net/Docs/PyQt5/introduction.html) library. QtWidgets are the building blocks for each of the items on the `command dialog` window.|
|`from`<br>`geoprocessor.commands.[python package].[command]`<br>`import`<br>`[command class]`|The user interface obtains information from the command's core code. |
|`from`<br>`geoprocessor.ui.util.AbstractCommand_Editor`<br>`import`<br>`UI_AbstractDialog`|The *UI_AbstractDialog* class holds variables and functions that are consistent across all `command dialog` windows.|
|`from`<br>`geoprocessor.ui.util.command_parameter`<br>`import`<br>`Command_Parameter`|The *Command_Parameter* class is used as a building block to hold information about each of the command's parameters (specific to the user interface).|
|`from`<br>`geoprocessor.core`<br>`import`<br>`CommandParameterMetadata`|The *CommandParameterMetadata* holds information about each of the command's parameters (specific to the core processing code).|

2. Add PyQt5 Pre-defined Translation Code

	It is not known why this block of code is important. 
To create the first `command dialog` window, the [Qt Designer](http://doc.qt.io/qt-5/qtdesigner-manual.html) program was used to automate the creation of the *.py* file.
The Qt Designer program creates a *.ui* file and then using the [PyQt5 pyuic5 utility](http://pyqt.sourceforge.net/Docs/PyQt5/designer.html#pyuic5) the *.ui* file is converted to a *.py* file. 
This chunk of code was in the original converted *.py* file and remains present in the final version of the `command dialog` window *.py* file.

	![PyQt5 Pre-defined Translation Code](pyqt5-translation.png)

3. Create the `Command Dialog` Window Class

	The class name should be the same for all `command dialog` window classes - `UiDialog`.
The `UI_AbstractDialog` class is the parent class for all `command dialog` window classes.
It contains content and functions that apply to all `command dialog` window classes.

	![`Command Dialog` Window Class](command_dialog_window_class.png)
	
4. Create the Class Variables 

	The class variables are the variables that are consistent across each `command dialog` window for the specific commands. 
	They are static, remaining the same value throughout the time that the GeoProcessor is running. 
	
	


## List of Commands with Command Dialog Windows

The List of Commands with Command Dialog Windows provides an overview about which commands already have a `command dialog` window and which ones still need thier `command dialog` windows developed. 
An **X** in the *Command Dialog Window Completed* column demonstrates that a `command dialog` window has been developed for that command.
The *Recommended Dialog Window Type* column provides a suggestion about which `command dialog` window design to use for that command. 

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











