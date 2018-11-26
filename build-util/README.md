# build-util #

This folder contains Windows batch files and Linux scripts used in the development/build environment.
These scripts should generally be run from within the `build-util` folder from a
Windows command prompt window (if .bat file) or Cygwin/Git Bash/Windows Bash/Linux command shell (if .sh file).

* `1-create-gp-tar.sh` - Linux/Cygwin script to create tar.gz installer files for the geoprocessor
	+ Output is in the `build-tmp` folder
* `2-create-gp-venv.sh` - Linux/Cygwin script to a Python virtual environment from previous step tar.gz file
* `3-install-gp-venv-for-user.sh` - Linux/Cygwin script to install virtual environment from previous step
to user-specified installation folder, for use in production environment
* `git-check-gp.sh` - check Git/GitHub status of multiple product repositories
* `git-clone-all-gp.sh` - clone the full product's repositories after the `owf-app-geoprocessor-python`
repository is cloned
* `run-pycharm*.bat` - Windows batch file(s) to start PyCharm Community Edition (installed in standard location)
	+ Batch files are updated as new versions of PyCharm are released and used for development
