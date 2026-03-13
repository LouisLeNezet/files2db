"""
Created on Tue Jul  6 12:28:13 2021

@author: LouisLeNezet
"""

import logging
import re
import unicodedata
from typing import Any

import pandas as pd

from files2db.data_mg.data_convert import data_conv
from files2db.data_mg.data_validate import data_validate
from files2db.data_mg.string_management import (
    data_clean,
    data_replace,
    data_sep,
    data_sep_pattern,
)
from files2db.data_mg.utils import update_only_missing


def initial_clean_na_values_utf8(
    data_df: pd.DataFrame,
    na_values: list[Any] | None = None,
    normalize_text: bool = True,
) -> pd.DataFrame:
    """
    Cleans a DataFrame by removing empty rows/columns, filling NA values,
    and optionally normalizing text (lowercasing, accent removal).

    Parameters
    ----------
    data_df : pd.DataFrame
        The input DataFrame to clean.
    na_values : list of Any, optional
        Values to consider as NA/empty. Default includes common empty values.
    normalize_text : bool, optional
        Whether to lowercase and strip accents from string columns. Default is True.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame.
    """
    df = data_df.copy()

    # Set na_values
    if na_values is not None:
        df.replace(na_values, pd.NA, inplace=True)

    # Drop completely empty rows/columns
    df.dropna(how="all", axis=0, inplace=True)
    df.dropna(how="all", axis=1, inplace=True)

    # Normalize text in string columns
    if normalize_text:
        for col in df.select_dtypes(include=["object", "string"]):
            df[col] = df[col].apply(
                lambda x: (
                    x
                    if pd.isna(x)
                    else unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode("utf-8")
                )
            )

    return df


def norm_data(
    data_df: pd.DataFrame,
    db_field_rules: pd.DataFrame,
    db_values_map: pd.DataFrame,
    na_values: list[Any] | None = None,
    fillna_value=pd.NA,
):
    """
    Normalize dataframe based on informations read in excel file.

    Parameters
    ----------
    file : Dataframe
        Data to normalize.
    db_orga : data organisation and transformation by categories and types

    Returns
    -------
    file_normalized : Dataframe
        Data normalized.

    """
    logging.info("Starting normalization of the datas")

    if na_values is None:
        na_values = ["", None, "NaN", "nan", "<na>", "None", {}]

    normed_df = initial_clean_na_values_utf8(data_df)

    errors_df = pd.DataFrame()

    if "Field" not in db_field_rules.columns:
        logging.error(
            "No fields defined in the FieldRules. Please check the database organization."
        )
        return normed_df, errors_df

    for field_i in db_field_rules.index:
        field = db_field_rules.loc[field_i, "Field"]
        match_cols = [col for col in normed_df.columns if re.fullmatch(field, col)]
        if not match_cols:
            logging.info("Field %s not found in the file", field)
            continue
        field_infos = db_field_rules.loc[field_i].to_dict()
        field_equiv = db_values_map[db_values_map["Field"] == field].to_dict(
            orient="records"
        )
        field_equiv = {d["Value"]: d["Eq"] for d in field_equiv}

        for col_i in match_cols:
            logging.info("Processing column: %s", col_i)
            data_df_sep = data_sep(
                normed_df.loc[:, col_i],
                field_infos["Sep"],
            )

            normed_df.drop(columns=col_i, inplace=True, errors="ignore")

            for col_ii in data_df_sep:
                logging.info("Normalising column: %s", col_ii)
                data_se_cleaned = data_clean(
                    data_df_sep.loc[:, col_ii],
                    del_match=field_infos["DelMatch"],
                    del_in=field_infos["DelIn"],
                    del_start=field_infos["DelStart"],
                    del_end=field_infos["DelEnd"],
                    strip_from=field_infos["StripFrom"],
                )

                data_se_converted = data_conv(
                    data_se_cleaned, field_infos["DataType"]
                )

                data_se_replaced = data_replace(data_se_converted, field_equiv)

                errors = data_validate(
                    data_se = data_se_replaced,
                    contains = field_infos["Contains"],
                    min_value = field_infos["Min"],
                    max_value = field_infos["Max"],
                )

                logging.info("Separating column: %s by pattern", col_ii)
                data_df_separated = data_sep_pattern(
                    data_se = data_se_replaced,
                    pattern = field_infos["SepPattern"],
                    keep_link = field_infos["KeepLink"],
                )

                normed_df = update_only_missing(normed_df, data_df_separated)

                errors_df = pd.concat((errors_df, errors), axis=1)

    # Concatenate all error messages into a single column
    if not errors_df.empty and len(errors_df.columns) > 0:
        normed_df["Error"] = errors_df.apply(
            lambda row: pd.Series(
                {"Error": {col: val for col, val in row.items() if isinstance(val, dict)}}
            ),
            axis=1,
        )
    else:
        normed_df["Error"] = pd.NA
    normed_df.replace(na_values, fillna_value, inplace=True)
    normed_df.fillna(fillna_value, inplace=True)

    return normed_df
