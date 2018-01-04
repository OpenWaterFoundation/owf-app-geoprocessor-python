# doc-dev-mkdocs-project #

This folder contains a MkDocs project for the GeoProcessor developer documentation.
It is expected that the documentation will be updated by GeoProcessor software developers,
which is a relatively small number of people.

See the deployed documentation for developers (this documentation):  [OWF / Learn GeoProcessor (for developers)](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-dev/).

See also the deployed documentation for users:  [OWF / Learn GeoProcessor](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/).
The user documentation is maintained as a separate repository with the hope that a larger
community of people will contribute content because they are GeoProcessor users but not necessarily Python/GIS developers.
Therefore, the user documentation repository can be cloned without cloning the GeoProcessor code repository.

## GeoProcessor Software ##

The OWF GeoProcessor software is a Python application and supporting modules that runs [QGIS](https://qgis.org) Python modules
and other code to process spatial data.  The OWF GeoProcessor is under development and is being tested internally at OWF,
with the expectation that it will be released publicly as an open source project in the first half of 2018.
Documentation and tests are being provided in public repositories to evaluate opportunities to use on projects.
The OWF GeoProcessor is designed to provide the following functionality:

1. Command-based workflow language similar to [TSTool Software](http://openwaterfoundation.org/software-tools/tstool),
but focusing on processing spatial data layers.
2. General commands similar to TSTool, such as file manipulation, logic controls such as `For` and `If` commands,
and support for processor properties to allow dynamic scripting.
3. Spatial data processing commands for basic operations such as clipping, joining, format conversion,
and coordinate system conversion.
	1. Leverage QGIS functionality.
	2. Commands beyond what QGIS provides.
3. Built-in test framework, which is used to run functional tests, suitable for software developers and also
non-programmers who want to validate processing workflows.
4. Multiple run modes including batch, command shell interpreter, user interface, HTTP server.
5. Integration with other tools to leverage the strengths of those tools.

The goal is to allow software users to install QGIS, install the OWF GeoProcessor software,
and begin automating simple to complex geoprocessing tasks.
The approach also facilitates maintaining geoprocessing workflow in text files that can be
maintained under version control, such as on GitHub.

## Repository Contents ##

The repository for developer documentation is part of the full GeoProcessor code repository and contains the following folders.
Note that this folder structure is slightly different that the user documentation,
which exists in its own [GitHub repository
(owf-app-geoprocessor-python-doc-user)](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-doc-user).

```text
build-util/         Useful scripts to view, build, and deploy documentation.
mkdocs.yml          MkDocs configuration file for website.
docs/               Folder containing source Markdown and other files for website.
site/               Folder created by MkDocs containing the static website - ignored using .gitignore.

```

## Development Environment ##

The development environment for developer documentation requires installation of Python, MkDocs, and Material MkDocs theme.
**Python 2 has been used for documentation development, although the Python used for MkDocs documentation
is the general version installed on the computer, rather than the QGIS version used with the GeoProcessor.**
See the [OWF / Learn MkDocs](http://learn.openwaterfoundation.org/owf-learn-mkdocs/)
documentation for information about installing these tools.

The development environment will change as the developers upgrade to newer versions of software tools.

## Editing and Viewing Content ##

If the development environment is properly configured, edit and view content as follows:

1. Edit content in the `docs` folder and update `mkdocs.yml` as appropriate.
2. Run the `build-util/run-mkdocs-serve-8000.sh` script (Linux) or equivalent.
3. View content in a web browser using URL `http://localhost:8000`.

## Style Guide ##

The following are general style guide recommendations for this documentation,
with the goal of keeping formatting simple in favor of focusing on useful content:

* Use the Material MkDocs theme - it looks nice, provides good navigation features, and enables search.
* Follow MkDocs Markdown standards - use extensions beyond basic Markdown when useful.
* Show files and program names as `code (tick-surrounded)` formatting.
* Where a source file can be linked to in GitHub, provide a link so that the most current file can be viewed.
* Use triple-tick formatting for code blocks, with language specifier.
* Use ***bold italics*** when referencing UI components such as menus.
* Use slashes to indicate ***Menu / SubMenu***.
* Place images in a folder with the same name as the content file and include `-images` at the end of the folder name.
* Minimize the use of inlined HTML, but use it where Markdown formatting is limited.
* Although the Material them provides site and page navigation sidebars,
provide in-line table of contents on pages, where appropriate, to facilitate review of page content.

## License ##

This documentation is licensed under the
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0).

## Contributing ##

Contribute to the documentation as follows:

1. Use GitHub repository issues to report minor issues.
2. Use GitHub pull requests.

## Maintainers ##

This repository is maintained by the [Open Water Foundation](http://openwaterfoundation.org/).

## Contributors ##

* Steve Malers, Open Water Foundation (@smalers)
* Emma Giles, Open Water Foundation (@egiles16)

## Release Notes ##

The following release notes indicate the update history for documentation, with GitHub repository issue indicated,
if applicable (links to issues via README.md are not cleanly supported by GitHub so use the repository issues page to find).

* 2018-01-04 - initial content
