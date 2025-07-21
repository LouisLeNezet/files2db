import pandas as pd
import numpy as np

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
    if alter:
        if isinstance(value, str):
            value = value.replace(" ", "").upper()
    if is_null(value, alter=alter):
        return None
    return value

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
                if isinstance(values, list | np.ndarray):
                    for value in values:
                        if isinstance(value, all_array_types):
                            dnn.append(all_modify(value, alter=alter))
                        else:
                            dnn.append(modify(value, alter))
                    return dnn
                if isinstance(values, tuple):
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
                raise ValueError("Values is iterable but not recognize")
            else:
                return modify(values, alter)
        else:
            return None
    else:
        return values


from collections.abc import Iterable

def any_nested_list(my_data, item):
    """
    Determines if an item is in my_data, even if nested in lower-level iterables.

    Works for any iterable type except strings and bytes (which are treated as atomic).
    """
    # Handle direct equality (including bool)
    if my_data == item:
        return True

    # Avoid treating strings or bytes as iterable here to prevent infinite recursion
    if isinstance(my_data, str | bytes):
        return False

    # If it's iterable, recurse into it
    if isinstance(my_data, dict):
        # For dict, check values
        return any(any_nested_list(v, item) for v in my_data.values())

    if isinstance(my_data, Iterable):
        # For other iterables, check each element
        return any(any_nested_list(elem, item) for elem in my_data)

    # For non-iterable types that did not match item, return False
    return False



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
    all_val_check = get_not_null(values, alter=alter)
    if all_val_check is None:
        return None
    if isinstance(all_val_check, set | tuple | list):
        all_val_check = list(set(all_val_check))
    if len(all_val_check) == 1:
        return all_val_check[0]
    return all_val_check
