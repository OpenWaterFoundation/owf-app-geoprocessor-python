# build #

This folder is used to build distributions.
Most files here will be ignored via the main `.gitignore` file.

* `tmp-gp` - version of the deployed application, extends QGIS
	+ corresponds to `gp-site-package.tar.gz`, install in Python `site-packages` folder
	+ `setup.py` approach will also be used as per Pythonic ways at some point, but need to evaluate.
* `tmp-gptest` - version that does not have QGIS dependencies, to use as functional testing framework
	+ corresponds to `gptest-site-package.tar.gz`, install in Python `site-packages` folder
