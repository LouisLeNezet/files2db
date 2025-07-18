#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 09/12/2022
@author: LouisLeNezet
Modules for all converting functions
"""

import re
import pandas as pd
import numpy as np
from typing import Optional
from files2db.data_process.null_values import not_null
from files2db.data_mg.utils import check_pd_series


short_date_f = re.compile(r"\d{1,2}\.\d\d\.\d\d")
long_date_f = re.compile(r"\d\d\.\d\d\.\d\d\d\d")
long_date_f_inv = re.compile(r"\d\d\d\d\.\d\d\.\d\d")
long_date_f_time = re.compile(r"\d\d\d\d-\d\d-\d\d00:00:00")


def date_convert(
    date_to_convert: str,
    na_values: list = ["", None, "NaN", "nan", "<na>"],
    fillna_value: str = None,
) -> str:
    """
    Convert a string representing a date into a unique format.

    Parameters
    ----------
    date_to_convert : String
        String to convert to right format dd.mm.yyyy.

    Returns
    -------
    str
        Date in the right format.

    """
    if pd.isna(date_to_convert) or date_to_convert in na_values:
        return fillna_value

    if not isinstance(date_to_convert, str):
        raise TypeError("date_to_convert should be a string")

    global \
        super_short_date_f, \
        short_date_f, \
        long_date_f, \
        long_date_f_inv, \
        long_date_f_time

    date_to_convert = date_to_convert.replace("/", ".")
    if date_to_convert == "00:00:00" or date_to_convert == "0000-00-00":
        new_date = fillna_value
    else:
        if short_date_f.fullmatch(date_to_convert):
            raise TypeError(
                "Format is not reliable please modify it to full year format"
            )
            # if date_to_convert[-2:] > "80":  # Siecle dernier
            #    new_date = str(date_to_convert[0:6] + "19" + date_to_convert[-2:])
            # else:
            #    new_date = str(date_to_convert[0:6] + "20" + date_to_convert[-2:])
        elif long_date_f_time.fullmatch(date_to_convert):
            new_date = str(
                date_to_convert[8:10]
                + "."
                + date_to_convert[5:7]
                + "."
                + date_to_convert[0:4]
            )
        elif long_date_f.fullmatch(date_to_convert):
            new_date = str(date_to_convert)
        elif long_date_f_inv.fullmatch(date_to_convert):
            new_date = str(
                date_to_convert[8:10]
                + "."
                + date_to_convert[5:7]
                + "."
                + date_to_convert[0:4]
            )
        else:
            raise TypeError(f"Format not recognised {date_to_convert}")

    if not_null(new_date):
        return new_date
    else:
        return fillna_value


def check_numeric(value):
    """Check if value is numeric.

    Args:
        x (_type_): Value to check

    Raises:
        ValueError: If value is not numeric. return false
        TypeError: Value need to be a string. return false
    Returns:
        bool: Is value numeric  and not NaN.
    """
    try:
        return not np.isnan(float(value))
    except ValueError:
        return False
    except TypeError:
        return False


def num_convert(
    data_se: pd.Series,
    to_type: Optional[str] = "float",
    fillna_value: Optional[str] = None,
) -> pd.Series:
    """
    Convert string pandas Series to numeric while checking for errors and setting the type.

    Parameters
    ----------
    data : Series
        Series to convert (will be first convert to str).
    to_type : 'int', 'float'
        Data type to convert to.

    Raises
    ------
    Exception
        General exception.

    Returns
    -------
    data_conv : Series
        Series converted back, value who couldn't be converted to numeric are replaced by NaN.
    error_conv : List
        List of the errors obtained.

    """
    if not check_pd_series(data_se, type_check=(str, int, float)):
        return data_se

    data = data_se.astype(str).str.replace(",", ".")
    num_conv = data.apply(check_numeric)

    data_conv = pd.Series()
    if to_type == "int":
        data_conv = pd.Series(
            [
                int(round(float(x), 0)) if num else fillna_value
                for x, num in zip(data, num_conv)
            ]
        )
    if to_type == "float":
        data_conv = pd.Series(
            [float(x) if num else fillna_value for x, num in zip(data, num_conv)]
        )

    # Preserve the original name of the Series
    data_conv.name = data_se.name

    return data_conv


def data_conv(
    data_se: pd.Series,
    data_type: Optional[str] = None,
    fillna_value: Optional[str] = None,
) -> pd.Series:
    if not check_pd_series(data_se, type_check=str):
        return data_se

    if data_type is not None:
        if data_type == "lower":
            data_se = data_se.str.lower()
        elif data_type == "UPPER":
            data_se = data_se.str.upper()
        elif data_type == "Title":
            data_se = data_se.str.title()
        elif data_type == "date":
            data_se = data_se.str.replace("-", ".", regex=False)
            data_se = data_se.apply(
                lambda row: date_convert(row, fillna_value=fillna_value)
            )
        elif data_type in ["int", "float"]:
            data_se = num_convert(data_se, to_type=data_type, fillna_value=fillna_value)
        elif data_type == "string":
            # Convert to string, preserving NaN values
            data_se = pd.Series(
                [str(x) if pd.notna(x) else fillna_value for x in data_se],
                index=data_se.index,
                name=data_se.name,
            )
        elif data_type == "bool":
            data_se = data_se.str.lower().replace({"true": True, "false": False})
            data_se = data_se.astype(bool)
        else:
            raise ValueError(f"Unknown case type: {data_type}")

    return data_se
