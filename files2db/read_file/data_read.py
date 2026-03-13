"""
Created on 19/01/2021
@author: LouisLeNezet
Module to read excel files and checkout the columns names.
"""

import logging
import os
import re

import pandas as pd

from ..ui.get_infos import get_file_path


def columns_convert(col):
    """Convert column letters to integers."""
    if isinstance(col, str):
        if re.match(r"^\d+$", col):
            return int(col)
        elif re.match(r"^[A-Z]+$", col):
            col_index = [ord(c) - ord("A") + 1 for c in col.upper()]
            col_index = sum([c * (26**i) for i, c in enumerate(reversed(col_index))])
            return col_index
        else:
            raise TypeError("col should be a string of letters or an integer")
    elif not isinstance(col, int):
        raise TypeError("col should be a string or an integer")
    return col


def columns_to_int(col_start, col_end, max_col=None):
    """Convert column letters to integers."""
    if max_col is None:
        raise TypeError("max_col should be provided to check column numbers")
    if col_start is None:
        col_start = 1
    if col_end is None:
        col_end = max_col

    col_start = columns_convert(col_start)
    col_end = columns_convert(col_end)

    if col_start > col_end:
        raise ValueError("col_start should be smaller than col_end")

    if col_start > max_col:
        raise ValueError("ColStart should be smaller than the number of columns")

    if col_end > max_col:
        raise ValueError("ColEnd should be smaller than the number of columns")

    return col_start, col_end


def lines_to_int(line_start, line_end, header, max_lines=None):
    """Convert line numbers to integers."""
    if max_lines is None:
        raise TypeError("max_lines should be provided to check line numbers")

    if header is None:
        header = 1
    if line_start is None:
        line_start = header + 1
    if line_end is None:
        line_end = max_lines

    if line_start < 1:
        raise ValueError("line_start should be greater than 0")

    if header >= line_start:
        raise ValueError("header should be smaller than line_start")

    if line_start > line_end:
        raise ValueError("line_start should be smaller than line_end")

    if line_end > max_lines:
        raise ValueError("line_end should be smaller than the number of rows")

    return line_start, line_end, header


def read_file(
    file_to_add_path: str,
    header=1,
    line_start=2,
    line_end=None,
    col_start: str = "A",
    col_end: str = None,
    sheet_name=None,
    encoding="utf8",
    sep=None,
):
    """Read dataframe file from path and export it in pandas DataFrame.

    Beware the all indexes in file_infos should be integers and are in base 1.
    i.e. the first line is 1, the first column is 1.

    Parameters
    ----------
    file_to_add_path : str
        Path to excel or csv file.

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
            file_to_add_path,
        )
        raise FileNotFoundError(f"Couldn't access File {file_to_add_path}")

    # Read the file depending on the extension
    if re.search(string=file_to_add_path, pattern=r"\.csv$"):
        if sep is None:
            logging.error(
                "No separator available please complete data in repertory %s",
                file_to_add_path,
            )
            raise KeyError(f"No separator available for {file_to_add_path}")
        file_read = pd.read_csv(
            file_to_add_path, sep=sep, encoding=encoding, header=None, dtype="str"
        )
    elif re.search(string=file_to_add_path, pattern=r"\.(xlsx|xls|xlsm)$"):
        if sheet_name is None:
            logging.error("No sheet available please complete data in repertory")
            raise KeyError(f"No sheet available for {file_to_add_path}")
        file_read = pd.read_excel(file_to_add_path, sheet_name=sheet_name, header=None, dtype="str")
    else:
        raise TypeError(f"File {file_to_add_path} should be either an .xlsx, .xls, xlsm or a .csv")

    # Check for column and line start and end
    col_start, col_end = columns_to_int(col_start, col_end, file_read.shape[1] + 1)
    line_start, line_end, header = lines_to_int(
        line_start, line_end, header, file_read.shape[0] + 1
    )

    # Set the header
    file_read.columns = file_read.iloc[header - 1]

    row_bf_data = range(0, line_start - 1)
    row_af_data = range(line_end, file_read.shape[0])
    row_to_skip = [*row_bf_data, *row_af_data]

    # Skip the lines before the header and between the header and the first line
    file_read.drop(row_to_skip, inplace=True)
    file_read.fillna(pd.NA, inplace=True)
    file_read.replace("", pd.NA, inplace=True)

    # Read the file from the line start to the line end and from the column start to the column end
    file_to_add = file_read.iloc[:, col_start - 1 : col_end]
    file_to_add = file_to_add.astype("string")

    return file_to_add


def check_files_exist(files_path: pd.Series):
    """Check for the existence of all files in the given series

    Parameters
    ----------
    files_path : pd.Series
        Series containing the files paths to check

    Raises
    ------
    FileNotFoundError
        File not found, could not access the file.
    """
    # Check for all file if accessible
    for file_path in files_path:
        # Change '/' to '\\'
        file_path = get_file_path(file_path.replace("/", "\\"))
        if int(os.path.isfile(file_path)):
            pass
        else:
            logging.error(
                "Couldn't access file:\n%s\nPlease make sure the file is present",
                file_path,
            )
            raise FileNotFoundError("Couldn't access File")
