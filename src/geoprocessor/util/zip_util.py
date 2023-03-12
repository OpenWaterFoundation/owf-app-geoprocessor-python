# zip_util - useful utility functions for zip file manipulations.
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

import os
import shutil
from io import StringIO
import tarfile
import zipfile


def is_tar_file(file_path: str) -> bool:
    """
    Determines if the input file is a tar file.

    Arg:
        file_path (str): the full pathname of the input file to check

    Return:
        Boolean. If TRUE, the input file is a valid tar file. If FALSE, the input file is not a valid tar file.
    """

    return tarfile.is_tarfile(file_path)


def is_zip_file(file_path: str) -> bool:
    """
    Determines if the input file is a zip file.

    Arg:
        file_path (str): the full pathname of the input file to check

    Return:
        Boolean. If TRUE, the input file is a valid zip file. If FALSE, the input file is not a valid zip file.
    """

    return zipfile.is_zipfile(file_path)


def is_zip_file_request(response_obj) -> bool:
    """
    Checks if a request response object is of zip file format.

    Args:
        response_obj: the request response object to check. For more information on request response objects,
            refer to `http://docs.python-requests.org/en/master/api/`

    Returns:
        Boolean. True if request response object is a zip file format. False if request response object is not a
        zip file format.
    """

    # The following comment is in place to make PyCharm skip review of the exception clause.
    # Without this comment, PyCharm raises error "Too broad exception clause".
    # noinspection PyBroadException
    try:
        zipfile.ZipFile(StringIO(response_obj.content))
        return True

    except Exception:
        return False


def untar_all_files(tar_file_path: str, output_folder: str) -> None:
    """
    Extracts all the archived files from a .tar file and saves them to the output folder.

    Args:
        tar_file_path: the full pathname to the tar file that is to be extracted
        output_folder: the full pathname to the folder where the archived files will be saved to

    Return: None.
    """

    # Create a tar file object from the input tar file.
    tar_file = tarfile.open(tar_file_path)

    # Extract all the archived files within the tar file to the output_folder.
    tar_file.extractall(output_folder)

    # Close the .tar file object.
    tar_file.close()


def unzip_all_files(zip_file_path: str, output_folder: str) -> None:
    """
    Extracts all the archived files from a .zip file and saves them to the output folder.

    Args:
        zip_file_path: the full pathname to the zip file that is to be unzipped
        output_folder: the full pathname to the folder where the archived files will be saved to

    Return: None.
    """

    # Create a .zip file object from the input zip file.
    zip_file = zipfile.ZipFile(zip_file_path, 'r')

    # Extract all the archived files within the zip file to the output_folder.
    zip_file.extractall(output_folder)

    # Close the .zip file object.
    zip_file.close()


def unzip_one_file(zip_file_path: str, input_filename: str, output_folder: str) -> None:

    # Create a .zip file object from the input zip file.
    zip_file = zipfile.ZipFile(zip_file_path, 'r')

    # Extract one of the archived files within the zip file to the output_folder.
    zip_file.extractall(input_filename, output_folder)

    # Close the .zip file object.
    zip_file.close()


def zip_files(list_of_files_to_archive: [str], output_filename: str, keep_originals: bool = True):
    """
    Compress a list of files into a .zip file.

    Args:
        list_of_files_to_archive (list of strings):
            each item of the list is the full pathname to a file that will be archived
        output_filename (string): the name of the output .zip file (can, but is not required to, end in .zip extension)
        keep_originals (Boolean): if True, the files to be archived will be saved. if False, the files to be archived
            will be deleted (once the files have been successfully archived within the .zip file). Default: TRUE

    Return: None
    """

    # Add the .zip extension if the output filename does not include it.
    if not output_filename.upper().endswith('.ZIP'):
        output_filename += '.zip'

    # Create a .zip file object.
    output_zip_file = zipfile.ZipFile(output_filename, 'w')

    # Iterate over the input files to archive.
    for to_archive_file in list_of_files_to_archive:

        # Get the file's filename (without leading path).
        filename = os.path.basename(to_archive_file)

        # Archive the file. The archived file will have the same filename as the input file.
        output_zip_file.write(to_archive_file, filename)

    # Close the .zip file object.
    output_zip_file.close()

    # If configured, delete the original input files.
    if not keep_originals:

        # Iterate over the input files.
        for to_archive_file in list_of_files_to_archive:

            # Delete the file if it is a valid file.
            if os.path.isfile(to_archive_file):
                os.remove(to_archive_file)

            # Delete the folder if it is a valid folder.
            else:
                shutil.rmtree(to_archive_file)


def zip_shapefile(output_file_abs: str, keep_archive_files: bool = False) -> None:
    """
    Compresses a shapefile.

    Args:
       output_file_abs: the full pathname to the output shapefile
       keep_archive_files (boolean): If set to TRUE, the orginal files will be saved. If set to FALSE, the original
            files will be deleted (leaving only the zip file and its archived components). Default: False.

    Return: None
    """

    # Get the output folder.
    output_folder = os.path.dirname(output_file_abs)
    output_filename = os.path.basename(output_file_abs)

    # The list of files to archive.
    files_to_archive = []

    # Iterate over the possible extensions of a shapefile.
    for extension in ['.shx', '.shp', '.qpj', '.prj', '.dbf', '.cpg', '.sbn', '.sbx', '.shp.xml']:

        # Get the full pathname of the shapefile component file.
        output_file_full_path = os.path.join(output_folder, output_filename + extension)

        # If the shapefile component file exists, add it' s absolute path to the files_to_archive list.
        # Note that not all shapefile component files are required -- some may not exist.
        if os.path.exists(output_file_full_path):
            files_to_archive.append(output_file_full_path)

    # Zip the files to archive (the zip file will have the same name as the original file).
    zip_files(files_to_archive, output_file_abs, keep_archive_files)
