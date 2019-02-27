import pytest
import geoprocessor.util.zip_util as zip_util
import os
import tarfile
import zipfile


# Create a temporary text file for testing tarred and zipped files
@pytest.fixture
def text_file(tmpdir):
    file = tmpdir.join("test_file.txt")
    file.write("Hello World!")
    return str(file)


# Create a second temporary text file for testing multiple files
@pytest.fixture
def text_file_2(tmpdir):
    file = tmpdir.join("test_file_2.txt")
    file.write("Goodbye!")
    return str(file)


# Create a temporary tar file using the temporary file above
# Returns the path to the tar file.
@pytest.fixture
def tar_file(tmpdir, text_file):
    path = str(tmpdir) + "/test_file.tar.gz"
    with tarfile.open(path, "w:gz") as tar:
        tar.add(text_file, arcname=os.path.basename(text_file))
    tar.close()
    return path


# Create a temporary zip file using the temporary file above.
# Returns the path to the zip file
@pytest.fixture
def zip_file(tmpdir, text_file):
    path = str(tmpdir) + "/test_file.zip"
    with zipfile.ZipFile(path, mode="w") as zip:
        zip.write(text_file, arcname=os.path.basename(text_file))
    zip.close()
    return path


@pytest.fixture
def zip_multiple_files(tmpdir, text_file, text_file_2):
    path = str(tmpdir) + "/test_multiple_files.zip"
    # Create a second file to add to zip file
    with zipfile.ZipFile(path, mode="w") as zip:
        zip.write(text_file, arcname=os.path.basename(text_file))
        zip.write(text_file_2, arcname=os.path.basename(text_file_2))
    zip.close()
    return path


# Create a temporary folder for unzipping and untarring files
@pytest.fixture
def output_folder(tmpdir):
    return str(tmpdir) + "/output_folder"


# Tests for function is_tar_file()
def test_is_tar_file_true(tar_file):
    """ Test a tar file to ensure is_tar_file() returns True """
    assert zip_util.is_tar_file(tar_file) is True


def test_is_tar_file_false(text_file):
    """ Test using a simple text file to ensure is_tar_file() returns False """
    assert zip_util.is_tar_file(text_file) is False


# Tests for function is_zip_file()
def test_is_zip_file_true(zip_file):
    """ Test using a zip file to ensure is_tar_file() returns True """
    assert zip_util.is_zip_file(zip_file) is True


def test_is_zip_file_false(text_file):
    """ Test using a simple text file to ensure is_zip_file() returns False"""
    assert zip_util.is_zip_file(text_file) is False


# TODO @jurentie 02/27/2019 - add tests for is_zip_file_request()


# Tests for function untar_all_files()
def test_untar_all_files(tar_file, output_folder):
    zip_util.untar_all_files(tar_file, output_folder)
    assert os.path.isfile(output_folder + "/test_file.txt") is True


# Tests for function unzip_all_files
def test_unzip_all_files(zip_file, output_folder):
    zip_util.unzip_all_files(zip_file, output_folder)
    assert os.path.isfile(output_folder + "/test_file.txt") is True


# TODO @jurentie 02/27/2019 need to fix this test function
# Tests for function unzip_one_file()
# def test_unzip_one_file(zip_multiple_files, output_folder):
#     zip_util.unzip_one_file(zip_multiple_files, 'test_file_2.txt', output_folder)
#     assert os.path.isfile(output_folder + "/test_file_2.txt") is True

# Tests for function zip_files()
def test_zip_files_multiple_file(tmpdir, text_file, text_file_2):
    list_of_files = [text_file, text_file_2]
    output_file = str(tmpdir) + '/test_file.zip'
    zip_util.zip_files(list_of_files, output_file)
    # Manually unzip the file...
    output_folder = str(tmpdir) + '/output_folder'
    zip_file = zipfile.ZipFile(output_file, 'r').extractall(output_folder)
    # Check to see that test_file.txt has been extracted from zipped file therefore that file has been zipped
    # appropriately
    assert os.path.isfile(output_folder + "/test_file.txt") is True and \
           os.path.isfile(output_folder + "/test_file_2.txt") is True


def test_zip_files_single_file(tmpdir, text_file):
    list_of_files = [text_file]
    output_file = str(tmpdir) + '/test_file.zip'
    zip_util.zip_files(list_of_files, output_file)
    # Manually unzip the file...
    output_folder = str(tmpdir) + '/output_folder'
    zip_file = zipfile.ZipFile(output_file, 'r').extractall(output_folder)
    # Check to see that test_file.txt has been extracted from zipped file therefore that file has been zipped
    # appropriately
    assert os.path.isfile(output_folder + "/test_file.txt") is True


def test_zip_files_do_not_keep_originals(tmpdir, text_file):
    list_of_files = [text_file]
    output_file = str(tmpdir) + '/test_file.zip'
    zip_util.zip_files(list_of_files, output_file, False)
    # Files should no longer be in directory
    assert os.path.isfile(text_file) is False

# TODO @jurentie 02/27/2019 - create various tests for zipping shapefiles