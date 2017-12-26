import geoprocessor.util.command as command_util

import geoprocessor.commands.layers.CreateGeolayers as CreateGeolayers
import geoprocessor.commands.layers.CreateGeolist as CreateGeolist

from geoprocessor.commands.logging.Message import Message

import geoprocessor.commands.running.EndFor as EndFor
import geoprocessor.commands.running.EndIf as EndIf
import geoprocessor.commands.running.For as For
import geoprocessor.commands.running.If as If
import geoprocessor.commands.running.SetProperty as SetProperty

import geoprocessor.commands.util.UnknownCommand as UnknownCommand

class GeoProcessorCommandFactory(object):
    """
    Factory to create command instances by examining command string.
    Only instantiates the command instance but does not parse the command string.
    The command string is parsed within the command class instance."""

    # The dictionary of all available commands, in alphabetical order.
    # key: the name of the command (converted to all UPPERCASE)
    # value: the constructure function to create an instance of the command
    command_factory = {
        "CREATEGEOLAYERS": CreateGeolayers.CreateGeolayers(),
        "CREATEGEOLIST": CreateGeolist.CreateGeolist(),
        "ENDFOR": EndFor.EndFor(),
        "ENDIF": EndIf.EndIf(),
        "FOR": For.For(),
        "IF": If.If(),
        "MESSAGE": Message(),
        "SETPROPERTY": SetProperty.SetProperty()
    }

    def __init__(self):
        pass

    def __is_command_valid(self, command_name):
        """
        Checks if the command is a valid registered command by examining the command name.

        Args:
            command_name: the name of the command
        Returns:
            True if the command is registered as recognized, False if not.
        """

        registered_command_names = list(self.command_factory.keys())
        if command_name.upper() in registered_command_names:
            return True
        else:
            return False

    def new_command(self, command_string, create_unknown_command_if_not_recognized):
        """Creates the object of a command class called from a command line of the command file.

        :param command_string: a string, the command string entered by the user in the command file
        :param create_unknown_command_if_not_recognized: boolean, if TRUE, create an unknown command when the input
        command is not recognized, if FALSE, throw an error"""

        # Get command name from the first part of the command.
        command_string_trimmed = command_string.strip()
        paren_pos = command_string_trimmed.find('(')

        # Blank line so insert a BlankCommand command.
        if len(command_string_trimmed) == 0:
            #return BlankCommand.BlankCommand()
            pass

        # Comment line.
        #elif command_string_trimmed[:1] == '#':
            #return CommentCommand.CommentCommand()
            pass

        # The symbol '(' was found.
        # Assume command of syntax CommandName(Param1="...",Param2="...").
        elif (paren_pos != -1):

            # Get command name from command string, command name is before the first open parenthesis.
            command_name = command_util.parse_command_name_from_command_string(command_string_trimmed)

            # Initialize the command class object if it is a valid command.
            if self.__is_command_valid(command_name):
                command = self.command_factory[command_name.upper()]
                return command

            # Don't know the command so create an UnknownCommand.
            else:
                print("Command line is unknown command. Adding UnknownCommand: " + command_string_trimmed)
                return UnknownCommand.UnknownCommand()

        # The syntax is not recognized so create an UnknownCommand.
        else:
            print("Command line is unknown syntax. Adding UnknownCommand: " + command_string_trimmed)
            return UnknownCommand.UnknownCommand()
