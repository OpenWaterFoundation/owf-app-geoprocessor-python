# GeoProcessor / Development Environment / Python ##

Multiple versions of Python are installed to support GeoProcessor development and deployment.
Python versions that are used include:

* QGIS - Python 3.7 (or similar, depending on QGIS version)
installed with QGIS and will be used to initialize the Pycharm virtual environment
to edit code and run the GeoProcessor in PyCharm.
It is also used to initialize the virtual environment for deployment of full QGIS `gp` installations.
* Testing Framework - Python 3.7 (or similar, depending on QGIS version)
is used to create a virtual environment for the `gptest` testing framework,
which has no dependency on QGIS:
	+ for Windows, use a Python version consistent with QGIS to avoid issues
	+ for Cygwin, the latest Python 3 - deal with issues as necessary
	+ for Linux, the latest stable Python 3 - deal with issues as necessary
* Development Tools - Python 3 is used by MkDocs to process Markdown documentation into static websites
(typically use a system or user-installed Python 3) that may be the same as above.

The deployed GeoProcessor environment uses a Python virtual environment with Python that is compatible
with the operating system.
Therefore it is necessary to install Python and third-party packages in Windows, Cygwin, and Linux.
Windows 10 is currently the primary development environment and testing and secondary development occurs on Cygwin and Linux.
See the sections below discussing the installation of each version.

* [Install Python](#install-python)
	+ [Python for QGIS](#python-for-qgis) - currently ships with Python 3.7,
	and 3.6 was previously used with older versions of QGIS
	+ [Python 3.x](#python-3x) - currently 3.7 is the focus, although versions 3.4 to 3.7 have been used depending on operating system
* [Install Additional Python Packages](#install-additional-python-packages) - for example `virtualenv`

-----------------------------

## Install Python ##

Python must be installed consistent with the development environment and also
support the QGIS and testing framework variants of the GeoProcessor.

### Python for QGIS ###

Python for QGIS is installed when installing QGIS.
See the [QGIS installation documentation](qgis.md).

### Python 3.x ###

A typical Python installation is used (for example on Cygwin) for the GeoProcessor testing framework variant.
This Python is used as the base Python version for `virtualenv`, with no QGIS dependencies.
In this case, Python might use a version installed in a shared location (e.g., `C:\Python37` on Windows),
or in a user's account (e.g., `C:\Users\user\AppData\Local\Programs\Python...` on Windows 10).
The latter is recommended (by the installer dialog and its documentation) for newer Python versions
to isolate potential negative impacts on the system from Python
packages downloaded from the internet (less of an issue for well-respected packages).

The installation location of Python core software and third-party packages has evolved with each Python version.
Unfortunately, this can lead to confusion.
Consequently, within the GeoProcessor development environment,
it is recommended to use a script to run each Python application,
which allows configuration of the installed Python and add-ons to use.
For the GeoProcessor, this means that a script is use to run the GeoProcssor,
and a separate script is used to start PyCharm so that it can run the GeoProcessor (discussed in following sections).

In addition to a standard system or user Python installation, Python now also supports a virtual environment approach.
This approach is used to fully isolate the Python installation used by an application.
More disk space is needed because multiple versions of Python are installed in various folders.
However, the application is fully isolated from changes to the system/user Python installations.
A virtual environment approach is used with PyCharm development (see [Development Environment / PyCharm section](pycharm.md)) to run PyCharm.
A virtual environment approach is also used to deploy the GeoProcessor
(see [Development Tasks / Creating Installer](../dev-tasks/creating-installer.md)).

* See [Pipenv and Virtual Environments](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

The MkDocs software, which is used to prepare documentation,
will generally use a system/user version of Python since it can be used across multiple
Python projects.
The Python version that is used will be updated to include the MkDocs software packages and launch program.
In other words, the Python that is used for MkDocs may not be the QGIS or PyCharm Python versions.

The following can be used to check the version of Python that is installed:

#### ![Cygwin](../images/cygwin-32.png) Cygwin ####

```sh
$ which python3
$ python3 --version
```

#### ![Linux](../images/linux-32.png) Linux ####

```sh
$ which python3
$ python3 --version
```

#### ![Windows](../images/windows-32.png) Windows ####

```sh
> where python3
> python3 --version
```

The version of Python that is installed for testing framework and other uses
should be as close as possible to the QGIS version, which is 3.7 as of QGIS 3.4.3.
See the `C:\OSGeo4W64\apps` folder on Windows to see which version of Python is used.

If not installed, a typical Python install should be done as per Python installer instructions.

**Note that on Windows, trying to run `python` or `python3` directly may fail.**
This is because the Python version(s) that are installed may not have resulted in changing the `PATH`
environment variable and consequently the software can't be run from the command shell with just the program name.
To address this issue, recent versions of Python are distributed with `py.exe` program that is installed in
a system folder that is always in the `PATH`:

```
> where py
C:\Windows\py.exe
```

The `py` program provides a unified interface to Python and automatically finds Python installed in standard locations.
Use `py --help` to see usage information.
To be certain about which Python is being run, use an option like `py -3.7`,
where the number agrees with the QGIS Python version for consistency.
Windows batch files that run Python in the development environment use `py` with appropriate command line options
and the deployed software uses scripts that find the QGIS Python (for `gp` variant of GeoProcessor) and
virtual environment (for `gptest` variant).

#### ![Cygwin](../images/cygwin-32.png) Cygwin ####

Use the Cygwin setup tool to install Python as part of the Cygwin setup.
See the [Cygwin Installation](cygwin.md) documentation.
The version should be as near as possible to that used by QGIS although the Cygwin setup tool will
only provide selections for `python3`, not a specific version.
The latest Cygwin Python 3 version is typically compatible with GeoProcessor.

#### ![Linux](../images/linux-32.png) Linux ####

Use the `apt-get` program to install the Python 3 that is supported on the system.
If may be necessary to do a custom install if Python 3.7 is not available for the operating system.
The version should be as near as possible to that used by QGIS.
The latest Cygwin Python 3 version is typically compatible with GeoProcessor and version 3.4
and later has been tested successfully.

#### ![Windows](../images/windows-32.png) Windows ####

Download and install Python for Windows.
The version should be as near as possible to that used by QGIS, for example 3.7 in both cases.
If necessary, install QGIS first to confirm the Python version that is used.  See:

* [GeoProcessor Development Environment / QGIS](qgis.md)
* [Python Releases for Windows](https://www.python.org/downloads/windows/)
* [OWF / Learn Python](http://learn.openwaterfoundation.org/owf-learn-python/dev-env/python/python/)

## Install Additional Python Packages ##

After installing Python it will be necessary to install additional Python packages
that enable necessary functionality in the development environment,
such a as creating virtual environments.

### ![Cygwin](../images/cygwin-32.png) Cygwin ###

For Cygwin GeoProcessor `gptest` testing framework,
the GeoProcessor is run in a virtual environment into which are installed necessary Python additional packages.
Cygwin is often also typically used to run MkDocs for documentation.
Therefore, install the following Python packages in the Cygwin system Python,
from a Cygwin terminal window:

| **Package**           | **Description**                  | **Installation Command**       |
| --------------------- | -------------------------------- | ------------------------------ |
| `mkdocs`              | MkDocs documentation software.   | `pip3 install mkdocs`          |
| `mkdocs-material`     | MkDocs material theme.           | `pip3 install mkdocs-material` |
| `virtualenv`          | Python virtual environment tool. | `pip3 install virtualenv`      |

### ![Linux](../images/linux-32.png) Linux ###

For Linux GeoProcessor `gptest` testing framework,
the GeoProcessor is run in a virtual environment into which are installed necessary Python additional packages.
MkDocs may be used for documentation (or such documentation editing may be confined to Windows/Cygwin).
Therefore, install the following Python packages in the Linux system Python from a Linux terminal window:

| **Package**           | **Description**                  | **Installation Command**       |
| --------------------- | -------------------------------- | ------------------------------ |
| `mkdocs`              | MkDocs documentation software.   | `pip3 install mkdocs`          |
| `mkdocs-material`     | MkDocs material theme.           | `pip3 install mkdocs-material` |
| `virtualenv`          | Python virtual environment tool. | `pip3 install virtualenv`      |

### ![Windows](../images/windows-32.png) Windows QGIS Development Environment ###

The Windows QGIS development environment requires a number of additional packages
that are used by the GeoProcessor and if not installed will result in import errors when running the GeoProcessor.
The packages are installed into the QGIS Python environment.
See the [QGIS Install Additional Python Packages documentation](qgis.md#install-additional-python-packages) for instructions.
In particular, make sure to install `virtualenv` in order to be able to create Windows GeoProcessor
Python virtual environments for testing and for the GeoProcessor installer.

For general Python version (non-QGIS version) and to create the GeoProcessor virtual environment,
install the following additional packages in a Windows command shell for the developer's Python (non-QGIS Python).
Note that MkDocs is generally run in Cygwin but some developers may want to run in Windows.
**Currently a `gptest` (non-QGIS) version of the GeoProcessor and the `gp` distribution packages
a Python virtual environment that is not used (yet).**

The installation commands below indicate to the general Windows `py.exe` program which specific Python version
to install, by running `pip` within the correct Python version. 

| **Package**           | **Description**                  | **Installation Command**       |
| --------------------- | -------------------------------- | ------------------------------ |
| `mkdocs`              | MkDocs documentation software.   | `py -3.7 -m pip install mkdocs`          |
| `mkdocs-material`     | MkDocs material theme.           | `py -3.7 -m pip install mkdocs-material` |
| `virtualenv`          | Python virtual environment tool. | `py -3.7 -m pip install virtualenv`      |
