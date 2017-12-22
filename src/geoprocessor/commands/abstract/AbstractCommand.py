import geoprocessor.util.CommonUtil as CommonUtil

class AbstractCommand():
    """Parent to all other command classes. Stores common data. Provides common functions, which can be overloaded in
    child classes."""

    def __init__(self):

        # full command string (with indentation)
        self.command_string = ""

        # command name as user would see. will be set when command is parsed. will NOT be set if an UnknownCommand.
        self.command_name = ""

        # command processor, needed to interact with the geoprocessing environment
        self.command_processor = None

        # command parameters, a dictionary of input parameter names and parameter values
        self.command_parameters = {}

    def initialize_command(self, command_string, processor, full_initialization):
        """Initialize the command by setting the processor and parsing parameters."""

        # sets the command processor
        self.command_processor = processor

        # if full initialization, the input parameters will be parsed and the values will be added to the
        # command_parameters
        if full_initialization:

            # the following will call the AbstractCommand.parse_command by default
            self.parse_command(command_string)

    def parse_command(self, command_string):
        """Parse the command string and assign the abstract command command_parameters variable with a dictionary of
        the input parameter names and values."""

        # get the parameter string from the command string (this is the string within the parenthesis of a command
        # string)
        parameter_string = CommonUtil.to_parameter_string(command_string)

        # parse the single parameter string into a list of parameter items. parameter items are strings that represent
        # key value pairs for EACH parameter in the parameter string. the parameter items are separated by commas in
        # the parameter string
        parameter_items = CommonUtil.to_parameter_items(parameter_string)

        # parse each parameter item by its key and value. if the parameter value is supposed to be in list format
        # (rather than string format) convert it to a list. return a dictionary with each parameter as a separate
        # entry (key: parameter name as entered by the user, value: the parameter value (in either string or list
        # format) assign the parameter dictionary to the command_parameters variable
        self.command_parameters = CommonUtil.to_parameter_dic(parameter_items)

    def return_parameter_value_required(self, parameter_name):
        """Returns the user-defined parameter value given a parameter name. Throws error if the parameter name was not
        entered by the user."""

        if parameter_name in list(self.command_parameters.keys()):
            return self.command_parameters[parameter_name]
        else:
            print "ERROR: the required parameter ({}) does not exist in the command string ({}).".format(parameter_name, self.command_string)
            return None

    def return_parameter_value_optional(self, parameter_name, default_value):
        """Returns the user-defined parameter value given a parameter name. Returns default value if the parameter name
        was not entered by the user. """

        if parameter_name in list(self.command_parameters.keys()):
            return self.command_parameters[parameter_name]
        else:
            return default_value

    def run_command(self):
        '''Run the command. This should always be overwritten by the command class.'''

        print 'In AbstractCommand.run_command'
