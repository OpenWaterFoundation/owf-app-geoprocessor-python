import logging

import geoprocessor.util.command as command_util

from geoprocessor.commands.layers.AddGeoLayerAttribute import AddGeoLayerAttribute
from geoprocessor.commands.layers.ClipGeoLayer import ClipGeoLayer
from geoprocessor.commands.layers.CopyGeoLayer import CopyGeoLayer
from geoprocessor.commands.layers.FreeGeoLayer import FreeGeoLayer
from geoprocessor.commands.layers.MergeGeoLayers import MergeGeoLayers
from geoprocessor.commands.layers.ReadGeoLayerFromGeoJSON import ReadGeoLayerFromGeoJSON
from geoprocessor.commands.layers.ReadGeoLayerFromShapefile import ReadGeoLayerFromShapefile
from geoprocessor.commands.layers.ReadGeoLayersFromFGDB import ReadGeoLayersFromFGDB
from geoprocessor.commands.layers.ReadGeoLayersFromFolder import ReadGeoLayersFromFolder
from geoprocessor.commands.layers.RemoveGeoLayerAttribute import RemoveGeoLayerAttribute
from geoprocessor.commands.layers.RenameGeoLayerAttribute import RenameGeoLayerAttribute
from geoprocessor.commands.layers.SetGeoLayerProperty import SetGeoLayerProperty
from geoprocessor.commands.layers.WriteGeoLayerPropertiesToFile import WriteGeoLayerPropertiesToFile
from geoprocessor.commands.layers.WriteGeoLayerToGeoJSON import WriteGeoLayerToGeoJSON
from geoprocessor.commands.layers.WriteGeoLayerToShapefile import WriteGeoLayerToShapefile

from geoprocessor.commands.logging.Message import Message
from geoprocessor.commands.logging.StartLog import StartLog

from geoprocessor.commands.running.EndFor import EndFor
from geoprocessor.commands.running.EndIf import EndIf
from geoprocessor.commands.running.For import For
from geoprocessor.commands.running.If import If
from geoprocessor.commands.running.SetProperty import SetProperty
from geoprocessor.commands.running.SetPropertyFromGeoLayer import SetPropertyFromGeoLayer
from geoprocessor.commands.running.WritePropertiesToFile import WritePropertiesToFile

from geoprocessor.commands.testing.CompareFiles import CompareFiles
from geoprocessor.commands.testing.CreateRegressionTestCommandFile import CreateRegressionTestCommandFile

from geoprocessor.commands.util.Blank import Blank
from geoprocessor.commands.util.Comment import Comment
from geoprocessor.commands.util.CopyFile import CopyFile
from geoprocessor.commands.util.RemoveFile import RemoveFile
from geoprocessor.commands.util.UnknownCommand import UnknownCommand
from geoprocessor.commands.util.WebGet import WebGet


class GeoProcessorCommandFactory(object):
    """
    Factory to create command instances by examining command string.
    Only instantiates the command instance but does not parse the command string.
    The command string is parsed within the command class instance.
    """

    # The dictionary of all available commands, in alphabetical order.
    # key: the name of the command (converted to all UPPERCASE)
    # value: the constructor (__init__) function to create an instance of the command
    # This dictionary serves two purposes:
    # 1) It provides a registry of all commands known to the geoprocessor (via this factory class)
    # 2) It provides the list of constructor functions to call, to simplify logic
    registered_commands = {
        "ADDGEOLAYERATTRIBUTE": AddGeoLayerAttribute(),
        "BLANKCOMMAND": Blank(),  # Actually has no name, is whitespace only
        "CLIPGEOLAYER": ClipGeoLayer(),
        "COMMENT": Comment(),  # Actually is line starting with #
        "COMPAREFILES": CompareFiles(),
        "COPYFILE": CopyFile(),
        "COPYGEOLAYER": CopyGeoLayer(),
        "CREATEREGRESSIONTESTCOMMANDFILE": CreateRegressionTestCommandFile(),
        "ENDFOR": EndFor(),
        "ENDIF": EndIf(),
        "FOR": For(),
        "FREEGEOLAYER": FreeGeoLayer(),
        "IF": If(),
        "MERGEGEOLAYERS": MergeGeoLayers(),
        "MESSAGE": Message(),
        "READGEOLAYERFROMGEOJSON": ReadGeoLayerFromGeoJSON(),
        "READGEOLAYERFROMSHAPEFILE": ReadGeoLayerFromShapefile(),
        "READGEOLAYERSFROMFGDB": ReadGeoLayersFromFGDB(),
        "READGEOLAYERSFROMFOLDER": ReadGeoLayersFromFolder(),
        "REMOVEFILE": RemoveFile(),
        "REMOVEGEOLAYERATTRIBUTE": RemoveGeoLayerAttribute(),
        "RENAMEGEOLAYERATTRIBUTE": RenameGeoLayerAttribute(),
        "SETGEOLAYERPROPERTY": SetGeoLayerProperty(),
        "SETPROPERTY": SetProperty(),
        "SETPROPERTYFROMGEOLAYER": SetPropertyFromGeoLayer(),
        "STARTLOG": StartLog(),
        "WEBGET": WebGet(),
        "WRITEGEOLAYERPROPERTIESTOFILE": WriteGeoLayerPropertiesToFile(),
        "WRITEGEOLAYERTOGEOJSON": WriteGeoLayerToGeoJSON(),
        "WRITEGEOLAYERTOSHAPEFILE": WriteGeoLayerToShapefile(),
        "WRITEPROPERTIESTOFILE": WritePropertiesToFile()
    }

    def __init__(self):
        pass

    def __is_command_valid(self, command_name):
        """
        Checks if the command is a valid registered command by examining the command name.
        A valid command can be further processed to create a command instance.

        Args:
            command_name: the name of the command

        Returns:
            True if the command is registered as recognized, False if not.
        """

        registered_command_names = list(self.registered_commands.keys())
        if command_name.upper() in registered_command_names:
            return True
        else:
            return False

    def new_command(self, command_string, create_unknown_command_if_not_recognized=True):
        """
        Creates the object of a command class called from a command line of the command file.

        Args:
            command_string (str): the command string entered by the user in the command file
            create_unknown_command_if_not_recognized (bool) If TRUE, create an UnknownCommand when the input
            command is not recognized, if FALSE, throw an error.

        Returns:
            A command instance of class type that matches the command name.
            The command is not parsed.

        Raises:
            ValueError if the command is not recognized and create_unknown_command_if_not_recognized=False.
        """

        logger = logging.getLogger(__name__)

        # Get command name from the first part of the command.
        command_string_trimmed = command_string.strip()
        paren_pos = command_string_trimmed.find('(')

        if len(command_string_trimmed) == 0:
            # Blank line so insert a BlankCommand command.
            return Blank()

        # Comment line.
        elif command_string_trimmed[:1] == '#':
            return Comment()

        # The symbol '(' was found.
        # Assume command of syntax CommandName(Param1="...",Param2="...").
        elif paren_pos != -1:

            # Get command name from command string, command name is before the first open parenthesis.
            command_name = command_util.parse_command_name_from_command_string(command_string_trimmed)

            # Initialize the command class object if it is a valid command.
            command_name_upper = command_name.upper()
            init_from_dictionary_constructor = False
            if init_from_dictionary_constructor:
                # TODO smalers 2017-12-28 Figure out if the dictionary constructor can be called.
                # The following is a clever way to initialize instances using a constructor function
                # from the command dictionary.
                # However, it does not seem to work.  For example, if multiple Message commands
                # are initialized, the AbstractCommand.command_parameters dictionary for all Message
                # command instances will have the values corresponding to the last Message command.
                if self.__is_command_valid(command_name):
                    command = self.registered_commands[command_name_upper]
                    return command
            else:
                # Constructing the following way always seems to work properly
                # - Alphabetize the commands.
                if command_name_upper == "ADDGEOLAYERATTRIBUTE":
                    return AddGeoLayerAttribute()
                elif command_name_upper == "CLIPGEOLAYER":
                    return ClipGeoLayer()
                elif command_name_upper == "COMPAREFILES":
                    return CompareFiles()
                elif command_name_upper == "COPYFILE":
                    return CopyFile()
                elif command_name_upper == "COPYGEOLAYER":
                    return CopyGeoLayer()
                elif command_name_upper == "CREATEREGRESSIONTESTCOMMANDFILE":
                    return CreateRegressionTestCommandFile()
                elif command_name_upper == "ENDFOR":
                    return EndFor()
                elif command_name_upper == "ENDIF":
                    return EndIf()
                elif command_name_upper == "FOR":
                    return For()
                elif command_name_upper == "FREEGEOLAYER":
                    return FreeGeoLayer()
                elif command_name_upper == "IF":
                    return If()
                elif command_name_upper == "MERGEGEOLAYERS":
                    return MergeGeoLayers()
                elif command_name_upper == "MESSAGE":
                    return Message()
                elif command_name_upper == "READGEOLAYERFROMGEOJSON":
                    return ReadGeoLayerFromGeoJSON()
                elif command_name_upper == "READGEOLAYERFROMSHAPEFILE":
                    return ReadGeoLayerFromShapefile()
                elif command_name_upper == "READGEOLAYERSFROMFGDB":
                    return ReadGeoLayersFromFGDB()
                elif command_name_upper == "READGEOLAYERSFROMFOLDER":
                    return ReadGeoLayersFromFolder()
                elif command_name_upper == "REMOVEFILE":
                    return RemoveFile()
                elif command_name_upper == "REMOVEGEOLAYERATTRIBUTE":
                    return RemoveGeoLayerAttribute()
                elif command_name_upper == "RENAMEGEOLAYERATTRIBUTE":
                    return RenameGeoLayerAttribute()
                elif command_name_upper == "SETGEOLAYERPROPERTY":
                    return SetGeoLayerProperty()
                elif command_name_upper == "SETPROPERTY":
                    return SetProperty()
                elif command_name_upper == "SETPROPERTYFROMGEOLAYER":
                    return SetPropertyFromGeoLayer()
                elif command_name_upper == "STARTLOG":
                    return StartLog()
                elif command_name_upper == "WEBGET":
                    return WebGet()
                elif command_name_upper == "WRITEGEOLAYERPROPERTIESTOFILE":
                    return WriteGeoLayerPropertiesToFile()
                elif command_name_upper == "WRITEGEOLAYERTOGEOJSON":
                    return WriteGeoLayerToGeoJSON()
                elif command_name_upper == "WRITEGEOLAYERTOSHAPEFILE":
                    return WriteGeoLayerToShapefile()
                elif command_name_upper == "WRITEPROPERTIESTOFILE":
                    return WritePropertiesToFile()

            # If here the command name was not matched.
            # Don't know the command so create an UnknownCommand or throw an exception.
            if create_unknown_command_if_not_recognized:
                logger.warn("Command line is unknown command. Adding UnknownCommand: " + command_string_trimmed)
                return UnknownCommand()
            else:
                logger.warn("Command line is unknown syntax.")
                raise ValueError('Unrecognized command "' + command_string + '"')

        # The syntax is not recognized so create an UnknownCommand or throw an exception.
        else:
            if create_unknown_command_if_not_recognized:
                logger.warn("Command line is unknown syntax. Adding UnknownCommand: " + command_string_trimmed)
                return UnknownCommand()
            else:
                logger.warn("Command line is unknown syntax.")
                raise ValueError('Unrecognized command "' + command_string + '"')
