# PyCharm #

PyCharm is the Python integrated development environment tool that has been chosen by OWF for development.
Other developers may use other tools if they desire but such tools have not been investigated.
The PyCharm Community Edition is adequate for development.
The GitHub repository for the project is used as the PyCharm project folder
and PyCharm project files are ignored using `.gitignore`.
This means that the developer must set up the PyCharm project themselves rather than
relying on PyCharm project files in the repository.
This approach has been chosen because it is the least prescriptive to the developer community
and Python developers are expected to at least know how to set up a project in their development tool of choice.

The PyCharm IDE runs Python in the development environment,
and therefore each project must be configured to know which Python interpreter to use.
PyCharm is typically configured to use a Python version in the virtual environment folder (`venv`) that is
set up when the GeoProcessor Python project is setup, as shown in the following figure.
If a virtual environment is not set up, then the Python that was selected when
the project was set up will be used (such as user's copy of Python).
A virtual environment is recommended in order to better control development environment Python
packages, which helps understand which packages are needed in the deployed system.
The following image illustrates the interpreter installed in a `venv` folder
(open the image in a new tab to view a larger image).

![PyCharm interpreter](images/pycharm-settings-project-interpreter.png)

QGIS is distributed with Python for its run-time environment,
rather than using the user's or computer's Python or PyCharm Python.
The QGIS libraries must be made known to PyCharm in order for the GeoProcessor code to
function without errors (see the [Script to Run PyCharm](#script-to-run-pycharm) section).
The PyCharm virtual environment Python (3.x, consistent with QGIS) will be used for development.
The Python environment used for PyCharm can use the QGIS Python if it is specified as the project interpreter, as shown below.
However, the GeoProcessor is typically run in the development environment using the batch file `gpdev.bat` or `gpuidev.bat`.

![PyCharm interpreter](images/pycharm-settings-project-interpreter-qgis.png)

**Need to clarify the above, especially as development with QGIS/Python 3 is implemented.**

The QGIS Python can be used in a deployed environment, as long as the GeoProcessor module (`geoprocessor`) is
installed in QGIS `site-packages` folder or `PYTHONPATH` includes the GeoProcessor module.
Using the QGIS environment as much as possible helps ensure that there are no compatibility issues with the QGIS software,
which is important because much of the GeoProcessor processing is performed with QGIS tools.
The GeoProcessor is normally distributed using a Python virtual environment so that users don't
have to install any Python or other software.
See the [Development Tasks / Creating Installer](../dev-tasks/creating-installer) documentation.

To run QGIS software, PyCharm and applications that use QGIS (including the GeoProcessor),
it is best to use a batch file (Windows) or shell script (Linux).
This ensures that the correct version of Python and additional Python modules are properly configured.
This is discussed in the [New Developer](../dev-new/dev-new) section.

### Install PyCharm ##

Install the PyCharm 64-bit Community Edition:

* [PyCharm Download page](https://www.jetbrains.com/pycharm/download/#section=windows) - select Windows
* The installer has the option of creating a desktop shortcut.  Do this for 64-bit launcher.
* It is not necessary to associate `.py` files with PyCharm.
* Otherwise, accept the defaults.
* The installer appears to be intelligent enough to carry forward configuration information from previous installations of PyCharm.

This will install into a folder similar to `C:\Program Files\JetBrains\PyCharm Community Edition 2018.1.2`
(new versions are released periodically).
Once installed the software may periodically ask to install updates.
Doing so does not appear to change the original install folder (even if the version changes)...updates seem
to install in the same folder.
It may be that an update only creates a new folder for a new year.

### Script to Run PyCharm ###

As indicated in previous sections, it is necessary to use the QGIS Python and packages in order to use the QGIS functionality.
PyCharm must also leverage QGIS.
Therefore, a batch file or script can be used to configure the environment and run PyCharm.
This script must recognize the install location of PyCharm software, which may be different for each developer.
To start PyCharm, run one of the following scripts, with location shown relative to the project files once
cloned from the repository (explained in the [New Developer](../dev-new/dev-new) section):

* Windows (via command prompt window):
	+ [owf-app-geoprocessor-python/build-util/run-pycharm-ce-for-qgis.bat](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/blob/master/build-util/run-pycharm-ce-for-qgis.bat) - run PyCharm Community Edition installed in the standard location - the most recent PyCharm version found will be run
	+ Other scripts may be added to run other versions of PyCharm or other tools
* Linux (via terminal window):
	+ PyCharm is currently not used in Linux for development but will be tested in the future.
