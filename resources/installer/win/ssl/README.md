# resourdes/installer/win/ssl #

These files are used to create the Windows installer.
Python pip utility uses SSL to connect to the server to download Python packages.
However, the necessary software to do this is not included by default for some Python versions.
In particular, the Python that is used as the base interpreter for deployed virtual environment
must have the files.  Rather than hope that the software developer who is creating the
installer has the files, they are included here and are copied as necessary.
