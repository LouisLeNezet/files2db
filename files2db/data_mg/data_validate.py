import re
import pandas as pd
import numpy as np

from files2db.data_process.null_values import not_null, get_not_null
from files2db.data_mg.utils import check_pd_series

from typing import Optional, Any

long_date_f = re.compile(r"\d\d\.\d\d\.\d\d\d\d")

def data_contains(
    data_se: pd.Series,
    contains: Optional[str] = None
) -> pd.Series:
    """
    Check if the data contains specific patterns.
    
    Parameters:
    - data_se: pd.Series - The data to check.
    - contains: str - The pattern to check for.
    
    Returns:
    - pd.Series: A series with boolean values indicating if the pattern is found.
    """
    if not check_pd_series(data_se, type_check=(str, int, float)):
        return data_se

    if pd.isna(contains) or contains is None :
        return pd.Series([True] * len(data_se))
    if not isinstance(contains, str):
        raise TypeError("contains should be a string")

    if contains == "LETTERS":
        return data_se.str.fullmatch("[A-Z]+", case=True, na=False)
    elif contains == "letters":
        return data_se.str.fullmatch("[a-z]+", case=True, na=False)
    elif contains == "Letters":
        return data_se.str.fullmatch(r"[A-Za-z]*", case=True, na=False)
    elif contains == "ALPHANUM":
        return data_se.str.fullmatch(r"[A-Z0-9]*", case=True, na=False)
    elif contains == "alphanum":
        return data_se.str.fullmatch(r"[a-z0-9]*", case=True, na=False)
    elif contains == "Alphanum":
        return data_se.str.fullmatch(r"[A-Za-z0-9]*", case=True, na=False)
    elif contains == "date":
        return data_se.str.fullmatch(long_date_f, case=True, na=False)
    elif contains == "int":
        return pd.Series([isinstance(x, int) for x in data_se], index=data_se.index)
    elif contains == "float":
        return pd.Series([isinstance(x, float) for x in data_se], index=data_se.index)
    else:
        return data_se.str.fullmatch(contains.replace(",", "|"), case=True, na=False)


def data_validate(
    data_se: pd.Series,
    contains: Optional[str] = None,
    min_value: Optional[Any] = None,
    max_value: Optional[Any] = None,
    fillna_value: Optional[Any] = None
) -> pd.Series:
    err_content = err_min = err_max = [pd.NA for x in data_se]
    print(data_se)
    err_content = data_contains(data_se, contains) 

    err_content = [
        "not " + contains
        if (not err and not_null(val))
        else fillna_value
        for err, val in zip(err_content, data_se)
    ]
    print(data_se)

    if min_value is not None:
        if not isinstance(min_value, (int, float)):
            raise TypeError("min_value should be an int or float")
        err_min = [
            "InfToMin" if isinstance(x, (int, float)) and (not_null(x) and x < min_value)
            else fillna_value
            for x in data_se
        ]

    if max_value is not None:
        if not isinstance(max_value, (int, float)):
            raise TypeError("max_value should be an int or float")
        err_max = [
            "SupToMax" if isinstance(x, (int, float)) and (not_null(x) and x > max_value)
            else fillna_value
            for x in data_se
        ]

    err = [
        get_not_null([e_cont, e_min, e_max], alter = False)
        for e_cont, e_min, e_max in zip(err_content, err_min, err_max)
    ]

    errors = pd.Series([
        {data_se.name: {"Value": data_se.loc[ind], "Error": err}}
        if not_null(err)
        else pd.NA
        for ind, err in zip(data_se.index, err)
    ], index=data_se.index, name=data_se.name)

    return errors