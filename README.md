# owf-app-geoprocessor-python #

Open Water Foundation geoprocessor based on QGIS.

## Design Elements ##

The OWF GeoProcessor is a Python application similar to TSTool, but for processing spatial data layers and maps.
The following are basic design elements:

1. The user interface will be similar to TSTool:
	* Instead of focusing on time series, focus on map layers, each with unique ID.
	* A layer is a collection of features.
2. Implement concept of datastores to read/write layers:
	* Geodatabase and web services allow query of a set of features (as a layer).
	* GeoJSON and shapefiles are implemented as "file datastore".
	* Use configuration file for each datastore.
3. Graphical User Interface (User Interface, UI) implemented in QT or TCL?
	* Main window.
	* Menus to select and edit commands.
	* Tabular area to browse map layers.
	* Area to display commands.
	* Tabbed area to display results.
	* Map window to view maps similar to TSTool time series graphs?
	* Off-screen map window for creating images.
3. Provide menus for geoprocessing commands.
	* See TSTool organization for reading, manipulationg, outputting, etc., but instead
	of time series, process map layers.
	* Also include general menus similar to TSTool for performing tasks such as copy file, WebGet(), etc.
	* Include commands to perform testing, for example CompareMapLayers(), CompareFiles().
4. Commands are run using a processor, similar to:
	* [TSCommandProcessor](https://github.com/OpenWaterFoundation/cdss-lib-processor-ts-java/blob/master/src/rti/tscommandprocessor/core/TSCommandProcessor.java)
	* The above calls [TSEngine](https://github.com/OpenWaterFoundation/cdss-lib-processor-ts-java/blob/master/src/rti/tscommandprocessor/core/TSEngine.java)
	* The processor keeps in memory a list of global properties to control processing
	* The processor keeps in memory a list of map layers, which have unique identifiers
	* Question:  does python library have concept if in-memory layer,
	or are they always representing in a datastore or file?
	* Commands have a status and log of messages
	* Commands should use TSTool-like syntax, text with named-parameter syntax.
	* Save commands as a file.
5. Software should be object-oriented
	* Use parent classes for abstract functionality
	* Use class for each command
	* Use class for each command editor.  See TSTool's design.  This keeps UI and computation code separate.
6. Implement logging:
	* See TSTool StartLog() command.
7. Application should run in different modes:
	* Full UI similar to TSTool.
	* Batch mode with --commands CommandFile option.
8. Portable to run on Windows and Linux.
