import re

import numpy as np
import pandas as pd

from files2db.data_mg.utils import check_pd_series, to_bool


def data_replace(
    data_se: pd.Series, equiv_data: dict[str, list[str]], to_lower: bool = True
):
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
    if not isinstance(equiv_data, dict):
        raise TypeError("equiv_data should be a dictionary")
    if not all(
        isinstance(k, str) and isinstance(v, list) for k, v in equiv_data.items()
    ):
        raise TypeError(
            "equiv_data should be a dictionary with string keys and list values"
        )
    if not all(
        isinstance(val, str) for sublist in equiv_data.values() for val in sublist
    ):
        raise TypeError("All values in equiv_data should be strings")
    if equiv_data == {}:
        return data_se

    if not check_pd_series(data_se, type_check=str):
        return data_se

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


def _replace_full_matches(series: pd.Series, match_list: list[str], fill_value) -> pd.Series:
    return series.replace(match_list, fill_value)


def _remove_substrings(series: pd.Series, substrings: list[str]) -> pd.Series:
    for sub in substrings:
        series = series.str.replace(sub, "", regex=True)
    return series


def _remove_start(series: pd.Series, patterns: list[str]) -> pd.Series:
    for p in patterns:
        series = series.str.replace(f"^{p}", "", regex=True)
    return series


def _remove_end(series: pd.Series, patterns: list[str]) -> pd.Series:
    for p in patterns:
        series = series.str.replace(f"{p}$", "", regex=True)
    return series


def _strip_after_delimiters(series: pd.Series, delimiters: list[str]) -> pd.Series:
    for delim in delimiters:
        series = series.str.partition(delim)[0]
    return series

def data_clean(
    data_se: pd.Series,
    del_match: list[str] | None = None,
    del_start: list[str] | None = None,
    del_end: list[str] | None = None,
    strip_from: list[str] | None = None,
    del_in: list[str] | None = None,
    fillna_value=np.nan,
) -> pd.Series:
    """
    Clean and normalize string data in a Pandas Series.

    Parameters
    ----------
    data_se : pd.Series
        Series to normalize.
    del_match : list of str, optional
        Values that, if fully matched, will be replaced by `fillna_value`.
    strip_from : list of str, optional
        Substrings; everything after each will be removed.
    del_in : list of str, optional
        Substrings to delete from inside strings.
    fillna_value : Any, optional
        Value to use when replacing removed items (default is np.nan).

    Returns
    -------
    pd.Series
        Cleaned Pandas Series.
    """
    original_name = data_se.name
    if not check_pd_series(data_se, type_check=str):
        return data_se

    if del_match:
        data_se = _replace_full_matches(data_se, del_match, fillna_value)
    if del_in:
        data_se = _remove_substrings(data_se, del_in)
    if del_start:
        data_se = _remove_start(data_se, del_start)
    if del_end:
        data_se = _remove_end(data_se, del_end)
    if strip_from:
        data_se = _strip_after_delimiters(data_se, strip_from)

    data_se.name = original_name
    return data_se


def data_sep(
    data_se: pd.Series,
    sep: list[str] | None = None,
    fillna_value: str | None = None,
) -> pd.DataFrame:
    if not check_pd_series(data_se, type_check=str):
        return pd.DataFrame(data_se)

    data_se = data_se.copy()

    if sep is None:
        return pd.DataFrame(data_se)

    # Combine all separators into a single regex pattern
    regex_pattern = "|".join(map(re.escape, sep))

    original_name = data_se.name

    # Split using the combined regex pattern
    data_exp = data_se.str.split(regex_pattern, expand=True)

    # Fill NaN values with the specified fillna_value
    if fillna_value is not None:
        data_exp.fillna(fillna_value, inplace=True)

    # Rename split columns
    data_exp.columns = [f"{original_name}_{i}" for i in range(data_exp.shape[1])]

    # Concatenate all new columns and return
    return data_exp


def data_sep_pattern(
    data_se: pd.Series,
    pattern: str | None = None,
    keep_link: bool = False,
    ignore_case: bool = True,
    fillna_value: str | None = None,
) -> pd.DataFrame:
    """
    Separate data given into different columns based on regex patterns.

    Parameters
    ----------
    data_se : pd.Series
        Series to separate.
    pattern : str, optional
        Regex pattern to use for separation. If None, no separation is performed.
        Patterns should be of the form (?P<column_name>)(?P<column_name2>).
        Unnamed groups will be ignored.

    Raises
    ------
    Wrong pattern group name
        Group name in regex patters should only be Data or Other.
    """
    # Set keep_link to boolean
    keep_link = to_bool(keep_link, fillna_value=False)

    if pattern is None:
        return pd.DataFrame(data_se)

    if not check_pd_series(data_se, type_check=str):
        return pd.DataFrame(data_se)

    # Compile pattern
    flags = re.IGNORECASE if ignore_case else 0
    try:
        compiled_pattern = re.compile(pattern, flags=flags)
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern: {exc}") from re.error

    # Extract named groups
    named_groups = compiled_pattern.groupindex.keys()
    if not named_groups:
        raise ValueError("Pattern must contain named groups (e.g., ?P<ColA>)")

    # Extract and keep only named groups
    data_match = data_se.str.extractall(compiled_pattern)

    aggregated = (
        data_match.reset_index()
        .drop(columns="match")
        .groupby("level_0")
        .agg(lambda x: next((i for i in x if pd.notna(i)), pd.NA))
    )

    # Reindex to original data with missing rows as pd.NA
    data_match_grouped = aggregated.reindex(data_se.index, fill_value=pd.NA)

    data_match_filtered = data_match_grouped.loc[:, named_groups]

    if keep_link:
        # Add the column original name to the new columns
        data_match_filtered.columns = [
            f"{data_se.name}_{col}" for col in data_match_filtered.columns
        ]

    if fillna_value is not None:
        data_match_filtered = data_match_filtered.fillna(fillna_value)

    return data_match_filtered
