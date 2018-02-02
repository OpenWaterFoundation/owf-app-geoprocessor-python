# Useful utility functions for file manipulations.

import os
import shutil
from zipfile import ZipFile


def get_col_names_from_delimited_file(delimited_file_abs, delimiter):
    """

    Reads a delimited file and returns the column names in list format.

    Args:
        delimited_file_abs (string): the full pathname to a delimited file to read.
        delimiter (string): the delimiter used in the delimited file.

    Returns:
        A list of strings. Each string represents a column name. If an error occurs within the function, None is
         returned.
    """

    try:

        # Open the delimited file and iterate through the lines of the file.
        with open(delimited_file_abs) as in_file:
            for lineNum, line in enumerate(in_file):

                # Return the column names of the header line in the delimited file. The column names are items of a
                # list and the column names are striped of whitespaces on either side.
                if lineNum == 0:
                    return map(str.strip, line.split(delimiter))

    # If an error occurs within the process, return None.
    except:
        return None


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
