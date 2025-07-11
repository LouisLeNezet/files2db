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

from .read_file.data_read import read_file
from .data_mg.normdata_old import norm_data
from .read_file.orga_read import get_db_from_path, load_file_orga
from .ui.get_infos import get_file_path, get_os, welcome
from .data_process.null_values import not_null

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def start():
    """Get the current directory and operating system.
    Print a welcoming message
    """
    op_sys, path_wd = get_os()
    welcome("concatenate files", path_wd, op_sys)
    return (op_sys, path_wd)


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


def iterate_file(file):
    """Iterate through all files in the database

    All the files are read and concatenated into a single dataframe.
    Each file is expected to have a 'FileName' and 'Folder' column
    which are used to construct the full file path.
    The metadata columns (starting with 'meta_') are also added to the dataframe.
    If a metadata column is not present in the file data, it is added with the value from the file info.

    Args:
        file (pd.DataFrame): Pandas dataframe containing the files to parse

    Returns:
        pd.DataFrame: Dataframe containing all the data from the files

    Raises:
        FileNotFoundError: If a file cannot be found or accessed
    """

    all_data = pd.DataFrame()
    metadata_columns = [
        col for col in file.columns if isinstance(col, str) and col.startswith("meta_")
    ]

    if file.empty:
        logging.warning(
            "No files to process. The input dataframe is empty. Check ToAdd column in the database."
        )
        return all_data

    for index in file.index:
        file_infos = file.loc[index].copy()
        file_name = file_infos["FileName"]
        file_path = get_file_path(file_infos["FilePath"])

        print("--------------------------------------------------")
        print(file_name)

        # Read  file
        try:
            file_data = read_file(
                file_to_add_path=file_path,
                header=file_infos.get("Header"),
                line_start=file_infos.get("LineStart"),
                line_end=file_infos.get("LineEnd"),
                col_start=file_infos.get("ColStart"),
                col_end=file_infos.get("ColEnd"),
                sheet_name=file_infos.get("SheetName"),
                encoding=file_infos.get("Encoding", "utf8"),
                sep=file_infos.get("Sep", "\t"),
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {file_path}") from e
        except Exception as e:
            raise e

        # Add meta data to file
        file_data["File"] = file_infos["FileName"]

        for col in metadata_columns:
            col_name = col.replace("meta_", "")
            if col_name not in file_data.columns:
                file_data[col_name] = file_infos[col]
            else:
                # If the column is already present, we can just skip it
                pass

        # Add file to merged data_frame
        all_data = pd.concat([all_data, file_data])

    return all_data


app = typer.Typer()


@app.command()
def main(
    path: str = typer.Argument(..., help="Path to the main file to use."),
    normalize: bool = typer.Option(
        False, "--normalize", "-n", help="Normalize the data after concatenation."
    ),
    output_folder: str = typer.Option(
        "./DataGenerated",
        "--output",
        "-o",
        help="Output directory for the generated files.",
    ),
    output_files_prefix: str = typer.Option(
        "AllID", "--prefix", "-p", help="Prefix for the output files."
    ),
):
    """Main function of the concatenation script."""

    start()
    db_orga = load_file_orga()
    db_get = get_db_from_path(path, db_orga)

    if db_get is None:
        logging.error("No database found. Please check the file path and format.")
        return

    logging.info("Database loaded successfully")

    try:
        check_files_exist(db_get["Files"]["FilePath"])
    except FileNotFoundError:
        logging.error(
            "One or more files could not be found. Please check the file paths."
        )
        return

    try:
        all_data_raw = iterate_file(db_get["Files"].loc[db_get["Files"]["ToAdd"] == 1])
    except Exception as e:
        logging.error("An error occurred while iterating through the files: %s", e)
        return

    # Check if output folder exists, if not create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        logging.info("Output folder created: %s", output_folder)

    # Save RAW as csv
    save_path = os.path.join(
        f"{output_folder}/{output_files_prefix}_{date.today()}_raw.csv"
    )
    all_data_raw.to_csv(get_file_path(save_path), sep=";")

    # Normalize data
    if normalize:
        logging.info("Normalizing data...")
        all_data_raw = all_data_raw.dropna(how="all", axis="index")
        all_data, all_errors = norm_data(all_data_raw)

        # Save normalized data
        save_path = os.path.join(
            f"{output_folder}/{output_files_prefix}_{date.today()}.csv"
        )
        all_data.to_csv(get_file_path(save_path), sep=";")
        logging.info("Data saved to %s", save_path)

        # Save errors
        if len(all_errors) > 0:
            save_path = os.path.join(
                f"{output_folder}/{output_files_prefix}_{date.today()}_errors.csv"
            )
            all_errors.to_csv(get_file_path(save_path), sep=";")
            logging.info("Errors saved to %s", save_path)
        else:
            logging.info("No errors found in the data")

    logging.info("Concatenation completed successfully")


if __name__ == "__main__":
    app()
