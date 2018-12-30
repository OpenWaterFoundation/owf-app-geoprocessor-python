# GeoProcessor / Development Tasks / Version Control #

* [Git Utility Scripts](#git-utility-scripts)
* [Issues with File Permissions](#issues-with-file-permissions)

---------------------------------

## Git Utility Scripts ##

Git and GitHub are used for version control and software developers are expected to be proficient with Git.
A feature/topic branching model is used with the `master` branch being the main branch for deployment.
Tags and releases are created at major milestones.
The following `build-util` scripts are provided to facilitate Git use and can be run in Cygwin, Git Bash, and Linux:

* `git-check-gp.sh` - check all component repositories for local and remote status
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
PyCharm defaults create a new file and then copy over the source file when changes are saved.
Creating the new file results in the file permissions issues.
To prevent PyCharm from creating the temporary file, use the
***File / Settings / Appearance & Behavior / System Settings / Synchronization*** configuration editor and change the
***Use "safe write" (save changes to a temporary file first)***  setting to unchecked.

It may be necessary to use Cygwin command line to change file permissions to/from executable to compensate for permissions issues.
