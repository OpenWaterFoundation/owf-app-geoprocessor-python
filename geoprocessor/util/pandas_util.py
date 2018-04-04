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

    writer = pd.ExcelWriter(excel_workbook_path, engine="xlsxwriter")
    import pandas.io.formats.excel
    pandas.io.formats.excel.header_style = None
    df.to_excel(writer, index=False, sheet_name=excel_worksheet_name)
    workbook = writer.book
    worksheet = writer.sheets[excel_worksheet_name]
    writer.save()
