# GeoProcessor / Development Tasks / Version Control #

* [Introduction](#introduction)
* [Developer Use of Git](#developer-use-of-git)
* [Git Utility Scripts](#git-utility-scripts)
* [Issues with File Permissions](#issues-with-file-permissions)

---------------------------------

## Introduction ##

Version control is important for any software project in order to track changes and
manage when milestone releases are made.
Version control for the GeoProcessor uses a feature/topic branch approach where
the `master` branch contains the main working code and feature/topic branches are used to fix bugs or add new features.
Currently, a `dev` branch parallel to `master` is not used.
[GitHub issues](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python/issues) are used to track bugs and feature requests.

Stable versions of the GeoProcessor are released by coordinating resolution of issues.
When a version is stable on the supported platforms,
all GeoProcessor repositories are tagged with a tag name like `GeoProcessor-1.1.0` and a release is made as a software installer.
In cases where bug fixes to a version are needed, a long-running branch might be created,
or an incremental version along the `master` may be created.

Once a relase is made, the version number is incremented in the `geoprocessor/app/version.py` file with a `dev` suffix such as `1.3.0dev`
and is retained until the next release is made, at which time the `dev` is removed.
The development version can be worked on as long as necessary.
Currently, no continuous/nightly build occurs, but this may be implemented at some point, with corresponding build number.

A more sophisticated versioning workflow may be adopted in the future but currently the team is small
and the workflow is correspondingly simple.
Users are steered towards stable version releases.

## Developer Use of Git ##

GeoProcessor software developers are assumed to be competent with Git and GitHub.
Developers should use tools that they feel comfortable with such a integrated PyCharm Git features,
command-line Git commands, and other tools.

Developers should help each other with Git issues such as merge conflicts and learning Git skills.
More sophisticated use of Git will be implemented as time allows and developer skills are enhanced.

## Git Utility Scripts ##

The following `build-util` scripts are provided in the main `owf-app-geoprocessor-python` repository
to facilitate Git use and can be run from Cygwin, Git Bash, and Linux command line.
These scripts are aware of the multiple repositories that comprise the GeoProcessor.

* `git-check-gp.sh` - check all component repositories for status, including whether need to pull, push, etc.
* `git-clone-all-gp.sh` - clone all repositories after main repository is cloned
* `git-tag-all-gp.sh` - tag all repositories with consistent tag name and commit message

## Issues with File Permissions ##

File permissions can be incorrect depending on how files are created.
Git stores a single file permission bit to indicate whether a file is executable.

It is useful to use the Cygwin environment for command line operations, including running the above scripts.
However, experience has shown that there are some technical issues that may need to be addressed.
Using Git Bash does not have such issues, but Git Bash may not properly set file permissions on scripts.

If PyCharm is run as a windows application, it can save files that when listed in Cygwin have executable
permissions even if the files are not executable.
This also happens when other Windows applications are used to create files, such as screen captures.
PyCharm configuration defaults create a new file and then copy over the source file when changes are saved.
Creating the new file results in the file permissions issues.
To prevent PyCharm from creating the temporary file, use the
***File / Settings / Appearance & Behavior / System Settings / Synchronization*** configuration editor and change the
***Use "safe write" (save changes to a temporary file first)***  setting to unchecked.

It may be necessary to use Cygwin command line to change file permissions to/from executable to compensate for permissions issues.

Developers that use only Windows development tools will not have the ability to set the execute
permissions on files and therefor shell scripts will not be executable.
Git Bash permissions should be OK as long as Cygwin is not mixed with Git Bash in the same repository.
