# build-util #

This folder contains Windows batch files and Linux scripts used in the development/build environment.
Scripts and batch files typically can be run from any folder, but do use input and output files
that have fixed locations relative to the script being run.

## Script to Start PyCharm ###

*   `old-runners/` - old scripts to run PyCharm, will be deleted in the future
*   `run-pycharm-ce-for-qgis.bat` - Windows batch file to run PyCharm Community Edition (installed in default location)
    +   Will search for latest known release and run if found, cascading to older versions
    +   The batch file should be updated as new versions of PyCharm are released and used for development

## Scripts and Folders for Git Version Control ##

The following scripts, folders, and files are used during software development as code is written and tested.
Scripts can be run in Cygwin, Linux, and Windows Git Bash.

*   `git-check-gp.sh` - check Git/GitHub status of multiple product repositories, calls `git-util/git-check.sh`
*   `git-clone-all-gp.sh` - clone the full product's repositories after the `owf-app-geoprocessor-python`
    repository is cloned, calls `git-util/git-clone-all.sh`
*   `git-util/` - used by `git` scripts listed above
*   `product-repo-list.txt` - list of Git repositories that comprise the GeoProcessor product, used by above scripts

## Scripts to Build Installers ##

The following scripts can be run in sequence to create installers and upload to OWF's Amazon S3 software bucket.

*   Folders that support build process:
    +   `venv-tmp/` - used by scripts that build staging Python virtual environments (venv) for installers,
        ignored in Git repository so all sub-folders are also ignored
    +   `venv-tmp/gp-1.3.0.dev-win-qgis-3.10-venv` - example venv folder for specific software release

*   Cygwin and Linux: **These need to be reviewed and updated.**
    +   `1-create-gp-tar.sh` - Linux/Cygwin script to pull together files needed to create an installer
        -   Output is in the `build-tmp` folder
        -   Was previously used to distribute `tar.gz` file for `site-package` but the next script
            now builds a Python virtual environment using the files
    *   `2-create-gp-venv.sh` - Linux/Cygwin script to create a Python virtual environment from previous step's files
        +   the virtual environment is packaged as a `tar.gz` file specific for `gptest` (may add `gp later),
            operating system, and GeoProcessor version
    *   `2-update-gp-venv.sh` - Linux/Cygwin script to update the Python virtual environment from `1-create-gp-tar.sh`,
        used to copy source files into venv and also strip QGIS for gptest version
    *   `3-copy-gp-to-amazon-s3.sh` - Linux/Cygwin script to copy the virtual environment installer to OWF's Amazon S3 bucket
        for publishing on the [GeoProcessor downloads](http://software.openwaterfoundation.org/geoprocessor/) web page

*   Windows:
    +   No "1" script is used - source files are copied directly into the virtual environment.
    +   `2-create-gp-venv.bat` - batch file to create a Python virtual environment from development files
        -   the virtual environment is packaged as a `zip` file specific for GeoProcessor and QGIS version
    *   `2-update-gp-venv.bat` - batch file to update the Python virtual environment created `2-create-gp-venv.bat`,
        used to copy the latest source files into venv.  This does not create the venv or zip file.
    +   `3-copy-gp-to-amazon-s3.sh` - copy the current Windows GeoProcessor installer files to the Amazon S3 bucket and
        update the `index.html` page that lists avaailable downloads

## Scripts to Install the GeoProcessor ##

The following scripts are used to install the software.
They are packaged in the installer and the `download-gp.sh` script is provided
on the downloads page to download to help with the installation.

**These need to be reviewed and updated - previously focused on Linux.**

*   `install/download-gp.sh` - used with Cygwin and Linux to download and install from the software download site
*   `install/install-gp-venv.sh` - called from `download-gp.sh` to complete the software installation
