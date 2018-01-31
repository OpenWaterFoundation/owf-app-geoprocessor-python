# Useful utility functions for file manipulations.

import os, shutil
from zipfile import ZipFile

def zip_files(list_of_files_to_archive, output_filename, keep_originals=True):

    if not output_filename.upper().endswith('.ZIP'):

        output_filename = output_filename + '.zip'

    output_zip_file = ZipFile(output_filename, 'w')

    for to_archive_file in list_of_files_to_archive:

        filename = os.path.basename(to_archive_file)
        output_zip_file.write(to_archive_file, filename)

    output_zip_file.close()

    if not keep_originals:

        for to_archive_file in list_of_files_to_archive:

            if os.path.isfile(to_archive_file):
                os.remove(to_archive_file)
            else:
                shutil.rmtree(to_archive_file)
