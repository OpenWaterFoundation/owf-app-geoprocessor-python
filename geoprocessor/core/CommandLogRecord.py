

class CommandLogRecord(object):
    """
    Command log record, which carries a single message and corresponding status.
    """

    def __init__(self, command_status_type, problem, recommendation, log_record_type=None):
        """
        Initialize an instance.

        Args:
            command_status_type:  The command status type, such as command_status_type.SUCCESS, etc.
            problem:  The message describing the problem.
            recommendation:  The recommendation for how to resolve the problem.
            log_record_type:  The log record type, to group the messages, currently not used.
        """
        self.severity = command_status_type
        self.problem = problem
        self.recommendation = recommendation
        # Log record type is not currently used
        self.log_record_type = log_record_type
