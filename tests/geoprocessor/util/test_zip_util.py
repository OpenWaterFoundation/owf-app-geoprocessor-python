import pytest
import geoprocessor.util.zip_util as zip_util
import os
import tarfile

def test_is_tar_file_true(tmpdir):
    file = tmpdir.join("test_file.txt")
    file.write("Hello World!")
    with tarfile.open("test_file.tar.gz", "w:gz") as tar:
        tar.add(file)
    tar.close()
    tarredfile = tmpdir + "/test_file.tar.gz"
    # assert zip_util.is_tar_file(tarredfile) == True