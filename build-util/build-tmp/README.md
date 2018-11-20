# build-tmp #

This folder is used to build distributions.
Most files here will be ignored via the `.gitignore` file in this folder.
In the following, `VERSION` is the software version (e.g., `1.0.0`) from the
`geoprocessor/app/version.py` file.

Copies of the `geoprocessor` repository working files are copied to the following folders:

* `tmp-gp-VERSION` - version of the deployed application, extends QGIS
	+ corresponds to `gp-VERSION-site-package.tar.gz` and `gp-VERSION-site-package.zip`,
	install in Python `site-packages` folder
	+ `setup.py` approach will also be used as per Pythonic ways at some point, but need to evaluate.
* `tmp-gptest-VERSION` - version that does not have QGIS dependencies, to use as functional testing framework
	+ corresponds to `gptest-VERSION-site-package.tar.gz` and `gptest-VERSION-site-package.zip`,
	install in Python `site-packages` folder

The contents of the above folders are packaged into the following distributable files:

* Windows:
	+ `gp-VERSION-site-package.zip` - full QGIS-compatible distribution
	+ `gptest-VERSION-site-package.zip` - test framework distribution
* Linux and Cygwin:
	+ `gp-VERSION-site-package.tar.gz` - full QGIS-compatible distribution
	+ `gptest-VERSION-site-package.tar.gz` - test framework distribution
