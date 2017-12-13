from commandprocessor.core import command_dictionary

# each command class has an ordered list of parameters (each with a specific name)
# return the ordered list of parameter names given the command name
def get_command_parameter_names(command_name):

    command_parameter_names = command_dictionary.command_dictionary[command_name].parameter_names
    return command_parameter_names

# each command class has a dictionary of parameter names and values (set to None or a default value)
# return the dictionary of parameter names and values given the command name
def get_command_parameter_values_dic(command_name):

    parameter_values_dic = command_dictionary.command_dictionary[command_name].parameter_values
    return parameter_values_dic

# check if command name exists
def is_command_name_valid(command_name):

    valid_command_name = False

    list_of_command_names = list(command_dictionary.command_dictionary.keys())

    if command_name in list_of_command_names:
        valid_command_name = True

    return valid_command_name
