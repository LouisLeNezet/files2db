#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 22/10/2021
@author: LouisLeNezet
Check for presence absence of file, sheets, columns
"""
import logging
from importlib import resources
import pandas as pd
from openpyxl import load_workbook
from ui.get_infos import get_file_path
from read_file.data_read import read_file

def load_file_orga():
    """Load internal file_orga.csv as a Pandas DataFrame and transform it into a dictionary."""
    with resources.open_text("data", "file_orga.csv") as csvfile:
        orga = pd.read_csv(csvfile)

        # Validate required columns
        required_columns = {"file", "columns_needed", "columns_sup"}
        missing_columns = required_columns - set(orga.columns)
        if missing_columns:
            raise KeyError(
                f"Missing required columns in organisation file: {sorted(missing_columns)}"
            )

        # Convert columns_needed from comma-separated strings to lists
        orga["columns_needed"] = orga["columns_needed"].apply(lambda x: x.split(","))

        # Convert columns_sup to boolean (if it's not already)
        orga["columns_sup"] = orga["columns_sup"].astype(bool)

        # Convert DataFrame to dictionary
        orga_dict = orga.set_index("file").to_dict(orient="index")

        return orga_dict

def validate_files_presence(files_needed: set, files_available: set, path: str):
    """Check if required files exist in the dataset."""
    missing_files = files_needed - files_available
    extra_files = files_available - files_needed

    if missing_files:
        raise KeyError(f"Missing files {sorted(missing_files)} in my_organisation file {path}")

    if extra_files:
        logging.warning("Extra files %s present in %s and not needed", extra_files, path)

def validate_columns(df: pd.DataFrame, path: str, cols_need: list, cols_sup = False):
    """Check for missing and extra columns in each file."""
    missing = cols_need - set(df.columns)
    extra = set(df.columns) - cols_need

    if missing:
        raise KeyError(f"Missing columns {missing} in {path}")

    if not cols_sup and extra:
        logging.warning("Extra columns %s in %s and won't be used", extra, path)

def validate_columns_orga(orga_dict: dict, db_dict: dict):
    """Check for missing and extra columns in each file based on organisation specifications."""
    for file, df in db_dict.items():
        validate_columns(
            df, path=file, cols_need=set(orga_dict[file]["columns_needed"]),
            cols_sup=orga_dict[file]["columns_sup"]
        )

def get_db_from_excel(path: str, orga_dict: dict) -> dict:
    """Load and validate an Excel file based on organisation specifications."""
    path_file = get_file_path(path)

    try:
        wb = load_workbook(path_file, read_only=True)
    except FileNotFoundError as error:
        logging.error("File %s not found", path)
        raise error

    validate_files_presence(set(orga_dict.keys()), set(wb.sheetnames), path)

    db_dict = {sheet: pd.read_excel(path_file, sheet_name=sheet) for sheet in orga_dict}

    validate_columns_orga(orga_dict, db_dict)

    return db_dict

def get_db_from_csv(path: str, orga_dict: dict) -> dict:
    """Load and validate a CSV file based on organisation specifications."""
    path_file = get_file_path(path)
    all_db_files = pd.read_csv(path_file)

    if set(all_db_files.columns) != {"file", "path", "sep"}:
        raise KeyError(f"Columns in {path} should only contain ['file', 'path', 'sep']")

    validate_files_presence(set(orga_dict.keys()), set(all_db_files['file']), path)

    db_dict = {}
    all_db_files.set_index("file", inplace=True)
    for file, file_path, sep in all_db_files.itertuples():
        db_path_file = get_file_path(file_path)
        db_dict[file] = read_file(db_path_file, sep = sep)

    validate_columns_orga(orga_dict, db_dict)

    return db_dict
