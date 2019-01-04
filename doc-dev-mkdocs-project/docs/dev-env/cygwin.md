# GeoProcessor / Development Environment / Cygwin #

Cygwin provides a Linux-like environment on Windows that can be used to
run scripts in the Windows development environment (the other option being Git Bash).
See the [OWF / Learn Cygwin](http://learn.openwaterfoundation.org/owf-learn-cygwin/)
documentation for information on installing Cygwin.
The following Cygwin software must be installed in order to create a Python virtual environment
to test GeoProcessor software.  Use the Cygwin setup utility to install software.

| **Cygwin Software**                | **Needed by**                             | **Description**                                                                               |
|------------------------------------|-------------------------------------------|-----------------------------------------------------------------------------------------------|
| `gcc-core`                         | Compiling source.                         | Needed when `pip` compiles software because no binary is available.                           |
| `gcc-fortran`                      | Compiling source.                         | Needed when `pip` compiles software because no binary is available.                           |
| `python3-devel`                    | Compiling source.                         | Needed when `pip` compiles software because no binary is available (multiple components).     |
| `libffi-devel`                     | Compiling source.                         | Needed when `pip` compiles software because no binary is available (for `requests[security]`. |
| `libpq-devel`                      | Compiling source for PostgreSQL           | Needed when `pip` compiles software because no binary is available (for PostgreSQL driver).   |
| `openssl-devel`                    | Compiling source for `requests[security]` | Needed when `pip` compiles software because no binary is available (for `requests[security]`. |
| `python3-numpy`                    | `pandas`                                  | Needed because `pip` version was not available.                                               |
| `python3-six`                      | `pandas`                                  | Needed because `pip` version was not available.                                               |
| `python3-wheel`                    | `pandas`                                  | Needed because `pip` version was not available.                                               |
| `python3-setuptools`               | `pandas`                                  | Needed because `pip` version was not available.                                               |
| `python3-pip`                      | `pandas`                                  | Needed because `pip` version was not available.                                               |
| `python3-cython`                   | `pandas`                                  | Needed because `pip` version was not available.                                               |
| `gcc-g++`                          | Compiling source.                         | Needed because `pip` version was not available.                                               |
| `make`                             | Compiling source.                         | Needed because `pip` version was not available.                                               |
| `wget`                             | `pandas`                                  | Needed because `pip` version was not available.                                               |
| `python3-pyqt5`                    | `PyQt5`                                   | Needed because `pip` version was not available.                                               |
| `python3-pyqt5-qsci`               | `PyQt5`                                   | Needed because `pip` version was not available.                                               |
| `python3-pyqt5-qt3d`               | `PyQt5`                                   | Needed because `pip` version was not available.                                               |
| `python3-pyqt5-qtchart`            | `PyQt5`                                   | Needed because `pip` version was not available.                                               |
| `python3-pyqt5-qtdatavisualization`| `PyQt5`                                   | Needed because `pip` version was not available.                                               |
| `python3-sip`                      | `PyQt5`                                   | Needed because `pip` version was not available.                                               |
