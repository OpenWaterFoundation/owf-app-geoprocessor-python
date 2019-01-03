# build-util/install

This folder contains scripts to download and install the GeoProcessor.
Download `download-gp.sh` from the
[OWF GeoProcessor download site](http://software.openwaterfoundation.org/geoprocessor) and run to install.

* `download-gp.sh` - script to download and install the GeoProcessor.
	+ This script is uploaded to the above website and needs to be
	downloaded and run to install on Linux.
	+ This calls the `install-gp-venv.sh` script.
* `install-gp-venv.sh` - script called by `downlod-gp.sh` to install the downloaded
software into its final location.
	+ Will prompt the user for destination folder.
