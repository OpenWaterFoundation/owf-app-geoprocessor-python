# GeoProcessorAppSession - class to manage GeoProcessor session
# ________________________________________________________________NoticeStart_
# GeoProcessor
# Copyright (C) 2017-2023 Open Water Foundation
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

# The following is needed to allow type hinting -> GeoProcessorAppSession, and requires Python 3.7+
# See:  https://stackoverflow.com/questions/33533148/
#         how-do-i-specify-that-the-return-type-of-a-method-is-the-same-as-the-class-itsel
from __future__ import annotations

import getpass
import logging
import os
from pathlib import Path

import geoprocessor.util.io_util as io_util


class GeoProcessorAppSession(object):
    """
    Manage the session, such as saving the application state.
    The number below is the major software version.

    The $HOME/.owf-gp/1/command-file-history.txt file contains a list of recently opened or saved command files,
    with format shown below (paths will be consistent with the operating system, in the case below for Cygwin):

    The user session files are:

    C:/Users/user/.owf-gp/1/         # Windows
    $HOME/.owf-gp/1/                 # Linux
       command-file-history.txt
       logs/
    """

    # Private singleton instance (class data).
    _instance: GeoProcessorAppSession = None

    def __init__(self, app_major_version: int) -> None:
        """
        Constructor.
        """

        # Major version for software, used to locate files in home folder.
        self.app_major_version = app_major_version

    def create_user_logs_folder(self) -> bool:
        """
        Create the user logs folder where the application log file lives.

        Returns:
            True if the creation is successful, False if not.
        """
        log_folder = self.get_user_logs_folder()
        # Do not allow log file to be created under Linux root but allow the application to run.
        if log_folder == "/":
            return False

        if not os.path.exists(log_folder):
            try:
                os.makedirs(log_folder)
            except OSError:
                return False
        else:
            # Make sure it is writeable.
            if not os.access(log_folder, os.W_OK):
                return False
        return True

    def create_user_tmp_files_to_remove_folder(self):
        """
        Create the folder containing temporary files to remove.
        Each file in the folder contains the path of the true temporary file to remove.
        The files are sometimes locked during a session and can only be removed when the next session starts.

        Returns:
            True if the creation is successful, False if not.
        """
        tmp_folder = self.get_user_tmp_files_to_remove_folder()
        # Do not allow log file to be created under Linux root but allow the application to run.
        if tmp_folder == "/":
            return False

        if not os.path.exists(tmp_folder):
            try:
                os.makedirs(tmp_folder)
            except OSError:
                return False
        else:
            # Make sure it is writeable.
            if not os.access(tmp_folder, os.W_OK):
                return False
        return True

    def get_history_file(self) -> str:
        """
        Get the name of the command history file for the user.

        Returns:
            The name of the history file.
        """
        history_file = os.path.join(self.get_user_app_major_version_folder(), "command-file-history.txt")
        logging.info('Command file history is"' + history_file + '"')
        return history_file

    @classmethod
    def get_instance(cls, app_major_version: int = None) -> GeoProcessorAppSession:
        """
        Return a singleton instance.

        Returns:
            Singleton instance of GeoProcessorAppSession
        """
        if cls._instance is None:
            # None instance because called the first time, so create an instance.
            cls._instance = GeoProcessorAppSession(app_major_version=app_major_version)
        # Else an instance exists so can use it:
        # - the following won't do anything if already initialized
        cls._instance.initialize_user_files()

        return cls._instance

    def get_app_major_version(self) -> int:
        """
        Get the major version for the software, as an integer.

        Returns:
            Major version for the software.
        """
        return self.app_major_version

    def get_user_app_folder(self) -> str:
        """
        Get the name of the application folder for the user.

        Returns:
            The name of the folder for user geoprocessor application files.
        """
        app_folder = os.path.join(self.get_user_folder(), ".owf-gp")
        logging.info('Application folder for user is "' + app_folder + '"')
        return app_folder

    def get_user_app_major_version_folder(self) -> str:
        """
        Get the major version folder for application user files.

        Returns:
            The major version folder for application user files.
        """
        major_user_app_folder = os.path.join(self.get_user_app_folder(), str(self.get_app_major_version()))
        return major_user_app_folder

    def get_user_folder(self) -> str:
        """
        Return the name of the user folder for the operating system, for example:
            Windows:  C:\\Users\\UserName\\.owfgp
            Linux: /home/UserName/.owfgp

        Returns:
            The name of the user folder.
        """
        user_folder = os.path.expanduser("~")
        logging.info('User folder is "' + user_folder + '"')
        return user_folder

    def get_user_log_file(self) -> str:
        """
        Get the name of the log file for the user.

        Returns:
            The name of the log file.
        """
        log_file = os.path.join(self.get_user_logs_folder(), "gp_" + getpass.getuser() + ".log")
        logging.info('Log file for user is "' + log_file + '"')
        return log_file

    def get_user_logs_folder(self) -> str:
        """
        Get the name of the log file folder for the user.

        Returns:
            The name of the folder for user log files.
        """
        logs_folder = os.path.join(self.get_user_app_major_version_folder(), "logs")
        logging.info('Logs folder for user is "' + logs_folder + '"')
        return logs_folder

    def get_user_tmp_files_to_remove_folder(self) -> str:
        """
        Get the name of the folder containing fils with temporary files to remove.

        Returns:
            The name of the folder for user temporary files to remove.
        """
        tmp_folder = os.path.join(self.get_user_app_major_version_folder(), "tmp-files-to-remove")
        logging.info('Folder for user temporary files to remove is "' + tmp_folder + '"')
        return tmp_folder

    def initialize_user_files(self) -> bool:
        """
        Initialize user files.
        This method should be called at application startup by calling 'get_instance()' to make sure that
        user files are created.
        The following summarizes the file structure:

            C:/Users/user/              # Windows user folder
            /home/user/                 # Linux user folder
                .owf-gp/
                    1/
                        logs/
                            gp-user.log
                        tmp-files-to-remove/   # list of files that need to be removed at startup, from previous session
                            file1
                            file2
                    2/
                        ... next major version's files ...

        The use of a version folder is a design compromise.
        Users will need to use migration tools to import previous version configuration.
        The version folder allows different major versions of software to remain functional
        if major design changes occur.

        Returns:
            True if initialization was successful, False if initialization failed.
        """
        logger = logging.getLogger(__name__)
        user_folder = self.get_user_app_folder()
        return_status = True
        if user_folder == "/":
            # Don't allow files to be created under root on Linux.
            logger.warning("Unable to create user files in / (root) folder - need to run as a normal user.")
            return_status = False

        # If OK so far, continue.
        if return_status:
            # Create the version folder if it does not exist.
            if not os.path.exists(user_folder):
                # The following gets rid of IDE warning about catching Exception, which is considered "too broad".
                # noinspection PyBroadException
                try:
                    os.mkdir(user_folder)
                except Exception:
                    logger.warning("Could not create application user folder \"" + user_folder + "\"",
                                   exc_info=True)
                    return_status = False
            else:
                # Make sure it is writeable.
                if not os.access(user_folder, os.W_OK):
                    logger.warning("Application user folder \"" + user_folder + "\" is not writeable.")
                    return_status = False

            # If OK so far, continue.
            if return_status:
                version_folder = self.get_user_app_major_version_folder()
                if not os.path.exists(version_folder):
                    # The following gets rid of IDE warning about catching Exception, which is considered "too broad".
                    # noinspection PyBroadException
                    try:
                        os.mkdir(version_folder)
                    except Exception:
                        logger.warning("Could not create application user files version folder \"" +
                                       version_folder + "\"", exc_info=True)
                        return_status = False
                else:
                    # Version folder exists.
                    # Make sure it is writeable.
                    if not os.access(version_folder, os.W_OK):
                        logger.warning("Application user files version folder \"" + version_folder +
                                       "\" is not writeable.")
                        return_status = False

                if return_status:
                    # Check/create main folders under the version folder:
                    # - if folders already exist, True will be returned

                    # Check/create the 'logs' folder.
                    if not self.create_user_logs_folder():
                        logger.warning("Could not create application log files folder \"" +
                                       self.get_user_logs_folder_folder + "\"", exc_info=True)
                        return_status = False

                    # Check/create the folder for temporary files that need to be removed.
                    if not self.create_user_tmp_files_to_remove_folder():
                        logger.warning("Could not create application user tmp files to remove folder \"" +
                                       self.get_user_tmp_files_to_remove_folder() + "\"", exc_info=True)
                        return_status = False

                    else:
                        # Set the path in io_util so it can save files there without knowing about application.
                        io_util.tmp_files_to_remove_folder = self.get_user_tmp_files_to_remove_folder()

        # Always attempt to remove temporary files from the previous session:
        # - necessary because they were locked at the time the GeoProcessor was previously run
        # - call this in the main application after logging has been set up
        # self.remove_user_tmp_files()

        # Return the status:
        # - should be True if no issues or False if some issue occurred that may need attention
        return return_status

    def push_history(self, command_file: str) -> None:
        """
        Push a new command file onto history. This reads the history, updates it, and writes it.
        The new file is added at the top, corresponding to the most recent file.
        This is done because if multiple GeoProcessor sessions are running, they will share history.

        Args:
            command_file:
                 Full path to command file that has been opened.

        Returns:
            None
        """

        # Read the history file from the .geoprocessor file.
        history = self.read_history()
        # Add in the first position so it will show up first in the File... Open... menu.
        history.insert(0, command_file)

        # print("Command File: " + command_file)

        # Process from back so that old duplicates are removed and recent access is always at the top of the list.
        # print("History before loop: " +  str(history))
        max_files = 100
        for i in reversed(list(range(0, len(history)))):
            if i >= 1:
                old = history[i]
                if i >= max_files:
                    # Trim the history to the maximum.
                    del history[i]
                elif old == command_file or old == '' or old.startswith("#"):
                    # Ignore comments, blank lines and duplicate to most recent access.
                    del history[i]
                    i -= 1
        self.write_history(history)

    def read_history(self) -> [str]:
        """
        Read the history of command files that have been opened.

        Returns:
            The list of command files recently opened, newest first, with comments removed.
        """

        # history_list = list(history.splitlines())

        # for line in history_list:
        #    if(line.startswith("#")):
        #        history_list.remove(line)

        # print(history_list)

        f = None
        # The following gets rid of IDE warning about catching Exception, which is considered "too broad".
        # noinspection PyBroadException
        try:
            with open(self.get_history_file()) as f:
                history = f.read().splitlines()
                for line in history:
                    if line.startswith("#"):
                        # Remove comments.
                        history.remove(line)
                return history
        except Exception:
            # For now just swallow exception, which may be because the history folder does not exist.
            # message = 'Exception opening command file history'
            # print(message)
            # logging.warning(message, exc_info=True)
            return []
        finally:
            # Close the history file.
            if f is not None:
                f.close()

    def remove_user_tmp_files(self) -> int:
        """
        Remove temporary files that were left over from a previous session and could not be removed because they
        were locked.

        Returns:
            (int) number of files removed.
        """
        logger = logging.getLogger(__name__)
        tmp_folder = self.get_user_tmp_files_to_remove_folder()
        logger.info("Removing tmp files from previous session tracked by files in: {}".format(tmp_folder))
        tmp_file_count = 0
        tmp_file_removed_count = 0

        # List the files in the temporary folder:
        # - see:  https://mkyong.com/python/python-how-to-list-all-files-in-a-directory/
        for r, d, f in os.walk(tmp_folder):
            # Process the files in the folder.
            for file in f:
                # logger.info("Processing tmp file: {}".format(f))
                # Get the full path to the file.
                tracker_path = Path(os.path.join(r,file))
                # Read the contents of the file, which include the path to a temporary file to remove.
                tmp_file_lines = io_util.read_file(tracker_path, comment='#', return_comments=False)
                if len(tmp_file_lines) > 0:
                    tmp_file = tmp_file_lines[0]
                    tmp_file_count += 1
                    # Remove the temporary file.
                    # logger.info("tmp file to remove: {}".format(tmp_file))
                    tmp_file_path = Path(tmp_file)
                    # Whether to remove the tracker.
                    do_remove_tracker = False
                    if tmp_file_path.exists():
                        # noinspection PyBroadException
                        try:
                            tmp_file_path.unlink()
                            tmp_file_removed_count += 1
                            logger.info("Removed tmp file from previous session: {}".format(tmp_file))
                            do_remove_tracker = True
                        except Exception:
                            logger.warning("Could not remove temporary file from previous session: {}".format(
                                           tmp_file))
                    else:
                        # Temporary file to remove does not exist.  It must have been removed already.
                        logger.info("tmp file from previous session does not exist: {}".format(tmp_file))
                        do_remove_tracker = True
                    if do_remove_tracker:
                        # Remove the tracker file.
                        # noinspection PyBroadException
                        try:
                            tracker_path.unlink()
                            logger.info("Removed tmp file tracker file: {}".format(tracker_path))
                        except Exception:
                            logger.warning("Could not remove tmp file tracker (will waste disk space): {}".
                                           format(tracker_path))
        logger.info("Removed {} of {} tmp files from previous session.".format(tmp_file_removed_count, tmp_file_count))
        return tmp_file_removed_count

    def write_history(self, history_list: [str]) -> None:
        """
        Write the history of command files that have been opened.

        :param history_list: a list of strings representing the history of command files
        """

        # Don't allow files to be created under root on Linux(?).

        # History being written (?).

        string_builder =\
            "# GeoProcessor command file history, most recent at top, shared between GeoProcessor instances\n"

        # The following gets rid of IDE warning about catching Exception, which is considered "too broad".
        # noinspection PyBroadException
        try:
            for s in history_list:
                string_builder += s + "\n"
            # Create the history folder if necessary.
            f = open(self.get_history_file(), "w")
            folder = os.path.abspath(os.path.join(self.get_history_file(), '..'))
            if not os.path.exists(folder):
                if not os.makedirs(folder):
                    # Unable to make folder
                    return
            # The following gets rid of IDE warning about catching Exception, which is considered "too broad".
            # noinspection PyBroadException
            try:
                f.write(string_builder)
                f.close()
            except Exception:
                # Absorb exception for now.
                pass
        except Exception:
            message = 'Exception writing command file history'
            print(message)
            logging.warning(message, exc_info=True)
