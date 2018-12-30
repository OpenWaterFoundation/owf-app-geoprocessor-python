# log_util - utility functions for logging
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2019 Open Water Foundation
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
This module provides logging utilities for the geoprocessor package.
The module is named 'log_util' to avoid conflicts with the standard Python 'logging' module.
Useful resources are:

    Python 2 logging module:  https://docs.python.org/2/library/logging.html
    Hitchhiker's Guide to Python:  http://docs.python-guide.org/en/latest/writing/logging/
    Exceptional logging of exceptional in Python:
        https://www.loggly.com/blog/exceptional-logging-of-exceptions-in-python/

TODO smalers 2018-01-01 It may be useful to use different formatters for different levels, see:
https://stackoverflow.com/questions/28635679/python-logging-different-formatters-for-the-same-log-file

"""

import datetime
import getpass
import logging
import os
import platform

# The name of the current log file, will be reset by functions below
__logfile_name = None


def get_logfile_name():
    """
    Get the name of the logfile that is currently being used.

    Returns:
        The name of the current logfile, or None if not used.
    """
    global __logfile_name
    return __logfile_name


def initialize_logging(app_name=None, logfile_name=None, logfile_log_level=logging.INFO,
                       console_log_level=logging.ERROR):
    """
    Initialize logging for the geoprocessor, using the Python logging module.
    This function can be called by applications to set up the initial logfile.
    Later, the StartLog command can be used to reset the log file to a new file.
    Named parameters should be used to ensure proper handling of parameters.
    The following is configured:

    Logger:
        - logger name is "geoprocessor" so that all modules can inherit
          (consequently, using the logger from a main application should request logger "geoprocessor"
          since the __name__ will be '__main__').
        - log formatter = '%(levelname)s|%(module)s line %(lineno)d|%(message)s'
          By default the format does not include the date/time because this eats up log file space.
          If necessary, print the time to indicate start/end of processing.
        - FileHandler is initialized corresponding to logfile_name with level INFO.

    Args:
        app_name (str):           Name of the application, written to top of log file.
        logfile_name (str):       Name of the initial log file, None indicates no logfile.
        logfile_log_level (int):  The logging level for the log file (default is logging.INFO).
        console_log_level (int):  Console log level (default is logging.ERROR),
                                  use logging.NOTSET for no console logging.

    Returns:
        The logger that is created.
    """
    log_formatter = logging.Formatter('%(levelname)s|%(name)s|%(module)s line %(lineno)d|%(message)s')

    # Request a logger for the geoprocessor (gp), which will create a new logger since not previously found.
    # - Use "geoprocessor" for the name, which matches the top-level package name.
    #   All requests in library code using __name__ will therefore match the root module name.
    # - This also allows the __main__ program to request a logger with name "geoprocessor" so that
    #   messages can be written to the same log file.
    logger_name = "geoprocessor"
    logger = logging.getLogger(logger_name)

    # Set the logger level to DEBUG because it needs to handle all levels
    # - If this is not set then the default of WARNING will control
    logger.setLevel(logging.DEBUG)

    # Configure the logger handlers below, which indicate how to output log messages if they
    # pass through the logger.

    # Configure the log file handler
    if logfile_name is not None:
        # Use mode 'w' to restart the log because default is append 'a'.
        log_file_handler = logging.FileHandler(logfile_name, mode='w')
        log_file_handler.setLevel(logfile_log_level)
        log_file_handler.setFormatter(log_formatter)
        logger.addHandler(log_file_handler)
        # Save the logfile as a module variable
        global __logfile_name
        __logfile_name = logfile_name

    # Configure the console handler, which defaults to stderr
    # - This is OK for startup but once a StartLog command is used the console handler should not be used
    # - Console output defaults to WARNING and worse
    if console_log_level != logging.NOTSET:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_log_level)
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

    # Print some messages to logging so that the application, user, etc. are known
    if app_name is None:
        logger.info("Application = unknown")
    else:
        logger.info("Application = " + app_name)
    logger.info("Date/time = " + str(datetime.datetime.now()))
    logger.info("User = " + getpass.getuser())
    logger.info("Machine = " + platform.node())
    logger.info("Folder = " + os.getcwd())

    return logger


def reset_log_file_handler(logfile_name):
    """
    Close the current log file handler and re-open using the specified log file name
    for the logger named 'geoprocessor', which is associated with the geoprocessor package.
    This is used, for example, by the StartLog command to switch logging to another file.

    Args:
        logfile_name: Name of the log file to use for logging, needs to be absolute path to be robust.

    Returns:
        Nothing

    Raises:
        Run

    """
    # Get the GeoProcessor logging handler
    # - the logger should have been set up initially by the application by calling initialize_logging()

    logger = logging.getLogger("geoprocessor")

    # Loop through the handlers on the "geoprocessor" logger and replace the FileHandler logger.
    # - there should only be one such handler

    found_handler = None
    # Defaults are the same as in the initialize_logging() function
    old_log_file_handler_level = logging.INFO
    old_log_file_handler_formatter = logging.Formatter('%(levelname)s|%(name)s|%(module)s line %(lineno)d|%(message)s')
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            old_log_file_handler_level = handler.level
            old_log_file_handler_formatter = handler.formatter
            found_handler = handler
            break

    if found_handler:
        # Found an old FileHandler so remove it first
        # - the following message will show up in the old log file
        message = 'Closing the old file so new log file can be used: "' + logfile_name + '"'
        logger.info(message)
        # Remove the old FileHandler
        found_handler.close()
        logger.removeHandler(found_handler)

    # Whether or not a handler was found, always create a new FileHandler using the information determined from above
    new_log_file_handler = logging.FileHandler(logfile_name, mode='w')
    new_log_file_handler.setLevel(old_log_file_handler_level)
    new_log_file_handler.setFormatter(old_log_file_handler_formatter)
    logger.addHandler(new_log_file_handler)

    # Save the logfile name in the module data
    global __logfile_name
    __logfile_name = logfile_name

    # The following message will show up in the new log file
    message = 'Opened new log file: "' + logfile_name + '"'
    print('Opened new log file: "' + logfile_name + '"')
    logger.info(message)
