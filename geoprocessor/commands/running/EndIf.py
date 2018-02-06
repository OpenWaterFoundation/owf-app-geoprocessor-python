# EndIf command

from geoprocessor.commands.abstract.AbstractCommand import AbstractCommand

from geoprocessor.core.CommandLogRecord import CommandLogRecord
from geoprocessor.core.CommandParameterMetadata import CommandParameterMetadata
import geoprocessor.core.command_phase_type as command_phase_type
import geoprocessor.core.command_status_type as command_status_type

import geoprocessor.util.command_util as command_util
import geoprocessor.util.validator_util as validators


class EndIf(AbstractCommand):
    """
    The EndIf command indicates the end of an If block.
    """

    __command_parameter_metadata = [
        CommandParameterMetadata("Name", type(""))
    ]

    def __init__(self):
        """
        Initialize the command instance.
        """
        super(EndIf, self).__init__()
        self.command_name = "EndIf"
        self.command_parameter_metadata = self.__command_parameter_metadata

    def check_command_parameters(self, command_parameters):
        """
        Check the command parameters for validity.
        Args:
            command_parameters:

        Returns:

        """
        print('In EndIf.check_command_parameters - need to complete.')

    def get_name(self):
        """
        Return the name of the EndIf (will match name of corresponding If).

        Returns:
            The name of the EndIf (will match name of corresponding If).
        """
        return self.command_parameters.get("Name", None)

    def run_command(self):
        print("In EndIf.run_command")
