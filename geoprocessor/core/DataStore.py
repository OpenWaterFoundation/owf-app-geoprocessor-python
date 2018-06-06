class DataStore(object):

    """
    NEED TO ADD DOCUMENTATION
    """

    def __init__(self, datastore_id, datastore_connection, db_name, db_host, db_user, db_password, db_port):
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

        # "name" is the name of the database
        self.name = db_name

        # "password_length" is the length of the DataStore connection's password
        self.password_length = len(db_password)

        # "user" is the username of the DataStore connection
        self.user = db_user

        # "host" is the host of the DataStore connection
        self.host = db_host

        # "port" is the port of the DataStore connection
        self.port = db_port
