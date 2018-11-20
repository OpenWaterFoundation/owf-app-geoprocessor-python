# Python Virtual Environment #

## Overview ##

Python relies extensively on built-in and third-party modules in multiple files.
Multiple versions of Python may also be installed on a computer,
leading to potential confusion in what is installed and what is used at runtime.

The current best practice is to use Python virtual environments to deploy applications.
This should work well for the test framework version of the GeoProcessor (no QGIS).
Additional effort will be needed to evaluate how a virtual environment might work with QGIS.

Resources:

* [Python Virtual Environment Introduction](https://www.geeksforgeeks.org/python-virtual-environment/)
* [Creating Python Virtual Environment in Windows and Linux](https://www.geeksforgeeks.org/creating-python-virtual-environment-windows-linux/)

## Cygwin Python Setup ##

The target environment for the GeoProcessor is Windows (mainly QGIS), Cygwin (mainly test framework),
and Linux (initially test framework but may also support QGIS).

### Cygwin ###

The core Python environment should be available as the base Python to initialize the virtual environment.
Therefore, install the `python3` software via the Cygwin installer.
Note that Python 2 will be available with command line `python` command and Python 3 will be
available with the `python3` command.
Confirm that `python3` is available as expected.
If not available in Cygwin, install using the Cygwin setup program.
If `python3` is found in a Windows folder, then make sure to install in Cygwin.

```
$ which python3
/usr/bin/python3
```

`pip3` does not appear to be installed by default, which can be confirmed as follows.
The following indicates that Cygwin is actually finding `pip3` via the Windows `PATH`,
not a Cygwin version of `pip3`.

```
$ which pip3
/cygdrive/c/Program Files/Python35/Scripts/pip3
```

Another way to check is by trying to load the pip module in Python 3.
The following confirms that the pip module is not found in the normal Python 3 installation.

```
$ python3 -m pip
/usr/bin/python3: No module named pip
```

Given that `pip` and `pip3` are the standard way to install software modules,
how is it possible to install `pip3`?
Python 3 provides a one-line way to install `pip3`, as shown below.
Because the files are installed into protected space,
the command must be run in a Cygwin terminal ***Run as administrator***
(right-click on the Cygwin desktop icon and run as administrator).

```
SystemAdmin@RoaringFork ~
$ python3 -m ensurepip
Collecting setuptools
Collecting pip
Installing collected packages: setuptools, pip
Successfully installed pip-9.0.1 setuptools-28.8.0
```

The installation of `pip3` can be confirmed in a normal Cygwin terminal (not run as Administrator) as follows:

```
$ which pip3
/usr/bin/pip3
```

The `virtualenv` module is also needed to create vitual environments.  Check for availability with:

```
$ virtualenv --version
-bash: virtualenv: command not found
```

If not found, install from a Cygwin command line run as Administrator:

```
$ pip3 install virtualenv
Collecting virtualenv
  Downloading https://files.pythonhosted.org/packages/7c/17/9b7b6cddfd255388b58c61e25b091047f6814183e1d63741c8df8dcd65a2/virtualenv-16.1.0-py2.py3-none-any.whl (1.9MB)
    100% |████████████████████████████████| 1.9MB 449kB/s
Installing collected packages: virtualenv
Successfully installed virtualenv-16.1.0
You are using pip version 9.0.1, however version 18.1 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.
```

Installation can be confirmed in a normal Cygwin (not Administrator) window:

```
$ which virtualenv
/usr/bin/virtualenv
$ virtualenv --version
16.1.0
```

The Cygwin Python 3 installation can then be used for building
virtual environments for the GeoProcessor.

### Linux ###

### Windows ###

## build-util/create-gp-virtualenv-installer.sh ##

This script creates a virtual environment containing the GeoProcessor and necessary dependencies.

## Need GCC

Some pip downloads try to recompile C programs. There are pip options `--only-binary` and `--prefer-binary` but
even so it seems that being able to compile is a better option.  Therefore, make sure that Cygwin packages
are installed for:

* `gcc-core` - needed to compile C programs
* `gcc-fortran` - needed to compile Fortran
* `python3-devel` - need for Python development tools, which includes Python.h header file, needed by multiple packages
* `libffi-devel` - needed to compile requests[security]
* `libpq-devel` - needed for psycopg2
* `openssl-devel` - needed to compile requests[security]
* For Pandas, see [list of required modules](https://stackoverflow.com/questions/34341112/pandas-build-on-cygwin)
and substitue the Python3 versions listed below.  Tried to let pip build Pandas but it had lots of issues.
	+ `python3-numpy`
	+ `python3-six`
	+ `python3-wheel`
	+ `python3-setuptools`
	+ `python3-pip`
	+ `python3-cython`
	+ `gcc-g++`
	+ `make`
	+ `wget`

Rather than using pip to install qt5, install the following via Cygwin, with the first definitely being needed:

* `python3-pyqt5`
* `python3-pyqt5-qsci`
* `python3-pyqt5-qt3d`
* `python3-pyqt5-qtchart`
* `python3-pyqt5-qtdatavisualization`
* `python3-sip` - C++ to Python bindings, required by Qt5

The above installs into Cygwin.  Need to copy the PyQt5 and sip* files from /usr/lib/python3.6/site-packages to the virtualenv.

After activating the virtual environment with source bin/activate, running the gptest script gives:

```
Running the geoprocessor for Python3...
PYTHONPATH items:

/cygdrive/C/Users/sam/owf-dev/GeoProcessor/git-repos/owf-app-geoprocessor-python/build-util/virtualenv-tmp/gptest-1.0.0-cygwin-venv/lib/python36.zip
/cygdrive/C/Users/sam/owf-dev/GeoProcessor/git-repos/owf-app-geoprocessor-python/build-util/virtualenv-tmp/gptest-1.0.0-cygwin-venv/lib/python3.6
/cygdrive/C/Users/sam/owf-dev/GeoProcessor/git-repos/owf-app-geoprocessor-python/build-util/virtualenv-tmp/gptest-1.0.0-cygwin-venv/lib/python3.6/lib-dynload
/usr/lib/python3.6
/cygdrive/C/Users/sam/owf-dev/GeoProcessor/git-repos/owf-app-geoprocessor-python/build-util/virtualenv-tmp/gptest-1.0.0-cygwin-venv/lib/python3.6/site-packages
Initializing QApplication
QStandardPaths: XDG_RUNTIME_DIR not set, defaulting to '/tmp/runtime-sam'
qt.qpa.screen: QXcbConnection: Could not connect to display
Could not connect to any X display.
```

Need to start the Cygwin X-windows. Make sure to install the following from the Cygwin setup program:

* `xinit`

Then run the following from any Cygwin terminal:  `startxwin` or use the **Cygwin X / XWin Server*** from ***Start*** menu.

Set the DISPLAY:

```
export DISPLAY=:0.0
```

Then run `gptest --ui`.
