# Utility functions related to the pandas library

import pandas as pd


def create_data_frame_from_delimited_file(file_path, delimiter):
    """
    Creates a pandas data frame object from a delimited file.

    Args:
        file_path (str): the full pathname to a delimited file
        delimiter (str): the delimiter symbol (often times is a comma)

    Returns:
        A pandas data frame object. This is the object that support the GeoProcessor's Table object.
    """

    # Define and return the data frame from the delimited file. Pass the delimited file's delimiter as the sep argument.
    df = pd.DataFrame.from_csv(file_path, sep=delimiter)
    return df


def create_data_frame_from_excel(excel_workbook_path, excel_worksheet_name=None):
    """
    Creates a pandas data frame object from an excel file.

    Args:
        excel_workbook_path (str): the full pathname to the excel file
        excel_worksheet_name (str): the name of the worksheet to read from the excel workbook

    Returns:
        A pandas data frame object. This is the object that support the GeoProcessor's Table object.
    """

    # If an excel worksheet is defined, define and return the data frame from the worksheet.
    if excel_worksheet_name:
        df = pd.read_excel(excel_workbook_path, sheet_name=excel_worksheet_name)
        return df

    # If an excel worksheet is not defined, define and return the data frame from the FIRST worksheet.
    else:
        df = pd.read_excel(excel_workbook_path)
        return df


def create_excel_workbook_obj(excel_workbook_path):
    """
    Creates a pandas excel workbook object from an excel file.

    Args:
        excel_workbook_path (str): the full pathname to the excel file

    Returns:
        A pandas excel workbook object. This object allows for the GeoProcessor to read the properties of the Excel
         workbook. For example, it can return the names of all of the available worksheets.
    """

    # Define and return the pandas excel workbook object from the excel file.
    xl = pd.ExcelFile(excel_workbook_path)
    return xl


def write_df_to_delimited_file(df, output_file_full_path, include_header, include_index, delimiter=","):
    """
    Writes a pandas data frame object to a delimited file.

    Args:
        df (object): the pandas data frame object to write
        output_file_full_path (str): the full pathname to an output delimited file
        include_header (bool): If TRUE, write the header row. If FALSE, exclude the header row.
        include_index (bool): If TRUE, write the index column. If FALSE, exclude the index column.
        delimiter (str): the delimiter symbol to use in the output delimited file. Must be a single character. Default
         value is a comma.

    Returns: None
    """

    # Write the pandas data frame to a csv file.
    df.to_csv(output_file_full_path, header=include_header, index=include_index, sep=delimiter)


def write_df_to_excel(df, excel_workbook_path, excel_worksheet_name, include_header, include_index):
    """
    Writes a pandas data frame object to an excel file.

    Args:
        df (object): the pandas data frame object to write
        excel_workbook_path (str): the full pathname to an excel workbook (either existing or non-existing)
        excel_worksheet_name (str): the worksheet name to write to (either existing or non-existing)
        include_header (bool): If TRUE, write row index. If FALSE, do not include row index.
        include_index (bool): If TRUE, write out column names. If FALSE, do not write column names.

    Returns: None
    """

    # REf: https://stackoverflow.com/questions/20219254/
    # how-to-write-to-an-existing-excel-file-without-overwriting-data-using-pandas
    from openpyxl import load_workbook

    # Set the writer object.
    writer = pd.ExcelWriter(excel_workbook_path, engine="openpyxl")

    # Removes the default styling of the table (provided in the pandas library).
    import pandas.io.formats.excel
    pandas.io.formats.excel.header_style = None

    # If applicable, inform the writer object of the already-existing excel workbook.
    book = load_workbook(excel_workbook_path)
    writer.book = book

    # If applicable, inform the writer object of the already-existing excel worksheets.
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    # Write the df to the excel workbook with the given worksheet name.
    df.to_excel(writer, sheet_name=excel_worksheet_name, index=include_index, header=include_header)
    writer.save()
