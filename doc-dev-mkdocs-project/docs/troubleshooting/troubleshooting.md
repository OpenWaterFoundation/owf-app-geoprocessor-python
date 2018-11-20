# GeoProcessor / Troubleshooting #

The GeoProcessor is a Python application that uses Python modules developed as part of the GeoProcessor,
and Python modules and software that are part of the QGIS software.
Consequently, errors can occur in various software components.

## Log File ##

The GeoProcessor uses the Python logging features to create a log file that is helpful to troubleshoot issues.
However, although log files may be helpful to software developers, they can be difficult for others to understand.
The log file exists in the following locations:

* User's home folder GeoProcessor files, for example:
	+ Windows: `C:\Users\user\.owf-gp\log\gp_user.log`
	+ Linux:  `/home/user/.owf-gp/log/gp_user.log`
	+ Cygwin:  `/cygdrive/C/Users/user/.owf-gp/log/gp_user.log` (different files from Windows)
	+ Git Bash (MinGW):  `/c/Users/user/.owf-gp/log/gp_user.log` (same files as Windows)
* File specified by the GeoProcessor [StartLog](http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user/command-ref/StartLog/StartLog/) command.

The log file contains a sequential record of log messages for application startup followed by
output from running the commands, as shown in the following example.
The first part of the line indicates the message type, which can be one of the following,
shown in increasing severity and therefore decreasing frequency:  `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`.
In other words, one should expect very few `CRITICAL` messages.  Any message of level `WARNING`, `ERROR`, or `CRITICAL`
should be dealt with because they can lead to a proliferation of problems in later commands.

```txt
INFO|geoprocessor|log line 151|Opened new log file: "C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python-test\test\commands\RemoveFile\results\test-RemoveFile.gp.log"
INFO|geoprocessor.core.GeoProcessor|GeoProcessor line 547|-> Start processing command 2 of 5: # Test removing a file
INFO|geoprocessor.core.GeoProcessor|GeoProcessor line 547|-> Start processing command 3 of 5: # Uncomment the following line to regenerate expected results
INFO|geoprocessor.core.GeoProcessor|GeoProcessor line 547|-> Start processing command 4 of 5: CopyFile(SourceFile="data/testfile.txt",DestinationFile="results/test-RemoveFile-out.txt")
INFO|geoprocessor.commands.util.CopyFile|CopyFile line 144|Copying file "C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python-test\test\commands\RemoveFile\data\testfile.txt" to "C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python-test\test\commands\RemoveFile\results\test-RemoveFile-out.txt"
INFO|geoprocessor.core.GeoProcessor|GeoProcessor line 547|-> Start processing command 5 of 5: RemoveFile(SourceFile="results/test-RemoveFile-out.txt")
INFO|geoprocessor.commands.util.RemoveFile|RemoveFile line 120|Removing file "C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python-test\test\commands\RemoveFile\results\test-RemoveFile-out.txt"
INFO|geoprocessor|gp line 188|GeoProcessor properties after running:
INFO|geoprocessor|gp line 190|UserName = sam
INFO|geoprocessor|gp line 190|ComputerName = colorado
INFO|geoprocessor|gp line 190|InstallDirURL = None
INFO|geoprocessor|gp line 190|OutputStart = None
INFO|geoprocessor|gp line 190|InitialWorkingDir = C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python-test\test\commands\RemoveFile
INFO|geoprocessor|gp line 190|WorkingDir = C:\Users\sam\owf-dev\GeoProcessor\git-repos\owf-app-geoprocessor-python-test\test\commands\RemoveFile
INFO|geoprocessor|gp line 190|InputStart = None
INFO|geoprocessor|gp line 190|OutputEnd = None
INFO|geoprocessor|gp line 190|UserHomeDir = C:\Users\sam
INFO|geoprocessor|gp line 190|ProgramVersionString = None
INFO|geoprocessor|gp line 190|TempDir = c:\users\sam\appdata\local\temp
INFO|geoprocessor|gp line 190|ComputerTimezone = Mountain Standard Time
INFO|geoprocessor|gp line 190|InputEnd = None
INFO|geoprocessor|gp line 190|InstallDir = None
INFO|geoprocessor|gp line 190|OutputYearType = None
INFO|geoprocessor|gp line 190|UserHomeDirURL = file:///C:/Users/sam
INFO|geoprocessor|gp line 190|ProgramVersionNumber = None
```

## Command Status/Log ##

The GeoProcessor user interface (under development) displays command-specific warning messages,
which indicate problems that need to be resolved.
A command flagged with red X or yellow warning symbol can be reviewed to determine problems.

Pending user interface implementation, the GeoProcessor may be enhanced to add a file to write the command messages.

## Specific Issues ##

Insert here troubleshooting information for specific issues as such issues are identified.
