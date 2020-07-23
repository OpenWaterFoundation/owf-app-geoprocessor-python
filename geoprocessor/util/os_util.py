# os_util - useful utility functions for the operating system
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

"""
Functions related to the operating system.
"""

import logging
import os
from pathlib import Path
import platform
import subprocess


def get_os_distro() -> str:
    """
    Determine the operating system distribution, useful for showing system information
    but not advised for checks (use the is_*_os() functions to control program logic).

    Returns:
        (str) operating system distribution as "Cygwin", "MinGW", "Debian" (Linux), "Windows 10" for Windows 10,
        or None if unknown.
    """
    os_type_distro = None
    if is_cygwin_os():
        os_type_distro = "Cygwin"
    elif is_mingw_os():
        os_type_distro = "MinGW"
    elif is_windows_os():
        # Use the platform version
        os_type_distro = platform.uname()[2]
    return os_type_distro


def get_os_type() -> str:
    """
    Determine the major operating system type, useful for showing system information
    but not advised for checks (use the is_*_os() functions to control program logic).

    Returns:
        (str) operating system type as "Linux" or "Windows", or None if unknown.
    """
    os_type = None
    if is_linux_os():
        os_type = "Linux"
    elif is_windows_os():
        os_type = "Windows"
    return os_type


def is_cygwin_os() -> bool:
    """
    Indicate whether the operating system is Cygwin.
    Cygwin is a Linux OS but someones Cygwin-specific logic must be implemented.

    Returns:  True if Cygwin operating system, False if not.
    """
    if platform.uname()[0].upper().find('CYGWIN') >= 0:
        return True
    else:
        return False


def is_linux_os() -> bool:
    """
    Indicate whether the operating system is Linux.

    Returns:  True if Linux operating system, False if not.
    """
    if os.name.upper() == 'POSIX':
        return True
    else:
        return False


def is_mingw_os() -> bool:
    """
    Indicate whether the operating system is MinGW, such as used with Git Bash.
    MinGW is a Linux OS but someones MinGW-specific logic must be implemented.

    Returns:  True if MinGW operating system, False if not.
    """
    if platform.uname()[0].upper().find('MINGW') >= 0:
        return True
    else:
        return False


def is_windows_os() -> bool:
    """
    Indicate whether the operating system is Windows.

    Returns:  True if Windows operating system, False if not.
    """
    if os.name.upper() == 'NT':
        return True
    else:
        return False


def run_default_app(file_path: str, as_text: bool = False) -> None:
    """
    Run the default application for the operating system for a file with an extension.
    For example, open a text editor for files with '.txt' extension.

    Args:
        file_path (str): Path to file to open.
        as_text (bool): Indicate whether the file should be treated as text, useful if the file extension is
            not associated with an application.

    Returns:
        None

    Raises:
        RuntimeError if cannot run an application for the file extension
    """
    logger = logging.getLogger(__name__)
    if is_windows_os():
        # The following does not seem reliable:
        #   https://stackoverflow.com/questions/48051864/
        #       how-to-get-the-default-application-mapped-to-a-file-extention-in-windows-using-p/48121945
        #
        # Instead, run Windows commands to get the application.
        # - see:  https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/assoc
        # - see:  https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/ftype
        path = Path(file_path)
        # Get the extension, which includes the leading period
        if as_text:
            # Treat as text
            ext = ".txt"
        else:
            ext = path.suffix
        # Run the 'assoc' command, which determines the file type for an extension, for example:
        #    assoc .txt
        #    .txt=textfile
        #
        #    assoc .zzz
        #    File association not found for extension .zzz
        #
        # The file type 'textfile' is a general type that may be associated with more than one file extension.
        # Next, look up the file type to determine the associated application.

        # Use parameters for no-wait process
        command_line = "assoc {}".format(ext)
        logger.info("Running: {}".format(command_line))
        use_command_shell = True
        completed_process = subprocess.run(command_line, shell=use_command_shell, capture_output=True,
                                           encoding='utf-8',
                                           timeout=10, close_fds=True)
        logger.info("Done running: {}".format(command_line))
        # Output is a byte string so convert to string
        assoc_out = "{}".format(completed_process.stdout)
        logger.info("assoc output is: {}".format(assoc_out))
        if assoc_out.find("not found") >= 0:
            # Initial extension was not found.  Handle a few common cases.
            if ext == ".log":
                # Treat as .txt and repeat the above logic
                ext2 = ".txt"
                command_line = "assoc {}".format(ext2)
                logger.info("Running: {}".format(command_line))
                use_command_shell = True
                completed_process = subprocess.run(command_line, shell=use_command_shell, capture_output=True,
                                                   encoding='utf-8',
                                                   timeout=10, close_fds=True)
                logger.info("Done running: {}".format(command_line))
                # Output is a byte string so convert to string
                assoc_out = str(completed_process.stdout)
                logger.info("assoc output is: {}".format(assoc_out))
                if assoc_out.find("not found") >= 0:
                    raise RuntimeError("No application is associated with file extension: {} "
                                       "(tried because {} also was not associated with an application)", ext2, ext)
                else:
                    # Have an association so OK
                    pass
            else:
                # Don't know what to do
                raise RuntimeError("No application is associated with file extension: {}", ext)
        else:
            # Have an association so OK to continue to the next step.
            pass

        pos = assoc_out.find("=")
        if pos >= 0:
            filetype = assoc_out[pos+1:].strip()
            logger.info("File type for extension {} is:  {}".format(ext, filetype))
        else:
            # No associated file
            raise RuntimeError("No file type is associated with file extension: {}", ext)

        # Then get the application for that type
        #    ftype txtfile
        #    txtfile=%SystemRoot%\system32\NOTEPAD.EXE %1
        #
        #    ftype zzzfile
        #    File type 'zzzfile' not found or no open command associated with it.
        #
        # The app to the run is to the right of the equals sign.  Replace %1 with the filename.
        # The parent environment is required to expand %SystemRoot% and other environment variables,
        # so use the default.
        command_line = "ftype {}".format(filetype)
        logger.info("Running: {}".format(command_line))
        use_command_shell = True
        completed_process = subprocess.run(command_line, shell=use_command_shell, capture_output=True,
                                           encoding='utf-8',
                                           timeout=10, close_fds=True)
        # Output is a byte string so convert to string
        ftype_out = "{}".format(completed_process.stdout)
        logger.info("ftype output is: {}".format(ftype_out))
        if ftype_out.find("not found") >= 0:
            raise RuntimeError("No application is associated with file type: {}", filetype)
        else:
            # Have an association so OK
            pass

        pos = ftype_out.find("=")
        if pos >= 0:
            app_command_line = ftype_out[pos+1:].strip()
            logger.info("Application command line for file type {} is:  {}".format(filetype, app_command_line))
        else:
            # No associated file
            raise RuntimeError("No application is associated with file type: {}", filetype)

        if app_command_line.find("%1") >= 0:
            # The command line includes %1 so replace with the filename
            app_command_line = app_command_line.replace("%1", file_path)
        else:
            # The command line does not include %1 so add the filename at the end
            app_command_line = "{} {}".format(app_command_line, file_path)

        # Run the application
        # - run detached so that it does not block the GeoProcessor
        # - no timeout since a separate process
        env_dict = None
        use_command_shell = True
        logger.info("Running command: {}".format(app_command_line))
        subprocess.run(app_command_line, shell=use_command_shell, env=env_dict,
                       close_fds=True, creationflags=subprocess.DETACHED_PROCESS)
    elif is_linux_os():
        # TODO smalers 2020-07-22 need to implement
        pass
    else:
        # TODO smalers 2020-07-22 need to implement
        pass
