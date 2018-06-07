class DataStore(object):

    """
    NEED TO ADD DOCUMENTATION
    """

    def __init__(self, datastore_id, datastore_connection, db_type, db_name, db_host, db_user, db_password, db_port):
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

        # "type" is the database type, used to format the database connection URL for the matching database driver
        # software. Currently the following are supported: PostgreSQL.
        self.type = db_type

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

        # "cursor" allows interaction with the database (this is available for PostGreSql databases using psycopg2
        # REF: http://initd.org/psycopg/docs/usage.html
        if self.type.upper() == "POSTGRESQL":
            self.cursor = self.connection.cursor()

    def get_list_of_tables(self):
        """
        Return a list of the tables in the DataStore's database.

        Return: a list of the tables in the DataStore's database
        """

        # An empty list to hold all of the table names.
        tables = []

        # Continue with PostGreSql logic if this DataStore holds a PostGreSql database.
        if self.type.upper() == "POSTGRESQL":

            # Select all of the table names in the public schema.
            self.cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")

            # Iterate over the table names. Returns a tuple.
            for table in self.cursor.fetchall():

                # Append the table name to the tables list.
                tables.append(table[0])

        # As more database types are configured within the GeoProcessor, include their logic in elif statements.
        else:
            pass

        # Return the list of table names.
        return tables

    def get_list_of_columns(self, table):
        """
        Return a list of columns for a specific DataStore table.

        Args:
            table (str): the name of a table in the DataStore's database

        Return: a list of columns within table=
        """

        # An empty list to hold all of the column names.
        cols = []

        # Continue with PostGreSql logic if this DataStore holds a PostGreSql database.
        if self.type.upper() == "POSTGRESQL":

            # Select all of the columns in the table.
            self.cursor.execute("select * from " + table + " LIMIT 0")

            # Iterate over the column descriptions in the table.
            for desc in self.cursor.description:

                # Append the column name to the cols list.
                # See http://initd.org/psycopg/docs/cursor.html for a description on the description index meanings.
                cols.append(desc[0])

        # As more database types are configured within the GeoProcessor, include their logic in elif statements.
        else:
            pass

        # Return the list of column names.
        return cols
