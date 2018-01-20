"""
This module provides access to the Open Water Foundation GeoProcessor tools via
the gp application, which provides several run modes:

- command shell
- batch (gp --commands CommandFile)
- user interface (gp)
- http server

The initial implementation focuses on batch and command shell.
"""

from geoprocessor.app.GeoProcessorAppSession import GeoProcessorAppSession
from geoprocessor.core.GeoProcessor import GeoProcessor
from geoprocessor.core.CommandFileRunner import CommandFileRunner
import geoprocessor.util.io as io_util
import geoprocessor.util.log as log_util

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


# This is the same as the GeoProcessorCmd.do_run() function.
# - could reuse code but inline it for now
def run_batch(command_file):
    """
    Run in batch mode by processing the specific command file.

    Args:
        command_file (str):  The name of the command file to run, absolute path or relative to the current folder.

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
        runner.run_commands()
    except:
        message = 'Error running command file.'
        print(message)
        traceback.print_exc(file=sys.stdout)
        logger.error(message,exc_info=True)
        return

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

    Returns:

    """
    # TODO smalers 2018-01-01 need to coordinate with Emma on a class for the UI
    print("The GeoProcessor user interface is not implemented.  Exiting...")


def run_steve():
    """
    Hard-coded test for Steve.  Will remove once testing framework is in place.

    Returns:

    """
    # Simulate case where a command file is opened via the command line.
    # First declare a processor.
    geoprocessor = GeoProcessor()
    # For initial development hard-code a command file in memory.
    # TODO smalers 2017-12-23 need to enable testing with command files
    command_file_strings = [
        'Message(Message="Start command file")',
        'SetProperty(PropertyName="Property1",PropertyType="str",PropertyValue="test property")',
        'Message(Message="Test message with Property1=${Property1}")',
        'For(Name="for_outer",IteratorProperty="ForOuterProperty",SequenceStart="1",SequenceEnd="3",SequenceIncrement="1")',
        '  Message(Message="In outer loop, ${ForOuterProperty}")',
        '  For(Name="for_inner",IteratorProperty="ForInnerProperty",SequenceStart="10.0",SequenceEnd="11.5",SequenceIncrement=".5")',
        '    Message(Message="In inner loop")',
        '  EndFor(Name="for_inner")',
        'EndFor(Name="for_outer")',
        'If(Name="if1")',
        '  JunkXXX()',
        'EndIf(Name="if1")',
        'Message(Message="End command file")']
    geoprocessor.set_command_strings(command_file_strings)
    # Run the commands
    geoprocessor.run_commands()
    # Print some information at the end (will display in UI when that is enabled)
    # Print the processor properties
    for property_name in geoprocessor.properties:
        print('Processor property "' + property_name + '="' + str(geoprocessor.properties[property_name]) + '"')


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
    parser.add_argument("-c", "--commands", help="Specify command file.")
    # Start the http server (will store True in the 'http' variable)
    parser.add_argument("--http", action='store_true', help="Start the web server.")
    # Start the user interface (will store True in the 'ui' variable)
    parser.add_argument("--ui", action='store_true', help="Start the user interface.")
    # Immediately prints the version using the 'version' value
    parser.add_argument("--version", help="Print program version.", action="version",
                        version="gp " + __geoprocessor_app_version)
    args = parser.parse_args()

    # Launch a GeoProcessor based on the command line parameters
    if args.commands:
        # A command file has been specified so run the batch processor.
        run_batch(args.commands)
        exit(0)
    elif args.http:
        # Run the http server
        run_http_server()
    elif args.ui:
        # Run the user interface
        run_ui()
    else:
        # No arguments given to indicate whether batch, UI, etc. so start up the shell.
        run_prompt()
        exit(0)

    exit(0)
