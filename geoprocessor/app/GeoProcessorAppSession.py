# Class to manage GeoProcessor session

import getpass
import logging
import os


class GeoProcessorAppSession(object):
    """
    Manage the session, such as saving the application state.
    This is a port of the Java TSToolSession class.
    """
    def __init__(self):
        pass

    def create_log_folder(self):
        """
        Create the folder where the application log file lives.

        Returns:
            True if the creation is successful, False if not.
        """
        log_folder = self.get_log_folder()
        # Do not allow log file to be created under Linux root but allow the application to run
        if  log_folder == "/":
            return False

        if not os.path.exists(log_folder):
            try:
                os.makedirs(log_folder)
            except OSError as e:
                return False
        else:
            # Make sure it is writeable
            if not os.access(log_folder, os.W_OK):
                return False
        return True

    def get_app_folder(self):
        """
        Get the name of the application folder for the user.

        Returns:
            The name of the folder for user geoprocessor application files.
        """
        app_folder = os.path.join(self.get_user_folder(),".owf-gp")
        logging.info('Application folder is "' + app_folder + '"');
        return app_folder

    def get_log_file(self):
        """
        Get the name of the log file for the user.

        Returns:

        """
        log_file = os.path.join(self.get_log_folder(), "gp_" + getpass.getuser() + ".log")
        logging.info('Log file is "' + log_file + '"')
        return log_file;

    def get_log_folder(self):
        """
        Get the name of the log file folder for the user.
        
        Returns:
            The name of the folder for user log files.
        """
        log_folder = os.path.join(self.get_app_folder(),"log")
        logging.info('Log folder is "' + log_folder + '"');
        return log_folder

    def get_user_folder(self):
        """
        Return the name of the user folder for the operating system, for example:
            Windows:  C:\Users\UserName\.owfgp
            Linux: /home/UserName/.owfgp

        Returns:

        """
        user_folder = os.path.expanduser("~")
        logging.info('User folder is "' + user_folder + '"')
        return user_folder