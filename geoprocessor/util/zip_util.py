# Useful utility functions for zip file manipulations.

import os
import shutil
from zipfile import ZipFile


def unzip_all_files(zip_file_path, output_folder):
    """
    Extracts all of the archived files from a .zip file and saves them to the output folder.

    Args:
        zip_file_path: the full pathname to the zip file that is to be unzipped
        output_folder: the full pathname to the folder where the archived files will be saved to

    Return: None.
    """

    # Create a .zip file object from the input zip file.
    zip_file = ZipFile(zip_file_path, 'r')

    # Extract all of the archived files within the zip file to the output_folder.
    zip_file.extractall(output_folder)

    # Close the .zip file object.
    zip_file.close()


def unzip_one_file(zip_file_path, input_filename, output_folder):

    # Create a .zip file object from the input zip file.
    zip_file = ZipFile(zip_file_path, 'r')

    # Extract one of the archived files within the zip file to the output_folder.
    zip_file.extractall(input_filename, output_folder)

    # Close the .zip file object.
    zip_file.close()


def zip_files(list_of_files_to_archive, output_filename, keep_originals=True):
    """
    Compress a list of files into a .zip file.

    Args:
        list_of_files_to_archive (list of strings): each item of the list is the full pathname to a file that will
            be archived
        output_filename (string): the name of the output .zip file (can, but is not required to, end in .zip extension)
        keep_originals (Boolean): if True, the files to be archived will be saved. if False, the files to be archived
            will be deleted (once the files have been successfully archived within the .zip file). Default: TRUE

    Return: None
    """

    # Add the .zip extension if the output filename does not include it.
    if not output_filename.upper().endswith('.ZIP'):
        output_filename += '.zip'

    # Create a .zip file object.
    output_zip_file = ZipFile(output_filename, 'w')

    # Iterate over the input files to archive.
    for to_archive_file in list_of_files_to_archive:

        # Get the file's filename (without leading path)
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
