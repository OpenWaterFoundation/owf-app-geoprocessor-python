import geoprocessor.util.CommonUtil as CommonUtil
import geoprocessor.commands.layers.CreateGeolayers as CreateGeolayers
import geoprocessor.commands.layers.CreateGeolist as CreateGeolist
import geoprocessor.commands.util.UnknownCommand as UnknownCommand


class GeoProcessorCommandFactory():
    """Factory to create command classes. Only instantiates the class but does not parse the command string. The
    command string is parsed from within the command class instance."""

    # the dictionary of all available commands
    # key: the name of the command as called from the user (converted to all UPPERCASE)
    # value: the command class object to be created
    command_factory = {"CREATEGEOLAYERS": CreateGeolayers.CreateGeolayers(),
                       "CREATEGEOLIST": CreateGeolist.CreateGeolist()}

    def __init__(self):
        pass

    def __is_command_valid(self, command_name):
        """Checks if the command is a valid registered . Returns TRUE if the command is within in the command factory
        dictionary. Returns FALSE is the command is not found in teh command factory dictionary.

        :param command_name: the name of the command as entered by the user in the command line"""

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

        # get command name from the first part of the command
        command_string_trimmed = command_string.strip()
        paren_pos = command_string_trimmed.find('(')

        # blank line so insert a BlankCommand command
        if len(command_string_trimmed) == 0:
            return BlankCommand.BlankCommand()

        # comment line
        elif command_string_trimmed[:1] == '#':
            return CommentCommand.CommentCommand()

        # the symbol '(' was found
        # Assume command of syntax CommandName(Param1="...",Param2="...")
        elif not (paren_pos == -1):

            # get command name from command string, command name is before the first open parenthesis
            command_name = CommonUtil.get_command_name(command_string_trimmed)

            # initiate the command class object if it is a valid command
            if self.__is_command_valid(command_name):
                object = self.command_factory[command_name.upper()]
                return object

            # don't know the command so create an UnknownCommand
            else:
                print("Command line is unknown command. Adding UnknownCommand: " + command_string_trimmed)
                return UnknownCommand.UnknownCommand()

       # the syntax is not readable so create an UnknownCommand
        else:
            print("Command line is unknown syntax. Adding UnknownCommand: " + command_string_trimmed)
            return UnknownCommand.UnknownCommand()
