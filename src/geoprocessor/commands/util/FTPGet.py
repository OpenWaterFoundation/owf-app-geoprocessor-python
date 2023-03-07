# FTPGet - command to retrieve a file from the web
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

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandError import CommandError
from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterError import CommandParameterError
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
from geoprocessor.core.CommandPhaseType import CommandPhaseType
from geoprocessor.core.CommandStatusType import CommandStatusType

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.validator_util as validator_util

import fnmatch
from ftplib import FTP
import logging
import os


class FTPGet(AbstractCommand):
    """
    Downloads one or more files from an ftp site and saves to the local computer.
    """

    # Define the command parameters.
    __command_parameter_metadata: [CommandParameterMetadata] = [
        CommandParameterMetadata("RemoteSite", type("")),
        CommandParameterMetadata("Login", type("")),
        CommandParameterMetadata("Password", type("")),
        CommandParameterMetadata("RemoteFolder", type("")),
        CommandParameterMetadata("FilePattern", int),
        CommandParameterMetadata("IncludeSubfolders", int),
        CommandParameterMetadata("DestinationFolder", type("")),
        CommandParameterMetadata("TransferMode", type("")),
        CommandParameterMetadata("RetryCount", type("")),
        CommandParameterMetadata("RetryWait", type("")),
        CommandParameterMetadata("DryRun", type(""))
    ]

    # Command metadata for command editor display
    __command_metadata = dict()
    __command_metadata['Description'] = "Download one or more files from an FTP site."
    __command_metadata['EditorType'] = "Simple"

    __parameter_input_metadata = dict()
    # RemoteSite
    __parameter_input_metadata['RemoteSite.Description'] = "FTP address for remote site"
    __parameter_input_metadata['RemoteSite.Label'] = "Remote site"
    __parameter_input_metadata['RemoteSite.Tooltip'] =\
        "Specify the FTP site address (e.g., 'ftp.server.com', can use ${Property}."
    __parameter_input_metadata['RemoteSite.Required'] = True
    # Login
    __parameter_input_metadata['Login.Description'] = "case-sensitive"
    __parameter_input_metadata['Login.Label'] = "Login name"
    __parameter_input_metadata['Login.Tooltip'] =\
        "Specify a valid login to access a private FTP site (default is anonymous login)."
    __parameter_input_metadata['Login.Required'] = False
    __parameter_input_metadata['Login.Value.Default'] = 'anonymous'
    # Password
    __parameter_input_metadata['Password.Description'] = "case-sensitive"
    __parameter_input_metadata['Password.Label'] = "Password"
    __parameter_input_metadata['Password.Tooltip'] =\
        "Specify a valid password to access a private FTP site (default is anonymous login)."
    __parameter_input_metadata['Password.Required'] = False
    __parameter_input_metadata['Password.Value.Default'] = 'anonymous'
    # RemoteFolder
    __parameter_input_metadata['RemoteFolder.Description'] = "folder on FTP server"
    __parameter_input_metadata['RemoteFolder.Label'] = "Remote folder"
    __parameter_input_metadata['RemoteFolder.Tooltip'] = "Specify the remote folder, can use ${Property}."
    __parameter_input_metadata['RemoteFolder.Required'] = False
    __parameter_input_metadata['RemoteFolder.Value.Default'] = '/'
    # FilePattern
    __parameter_input_metadata['FilePattern.Description'] = "filename or pattern"
    __parameter_input_metadata['FilePattern.Label'] = "File pattern"
    __parameter_input_metadata['FilePattern.Tooltip'] =\
        "Specify the pattern for files to retrieve, using * for wildcard, can use ${Property}."
    __parameter_input_metadata['FilePattern.Required'] = False
    __parameter_input_metadata['FilePattern.Value.Default'] = "*"
    # IncludeSubfolders
    __parameter_input_metadata['IncludeSubfolders.Description'] = "NOT ENABLED"
    __parameter_input_metadata['IncludeSubfolders.Enabled'] = False
    __parameter_input_metadata['IncludeSubfolders.Label'] = "Include subfolders?"
    __parameter_input_metadata['IncludeSubfolders.Tooltip'] = "Whether to include subfolders."
    __parameter_input_metadata['IncludeSubfolders.Required'] = False
    __parameter_input_metadata['IncludeSubfolders.Values'] = [' ', 'False', 'True']
    __parameter_input_metadata['IncludeSubfolders.Value.Default'] = 'False'
    # DestinationFolder
    __parameter_input_metadata['DestinationFolder.Description'] = ""
    __parameter_input_metadata['DestinationFolder.Label'] = "Destination folder"
    __parameter_input_metadata['DestinationFolder.Tooltip'] = (
        "The output folder (relative or absolute). ${Property} syntax is recognized." )
    __parameter_input_metadata['DestinationFolder.Required'] = True
    __parameter_input_metadata['DestinationFolder.FileSelector.SelectFolder'] = True
    __parameter_input_metadata['DestinationFolder.FileSelector.Type'] = "Write"
    __parameter_input_metadata['DestinationFolder.FileSelector.Filters'] = ["All files (*)"]
    # TransferMode
    __parameter_input_metadata['TransferMode.Description'] = "transfer mode"
    __parameter_input_metadata['TransferMode.Label'] = "Transfer mode"
    __parameter_input_metadata['TransferMode.Tooltip'] = "Transfer mode for files."
    __parameter_input_metadata['TransferMode.Required'] = False
    __parameter_input_metadata['TransferMode.Values'] = [' ', 'Binary', 'Text']
    __parameter_input_metadata['TransferMode.Value.Default'] = 'Binary'
    # RetryCount
    __parameter_input_metadata['RetryCount.Description'] = "NOT ENABLED"
    __parameter_input_metadata['RetryCount.Enabled'] = False
    __parameter_input_metadata['RetryCount.Label'] = "Retry count"
    __parameter_input_metadata['RetryCount.Tooltip'] = "Number of times to retry FTP get."
    __parameter_input_metadata['RetryCount.Required'] = False
    __parameter_input_metadata['RetryCount.Value.Default'] = "3"
    # RetryWait
    __parameter_input_metadata['RetryWait.Description'] = "NOT ENABLED"
    __parameter_input_metadata['RetryWait.Enabled'] = False
    __parameter_input_metadata['RetryWait.Label'] = "Retry wait"
    __parameter_input_metadata['RetryWait.Tooltip'] = "Number of seconds to wait between retries."
    __parameter_input_metadata['RetryWait.Required'] = False
    __parameter_input_metadata['RetryWait.Value.Default'] = "3"
    # DryRun
    __parameter_input_metadata['DryRun.Description'] = "to test"
    __parameter_input_metadata['DryRun.Label'] = "Dry run?"
    __parameter_input_metadata['DryRun.Tooltip'] = "Whether to do a dry run where files are listed but not downloaded."
    __parameter_input_metadata['DryRun.Required'] = False
    __parameter_input_metadata['DryRun.Values'] = [' ', 'False', 'True']
    __parameter_input_metadata['DryRun.Value.Default'] = 'False'

    def __init__(self) -> None:
        """
        Initialize the command.
        """

        # AbstractCommand data
        super().__init__()
        # Name of command for menu and window title
        self.command_name = "FTPGet"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Command metadata for command editor display
        self.command_metadata = self.__command_metadata

        self.parameter_input_metadata = self.__parameter_input_metadata

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters: dict) -> None:
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns: None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning_message = ""

        # Check that required parameters are non-empty, non-None strings.
        required_parameters = command_util.get_required_parameter_names(self)
        for parameter in required_parameters:
            parameter_value = self.get_parameter_value(parameter_name=parameter, command_parameters=command_parameters)
            if not validator_util.validate_string(parameter_value, False, False):
                message = "Required {} parameter has no value.".format(parameter)
                recommendation = "Specify the {} parameter.".format(parameter)
                warning_message += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that the retry count is a number
        # noinspection PyPep8Naming
        pv_RetryCount = self.get_parameter_value(parameter_name='RetryCount', command_parameters=command_parameters)
        if pv_RetryCount is not None:
            if not validator_util.validate_float(pv_RetryCount, False, False):
                message = "RetryCount parameter value {} is not a number.".format(parameter_value)
                recommendation = "Specify a number of retries.".format(parameter)
                warning_message += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check that the retry wait is a number
        # noinspection PyPep8Naming
        pv_RetryCount = self.get_parameter_value(parameter_name='RetryWait', command_parameters=command_parameters)
        if pv_RetryCount is not None:
            if not validator_util.validate_float(pv_RetryCount, False, False):
                message = "RetryWait parameter value {} is not a number.".format(parameter_value)
                recommendation = "Specify a number of seconds.".format(parameter)
                warning_message += "\n" + message
                self.command_status.add_to_log(CommandPhaseType.INITIALIZATION,
                                               CommandLogRecord(CommandStatusType.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning_message = command_util.validate_command_parameter_names(self, warning_message)

        # If any warnings were generated, throw an exception.
        if len(warning_message) > 0:
            self.logger.warning(warning_message)
            raise CommandParameterError(warning_message)
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(CommandPhaseType.INITIALIZATION, CommandStatusType.SUCCESS)

    def check_runtime_data(self, output_file_abs: str) -> bool:
        """
        Checks the following:
        * the output folder is a valid folder

        Args:
            output_file_abs: the full pathname to the output file

        Returns:
            run_ftpget: Boolean. If TRUE, the FTPGet command should be run. If FALSE, it should not be run.
        """

        # Boolean to determine if the ftpget process should be run. Set to true until an error occurs.
        run_ftpget = True

        # If the DestinationFolder is not a valid folder, raise a FAILURE.
        destination_folder = os.path.dirname(output_file_abs)
        if not os.path.isdir(destination_folder):

            run_webget = False
            self.warning_count += 1
            message = 'The destination folder ({}) is not a valid folder.'.format(destination_folder)
            recommendation = 'Specify a valid relative pathname for the destination folder.'
            self.logger.warning(message)
            self.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.FAILURE,
                                                                                  message, recommendation))

        # Return the Boolean to determine if the FTPGet command should be run. If TRUE, all checks passed. If FALSE,
        # one or many checks failed.
        return run_ftpget

    def run_command(self) -> None:
        """
        Run the command. Download the file from the FTP site and save on the local computer.

        Returns:
            None.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        self.warning_count = 0

        # Obtain the parameter values
        # noinspection PyPep8Naming
        pv_RemoteSite = self.get_parameter_value("RemoteSite")
        # noinspection PyPep8Naming
        pv_Login = self.get_parameter_value("Username", default_value=None)
        # noinspection PyPep8Naming
        pv_Password = self.get_parameter_value("Password", default_value=None)
        # noinspection PyPep8Naming
        pv_RemoteFolder = self.get_parameter_value(
            "RemoteFolder", default_value=self.__parameter_input_metadata['RemoteFolder.Value.Default'])
        # noinspection PyPep8Naming
        pv_FilePattern = self.get_parameter_value(
            "FilePattern", default_value=self.__parameter_input_metadata['FilePattern.Value.Default'])
        # noinspection PyPep8Naming
        pv_IncludeSubfolders = self.get_parameter_value(
            "IncludeSubfolders", default_value=self.__parameter_input_metadata['IncludeSubfolders.Value.Default'])
        include_subfolders = False
        if pv_IncludeSubfolders is not None and pv_IncludeSubfolders.upper() == 'TRUE':
            include_subfolders = True
        # noinspection PyPep8Naming
        pv_DestinationFolder = self.get_parameter_value("DestinationFolder")
        # noinspection PyPep8Naming
        pv_TransferMode = self.get_parameter_value(
            "TransferMode", default_value=self.__parameter_input_metadata['TransferMode.Value.Default'])
        if pv_TransferMode == ' ':
            pv_TransferMode = 'Binary'
        # noinspection PyPep8Naming
        pv_RetryCount = self.get_parameter_value(
            "RetryCount", default_value=self.__parameter_input_metadata['RetryCount.Value.Default'])
        # noinspection PyPep8Naming
        pv_RetryWait = self.get_parameter_value(
            "RetryWait", default_value=self.__parameter_input_metadata['RetryWait.Value.Default'])
        pv_DryRun = self.get_parameter_value(
            "DryRun", default_value=self.__parameter_input_metadata['DryRun.Value.Default'])
        dry_run = False
        if pv_DryRun is not None and pv_DryRun.upper() == 'TRUE':
            dry_run = True

        # Expand properties if ${Property} notation is used
        remote_site = self.command_processor.expand_parameter_value(pv_RemoteSite, self)
        remote_folder = self.command_processor.expand_parameter_value(pv_RemoteFolder, self)

        # Convert the DestinationFolder parameter value relative path to an absolute path.
        # Expand for ${Property} syntax.
        destination_folder_absolute = pv_DestinationFolder
        if pv_DestinationFolder:
            destination_folder_absolute = io_util.verify_path_for_os(io_util.to_absolute_path(
                self.command_processor.get_property('WorkingDir'),
                self.command_processor.expand_parameter_value(pv_DestinationFolder, self)))

        # Run the checks on the parameter values. Only continue if the checks passed.
        if self.check_runtime_data(destination_folder_absolute):
            # noinspection PyBroadException
            try:
                # Open a connection
                self.logger.info("Connecting to FTP server:  {}".format(remote_site))
                ftp = FTP(remote_site)

                # Login to the FTP site
                if pv_Login is None or pv_Login == "":
                    # Anonymous
                    self.logger.info("Logging into FTP server using anonymous")
                    ftp.login()
                else:
                    self.logger.info("Logging into FTP server using login and password")
                    ftp.login(pv_Login, pv_Password)

                # Change to the folder on the remote folder
                self.logger.info("Changing to FTP server folder: {}".format(remote_folder))
                ftp.cwd(remote_folder)

                # Retrieve files

                #root_dirs = ftp.nlst()
                #facts = ['type']
                #root_dirs = ftp.mlsd(facts=facts)
                remote_list = ftp.mlsd(path=remote_folder)
                download_count = 0
                for name, facts in remote_list:
                    # self.logger.info('Remote server folder contains:  {} {}'.format(name, facts))
                    if name == "." or name == "..":
                        # Don't process special folders
                        continue
                    local_dir = os.path.join(destination_folder_absolute)
                    file_type = facts['type']
                    if file_type == 'file':
                        # See if it matches and if so download
                        if fnmatch.fnmatch(name, pv_FilePattern):  # cannot use glob.glob
                            self.logger.info("File pattern matched, downloading:")
                            remote_path = remote_folder + "/" + name
                            local_filename = os.path.join(local_dir, name)
                            self.logger.info("  remote:  {}".format(remote_path))
                            self.logger.info("   local:  {}".format(local_filename))
                            if dry_run:
                                self.logger.info('Dry run:  RETR ' + remote_path)
                            else:
                                # Download the file by opening a local file.
                                # The open file's 'write' function is called to write.
                                if pv_TransferMode == 'Binary':
                                    open_mode = 'wb'
                                else:
                                    open_mode = 'w'
                                # 'with' will automatically close the file
                                with open(local_filename, open_mode) as fh:
                                    try:
                                        ftp.retrbinary('RETR ' + remote_path, fh.write)
                                    except ftp.all_errors:
                                        self.logger.error("Error getting file.", exc_info=True)
                                # Increment the download count
                                download_count += 1
                    elif file_type == 'cdir':
                        # Create directory
                        # - TODO smalers 2020-08-22 need to enable and recurse
                        # if not os.path.exists(local_dir):
                        #    self.logger.info("Creating local folder:  {}".format(local_dir))
                        #    if not dry_run:
                        #        os.mkdir(local_dir)
                        pass

                # Quit the FTP session
                ftp.quit()

                self.logger.info("Downloaded {}".format(download_count) + " files.")

            except Exception:
                # Raise an exception if an unexpected error occurs during the process
                self.warning_count += 1
                message = "Unexpected error downloading file from FTP site {}.".format(pv_RemoteSite)
                recommendation = "Check the log file for details."
                self.logger.warning(message, exc_info=True)
                self.command_status.add_to_log(CommandPhaseType.RUN, CommandLogRecord(CommandStatusType.FAILURE,
                                                                                      message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if self.warning_count > 0:
            message = "There were {} warnings processing the command.".format(self.warning_count)
            raise CommandError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(CommandPhaseType.RUN, CommandStatusType.SUCCESS)
