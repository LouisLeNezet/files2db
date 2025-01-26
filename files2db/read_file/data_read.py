# -*- coding: utf-8 -*-
"""
Created on 19/01/2021
@author: LouisLeNezet
Module to read excel files and checkout the columns names.
"""
import os
import re
import logging
import pandas as pd

def read_file(
    file_to_add_path:str, header = 1, line_start = 2, line_end = None,
    col_start = 1, col_end = None, sheet_name = None, encoding = "utf8",
    sep = None
):
    """Read dataframe file from path and export it in pandas DataFrame.
    
    Beware the all indexes in file_infos should be integers and are in base 1.
    i.e. the first line is 1, the first column is 1.

    Parameters
    ----------
    file_to_add_path : str
        Path to excel or csv file.
    file_infos : pd.Series
        All the infos about the file to read.

    Returns
    -------
    file_to_add: DataFrame
        Panda DataFrame with all data read

    Raises
    ------
    FileNotFoundError
        File doesn't exist
    TypeError
        File isn't a csv or a xlsx
    KeyError
        No sheet name given for excel file
        No separator given for csv file
    ValueError
        The header should be smaller than the line start or
        the line start should be smaller than the line end or
        the column start should be smaller than the column end or
        the column end should be smaller or equal than the number of columns or
        the line end should be smaller or equal than the number of rows in the file.
    """
    if not os.path.isfile(file_to_add_path):
        logging.info(
            "Couldn't access file:\n %s \n Please make sure the file is present",
            file_to_add_path
        )
        raise FileNotFoundError(f"Couldn't access File {file_to_add_path}")

    # Read the file depending on the extension
    if re.search(string=file_to_add_path, pattern=r"\.csv$"):
        if sep is None:
            logging.error(
                "No separator available please complete data in repertory %s",
                file_to_add_path
            )
            raise KeyError(f"No separator available for {file_to_add_path}")
        file_read = pd.read_csv(
            file_to_add_path, sep=sep, encoding=encoding,
            header=None, dtype="object"
        )
    elif re.search(string=file_to_add_path,pattern=r"\.(xlsx|xls|xlsm)$"):
        if sheet_name is None:
            logging.error(
                "No sheet available please complete data in repertory %s",
                sheet_name
            )
            raise KeyError(f"No sheet available for {file_to_add_path}")
        file_read = pd.read_excel(
            file_to_add_path, sheet_name=sheet_name,
            header=None, dtype="object"
        )
    else:
        raise TypeError(
            f"File {file_to_add_path} should be either an .xlsx, .xls, xlsm or a .csv"
        )

    if col_end is None:
        col_end = file_read.shape[1] + 1
    if line_end is None:
        line_end = file_read.shape[0] + 1

    # Check for correct values
    if header > line_start:
        logging.error(
            "header should be smaller than line_start in file %s",
            file_to_add_path
        )
        raise ValueError("header should be smaller than line_start")

    if line_start > line_end:
        logging.error(
            "line_start should be smaller than line_end in file %s",
            file_to_add_path
        )
        raise ValueError("line_start should be smaller than line_end")

    if col_start > col_end:
        logging.error(
            "col_start should be smaller than col_end in file %s",
            file_to_add_path
        )
        raise ValueError("col_start should be smaller than col_end")

    if col_end - 1 > file_read.shape[1]:
        logging.error(
            "col_end should be smaller than the number of columns in file %s",
            file_to_add_path
        )
        raise ValueError("ColEnd should be smaller than the number of columns")

    if line_end - 1 > file_read.shape[0]:
        logging.error(
            "line_end should be smaller than the number of rows in file %s",
            file_to_add_path
        )
        raise ValueError("line_end should be smaller than the number of rows")

    # Set the header
    file_read.columns = file_read.iloc[header - 1]

    row_bf_data = range(0, line_start - 1)
    row_af_data = range(line_end, file_read.shape[0])
    row_to_skip = [*row_bf_data, *row_af_data]

    # Skip the lines before the header and between the header and the first line
    file_read.drop(row_to_skip, inplace=True)

    # Read the file from the line start to the line end and from the column start to the column end
    file_to_add = file_read.iloc[ : , col_start - 1 : col_end]

    return file_to_add


def get_columns(file_to_add, field_orga):
    """
    Found all the columns present inside DataFrame by category.

    Parameters
    ----------
    file_to_add : DataFrame
        Data to analyse.
    field_orga : DataFrame
        Organisation of the data.

    Returns
    -------
    all_columns : Dict
        Dict of all the column names present in the data frame in a list for each field category
    """
    genealogy_col = list(set(file_to_add.columns) &
                            set(field_orga.loc[field_orga["Category"] == "Genealogy", "Field"]))
    dcf_col = [col for col in file_to_add.columns if "Dys_" in col]
    infos_col = list(set(file_to_add.columns) &
                        set(field_orga.loc[field_orga["Category"] == "Infos", "Field"]))
    cani_dna_col = list(set(file_to_add.columns) &
                        set(field_orga.loc[field_orga["Category"] == "CaniDNA", "Field"]))
    adress_col = list(set(file_to_add.columns) &
                        set(field_orga.loc[field_orga["Category"] == "Adresse", "Field"]))
    id_col = list(set(file_to_add.columns) &
                    set(field_orga.loc[field_orga["Category"] == "Identity", "Field"]))
    id_supl_col = list(set(file_to_add.columns) &
                        set(field_orga.loc[field_orga["Category"] == "IdentitySupl", "Field"]))
    all_cols = {"Genealogy": genealogy_col,
                "DCF": dcf_col,
                "Infos": infos_col,
                "CaniDNA": cani_dna_col,
                "Adress": adress_col,
                "Id": id_col,
                "IdSupl": id_supl_col}
    return all_cols
