import re
import pandas as pd

long_date_f = re.compile(r"\d\d\.\d\d\.\d\d\d\d")

def data_contains(
    data_se = pd.Series(),
    contains=None,
) -> pd.Series:
    """
    Check if the data contains specific patterns.
    
    Parameters:
    - data_se: pd.Series - The data to check.
    - contains: str - The pattern to check for.
    
    Returns:
    - pd.Series: A series with boolean values indicating if the pattern is found.
    """
    if contains is not None :
        if contains == "LETTERS":
            return data_se.str.fullmatch("[A-Z]+", case=True, na=False)
        elif contains == "letters":
            return data_se.str.fullmatch("[a-z]+", case=True, na=False)
        elif contains == "Letters":
            return data_se.str.fullmatch(r"([A-Z][a-z]+)(\s[A-Z][a-z]+)*", case=True, na=False)
        elif contains == "Date":
            return data_se.str.fullmatch(long_date_f, case=True, na=False)
        elif contains == "ALPHANUM":
            return data_se.str.fullmatch("[A-Z0-9]*", case=True, na=False)
        elif contains == "alphanum":
            return data_se.str.fullmatch("[a-z0-9]*", case=True, na=False)
        elif contains == "Int":
            return [isinstance(x, int) for x in data_se]
        elif contains == "Float":
            return [isinstance(x, float) for x in data_se]
        else:
            return data_se.str.fullmatch(contains.replace(",", "|"), case=True, na=False)
    else:
        return pd.Series([True] * len(data_se))

def data_vali(data_df, params):
    try:
        all_errors = None
        errors = []
        for col in data_df:
            data = data_df[col]
            err_content = err_min = err_max = [None for x in data]
            err_content = data_contains(data[col], params.get("Contains")) 
            err_content = [
                    "No corres with " + params["Contains"]
                    if (not err and not_null(val))
                    else None
                    for err, val in zip(err_content, data)
                ]

            all_num = [isinstance(x, (int, float)) for x in data]

            check_min = "Min" in params.keys() and not_null(params["Min"])
            check_max = "Max" in params.keys() and not_null(params["Max"])

            if not all(all_num):
                if check_min:
                    err_min = [
                        "InfToMin" if (not_null(x) and len(x) < params["Min"]) else None
                        for x in data
                    ]
                if check_max:
                    err_max = [
                        "SupToMax" if (not_null(x) and len(x) > params["Max"]) else None
                        for x in data
                    ]
            else:
                if check_min:
                    err_min = [
                        "InfToMin" if (not_null(x) and x < params["Min"]) else None
                        for x in data
                    ]
                if check_max:
                    err_max = [
                        "SupToMax" if (not_null(x) and x > params["Max"]) else None
                        for x in data
                    ]

            err = [
                get_not_null([e_cont, e_min, e_max])
                for e_cont, e_min, e_max in zip(err_content, err_min, err_max)
            ]

            errors.append(
                [
                    {"When": "Validating", "Which": data_df.loc[ind, col], "Error": err}
                    if not_null(err)
                    else {}
                    for ind, err in zip(data_df.index, err)
                ]
            )

        if not_null(errors):
            all_errors = [value for value in np.column_stack(errors).tolist()]
        return all_errors
    except Exception as exc:
        print_exception()
        raise RuntimeError("Error while validating") from exc