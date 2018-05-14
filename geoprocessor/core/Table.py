class Table(object):

    """
    The Table class holds tabular data objects (columns and rows). The core data is stored in a pandas data frame
    object in order to leverage the pandas library and functionality. Additional data members are used to store data
    that are not part of the pandas data frame object and are required from the GeoProcessor. These include attributes
    like a table identifier and a source filename.

    A list of registered Table instances are maintained by the GeoProcessor's self.tables property (type: list). The
    GeoProcessor's commands retrieve in-memory Table instances from the GeoProcessor's self.tables property using the
    GeoProcessor.get_table() function. New Table instances are added to teh GeoProcessor list using the add_table()
    function.

    There are a number of properties associated with each Table. The initialized properties stored within each Table
     instance are the STATIC properties that will never change (identifier, df object, and source path). The DYNAMIC
     properties (column names, number of table entries, etc.) are created when needed by accessing class functions.

    Tables can be made in memory from within the GeoProcessor. This occurs when a command is called that, by design,
    creates a new Table. When this occurs, the in-memory Table is assigned a table_id from within the command,
    the df is created from within the command and the source_path is set to 'MEMORY'or 'NONE'.
    """

    def __init__(self, table_id, pandas_df, table_source_path, properties=None):
        """
        Initialize a new Table instance.

        Args:
            table_id (str):
                String that is the Table's reference ID. This ID is used to access the Table from the GeoProcessor for
                manipulation.
            pandas_df (pandas Data Frame object):
                Object created by the pandas library. All Table manipulations are performed on the Tables's pandas data
                 frame object.
            table_source_path (str):
                The full pathname to the original file on the user's local computer. If the tables was made in memory
                from the GeoProcessor, this value is set to `MEMORY`.
            properties ({}):
                A dictionary of user (non-built-in) properties that can be assigned to the tables.
                These properties facilitate processing.
        """

        # "id" is a string that is the Table's reference ID. This ID is used to access the Table from the GeoProcessor
        # for manipulation.
        self.id = table_id

        # "pandas_df" is a Pandas Data Frame object created by the pandas library. All manipulations are performed on
        # the Table's pandas data frame.
        self.df = pandas_df

        # "source_path" (str) is the full pathname to the original data file on the user's local computer
        self.source_path = table_source_path

        # "properties" (dict) is a dictionary of user (non-built-in) properties that are assigned to the layer.
        # These properties facilitate processing and may or may not be output to to a persistent format,
        # depending on whether the format allows general properties on the layer.
        # If None an empty dictionary is created.
        # TODO smalers 2018-01-10 does the QGIS layer have such an object already that could be used without confusion?
        # - don't want a bunch of internal properties visible to the user.
        if properties is None:
            self.properties = {}
        else:
            self.properties = properties

    def get_column_values_as_list(self, column_name):
        """
        Return all of the column values for a given column.

        Args:
            column_name (str): the name of the column of interest

        Return: A list of the column values.
        """

        # Return a list of the column values for the given input column.
        return self.df[column_name].tolist()

    def count(self, returnCol=True):
        """
        Return either the number of columns within the table or the number of rows within the table.

        Args:
            returnCol: Boolean. If TRUE, returns column count. If FALSE, returns row count.

        Return: The column or row count (int). Returns None if returnCol argument is invalid Boolean.
        """

        row, col = self.df.shape
        if returnCol:
            return col
        elif returnCol is False:
            return row
        else:
            return None
