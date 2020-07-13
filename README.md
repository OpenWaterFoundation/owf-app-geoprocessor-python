# owf-app-geoprocessor-python #

This repository contains the source code for the
[Open Water Foundation (OWF)](http://openwaterfoundation.org) GeoProcessor software.
The GeoProcessor is Python software that leverages [QGIS](https://www.qgis.org) Python packages to provide
features to automate processing geospatial data.

See the following online user and developer documentation:

* [OWF GeoProcessor](http://software.openwaterfoundation.org/geoprocessor/) - download page (with links to versioned software and documentation)
* [Latest GeoProcessor user documentation](http://software.openwaterfoundation.org/geoprocessor/latest/doc-user/) - latest user documentation
* [Latest GeoProcessor developer documentation)](http://software.openwaterfoundation.org/geoprocessor/latest/doc-dev/) - latest developer documentation

The following sections provide a summary of the project repository and getting started:

* [GeoProcessor Repository Folder Structure](#geoprocessor-repository-folder-structure)
* [Links to GeoProcessor Repositories and Online Resources](#links-to-geoprocessor-repositories-and-online-resources)
* [Development Environment](#development-environment)
* [Git Workflow](#git-workflow)
* [Testing](#testing)
* [Contributing](#contributing)
* [License](#license)
* [Maintainers](#maintainers)
* [Release Notes](#release-notes)

-----

## GeoProcessor Repository Folder Structure ##

The following folder structure is recommended for GeoProcessor development.
Top-level folders should be created as necessary.
The following folder structure clearly separates user files,
development area (`owf-dev/`),
product (`GeoProcessor/`), repositories for the product (`git-repos/`),
and specific repositories for the product (`owf-dev-geoprocessor-*/`).

```text
C:\Users\user\                                   User's home folder for Windows.
/c/Users/user/                                   User's home folder for Git Bash.
/cygdrive/C/Users/user/                          User's home folder for Cygwin.
/home/user/                                      User's home folder for Linux.
  owf-dev/                                       Work done on Open Water Foundation products.
    GeoProcessor/                                GeoProcessor product.
      git-repos/                                 Git repositories for the GeoProcessor.
        owf-app-geoprocessor-python/             GeoProcessor code repository.
        owf-app-geoprocessor-python-doc-dev/     GeoProcessor user documentation repository.
        owf-app-geoprocessor-python-doc-user/    GeoProcessor developer documentation repository.
        owf-app-geoprocessor-python-test/        Functional test repository (GeoProcessor command files).
```

Separate repositories have been created for documentation and functional tests to
limit each repository's size and complexity and to facilitate contributions by different people.
The [owf-util-git](https://github.com/OpenWaterFoundation/owf-util-git) utilities are being developed
to facilitate use of Git and useful scripts are copied into `build-util/git-util` (see below).

The following summarizes the folder structure for this (`owf-app-geoprocessor-python`) repository.
OWF uses [PyCharm Community Edition IDE](https://www.jetbrains.com/pycharm/download) for development
and configures the repository to ignore PyCharm files, which can be configured for a new developer.
Other developers can use a different Python development environment tool;
however, OWF may not have resources to troubleshoot.
Folders and files in repositories will be automatically created when the repository is cloned
or when PyCharm is used.

```text
owf-app-geoprocessor-python/       The GeoProcessor code and documentation repository.
  .git/                            Standard Git folder for repository files (DO NOT TOUCH!).
  .gitattributes/                  Standard Git configuration file for repository (for portability).
  .gitignore/                      Standard Git configuration file to ignore dynamic working files.
  .idea/                           PyCharm project files (ignored using .gitignore).
  build-util/                      Scripts to help in the GeoProcessor development environment.
  geoprocessor/                    Main module folder for GeoProcessor software.
    app/                           Main GeoProcessor application module.
    commands/                      Modules containing GeoProcessor commands.
    core/                          Core GeoProcessor module, containing the processor.
    resources/                     Resources that support the softare.
      images/                      Images including icons that should be distributed at runtime.
      notices/                     License notices to be inserted into code files.
      qt-stylesheets/              Qt stylesheets that customize the UI, to be distributed.
    ui/                            User interface modules, using Qt.
    util/                          Utility modules.
  LICENSE.md                       GeoProcessor license (GPL v3).
  README.md                        This README file.
  scripts/                         Scripts to run GeoProcesssor in the development and tdeployed environments.
  venv/                            Virtual environments used by PyCharm (ignored using .gitignore).
    venv-qgis-3.10-python37/       Example virtual environment used for development.
  venv-qgis-python37/              Virtual environment used by PyCharm (ignored using .gitignore),
                                   old convention that is being phased out.
  z-local-notes/                   Use for local files that won't be committed to the repository.
```

## Links to GeoProcessor Repositories and Online Resources ##

The following are resources related to the GeoProcessor project,
listed by repository, with links to source and deployed versions.

| **Repository**                                       | **Description** | **Deployed Copy** |
| ---------------------------------------------------- | --------------- | ----------------- |
| `owf-app-geoprocessor-python` (this repository)      | GeoProcessor code. | [GeoProcessor Downloads ](http://software.openwaterfoundation.org/geoprocessor/) |
| [`owf-app-geoprocessor-python-doc-dev`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-doc-dev) | GeoProcessor developer documentation. | [GeoProcessor Developer Documentation ](http://software.openwaterfoundation.org/geoprocessor/latest/doc-dev/) |
| [`owf-app-geoprocessor-python-doc-user`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-doc-user) | GeoProcessor user documentation. | [GeoProcessor User Documentation ](http://software.openwaterfoundation.org/geoprocessor/latest/doc-user/) |
| [`owf-app-geoprocessor-python-test`](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test) | GeoProcessor automated tests. | Download from repository using clone or download zip file from GitHub website. |

## Development Environment ##

The development environment consists of the following.
OWF has developed the GeoProcessor on Windows using Cygwin but other development environments will be supported
as resources allow.

* QGIS (Python 3 version - Python is included with QGIS) - recent version is supported, as resources allow
* Python 3 (used with MkDocs documentation) - compatible with QGIS Python version
* PyCharm Community Edition - latest version if possible
* Git client such as Git for Windows - latest version for operating system

See the published [GeoProcessor Developer Documentation](http://software.openwaterfoundation.org/geoprocessor/latest/doc-dev/).

## Git Workflow ##

OWF uses a "feature branching Git workflow" for this project, as illustrated in the following resources.
The `master` branch contains the most current commits, with functionality tested before committing,
but should not be considered bulletproof.
Periodic releases are made and are indicated by tags on the master branch.

* [Jeremy Helms "Branching" gist, with diagram](https://gist.github.com/digitaljhelms/4287848)
* [Git Feature Branch Workflow documentation on Atlassian](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow)

A small number of committers are responsible for maintaining the integrity of the master branch.

A more complex workflow with development branch may be implemented in the future.
However, the focus at OWF is not on supporting a large open source development effort but instead to
provide a useful product to software users.

## Testing ##

Unit testing of module functions has not been a major focus yet but will be implemented using pytest,
consistent with normal Python conventions.

The GeoProcessor contains an internal functional testing framework described in the following resources:

* [Developer documentation for testing tasks](http://software.openwaterfoundation.org/geoprocessor/latest/doc-dev/dev-tasks/dev-tasks/#testing)
* [owf-app-geoprocessor-python-test functional tests repository](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test)

## Contributing ##

Contributions to this project can be submitted using the following options.

1. GeoProcessor software developers with commit privileges can write to this repository
as per normal development Git workflow protocols.
2. Post an issue on GitHub with suggested change (preferred for small changes).
3. Fork the repository, make changes, and do a pull request (preferred for large changes).
Contents of the current master branch should be merged with the fork to minimize
code review before committing the pull request.
OWF developers will review suggestions and implement by whatever means makes sense.

## License ##

The GeoProcessor is licensed under the GPL v3+ license.  See the [GPL v3 license](LICENSE.md).

## Maintainers ##

OWF staff are the lead developers/maintainers for the GeoProcessor.

## Release Notes ##

See the [User Documentation Release Notes](http://software.openwaterfoundation.org/geoprocessor/doc-user/latest/appendix-release-notes/release-notes/).
