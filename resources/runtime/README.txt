GeoProcessor/README.txt
=======================

Introduction
------------

The GeoProcessor software is developed by the Open Water Foundation (OWF, http://openwaterfoundation.org).
The GeoProcessor automates spatial data processing, by leveraging QGIS installed on the computer.
It is recommended that standalone QGIS be used (not OSGeo4W installer) to allow multiple versions of
QGIS and the GeoProcessor to be installed over time.
The GeoProcessor is distributed in a Python virtual environment (venv).
See the following resources:

- GeoProcessor download page:  http://software.openwaterfoundation.org/geoprocessor/
- Latest user documentation:  http://software.openwaterfoundation.org/geoprocessor/latest/doc-user/
- Latest developer documenation:  http://software.openwaterfoundation.org/geoprocessor/latest/doc-dev/

Running the GeoProcessor on Windows
-----------------------------------

IT IS NOT NECESSARY TO ACTIVATE the VIRTUAL ENVIRONMENT!
In fact, the venv 'Scripts/activate.bat' Windows batch file and `Scripts/activate` Linux script
will by default have incorrect VIRTUAL_ENV set to the folder where the venv was created.
An improved GeoProcessor installation process will address this issue in the future but currently
it is not a problem because the venv does not need to be activated to run the GeoProcessor.

To run the GeoProcessor on Windows:

1. Open a Command Prompt window.
2. Change to the Scripts folder.
3. Run the user interface:  gpui.bat    (this just calls gp.bat -ui)
4. Or, run the command line interface:  gp.bat

Clicking on the gp.bat file in File Explorer will also run.
However, the command prompt window will disappear when complete,
which makes it more difficult to troubleshoot issues.

Software Files
--------------

The GeoProcessor is distributed in a Python virtual environment (venv) as a matter of convenience.
However, the venv is not fully used because of the integration with QGIS Python environment.

- The gp.bat batch file runs QGIS setup batch files and does additional setup.
- The batch file sets the PYTHONHOME environment variable to run the QGIS Python.
- The batch file sets the PYTHONPATH environment variable to find QGIS Python files.
  GeoProcessor and additional packages are installed in the venv Lib/site-packages folder,
  which is added to PYTHONPATH.
- The GeoProcessor-QGIS-Version.txt file indicates the QGIS version that is compatible with
  the GeoProcessor.

Consequently, the venv is a hybrid environment that allows the original QGIS to remain unmodified
while adding files for GeoProcessor.  This ensures that if other applications depend on QGIS,
its software files are intact.  This also allows the GeoProcessor to be installed outside of
system files and avoid the need for administrator privileges.
