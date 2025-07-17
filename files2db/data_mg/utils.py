import pandas as pd
from typing import Dict, Optional

from ..data_process.null_values import is_null, get_not_null

def conca_simplify(
    data_df: pd.DataFrame,
    col_names: Optional[Dict[str, list]] = None
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
            None
            if is_null(x)
            else x
            if len(x) > 1
            else x[0]
            if len(x) == 1
            else None
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


def conca_data(row):
    """
    Concatenate all data in list or unique if only one.

    Parameters
    ----------
    row : Serie
        Row to concatenate.

    Returns
    -------
    Array or String
        All data available.

    """
    try:
        all_data_check = []
        for x in range(len(row)):
            if not_null(row[x]):
                all_data_check.append(row[x])
        if len(all_data_check) == 0:
            return ""
        elif len(all_data_check) == 1:
            return all_data_check[0]
        else:
            return all_data_check

    except RuntimeError as exc:
        print_exception()
        return f"Error: {exc}"


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


def error_register(df_errors):
    """
    Generate a list with all the errors as independent document.

    Parameters
    ----------
    df_errors : Dataframe
        The dataframe with all the errors by rows.

    Returns
    -------
    errors : list
        List of dictionnaries of each row of the dataframe with the index added.

    """
    try:
        errors = []
        values = df_errors.to_dict("records")
        for index, val in zip(df_errors.index, values):
            error = {}
            if not_null(val) and any(array_not_null(val)):
                error.update(get_not_null(val))
                error.update({"Index": index})
                errors.append(error)
        return errors
    except Exception as exc:
        print_exception()
        raise RuntimeError("Error while registering error") from exc


def check_pd_series(
    data_se: pd.Series,
    type_check: Optional[tuple] = ("str", "int")
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
