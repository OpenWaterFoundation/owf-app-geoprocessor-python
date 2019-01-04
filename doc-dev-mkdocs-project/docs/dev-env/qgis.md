# GeoProcessor / Development Environment / QGIS #

The GeoProcessor is being developed for QGIS 3.x, which uses Python 3.6+.
QGIS is distributed with an optional long-term stable release that uses Python 2.7;
this version was used with initial GeoProcessor development but is no longer used.
The following resources explain how to install QGIS, and 64-bit QGIS is recommended if the
computer operating system is 64-bit.

* [Install QGIS](#install-qgis)
* [Install Additional Python Packages](#install-additional-python-packages)
* [QGIS Python Runtime Configuration](#qgis-python-runtime-configuration)

-------------

## Install QGIS ##

Install QGIS using the instructions in the
[OWF / Learn QGIS](http://learn.openwaterfoundation.org/owf-learn-qgis/install-qgis/install-qgis/) documentation.
See also:

* [QGIS download page](https://www.qgis.org/en/site/forusers/download.html)
	+ The ***Express Install*** is generally OK since QGIS 2 is no longer used by the GeoProcessor.
	GeoProcessor developers can typically use the OsGeo4W suite (no need for map server, etc.).
* For information on how QGIS is packaged, see also:
[QGIS Version Install Experiments](../resources/qgis-version-install-experiments) for detailed background.

## Install Additional Python Packages ##

After installing QGIS, it is necessary to install additional Python packages that are used in the GeoProcessor.
Currently, these are installed in the QGIS Python environment.
However, in the future an alternate approach may be implemented to avoid corrupting the QGIS environment.
The deployed GeoProcessor environment uses a virtual environment that is separate from QGIS files to separate QGIS
and GeoProcessor software.
To install the third party packages in the QGIS installation, run the installation commands as shown in the following table.

To install third party packages on the Windows QGIS version of GeoProcessor:

1. Open ***Start / OSGeo4W / OSGeo4W Shell*** 
2. Enter `set PYTHONHOME=C:\OSGeo4W64\apps\Python37` (similar if Python 3.6 or other version of Python is being used)
3. Enter the software package command (located in the `Command` column of the table below).
Note that `python3 -m pip` is used instead of `pip3` because `pip3` is not available in the QGIS bin folder.

|**Software Package Name**|**Source Link(s)**|**How Used Within GeoProcessor**| **Command**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|
|-|-|-|-|
|pandas|[https://pandas.pydata.org/](https://pandas.pydata.org/)|Holds and manipulates Table data.|`python3 -m pip install pandas`|
|OpenPyXL|[https://openpyxl.readthedocs.io/en/stable/](https://openpyxl.readthedocs.io/en/stable/)|Reads and writes Excel 2010 xlsx/xlsm files to and from Table objects.|`python3 -m pip install openpyxl`|
|requests (extended package)|[http://docs.python-requests.org/en/master/](http://docs.python-requests.org/en/master/)<br><br> [https://pypi.org/project/requests/](https://pypi.org/project/requests/)|Downloads data files within the [`WebGet`](../command-ref/WebGet/WebGet) command. <br><br>The `requests[security]` extension package is preferred over the core `requests` package to avoid an error that would occur when downloading a file over `https` with the [`WebGet`](../command-ref/WebGet/WebGet) command. The error that occurred when using the core `requests` package printed:<br>`requests.exceptions.SSLError: [Errno 1] _ssl.c:503: error:140770FC:SSL routines:SSL23_GET_SERVER_HELLO:unknown protocol`. <br>This error does not occur when utilizing the `requests[security]` extension package. | `python3 -m pip install requests[security]`|
|SQLAlchemy|[http://www.sqlalchemy.org/](http://www.sqlalchemy.org/)|Enables connections to databases.|`python3 -m pip install SQLAlchemy`|

## QGIS Python Runtime Configuration ##

The QGIS Python installation version will vary depending on QGIS version but is generally
configured similar to the following on Windows:

* `C:\OSGeo4W64\bin\python3.exe` (Python 3) -
QGIS Python interpreter, found in QGIS `bin` folder for convenience.
Other Python executables that would normally be found in the Python `bin` folder
also exist in `C:\OSGeo4W64\bin`.
* `C:\OSGeo4W64\apps\Python37\` - similar to above but for Python 3, phased in in 2018
* `C:\OSGeo4W64\apps\Python36\` - similar to above but for Python 3, phased out in 2018
* [For historical purposes]: `C:\OSGeo4W64\apps\Python27\` - typical Python 2 installation folder structure, minus `bin`
(since those programs exist in the folder described above):
	+ `C:\OSGeo4W64\apps\Python27\Lib\*` - third-party Python packages
	+ `C:\OSGeo4W64\apps\Python27\Lib\site-packages\*` - additional contributed Python packages
	(this is one option to install the GeoProcessor in the deployed environment)

The GeoProcessor should use the QGIS configuration during development:

* PyCharm must use QGIS libraries in `PYTHONPATH` ([discussed more here](pycharm))
* Running tests in the development environment via `scripts/gpdev` and `scripts/gpuidev` scripts,
which uses the development GeoProcessor code
([discussed more here](running)) can use the QGIS Python and libraries.

The deployed environment uses a Python virtual environment to isolate the GeoProcessor from other Python versions
on the computer and can be run using the `scripts/gp` and `scripts/gpui` programs.
