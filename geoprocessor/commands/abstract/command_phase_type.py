"""
Possible values of command phase.
When the code migrates to Python 3 this can be replaced with an Enum named CommandPhaseType.

INITIALIZATION:  Creation and initialization of the command.
DISCOVERY:  Run the command in discovery mode.
RUN:  Run the command completely.
"""

INITIALIZATION = 'INITIALIZATION'
DISCOVERY = 'DISCOVERY'
RUN = 'RUN'

def get_command_status_types(sort=False):
    """
    Return the list of valid command phases.

    Args:
        sort:  If True, sort alphabetically.  If False, return in order of execution (default).

    Returns:
        The list of phase types, for example for use in command parameter choice.

    """
    if ( sort ):
        # Sort alphabetically
        return [ DISCOVERY, INITIALIZATION, RUN ]
    else:
        # Return in order of processing order.
        return [ INITIALIZATION, DISCOVERY, RUN ]
