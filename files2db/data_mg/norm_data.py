# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 12:28:13 2021

@author: LouisLeNezet
"""

import re
import logging
import pandas as pd
import numpy as np
import unicodedata

from typing import Optional, Any
from files2db.data_mg.string_management import data_sep, data_clean, data_conv, data_replace, data_sep_pattern

pd.set_option("display.max_columns", None)

def initial_clean_na_values_utf8(
    data_df: pd.DataFrame,
    na_values: Optional[Any] = [None, "", " ", "NaN", "nan", "N/A", "n/a", "NA", "na"],
    fillna_value: Optional[Any] = None,
    normalize_text: bool = True
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
    fill_value : Any, optional
        Value to fill missing entries with. Default is None (no fill).
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
        df.replace(na_values, np.nan, inplace=True)

    # Drop completely empty rows/columns
    df.dropna(how="all", axis=0, inplace=True)
    df.dropna(how="all", axis=1, inplace=True)

    # Fill missing values
    if fillna_value is not None:
        df.fillna(fillna_value, inplace=True)

    # Normalize text in string columns
    if normalize_text:
        for col in df.select_dtypes(include=["object", "string"]):
            df[col] = (
                df[col]
                .astype(str)
                .apply(lambda x: 
                    unicodedata.normalize("NFKD", x)
                        .encode("ascii", "ignore")
                        .decode("utf-8")
                        .lower()
                )
            )

    return df

def normalize_column(data_se: pd.Series, field_info, field_equiv):
    return (
        data_sep(data_se, field_info["sep"])
        .pipe(lambda df: df.apply(data_clean, **params))
        .pipe(lambda df: df.apply(data_conv, args=(field_info["data_type"],)))
        .pipe(lambda df: df.apply(data_replace, args=(field_equiv,)))
        #.pipe(lambda df: data_validate(df, field_info["contains"], field_info["min"], field_info["max"]))
        .pipe(lambda df: data_sep_pattern(df, field_info["sep_pattern"], field_info["keep_link"]))
    )

def norm_data(
    data_df: pd.DataFrame,
    db_orga: dict[pd.DataFrame],
    fillna_value = None
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

    data_df_cleaned_init = initial_clean_na_values_utf8(data_df, fillna_value=fillna_value)
    
    normed_df = pd.DataFrame()
    errors_df = pd.DataFrame()
    
    if "Field" not in db_orga["FieldRules"].columns:
        logging.error("No fields defined in the FieldRules. Please check the database organization.")
        return normed_df, errors_df

    for field in db_orga["FieldRules"]["Field"]:
        logging.info("Normalizing field: %s", field)
        match_cols = [col for col in data_df_cleaned_init.columns if re.fullmatch(field, col)]
        if not match_cols:
            logging.info("Field %s not found in the file", field)
            continue
        field_infos = db_orga["FieldRules"].set_index("Field").loc[field].to_dict()
        field_equiv = db_orga["ValuesMap"][db_orga["ValuesMap"]["Field"] == field].to_dict(orient="records")
        field_equiv = {d["Value"]: d["Eq"].split(",") for d in field_equiv }
        print(field_equiv)

        for col_i in match_cols:
            logging.info("Processing column: %s", col_i)
            data_df_sep = data_sep(
                data_df_cleaned_init.loc[:, col_i],
                field_infos["Sep"]
            )
            for col_ii in data_df_sep :
                data_se_cleaned = data_clean(
                    data_df_sep.loc[:, col_ii],
                    del_match = field_infos["DelMatch"],
                    del_in = field_infos["DelIn"],
                    del_start = field_infos["DelStart"],
                    del_end = field_infos["DelEnd"],
                    strip_from = field_infos["StripFrom"],
                )
                data_se_converted = data_conv(data_se_cleaned, field_infos["DataType"])
                data_se_replaced = data_replace(data_se_converted, field_equiv)
                
                if False:
                    data_se_validate, errors = data_validate(
                        data_se_replaced, field_infos.contains,
                        field_infos.data_min, field_infos.data_max
                    )
                else:
                    data_se_validate = data_se_replaced
                    errors = pd.Series([None] * len(data_se_validate))
                data_df_separated = data_sep_pattern(
                    data_se_validate,
                    field_infos["SepPattern"],
                    field_infos["KeepLink"]
                )
                normed_df = pd.concat((normed_df, data_df_separated))
                errors_df = pd.concat((errors_df, errors))

    return normed_df, errors_df
