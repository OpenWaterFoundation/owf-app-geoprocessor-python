# GeoProcessor / New Developer #

This documentation explains how new developers can set up the development environment for
the GeoProcessor software.  The development environment should be set up as follows:

1. Install software:
	1. [Python](#install-python)
	2. [QGIS](#install-qgis)
	3. [PyCharm](#install-pycharm)
	4. [MkDocs](#install-mkdocs)
	5. [Git](#install-git)
	6. [Cygwin](#install-cygwin)
2. [Clone Repository and Configure Project](#clone-repository-and-configure-project)
3. [Develop software as per Development Tasks](dev-tasks)
4. [Update PyCharm to use New Python](#update-pycharm-to-use-new-python)

-----------------

## Install Python ##

Multiple versions of Python need to be installed, if not already installed.
Python versions are used as follows:

* Python 3.7 (or similar, depending on QGIS version)
installed with QGIS will be used to initialize the Pycharm virtual environment
to edit code and run the GeoProcessor in PyCharm.
It may also be used to initialize the virtual environment for deployment;
however, the QGIS Python environment is a bit nonstandard and therefore a normal Python install
is recommended for creating the Python virtual environment for testing framework deployment (see below).
* Python 3.7 (or similar, depending on QGIS version) is used to create a virtual environment
for the GeoProcessor testing framework, independent of QGIS Python version.
* Python 2 or 3 is used by MkDocs to process Markdown documentation into static websites (can use the above version).

See the following:

* [Development Environment / Python](../dev-env/python)

## Install QGIS ##

Install QGIS, which provides Python packages that are used by the GeoProccessor.
QGIS is distributed with a version of Python 3.
The QGIS Python and associated libraries are used by the deployed GeoProcessor.
GeoProcessor modules are installed in the `site-packages` folder of the GeoProcessor virtual environment and
are made known to the QGIS Python at runtime.
See the following:

* [Development Environment / QGIS](../dev-env/qgis)

## Install PyCharm ##

The PyCharm integrated development environment is used by OWF to develop the GeoProcessor and is recommended for development.
A PyCharm Python virtual environment is recommended for development to isolate from the system/user Python.
The Python virtual environment should use Python 3.x consistent with QGIS and as the base interpreter for the
PyCharm virtual environment.
The PyCharm Python virtual environment will be used to run the GeoProcessor in the development environment,
with QGIS libraries added via the `PYTHONPATH` environment variable in the PyCharm run script and `scripts` run scripts.
See the following:

* [Development Environment / PyCharm](../dev-env/pycharm)

## Install MkDocs ##

MkDocs is used to create user and developer documentation, each as separate static websites.
See the following:

* [Development Environment / MkDocs](../dev-env/mkdocs)

## Install Git ##

Git and GitHub are used for version control.
GeoProcessor contributors are expected to have reasonably good Git skills.

See the following:

* [Development Environment / Git](../dev-env/git)

## Install Cygwin ##

Cygwin provides a Linux-like environment on Windows that can be used to run the GeoProcessor testing framework.
A Cygwin-compatible Python virtual environment is created.
See the following:

* [Development Environment / Cygwin](../dev-env/cygwin)

## Clone Repository and Configure Project ##

The following steps illustrate how to clone and configure a PyCharm project.
These instructions are consistent with the project
[README](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python) file.

The GeoProcessor code project is maintained within a single GitHub repository.
Additional repositories are used for user documentation and functional tests.
This allows progress to occur in all areas, while only requiring Python expertise in the code project.

Once set up, scripts within the project will use relative paths (using `..`) or will refer to known absolute paths
by determining the folder that a script is run in and appending to that path.
The following folder structure is the recommended folder structure for organizing the GeoProcessor project.
Each of the folders under `git-repos` matches the name of a GitHub repository.

```text
C:\Users\user\owf-dev\                         Top-level development folder (Windows).
/home/user/owf-dev/                            Top-level development folder (Linux).
/cygdrive/C/Users/user/owf-dev/                Top-level development folder (Cygwin).
  GeoProcessor/                                Product folder.
    git-repos/                                 Git repositories for the GeoProcessor.
      owf-app-geoprocessor-arcpy/              Code repository for ArcGIS version (only if developing ArcGIS version).
      owf-app-geoprocessor-python/             Code repository.
      owf-app-geoprocessor-python-doc-user/    User documentation.
      owf-app-geoprocessor-python-test/        Functional tests.
      owf-util-git/                            Git utility scripts (under development).

```

To set up a new project:

1. Create a folder inclusive of the `git-repos` level.
2. Clone the main component repository into `git-repos`: `owf-app-geoprocessor-python`.
3. Run the `build-util/git-clone-all-gp.sh` script to clone the other repositories (if they don't already exist).

The `owf-app-geoprocessor-arcpy` project relies on Esri's ArcGIS Pro and is not needed for the QGIS GeoProcessor.
Additional information will be added later for the ArcGIS Pro version of the GeoProcessor.

### Start PyCharm ###

Once cloned, the following script can be used to start PyCharm Community Edition on Windows, or use a similar approach.
The script configures the Python environment to find QGIS libraries, which are needed by the GeoProcessor.
Other versions of this script may also be added over time.

```text
git-repos/owf-app-geoprocessor-python/build-util/run-pycharm-ce-for-qgis.bat
```

The script will detect the latest version of PyCharm that is installed.
This approach ensures that basic development environment configuration is as expected.

### Configure New Project ###

Once PyCharm is started, a new project can be configured.
This will rely on a Python virtual environment.

![Create project 1](images/create-project1.png)

Select ***Create New Project***.
Then select the folder that was cloned from GitHub, similar to the following.
Note that the `owf-app-geoprocessor-python` repository's `.gitignore` file indicates to ignore all PyCharm project files.
The user documentation and functional test repositories do not need to be known to PyCharm.
**The following image needs to be updated to use a Python 3.x base interpreter.
The QGIS Python version can be determined by checking folder names in the `C:\OSGeo4W64\apps` folder,
which will use `Python3x` for recent release and may include `Python27` for the long-term stable release
if installed.**

![Create project 2](images/create-project2.png)

PyCharm may display a warning:

![Create project 3](images/create-project3.png)

Press ***Yes***.
The project will be created/imported and the main PyCharm interface will be shown, with project files listed,
as shown in the following image.
Note that the project name in the upper left of the file listing matches the Git repository name.
Note also that PyCharm warns about no interpreter being defined.

![Create project 4](images/create-project4.png)

To add an interpreter, use the ***File / Settings*** menu and then ***Project: owf-app-geoprocessor-python / Project Interpreter***.
Indicate that a new environment should be used, which will create a virtual environment as shown in the following image.
Select a base interpreter that is Python 3.x consistent with QGIS Python version,
since that is what will be used in the deployed environment.
**The QGIS Python distribution is not a standard Python distribution folder structure so don't use it for the base interpreter.**
Pressing ***OK*** will copy needed files from the base interpreter to the virtual environment.
**The following image needs to be updated to indicate Python 3.x.**

![Create project 5](images/create-project5.png)

The environment is then ready for development.  Use the PyCharm startup script each time that PyCharm needs to be started for development.

## Update PyCharm to use New Python ##

It may be necessary to update the Python that is used in PyCharm,
for example if a new version of QGIS is installed.
In this case, a new virtual environment can be created and the project settings updated to use the new virtual environment.
Update the virtual environment as follows.

First start PyCharm for the GeoProcessor.
Then select the project settings in PyCharm with ***File / Settings***.
Then select the ***Project Interpreter*** item, as shown below.

![Update Python 1](images/update-pycharm-python1.png)

**Need to evaluate whether the warning shown at the bottom of the above dialog is significant.**
The `C:\OSGeo4W64\apps\Python37` and `C:\OSGeo4W64\apps\bin` folders do not include `pip3` by default.

Click on the gear icon in the upper right and select ***Show All...***, which will display the following.

![Update Python 2](images/update-pycharm-python2.png)

Clicking on the + icon in the upper right will show the following dialog to add a new Python interpreter.
In this case the error is due to QGIS having been updated to version 3.7 and the
`C:\OSGeo4W64\apps\Python36` folder no longer exists.

![Update Python 3](images/update-pycharm-python3.png)

To create a new virtual environment,
use the ***Base Interpreter ...*** button to select a new QGIS Python, for example select Python37 as shown below.

![Update Python 4](images/update-pycharm-python4.png)

Press ***OK*** to create the virtual environment in the folder shown above.
This may take a minute or two.
This will only copy the core Python executable programs and files, but not `site-packages` or other third-party packages.
Once the virtual environment is created, it will be listed in available ***Project Interpreters*** as shown in the following figure.

![Update Python 5](images/update-pycharm-python5.png)

Select the new virtual environment and press ***OK***.
The following dialog will be shown showing the installed packages.

![Update Python 5](images/update-pycharm-python6.png)

Press ***OK*** to confirm selection of the new Python virtual environment.
It may take a few minutes for the project to refresh using the new virtual environment.

To confirm which version of Python is running,
run the `geoprocessor/app/printenv.py` script in PyCharm (right click and run).
Output will be similar to the following.
Note that the Python being used is the virtual environment and that the `sys.path`
includes QGIS libraries using old-style 8.3 paths.
The Python path is defined in the `build-util/run-pycharm-ce-for-qgis.bat` file to run in Windows.

```
Python Properties:
    Python executable (.executable): C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python\venv-qgis-python37\Scripts\python.exe
    Python Version (sys.version): 3.7.0 (v3.7.0:1bf9cc5093, Jun 27 2018, 04:59:51) [MSC v.1914 64 bit (AMD64)]
    Python Path (sys.path):
        C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python
        C:\OSGEO4~2\apps\Python37\lib\site-packages
        C:\OSGEO4~2\apps\qgis\python
        C:\OSGEO4~2\apps\qgis\python\plugins
        C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python\venv-qgis-python37\Scripts\python37.zip
        C:\OSGEO4~2\apps\Python37\DLLs
        C:\OSGEO4~2\apps\Python37\lib
        C:\OSGeo4W64\apps\Python37
        C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python\venv-qgis-python37
        C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python\venv-qgis-python37\lib\site-packages
```
