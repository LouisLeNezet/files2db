import re
from typing import Any

import pandas as pd

from files2db.data_mg.utils import check_pd_series
from files2db.data_process.null_values import get_not_null, not_null

long_date_f = re.compile(r"\d\d\.\d\d\.\d\d\d\d")


def data_contains(data_se: pd.Series, contains: str | None = None) -> pd.Series:
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

    if pd.isna(contains) or contains is None:
        return pd.Series([True] * len(data_se))

    if not isinstance(contains, str):
        raise TypeError("contains should be a string")

    string_patterns = {
        "LETTERS": r"[A-Z]+",
        "letters": r"[a-z]+",
        "Letters": r"[A-Za-z]*",
        "ALPHANUM": r"[A-Z0-9]*",
        "alphanum": r"[a-z0-9]*",
        "Alphanum": r"[A-Za-z0-9]*",
        "date": long_date_f,
    }

    if contains in string_patterns:
        return data_se.str.fullmatch(string_patterns[contains], case=True, na=False)


    if contains == "int":
        return data_se.apply(lambda x: isinstance(x, int))
    if contains == "float":
        return data_se.apply(lambda x: isinstance(x, float))

    # Default: treat contains as a regex pattern or comma-separated alternatives
    return data_se.str.fullmatch(contains.replace(",", "|"), case=True, na=False)


def data_validate(
    data_se: pd.Series,
    contains: str | None = None,
    min_value: Any | None = None,
    max_value: Any | None = None,
    fillna_value: Any | None = None,
) -> pd.Series:
    err_content = err_min = err_max = [pd.NA for x in data_se]
    err_content = data_contains(data_se, contains)

    err_content = [
        "not " + contains if (not err and not_null(val)) else fillna_value
        for err, val in zip(err_content, data_se, strict=False)
    ]

    if min_value is not None:
        if not isinstance(min_value, int | float):
            raise TypeError("min_value should be an int or float")
        err_min = [
            "InfToMin"
            if isinstance(x, int | float) and (not_null(x) and x < min_value)
            else fillna_value
            for x in data_se
        ]

    if max_value is not None:
        if not isinstance(max_value, int | float):
            raise TypeError("max_value should be an int or float")
        err_max = [
            "SupToMax"
            if isinstance(x, int | float) and (not_null(x) and x > max_value)
            else fillna_value
            for x in data_se
        ]

    err = [
        get_not_null([e_cont, e_min, e_max], alter=False)
        for e_cont, e_min, e_max in zip(err_content, err_min, err_max, strict=False)
    ]

    errors = pd.Series(
        [
            {"Value": data_se.loc[ind], "Error": err} if not_null(err) else pd.NA
            for ind, err in zip(data_se.index, err, strict=False)
        ],
        index=data_se.index,
        name=data_se.name,
    )

    return errors
