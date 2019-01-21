# QGIS Install Version Experiments #

*Emma Giles, Steve Malers | March 2018 | Open Water Foundation*

This documentation was created to record experiments with installing different versions of QGIS.
This was done to evaluate transition from QGIS 2 to QGIS 3.
Questions that need to be answered relevant to the GeoProcessor include:

* Can multiple versions of QGIS be installed on a computer at the same time? Answer:  Yes, with some limitations.
* Can the GeoProcessor be run with a specific QGIS versions? Answer:  Yes, by configuring the Python environment.

The following sections are included in this page.  Experiments were done on a Windows 10 computer.

* [QGIS Versioning Overview](#qgis-versioning-overview)
* [OSGeo4W Suite Download of QGIS vs. Stand-alone QGIS Download](#osgeo4w-suite-download-of-qgis-vs-stand-alone-qgis-download)
* [How to Download Multiple Versions of QGIS on a Windows Machine](#how-to-download-multiple-versions-of-qgis-on-a-windows-machine)
* [GeoProcessor Testing Overview](#geoprocessor-testing-overview)
	+ [Methodology](#methodology)
	+ [Findings](#findings)
	+ [Conclusions](#conclusions)
* [Resources](#resources)

----

## QGIS Versioning Overview ##

QGIS is distributed by 2 methods: 

* **OSGEO4W suite** - what most people will use to install the current version (3.0+, not stable as of March 2018),
and advanced install allows installing the long-term release (2.18+, stable)
* **stand-alone installer** - can be used to install specific versions, as needed

QGIS has multiple releases. Each version is defined by QGIS `A`.`B`.`C` where: 

* `A` is the `MAJOR` release
* `B` is the `MINOR` release
* `C` is a `BUG FIX`

For example, version `2.18.17`  is `MAJOR` release `2`, `MINOR` release `18` and `BUG FIX` `17`.

Each minor version is also assigned a name, such as `Las Palmas` for version 2.18.
Although the name is useful for some purposes, using the numeric version is more precise
and also helps understand historical sequence corresponding to the number sequence.

## OSGeo4W Suite Download of QGIS vs. Stand-alone QGIS Download ##

The OSGeo4W suite includes QGIS and other GIS software including [GRASS](https://grass.osgeo.org/),
[GDAL](http://www.gdal.org/) and [SAGA](http://saga-gis.org/en/index.html).
**Additional effort is needed to fully understand which components are involved in
each of the installation types described below.**

QGIS can be downloaded and installed two ways:

1. **OSGeo4W suite**:
	* this is the default installer that includes bundled components indicated above
	* is only available for the latest version (version 3 as of March 10, 2018, does not appear to be production-ready)
	* on Windows 64-bit, installs to `C:\OSGeo4W64`
		+ within this folder the default is to run the latest QGIS, for example 3.0
		 ("qgis" will be used in folders and scripts, for example `qgis.bat`)
		+ using the ***Advanced Install on the QGIS download page***,
		can optionally install other versions such as the latest long-term release, for example 2.18
		("ltr" will be used in folders and scripts, for example `qgis-ltr.bat`), see below for more explanation
		+ the installer will overwrite any previous contents in this folder
		(use stand-alone installer approach to install older versions on the same machine)
2. **"stand-alone" install**:
	* includes some bundled components (**unclear how many**)
	* allows installing older versions
	* On Windows, installs to `C:\Program Files\QGIS QGIS-Name`
		+ only one variant of QGIS is installed, in this case the most recent version
		(not like the OSGeo4W suite, see below for more explanation)
		+ the installer will overwrite any previous contents in this folder considering the minor release
		(cannot install 2.18.1 and 2.18.2 on the same machine but can install 2.17 and 2.18)
	* QGIS is run using normal `qgis.bat`, etc.

The following presents more information about the OSgeo4W suite.
For Windows 10, the OSGeo4W suite installer can install three variants of QGIS under the `C:\Windows\OSGeo4W64` folder:

* `Latest Release`:
	+ Most recently released version of QGIS
	+ Beware that current 3.x release is new and may not be production-ready
	+ Will run from the Windows ***Start*** menu
	+ Run on the command line with `qgis.bat`
	+ GeoProcessor is currently **not supported** with this version
* `Long Term Release (qgis-ltr-full)`:
	+ Most recent, stable version of QGIS (version 2.18.17 as of March 10, 2018, since version 3.0 needs more time)
	+ Run on the command line with `qgis-ltr.bat`
	+ GeoProcessor is currently supported with this version by running `qgis-ltr.bat`
	in development and deployed environments
* `Bleeding-Edge Development Build (qgis-dev-full)`:
	+ Unstable development version of QGIS.
	+ Should generally be avoided except by software developers that are contributing to QGIS or
	are troubleshooting

Installing the OSGeo4W suite using the ***Advanced Install*** is recommended,
in order to also install the long-term release.
The stand-alone installer is available for any historically released version of QGIS,
but is generally not necessary unless a specific version of QGIS and the GeoProcessor is needed,
such as a "frozen" version of an application.

The GeoProcessor functions when using QGIS from the OSGeo4W suite,
but currently only when the ***Advanced Install*** is done and the optional long-term release is installed.
This is because the GeoProcessor is currently only supported for Python 2 and the
QGIS long-term release is 2.18.17 (or later), which uses Python 2.7.

The GeoProcessor also functions when using QGIS from the stand-alone QGIS installer
for recent QGIS 2.x versions, because those versions use Python 2.7.

See `Stack Exchange - What is OSGeo4W?` link in the [Resources](#resources) page for more information.

## How to Download Multiple Versions of QGIS on a Windows Machine ##

||How to Download QGIS with Stand-alone Installer (without OSGeo4W Suite)|
|-|-|
|1|Access the [OSGeo4W QGIS Downloads Page](https://qgis.org/en/site/forusers/download.html#). <br> Click the `All Releases` tab. <br>Click the [Older Releases of QGIS are available here](http://download.osgeo.org/qgis/windows/) link. * Note: More QGIS versions are available for download from the [QGIS Downloads Page](https://qgis.org/downloads/) |
|2|Click on the `.exe` file of the desired version. <br>For this example, `QGIS-OSGeo4W-2.18.10-Setup-x86_64.exe` is used.|
|3|The installer will begin to download. When complete, navigate to the `File Explorer` `Downloads` folder. The file will be named similar to `QGIS-OSGeo4W-2.18.10-1-Setup-x86.exe`.|
|4|Right-click the file and select `Run as Administrator`. If you are not logged into the admin account, enter the admin credentials.|
|5|A window will appear that says, `"Do you want to allow this app from an unknown publisher to make changes to your device?"`. Click `Yes`.|
|6|A `Welcome` window will appear. Click `Next >`.|
|7|A `License Agreement` window will appear. Click `I Agree`. |
|8|A `Choose Components` window will appear. Keep defaults and click `Install`.|
|9|The installation will begin. When complete, click `Finish`.|
|10|The stand-alone QGIS software will be installed under `C:/Program Files/QGIS [major.minor version]`. For this example, the stand-alone QGIS software is installed under `C:/Program Files/QGIS 2.18`. <br><br>To start QGIS Desktop `[major.minor.bugFix version]`, open the Windows `Start` menu. Under the `QGIS [major.minor version]` folder, select `QGIS Desktop [major.minor.bugFix version]`.|
||*Note: <br><br> There are multiple releases of QGIS for each QGIS `major.minor` version. These other releases are bug fixes. These releases are indicated by a third decimal specification. For example, bug fix release 3 of QGIS version `2.18` is `2.18.3`. <br><br> When a stand-alone QGIS software is downloaded, the software is kept in a folder called `C:/Program Files/QGIS [major.minor version]`. The installer only allows a unique `major.minor` folder to be installed.<br><br> If a different `bug fix` release of an already installed QGIS version is installed, the current QGIS software will be uninstalled and the new QGIS software (same `major.minor` version but different `bug fix` release) will replace it. This means that there cannot be more than one `bug fix` release of any one QGIS `major.minor` version installed on the same computer. <br><br> If a different `major.minor` version is being downloaded than the one listed under the `C:/Program Files` folder, the install will take place without uninstalling any QGIS software. The `C:Program Files` folder will then hold 2 QGIS folders. <br><br> For example, if stand-alone QGIS version `2.18.3` was installed on the computer and then the stand-alone QGIS version `2.12.2` was installed on the computer, then both the `C:/Program Files QGIS 2.12` folder and the `C:/Program Files QGIS 2.18` folder would exist.* | 

||How to Download Multiple `Bug Fix` Releases of the Same QGIS `Major.Minor` Version (Stand-alone Installer) - *Not Possible*|
|-|-|
||*Note:  <br><br> It is not possible, according to the findings in this investigation, to download multiple `bug fix` releases of the same `major.minor` QGIS version (installed with the stand-alone installer). For example, one cannot have version `2.18.1` and version `2.18.3` installed on one computer at the same time. However, the following step-by-step instructions remain pertinent in this documentation to memorialize the steps/logic pursued to determine this understanding. <br><br> Issue causing this task to be impossible:  When downloading the second `bug fix` release of the same QGIS `major.minor` version `step 5`, a prompt window appears with the following message: <br><br>`QGIS [major.minor version] is already installed on you system. The installed release is [currently installed `bug fix` version. You are going to install a newer/older release of QGIS [major.minor version]. Press OK to uninstall QGIS [currently installed major.minor.bugFix version] and install  [new major.minor.bugFix version] or Cancel to quit.` <br><br> This message occurs even when the top-folder is renamed from its default name of `C:Program Files/QGIS [major.minor version]` to the unique name of `C:Program Files/QGIS [major.minor.bugFix version]`. <br>For example, when `C:Program Files/QGIS 2.18` is renamed to `C:Program Files/QGIS 2.18.7`.*|
|1|Follow the `How to Download QGIS with Stand-alone Installer (without OSGeo4W Suite)` instructions to download a release of the QGIS version.|
|2|Open the `C:/Program Files` folder on `File Explorer`.|
|3|Rename the `QGIS [major.minor version]` folder to `QGIS [major.minor.bugFix version]`. <br><br> For example, if you downloaded QGIS `2.18.1` in `Step 2` of the `How to Download QGIS with Stand-alone Installer (without OSGeo4W Suite)` instructions, rename the folder from `QGIS 2.18` to `QGIS 2.18.1`.|
|4|Install the GeoProcessor within the QGIS software by following the steps in the `How to Deploy the GeoProcessor on a stand-alone QGIS version` instructions. Where it says `[major.minor version]`, make sure to include the QGIS `major.minor.bugFix` version.|
|5|Follow the `How to Download QGIS with Stand-alone Installer (without OSGeo4W Suite)` instructions to download a different `bug fix` release of the same QGIS `major.minor` version. Then follow `steps 2-4` of this instruction table.|

||How to Download OSGeo4W Suite for Version 2.18.17 (Long Term Release)|
|:-:|-|
|1|Access the [QGIS Main Download Page](https://qgis.org/en/site/forusers/download.html).|
|2|Click the [OSGeo4W Network Installer (64 bit)](http://download.osgeo.org/osgeo4w/osgeo4w-setup-x86_64.exe) link.|
|3|The installer will begin to download. When complete, navigate to the `File Explorer` `Downloads` folder. The file will be named something similar to `osgeo4w-setup-x86_64.exe`.|
|4|Right-click the file and select `Run as Administrator`. If you are not logged into the admin account, enter the admin credentials.|
|5|A window will appear that says, `"Do you want to allow this app from an unknown publisher to make changes to your device?"`. Click `Yes`.|
|6|The `OSGeo4W Net Release Setup Program` window will appear. Select `Advanced Install` and then click `Next >`.|
|7|The `Choose A Download Source` window will appear. Select `Install from Internet` and then click `Next >`.|
|8|The `Choose Root Install Directory` window will appear. Keep defaults and click `Next >`.|
|9|The `Select Local Package Directory` window will appear. Keep defaults and click `Next >`.|
|10|The `Select Connection Type` window will appear. Keep defaults and click `Next >`.|
|11|The `Choose Download Site` window will appear. Select `http://download.osgeo.org` and then click `Next >`.|
|12|The `Select Packages` window will appear. Expand the `Desktop` option. Click the `Skip` button next to the `qgis-ltr-full` option. Click `Next >`. <br><br> By default, the QSGeo4W download will download the newest release. By selecting the `Advanced Install`, the `Long Term Release` version of QGIS can be installed rather than the `Newest Release`. The `qgis-ltr-full` selection will download the `Long Term Release` version of QGIS. Note that this will not *always* be version `2.18.17` as it is when this documentation was written. It will download the current `Long Term Release` version. |
|13|A `Resolve Dependencies` window will appear. Select `Install these packages to meet dependencies (RECOMMENDED)` Click `Next >`.|
|14|The `Agreement of Restrictive Package` window will appear. Scroll to the bottom of the text box. Select `I agreed with above license terms`. Click `Next >`. Another `Agreement of Restrictive Package` window might appear. Select the `I agreed with above license terms` again and then click `Next >`.|
|15|The installation will begin. When complete, click `Finish`.|
|16|The QSGeo4W suite QGIS software will be installed under `C:/OSGeo4W64`. To run the `Long Term Release` version, open the Windows `Start` menu. Under the `OSGeo4W` folder, select `QGIS Desktop 2.18.17`.|

||How to Download OSGeo4W Suite for Version 3.0.0 (Latest Release)|
|:-:|-|
||*Note: <br> If you download the `Latest Release` version with the `Express Desktop Install` after installing the `OSGeo4w Suite Long Term Release`, both the `Latest Release` and the `Long Term Release` will be housed (and functional) under the `C:/OSGeo4W64` folder.The `Long Term Release` startup file will be `C:/OSGeo4W64/bin/qgis-ltr.bat` whereas the `Latest Release` startup file will be `C:/OSGeo4W64/bin/qgis.bat`.* <br> |
|1|Navigate to the [QGIS Main Download Page](https://qgis.org/en/site/forusers/download.html).|
|2|Click the [OSGeo4W Network Installer (64 bit)](http://download.osgeo.org/osgeo4w/osgeo4w-setup-x86_64.exe) link.|
|3|The installer will begin to download. When complete, navigate to the `File Explorer` `Downloads` folder. You should see a file that is named something similar to `osgeo4w-setup-x86_64.exe`.|
|4|Right-click the file and select `Run as Administrator`. If you are not logged into the admin account, enter the admin credentials.|
|5|A window will appear that says, `"Do you want to allow this app from an unknown publisher to make changes to your device?"`. Click `Yes`.|
|6|The `OSGeo4W Net Release Setup Program` window will appear. Select `Express Desktop Install` and then click `Next >`.|
|7|The `Select Packages` window will appear. Keep defaults and then click `Next >`.|
|8|The installation will begin. When complete, click `Finish`.|
|9|The QSGeo4W suite QGIS software will be installed under `C:/OSGeo4W64`. To run the `Latest Release` version, double-click on the `C:/OsGeo4W64/bin/qgis.bat`.|
|10|To start QGIS Desktop `3.0.0`, open the Windows `Start` menu. Under the `OSGeo4W` folder, select `QGIS Desktop 3.0.0`.|

## GeoProcessor Testing Overview ##

The OWF GeoProcessor is reliant on the QGIS software. The GeoProcessor testing framework has been developed to test the GeoProcessor's functionality in varied environments. It is pertinent to test the GeoProcessor functionality for different versions of QGIS. Below are some questions that need to be addressed and answered. 

* Will the OWF GeoProcessor function properly on a QGIS version that was deployed with the `stand-alone installers`? Or, is it required that the QGIS software is deployed from within the OSGeo4W suite? Currently the GeoProcessor has only been tested with the QGIS software in the OSGeo4W suite. 
* Which versions of QGIS are compatible with the GeoProcessor? QGIS `3.0` was recently released. What will happen if the GeoProcessor runs with QGIS `3.0`? Currently the GeoProcessor has been developed for QGIS `2.18`. 

### Methodology ###

||How to Deploy the GeoProcessor on OSGeo4W64 Suite (QGIS `Long Term Release` Version 2.18.17) |
|:-:|-|
|1| The OSGeo4W64 suite for this experiment has the `Latest Release: QGIS 3.0.0 (bin/qgis.bat)` and the `Long Term Release: QGIS 2.18.17 (bin/qgis-ltr.bat)` installed.|
|2|Download and extract the `gp-site-package.zip` in the `Downloads` folder. Within the extracted `gp-site-package` folder, copy the `geoprocessor` folder.|
|3|Paste the `geoprocessor` folder in the `C:/OSGeo4W64/apps/Python27/Lib/site-packages` folder.|
|4|Download the `gp.bat` file. Copy the file and paste it to the `C:/Users/[user]/Desktop` folder.|
|5|Edit the gp.bat file. Change the `QGISNAME` variable in the `gp.bat` file from `qgis` to `qgis-ltr`.|
|6|Test that the geoprocessor is correctly downloaded. <br><br>Create a `.gp` workflow in your `Desktop` with one comment line. <br> Open the `Windows Command Prompt`. <br> Use `cd` to navigate to the `Desktop` folder. <br>Type `gp.bat --commands [name-of-test-workflow.gp]`. Press `Enter`. <br> Make sure that `Running OWF GeoProcessor application gp...` prints to the console. <br><br> This is expected because the QGIS version `2.18.17` or older is compatible with the current version of the GeoProcessor. |


||How to Deploy the GeoProcessor on OSGeo4W64 Suite (QGIS `Latest Release` Version 3.0.0) - *Causes Error*|
|:-:|-|
|1| The OSGeo4W64 suite for this experiment has the `Latest Release: QGIS 3.0.0 (bin/qgis.bat)` and the `Long Term Release: QGIS 2.18.17 (bin/qgis-ltr.bat)` installed.|
|2|Download and extract the `gp-site-package.zip` in the `Downloads` folder. Within the extracted `gp-site-package` folder, copy the `geoprocessor` folder.|
|3|Paste the `geoprocessor` folder in the `C:/OSGeo4W64/apps/Python36/lib/site-packages` folder.|
|4|Download the `gp.bat` file. Copy the file and paste it to the `C:/Users/[user]/Desktop` folder.|
|5|Edit the gp.bat file. <br>Replace the line <br>`set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\Python27\Lib\site-packages` <br>with<br> `set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\Python36\lib\site-packages`. |
|6|Test that the geoprocessor is correctly downloaded. <br><br>Create a `.gp` workflow in your `Desktop` with one comment line. <br> Open the `Windows Command Prompt`. <br> Use `cd` to navigate to the `Desktop` folder. <br>Type `gp.bat --commands [name-of-test-workflow.gp]`. Press `Enter`. <br> Make sure that `Running OWF GeoProcessor application gp...` prints to the console.|
||*Note: <br><br> This causes an error. The following message is print to the command prompt when running the `gp.bat` file:* <br><br> `from geoprocessor.commands.layers.AddGeoLayerAttribute import AddGeoLayerAttribute`<br>`File "C:\OSGEO4~1\apps\Python36\lib\site-packages\geoprocessor\commands\layers\AddGeoLayerAttribute.py", line 11, in <module>`<br>`   import geoprocessor.util.validator_util as validators`<br>`File "C:\OSGEO4~1\apps\Python36\lib\site-packages\geoprocessor\util\validator_util.py", line 16, in <module>`<br>`import geoprocessor.util.qgis_util as qgis_util`<br>`File "C:\OSGEO4~1\apps\Python36\lib\site-packages\geoprocessor\util\qgis_util.py", line 7, in <module>`<br>`from qgis.core import QgsApplication, QgsCoordinateReferenceSystem, QgsExpression, QgsFeature, QgsField`<br>`File "C:\OSGEO4~1\apps\qgis\python\qgis\__init__.py", line 71, in <module>`<br>`from qgis.PyQt import QtCore`<br>`File "C:\OSGEO4~1\apps\qgis\python\qgis\PyQt\QtCore.py", line 26, in <module>`<br>`from PyQt5.QtCore import *`<br>`ImportError: DLL load failed: The specified module could not be found.`<br><br>This is expected because the GeoProcessor code has not yet been written to work with Python 3. |

||How to Deploy the GeoProcessor on a Stand-alone QGIS version|
|:-:|-|
|1|Download and extract the `gp-site-package.zip` in the `Downloads` folder. Within the extracted `gp-site-package` folder, copy the `geoprocessor` folder.|
|2|Paste the `geoprocessor` folder in the `C:/Program Files/QGIS [major.minor version]/apps/Python27/Lib/site-packages` folder.|
|3|Download the `gp.bat` file. Copy the file and paste it to the `C:/Users/[user]/Desktop` folder.|
|4|Edit the `gp.bat` file with a text editor. <br> Change the value of the `QGIS_INSTALL_HOME` variable from `C:\OSGeo4W64` to `C:/Program Files/QGIS [major.minor version]`. <br> Rename the file to `gp-sa-[major.minor.bugFix version]`. <br>*Note: `sa` stands for stand-alone.*|
|5|Test that the geoprocessor is correctly downloaded. <br><br>Create a `.gp` workflow in your `Dekstop` with one comment line. <br> Open the `Windows Command Prompt`. <br> Use `cd` to navigate to the `Desktop` folder. <br>Type `gp-sa-[major.minor.bugFix version].bat --commands [name-of-test-workflow.gp]`. Press `Enter`. <br> Make sure that `Running OWF GeoProcessor application gp...` prints to the console and that no warnings or errors are created.<br><br> This is expected because this step-by-step instruction table assumes that the QGIS `major.minor.bugFix` version is QGIS version `2.18.17` or older. The GeoProcessor has not yet been written to handle QGIS version 3.0.0 or later becasue the GeoProcessor has not compatibility with Python 3.|

||How to Test the GeoProcessor on a Stand-alone QGIS version|
|:-:|-|
|1|If you have not installed the most recent version of the GeoProcessor testing framework, start at `step 2`. If the most recent version of the GeoProcessor testing framework has been installed, start at `step 6`.|
|2|Create a folder named `gp-test` in the `Desktop` folder.|
|3|Access the `owf-app-geoprocessor-python-test` GitHub repository via this [link](https://github.com/OpenWaterFoundation/owf-app-geoprocessor-python-test).|
|4|Click the green `Clone or download` button and copy the link.|
|5|Open `Git Bash`. <br>Use `cd` to navigate to the `Desktop/gp-test` folder. <br> Type `git clone [copied link from step 3]`. Press `Enter`. <br> There should now be the `owf-app-geoprocessor-python-test` folder within the `gp-test` folder.|
|6|Edit the `gp-test/owf-app-geoprocessor-python-test/test/suites/create/create-test-command-file.bat` file with a text editor. <br> Change the value of the `GP` variable to point to the `gp-sa-[major.minor.bugFix version].bat` file. <br>Change the `create-regression-test-command-file.gp` value to `create-regression-test-command-file-[major.minor.bugFix version].gp`. <br>Save the file *as* `create-test-commmand-file-[major.minor.bugFix version].bat`. <br> Do not overwrite the original `create-test-command-file.bat` file.|
|7|Edit the `gp-test/owf-app-geoprocessor-python-test/test/suites/create/create-regression-test-command-file.gp` file with a text editor. <br> Change the value of the `OutputFile` variable to `"../run/geoprocessor-tests-[major.minor.bugFix version].gp"`. <br>Save the file *as* `create-regression-test-command-file-[major.minor.bugFix version].gp`.  <br>Do not overwrite the original `create-regression-test-command-file.gp`.|
|8|Edit the `gp-test\owf-app-geoprocessor-python-test\test\suites\run\run-geoprocessor-tests.bat` file with a text editor.<br> Change the value of the `GP` variable to point to the `gp-sa-[major.minor.bugFix version].bat` file. <br> Change the geoprocessor-tests.gp value  to `geoprocessor-tests-[major.minor.bugFix version].gp`. <br>Save the file *as* `run-geoprocessor-tests-[major.minor.bugFix version].bat`.  <br>Do not overwrite the original `run-geoprocessor-tests.bat` file.|
|9|Open the `Windows Command Prompt`. <br> Use `cd` to navigate to the `gp-test/owf-app-geoprocessor-python-test/test/suites/create` folder. <br> Type `create-regression-test-command-file-major.minor.bugFix version].bat`. Press `Enter`. <br> Use `cd` to navigate to the `gp-test/owf-app-geoprocessor-python-test/test/suites/run` folder. <br> Type `run-geoprocessor-tests-[major.minor.bugFix version].bat`. Press `Enter`. <br>|
|10|Use `cd` to navigate to the `gp-test/owf-app-geoprocessor-python-test/test/suites/create` folder. <br> Run the `create-test-commmand-file-[major.minor.bugFix version].bat` file. <br> Type `cd ..\run`. Press `Enter`. <br> Run the `run-geoprocessor-tests-[major.minor.bugFix version].bat` file. <br><br> View the test results in the `run\geoprocessor-tests-[major.minor.bugFix version].gp.summary.html` file and the `geoprocessor-tests-[major.minor.bugFix version].gp.out.txt` file.|
|11|Make sure that you start a *new* command prompt window between each test. Otherwise the `PYTHONPATH` variable can be set to incorrect versions causing the testing framework to break.|

### Findings ###

|QGIS <br> Version|Fail Count <br> (`HTML`)|Fail Count <br> (`TXT`)|Computer <br> Name|Test Run <br>Date|Installer Type|
|:-:|:-:|:-:|:-:|:-:|:-:|
|2.16.3|14|21|`DESKTOP-F5QVQ8P`|3/6/2018|`stand-alone`|
|2.18.1|9|16|`DESKTOP-F5QVQ8P`|3/6/2018|`stand-alone`|
|2.18.10|2|9|`DESKTOP-F5QVQ8P`|3/6/2018|`stand-alone`|
|2.18.17|2|9|`DESKTOP-F5QVQ8P`|3/7/2018|`OSGeo4W qgis-ltr`|

### Conclusions ###

||The GeoProcessor functions with the stand-alone QGIS downloads.|
|:-:|-|
|Proof|The suite test results for the GeoProcessor with the `stand-alone QGIS` (in the [`Findings`](#findings) section) match the suite test results for the GeoProcessor with the `OSGeo4W QGIS`.|
|Why important?|The GeoProcessor can be tested with *any* past QGIS versions/releases. One can only download a select number of releases of QGIS under the OSGeo4W suite.|
|Further investigation needed?| Yes. How does QGIS within the OSGeo4W suite differ from the QGIS downloaded with the stand-alone installer. It could be that there are functions that are possible within the OSGeo4W suite but not possible within the stand-alone version - those functions are not determined with this tests because the GeoProcessor is still in development and may not access those functionalities *yet*. | 

||The GeoProcessor fails when running with the OSGeo4W QGIS 3.0 Version|
|:-:|-|
|Proof|An error message is thrown when running a simple test `.gp` workflow. Refer to the *Note* in the `How to Deploy the GeoProcessor on OSGeo4W64 Suite (QGIS Version 3.0.0) - *Causes Error*` instruction table. |
|Why important?|Currently, when downloading the default version of OSGeo4W QGIS, the QGIS version is `3.0.0` (the `latest release` of QGIS is downloaded). It will be important for GeoProcessor users and testers to *NOT* download the most recent version of OSGeo4W QGIS. It will be pertinent that `OWF` changes the GeoProcessor's installation instructions to have the users download a QGIS version that is compatible with the current version of the GeoProcessor.|
|Further investigation needed?|Yes. Is there a workaround to get the GeoProcessor to run on QGIS Version `3.0.0`? If the `Long Term Release` is downloaded, is there a way to have the GeoProcessor access that version of the OSGeo4W QGIS? Currently the `Long Term Release` is a compatible QGIS version of `2.18.17`.|

## Resources ##

* [Stack Overflow - Can I install two versions of QGIS on the same computer?](https://gis.stackexchange.com/questions/32820/can-i-install-two-versions-of-qgis-on-the-same-computer)
* [Stack Overflow - How to install OSGeo4W libraries in older version of QGIS (2.16)?](https://gis.stackexchange.com/questions/230672/how-to-install-osgeo4w-libraries-in-older-version-of-qgis-2-16)
* [Stack Exchange - What is OSGeo4W?](https://gis.stackexchange.com/questions/164976/what-is-osgeo4w)
* [QGIS Downloads - All Releases](https://qgis.org/downloads/)
* [QGIS Downloads - Select Releases](http://download.osgeo.org/qgis/windows/)
