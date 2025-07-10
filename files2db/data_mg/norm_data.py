# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 12:28:13 2021

@author: LouisLeNezet
"""
import re
import logging
import numpy as np
import pandas as pd
from ..ui.print_infos import print_exception
from ..data_process.set_operation import intersect, joint, match
from ..data_process.null_values import array_not_null, not_null, is_null
from ..data_process.null_values import get_not_null, any_nested_list
from .convert import date_convert, num_convert

pd.set_option('display.max_columns', None)

def conca_simplify(data_df, col_names=None):
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
    try:
        if col_names is None:
            nest_array = data_df.values.tolist()
            nest_array = [get_not_null(x)
                        for x in nest_array]
            nest_array = [None if is_null(x)
                        else x if len(x) > 1
                        else x[0] if len(x) == 1
                        else None for x in nest_array]
            return nest_array
        else:
            for col_main, col_all_sub in col_names.items():
                if not col_all_sub is None:
                    all_col = {col_main+"_"+col_sub: col_sub for col_sub in col_all_sub
                                if col_main+"_"+col_sub in data_df.columns}
                    data_df.rename(columns=all_col, inplace=True)
                    data_df[col_main] = pd.Series(data_df[all_col.values()].to_dict('records'))
                    data_df.drop(all_col.values(), axis=1, inplace=True)
            return conca_simplify(data_df)
    except Exception as exc:
        print_exception()
        raise RuntimeError("Error while concatenating the datas") from exc


def data_conv(data_df, params):
    """
    Convert all columns of a dataframe based on the parameters given.

    Parameters
    ----------
    data_df : DataFrame
        DataFrame with all the columns to convert.
    params : Dict
        Dictionary with  all the parameteres necessary for the conversion.

    Raises
    ------
    No type given
        When converting to numeric a type should be given.

    Returns
    -------
    data_df : DataFrame
        Same dataFrame as iinput but with all columns converted.
    all_errors : TYPE
        DESCRIPTION.

    """
    try:
        all_errors = None
        errors = []
        for col in data_df:
            data = data_df[col]
            err_conv = [None for x in data_df.index]
            if "DelStart" in params.keys() and not_null(params["DelStart"], True):
                for mod_del in params["DelStart"].split(","):
                    data = data.str.replace(f'^{mod_del}', "", regex=True)
            if "DelEnd" in params.keys() and not_null(params["DelEnd"], True):
                for mod_del in params["DelEnd"].split(","):
                    data = data.str.replace(f'{mod_del}$', "", regex=True)

            if "Corres" in params.keys() and not_null(params["Corres"]):
                data = data_replace(data, params["Corres"])

            if "Case" in params.keys() and not_null(params["Case"], True):
                if params["Case"] == "UPPER":
                    data = data.str.upper()
                elif params["Case"] == "lower":
                    data = data.str.lower()
                elif params["Case"] == "Title":
                    data = data.str.title()

            if "ToDate" in params.keys() and params["ToDate"] == "T":
                data = data.str.replace("-", ".", regex=False)
                data = data.apply(lambda row: date_convert(row))

            if "ToNum" in params.keys() and params["ToNum"] == "T":
                if "ToType" in params.keys() and not_null(params["ToType"]):
                    data, err_conv = num_convert(data, params["ToType"])
                else:
                    raise ValueError("Error while converting to numeric, no type given")

            errors.append([{"When": "Converting",
                            "Which": data_df.loc[ind, col],
                            "Error": err} if not_null(err)
                            else {}
                            for ind, err in zip(data_df.index, err_conv)])

            data_df[col] = data

        if not_null(errors):
            all_errors = [value for value in np.column_stack(errors).tolist()]

        return data_df, all_errors
    except Exception as exc:
        print_exception()
        raise RuntimeError("Error while converting data") from exc

def data_vali(data_df, params):
    try:
        all_errors = None
        errors = []
        for col in data_df:
            data = data_df[col]
            err_content = err_min = err_max = [None for x in data]
            if "Contains" in params.keys() and not_null(params["Contains"]):
                if params["Contains"] == "LETTERS":
                    err_content = data.str.fullmatch('[A-Z]+', case=True, na=False)
                elif params["Contains"] == "letters":
                    err_content = data.str.fullmatch('[a-z]+', case=True, na=False)
                elif params["Contains"] == "Letters":
                    err_content = data.str.fullmatch(r'([A-Z][a-z]+)(\s[A-Z][a-z]+)*', case=True, na=False)
                elif params["Contains"] == "Date":
                    err_content = data.str.fullmatch(long_date_f, case=True, na=False)
                elif params["Contains"] == "ALPHANUM":
                    err_content = data.str.fullmatch("[A-Z0-9]*", case=True, na=False)
                elif params["Contains"] == "alphanum":
                    err_content = data.str.fullmatch("[a-z0-9]*", case=True, na=False)
                elif params["Contains"] == "Int":
                    err_content = [isinstance(x, int) for x in data]
                elif params["Contains"] == "Float":
                    err_content = [isinstance(x, float) for x in data]
                else:
                    err_content = data.str.fullmatch(params["Contains"].replace(",", "|"), case=True, na=False)
                err_content = ["No corres with " + params["Contains"] if (not err and not_null(val))
                                else None for err, val in zip(err_content, data)]

            all_num = [isinstance(x, (int, float)) for x in data]
            types = [type(x) for x in data]
            check_min = "Min" in params.keys() and not_null(params["Min"])
            check_max = "Max" in params.keys() and not_null(params["Max"])

            if not all(all_num):
                if check_min:
                    err_min = ["InfToMin" if (not_null(x) and len(x) < params["Min"]) else None for x in data]
                if check_max:
                    err_max = ["SupToMax" if (not_null(x) and len(x) > params["Max"]) else None for x in data]
            else:
                if check_min:
                    err_min = ["InfToMin" if (not_null(x) and x < params["Min"]) else None for x in data]
                if check_max:
                    err_max = ["SupToMax" if (not_null(x) and x > params["Max"]) else None for x in data]

            err = [get_not_null([e_cont, e_min, e_max])
                    for e_cont, e_min, e_max in zip(err_content, err_min, err_max)]

            errors.append([{"When": "Validating",
                            "Which": data_df.loc[ind, col],
                            "Error": err} if not_null(err)
                            else {}
                            for ind, err in zip(data_df.index, err)])

        if not_null(errors):
            all_errors = [value for value in np.column_stack(errors).tolist()]
        return all_errors
    except Exception as exc:
        print_exception()
        raise RuntimeError("Error while validating") from exc

def data_manage(df, col_to_use, all_params, col_not_to_add):
    """
    Convert data based on the parameters given.

    Parameters
    ----------
    data : Series
        Data to normalize.
    params : Series
        Parameters necessary to normalize.
    corres : Dataframe
        Corresponding value

    Returns
    -------
    Series normalized.

    """
    try:
        data_df = df[[col_to_use]].copy()
        all_errors = {ind: [] for ind in data_df.index}
        err = pd.DataFrame(index=data_df.index)

        for norm_by in all_params.keys():
            key_keep_case = [k for k in all_params[norm_by].keys() if re.match(r"Sep\dName|Sep\dPat", k)]
            key_keep_case = key_keep_case+["Contains", "Case", "Value", "ToDate", "ToNum", "ToSep", "Types", "SepKeepLink"]
            all_params[norm_by] = dict((k, v.lower()) if (k not in key_keep_case and isinstance(v, str))
                                        else (k, v) for k, v in all_params[norm_by].items())

        for norm_by in all_params.keys():
            params = all_params[norm_by]
            data_df = data_sep_del(data_df, params)

        col_for_rename = {col_name: None for col_name in data_df.columns}
        for norm_by in all_params.keys():
            params = all_params[norm_by]
            data_df, df, err[norm_by+"_Sep"], col_for_rename = data_sep_pat(data_df, df, col_for_rename, params)
        print("SepDone")
        for norm_by in all_params.keys():
            params = all_params[norm_by]
            data_df, err[norm_by+"_Conv"] = data_conv(data_df, params)
        print("ConvDone")
        for norm_by in all_params.keys():
            params = all_params[norm_by]
            err[norm_by+"_Vali"] = data_vali(data_df, params)
        print("ValiDone")
        if col_for_rename is None:
            col_not_to_add.append(col_to_use)
        else:
            df[col_to_use] = pd.Series(conca_simplify(data_df, col_for_rename))
        for ind in data_df.index:
            err_to_add = []
            for norm_by in all_params.keys():
                for err_type in ["Sep", "Conv", "Vali"]:
                    err_ind = err.loc[ind, norm_by + "_" + err_type]
                    if any_nested_list(array_not_null(err_ind, True), True):
                        for val in err_ind:
                            if not_null(val):
                                val.update({"NormBy": norm_by})
                                err_to_add.append(val)
            if not_null(err_to_add):
                all_errors[ind] = err_to_add

        return df, all_errors, col_not_to_add
    except Exception as exc:
        print_exception()
        raise RuntimeError("Error while converting") from exc

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
        return [x > value if not isinstance(x, list)
                else (all(nested_serie_test(x, value, test))) for x in data]
    elif test == "Inf":
        return [x < value if not isinstance(x, list)
                else (all(nested_serie_test(x, value, test))) for x in data]
    elif test == "Equal":
        return [x == value if not isinstance(x, list)
                else (all(nested_serie_test(x, value, test))) for x in data]
    elif test == "Diff":
        return [x != value if not isinstance(x, list)
                else (all(nested_serie_test(x, value, test))) for x in data]
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

def get_col_infos(columns, db_orga):
    """
    Extract and summarize the informations for a column.

    All informations are extracted from a DataFrame obtained from the Excel File.
    If the Column inherit from multiple class, their should be listed.
    All parameters will be listed for each corresponding class.

    Parameters
    ----------
    column : list or str
        List of all the subfield to get information from.
    db_orga : list of dataframe
        Organisation of the database obtained from the Excel file.

    Raises
    ------
    Multi match
        A field/subfield has been found more than once in the database organisation.
    No match
        None of the field/subfield given was found in the database organisation.

    Returns
    -------
    all_col_infos : list of dict
        Dictionnary for each columns with their information.

    """
    try:
        if not isinstance(columns, list):
            columns = [columns]
        all_col_infos = []
        for col in columns:
            col_infos = {}
            col_field = intersect(db_orga["Fields"]["Fields"], col)
            field_match = match(db_orga["Fields"]["Fields"], col_field)
            if sum(field_match) == 1:
                col_infos["Types"] = db_orga["Fields"]["Types"].values[field_match][0]
                col_infos["Categories"] = db_orga["Fields"]["Categories"].values[field_match][0]
                col_infos["Contains"] = db_orga["Fields"].loc[field_match,
                                                            ["Min", "Max", "Contains"]].squeeze()
                col_infos["Fields"] = col_field[0]
                col_infos["Field_match"] = field_match
                all_col_infos.append(col_infos)
            else:
                if sum(field_match) == 0:
                    logging.info("%s field not recognize", col)
                else:
                    raise ValueError(f"{col} field present more than once")
            #  print(all_col_infos)
        if is_null(all_col_infos):
            raise ValueError(f"{col} field(s) not present")
        return all_col_infos
    except Exception as exc:
        print_exception()
        raise RuntimeError(f"Error while getting info for {col}") from exc

def norm_data2(file, db_orga):
    """
    Normalize dataframe based on informations read in excel file.

    Parameters
    ----------
    file : Dataframe
        Data to normalize.
    db_orga : data organisation and transformation by Categories and types

    Returns
    -------
    file_normalized : Dataframe
        Data normalized.

    """
    try:
        logging.info("Starting normalization of the datas")
        all_errors = {}
        # Delete empty columns
        file.dropna(how='all', axis='columns', inplace=True)
        file.columns = file.columns.str.replace(".", "_", regex=False)
        # Normalize all accent and lower all data
        file.fillna("", inplace=True)
        file = file.apply(lambda x: (x.astype(str).str.normalize('NFKD')
                                    .str.lower()
                                    .str.encode('ascii', errors='ignore')
                                    .str.decode('utf-8')))

        col_checked = {x: False for x in file.columns}
        col_not_to_add = []
        while not all(col_checked.values()):
            col_to_use = [k for k in col_checked.keys() if not col_checked[k]][0]
            col = col_to_use.split("_")
            print(col)

            all_col_infos = get_col_infos(col, db_orga)
            all_params = {}

            if all_col_infos:
                #  Data wil be normalize by each sub_field
                for col_infos in all_col_infos:
                    #  Data will be normalize by Type -> Category -> Field
                    for norm_by, params_in in zip(["Types", "Categories", "Fields"],
                                                ["Types", "Types", "Fields"]):
                        print(col_infos[norm_by], norm_by)
                        if joint(col_infos[norm_by], db_orga[params_in][params_in]):
                            params = db_orga[params_in].loc[match(db_orga[params_in][params_in],
                                                                col_infos[norm_by]), ].squeeze().to_dict()
                            params = get_not_null(params)
                            if col in list(db_orga["Corres"]["Fields"]):
                                corres = db_orga["Corres"].loc[match(db_orga["Corres"]["Fields"],
                                                                    col_infos[norm_by]), ["Eq", "Value"]]
                                params.update({"Corres": corres.to_dict("records")})
                            all_params.update({norm_by+"_"+params[norm_by]: params})
                file, errors_present, col_not_to_add = data_manage(file, col_to_use, all_params, col_not_to_add)

                errors_to_add = [not_null(lvl1) for lvl1 in errors_present.values()]
                if any(errors_to_add):
                    file[str(col_to_use + "_Error")] = errors_present.values()
                    if col_to_use != "NomChien":
                        cols_to_use = ["NomChien", col_to_use, str(col_to_use + "_Error")]
                    else:
                        cols_to_use = ["NomChien", str(col_to_use + "_Error")]
                    all_errors.update({col_to_use: error_register(file.loc[errors_to_add, cols_to_use])})
                    del file[str(col_to_use + "_Error")]
                    file.loc[errors_to_add, col_to_use] = None
                col_checked[col_to_use] = True

                for col in file.columns:
                    if "_Error" not in col and col not in col_checked.keys():
                        col_checked.update({col: False})
            else:
                logging.info("No information found to normalize this column")
        col_to_add = [col for col in file.columns if col not in col_not_to_add]
        return(file[col_to_add], all_errors)
    except Exception as exc:
        print_exception()
        raise RuntimeError("Could not normalize") from exc
