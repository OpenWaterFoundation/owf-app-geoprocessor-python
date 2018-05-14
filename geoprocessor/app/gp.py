"""
This module provides access to the Open Water Foundation GeoProcessor tools via
the gp application, which provides several run modes:

- command shell
- batch (gp --commands CommandFile)
- user interface (gp)
- http server

The initial implementation focuses on batch and command shell.
"""

# GeoProcessor modules
from geoprocessor.app.GeoProcessorAppSession import GeoProcessorAppSession
from geoprocessor.core.GeoProcessor import GeoProcessor
from geoprocessor.core.CommandFileRunner import CommandFileRunner
from geoprocessor.commands.testing.StartRegressionTestResultsReport import StartRegressionTestResultsReport
import geoprocessor.util.app_util as app_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.log_util as log_util
import geoprocessor.util.qgis_util as qgis_util
import geoprocessor.util.string_util as string_util

from PyQt4 import QtGui
from geoprocessor.ui.app.launchUI import GeoProcessorUI

# General Python modules
import argparse
import cmd
import getpass
import logging
import os
import platform
import sys
import traceback

__geoprocessor_app_version = "0.0.1"


class GeoProcessorCmd(cmd.Cmd):
    """
    Class to provide GeoProcessor interactive shell.
    The shell prints a prompt and allows geoprocessor commands to be entered.

    See:  https://docs.python.org/2/library/cmd.html
    See:  https://pymotw.com/2/cmd/

    Example commands:  run command-file.gp

    Because the docstrings are usd for user help, documentation for functions is provided in in-lined comments.
    """
    def __init__(self):
        # Old style cmd.Cmd parent class in Python 2.7 does not inherit from object so be careful calling super().
        is_new_style_class = True
        try:
            is_new_style_class = issubclass(cmd.Cmd, object)
        except TypeError:
            is_new_style_class = False
        if is_new_style_class:
            super(GeoProcessorCmd, self).__init__()
        else:
            cmd.Cmd.__init__(self)
        self.prompt = "gp> "

        print('Running GeoProcessor shell')
        print('  - Current working directory is:  ' + os.getcwd())
        print('  - Type help at ' + self.prompt + ' to see options')

    def do_exit(self, line):
        """
        Exit the geoprocessor command shell.
        """
        exit(0)

    def do_printenv(self, line):
        """
        Print information about the runtime environment.
        Run in the shell with:  printenv
        """
        print("Python version (sys.version) = " + sys.version)
        # Print value of environment variables that impact Python, alphabetized.
        # - skip the more esoteric ones
        # - See:  https://docs.python.org/2/using/cmdline.html
        env_vars = ["PYTHONBYTECODE", "PYTHONDEBUG", "PYTHONHOME", "PYTHONHTTPSVERIFY", "PYTHONOPTIMIZE",
                    "PYTHONPATH", "PYTHONSTARTUP", "PYTHONUSERBASE", "PYTHONUSERSITE", "PYTHONVERBOSE"]
        for env_var in env_vars:
            try:
                print(env_var + " = " + os.environ[env_var])
            except:
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
        processor = GeoProcessor()
        print("GeoProcessor properties:")
        for property_name, property_value in processor.properties.iteritems():
            print(property_name + " = " + str(property_value))

    def do_EOF(self, line):
        return True

    def do_run(self, line):
        """
        Run the command file from the command line using syntax:  run command-file
        """
        logger = logging.getLogger("geoprocessor")
        command_file = line
        if command_file is None:
            print('Error:  no command file specified for "run" command.')
        print('Running command file: ' + command_file)
        working_dir = os.getcwd()
        # Convert the command file to an absolute path if not already.
        command_file_absolute = io_util.verify_path_for_os(io_util.to_absolute_path(working_dir, command_file))
        runner = CommandFileRunner()
        # Read the command file
        try:
            runner.read_command_file(command_file_absolute)
        except IOError as e:
            # Would be nice to use FileNotFoundError but that is Python 3.3+
            message = 'Error:  Command file "' + command_file_absolute + '" was not found.'
            print(message)
            logger.exception(message, e)
        except:
            message = 'Error reading command file.'
            logger.error(message)
            print(message)
        # Run the command file
        try:
            runner.run_commands()
        except:
            message = 'Error running command file.'
            print(message)
            traceback.print_exc(file=sys.stdout)
            logger.error(message)

        logger.info("GeoProcessor properties after running:")
        for property_name, property_value in runner.get_processor().properties.iteritems():
            logger.info(property_name + " = " + str(property_value))
        print("See log file for more information.")

    def postloop(self):
        print


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


# This is the same as the GeoProcessorCmd.do_run() function.
# - could reuse code but inline it for now
def run_batch(command_file, runtime_properties):
    """
    Run in batch mode by processing the specific command file.

    Args:
        command_file (str):  The name of the command file to run, absolute path or relative to the current folder.
        runtime_properties (dict):  A dictionary of properties for the processor.

    Returns:
        Nothing.
    """
    logger = logging.getLogger("geoprocessor")
    print('Running command file: ' + command_file)
    working_dir = os.getcwd()
    # Convert the command file to an absolute path if not already.
    logger.info("Working directory=" + working_dir)
    logger.info("Command file=" + command_file)
    command_file_absolute = io_util.verify_path_for_os(io_util.to_absolute_path(working_dir, command_file))
    logger.info("Command file (absolute)=" + command_file_absolute)
    runner = CommandFileRunner()
    # Read the command file
    try:
        runner.read_command_file(command_file_absolute)
    except IOError as e:
        # Would be nice to use FileNotFoundError but that is Python 3.3+
        message = 'Error:  Command file "' + command_file_absolute + '" was not found.'
        print(message)
        logger.exception(message, e)
        return
    except:
        message = 'Error reading command file "' + command_file_absolute + '".'
        traceback.print_exc(file=sys.stdout)
        logger.error(message)
        print(message)
        return
    # Run the command file
    try:
        # Pass the runtime properties to supplement default properties and those created in the command file
        runner.run_commands(env_properties=runtime_properties)
        logger.info("At end of gp.run_batch")
    except:
        message = 'Error running command file.'
        print(message)
        traceback.print_exc(file=sys.stdout)
        logger.error(message, exc_info=True)
        return
    finally:
        StartRegressionTestResultsReport.close_regression_test_report_file()

    logger.info("GeoProcessor properties after running:")
    for property_name, property_value in runner.get_processor().properties.iteritems():
        logger.info(property_name + " = " + str(property_value))
    print("See log file for more information.")


def run_http_server():
    """
    Run an http server so that the geoprocessor can respond to web requests.
    TODO smalers 2017-12-30 need to evaluate whether to use Python built-in capabilities or something like Flask.

    Returns:
        Nothing.
    """
    print("The GeoProcessor web server is not implemented.  Exiting...")


def run_prompt():
    """
    Run the command line prompt interface.

    Returns:
        Nothing.
    """
    GeoProcessorCmd().cmdloop()


def run_ui():
    """
    Run the GeoProcessor user interface.

    Returns: None
    """

    command_processor = GeoProcessor()
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QMainWindow()
    prog = GeoProcessorUI(window, command_processor)
    window.show()
    sys.exit(app.exec_())


def set_global_data():
    """
    Set global data that is useful in library code but is difficult to pass into deep code.
    This may evolve as greater understanding is gained about how to use standard Python modules
    to retrieve application data.

    Returns:
        None
    """
    app_util.program_name = "gp"
    app_util.program_version = __geoprocessor_app_version


def setup_logging(session):
    """
    Setup logging for the application.

    Args:
        session:  Application session instance.

    Returns:
        Nothing.
    """
    # Customized logging config using log file in user's home folder
    # - For now use default log levels defined by the utility function
    print("Setting up customized app logging config")
    initial_file_log_level = logging.DEBUG
    logger = log_util.initialize_logging(app_name="gp", logfile_name=session.get_log_file(),
                                         logfile_log_level=initial_file_log_level)

    # Test some logging messages
    message = 'Opened initial log file: "' + session.get_log_file() + '"'
    logger.info(message)
    # Also print to the console because normal the console should only have error messages
    print(message)


def setup_session(session):
    """
    Setup the application session.  Make sure application folder, etc. are created.

    Args:
        session:  The GeoProcessorAppSession instance to manage the user's session.

    Returns:
        Nothing.
    """
    if not session.create_log_folder():
        logging.warning('Unable to create log folder "' + session.get_log_folder() + '"')
    else:
        # No message since log folder exists.
        pass


if __name__ == '__main__':
    """
    Entry point for the OWF GeoProcessor application.
    """
    # Set up a session instance
    app_session = GeoProcessorAppSession()
    setup_session(app_session)

    # Set up logging for the application
    # - A logger is defined for all geoprocessing code.
    # - A default log file is created in the users .owfgp/log folder.
    # - The log file will be closed and another restarted by the StartLog() command.
    setup_logging(app_session)

    # Parse the command line parameters...
    # - The -h and --help arguments are automatically included so don't need to add below.
    # - The default action is "store" which will save a variable with the same name as the option.
    # - The --version option has special behavior, as documented in the argparse module documentation.
    parser = argparse.ArgumentParser(description='Open Water Foundation (OWF) GeoProcessor Application')
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
    # -ui
    parser.add_argument("--ui", action='store_true', help="Start the user interface.")
    # Immediately prints the version using the 'version' value
    # --version
    parser.add_argument("--version", help="Print program version.", action="version",
                        version="gp " + __geoprocessor_app_version)
    args = parser.parse_args()

    # Set global environment data that will be used by library code
    set_global_data()

    # If handling QGIS environment here, rather than in GeoProcessor
    # - previously the QGIS set up was done in the GeoProcessor but better to start and stop once
    # TODO smalers 2018-01-28 Need to handle the QGIS prefix path dynamically or with software configuration.
    qgis_util.initialize_qgis(r"C:\OSGeo4W\apps\qgis")

    # Process configuration parameters
    runtime_properties = {}
    if args.p:
        print("-p options: " + str(args.p))
        runtime_properties = parse_command_line_properties(args.p)

    # Launch a GeoProcessor based on command line parameters that control run mode
    if args.commands:
        # A command file has been specified so run the batch processor.
        run_batch(args.commands, runtime_properties)
    elif args.http:
        # Run the http server
        run_http_server()
    elif args.ui:
        # Run the user interface
        run_ui()
    else:
        # No arguments given to indicate whether batch, UI, etc. so start up the shell.
        run_prompt()

    # Exit QGIS environment
    qgis_util.exit_qgis()

    # Close the regression test file
    # - If none is used then nothing is done
    StartRegressionTestResultsReport.close_regression_test_report_file()

    # Application exit
    exit(0)
