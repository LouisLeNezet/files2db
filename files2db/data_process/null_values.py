#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 18/11/2022
@author: LouisLeNezet
Modules for all tools needed to test presence / absence of null values
"""

import logging
from collections import abc as class_name
import numpy as np
import pandas as pd
from ..ui.print_infos import print_exception


def modify(value, alter=True):
    """Modify value given if asked and change all null value to None.

    Parameters
    ----------
    value : _type_
        Value to modify
    alter : bool, optional
        Does the value need to be stripped from white space and be put to upper case.
        Defaults to True.

    Returns
    -------
    _type_
        Modified value, if null replaced by None.

    Raises
    ------
    Exception
        If alter isn't a boolean
    """
    try:
        if alter:
            if isinstance(value, str):
                value = value.replace(" ", "").upper()
        if is_null(value, alter=alter):
            return None
        return value
    except ValueError as error:
        print_exception()
        raise ValueError(f"Error while modifying {value}") from error


def all_modify(values, alter=True):
    """Apply modify function to all elements of values

    Parameters
    ----------
    values : _type_
        Iterable element
    alter : bool, optional
        Does the values need to be stripped from white space and be put to upper case.
        Defaults to True.

    Returns
    -------
    _type_
        All elements with same architecture modified

    Raises
    ------
    TypeError
        Iterable value not recognise
    Exception
        _description_
    """
    try:
        all_array_types = (set, tuple, list, dict, pd.Series, np.ndarray)
        all_empty_types = {
            "set": set(),
            "tuple": (),
            "list": [],
            "dict": {},
            "Series": pd.Series([], dtype=object),
            "ndarray": [],
        }
        if alter:
            if not_null(values, alter=alter):
                if values.__class__.__name__ in all_empty_types:
                    dnn = all_empty_types[values.__class__.__name__]
                    if isinstance(values, pd.Series):
                        for key, value in values.items():
                            if isinstance(value, all_array_types):
                                dnn = pd.concat(
                                    [
                                        dnn,
                                        pd.Series(
                                            {key: all_modify(value, alter=alter)}
                                        ),
                                    ]
                                )
                            else:
                                dnn = pd.concat(
                                    [dnn, pd.Series({key: modify(value, alter)})]
                                )
                        return dnn
                    if isinstance(values, dict):
                        for key, value in values.items():
                            if isinstance(value, all_array_types):
                                dnn.update({key: all_modify(value, alter=alter)})
                            else:
                                dnn.update({key: modify(value, alter)})
                        return dnn
                    if isinstance(values, (list, np.ndarray)):
                        for value in values:
                            if isinstance(value, all_array_types):
                                dnn.append(all_modify(value, alter=alter))
                            else:
                                dnn.append(modify(value, alter))
                        return dnn
                    if isinstance(values, (tuple)):
                        for value in values:
                            if isinstance(value, all_array_types):
                                dnn = dnn + ((all_modify(value, alter=alter)),)
                            else:
                                dnn = dnn + (modify(value, alter),)
                        return dnn
                    if isinstance(values, (set)):
                        for value in values:
                            if isinstance(value, all_array_types):
                                dnn.add(all_modify(value, alter=alter))
                            else:
                                dnn.add(modify(value, alter))
                        return dnn

                elif hasattr(values, "__iter__") and not isinstance(values, str):
                    logging.info(values, type(values))
                    logging.info(values.__class__.__name__)
                    raise ValueError("Values is iterable but not recognize")
                else:
                    return modify(values, alter)
            else:
                return None
        else:
            return values
    except ValueError as error:
        print_exception()
        raise ValueError("Error while modifying all values from iterable") from error


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
    try:
        if isinstance(value, (np.floating, float)):
            return bool(not np.isnan(value) and value != 0)

        if isinstance(value, pd.Series):
            return len(value.index) != 0

        if isinstance(value, (set, list, np.ndarray, dict, tuple)):
            return len(value) != 0

        if isinstance(value, str):
            if str_size:
                return len(value) != 0
            if alter:
                value = str(value).upper()
                value = value.replace(" ", "")
            return value not in ("", "NAN", "NONE", "NULL", "NA")

        if value is None:
            return False

        if isinstance(value, bool):
            return True

        if isinstance(value, (int, np.integer)):
            return bool(value != 0 and value == value)

        if isinstance(value, class_name.KeysView):
            return value != {}.keys()

        if isinstance(value, (type(pd.NaT), type(pd.NA))):
            return bool(not pd.isnull(value))

        if isinstance(value, type(pd.Timestamp("2022"))):
            return bool(value != pd.Timestamp(0))

        raise ValueError("Value passed not recognize")

    except ValueError as error:
        logging.info(value, type(value))
        print_exception()
        raise ValueError("Error, while checking for null values") from error


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
    try:
        res = []
        if not_null(values, alter=alter):
            if recursive:
                if isinstance(values, (list, pd.Series, pd.DataFrame, set, tuple)):
                    for value in values:
                        res.append(array_not_null(value, recursive=recursive))
                elif isinstance(values, (dict)):
                    for value in values.values():
                        res.append(array_not_null(value, recursive=recursive))
                else:
                    return True
            else:
                if isinstance(values, (list, pd.Series, pd.DataFrame, set, tuple)):
                    for value in values:
                        res.append(not_null(value, alter=alter))
                elif isinstance(values, (dict)):
                    for value in values.values():
                        res.append(not_null(value, alter=alter))
                else:
                    return True
        else:
            return False
        return res
    except ValueError as error:
        logging.info(values)
        print_exception()
        raise ValueError("Error while checking null values in array") from error


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
    try:
        if isinstance(values, (pd.Series, list)):
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

    except ValueError as error:
        logging.info(values, type(values))
        print_exception()
        raise ValueError("Error, while inverting boolean values") from error


def get_not_null(values, alter=True):
    """
    Simplify nested list/dictionary by deleting null values with its respective structure.

    Parameters
    ----------
    values : dict/list and nested dict/list
        Dictionary or list to treat.
    alter: Boolean
        Does the values need to be stripped from whitespace and put to UPPER case

    Returns
    -------
    dnn : dict or nested dict
        Same dictionary as the one gave without null values.

    """
    try:
        all_array_types = (set, tuple, list, dict, pd.Series, np.ndarray)
        all_empty_types = {
            "set": set(),
            "tuple": (),
            "list": [],
            "dict": {},
            "Series": pd.Series([], dtype=object),
            "ndarray": [],
        }
        if not_null(values, alter=alter):
            if values.__class__.__name__ in all_empty_types:
                dnn = all_empty_types[values.__class__.__name__]
                if isinstance(values, pd.Series):
                    for key, value in values.items():
                        if isinstance(value, all_array_types):
                            if any_nested_list(
                                array_not_null(value, recursive=True, alter=alter), True
                            ):
                                dnn = pd.concat(
                                    [
                                        dnn,
                                        pd.Series(
                                            {key: get_not_null(value, alter=alter)}
                                        ),
                                    ]
                                )
                        else:
                            if not_null(value, alter=alter):
                                dnn = pd.concat(
                                    [dnn, pd.Series({key: modify(value, alter)})]
                                )
                    return dnn
                if isinstance(values, dict):
                    for key, value in values.items():
                        if isinstance(value, all_array_types):
                            if any_nested_list(
                                array_not_null(value, recursive=True, alter=alter), True
                            ):
                                dnn.update({key: get_not_null(value, alter=alter)})
                        else:
                            if not_null(value, alter=alter):
                                dnn.update({key: modify(value, alter)})
                    return dnn
                if isinstance(values, (list, np.ndarray)):
                    for value in values:
                        if isinstance(value, all_array_types):
                            if any_nested_list(
                                array_not_null(value, recursive=True, alter=alter), True
                            ):
                                dnn.append(get_not_null(value, alter=alter))
                        else:
                            if not_null(value, alter=alter):
                                dnn.append(modify(value, alter))
                    return dnn
                if isinstance(values, (tuple)):
                    for value in values:
                        if isinstance(value, all_array_types):
                            if any_nested_list(
                                array_not_null(value, recursive=True, alter=alter), True
                            ):
                                dnn = dnn + ((get_not_null(value, alter=alter)),)
                        else:
                            if not_null(value, alter=alter):
                                dnn = dnn + (modify(value, alter),)
                    return dnn
                if isinstance(values, (set)):
                    for value in values:
                        if isinstance(value, all_array_types):
                            if any_nested_list(
                                array_not_null(value, recursive=True, alter=alter), True
                            ):
                                dnn.add(get_not_null(value, alter=alter))
                        else:
                            if not_null(value, alter=alter):
                                dnn.add(modify(value, alter))
                    return dnn

            elif hasattr(values, "__iter__") and not isinstance(values, str):
                logging.info(values, type(values))
                logging.info(values.__class__.__name__)
                raise TypeError("Values is iterable but not recognize")
            else:
                return modify(values, alter)
        else:
            return None
    except Exception as error:
        print_exception()
        raise ValueError(
            f"Error while filtering null value from iterable {error}"
        ) from error


def any_nested_list(my_list, item):
    """
    Determines if an item is in my_list, even if nested in a lower-level list.

    Work only for list, tuple and set types
    """
    try:
        if isinstance(my_list, bool):
            return my_list == item
        if item in my_list:
            return True
        else:
            return any(
                [
                    any_nested_list(sublist, item)
                    for sublist in my_list
                    if isinstance(sublist, (list, tuple, set))
                ]
            )
    except Exception as error:
        print_exception()
        raise ValueError(
            f"Error while testing for presence of {item} in {my_list}"
        ) from error


def simplify_array(values, alter=True):
    """
    List all unique non null value of an array and simplify to None or unique Item.

    Parameters
    ----------
    values : array
        Array to simplify.

    Returns
    -------
    None, value or Array
        All unique value available.

    """
    try:
        all_val_check = get_not_null(values, alter=alter)
        if all_val_check is None:
            return None
        if isinstance(all_val_check, (set, tuple, list)):
            all_val_check = list(set(all_val_check))
        if len(all_val_check) == 1:
            return all_val_check[0]
        return all_val_check

    except Exception as error:
        print_exception()
        raise ValueError(f"Error simplifying array {values}") from error
