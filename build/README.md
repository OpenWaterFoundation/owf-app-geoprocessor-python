# build #

This folder is used to build distributions.
Most files here will be ignored via the main `.gitignore` file.

Copies of the `geoprocessor` repository working files are copied to:

* `tmp-gp` - version of the deployed application, extends QGIS
	+ corresponds to `gp-site-package.tar.gz` and `gp-site-package.zip`,
	install in Python `site-packages` folder
	+ `setup.py` approach will also be used as per Pythonic ways at some point, but need to evaluate.
* `tmp-gptest` - version that does not have QGIS dependencies, to use as functional testing framework
	+ corresponds to `gptest-site-package.tar.gz` and `gptest-site-package.zip`,
	install in Python `site-packages` folder

The contents of the above folders are packaged into the following distributable files:

* Windows:
	+ `gp-site-package.zip` - full QGIS-compatible distribution
	+ `gptest-site-package.zip` - test framework distribution
* Linux:
	+ `gp-site-package.tar.gz` - full QGIS-compatible distribution
	+ `gptest-site-package.tar.gz` - test framework distribution
