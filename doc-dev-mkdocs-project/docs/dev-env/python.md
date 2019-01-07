# GeoProcessor / Development Environment / Python ##

Multiple versions of Python need to be installed, if not already installed.
Python versions are used as follows:

* Python 3.7 (or similar, depending on QGIS version)
installed with QGIS will be used to initialize the Pycharm virtual environment
to edit code and run the GeoProcessor in PyCharm.
It may also be used to initialize the virtual environment for deployment;
however, the QGIS Python environment is a bit nonstandard and therefore a normal Python install
is recommended for creating the Python virtual environment for testing framework deployment (see below).
* Python 3.7 (or similar, depending on QGIS version) is used to create a virtual environment:
	+ for Windows, consistent wiht QGIS Python version
	+ for the GeoProcessor testing framework, independent of QGIS Python version.
* Python 2 or 3 is used by MkDocs to process Markdown documentation into static websites (can use the above version).

**Need to evaluate whether QGIS Python can be used for Python testing framework virtual environment.**

The deployed GeoProcessor environment uses a Python virtual environment with Python that is compatible
with the operating system.
Therefore it is necessary to install Python and third-party packages in Windows, Cygwin, and Linux.
Windows is currently the primary development environment, but testing and secondary development occurs on Cygwin and Linux.
See the sections below discussing the installation of each version.

* [Install Python](#install-python)
	+ [Python for QGIS](#python-for-qgis) - currently ships with Python 3.7, and 3.6 was previously used
	+ [Python 3.x](#python-3x) - currently 3.7 is the focus, although versions 3.4 to 3.7 have been used
* [Install Additional Python Packages](#install-additional-python-packages)

-----------------------------

## Install Python ##

Python must be installed consistent with the development environment and also
support the QGIS and testing framework variants of the GeoProcessor.

### Python for QGIS ###

Python for QGIS is installed when installing QGIS.
See the [QGIS installation documentation](qgis).

### Python 3.x ###

A typical Python installation is used (for example on Cygwin) for the GeoProcessor testing framework
variant, which is deployed as a virtual environment with no QGIS dependencies.
In this case, Python might use a version installed in a shared location (e.g., `C:\Python37` on Windows),
or in a user's account (e.g., `C:\Users\user\AppData\Local\Programs\Python...` on Windows 10).
The latter is recommended for newer Python versions (by the installer and its documentation)
to isolate potential negative impacts on the system from Python
packages downloaded from the internet (less of an issue for well-respected packages).
The installation location of Python core software and third-party packages has evolved with each Python version.
Unfortunately, this can lead to confusion.
Consequently, it is recommended to use a script to run each Python application,
which allows configuration of the installed Python and add-ons to use.
For the GeoProcessor, this means that a script is use to run the GeoProcssor,
and a separate script is used to start PyCharm so that it can run the GeoProcessor (discussed in following sections).

In addition to a standard system or user Python installation, Python now also supports a virtual environment approach.
This approach can be used to fully isolate the Python installation used by an application.
More disk space is needed.
However, the application is fully isolated from changes to the system/user Python installations.
A virtual environment approach is used with PyCharm development (see [Development Environment / PyCharm section](pycharm)) to run PyCharm.
A virtual environment approach is also used to deploy the GeoProcessor
(see [Development Tasks / Creating Installer](../dev-tasks/creating-installer)).

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
See the `C:\OSGeo464\apps` folder on Windows to see which version of Python is used.

**Need to verify that more specific instructions are not needed.
The installed Python needs to be handled by the `build-util` scripts.**

A typically Python install should be done:

#### ![Cygwin](../images/cygwin-32.png) Cygwin ####

Use the Cygwin setup tool to install Python as part of the Cygwin setup.
See the [Cygwin Installation](cygwin) documentation.
The version should be as near as possible to that used by QGIS.

#### ![Linux](../images/linux-32.png) Linux ####

Use the `apt-get` program with Python 3 that is supported on the system.
If may be necessary to do a custom install if Python 3.7 is not available for the operating system.
The version should be as near as possible to that used by QGIS.

#### ![Windows](../images/windows-32.png) Windows ####

Download and install Python for Windows.
The version should be as near as possible to that used by QGIS.

## Install Additional Python Packages ##

After installing Python it will be necessary to install additional Python packages.

### ![Cygwin](../images/cygwin-32.png) Cygwin ###

For Cygwin GeoProcessor testing framework,
the GeoProcessor is run in a virtual environment into which are installed necessary Python
additional packages.  No additional Python package installation is needed.

**Need to confirm - do need to install virturalenv.**

### ![Linux](../images/linux-32.png) Linux ###

For Linux GeoProcessor testing framework,
the GeoProcessor is run in a virtual environment into which are installed necessary Python
additional packages.  No additional Python package installation is needed.

**Need to confirm - do need to install virturalenv.**

### ![Windows](../images/windows-32.png) Windows QGIS Development Environment ###

The Windows QGIS development environment requires a number of additional packages.
These are installed into the QGIS Python environment.
See the [QGIS Install Additional Python Packages documentation](qgis#install-additional-python-packages).

For general Python version (non-QGIS version) used to create the GeoProcessor virtual environment and
for general tasks, install the following additional packages.

| **Package**           | **Description**                  | **Installation Command**       |
| --------------------- | -------------------------------- | ------------------------------ |
| `mkdocs`              | MkDocs documentation software.   | `pip3 install mkdocs`          |
| `mkdocs-material`     | MkDocs material theme.           | `pip3 install mkdocs-material` |
| `virtualenv`          | Python virtual environment tool. | `pip3 install virtualenv`      |
