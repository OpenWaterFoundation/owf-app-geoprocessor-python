# GeoProcessor / Development Environment / QGIS #

The GeoProcessor is being developed for QGIS 3.x, which uses Python 3.6+.
QGIS is distributed with an optional long-term stable release that uses Python 2.7;
this version was used with initial GeoProcessor development but is no longer used.
The following resources explain how to install QGIS, and 64-bit QGIS is recommended if the
computer operating system is 64-bit.

* [Install QGIS](#install-qgis)
* [Install Additional Python Packages](#install-additional-python-packages)
* [QGIS Python Runtime Executable](#qgis-python-runtime-executable)

-------------

## Install QGIS ##

Install QGIS:

* The instructions in the
[OWF / Learn QGIS](http://learn.openwaterfoundation.org/owf-learn-qgis/install-qgis/install-qgis/) documentation
provide information about the QGIS downloads.
* [QGIS download page](https://www.qgis.org/en/site/forusers/download.html)
	+ Currently, the OSGeo4W install is recommended for GeoProcessor development.
	There is generally no need for map server, etc., but these components of the OSGeo4W suite may be
	integrated later.
	+ The standalone QGIS install can also be used but has not been tested or documented for a PyCharm project setup.
		- For testing, run `gpuidev.bat /s` in the development environment to run the development GeoProcessor
		with installed standalone QGIS.
		However, this will require installing add-on packages like `pandas`.
	+ The QGIS ***Express Install*** is generally OK since long term release QGIS 2 is no longer
	in GeoProcessor development.
* For information on how QGIS is packaged, see:
[QGIS Version Install Experiments](../resources/qgis-version-install-experiments.md) for detailed background.

## Install Additional Python Packages ##

**This section has been tested with OSGeo4W QGIS installation but not standalone QGIS installation.**

After installing QGIS, it is necessary to install additional Python packages that are used in the GeoProcessor.
Currently, these are installed in the QGIS Python environment.
However, in the future an alternate approach may be implemented to avoid dependency conflicts in the QGIS environment
(should that case occur).
The deployed GeoProcessor environment uses a virtual environment that keeps QGIS files separate from 
GeoProcessor-related Python packages.
To install the third party packages in the QGIS installation, run the installation commands as shown in the following table.

To install third party packages on the Windows QGIS version of GeoProcessor:

1. Open ***Start / OSGeo4W / OSGeo4W Shell*** to start an environment compatible with OSGeo4W Python.
Note that by default (as of 2019-01-20) the initial configuration will use Python 27
This seems like something that will be remedied in the future, in which case the following instructions
may need to be modified.
See the article [OSGeo4W shell with python3](https://gis.stackexchange.com/questions/273870/osgeo4w-shell-with-python3).
Therefore, once the shell is open, run `C:\OSGeo4W64\bin\py3_env.bat`.
3. Enter the command to install the software package.
Note that `python3 -m pip` is used instead of `pip3` because `pip3` is not available in the QGIS bin folder.

|**Software Package Name**|**Source Link(s)**|**How Used Within GeoProcessor**| **Command**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|
|-|-|-|-|
|pandas|[https://pandas.pydata.org/](https://pandas.pydata.org/)|Holds and manipulates Table data.|`python3 -m pip install pandas`|
|OpenPyXL|[https://openpyxl.readthedocs.io/en/stable/](https://openpyxl.readthedocs.io/en/stable/)|Reads and writes Excel 2010 xlsx/xlsm files to and from Table objects.|`python3 -m pip install openpyxl`|
|requests (extended package)|[http://docs.python-requests.org/en/master/](http://docs.python-requests.org/en/master/)<br><br> [https://pypi.org/project/requests/](https://pypi.org/project/requests/)|Downloads data files within the [`WebGet`](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/command-ref/WebGet/WebGet/) command. <br><br>The `requests[security]` extension package is preferred over the core `requests` package to avoid an error that would occur when downloading a file over `https` with the [`WebGet`](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/command-ref/WebGet/WebGet/) command. The error that occurred when using the core `requests` package printed:<br>`requests.exceptions.SSLError: [Errno 1] _ssl.c:503: error:140770FC:SSL routines:SSL23_GET_SERVER_HELLO:unknown protocol`. <br>This error does not occur when utilizing the `requests[security]` extension package. | `python3 -m pip install requests[security]`|
|SQLAlchemy|[http://www.sqlalchemy.org/](http://www.sqlalchemy.org/)|Enables connections to databases.|`python3 -m pip install SQLAlchemy`|
|virtualenv|[https://virtualenv.pypa.io/en/latest/](https://virtualenv.pypa.io/en/latest/)|Used to package the GeoProcessor runtime into an isolated Python environment when [creating an installer](../dev-tasks/creating-installer.md).  **This only needs to be installed if the software developer will be building the Windows GeoProcessor installer.**|`python3 -m pip install virtualenv`|

## QGIS Python Runtime Executable ##

The QGIS Python installation version will vary depending on QGIS version but is generally
configured similar to the following on Windows.
The location of executable is needed to configure the PyCharm virtual environment.

* OSGeo4W QGIS Install:
	+ `C:\OSGeo4W64\bin\python3.exe` (Python 3) -
	QGIS Python interpreter, found in QGIS `bin` folder for convenience.
	Other Python executables that would normally be found in the Python `bin` folder
	also exist in `C:\OSGeo4W64\bin`.
	+ `C:\OSGeo4W64\apps\Python37\` - similar to above but for Python 3, phased in in 2018
	+ `C:\OSGeo4W64\apps\Python36\` - similar to above but for Python 3, phased out in 2018
	+ [For historical purposes]: `C:\OSGeo4W64\apps\Python27\` - typical Python 2 installation folder structure, minus `bin`
	(since those programs exist in the folder described above):
		- `C:\OSGeo4W64\apps\Python27\Lib\*` - third-party Python packages
		- `C:\OSGeo4W64\apps\Python27\Lib\site-packages\*` - additional contributed Python packages
		(this is one option to install the GeoProcessor in the deployed environment)
* Standalone QGIS Install:
	+ `C:\Program Files\QGIS 3.#\bin\python3.exe`
	QGIS Python interpreter, found in QGIS `bin` folder for convenience.
	Other Python executables that would normally be found in the Python `bin` folder
	also exist in `C:\Program Files\QGIS #.#\bin`.
	+ `C:\Program Files\QGIS 3.#\apps\Python37` - full Python installation folder
	+ `C:\Program Files\QGIS 3.#\apps\Python27` - long term release Python version, for older software

The GeoProcessor should use the QGIS configuration during development:

* PyCharm must use QGIS libraries in `PYTHONPATH` ([discussed more here](pycharm.md)).
* Running tests in the development environment via `scripts/gpdev` and `scripts/gpuidev` scripts,
which uses the development GeoProcessor code
([discussed more here](running.md)) can use the QGIS Python and libraries.

The deployed environment uses a Python virtual environment to isolate each projects's development environment.
The Python files in the development environment can be run using the `scripts/gp` and `scripts/gpui` programs for QGIS version,
and `scripts/gptest` and `scripts/gptestui` for testing framework version.
