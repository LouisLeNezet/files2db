#!/usr/bin/env python3
"""
Created on 18/11/2022
@author: LouisLeNezet
Modules for all tools needed to test presence / absence of null values
"""

from collections import abc as class_name
from typing import Any

import numpy as np
import pandas as pd

ALL_ARRAY_TYPES = (set, tuple, list, dict, pd.Series, np.ndarray)


def _is_not_null_float(value):
    return bool(not np.isnan(value) and value != 0)


def _is_not_null_series(value):
    return len(value.index) != 0


def _is_not_null_iterable(value):
    return len(value) != 0


def _is_not_null_str(value, str_size, alter):
    if str_size:
        return len(value) != 0
    if alter:
        value = str(value).upper().replace(" ", "")
    return value not in ("", "NAN", "NONE", "NULL", "NA")


def _is_not_null_int(value):
    return bool(value != 0 and value == value)


def _is_not_null_keysview(value):
    return value != {}.keys()


def _is_not_null_pandas_null(value):
    return bool(not pd.isnull(value))


def _is_not_null_timestamp(value):
    return bool(value != pd.Timestamp(0))


def not_null(value, str_size=False, alter=True):
    """
    Test if value passed is null.

    Parameters
    ----------
    value : Multiple
        Value to test.
    str_size : Boolean
        If true, then only the size of the string will be tested

    Returns
    -------
    Bool
        Result if null or not.

    """
    type_handlers = [
        ((np.floating, float), _is_not_null_float),
        ((pd.Series,), _is_not_null_series),
        ((set, list, np.ndarray, dict, tuple), _is_not_null_iterable),
        ((str,), lambda v: _is_not_null_str(v, str_size, alter)),
        ((bool,), lambda v: True),
        ((int, np.integer), _is_not_null_int),
        ((class_name.KeysView,), _is_not_null_keysview),
        ((type(pd.NaT), type(pd.NA)), _is_not_null_pandas_null),
        ((type(pd.Timestamp("2022")),), _is_not_null_timestamp),
    ]

    if value is None:
        return False

    for types, handler in type_handlers:
        if isinstance(value, types):
            return handler(value)

    raise ValueError("Value passed not recognized")


def array_not_null(values, recursive=False, alter=True):
    """
    Test for null values inside array.

    Parameters
    ----------
    values : Iterable
        Array of value to test for null.
    recursive : Boolean
        Should the array be searched recursively

    Raises
    ------
    Exception
        Type error if values given not an iterable.

    Returns
    -------
    Array
        Array of boolean corresponding for not_null test on each value.

    """
    if not not_null(values, alter=alter):
        return False

    # Helper to get elements depending on type
    def get_elements(v):
        if isinstance(v, list | pd.Series | pd.DataFrame | set | tuple):
            return v
        if isinstance(v, dict):
            return v.values()
        return None

    if recursive:
        elements = get_elements(values)
        if elements is None:
            return True  # non-iterable value found, consider as True
        return [array_not_null(elem, recursive=True, alter=alter) for elem in elements]
    else:
        elements = get_elements(values)
        if elements is None:
            return True  # non-iterable value found, consider as True
        return [not_null(elem, alter=alter) for elem in elements]


def is_null(value, alter=True):
    """
    Test if value passed is null.

    Parameters
    ----------
    value : Multiple
        Value to test.

    Returns
    -------
    Bool
        Result if null or not.

    """
    return bool_invert(not_null(value, alter=alter))


def bool_invert(values, alter=True):
    """
    Invert boolean list or single value.

    None type value give false.

    Parameters
    ----------
    values : Bool
        Values to invert. Need to be boolean.

    Returns
    -------
    Bool
        Reverse boolean of the values.

    """
    if isinstance(values, pd.Series | list):
        new_list = []
        for value in values:
            if not_null(value, alter=alter):
                new_list.append(bool_invert(value))
            else:
                new_list.append(False)
        return new_list

    if isinstance(values, bool):
        return not values

    raise ValueError("Not a boolean")


def modify(value: Any, alter: bool = True) -> Any:
    """
    Modify value given if asked and change all null value to None.
    """
    if alter:
        if isinstance(value, str):
            value = value.replace(" ", "").upper()
    if is_null(value, alter=alter):
        return None
    return value


def cleaned_item(v: Any, all_array_types: tuple[type, ...], alter: bool = True) -> Any:
    if isinstance(v, all_array_types):
        return get_not_null(v, alter=alter)
    else:
        return modify(v, alter)


def keep_item(val, all_array_types):
    if val is None:
        return False
    if isinstance(val, all_array_types):
        return len(val) != 0
    return True


def _clean_pd_series(series: pd.Series, all_array_types, alter=True) -> pd.Series:
    """
    Handle pd.Series type, cleaning each item.
    """
    cleaned_series = pd.Series(dtype=object)
    for k, v in series.items():
        if not_null(v, alter=alter):
            cleaned_val = cleaned_item(v, all_array_types, alter=alter)
            if keep_item(cleaned_val, all_array_types):
                cleaned_series[k] = cleaned_val
    return cleaned_series


def _clean_dict(value: dict, all_array_types, alter=True) -> dict:
    """
    Handle dict type, cleaning each item.
    """
    cleaned_dict = {}
    for k, v in value.items():
        if not_null(v, alter=alter):
            cleaned_val = cleaned_item(v, all_array_types, alter=alter)
            if keep_item(cleaned_val, all_array_types):
                cleaned_dict[k] = cleaned_val
    return cleaned_dict


def _clean_list(value: list, all_array_types, alter=True) -> list:
    """
    Handle list type, cleaning each item.
    """
    cleaned_list = []

    for v in value:
        if not_null(v, alter=alter):
            cleaned_val = cleaned_item(v, all_array_types, alter=alter)
            if keep_item(cleaned_val, all_array_types):
                cleaned_list.append(cleaned_val)
    return cleaned_list


def _clean_set(value: set, all_array_types, alter=True) -> set:
    """
    Handle set type, cleaning each item.
    """
    cleaned_set = set()

    for v in value:
        if not_null(v, alter=alter):
            cleaned_val = cleaned_item(v, all_array_types, alter=alter)
            if keep_item(cleaned_val, all_array_types):
                cleaned_set.add(cleaned_val)
    return cleaned_set


def _clean_tuple(value: tuple, all_array_types, alter=True) -> tuple:
    """
    Handle tuple type, cleaning each item.
    """
    cleaned_items = []
    for v in value:
        if not_null(v, alter=alter):
            cleaned_val = cleaned_item(v, all_array_types, alter=alter)
            if keep_item(cleaned_val, all_array_types):
                cleaned_items.append(cleaned_val)
    return tuple(cleaned_items)


def handle_iterable(value, alter=True):
    if not isinstance(value, ALL_ARRAY_TYPES):
        raise TypeError(f"Unsupported iterable type: {type(value)}")

    if isinstance(value, pd.Series):
        return _clean_pd_series(value, ALL_ARRAY_TYPES, alter=alter)

    if isinstance(value, dict):
        return _clean_dict(value, ALL_ARRAY_TYPES, alter=alter)

    if isinstance(value, list | np.ndarray):
        return _clean_list(value, ALL_ARRAY_TYPES, alter=alter)

    if isinstance(value, tuple):
        return _clean_tuple(value, ALL_ARRAY_TYPES, alter=alter)

    if isinstance(value, set):
        return _clean_set(value, ALL_ARRAY_TYPES, alter=alter)

    raise TypeError("Iterable type not handled")


def get_not_null(values, alter=True):
    """
    Simplify nested list/dictionary by deleting null values with its respective structure.
    """
    if not not_null(values, alter=alter):
        return None

    if isinstance(values, ALL_ARRAY_TYPES):
        return handle_iterable(values, alter=alter)

    if hasattr(values, "__iter__") and not isinstance(values, str):
        raise TypeError("Values is iterable but not recognized")

    return modify(values, alter)
