#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 22/10/2021
@author: LouisLeNezet
Main script fo the concatenation of the files
"""
import os
import warnings
import re
import logging
from datetime import date
import pandas as pd
import typer

from files2db.read_file.data_reading import read_file
from files2db.data_mg.norm_data import norm_data
from files2db.read_file.data_reading import load_file_orga
from files2db.read_file.check_file import get_db_from_excel, get_db_from_csv
from files2db.ui.get_infos import get_file_path, get_os, welcome
from files2db.data_process.null_values import not_null

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

def start():
    """Get the current directory and operating system.
    Print a welcoming message
    """
    op_sys, path_wd = get_os()
    welcome("concatenate files", path_wd, op_sys)
    return(op_sys, path_wd)

def check_main_file(path:str, db_orga:str):
    """_summary_

    Parameters
    ----------
    path : str
        Path to main file

    Raises
    ------
    TypeError
        The file extension should either be xls, xlsx, xlsm or csv
    """
    path_file = get_file_path(path)
    if re.search(string=path_file, pattern=r"\.csv$"):
        db_dict = get_db_from_csv(path_file, db_orga)
    elif re.search(string=path_file, pattern=r"\.(xlsx|xls|xlsm)"):
        db_dict = get_db_from_excel(path_file, db_orga)
    else:
        raise TypeError(f"File {path_file} should be either an .xlsx, .xls, xlsm or a .csv")

    return db_dict

def check_files_exist(files_path:pd.Series):
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
        file_path = get_file_path(file_path.replace("/",'\\'))
        if int(os.path.isfile(file_path)):
            pass
        else:
            logging.error(
                "Couldn't access file:\n%s\nPlease make sure the file is present",
                file_path
            )
            raise FileNotFoundError("Couldn't access File")

def iterate_file(file):
    """Iterate through all files in the database

    Args:
        file (pd.DataFrame): Pandas dataframe containing the files to parse
    """
    line_raw = 0
    line_dropped_na = 0
    line_normed =0
    all_data = pd.DataFrame()
    for index in file.index:
        file_infos = file.loc[index].copy()
        file_errors_all = []
        file_name = file_infos["FileName"]
        file_loc = str(file_infos["Folder"] + "\\" + file_name)
        file_lect = file_infos["Lecteur"]
        file_infos.loc["FileLoc"] = file_loc
        file_path = get_file_path(file_infos["FilePath"])
        print("--------------------------------------------------")
        print(file_name)

        # Read  file
        file_data = read_file(file_path, file_infos)
        line_raw += file_data.shape[0]

        # Delete all rows with only NA values
        file_data = file_data.dropna(how="all",axis="index")
        line_dropped_na += file_data.shape[0]

        # Add meta data to file
        file_data["File"] = file_loc
        if not_null(file_lect):
            file_data["Dys_NA_Lecteur"] = file_lect

        # Normalize resulting file
        file_data, file_errors = norm_data(file_data)
        file_errors_all.append(file_errors)
        line_normed += file_data.shape[0]

        # Add file to merged data_frame
        all_data = pd.concat([all_data,file_data])

    # Save as csv
    save_path = os.path.join(f"/DataGenerated/AllID_{date.today()}.csv")
    print(save_path)
    all_data.to_csv(get_file_path(f"./DataGenerated/AllID_{date.today()}.csv"),sep=";")

    logging.info("LINE_RAW: %s", line_raw)
    logging.info("LINE_DROPPED_NA: %s", line_dropped_na)
    logging.info("LINE_NORMED: %s", line_normed)
    logging.info("Data obtained: %s", all_data.shape[0])

def main(path:str):
    """Main function of the concatenation script.
    Welcome user, check file given
    Iterate through all the files listed

    Args:
        path (str): String corresponding to the path of the main file to use.
    """
    _op_sys, _path_wd = start()
    db_orga = load_file_orga()
    db_get = check_main_file(path, db_orga)
    check_files_exist(db_get["Files"]["FilePath"])
    iterate_file(db_get["Files"].loc[db_get["Files"]["ToAdd"] == 1])


if __name__=="__main__":
    typer.run(main)
