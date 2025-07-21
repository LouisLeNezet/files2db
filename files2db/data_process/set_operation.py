#!/usr/bin/env python3
"""
Created on 22/01/2021
@author: LouisLeNezet
Module for all functions to analyse set of data.
"""

import logging
from collections import abc as class_name

import numpy as np
import pandas as pd

from ..data_process.null_values import all_modify, bool_invert, get_not_null, is_null, not_null
from ..ui.print_infos import print_exception


def convert_to_set(values, alter=False, to_list=False):
    """
    Convert multiple type of value to value_a set of value.

    Parameters
    ----------
    values : Multiple
        Array, list, string to convert to set.
    alter : Boolean
        Does the values need to be stripped from whitespace and put to UPPER case

    Raises
    ------
    Format
        Type of value not recognise.

    Returns
    -------
    Set
        Set obtained after conversion.

    """
    try:
        if is_null(values, alter=alter):
            set_values = []
        elif isinstance(values, (str, float, int, np.integer, np.floating)):
            set_values = [values]
        elif isinstance(values, (set, tuple)):
            set_values = list(values)
        elif isinstance(values, (pd.Series, list)):
            set_values = list(values)
        elif isinstance(values, class_name.KeysView):
            set_values = list(values)
        elif isinstance(values, dict):
            set_values = list(values.values())
        else:
            raise ValueError(f"Instance of {values} not recognised")

        if not_null(set_values) and alter:  # Delete spaces and put it to UPPER case
            set_values = [
                elem.replace(" ", "").upper() if isinstance(elem, str) else elem
                for elem in set_values
                if not_null(elem, alter=alter)
            ]

        if to_list:
            return list(set(set_values))
        return set(set_values)

    except Exception as error:
        logging.info("%s, %s", values, type(values))
        print_exception()
        raise ValueError(f"Error while converting {values} to set") from error


def percent_error(str_a, str_b, alter=False):
    """
    Give the percentage of difference existing between two string.

    Parameters
    ----------
    str_a : String
        First string.
    str_b : String
        Second string.

    Returns
    -------
    Int
        Percentage of difference between the two string.

    """
    try:
        instance_ok = (int, str)
        if not isinstance(str_a, instance_ok) or not isinstance(str_b, instance_ok):
            raise ValueError(f"{str_a} or {str_b} not recognised")
        str_a = str(str_a)
        str_b = str(str_b)
        if alter:
            str_a = str_a.replace(".", "").replace(" ", "").upper()
            str_b = str_b.replace(".", "").replace(" ", "").upper()
        values = sum(
            1 for value_a, value_b in zip(str(str_a), str(str_b), strict=False) if value_a != value_b
        )
        len_a = len(str(str_a))
        len_b = len(str(str_b))
        values = values + abs(len_a - len_b)
        diff_size = int(values / max(len_a, len_b) * 100)
        return diff_size
    except Exception as error:
        print_exception()
        raise ValueError(
            f"Error while calculating the % of difference between {str_a} and {str_b}"
        ) from error


def difference(values_a, values_b, alter=False):
    """
    Difference of set value_a by value_b.

    Both values will be converted to set

    Parameters
    ----------
    value_a : Multiple
        First values.
    value_b : Multiple
        Second values.
    alter : Boolean
        Does the values need to be stripped from whitespace and put to upper case

    Returns
    -------
    List
        List of elements from set value_a not in value_b.

    """
    try:
        values_a = convert_to_set(values_a, alter)
        values_b = convert_to_set(values_b, alter)
        return list(values_a - values_b)
    except Exception as error:
        logging.info(
            "Difference failed: %s, %s, %s, %s",
            values_a,
            type(values_a),
            values_b,
            type(values_b),
        )
        print_exception()
        raise ValueError(
            f"Error while getting the difference between {values_a} and {values_b}"
        ) from error


def joint(values_a, values_b, alter=False):
    """
    Is at least one element in common between set value_a and value_b.

    Both values will be converted to set

    Parameters
    ----------
    value_a : Multiple
        First values.
    value_b : Multiple
        Second values.
    alter : Boolean
        Does the values need to be stripped from whitespace and put to upper case

    Returns
    -------
    Bool
        Does set value_a and set value_b have a common element .

    """
    try:
        values_a = convert_to_set(values_a, alter)
        values_b = convert_to_set(values_b, alter)
        return not values_a.isdisjoint(values_b)
    except Exception as error:
        print_exception()
        raise ValueError(
            f"Error while getting the joint between {values_a} and {values_b}"
        ) from error


def disjoint(values_a, values_b, alter=False):
    """
    Is no element in common between set value_a and value_b.

    Both values will be converted to set

    Parameters
    ----------
    value_a : Multiple
        First values.
    value_b : Multiple
        Second values.
    alter : Boolean
        Does the values need to be stripped from whitespace and put to upper case

    Returns
    -------
    Bool
        Does set value_a and set value_b have no common element .

    """
    try:
        return bool_invert(joint(values_a, values_b, alter))
    except Exception as error:
        print_exception()
        raise ValueError(
            f"Error while getting the disjoint between {values_a} and {values_b}"
        ) from error


def intersect(values_a, values_b, alter=False):
    """
    Intersection of set value_a by value_b.

    Both values will be converted to set

    Parameters
    ----------
    value_a : Multiple
        First values.
    value_b : Multiple
        Second values.
    alter : Boolean
        Does the values need to be stripped from whitespace and put to upper case

    Returns
    -------
    List
        List of elements in set value_a and in value_b.

    """
    try:
        values_a = convert_to_set(values_a, alter)
        values_b = convert_to_set(values_b, alter)
        inter = list(values_a.intersection(values_b))
        if not inter:
            return []
        else:
            return inter
    except Exception as error:
        logging.info("Intersect failed: %s %s", str(values_a), str(values_b))
        print_exception()
        raise ValueError(
            f"Error while getting the intersect between {values_a} and {values_b}"
        ) from error


def union(values_a, values_b, alter=False):
    """
    Union of set value_a by value_b.

    Both values will be converted to set

    Parameters
    ----------
    value_a : Multiple
        First values.
    value_b : Multiple
        Second values.
    alter : Boolean
        Does the values need to be stripped from whitespace and put to upper case

    Returns
    -------
    List
        List of unique elements from set value_a and value_b.

    """
    try:
        values_a = convert_to_set(values_a, alter)
        values_b = convert_to_set(values_b, alter)
        if not_null(values_b):
            return list(values_a.union(values_b))
        return list(values_a)
    except Exception as error:
        logging.info("Union failed: %s %s", str(values_a), str(values_b))
        print_exception()
        raise ValueError(
            f"Error while getting the union between {values_a} and {values_b}"
        ) from error


def match(values_a, values_b, alter=False):
    """
    Get boolean array for the match of value_b in value_a.

    Parameters
    ----------
    value_a : Multiple
        First values.
    value_b : Multiple
        Second values.
    alter : Boolean
        Does the values need to be stripped from whitespace and put to upper case

    Returns
    -------
    List
        List of boolean of each elements from value_a if match element from value_b.

    """
    try:
        values_a = all_modify(values_a, alter)
        values_b = all_modify(values_b, alter)
        if any(get_not_null(values_b)):
            result = []
            for value in values_a:
                result.append(value in values_b)
            return result
        return [False for i in values_a]
    except Exception as error:
        logging.info("Match failed: %s %s", str(values_a), str(values_b))
        print_exception()
        raise ValueError(
            f"Error while getting the match between {values_a} and {values_b}"
        ) from error
