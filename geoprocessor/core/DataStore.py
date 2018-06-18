import sqlalchemy
from sqlalchemy.engine.url import URL


class DataStore(object):

    """
    NEED TO ADD DOCUMENTATION
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

        self.dialect = None

        self.db_uri = None

        self.engine = None

        self.connection = None

        self.is_connected = False

        self.inspector = None

        self.status_message = "No connection - connection has not been attempted."

    def close_db_connection(self):

        self.connection.close()
        self.update_status_message("Not connected. Connection has been closed.")
        self.is_connected = False

    def get_db_uri_postgres(self, host, dbname, user, password, port="5432"):

        postgres_db = {'drivername': "postgres",
                       'username': user,
                       'password': password,
                       'host': host,
                       'port': port,
                       'database': dbname}

        self.db_uri = URL(**postgres_db)
        self.dialect = "POSTGRES"

    def open_db_connection(self):

        self.engine = sqlalchemy.create_engine(self.db_uri)
        self.connection = self.engine.connect()
        self.update_status_message("Connected.")
        self.is_connected = True
        self.inspector = sqlalchemy.inspect(self.engine)

    def return_table_names(self):

        return self.inspector.get_table_names()

    def return_col_names(self, table):

        return [col["name"] for col in self.inspector.get_columns(table)]

    def update_status_message(self, message):
        """
        Updates the status message. The existing status message will be overwritten.

        Args:
            message (str): the new status message

        Return: None
        """

        self.status_message = message

    def run_sql(self, sql):

        trans = self.connection.begin()
        self.connection.execute(sql)
        trans.commit()