# ListFiles

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.io_util as io_util
import geoprocessor.util.string_util as string_util
import geoprocessor.util.validator_util as validators

import logging
import os
import urllib2


class ListFiles(AbstractCommand):
    """
    Lists file and/or folders from a input folder. The input folder can be a folder on a local machine or a url 
    directory.
    
    Command Parameters
    * Folder (str, optional): the path to a folder on the local machine (relative or absolute)
    * URL (str, optional): a valid URL/web address
    * IncludePatterns (str, optional): a comma-separated list of glob-style patterns to determine which files/folders
        to list from the input folder/url Default: * (All files/folders are listed.).
    * ExcludePatterns (str, optional): a comma-separated list of glob-style patterns to determine which files/folders
        to not list from the input folder/url Default: '' ( No files/folders are excluded from being listed).
    * ListFiles (str converted to Boolean within command): If True, files within the input folder/URL will be
        listed. If False, files within the folder/URL will not be listed.
    * ListFolders (str converted to Boolean within command): If True, folders within the input folder/URL will be
        listed. If False, folders within the input folder/URL or URL will not be listed.
    * ListProperty (str, required ): The name of the GeoProcessor property to store the output list of files/folders.
    * IfPropertyExists (str, optional): This parameter determines the action that occurs if the ListProperty
        already exists within the GeoProcessor. Available options are: `Replace`, `ReplaceAndWarn`, `Warn` and `Fail`
        (Refer to user documentation for detailed description.) Default value is `Replace`.
    """

    # Define the command parameters.
    __command_parameter_metadata = [
        CommandParameterMetadata("Folder", type("")),
        CommandParameterMetadata("URL", type("")),
        CommandParameterMetadata("IncludePatterns", type("")),
        CommandParameterMetadata("ExcludePatterns", type("")),
        CommandParameterMetadata("ListFiles", type("")),
        CommandParameterMetadata("ListFolders", type("")),
        CommandParameterMetadata("ListProperty", type("")),
        CommandParameterMetadata("IfPropertyExists", type(""))]

    def __init__(self):
        """
        Initialize the command
        """

        # AbstractCommand data
        super(ListFiles, self).__init__()
        self.command_name = "ListFiles"
        self.command_parameter_metadata = self.__command_parameter_metadata

        # Class data
        self.warning_count = 0
        self.logger = logging.getLogger(__name__)

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.

        Args:
            command_parameters: the dictionary of command parameters to check (key:string_value)

        Returns: None.

        Raises:
            ValueError if any parameters are invalid or do not have a valid value.
            The command status messages for initialization are populated with validation messages.
        """
        warning = ""

    def should_list_files(self):
        """
        Checks the following:
        * either the list files or list dirs or both are set to TRUE.
        * either the Folder or URL parameter is TRUE (not both).
        * the URL is valid.
        * the folder is valid.
        * the list property is unique
        """
        pass

    @staticmethod
    def scrape_html(url, read_files, read_dirs, include_list=None, exclude_list=None):
        """
        Reads a URL and outputs a list of links within the URL's source. The list of links can be filtered be the
        following options:
            * include file links, directory/folder links or both types of links
            * include/exclude links with names match a/multiple glob-style pattern(s)

        Args:
            url (str): a web address (URL) to scrape. Can, but is not required to, include an ending forward slash.
            read_files (bool): If True, the links associated with FILES will be included in the returned list. If False,
                the links associated with FILES will not be included in the returned list.
            read_dirs (bool): If True, the links associated with DIRECTORIES will be included in the returned list. If
                False, the links associated with DIRECTORIES will not be included in the returned list.
            include_list (list of str): A list of glob-style patterns. Links with names that match any of the glob-style
                patterns listed in this list will be included in the returned list. Default: None (All links are
                included.) The include_list is assigned ['*'] inside of the string_util.filter_list_of_strings function
                if set to None.
            exclude_list (list of str): A list of glob-style patterns. Links with names that match any of the glob-style
                patterns listed in this list will be excluded in the returned list. Default: None (No links excluded.)
                The exclude_list is assigned [''] inside of the string_util.filter_list_of_strings function if set to
                None.

        Return:
            A list of links within the URL source page that match the configured settings.
        """

        # If the URL does not end in a forward slash, add an ending forward slash.
        if not url.endswith('/'):
            url = url + '/'

        # Read the source content of the URL.
        urlpath = urllib2.urlopen(('{}'.format(url)))
        string = urlpath.read().decode('utf-8')

        # Get the URL of the parent directory.
        parent_dir_url = url.rsplit('/', 2)[0]

        # in_link determines if a URL character in within an HTML link. Set to FALSE until proven TRUE (when a link is
        # found within the source content of the URL).
        in_link = False

        # A list to hold the URL's source links that are directories/folders.
        dir_list = []

        # A list to hold the URL's source links that are files.
        file_list = []

        # Iterate through each character of the URL's source content.
        for i in range(len(string)):

            # If the string contains <A HREF= and the program is not currently reading a source content link, continue.
            if (string[i:i + 8]).upper() == "<A HREF=" and not in_link:
                # Set the in_link Boolean variable to True. Marks the start of reading a source link.
                in_link = True

                # Get the index of the character that starts the link's name.
                link_start_char_index = i + 9

            # If the string contains "> and the program is currently reading a source content link, continue.
            if (string[i:i + 2]).upper() == '">' and in_link:

                # Set the in_link Boolean variable to False. Marks the end of reading a source link.
                in_link = False

                # Get the index of the character that ends the link's name.
                link_end_char_index = i

                # Get the link's name.
                link_name = string[link_start_char_index: link_end_char_index]

                # If the link name ends in a forward slash, the link is a folder/directory. Add the link name (without
                # the leading path or the ending forward slash) to the dir_list.
                if link_name.endswith('/'):
                    dir_list.append(link_name.split('/')[-2])

                # If the link name does not end in a forward slash, the link is a file. Add the link name (without
                # the leading path) to the file_list.
                else:
                    file_list.append(link_name.split('/')[-1])

        # If the files and directories are of interest, create a list with both the files and the directories.
        if read_files and read_dirs:
            link_list = dir_list + file_list

        # If the files are of interest, create a list with just the files.
        elif read_files:
            link_list = file_list

        # If the directories/folders are of interest, create a list with just the directories/folders.
        elif read_dirs:
            link_list = dir_list

        # Iterate over the each link name.
        for link in link_list:

            # Remove the link if it corresponds to a parent directory.
            if link in parent_dir_url:
                link_list.remove(link)

        # Filter the list of links with regards to the include_list and exclude_list parameters.
        link_list_filtered = string_util.filter_list_of_strings(link_list, include_list, exclude_list)

        # Return the list of filtered and available links within the input URL.
        return link_list_filtered

    def run_command(self):

        # Obtain the parameter values.
        pv_Folder = self.get_parameter_value("Folder")
        pv_URL = self.get_parameter_value("URL")
        pv_ListFiles = self.get_parameter_value("ListFiles", default_value=True)
        pv_ListFolders = self.get_parameter_value("ListFolders", default_value=True)
        pv_ListProperty = self.get_parameter_value("ListProperty")
        pv_IncludePatterns = self.get_parameter_value("IncludePatterns", default_value="*")
        pv_ExcludePatterns = self.get_parameter_value("ExcludePatterns", default_value="''")

        # Convert the IncludeAttributes and ExcludeAttributes to lists.
        to_include = string_util.delimited_string_to_list(pv_IncludePatterns)
        to_exclude = string_util.delimited_string_to_list(pv_ExcludePatterns)

        # If the input is a local folder.
        if pv_Folder:

            # Convert the Folder parameter value relative path to an absolute path and expand for ${Property} syntax.
            folder_abs = io_util.verify_path_for_os(io_util.to_absolute_path(
                self.command_processor.get_property('WorkingDir'),
                self.command_processor.expand_parameter_value(pv_Folder, self)))

        # If the input is a url.
        if pv_URL:

            # Convert the URL parameter to expand for ${Property} syntax.
            url_abs = self.command_processor.expand_parameter_value(pv_URL, self)


        # Do check. And then continue.
        ######################################

        # If the input is a local folder.
        if pv_Folder:

            # Get a list of the files in the folder.
            files = [file for file in os.listdir(folder_abs) if os.path.isfile(os.path.join(folder_abs, file))]

            # Get a list of directories in the folder.
            dirs = [dir for dir in os.listdir(folder_abs) if os.path.isdir(os.path.join(folder_abs, dir))]

            # If configured to list files and folders, continue.
            if pv_ListFiles and pv_ListFolders:

                # Filter the list of files and folders with regards to the IIncludePatterns and ExcludePatterns parameters.
                output_filtered = string_util.filter_list_of_strings(files + dirs, to_include, to_exclude)

            # If configured to list files, continue.
            elif pv_ListFiles:

                # Filter the list of files with regards to the IIncludePatterns and ExcludePatterns parameters.
                output_filtered = string_util.filter_list_of_strings(files, to_include, to_exclude)

            # If configured to list folders, continue.
            else:

                # Filter the list of folders with regards to the IIncludePatterns and ExcludePatterns parameters.
                output_filtered = string_util.filter_list_of_strings(dirs, to_include, to_exclude)

            # Add the filtered list to the desired ListProperty.
            self.command_processor.set_property(pv_ListProperty, output_filtered)

        # If the input is a url.
        if pv_URL:

            # If configured to list files and folders, continue.
            if pv_ListFiles and pv_ListFolders:
                output_filtered = self.scrape_html(url_abs, True, True, pv_IncludePatterns, pv_ExcludePatterns)

            # If configured to list files, continue.
            elif pv_ListFiles:
                output_filtered = self.scrape_html(url_abs, True, False, pv_IncludePatterns, pv_ExcludePatterns)

            # If configured to list folders, continue.
            else:
                output_filtered = self.scrape_html(url_abs, False, True, pv_IncludePatterns, pv_ExcludePatterns)

            # Add the filtered list to the desired ListProperty.
            self.command_processor.set_property(pv_ListProperty, output_filtered)

# def scrape_html(url, read_files, read_dirs, include_list=None, exclude_list=None):
#     """
#     Reads a URL and outputs a list of links within the URL's source. The list of links can be filtered be the
#     following options:
#         * include file links, directory/folder links or both types of links
#         * include/exclude links with names match a/multiple glob-style pattern(s)
#
#     Args:
#         url (str): a web address (URL) to scrape. Can, but is not required to, include an ending forward slash.
#         read_files (bool): If True, the links associated with FILES will be included in the returned list. If False,
#             the links associated with FILES will not be included in the returned list.
#         read_dirs (bool): If True, the links associated with DIRECTORIES will be included in the returned list. If
#             False, the links associated with DIRECTORIES will not be included in the returned list.
#         include_list (list of str): A list of glob-style patterns. Links with names that match any of the glob-style
#             patterns listed in this list will be included in the returned list. Default: None (All links are
#             included.) The include_list is assigned ['*'] inside of the string_util.filter_list_of_strings function
#             if set to None.
#         exclude_list (list of str): A list of glob-style patterns. Links with names that match any of the glob-style
#             patterns listed in this list will be excluded in the returned list. Default: None (No links excluded.)
#             The exclude_list is assigned [''] inside of the string_util.filter_list_of_strings function if set to
#             None.
#
#     Return:
#         A list of links within the URL source page that match the configured settings.
#     """
#
#     # If the URL does not end in a forward slash, add an ending forward slash.
#     if not url.endswith('/'):
#         url = url + '/'
#
#     # Read the source content of the URL.
#     urlpath = urllib2.urlopen(('{}'.format(url)))
#     string = urlpath.read().decode('utf-8')
#
#     # Get the URL of the parent directory.
#     parent_dir_url = url.rsplit('/', 2)[0]
#
#     # in_link determines if a URL character in within an HTML link. Set to FALSE until proven TRUE (when a link is
#     # found within the source content of the URL).
#     in_link = False
#
#     # A list to hold the URL's source links that are directories/folders.
#     dir_list = []
#
#     # A list to hold the URL's source links that are files.
#     file_list = []
#
#     # Iterate through each character of the URL's source content.
#     for i in range(len(string)):
#
#         # If the string contains <A HREF= and the program is not currently reading a source content link, continue.
#         if (string[i:i + 8]).upper() == "<A HREF=" and not in_link:
#             # Set the in_link Boolean variable to True. Marks the start of reading a source link.
#             in_link = True
#
#             # Get the index of the character that starts the link's name.
#             link_start_char_index = i + 9
#
#         # If the string contains "> and the program is currently reading a source content link, continue.
#         if (string[i:i + 2]).upper() == '">' and in_link:
#
#             # Set the in_link Boolean variable to False. Marks the end of reading a source link.
#             in_link = False
#
#             # Get the index of the character that ends the link's name.
#             link_end_char_index = i
#
#             # Get the link's name.
#             link_name = string[link_start_char_index: link_end_char_index]
#
#             # If the link name ends in a forward slash, the link is a folder/directory. Add the link name (without
#             # the leading path or the ending forward slash) to the dir_list.
#             if link_name.endswith('/'):
#                 dir_list.append(link_name.split('/')[-2])
#
#             # If the link name does not end in a forward slash, the link is a file. Add the link name (without
#             # the leading path) to the file_list.
#             else:
#                 file_list.append(link_name.split('/')[-1])
#
#     # If the files and directories are of interest, create a list with both the files and the directories.
#     if read_files and read_dirs:
#         link_list = dir_list + file_list
#
#     # If the files are of interest, create a list with just the files.
#     elif read_files:
#         link_list = file_list
#
#     # If the directories/folders are of interest, create a list with just the directories/folders.
#     elif read_dirs:
#         link_list = dir_list
#
#     # Iterate over the each link name.
#     for link in link_list:
#
#         # Remove the link if it corresponds to a parent directory.
#         if link in parent_dir_url:
#             link_list.remove(link)
#
#     # Filter the list of links with regards to the include_list and exclude_list parameters.
#     link_list_filtered = string_util.filter_list_of_strings(link_list, include_list, exclude_list)
#
#     # Return the list of filtered and available links within the input URL.
#     return [url + link_name for link_name in link_list_filtered]


# # geomac_url = "https://gec.cr.usgs.gov/outgoing/GeoMAC"
# #
# # # Iterate over the available date directories.
# # date_folders = scrape_html(geomac_url, False, True, ['2010*'])
# # for date in date_folders:
# #
# #     # Iterate over the available state directories.
# #     path = "{}/{}".format(geomac_url, date)
# #     state_folders = scrape_html(path, False, True, ['Colorado'])
# #     for state in state_folders:
# #
# #         # Iterate over the available fire directories.
# #         path = "{}/{}/{}".format(geomac_url, date, state)
# #         fire_names = scrape_html(path, False, True, ['Echo*Lake'])
# #         for fire in fire_names:
# #
# #             # Print the available fire files.
# #             path = "{}/{}/{}/{}".format(geomac_url, date, state, fire)
# #             fire_data = scrape_html(path, True, False)
# #             if fire_data:
# #                 print "\n STATE: {}, YEAR: {}, FIRE: {}, DATA: {}".format(state, date, fire, fire_data)
#
# geomac_url = "https://gec.cr.usgs.gov/outgoing/GeoMAC"
#
# # Iterate over the available date directories.
# date_folders = scrape_html(geomac_url, False, True, ['2010*'])
# for date in date_folders:
#
#     # Iterate over the available state directories.
#     state_folders = scrape_html(date, False, True, ['Colorado'])
#     for state in state_folders:
#
#         # Iterate over the available fire directories.
#         fire_names = scrape_html(state, False, True, ['*'])
#         print fire_names
#         # for fire in fire_names:
#         #
#         #     # Print the available fire files.=
#         #     fire_data = scrape_html(fire, True, False, ['*.zip'])
#         #     if fire_data:
#         #         print "\n DATA: {}".format(fire_data)
