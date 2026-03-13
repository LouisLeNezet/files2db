#!/usr/bin/env python3

# files2db - A tool to normalize and combine flat files into a database
# Copyright (C) 2024 Louis Le Nezet
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Created on 22/10/2021
@author: LouisLeNezet
Main script fo the concatenation of the files
"""

import logging
import os
import warnings
from datetime import date

import pandas as pd

from .data_mg.data_iterate import iterate_file
from .data_mg.data_norm import norm_data
from .read_file.data_read import check_files_exist
from .read_file.orga_read import get_db_from_path, load_file_orga
from .ui.get_infos import get_file_path, get_os, welcome

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
pd.set_option("future.no_silent_downcasting", True)
pd.set_option("display.max_columns", None)


def start():
    """Get the current directory and operating system.
    Print a welcoming message
    """
    op_sys, path_wd = get_os()
    welcome("concatenate files", path_wd, op_sys)
    return (op_sys, path_wd)


def main(
    path: str,
    normalize: bool,
    output_folder: str,
    output_files_prefix: str,
):
    """Main function of the concatenation script."""

    start()
    db_orga = load_file_orga()
    db_get = get_db_from_path(path, db_orga)

    if db_get is None:
        logging.error("No database found. Please check the file path and format.")
        return None, None

    logging.info("Database loaded successfully")

    try:
        check_files_exist(db_get["Files"]["FilePath"])
    except FileNotFoundError:
        logging.error("One or more files could not be found. Please check the file paths.")
        return None, None

    try:
        all_data_raw = iterate_file(db_get["Files"].loc[db_get["Files"]["ToAdd"]])
    except Exception as e:
        logging.error("An error occurred while iterating through the files: %s", e)
        return None, None

    logging.debug(all_data_raw.head())
    logging.info("All data concatenated successfully")

    # Check if output folder exists, if not create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logging.info("Output folder created: %s", output_folder)

    # Save RAW as csv
    save_path = os.path.join(f"{output_folder}/{output_files_prefix}_{date.today()}_raw.csv")
    all_data_raw.to_csv(get_file_path(save_path), sep=";")

    # Normalize data
    if normalize:
        logging.info("Normalizing data...")
        all_data = norm_data(
            data_df=all_data_raw,
            db_field_rules=db_get["FieldRules"],
            db_values_map=db_get["ValuesMap"],
            na_values=None,
            fillna_value=pd.NA
        )

        # Save normalized data
        save_path = os.path.join(f"{output_folder}/{output_files_prefix}_{date.today()}.csv")
        all_data.to_csv(get_file_path(save_path), sep=";")
        logging.info("Data saved to %s", save_path)

    logging.info("Concatenation completed successfully")

    return all_data_raw, all_data if normalize else None
