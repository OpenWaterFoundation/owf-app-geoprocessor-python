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
		+ **Exception to these standards may occur, in particular function names that include uppercase where appropriate.**
	+ Module file contents:
		+ Each class has its own file (`ClassName.py` for class named `ClassName`).
		+ Other modules contain functions grouped by functionality.
		For example `geoprocessor.util.string_util.py` contains utility functions that process strings.
* Use Google-style docstrings for documentation.
See how to the [Configure PyCharm documentation](../dev-env/pycharm.md#configure-pycharm).
* Respond to PyCharm PEP warnings to fix style issues so that each file receives a check-off.
* New files created in PyCharm or other Windows tools may need permissions changed to not be executable if
using Cygwin as the primary environment for the Git repository local files.
See the [Issues with File Permissions documentation](version-control.md#issues-with-file-permissions).
