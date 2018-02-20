# owf-app-geoprocessor-python #

This repository contains the source code and developer documentation for the
[Open Water Foundation (OWF)](http://openwaterfoundation.org) GeoProcessor software.
The GeoProcessor is Python software that leverages [QGIS](https://www.qgis.org) modules to provide
features to automate processing geospatial data.

See the following online user and developer documentation:

* [Learn OWF GeoProcessor](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/)
* [Learn OWF GeoProcessor (for Developers)](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-dev/)

The following sections provide a summary of the project repository and getting started:

* [GeoProcessor Repository Folder Structure](#geoprocessor-repository-folder-structure)
* [Development Environment](#development-environment)
* [Git Workflow](#git-workflow)
* [Testing](#testing)
* [Contributing](#contributing)
* [License](#license)
* [Maintainers](#maintainers)
* [Contributors](#contributors)
* [Release Notes](#release-notes)

-----

## GeoProcessor Repository Folder Structure ##

The following folder structure is recommended for GeoProcessor development.
Top-level folders should be created as necessary.
The following folder structure clearly separates user files (as per operating system),
development area (`owf-dev`),
product (`GeoProcessor`), repositories for the product (`git-repos`),
and specific repositories for the product.

```text
C:\Users\user\                                   User's home folder, Windows style.
/c/Users/user/                                   User's home folder, Git Bash style.
/cygdrive/C/Users/user/                          User's home folder, Cygwin style.
/home/user/                                      User's home folder, Linux style.
  owf-dev/                                       Work done on Open Water Foundation projects.
    GeoProcessor/                                GeoProcessor product.
      git-repos/                                 Git repositories for the GeoProcessor.
        owf-app-geoprocessor-python/             The GeoProcessor code and documentation repository.
        owf-app-geoprocessor-python-doc-user/    The user documentation repository.
        owf-app-geoprocessor-python-test/        The functional test repository.
        owf-util-git/                            Git utility scripts repository.

```

Separate repositories have been created for user documentation and functional tests to facilitate contributions by non-programmers.
The [owf-util-git](https://github.com/OpenWaterFoundation/owf-util-git) utilities are being developed
to facilitate use of Git, in particular more complex tasks such as diffs and merges.

The following summarizes the folder structure for this (owf-app-geoprocessor-python) repository,
in this case showing [PyCharm Community Edition IDE](https://www.jetbrains.com/pycharm/download) files.
OWF uses PyCharm for development and configures the repository to ignore PyCharm files.
Other developers can use a different Python development environment tool.
Everything shown will be automatically created when the repository is cloned
or when PyCharm is used.

```text
owf-app-geoprocessor-python/       The GeoProcessor code and documentation repository.
  .git/                            Standard Git software folder for repository files (DO NOT TOUCH!).
  .gitattributes/                  Standard Git configuration file for repository (for portability).
  .gitignore/                      Standard Git configuration file to ignore dynamic working files.
  .idea/                           PyCharm project files (ignored using .gitignore).
  build-util/                      Scripts to help in the GeoProcessor development environment.
  doc-dev-mkdocs-project/          MkDocs project for developer documentation.
    build-util/                    Scripts to help with MkDocs project.
  geoprocessor/                    Main module folder for GeoProcessor.
    app/                           Main GeoProcessor application module.
    commands/                      Modules containing GeoProcessor commands.
    core/                          Core GeoProcessor module, containing the processor.
    util/                          Utility modules.
  LICENSE.txt                      GeoProcessor license (being determined).
  README.md                        This README file.
  scripts/                         Scripts for the deployed application.
  venv/                            Virtual environment used by PyCharm (ignored using .gitignore).
```

## Development Environment ##

The development environment consists of QGIS (Python 2 version, and Python is included with QGIS),
Python 2 (normal install, used with MkDocs documentation and as needed), PyCharm Community Edition,
and Git client such as Git for Windows.

* See the published [GeoProcessor Developer Documentation](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-dev/)
(also can view within this project in the `doc-dev-mkdocs-project` folder).

## Git Workflow ##

OWF uses a "feature branching Git workflow" for this project, as illustrated in the following resources.
The `master` branch contains the most current commits, with functionality tested before committing.
Releases will be indicated with tags and release branches as needed.

* [Jeremy Helms "Branching" gist, with diagram](https://gist.github.com/digitaljhelms/4287848)
* [Git Feature Branch Workflow documentation on Atlassian](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow)

A small number of committers are responsible for maintaining the integrity of the master branch.

## Testing ##

Unit testing of module functions has not been a major focus yet but will be implemented using pytest,
consistent with normal Python conventions.

The GeoProcessor contains an internal functional testing framework described in the following resources:

* [Developer documentation for testing tasks](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-dev/dev-tasks/#testing)
* [owf-app-geoprocessor-python-test functional tests repository](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test)

## Contributing ##

Contributions to this project can be submitted using the following options:

1. GeoProcessor software developers with commit privileges can write to this repository
as per normal development Git workflow protocols.
2. Post an issue on GitHub with suggested change (preferred for small changes).
3. Email a maintainer (OK for collaboration but other options are preferred).
4. Fork the repository, make changes, and do a pull request (preferred for large changes).
Contents of the current master branch should be merged with the fork to minimize
code review before committing the pull request.

## License ##

A license for the software is being determined.

## Maintainers ##

The lead developers/maintainers for the GeoProcessor are OWF staff:

* Steve Malers, Open Water Foundation, [steve.malers@openwaterfoundation.org](mailto:steve.malers@openwaterfoundation.org), @smalers
* Emma Giles, Open Water Foundation, [emma.giles@openwaterfoundation.org](mailto:emma.giles@openwaterfoundation.org), @egiles16

## Contributors ##

* Steve Malers, Open Water Foundation (@smalers)
* Emma Giles, Open Water Foundation (@egiles16)

## Release Notes ##

The software is currently in pre-release development mode.
Release notes listing GitHub issues will be added.
