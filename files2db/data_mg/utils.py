from typing import Any

import pandas as pd


def check_pd_series(
    data_se: pd.Series,
    type_check: tuple[type, ...] | None = (str, int),  # Use type objects
) -> bool:
    """
    Check if the input is a Pandas Series.

    Parameters
    ----------
    data_se : any
        Input to check.

    type_check : Optional[Tuple[type, ...]]
        The types to check against. Defaults to (str, int).

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
        if type_check is not None and not isinstance(
            val, type_check
        ):  # Check only if type_check is not None
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
    raise ValueError(
        f"String value must be in true_values {true_values}"
        + f" or false_values {false_values}, got {val_lower}."
    )


def _to_bool_int(
    value: int,
    true_values: set[int] | None = None,
    false_values: set[int] | None = None,
) -> bool:
    if true_values is None:
        true_values = {1}
    if false_values is None:
        false_values = {0}

    if value in true_values:
        return True
    if value in false_values:
        return False
    raise ValueError(
        f"Integer value must be in true_values {true_values}"
        + f" or false_values {false_values}, got {value}."
    )


def _to_bool_float(
    value: float,
    true_values: set[float] | None = None,
    false_values: set[float] | None = None,
) -> bool:
    if true_values is None:
        true_values = {1.0}
    if false_values is None:
        false_values = {0.0}

    if value in true_values:
        return True
    if value in false_values:
        return False

    # Include true_values and false_values in the error message
    raise ValueError(
        f"Float value must be in true_values {true_values}"
        + f" or false_values {false_values}, got {value}."
    )


def to_bool(
    value: Any,
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
        lambda col: col.map(lambda x: str(x) if (not pd.isna(x) and x not in na_values) else pd.NA)
    )
