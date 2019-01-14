# GeoProcessor / Development Environment / Folders #

GeoProcessor developer occurs in a folder structure that is consistent between software developers.
This ensures that scripts used to perform development tasks work for all developers.

* [Development Environment Folders](#development-environment-folders)
* [Developer Preferences](#developer-preferences)
* [Troubleshooting](#troubleshooting)
	+ [Spaces in Paths](#spaces-in-paths)
	+ [Paths Longer than 127 Characters](#paths-longer-than-127-characters)

----------------

## Development Environment Folders ##

The following is the recommended folder structure for the GeoProcessor development environment.
The primary development environment is currently Windows 10.
Secondary testing occurs on Cygwin and is primarily focused on the `gptest` testing framework.
Development typically occurs mostly in Windows 10, followed by testing framework (`gptest`) testing on Cygwin,
and finally additional testing and enhancement in a full Linux environment.
Additional environments for development and testing will be added over time.

```text
C:\Users\user\owf-dev\                         Top-level development folder (Windows).
/home/user/owf-dev/                            Top-level development folder (Linux).
/cygdrive/C/Users/user/owf-dev/                Top-level development folder (Cygwin).
  GeoProcessor or GP/                          Product folder (see note below).
    git-repos/                                 Git repositories for the GeoProcessor.
      owf-app-geoprocessor-arcpy/              Code repository for ArcGIS version (only if developing ArcGIS version).
      owf-app-geoprocessor-python/             Code repository.
      owf-app-geoprocessor-python-doc-user/    User documentation.
      owf-app-geoprocessor-python-test/        Functional tests.
      owf-util-git/                            Optional git utility scripts.

```

## Developer Preferences ##

Software developers each have their own preferences for organizing software project folders.
The folder structure indicated in the previous section has some flexibility.
The folder `git-repos` is required in some form and must contain all the repository folders used by the GeoProcessor development tools.
This allows scripts and configuration to navigate files.
The folder does not necessary need to be called `git-repos`
but this is a convention that has been adopted across multiple Open Water Foundation software projects.

The folders below `git-repos` are defined in the repositories and cannot change because doing so would cause
conflicting commits in the repository.
Dynamic folders and files in the working files, such as virtual environments used to build and test
the software could be named differently but this would require enhancements to the build process.

The folders above `git-repos` can be named according to developer preferences.
The documentation describes a convention that has been implemented by GeoProcessor developers and
is shown in this documentation.
Long paths can result in problems (see the [Troubleshooting section](#troubleshooting) for more information).

## Troubleshooting ##

The folder structure generally does have any significant issues and can accommodate the preferences of different software developers.
The following are known issues (or potential issues).

### Spaces in Paths ###

Spaces in paths can be problematic and are generally avoided in the GeoProcessor development environment.
Spaces in folder and file names make it more difficult to navigate because sometimes spaces have to be escaped
on the command line with backslashes or surrounded in quotes.

On Windows, one place where spaces occur is in `C:\Program Files`, which is the installation location for standalone QGIS
and other tools needed in the development environment.
This folder is generally handled well without issues.

Underlying configuration information, such as environment variables, is sometimes specified with
[old-style 8.3 folder and filenames](https://en.wikipedia.org/wiki/8.3_filename),
presumably to deal with spaces and other issues.
For example, QGIS configuration when working in the OSGeo4W installation
will result in an environment variable using 8.3 convention, similar to `QGIS_PREFIX_PATH=C:\OSGEO4~2\apps\qgis`.

### Paths Longer than 127 Characters ###

The GeoProcessor is distributed as a virtual environment on Cygwin and Linux.
Scripts within the virtual environment, and Python itself, are configured by modifying the hashbang (`#!`) line
at the start of scripts, which tells the operating system how to run the script.
See the [hashbang/shebang article on Wikipedia](https://en.wikipedia.org/wiki/Shebang_(Unix)).
On Linux, there is a 127 character limit on the hashbang line.
Depending on the developer's environment, this limit may be reached and the overall path to the virtual environment files will need to be shorted.
One way to shorten the path is to use a shorter "product" folder.
For example, shorten `GeoProcessor` to `GP`.
This issue will be monitored to make sure that the recommended folder structure for GeoProcessor development environment is not an issue.

The path length issue will be discovered in specific cases.
For example, running the `build-util/2-create-gp-venv.sh` script on Linux will have issues because `pip` may not work
in the newly created virtual environment.
In this case, top-level folders in the development environment can be renamed (moved) with no issue as long
as processes are not using those files.
Scripts determine the installation folder when run.
However, after renaming a folder, it may be necessary to close some windows that have been configured by a script with old paths.
