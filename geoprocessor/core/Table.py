class Table(object):

    """
    The Table class holds tabular data objects.
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

        return self.df[column_name].tolist()


