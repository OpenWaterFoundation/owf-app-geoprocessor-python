# build-util #

This folder contains Windows batch files and Linux scripts used in the development/build environment.
Some scripts require running from the `build-util` folder from a
Windows command prompt window (if .bat file) or Cygwin/Git Bash/Windows Bash/Linux command shell (if .sh file).
However, updates are occurring to allow the scripts to run from any folder.

## Scripts and Folders used During Software Development ##

The following scripts, folders, and files are used during software development as code is written and tested.

* `build-util/` - used by [Scripts to Build Installers](#scripts-to-build-installers), ignored in Git repository
* `git-check-gp.sh` - check Git/GitHub status of multiple product repositories, calls `git-util/git-check.sh`
* `git-clone-all-gp.sh` - clone the full product's repositories after the `owf-app-geoprocessor-python`
repository is cloned, calls `git-util/git-clone-all.sh`
* `git-util/` - used by `git` scripts listed above
* `install/` - used by [Scripts to Install the GeoProcessor](#scripts-to-install-the-geoprocessor)
* `old-runners/` - old scripts to run PyCharm, in case anyone is using older PyCharm version
* `product-repo-list.txt` - list of Git repositories that comprise the GeoProcessor product
* `run-pycharm*.bat` - Windows batch file(s) to start PyCharm Community Edition (installed in standard location)
	+ Batch files are updated as new versions of PyCharm are released and used for development
* `venv-tmp/` - used by [Scripts to Build Installers](#scripts-to-build-installers), ignored in Git repository

## Scripts to Build Installers ##

The following scripts can be run in sequence to create installers and upload to OWF's Amazon S3 software bucket.

* `1-create-gp-tar.sh` - Linux/Cygwin script to pull together files needed to create an installer
	+ Output is in the `build-tmp` folder
	+ Was previously used to distribute `tar.gz` file for `site-package` but the next script
	now builds a Python virtual environment using the files
* `2-create-gp-venv.bat` - Windows batch file to create a Python virtual environment from development files
	+ the virtual environment is packaged as a `zip` file specific for `gp` (may add `gptest` later)
	and GeoProcessor version - Python venv is included but not currently used
* `2-create-gp-venv.sh` - Linux/Cygwin script to create a Python virtual environment from previous step's files
	+ the virtual environment is packaged as a `tar.gz` file specific for `gptest` (may add `gp later),
	operating system, and GeoProcessor version
* `2-update-gp-venv.sh` - Linux/Cygwin script to update the Python virtual environment from `1-create-gp-tar.sh`,
used to copy source files into venv and also strip QGIS for gptest version
* `3-copy-gp-to-amazon-s3.sh` - Linux/Cygwin script to copy the virtual environment installer to OWF's Amazon S3 bucket
for publishing on the [GeoProcessor downloads](http://software.openwaterfoundation.org/geoprocessor/) web page

## Scripts to Install the GeoProcessor ##

The following scripts are used to install the software.
They are packaged in the installer and the `download-gp.sh` script is provided
on the downloads page to download to help with the installation.

* `install/download-gp.sh` - run to download and install the GeoProcessor
* `install-gp-venv.sh` - called by `download-gp.sh`, installs the software after it is downloaded
