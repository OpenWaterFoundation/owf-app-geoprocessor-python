# GeoProcessor / Development Tasks / Creating Installer #

The GeoProcessor is not packaged via a `pip` or `pipenv` installer (or `apt-get` on Linux).
The deployment process uses a Python virtual environment.

The GeoProcessor software can then be installed as per the
[User Documentation](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/appendix-install/install/).

Installers are created for different operating systems:

* [Creating Installer for Cygwin](#creating-installer-for-cygwin)
* [Creating Installer for Linux](#creating-installer-for-linux)
* [Creating Installer for Windows](#creating-installer-for-windows)

---------------

### ![Cygwin](../images/cygwin-32.png) Creating Installer for Cygwin ###

The Cygwin installer currently focuses on the testing framework.
A Cygwin deployment is useful for testing the GeoProcessor testing framework prior to testing the Linux installer.

The Cygwin environment must have been properly configured as per the [Development Environment / Cygwin](../dev-env/cygwin.md) documentation.
A Python virtual environment is created in the development environment.
The following steps are executed:

1. Run `build-util/1-create-gp-tar.sh` to create `tar.gz` and `.zip` files that contain the `site-packages` files.
	1. This creates temporary folders in `build-util/build-tmp` containing the Python files, for example:
		1. `build-util/build-tmp/tmp-gp-1.1.0` contains the needed GeoProcessor files
		2. `build-util/build-tmp/gp-1.1.0-site-package.tar.gz contains the site `geoview` package for the GeoProcessor
		3. similarly, `gptest` files are created
	2. The testing framework version (`gptest`) has QGIS references stripped from the code.
2. Run `build-util/2-create-gp-venv.sh` to create a Python virtual environment.
	1. This creates a virtual environment from the files in the previous step, for example:
		1. `build-util/venv-tmp/gptest-1.1.0-cyg-venv` contains the virtual environment for
		testing framework version 1.1.0 for Cygwin
		2. `build-util/venv-tmp/gptest-1.1.0-cyg-venv.tar.gz` is the installer that can be deployed to a Cygwin environment
	2. Necessary components are also installed using `pip`.
3. More frequently, when code or other source files are edited and need to be tested in Cygwin, run `build-util/2-update-gp-venv.sh` to
	run step 1 and parts of step 2 that copy source code and scripts to the virtual environment
4. Run the `build-util/venv-tmp/gptest-1.1.0-cyg-venv/scripts/gptest` or `scripts/gptestui` script in the virtual environment to run the GeoProcessor.
	1. The scripts will configure the X-Window environment as needed
	2. The scripts also activate the Python virtual environment if necessary
5. Run tests with the GeoProcessor software to confirm functionality.
6. Upload the installer to the [OWF GeoProcessor Download page](http://software.openwaterfoundation.org/geoprocessor/)
by running the `build-util/3-copy-gp-to-amazon-s3.sh`.
	1. The `build-util/install/download-gp.sh` script is uploaded to the download site.
	2. The `build-util/install/install-gp-venv.sh` script is called by the above to install after downloading
	3. The files on the download site are updated to reflect the current list of downloadable products

### ![Linux](../images/linux-32.png) Creating Installer for Linux ###

1. Run `build-util/1-create-gp-tar.sh` to create `tar.gz` and `.zip` files that contain the `site-packages` files.
	1. This creates temporary folders in `build-util/build-tmp` containing the Python files, for example:
		1. `build-util/build-tmp/tmp-gp-1.1.0` contains the needed GeoProcessor files
		2. `build-util/build-tmp/gp-1.1.0-site-package.tar.gz contains the site `geoview` package for the GeoProcessor
		3. similarly, `gptest` files are created
	2. The testing framework version (`gptest`) has QGIS references stripped from the code.
2. Run `build-util/2-create-gp-venv.sh` to create a Python virtual environment.
	1. This creates a virtual environment from the files in the previous step, for example:
		1. `build-util/venv-tmp/gptest-1.1.0-lin-venv` contains the virtual environment for
		testing framework version 1.1.0 for Linux
		2. `build-util/venv-tmp/gptest-1.1.0-lin-venv.tar.gz` is the installer that can be deployed to a Linux environment
	2. Necessary components are also installed using `pip`.
3. More frequently, when code or other source files are edited and need to be tested in Linux, run `build-util/2-update-gp-venv.sh` to
	run step 1 and parts of step 2 that copy source code and scripts to the virtual environment
4. Run the `build-util/venv-tmp/gptest-1.1.0-lin-venv/scripts/gptest` or `scripts/gptestui` script in the virtual environment to run the GeoProcessor.
	1. The scripts will configure the X-Window environment as needed
	2. The scripts also activate the Python virtual environment if necessary
5. Run tests with the GeoProcessor software to confirm functionality.
6. Upload the installer to the [OWF GeoProcessor Download page](http://software.openwaterfoundation.org/geoprocessor/)
by running the `build-util/3-copy-gp-to-amazon-s3.sh`.
	1. The `build-util/install/download-gp.sh` script is uploaded to the download site.
	2. The `build-util/install/install-gp-venv.sh` script is called by the above to install after downloading
	3. The files on the download site are updated to reflect the current list of downloadable products

### ![Windows](../images/windows-32.png) Creating Installer for Windows ###

The installer for Windows packages the development files without modification
and is primarily targeted to the full QGIS distribution (`gp` rather than `gptest`).

1. Do development within PyCharm as normal.
2. Periodically, test within a Python Virtual environment.
Run `build-util/2-create-gp-venv.bat` to create a Python virtual environment.
	1. This creates a virtual environment from the development files, for example:
		1. `build-util/venv-tmp/gp-1.1.0-win-venv` contains the virtual environment for
		GeoProcessor for Windows.
		2. `build-util/venv-tmp/gp-1.1.0-win-venv.zip` can be unzipped in a Windows environment.
		3. Currently the virtual environment only provides a folder structure for `Lib\site-packages` and
		`Scripts`, for `gp.bat` and `gpui.bat`.  However, in the future, the `gptest` scripts may be implemented
		and use the distributed Python virtual environment.
	2. Necessary components such as `pandas` are also installed using `pip3` to augment the packages
	that are distributed with QGIS.
3. More frequently, when code or other source files are edited and need to be tested in Linux, run `build-util/2-update-gp-venv.bat` to
	copy source code and scripts to the virtual environment without recreating the virtual environment.
	This script **does not** re-create the zip file, which is needed to upload to the GeoProcessor downloads page.
	Run the `2-create-gp-venv.bat` batch file to create the installer for deployment.
4. Run the `build-util/venv-tmp/gp-1.1.0-win-venv/scripts/gp` or `scripts/gpui` script in the virtual environment to run the GeoProcessor.
	1. The scripts will configure the QGIS environment and also make Python aware of the GeoProcessor files in the virtual environment.
	2. The scripts do not currently need to activate the virtual environment (but may enable later to run `gptest` independent
	of QGIS).  Currently the scripts will detect a QGIS standalone or OSGeo4W Python install and set the `PYTHONPATH`
	to find the GeoProcessor packages and other necessary packages (beyond what QGIS is distributed with).
	A virtual environment approach is being used to prepare for `gptest` distribution and to isolate
	GeoProcessor files from the QGIS runtime files.
5. Run tests with the GeoProcessor software to confirm functionality.
6. Upload the installer to the [OWF GeoProcessor Download page](http://software.openwaterfoundation.org/geoprocessor/).
	1. Run the `build-util/3-copy-gp-win-to-amazon-s3.sh` batch file to upload the latest Windows installer.
	2. Run the `build-util/3-copy-gp-to-amazon-s3.sh` script to upload a Cygwin/Linux version and update the
	catalog file - this is necessary because the script above does not create the catalog file or `index.html` file.
	This script, when run on Cygwin, will also update the Windows installer zip file.
	Therefore, prepare the Windows installer file first and then process the Cygwin installer.
7. Test the installer.  Download the Windows installer from the
	[GeoProcessor Downloads](http://software.openwaterfoundation.org/geoprocessor/) page.
	1. Then run the `Scripts\gp.bat` or `Scripts\gpui.bat` batch file.
	Again, this does not currently use the virtual environment packaged in the zip file but will in the future.
