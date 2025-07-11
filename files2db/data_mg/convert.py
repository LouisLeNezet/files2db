#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 09/12/2022
@author: LouisLeNezet
Modules for all converting functions
"""

import re
import logging
import pandas as pd
import numpy as np
from ..ui.print_infos import print_exception
from ..data_process.null_values import not_null


short_date_f = re.compile(r"\d{1,2}\.\d\d\.\d\d")
long_date_f = re.compile(r"\d\d\.\d\d\.\d\d\d\d")
long_date_f_inv = re.compile(r"\d\d\d\d\.\d\d\.\d\d")
long_date_f_time = re.compile(r"\d\d\d\d-\d\d-\d\d00:00:00")


def date_convert(date_to_convert):
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
    try:
        if not_null(date_to_convert):
            global \
                super_short_date_f, \
                short_date_f, \
                long_date_f, \
                long_date_f_inv, \
                long_date_f_time
            date_to_convert = date_to_convert.replace("/", ".")
            if date_to_convert == "00:00:00" or date_to_convert == "0000-00-00":
                new_date = None
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
                return None
        else:
            return None
    except Exception as error:
        logging.info(date_to_convert)
        print_exception()
        raise RuntimeError("Error while converting date") from error


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


def num_convert(data, to_type):
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
    try:
        data = data.astype(str).str.replace(",", ".")
        num_conv = data.apply(check_numeric)
        data_conv = pd.Series()
        if to_type == "int":
            data_conv = pd.Series(
                [round(float(x), 0) if num else None for x, num in zip(data, num_conv)]
            )
        if to_type == "float":
            data_conv = pd.Series(
                [float(x) if num else None for x, num in zip(data, num_conv)]
            )

        error_conv = [
            "Cannot be converted to Numeric" if not num else None for num in num_conv
        ]
        return data_conv, error_conv
    except Exception as error:
        print_exception()
        raise ValueError("Error while converting to numeric") from error
