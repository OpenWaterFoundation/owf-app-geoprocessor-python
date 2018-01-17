# WebGet

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command as command_util
import geoprocessor.util.io as io_util
import geoprocessor.util.validators as validators

import logging
import os
import requests
import StringIO
import zipfile



class WebGet(AbstractCommand):

    """
    Downloads a file from a web url.

    This command downloads a file on the web and saves it on the local computer. There is a parameter that allows zip
    files to be downloaded and automatically unzipped.
    """

    # Command Parameters
    # FileURL (str, required): the URL of the file to be downloaded
    # OutputFile (str, required): the relative pathname of the output file
    # IsZipFile (str, required):
    # IfZipFile (str, optional): This parameter determines the action that occurs if the downloaded file is a .zip file.
    #   Available options are: `UnzipAndRemove`, `UnzipAndSave` and `Ignore` (Refer to user documentation for detailed
    #   description.) Default value is `UnzipAndSave`.
    __command_parameter_metadata = [
        CommandParameterMetadata("FileURL", type("")),
        CommandParameterMetadata("OutputFile", type("")),
        CommandParameterMetadata("IsZipFile", type(True)),
        CommandParameterMetadata("IfZipFile", type(""))]

    def __init__(self):
        """
        Initialize the command.
        """

        super(WebGet, self).__init__()
        self.command_name = "WebGet"
        self.command_parameter_metadata = self.__command_parameter_metadata

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns:
            Nothing.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning = ""
        logger = logging.getLogger(__name__)

        # Check that parameter FileURL is a non-empty, non-None string.
        # - existence of the url will also be checked in run_command().
        pv_FileURL = self.get_parameter_value(parameter_name='FileURL',
                                              command_parameters=command_parameters)

        if not validators.validate_string(pv_FileURL, False, False):

            message = "FileURL parameter has no value."
            recommendation = "Specify the FileURL parameter to indicate the URL of the file to download."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that parameter OutputFile is a non-empty, non-None string.
        # - existence of the flder will also be checked in run_command().
        pv_OutputFile = self.get_parameter_value(parameter_name='OutputFile',
                                                 command_parameters=command_parameters)

        if not validators.validate_string(pv_OutputFile, False, False):

            message = "OutputFile parameter has no value."
            recommendation = "Specify the OutputFile parameter to indicate the output file."
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check that optional parameter IfZipFile is either `UnzipAndRemove`, `UnzipAndSave`, `Ignore` or None.
        pv_IfZipFile = self.get_parameter_value(parameter_name="IfZipFile",
                                                command_parameters=command_parameters)
        acceptable_values = ["UnzipAndRemove", "UnzipAndSave", "Ignore"]
        if not validators.validate_string_in_list(pv_IfZipFile, acceptable_values, none_allowed=True,
                                                  empty_string_allowed=True, ignore_case=True):

            message = "IfZipFile parameter value ({}) is not recognized.".format(pv_IfZipFile)
            recommendation = "Specify one of the acceptable values ({}) for the IfZipFile parameter.".format(
                acceptable_values)
            warning += "\n" + message
            self.command_status.add_to_log(
                command_phase_type.INITIALIZATION,
                CommandLogRecord(command_status_type.FAILURE, message, recommendation))

        # Check for unrecognized parameters.
        # This returns a message that can be appended to the warning, which if non-empty triggers an exception below.
        warning = command_util.validate_command_parameter_names(self, warning)

        # If any warnings were generated, throw an exception.
        if len(warning) > 0:
            logger.warning(warning)
            raise ValueError(warning)
        else:
            # Refresh the phase severity
            self.command_status.refresh_phase_severity(command_phase_type.INITIALIZATION, command_status_type.SUCCESS)

    @staticmethod
    def __is_downloadable(url):
        """
        Does the url contain a downloadable resource. This code was copied from the following resource:
            https://www.codementor.io/aviaryan/downloading-files-from-urls-in-python-77q3bs0un

        Args:
            url: the url to a file that is to be checked for downloading capabilities

        Returns:
            Boolean.
                Returns True if the file can be downloaded with the requests library.
                Returns False if the file cannot be downloaded with the requests library.

        Raises:
            None.
        """

        h = requests.head(url, allow_redirects=True)
        header = h.headers
        content_type = header.get('content-type')
        if 'text' in content_type.lower():
            return False
        if 'html' in content_type.lower():
            return False
        return True

    @ staticmethod
    def __is_zipfile(response_object):
        """
        Checks if a request response object is of zip file format.

        Args:
            response_object: the request response object to check. For more information on request response objects,
                refer to `http://docs.python-requests.org/en/master/api/`

        Returns:
            Boolean. True if request response object is a zip file format. False if request response object is not a
            zip file format.

        Raises:
            None.
        """

        # The following comment is in place to make PyCharm skip review of the exception clause. Without this comment,
        # PyCharm raises error "Too broad exception clause"
        # noinspection PyBroadException
        try:
            zipfile.ZipFile(StringIO.StringIO(response_object.content))
            return True

        except:
            return False

    @ staticmethod
    def __rename_files_in_a_folder(list_of_files, folder_path, new_filename):
        """

        Renames files within a folder to a new name. The files retain their pathname (they stay in the same folder)
        and retain their file extension.

        Args:
            list_of_files (list of strings): a list of filenames (without the path but WITH the extension)
            folder_path (string): the full pathname to the folder that is storing the files in the list_of_files list
            new_filename (string): the new filename for the files in the list_of_files list. All files will be renamed
                to this same value.

        Returns:
             None.

        Raises:
            None.
        """

        # Iterate over the files to be renamed.
        for existing_file in list_of_files:

            # Get the full path of the existing file
            existing_path = os.path.join(folder_path, existing_file)

            # Get the filename and the file extension of the existing file
            existing_filename, existing_extension = os.path.splitext(existing_file)

            # Create the full path of the renamed file. If an extension was included in the original filename, then that
            # same extension is included in the new filename.
            new_path = os.path.join(folder_path, "{}{}".format(new_filename, existing_extension))
            os.rename(existing_path, new_path)

    def run_command(self):
        """
        Run the command. Download the file from the web and save it on the local computer. Handle zip files as
        pre-determined by the IfZipFile parameter value.

        Args:
            None.

        Returns:
            Nothing.

        Raises:
            RuntimeError if any warnings occurred during run_command method.
        """

        # Set up logger and warning count
        warning_count = 0
        logger = logging.getLogger(__name__)

        # Obtain the parameter values
        pv_FileURL = self.get_parameter_value("FileURL")
        pv_OutputFile = self.get_parameter_value("OutputFile")
        pv_IfZipFile = self.get_parameter_value("IfZipFile", default_value="UnzipAndSave")

        # Check if the provided URL is a file that is downloadable.
        if self.__is_downloadable(pv_FileURL):

            # Convert the OutputFile parameter value relative path to an absolute path. Expand for ${Property} syntax.
            output_file_absolute = io_util.verify_path_for_os(io_util.to_absolute_path(
                self.command_processor.get_property('WorkingDir'),
                self.command_processor.expand_parameter_value(pv_OutputFile, self)))

            # Get the output folder for the output file
            output_folder = os.path.dirname(output_file_absolute)

            # Check that the output folder is a valid folder
            if os.path.isdir(output_folder):

                try:
                    # Get the URL file and convert it into a request Response object
                    r = requests.get(pv_FileURL)

                    # Get the filename and the extension of the file URL
                    url_filename, url_extension = os.path.splitext(os.path.basename(pv_FileURL))

                    # Get the filename and the extension for the output file
                    output_filename, output_extension = os.path.splitext(os.path.basename(pv_OutputFile))

                    # If the URL file is a zip file, process as a zip file.
                    if self.__is_zipfile(r):

                        # Read in the url file as a zip file object.
                        zipfile_obj = zipfile.ZipFile(StringIO.StringIO(r.content))

                        # Create an empty list to hold the files that were downloaded/extracted to the output folder.
                        downloaded_files = []

                        # If the `IfZipFile` parameter is set to UnzipAndRemove, extract all of the archived members
                        # within the URL zip file and save the contents to the specified output folder. Do not save the
                        # .zip file to the output folder.
                        if pv_IfZipFile.upper() == "UNZIPANDREMOVE":
                            zipfile_obj.extractall(output_folder)
                            downloaded_files.extend(zipfile_obj.namelist())

                        # If the `IfZipFile` parameter is set to UnzipAndSave, extract all of the archived members
                        # within the URL zip file and save the contents to the specified output folder. Also, save the
                        # .zip file to the output folder.
                        elif pv_IfZipFile.upper() == "UNZIPANDSAVE":
                            zipfile_obj.extractall(output_folder)
                            downloaded_files.extend(zipfile_obj.namelist())
                            with open(os.path.join(output_folder, "{}.zip".format(url_filename)), "wb") as downloaded_zip_file:
                                downloaded_zip_file.write(r.content)
                            downloaded_files.append("{}.zip".format(url_filename))

                        # If the `IfZipFile` parameter is set to Ignore, only download the .zip file.
                        else:
                            with open(os.path.join(output_folder, "{}.zip".format(url_filename)), "wb") as downloaded_zip_file:
                                downloaded_zip_file.write(r.content)
                            downloaded_files.append("{}.zip".format(url_filename))

                        # Determine if the downloaded zip file(s) should be renamed. If the filename is %f then the
                        # filenames of the downloaded products should be the same as the url filenames
                        if not output_filename == '%f':
                            self.__rename_files_in_a_folder(list_of_files=downloaded_files, folder_path=output_folder,
                                                            new_filename=output_filename)

                    # If the URL file is a single file (a non-zip file), process accordingly.
                    else:

                        # Download the file to the output folder.
                        with open(os.path.join(output_folder, os.path.basename(pv_FileURL)), "wb") as downloaded_file:
                            downloaded_file.write(r.content)

                        # Determine if the downloaded file should be renamed. If the filename is %f then the filename
                        # of the downloaded product should be the same as the url filename
                        if not output_filename == '%f':
                            self.__rename_files_in_a_folder(list_of_files=[os.path.basename(pv_FileURL)],
                                                            folder_path=output_folder,
                                                            new_filename=output_filename)

                # Raise an exception if an unexpected error occurs during the process
                except Exception as e:
                    warning_count += 1
                    message = "Unexpected error downloading file from URL {}.".format(pv_FileURL)
                    recommendation = "Check the log file for details."
                    logger.exception(message, e)
                    self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                            message, recommendation))

            # If the output folder is not a valid folder, log error message.
            else:
                warning_count += 1
                message = 'The output folder ({}) of the OutputFile is not a valid folder.'.format(output_folder)
                recommendation = 'Specify a valid relative pathname for the output file.'
                logger.error(message)
                self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                        message, recommendation))

        # If the provided URL is not a downloadable file, print an error message.
        else:
            warning_count += 1
            message = 'The FileURL ({}) does not refer to a downloadable file.'.format(pv_OutputFile)
            recommendation = 'Specifiy a valid URL for a file that can be downloaded.'
            logger.error(message)
            self.command_status.add_to_log(command_phase_type.RUN, CommandLogRecord(command_status_type.FAILURE,
                                                                                    message, recommendation))

        # Determine success of command processing. Raise Runtime Error if any errors occurred
        if warning_count > 0:
            message = "There were {} warnings proceeding this command.".format(warning_count)
            raise RuntimeError(message)

        # Set command status type as SUCCESS if there are no errors.
        else:
            self.command_status.refresh_phase_severity(command_phase_type.RUN, command_status_type.SUCCESS)
