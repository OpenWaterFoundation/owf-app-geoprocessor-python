class DataStore(object):

    """
    NEED TO ADD DOCUMENTATION
    """

    def __init__(self, datastore_id, datastore_connection, host, user, password, port):
        """
        Initialize a new DataStore instance.

        Args:
            datastore_id (str):
                String that is the DataStore's reference ID. This ID is used to access the DataStore from the
                GeoProcessor for manipulation.

        """

        # "id"  is a string representing the DataStore's reference ID. This ID is used to access the DataStore from the
        # GeoProcessor for manipulation.
        self.id = datastore_id

        # "connection" is the open connection created to the database
        self.connection = datastore_connection

        # "password_length" is the length of the DataStore connection's password
        self.password_length = len(password)

        # "user" is the username of the DataStore connection
        self.user = user

        # "host" is the host of the DataStore connection
        self.host = host

        # "port" is the port of the DataStore connection
        self.port = port
