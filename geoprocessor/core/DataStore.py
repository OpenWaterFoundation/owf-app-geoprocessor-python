import sqlalchemy
from sqlalchemy.engine.url import URL


class DataStore(object):

    """
     DataStore (also called "datastore" and "data store"; mixed case "DataStore" is used in GeoProcessor for
     readability) is a persistent storage component that stores tabular and other data. Currently, the concept of
     datastores in the GeoProcessor focuses on databases and web services that store tabular data. Database datastores
     use a database connection, typically using Open Database Connectivity standard, and web service datastores
     typically use a REST web service API. Datastores have the following characteristics:

        * Datastore ID is used for identification.
        * Datastore also has a descriptive name.
        * Connection information such as database server name and port number are used for databases.
        * Web service requires root URL for start of API URLs.
        * Datastores may require credentials to access data.
        * Datastores are opened to establish a connection and can be closed to free resources.

     The GeoProcessor provides the OpenDataStore command to open a datastore connection at run-time, and other commands
     are used to read from and write to datastores. This is useful to run automated workflows. In the future, the
     ability to configure datastore connections for use at software startup will be enabled, which is useful to
     interactively browse datastore resources.
    """

    def __init__(self, datastore_id):
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

        # "dialect" is used to format the database connection URL for the matching database driver software.
        self.dialect = None

        # "db_uri" is the string of characters designed for unambiguous identification of resources and extensibility
        # via the URI scheme to reference the connection of the DataStore's database.
        self.db_uri = None

        # "engine" is the starting point for any SQLAlchemy application. It’s “home base” for the actual database and
        # its DBAPI, delivered to the SQLAlchemy application through a connection pool and a Dialect, which describes
        # how to talk to a specific kind of database/DBAPI combination.
        self.engine = None

        # "connection" is an instance of SqlAlchemy Connection, which is a proxy object for an actual DBAPI connection.
        # The DBAPI connection is retrieved from the connection pool at the point at which Connection is created.
        self.connection = None

        # "is_connected" is a Boolean value to determine if a SqlAlchemy Connection is open.
        self.is_connected = False

        # "inspector" is the entry point to SQLAlchemy’s public API for viewing the configuration and construction of
        # in-memory objects. It is an object which provides a known interface of the connected database instance.
        self.inspector = None

        # "status_message" is a string that provides the user information about the DataStore's current status.
        self.status_message = "No connection - connection has not been attempted."

        self.metadata = sqlalchemy.MetaData()

    def close_db_connection(self):
        """
        Closes the DataStore's connection to the database.

        Returns: None
        """

        # Close the SqlAlchemy database connection.
        self.connection.close()

        # Update the status message to inform users that the connection has been closed.
        self.update_status_message("Not connected. Connection has been closed.")

        # Update the is_connected Boolean value to reflect that the connection is closed.
        self.is_connected = False

    def get_db_uri_postgres(self, host, dbname, user, password, port="5432"):
        """
        Create the database URI for the PostgreSql dialect. Assign the URI to the DataStore's db_uri attribute.

        Args:
            host (str): The database server name or IP address.
            dbname (str): The name of the database.
            user (str): The database user.
            password (str): The database password.
            port (str): The database port. Default: "5432"

        Return: None
        """

        # Set the argument variables to create the database URI.
        postgres_db = {'drivername': "postgres",
                       'username': user,
                       'password': password,
                       'host': host,
                       'port': port,
                       'database': dbname}

        # Create the database URI and assign it to the DataStore's db_uri attribute.
        self.db_uri = URL(**postgres_db)

        # Assign the database dialect to the DataStore's dialect attribute.
        self.dialect = "POSTGRES"

    def open_db_connection(self):
        """
        Open a database connection.

        Return: None.
        """

        # Create the SqlAlchemy engine and assign it to the DataStore's engine attribute.
        self.engine = sqlalchemy.create_engine(self.db_uri)

        # Create the SqlAlchemy connection and assign it to the DataStore's connection attribute.
        self.connection = self.engine.connect()

        # Update the status message to inform users that the connection has been opened.
        self.update_status_message("Connected.")

        # Update the is_connected Boolean value to reflect that the connection is open.
        self.is_connected = True

        # Create the SqlAlchemy inspect object and assign it to the DataStore's inspector attribute.
        self.inspector = sqlalchemy.inspect(self.engine)

    def return_table_names(self):
        """
        Get a list of the table names currently in the connected database.

        Return: A list of the database's table names.
        """

        # Return a list of the database's table names.
        return self.inspector.get_table_names()

    def return_col_names(self, table):
        """
        Get a list of the column names in a given database table.

        Args:
            table (str): An existing table name within the database.

        Return: A list of the column names in the table.
        """

        # Return a list of the column names in the table.
        return [col["name"] for col in self.inspector.get_columns(table)]

    def return_col_types(self, table):
        """
        Get a list of the column types in a give database table.

        Args:
            table (str): An existing table name within the database.

        Return: A list of the column data types in the table.
        """

        # Return a list of the column data types in the table.
        return [col["type"] for col in self.inspector.get_columns(table)]

    def return_int_col_names(self, table):
        """
        Get a list of the column names that hold integer data in a given database table.

        Args:
            table (str): An existing table name within the database.

        Return: A list of column names in the table that holds integer data.
        """

        import sqlalchemy.sql.sqltypes
        return [col["name"] for col in self.inspector.get_columns(table) if type(col["type"]) == sqlalchemy.sql.sqltypes.INTEGER]

    def run_sql(self, sql):
        """
        Run a SQL statement on the DataStore's database.

        Args:
            sql (str): the SQL statement to run.

        Return: None
        """

        # Start a change to the connection.
        trans = self.connection.begin()

        # Execute the SQL statement on the database.
        self.connection.execute(sql)

        # Commit the changes made to the database.
        trans.commit()

    def update_status_message(self, message):
        """
        Updates the status message. The existing status message will be overwritten.

        Args:
            message (str): the new status message

        Return: None
        """

        # Update the status message to inform users of a specific message.
        self.status_message = message
