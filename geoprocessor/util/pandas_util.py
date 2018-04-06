import pandas as pd

def create_data_frame_from_excel(excel_workbook_path, excel_worksheet_name):

    if excel_worksheet_name:
        df = pd.read_excel(excel_workbook_path, sheet_name=excel_worksheet_name)
    else:
        df = pd.read_excel(excel_workbook_path)
    return df

def create_excel_workbook_obj(excel_workbook_path):

    xl = pd.ExcelFile(excel_workbook_path)
    return xl

def write_df_to_excel(df, excel_workbook_path, excel_worksheet_name):

    # REf:
    # https://stackoverflow.com/questions/20219254/
    # how-to-write-to-an-existing-excel-file-without-overwriting-data-using-pandas
    from openpyxl import load_workbook
    writer = pd.ExcelWriter(excel_workbook_path, engine="openpyxl")
    import pandas.io.formats.excel
    pandas.io.formats.excel.header_style = None
    book = load_workbook(excel_workbook_path)
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    df.to_excel(writer, index=False, sheet_name=excel_worksheet_name)
    writer.save()
