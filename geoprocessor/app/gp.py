# gp - main entry point for GeoProcessor application
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2020 Open Water Foundation
# 
# GeoProcessor is free software:  you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     GeoProcessor is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with GeoProcessor.  If not, see <https://www.gnu.org/licenses/>.
# ________________________________________________________________NoticeEnd___

"""
This module provides access to the Open Water Foundation GeoProcessor tools via
the gp application, which provides several run modes:

- command shell
- batch (gp --commands CommandFile)
- user interface (gp)
- http server

The initial implementation focuses on batch and command shell.
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
# from geoprocessor.ui.app.GeoProcessorUI import GeoProcessorUI

# GeoProcessor modules

from geoprocessor.app.GeoProcessorAppSession import GeoProcessorAppSession
from geoprocessor.commands.testing.StartRegressionTestResultsReport import StartRegressionTestResultsReport
# The following are imported dynamically since need a QtApplication instance in __main__ first
# from geoprocessor.core.GeoProcessor import GeoProcessor
# from geoprocessor.core.CommandFileRunner import CommandFileRunner

import geoprocessor.util.app_util as app_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.log_util as log_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.app.version as version

# General Python modules
import argparse
import cmd
import getpass
import importlib
import logging
import os
import platform
import sys


class GeoProcessorCmd(cmd.Cmd):
    """
    Class to provide GeoProcessor interactive shell.
    The shell prints a prompt and allows geoprocessor commands to be entered.

    See:  https://docs.python.org/2/library/cmd.html
    See:  https://pymotw.com/2/cmd/

    Example commands:  run command-file.gp

    Because the docstrings are usd for user help, documentation for functions is provided in in-lined comments.
    """
    def __init__(self, qtapp=None):
        # Initialize parent
        super().__init__()
        if qtapp is None:  # Put this here to get rid of PyCharm warning about qtapp not being used
            pass

        self.prompt = "gp> "

        print('Running GeoProcessor shell')
        print('  - Current working directory is:  ' + os.getcwd())
        print('  - Type help at ' + self.prompt + ' to see options')

    @classmethod
    def do_exit(cls, line):
        """
        Exit the geoprocessor command shell, same as "quit".
        """
        if line is None:  # Put this here to get rid of PyCharm warning about line not being used
            pass
        exit(0)

    @classmethod
    def do_printenv(cls, line):
        """
        Print information about the runtime environment.
        Run in the shell with:  printenv
        """
        logger = logging.getLogger(__name__)
        if line is None:  # Put this here to get rid of PyCharm warning about line not being used
            pass
        print("Python version (sys.version) = " + sys.version)
        # Print value of environment variables that impact Python, alphabetized.
        # - skip the more esoteric ones
        # - See:  https://docs.python.org/2/using/cmdline.html
        env_vars = ["PYTHONBYTECODE", "PYTHONDEBUG", "PYTHONHOME", "PYTHONHTTPSVERIFY", "PYTHONOPTIMIZE",
                    "PYTHONPATH", "PYTHONSTARTUP", "PYTHONUSERBASE", "PYTHONUSERSITE", "PYTHONVERBOSE"]
        for env_var in env_vars:
            try:
                print(env_var + " = " + os.environ[env_var])
            except KeyError:
                print(env_var + " = not defined")
        print("os.getcwd() = " + os.getcwd())
        print("platform.architecture = " + str(platform.architecture()))
        print("platform.machine = " + platform.machine())
        print("platform.node = " + platform.node())
        print("platform.platform = " + platform.platform())
        print("platform.processor = " + platform.processor())
        print("platform.system = " + platform.system())
        print("platform.system_alias = " + str(platform.system_alias(platform.system(),
              platform.release(), platform.version())))
        print("user = " + getpass.getuser())
        # GeoProcessor information, such as properties
        GeoProcessor = importlib.import_module('geoprocessor.core.GeoProcessor')
        class_ = getattr(GeoProcessor, 'GeoProcessor')
        processor = class_()
        print("GeoProcessor properties:")
        for property_name, property_value in processor.properties.items():
            print(property_name + " = " + str(property_value))

    @classmethod
    def do_EOF(cls, line):
        if line is None:  # Put this here to get rid of PyCharm warning about line not being used
            pass
        return True

    @classmethod
    def do_quit(cls, line):
        """
        Quit the geoprocessor command shell, same as "exit".
        """
        if line is None:  # Put this here to get rid of PyCharm warning about line not being used
            pass
        exit(0)

    @classmethod
    def do_run(cls, line):
        """
        Run the command file from the command line using syntax:  run command-file
        """
        if line is None:  # Put this here to get rid of PyCharm warning about line not being used
            pass
        logger = logging.getLogger(__name__)
        command_file = line
        if command_file is None:
            print('Error:  no command file specified for "run" command.')
        print('Running command file: ' + command_file)
        working_dir = os.getcwd()
        # Convert the command file to an absolute path if not already.
        command_file_absolute = io_util.verify_path_for_os(io_util.to_absolute_path(working_dir, command_file))
        # Make sure the file exists so ugly exception is not printed
        if not os.path.isfile(command_file_absolute):
            print("File does not exist, cannot run:  " + command_file_absolute)
            return
        # from geoprocessor.core.CommandFileRunner import CommandFileRunner
        CommandFileRunner = importlib.import_module('geoprocessor.core.CommandFileRunner')
        class_ = getattr(CommandFileRunner, 'CommandFileRunner')
        runner = class_()
        # Read the command file
        try:
            runner.read_command_file(command_file_absolute)
        except IOError:
            # Would be nice to use FileNotFoundError but that is Python 3.3+
            message = 'Error:  Command file "' + command_file_absolute + '" was not found.'
            print(message)
            logger.error(message, exc_info=True)
        except Exception:
            message = 'Error reading command file.'
            logger.error(message, exc_info=True)
            print(message)
        # Run the command file
        try:
            runner.run_commands()
        except Exception:
            message = 'Error running command file.'
            print(message)
            logger.error(message, exc_info=True)

        logger.info("GeoProcessor properties after running:")
        for property_name, property_value in runner.get_processor().properties.items():
            logger.info(property_name + " = " + str(property_value))
        print("See log file for more information.")

    @classmethod
    def do_ui(cls, line):
        """
        Run the command file from the command line using syntax:  run command-file
        """
        if line is None:  # Put this here to get rid of PyCharm warning about line not being used
            pass
        run_ui(app_session)

    def postloop(self):
        print()


def parse_command_line_properties(property_list):
    """
    Parse command line properties that were specified with the -p Property=Value syntax.
    The logic may need to be made more complex depending on how quoted strings, etc. are handled.

    Args:
        property_list: List containing zero or more Property=Value strings.

    Returns:
        Dictionary with key being property name and value being the property value as string.
    """
    logger = logging.getLogger(__name__)
    property_dict = string_util.key_value_pair_list_to_dictionary(property_list)
    # Print the properties to help with troubleshooting
    print("property_dict=" + str(property_dict))
    for key in property_dict:
        logger.info('Command line processor property: ' + key + '="' + str(property_dict[key]) + '"')
    return property_dict


def print_env():
    """
    Print information about the environment, useful for troubleshooting.
    Returns:  None
    """
    print("PYTHONPATH items:")
    for item in sys.path:
        print(item)


def print_version():
    """
    Print the program version.
    """
    print("")
    print("gp version " + version.app_version)
    print("")
    print("GeoProcessor")
    print("Copyright 2017-2020 Open Water Foundation.")
    print("")
    print("License GPLv3+:  GNU GPL version 3 or later")
    print("")
    print("There is ABSOLUTELY NO WARRANTY; for details see the")
    print("'Disclaimer of Warranty' section of the GPLv3 license in the LICENSE file.")
    print("This is free software: you are free to change and redistribute it")
    print("under the conditions of the GPLv3 license in the LICENSE file.")
    print("")


# This is the same as the GeoProcessorCmd.do_run() function.
# - could reuse code but inline it for now
def run_batch(command_file, runtime_properties):
    """
    Run in batch mode by processing the specific command file.

    Args:
        command_file (str):  The name of the command file to run, absolute path or relative to the current folder.
        runtime_properties (dict):  A dictionary of properties for the processor.

    Returns:
        None.
    """
    logger = logging.getLogger(__name__)
    print('Running command file: ' + command_file)
    working_dir = os.getcwd()
    # Convert the command file to an absolute path if not already.
    logger.info("Working directory=" + working_dir)
    logger.info("Command file=" + command_file)
    command_file_absolute = io_util.verify_path_for_os(io_util.to_absolute_path(working_dir, command_file))
    logger.info("Command file (absolute)=" + command_file_absolute)
    # from geoprocessor.core.CommandFileRunner import CommandFileRunner
    CommandFileRunner = importlib.import_module('geoprocessor.core.CommandFileRunner')
    class_ = getattr(CommandFileRunner, 'CommandFileRunner')
    runner = class_()
    # Read the command file
    try:
        runner.read_command_file(command_file_absolute)
    except IOError:
        # Would be nice to use FileNotFoundError but that is Python 3.3+
        message = 'Error:  Command file "' + command_file_absolute + '" was not found.'
        print(message)
        logger.error(message, exc_info=True)
        return
    except Exception:
        message = 'Error reading command file "' + command_file_absolute + '".'
        logger.error(message, exc_info=True)
        print(message)
        return
    # Run the command file
    try:
        # Pass the runtime properties to supplement default properties and those created in the command file
        runner.run_commands(env_properties=runtime_properties)
        logger.info("At end of gp.run_batch")
    except Exception:
        message = 'Error running command file.'
        print(message)
        logger.error(message, exc_info=True)
        return
    finally:
        StartRegressionTestResultsReport.close_regression_test_report_file()

    logger.info("GeoProcessor properties after running:")
    for property_name, property_value in runner.get_processor().properties.items():
        logger.info(property_name + " = " + str(property_value))
    print("See log file for more information.")


def run_http_server():
    """
    Run an http server so that the geoprocessor can respond to web requests.
    TODO smalers 2017-12-30 need to evaluate whether to use Python built-in capabilities or something like Flask.

    Returns:
        None.
    """
    print("The GeoProcessor web server is not implemented.  Exiting...")


def run_prompt():
    """
    Run the command line prompt interface.

    Returns:
        None.
    """
    GeoProcessorCmd().cmdloop()


def run_ui(ui_app_session):
    """
    Run the GeoProcessor user interface.

    Args:
        ui_app_session:  application session properties for use with the UI

    Returns: None
    """
    logger = logging.getLogger(__name__)
    # Trying to declare the following in the main and passing here does not seem to work.
    # logger.info("Declaring QApplication...")
    # print("Declaring QApplication...")
    # The following was done previously but is redundant with the call to qgis_util.initialize_qgis() in main.
    qt_app = None
    if qgis_util.qgs_app is None:
        # If QGIS is not used (such as with gptest), use Qt5 application
        # - QgsApplication is derived from QApplication
        # The following line is needed for initialization
        # - If not there is a warning about WebEngine initialization
        # - See similar code in qgis_util.initialize_qgis() for more information
        try:
            QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
        except Exception:
            # This happens when the current development Python packages are different than runtime
            print("Error calling QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)")
            print("- possibly due to Python API version issue")
            print("- ignoring exception and starting the application")
        qt_app = QApplication(sys.argv)
    # print("...back from declaring QApplication.")
    # logger.info("...back from declaring QApplication.")

    # window = QtWidgets.QWidget()
    # window.show()
    #
    # sys.exit(qtapp.exec())

    # The following is used when not dynamically importing modules
    # command_processor = GeoProcessor()
    logger.info("Loading GeoProcessor class...")
    print("Loading GeoProcessor class...")
    GeoProcessor_module = importlib.import_module('geoprocessor.core.GeoProcessor')
    class_ = getattr(GeoProcessor_module, 'GeoProcessor')
    command_processor = class_()
    # GeoProcessorUI derives from window = QtWidgets.QMainWindow()
    GeoProcessorUI_module = importlib.import_module('geoprocessor.ui.app.GeoProcessorUI')
    class_ = getattr(GeoProcessorUI_module, 'GeoProcessorUI')
    ui_runtime_properties = dict()  # PyCharm complains if = {} is used
    ui_runtime_properties['AppVersion'] = version.app_version
    ui_runtime_properties['AppVersionDate'] = version.app_version_date
    ui = class_(command_processor, ui_runtime_properties, ui_app_session)
    print("...back from loading GeoProcessor class.")
    logger.info("...back from loading GeoProcessor class.")
    print("Showing the UI...")
    logger.info("Showing the UI...")
    ui.show()
    # Enter the main loop for the application
    # - the following ensures a clean exit from the application
    if qgis_util.qgs_app is None:
        # QGIS is not used so use Qt5 application
        logger.info("QGIS application is null, assuming Qt5 application")
        if qt_app is None:
            logger.critical("Unable to initialize QApplication.  Exiting.", exc_info=True)
            sys.exit(1)
        else:
            sys.exit(qt_app.exec())
    else:
        # QGIS is used so use its application
        qgis_util.qgs_app.exec_()


# TODO smalers 2018-07-29 is there a global dictionary similar to Python system properties?
def set_global_data():
    """
    Set global data that is useful in library code but is difficult to pass into deep code.
    This may evolve as greater understanding is gained about how to use standard Python modules
    to retrieve application data.

    Returns:  None
    """
    # Determine the absolute path to the application, useful later when trying to find resources such as
    # configuration and image
    logger = logging.getLogger(__name__)
    try:
        # ps = os.sep
        ps = "\n"  # Always use newline, regardless of operating system
        app_util.set_property('ProgramCopyright', version.app_copyright)
        program_home = os.path.dirname(os.path.realpath(__file__))
        # Program executable name, what is typed on command line
        app_util.set_property('ProgramExecutableName', "gp")
        # Does not have trailing separator
        app_util.set_property('ProgramHome', program_home)
        # Icon is in geoprocessor/resources/images/OWF-Logo-Favicon-32x32.png
        # - TODO smalers 2018-07-29 figure out what the optimal logo size is for Qt
        app_util.set_property('ProgramIconPath', program_home + ps + ".." +
                              ps + "resources" + ps + "images" + ps + "OWF-Logo-Favicon-32x32.png")
        app_util.set_property('ProgramLicense', version.app_license)
        # Program name, shown in UI title bars
        app_util.set_property('ProgramName', version.app_name)
        # Program organization and URL, shown in Help / About
        app_util.set_property('ProgramOrganization', version.app_organization)
        app_util.set_property('ProgramOrganizationUrl', version.app_organization_url)
        # Resources are in geoprocessor/resources
        app_util.set_property('ProgramResourcesPath', program_home + ps + ".." + ps + "resources")
        # User documentation URL, without trailing slash
        app_util.set_property('ProgramUserDocumentationUrl',
                              "http://learn.openwaterfoundation.org/owf-app-geoprocessor-python-doc-user")
        # Program version, tracks with release notes
        app_util.set_property('ProgramVersion', version.app_version)
        app_util.set_property('ProgramVersionDate', version.app_version_date)
    except Exception:
        message = "Error setting up program data."
        print(message)
        logger.error(message, exc_info=True)


def setup_logging(session):
    """
    Setup logging for the application.

    Args:
        session:  Application session instance.

    Returns:
        None.
    """
    # Customized logging config using log file in user's home folder
    # - For now use default log levels defined by the utility function
    print("Setting up application logging configuration...")
    initial_file_log_level = logging.DEBUG
    logger = log_util.initialize_logging(app_name="gp", logfile_name=session.get_user_log_file(),
                                         logfile_log_level=initial_file_log_level)

    # Test some logging messages
    message = 'Opened initial log file: "' + session.get_user_log_file() + '"'
    logger.info(message)
    # Also print to the console because normal the console should only have error messages
    print(message)


if __name__ == '__main__':
    """
    Entry point for the OWF GeoProcessor application.
    """
    debug = True
    if debug:
        print_env()

    # Open an application to initialize static UI data
    # - might not be needed in batch mode, but UI may be needed for image manipulation, etc.
    # print("Initializing QApplication")
    # The following should work, and allow passing to run_ui(), but the UI does not open.
    # Instead, declare the application in run_ui(), which works.
    # qtapp = QtWidgets.QApplication(sys.argv)
    # qtapp = QApplication(sys.argv)
    # Set global environment data that will be used by library code
    set_global_data()
    # Set up a session instance
    # - requesting an instance will cause required user files to be created, if they do not exist
    print("Initializing GeoProcessorAppSession...")
    app_session = GeoProcessorAppSession.get_instance(version.app_version_major)
    print("...after initializing GeoProcessorAppSession")

    # Set up logging for the application
    # - A logger is defined for all geoprocessing code.
    # - A default log file is created in the users .owfgp/log folder.
    # - The log file will be closed and another restarted by the StartLog() command.
    setup_logging(app_session)
    logger_main = logging.getLogger(__name__)

    # Parse the command line parameters...
    # - The -h and --help arguments are automatically included so don't need to add below.
    # - The default action is "store" which will save a variable with the same name as the option.
    # - The --version option has special behavior, as documented in the argparse module documentation,
    #   but use a custom print_version() function so can include the license.
    parser = argparse.ArgumentParser(description='GeoProcessor Application')
    # Assigns the command file to args.commands
    # --commands CommandFile.gp
    parser.add_argument("-c", "--commands", help="Specify command file.")
    # Start the http server (will store True in the 'http' variable)
    # --http
    parser.add_argument("--http", action='store_true', help="Start the web server.")
    # Define processor properties on the command line, assumed to be str property
    # -p PropertyName=PropertyValue
    # Evaluate later how to allow values with quotes but maybe shell will handle?
    parser.add_argument("-p", action='append', help="Set a processor property.")
    # Start the user interface (will store True in the 'ui' variable)
    # --ui
    parser.add_argument("--ui", action='store_true', help="Start the user interface.")
    # Print the version using (will store True in the 'version' variable)
    # --version
    parser.add_argument("--version", help="Print program version.", action="store_true")
    args = parser.parse_args()

    # # If handling QGIS environment here, rather than in GeoProcessor
    # # - previously the QGIS set up was done in the GeoProcessor but better to start and stop once
    # # - previously used the following line of code  --->  qgis_util.initialize_qgis(r"C:\OSGeo4W64\apps\qgis")
    try:
        qgs_app = qgis_util.initialize_qgis()
    except Exception as e_app:
        err_message = 'Error initializing QGIS application'
        print(err_message)
        logger_main.error(err_message, exc_info=True)

    # Process configuration parameters
    runtime_properties_cl = {}
    if args.p:
        print("-p options: " + str(args.p))
        runtime_properties_cl = parse_command_line_properties(args.p)

    # Launch a GeoProcessor based on command line parameters that control run mode
    if args.commands:
        # A command file has been specified so run the batch processor.
        print("Running GeoProcessor batch")
        try:
            run_batch(args.commands, runtime_properties_cl)
        except Exception as e_batch:
            err_message = 'Exception running batch'
            print(err_message)
            logger_main.error(err_message, exc_info=True)
    elif args.http:
        # Run the http server
        print("Running GeoProcessor http server")
        try:
            run_http_server()
        except Exception as e_http:
            err_message = 'Exception running http'
            print(err_message)
            logger_main.error(err_message, exc_info=True)
    elif args.ui:
        # Run the user interface
        err_message = "Running GeoProcessor UI"
        print(err_message)
        logger_main.info(err_message)
        try:
            run_ui(app_session)
        except Exception as e_ui:
            err_message = 'Exception running UI (caught "Exception")'
            print(err_message)
            logger_main.error(err_message, exc_info=True)
    elif args.version:
        # Print the version
        print_version()
    else:
        # No arguments given to indicate whether batch, UI, etc. so start up the shell.
        print("Running GeoProcessor shell")
        try:
            run_prompt()
        except Exception as e_prompt:
            err_message = 'Exception running shell'
            print(err_message)
            logger_main.error(err_message, exc_info=True)

    # Exit QGIS environment
    qgis_util.exit_qgis()

    # Close the regression test file
    # - If none is used then nothing is done
    # from geoprocessor.commands.testing.StartRegressionTestResultsReport import StartRegressionTestResultsReport
    StartRegressionTestResultsReport.close_regression_test_report_file()

    # Application exit
    exit(0)
