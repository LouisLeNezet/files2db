import re
import pandas as pd
from typing import Optional, List
from ..ui.print_infos import print_exception

def data_replace(data_se: pd.Series, equiv_data: dict[str, list[str]], to_lower: bool = True):
    """
    Replace all values in a Series based on equivalency mappings.

    Parameters
    ----------
    data_se : pd.Series
        Series to normalize.
    equiv_data : dict
        Dictionary where keys are normalized values and values are lists of equivalent terms.
    to_lower : bool, optional
        Whether to lowercase all values before matching (default: True).

    Returns
    -------
    pd.Series
        Normalized Series with values replaced according to equivalency mappings.

    Raises
    ------
    RuntimeError
        If replacement fails.
    """
    try:
        replace_dict = {}

        for norm_val, equivalents in equiv_data.items():
            if to_lower:
                norm_val = norm_val.lower()
                equivalents = [val.lower() for val in equivalents]
            for eq in equivalents:
                replace_dict[eq] = norm_val

        if to_lower:
            data_se = data_se.str.lower()

        return data_se.replace(replace_dict)

    except Exception as exc:
        print_exception()
        raise RuntimeError("Error while replacing values using equivalency mappings") from exc


def data_del(
    data_se: pd.Series,
    del_match: Optional[List[str]] = None,
    strip_from: Optional[List[str]] = None,
    del_in: Optional[List[str]] = None,
    na_value=None
) -> pd.Series :
    """
    Clean and normalize string data in a Pandas Series.

    Parameters
    ----------
    data_se : pd.Series
        Series to normalize.
    del_match : list of str, optional
        Values that, if fully matched, will be replaced by `na_value`.
    strip_from : list of str, optional
        Substrings; everything after each will be removed.
    del_in : list of str, optional
        Substrings to delete from inside strings.
    na_value : Any, optional
        Value to use when replacing removed items (default is np.nan).

    Returns
    -------
    pd.Series
        Cleaned Pandas Series.
    """
    original_name = data_se.name
    data_se = data_se.astype(str)
    if data_se.empty:
        return data_se

    # Delete full matches
    if del_match:
        data_se = data_se.replace(del_match, na_value)

    # Strip after substring
    if strip_from:
        for delim in strip_from:
            data_se = data_se.str.partition(delim)[0]

    # Delete substring inside string
    if del_in:
        for sub in del_in:
            pattern = re.escape(sub)
            data_se = data_se.str.replace(pattern, "", regex=True)
    data_se.name = original_name
    return data_se

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
