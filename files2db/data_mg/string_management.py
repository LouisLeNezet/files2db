import re
import pandas as pd
from typing import Optional, List
from ..ui.print_infos import print_exception
from .data_convert import date_convert, num_convert


def data_replace(
    data_se: pd.Series,
    equiv_data: dict[str, list[str]],
    to_lower: bool = True
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
    print(data_se)
    if data_se.empty:
        return data_se

    if not isinstance(equiv_data, dict):
        raise TypeError("equiv_data should be a dictionary")
    if not all(isinstance(k, str) and isinstance(v, list) for k, v in equiv_data.items()):
        raise TypeError("equiv_data should be a dictionary with string keys and list values")
    if not all(isinstance(val, str) for sublist in equiv_data.values() for val in sublist):
        raise TypeError("All values in equiv_data should be strings")
    if equiv_data == {}:
        return data_se
    
    if not isinstance(data_se, pd.Series):
        raise TypeError("data_se should be a Pandas Series")

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


def data_clean(
    data_se: pd.Series,
    del_match: Optional[List[str]] = None,
    del_start: Optional[List[str]] = None,
    del_end: Optional[List[str]] = None,
    strip_from: Optional[List[str]] = None,
    del_in: Optional[List[str]] = None,
    na_value=None,
) -> pd.Series:
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

    if del_start is not None:
        for mod_del in del_start:
            data_se = data_se.str.replace(f"^{mod_del}", "", regex=True)
    if del_end is not None:
        for mod_del in del_end:
            data_se = data_se.str.replace(f"{mod_del}$", "", regex=True)

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


def data_conv(
    data_se : pd.Series,
    data_type: Optional[str] = None,
) -> pd.Series:
    if data_se.empty:
        return data_se

    if data_type is not None:
        if data_type == "lower":
            data_se = data_se.str.lower()
        elif data_type == "UPPER":
            data_se = data_se.str.upper()
        elif data_type == "Title":
            data_se = data_se.str.title()
        elif data_type == "date":
            data_se = data_se.str.replace("-", ".", regex=False)
            data_se = data_se.apply(lambda row: date_convert(row))
        elif data_type in ["int", "float"]:
            data_se = num_convert(data_se, to_type=data_type)
        elif data_type == "string":
            data_se = data_se.astype(str)
        elif data_type == "bool":
            data_se = data_se.str.lower().replace({"true": True, "false": False})
            data_se = data_se.astype(bool)
        else:
            raise ValueError(f"Unknown case type: {data_type}")

    return data_se


def data_sep(
    data_se: pd.Series,
    sep: Optional[List[str]] = None,
) -> pd.DataFrame:
    data_se = data_se.copy()

    if data_se.empty:
        return pd.DataFrame(data_se)
    if sep is None:
        return pd.DataFrame(data_se)

    # Combine all separators into a single regex pattern
    print(sep)
    regex_pattern = "|".join(map(re.escape, sep))

    data_se = data_se.astype(str)
    col = data_se.name

    # Split using the combined regex pattern
    data_exp = data_se.str.split(regex_pattern, expand=True)

    # Rename split columns
    data_exp.columns = [f"{col}_{i}" for i in range(data_exp.shape[1])]

    # Concatenate all new columns and return
    return data_exp


def data_sep_pattern(
    data_se: pd.Series,
    pattern: Optional[str] = None,
    keep_link: bool = False,
    ignore_case: bool = True,
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
    if data_se.empty:
        return pd.DataFrame(data_se)
    if pattern is None:
        return pd.DataFrame(data_se)

    # Extract named groups from the pattern
    named_groups = re.findall(r"\(\?P<(\w+)>", pattern)

    if not named_groups:
        raise ValueError("No named groups found in the regex pattern.")

    flags = re.IGNORECASE if ignore_case else 0

    try:
        # Extract based on pattern with named groups
        data_match = data_se.astype(str).str.extract(pattern, flags=flags)
    except re.error as exc:
        raise ValueError(f"Invalid regex pattern: {exc}")
    
    # Keep only named groups
    data_match = data_match.loc[:, named_groups]

    if keep_link:
        # Add the column original name to the new columns
        data_match.columns = [
            f"{data_se.name}_{col}"
            for col in data_match.columns
        ]

    return data_match
