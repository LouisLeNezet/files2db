

import pandas as pd

from files2db.data_process.null_values import get_not_null, is_null


def conca_simplify(
    data_df: pd.DataFrame, col_names: dict[str, list] | None = None
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
    data_se: pd.Series, type_check: tuple | None = ("str", "int")
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


def _to_bool_str(
    value: str,
    true_values: set[str] | None = None,
    false_values: set[str] | None = None,
) -> bool:
    if true_values is None:
        true_values = {"true", "1", "yes"}
    if false_values is None:
        false_values = {"false", "0", "no"}

    val_lower = value.lower()
    if val_lower in true_values:
        return True
    if val_lower in false_values:
        return False
    raise ValueError("String value must be 'True' or 'False'")


def _to_bool_int(
    value: int,
    true_values: set[str] | None = None,
    false_values: set[str] | None = None,
) -> bool:
    if true_values is None:
        true_values = {1}
    if false_values is None:
        false_values = {0}

    if value in true_values:
        return True
    if value in false_values:
        return False
    raise ValueError("Integer value must be 1 or 0")


def _to_bool_float(
    value: float,
    true_values: set[str] | None = None,
    false_values: set[str] | None = None,
) -> bool:
    if true_values is None:
        true_values = {1.0}
    if false_values is None:
        false_values = {0.0}

    if value in true_values:
        return True
    if value in false_values:
        return False
    raise ValueError("Float value must be 1.0 or 0.0")


def to_bool(
    value: any,
    fillna_value: bool | None = None,
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
        raise ValueError("value cannot be None and fillna_value is not provided")

    str_true = {"true"}
    str_false = {"false"}
    int_true = {1}
    int_false = {0}
    float_true = {1.0}
    float_false = {0.0}

    if isinstance(value, str):
        return _to_bool_str(value, str_true, str_false)

    if isinstance(value, int):
        return _to_bool_int(value, int_true, int_false)

    if isinstance(value, float):
        return _to_bool_float(value, float_true, float_false)

    if isinstance(value, bool):
        return value

    raise TypeError(f"Cannot interpret {value!r} of type {type(value)} as boolean")


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


def df_to_str_keep_na(
    df: pd.DataFrame,
    na_values: list | None = None,
) -> pd.DataFrame:
    if na_values is None:
        na_values = [None, "", "NaN", "nan", "<na>", "None", "NA", {}]  # Removed pd.NA explicitly

    return df.apply(
        lambda col: col.map(
            lambda x: str(x) if (not pd.isna(x) and x not in na_values) else pd.NA
        )
    )
