# Development Tasks / Editing Code #

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
