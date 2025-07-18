import pandas as pd
from typing import Dict, Optional

from ..data_process.null_values import is_null, get_not_null


def conca_simplify(
    data_df: pd.DataFrame, col_names: Optional[Dict[str, list]] = None
) -> pd.Series:
    """Simplify a nested dataframe into a single column.

    In the case of supplied col_names the columns

    Parameters
    ----------
    data_df: DataFrame
        DataFrame to simplify
    col_names: dict, optional
        Dictionnary of columns name. Defaults to None.

    Raises
    ----------
    Exception
        Error while trying to simplify the data

    Returns
    -------
    A vector of the simplified columns
    """
    if col_names is None:
        nest_array = data_df.values.tolist()
        nest_array = [get_not_null(x) for x in nest_array]
        nest_array = [
            None if is_null(x) else x if len(x) > 1 else x[0] if len(x) == 1 else None
            for x in nest_array
        ]
        return nest_array
    else:
        for col_main, col_all_sub in col_names.items():
            if col_all_sub is not None:
                all_col = {
                    col_main + "_" + col_sub: col_sub
                    for col_sub in col_all_sub
                    if col_main + "_" + col_sub in data_df.columns
                }
                data_df.rename(columns=all_col, inplace=True)
                data_df[col_main] = pd.Series(
                    data_df[all_col.values()].to_dict("records")
                )
                data_df.drop(all_col.values(), axis=1, inplace=True)
        return conca_simplify(data_df)


def nested_serie_test(data, value, test):
    """
    Test for each value at first level if all value present pass the test with a value given.

    Parameters
    ----------
    data : iterable
        Data from which should be compared the value.
    value : TYPE
        Value to use for the comparison.
    test: str
        Which test should be used: 'Sup', 'Inf', 'Equal', 'Diff'

    Returns
    -------
    list
        List of boolean.

    """
    if test == "Sup":
        return [
            x > value
            if not isinstance(x, list)
            else (all(nested_serie_test(x, value, test)))
            for x in data
        ]
    elif test == "Inf":
        return [
            x < value
            if not isinstance(x, list)
            else (all(nested_serie_test(x, value, test)))
            for x in data
        ]
    elif test == "Equal":
        return [
            x == value
            if not isinstance(x, list)
            else (all(nested_serie_test(x, value, test)))
            for x in data
        ]
    elif test == "Diff":
        return [
            x != value
            if not isinstance(x, list)
            else (all(nested_serie_test(x, value, test)))
            for x in data
        ]
    else:
        raise ValueError(f"Test {test} given isn't recognize")


def check_pd_series(
    data_se: pd.Series, type_check: Optional[tuple] = ("str", "int")
) -> bool:
    """
    Check if the input is a Pandas Series.

    Parameters
    ----------
    data_se : any
        Input to check.

    Returns
    -------
    bool
        True if input is a Pandas Series, False otherwise.
    """
    if not isinstance(data_se, pd.Series):
        raise TypeError("data_se should be a Pandas Series")

    if data_se.empty:
        return False

    for val in data_se:
        if pd.isna(val):
            continue
        if not isinstance(val, type_check):
            raise TypeError(f"data_se should be a Pandas Series of type {type_check}")

    return True


def to_bool(
    value: any,
    fillna_value: Optional[bool] = None,
) -> bool:
    """
    Convert a value to boolean.

    Parameters
    ----------
    value : any
        Value to convert.

    Returns
    -------
    bool
        Converted boolean value.
    """
    if value is None:
        if fillna_value is not None:
            return fillna_value
        else:
            raise ValueError("value cannot be None and fillna_value is not provided")

    if isinstance(value, str):
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        else:
            raise ValueError("value should be 'True' or 'False' as a string")
    elif isinstance(value, int):
        if value == 1:
            value = True
        elif value == 0:
            value = False
        else:
            raise ValueError("value should be 1 (True) or 0 (False) as an integer")
    elif isinstance(value, float):
        if value == 1.0:
            value = True
        elif value == 0.0:
            value = False
        else:
            raise ValueError("value should be 1.0 (True) or 0.0 (False) as a float")

    if not isinstance(value, bool):
        raise TypeError(
            f"value should be interpretable as a boolean value: got {value} of type {type(value)}"
        )

    return value


def update_only_missing(target_df, update_df):
    for col in update_df.columns:
        if col in target_df.columns:
            mask_target_is_notna = target_df[col].notna()
            mask_update_is_notna = update_df[col].notna()
            conflict_mask = mask_target_is_notna & mask_update_is_notna

            if conflict_mask.any():
                conflicted_indices = target_df.index[conflict_mask].tolist()
                raise ValueError(
                    f"Conflict detected in column '{col}' at rows {conflicted_indices}. "
                    "Attempt to overwrite non-null values."
                )

            # Safe to update only missing values
            mask = target_df[col].isna()
            target_df.loc[mask, col] = update_df.loc[mask, col]
        else:
            target_df[col] = update_df[col]
    return target_df


def df_to_str_keep_na(df):
    return df.applymap(lambda x: str(x) if pd.notna(x) else pd.NA)
