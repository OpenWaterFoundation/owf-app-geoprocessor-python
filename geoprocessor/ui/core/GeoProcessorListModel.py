


class GeoProcessorListModel(object):

    def __init__(self, geoprocessor, command_list_view):
        self.gp = geoprocessor
        self.gp.add_model_listener(self)

        self.command_list_view = command_list_view
        self.command_list_view.add_model_listener(self)

    def add_element(self, command_string):
        """
        Add a command to the end of the list
        :param command_string:
        :return:
        """
        self.gp.add_command_string(command_string)

    def command_list_read(self):
        command_list = self.gp.commands
        self.command_list_view.set_command_list(command_list)
        self.initialize_command_list()

    def command_list_ran(self):
        self.command_list_view.update_ui_command_list_errors()

    def delete_element(self, index):
        """
        Remove element from geoprocessor
        :param index:
        :return:
        """

        self.gp.remove_command(index)

    def get_command_list(self):

        return self.gp.get_command_list()

    def run_all_commands(self):

        # Runs the geoprocessor's processor_run_commands function to run the existing commands
        # that exist in the processor.
        print("Running commands in processor...")

        self.gp.run_commands()

    def initialize_command_list(self):

        self.command_list_view.update_command_list_widget()
        self.command_list_view.enable_buttons()


