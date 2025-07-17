#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 22/10/2021
@author: LouisLeNezet
Main script fo the concatenation of the files
"""

import os
import warnings
import logging
from datetime import date
import pandas as pd
import typer

from .data_mg.norm_data import norm_data
from .data_mg.data_iterate import iterate_file
from .read_file.orga_read import get_db_from_path, load_file_orga
from .read_file.data_read import check_files_exist
from .ui.get_infos import get_file_path, get_os, welcome

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
pd.set_option('future.no_silent_downcasting', True)

def start():
    """Get the current directory and operating system.
    Print a welcoming message
    """
    op_sys, path_wd = get_os()
    welcome("concatenate files", path_wd, op_sys)
    return (op_sys, path_wd)


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

    logging.debug(all_data_raw.head())
    logging.info("All data concatenated successfully")

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
        all_data = norm_data(all_data_raw, db_get)

        # Save normalized data
        save_path = os.path.join(
            f"{output_folder}/{output_files_prefix}_{date.today()}.csv"
        )
        all_data.to_csv(get_file_path(save_path), sep=";")
        logging.info("Data saved to %s", save_path)

    logging.info("Concatenation completed successfully")
    
    return all_data_raw, all_data if normalize else None


if __name__ == "__main__":
    app()
