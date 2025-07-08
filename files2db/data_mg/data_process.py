import pandas as pd
import re
from typing import Optional, List

def clean_series(
    s: pd.Series,
    del_list: Optional[List[str]] = None,
    strip_from: Optional[List[str]] = None,
    del_in: Optional[List[str]] = None
) -> pd.Series:
    original_name = s.name
    s = s.astype(str)
    if del_list:
        s = s.replace(del_list, "")
    if strip_from:
        for val in strip_from:
            s = s.str.partition(val)[0]
    if del_in:
        for val in del_in:
            s = s.str.replace(val, "", regex=True)
    s.name = original_name
    return s

def data_sep(
    data_df: pd.DataFrame,
    sep: Optional[List[str]] = None,
) -> pd.DataFrame:
    data_df = data_df.copy()

    if data_df.empty:
        return data_df
    if sep is None:
        return data_df

    # Combine all separators into a single regex pattern
    regex_pattern = '|'.join(map(re.escape, sep))

    new_cols = []

    for col in data_df.columns:
        data_se = data_df[col].astype(str)
        # Split using the combined regex pattern
        data_exp = data_se.str.split(regex_pattern, expand=True)

        # Rename split columns
        data_exp.columns = [f"{col}_{i}" for i in range(data_exp.shape[1])]
        new_cols.append(data_exp)

    # Concatenate all new columns and return
    return pd.concat(new_cols, axis=1)

