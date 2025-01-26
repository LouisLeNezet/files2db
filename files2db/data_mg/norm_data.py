# -*- coding: utf-8 -*-
"""
Module to normalize DataFrame.

Created on Tue Jan 19 12:50:51 2021

@author: LouisLeNezet
"""
import re
import logging
import numpy as np
import pandas as pd

from files2db.ui.print_infos import print_exception
from files2db.data_process.null_values import not_null, is_null, array_not_null
from files2db.data_process.null_values import get_not_null,bool_invert

def conca_name(row):
    """
    Concatenate usual name with name if present.

    Parameters
    ----------
    row : Serie
        Row to concatenate.

    Returns
    -------
    Array or String
        All name available.

    """
    try:
        all_name_check = get_not_null(row)
        if all_name_check is None:
            return None
        elif len(all_name_check) == 1:
            return all_name_check[0]
        else:
            return list(set(all_name_check))

    except Exception as error:
        print_exception()
        raise TypeError(f"Error while concatenating names {row}") from error


def num_id_sep(string_to_sep):
    """
    Separate chip number from tattoo and assert type and size.

    Parameters
    ----------
    string_to_sep : String
        String to separate.

    Raises
    ------
    Number of data
        Only one or two data should be available.
    Format
        Data doesn't have the right format. Chip is an int between 10^12 or 10^17.
        Tatoo is a string with 6 to 10 character.

    Returns
    -------
    list
        Tatoo and chip number separated.

    """
    pu_tat_array = list(str(string_to_sep).split("/"))
    puce, tatouage = np.NaN, np.NaN
    check = []
    try:
        nb_val = len(pu_tat_array)-pu_tat_array.count('')
        if nb_val > 2 or nb_val < 1:
            logging.info(pu_tat_array)
            raise TypeError("Too much or no data available")
        else:
            for data in pu_tat_array:
                if not_null(data):  # Do not check empty value
                    result = check_puce(data)
                    if result != "Not an int":
                        puce = result
                        check.append(result != "WrongFormat")
                    else:
                        tatouage = check_tatouage(data)
                        check.append(tatouage != "WrongFormat")
            if all(check):
                return [tatouage, puce]
            else:
                raise TypeError("Data do not have the right format")
    except TypeError:
        logging.info(str("Error for " + str(pu_tat_array) + " " + str(type(pu_tat_array))))
        return ["Error", "Error"]


def check_puce(puce):
    """
    Check if data passed is of type int and can be interpreted as a puce.

    Parameters
    ----------
    data : String
        Data to check.

    Returns
    -------
    String or Int
        Return 'Not an int', 'WrongFormat' or the corresponding int.

    """
    try:
        puce = int(puce)
        if len(str(puce)) > 12 and len(str(puce)) < 17:
            return puce
        if not_null(puce):
            return "WrongFormat"
    except ValueError:
        if not_null(puce):
            return "Not an int"
        return np.nan


def check_tatouage(data):
    """
    Check if data can be interpreted as a tatouage.

    Parameters
    ----------
    data : String
        Data to check.

    Returns
    -------
    String
        Return 'WrongFormat' or the corresponding string.

    """
    data = str(data)
    if len(data) > 6 or len(data) < 10:
        return data
    return "WrongFormat"

SHORT_DATE_F = re.compile(r"\d\d\.\d\d\.\d\d")
SUPER_SHORT_DATE_F = re.compile(r"\d\.\d\d\.\d\d")
LONG_DATE_F = re.compile(r"\d\d\.\d\d\.\d\d\d\d")
LONG_DATE_F_INV = re.compile(r"\d\d\d\d\.\d\d\.\d\d")
LONG_DATE_F_TIME = re.compile(r"\d\d\d\d-\d\d-\d\d00:00:00")

def date_convert(dates_to_convert):
    """
    Convert a string representing a date into a unique format.

    Parameters
    ----------
    date_to_convert : String
        String to convert to right format dd.mm.yyyy.

    Returns
    -------
    str
        Date in the right format.

    """
    try:
        if not_null(dates_to_convert):
            dates = []

            for date_to_convert in dates_to_convert.split("_"):
                if date_to_convert == "00:00:00" or date_to_convert == "0000-00-00":
                    new_date = None
                else:
                    if SUPER_SHORT_DATE_F.match(date_to_convert):
                        date_to_convert = str("0" + date_to_convert)
                    if SHORT_DATE_F.match(date_to_convert):
                        if date_to_convert[-2:] > "80":  # Siecle dernier
                            new_date = str(date_to_convert[0:6] + "19" + date_to_convert[-2:])
                        else:
                            new_date = str(date_to_convert[0:6] + "20" + date_to_convert[-2:])
                    elif LONG_DATE_F_TIME.match(date_to_convert):
                        new_date = str(date_to_convert[8:10] + "." +
                                        date_to_convert[5:7] + "." +
                                        date_to_convert[0:4])
                    elif LONG_DATE_F.match(date_to_convert):
                        new_date = str(date_to_convert)
                    elif LONG_DATE_F_INV.match(date_to_convert):
                        new_date = str(date_to_convert[8:10] + "." +
                                        date_to_convert[5:7] + "." +
                                        date_to_convert[0:4])
                    elif is_null(date_to_convert):
                        new_date = None
                    else:
                        new_date = "WrongFormat"
                dates.append(new_date)

            if not_null(dates):
                for date in dates:
                    if not_null(date):
                        if not LONG_DATE_F.match(date):
                            return "WrongFormat"
                if len(dates) == 1:
                    return dates[0]
                else:
                    return dates
            else:
                return None
        else:
            return None
    except Exception as error:
        logging.info(dates_to_convert)
        print_exception()
        raise RuntimeError("Error while converting date") from error


def norm_data(file):
    """
    Normalize DataFrame to correct format for the different data.

    Parameters
    ----------
    file : DataFrame
        Data to normalize.

    Returns
    -------
    file_normalized : DataFrame
        Data normalized.

    """
    try:
        errors = {}
        # Delete empty row
        file.dropna(how='all', axis='columns', inplace=True)
        file.columns = file.columns.str.replace(".", "_", regex=False)
        # Normalize all accent
        cols = file.select_dtypes(include=[np.object_]).columns
        file[cols] = file[cols].apply(lambda x: (x.astype(str).str.normalize('NFKD')
                                                .str.encode('ascii', errors='ignore')
                                                .str.decode('utf-8')))
        col_present = list(set(file.columns))
        if "NomChien" in col_present:
            file["NomChien"] = file["NomChien"].str.upper()
            file["NomChien"] = file["NomChien"].str.partition("_")[0]
            file["NomChien"] = file["NomChien"].str.partition(" (")[0]
            file["NomChien"] = file["NomChien"].str.partition("(")[0]
            file["NomChien"] = file["NomChien"].str.partition(" 2")[0]
            file["NomChien"] = file["NomChien"].str.partition(" 3")[0]
            file["NomChien"] = file["NomChien"].str.replace(" DITE ", " DIT ")
            file["NomChien"] = file["NomChien"].str.replace("=", " DIT ")
            file["NomChien"] = file["NomChien"].str.replace(" DU CESECAH", "")
            if file["NomChien"].str.contains(" DIT ").any():
                file["NomUsuel_1"] = file["NomChien"].str.split(" DIT ", expand=True)[1]
                file["NomChien"] = file["NomChien"].str.split(" DIT ", expand=True)[0]

        nom_cols = [col for col in col_present if ("NomUsuel" in col or "NomChien" in col)]

        if len(nom_cols) > 0:
            for col in nom_cols:
                file[col] = file[col].str.upper()
                file[col] = file[col].replace(r'\s$', '', regex=True)
                file[col] = file[col].replace(r'^\s', '', regex=True)
            file["AllName"] = file[nom_cols].values.tolist()
            file["AllName"] = file.apply(lambda row: get_not_null(row["AllName"]), axis=1)
            file["NomChien"] = file.apply(lambda row: conca_name(row["AllName"]), axis=1)

        cols_date = [x for x in col_present if "Date" in x]
        for col_date in cols_date:
            if file[col_date].dtypes == "datetime64[ns]":
                file[col_date] = pd.to_datetime(
                    file[col_date]).apply(
                        lambda ts: ts.strftime("%d.%m.%Y")  # type: ignore
                        if not pd.isnull(ts)
                        else "None"
                    )

            file[col_date] = file[col_date].astype(str)
            file[col_date] = file[col_date].replace(r"^\?*$", "", regex=True)
            file[col_date] = file[col_date].replace(r"^0$", None, regex=True)
            file[col_date] = file[col_date].replace(r"\/", ".", regex=True)
            file[col_date] = file[col_date].replace(r"\s", "", regex=True)
            file[col_date] = file[col_date].replace(r"-", ".", regex=True)
            file[col_date] = file[col_date].replace(r"(?<=[\d])et(?=\d)", "_", regex=True)
            file[col_date] = file[col_date].replace(r"[a-zA-Z]+", "", regex=True)
            file[col_date] = file[col_date].replace(r"\(.*\)", "", regex=True)
            file[col_date] = file[col_date].replace(r"^\.", "", regex=True)
            file[str(col_date + "Error")] = file.apply(
                lambda row, col=col_date: date_convert(row[col]), axis=1
            )

            errors_present = file[str(col_date + "Error")].astype(str).str.contains("WrongFormat")
            if any(errors_present):
                errors.update({col_date: error_register(
                    file.loc[errors_present, ["NomChien", col_date, str(col_date + "Error")]]
                )})
                logging.info(str(
                    file.loc[errors_present, ["NomChien", col_date, str(col_date + "Error")]]
                ))
            file[col_date] = file[str(col_date + "Error")]
            del file[str(col_date + "Error")]
            file.loc[errors_present, col_date] = np.NaN

        if "NumIdentification" in col_present:
            file["NumIdentification"] = file["NumIdentification"].replace(r"\.", "", regex=True)
            file["NumIdentification"] = file["NumIdentification"].replace(r"\s", "", regex=True)
            file["NumIdentification"] = file["NumIdentification"].replace(r"\\", "/", regex=True)
            file["NumIdentification"] = file["NumIdentification"].replace(r"\n", "/", regex=True)
            if "Puce" not in col_present and "Tatouage" not in col_present:
                file[["Tatouage", "Puce"]] = file.apply(
                    lambda row: num_id_sep(row["NumIdentification"]),
                    axis=1, result_type='expand'
                )
            else:
                logging.info(
                    "Error, numIdentification present and" +
                    "puce or tatouage also present choose only one"
                )

            errors_present = file["Puce"].astype(str).str.contains("Error")
            if any(errors_present):
                errors.update({
                    "NumIdentification": error_register(
                        file.loc[
                            errors_present,
                            ["NomChien", "NumIdentification", "Puce", "Tatouage"]
                        ]
                    )
                })
                logging.info(str(file.loc[errors_present, ["NomChien", "NumIdentification", "Puce", "Tatouage"]]))
                file.loc[errors_present, ["Puce", "Tatouage"]] = np.NaN
            file["Puce"] = file["Puce"].astype(np.float64)

        if "Puce" in list(set(file.columns)):
            if file["Puce"].dtypes != np.int64 and file["Puce"].dtypes != np.float64:
                file["Puce"] = file["Puce"].astype(str)
                file["Puce"] = file["Puce"].replace(r"\.", "", regex=True)
            file["PuceError"] = file.apply(lambda row: check_puce(row["Puce"]), axis=1)
            errors_present = file["PuceError"].astype(str).str.contains("WrongFormat|Not an int")
            if any(errors_present):
                errors.update({"Puce":
                                error_register(file.loc[errors_present,
                                                        ["NomChien", "Puce", "PuceError"]])})
                logging.info(str(file.loc[errors_present, ["NomChien", "Puce", "PuceError"]]))
                file.loc[errors_present, ["Puce"]] = np.NaN

            file.loc[bool_invert(errors_present), ["PuceError"]] = np.NaN
            file["Puce"] = file["Puce"].astype(np.float64)

        if "Tatouage" in list(set(file.columns)):
            file["Tatouage"] = file["Tatouage"].astype(str).replace(r"\s", "", regex=True)
            file["Tatouage"] = file["Tatouage"].str.upper()
            file["TatouageError"] = file.apply(lambda row: check_tatouage(row["Tatouage"]), axis=1)
            errors_present = file["TatouageError"].astype(str).str.contains("WrongFormat")
            if any(errors_present):
                errors.update({"Tatouage": error_register(
                    file.loc[errors_present,["NomChien", "Tatouage", "TatouageError"]]
                )})
                logging.info(str(file.loc[errors_present, ["NomChien", "Tatouage", "TatouageError"]]))
                file.loc[errors_present, ["Tatouage"]] = np.NaN
            file.loc[bool_invert(errors_present), ["TatouageError"]] = np.NaN

        breed = {'labrador': 'lab',
                'golden': 'gol',
                'goldenretriever': 'gol',
                'goldenrretriever': 'gol',
                "retrievergolden": "gol",
                "goldenrretriver": "gol",
                "gold":"gol",
                'labradorxgolden': 'labxgol',
                'labradorretriever': 'lab',
                'retrieverdulabrador': 'lab',
                'labrador/gr': 'labxgol',
                'lab/gr': 'labxgol',
                'labxgolden': 'labxgol',
                'labxgr': 'labxgol',
                'bergerallemand': 'bergerallemand',
                'goldenxba': 'golxba',
                'flatcoatedret': 'flatcoatedret',
                'flatcoatedretriever': 'flatcoatedret',
                'flatcoated': 'flatcoatedret',
                "setterirlandaisrouge": "setterirlandais",
                "bergerblanc": "bergerblancsuisse",
                "bergersuisse": "bergerblancsuisse",
                "canicheroyal": "caniche",
                "caniche-grand": "caniche",
                "raceindeterminee": "",
                "retrieverapoildurpoilboucle": "curlycoatedret",
                "retrieverapoilboucle": "curlycoatedret",
                "curly-coatedretriever": "curlycoatedret",
                "retrieverapoilplat": "flatcoatedret",
                "flat-coatedretriever":"flatcoatedret",
                "doguedebordeaux": "ddbx",
                "ddb":"ddbx",
                "chiendecouritalien": "canecorso",
                "canecorso(chiendecouritalien)":"canecorso",
                "bmd":"bouvierbernois",
                "bb":"bouvierbernois",
                "bouviersuisse":"grandbouviersuisse",
                "grandbouvier":"grandbouviersuisse",
                "appenzell":"bouvierdelappenzell",
                "bouvierdel'appenzell":"bouvierdelappenzell",
                "bouvierappenzellois":"bouvierdelappenzell",
                "bouvierdel'entlebuch":"bouvierdelentlebuch",
                "entlebuch":"bouvierdelentlebuch",
                "gsd":"bergerallemand"
                }

        if "Race" in col_present:
            file["Race"] = file["Race"].replace(r"\s", "", regex=True)
            file["Race"] = file["Race"].replace(r"\.", "", regex=True)
            file["Race"] = file["Race"].str.lower()
            file["Race"] = file["Race"].replace(r"o_", "c", regex=True)
            file["Race"] = file["Race"].replace(breed)

        sexe = {"femelle": "F", "f": "F",
                "male": "M", "mâle": "M", "m": "M", "nr": np.NaN, "nd": np.NaN}

        if "Sexe" in col_present:
            file["Sexe"] = file["Sexe"].replace(" ", "", regex=True)
            file["Sexe"] = file["Sexe"].str.lower()
            file["Sexe"] = file["Sexe"].replace(sexe)

        num_lof_present = {"oui": "oui", "non": "non", "parents": "parents"}
        num_lof = {"oui/": "","oui": "", "non": "", "parents/": "", "parents": "",
                    "NaN": "", "déjàtransmis": "", "dejatransmis": ""}
        if "NumLof" in col_present:
            try:
                file["NumLof"] = file["NumLof"].astype(str).str.lower()
                file["NumLof"] = file["NumLof"].replace(r"\s", "", regex=True)
                file["NumLof"] = file["NumLof"].replace(":", "")
                file["NumLof"] = file["NumLof"].replace("lof", "", regex=True)
                file["NumLof"] = file["NumLof"].replace("pasdansselect", "", regex=True)
                file["NumLofPresent"] = file["NumLof"].replace(num_lof_present)
                file["NumLof"] = file["NumLof"].replace(r"ls", "losh", regex=True)
                is_losh = file["NumLof"].str.contains('losh')
                if any(is_losh):
                    file["IsLosh"] = None
                    file.loc[is_losh, "IsLosh"] = True
                file["NumLof"] = file["NumLof"].replace("losh", "", regex=True)
                file["NumLof"] = file["NumLof"].replace(" ", "", regex=True)
                file["NumLof"] = file["NumLof"].replace(num_lof, regex=True)
                if any(file["NumLof"].str.contains('/')):
                    file["NumLofConf"] = file["NumLof"].str.split("/", expand=True)[1]
                file["NumLof"] = file["NumLof"].str.split("/", expand=True)[0]

                datas_conv, num_lof_errors = convert_to_num(file["NumLof"],"Int32")
                if any(num_lof_errors):
                    errors.update({"NumLof":
                                    error_register(file.loc[num_lof_errors,
                                                            ["NomChien", "NumLof"]])})
                file["NumLof"] = datas_conv

            except Exception as error:
                print_exception()
                logging.info(file.loc[array_not_null(file["NumLof"]),"NumLof"])
                raise ValueError("Error while normalizing Lof Number") from error

            errors_present = file["NumLof"].astype(str).str.contains("Error")
            if any(errors_present):
                errors.update({"NumLof": error_register(file.loc[errors_present, ["NomChien", "NumLof"]])})
                logging.info(file.loc[errors_present, ["NomChien", "NumLof"]])
                file.loc[errors_present, ["NumLof"]] = np.NaN
        if "NumLof" in col_present and "Race" in col_present:
            file["NumLofRace"] = file["NumLof"].astype(str) + file["Race"]
            file.loc[bool_invert(array_not_null(file["NumLof"])),"NumLofRace"] = "NA"
        dys_cols = [col for col in col_present if re.search(r'Dys[\d]?_', col)]
        for col in dys_cols:
            if col != "Lecteur":
                file[col] = file[col].astype(str)
                file[col] = file[col].str.replace(":", "/")
                file[col] = file[col].str.upper()
                file[col] = file[col].str.replace(" OU ", "_")
                file[col] = file[col].str.replace(" ET ", "_")
                file[col] = file[col].str.replace(" - ", "_")
                file[col] = file[col].str.replace(" ", "")
                file[col] = file[col].str.replace(r"^(NONMESURE|NONEFFECTUE|NONMESURABLE|NM|\?*)$", "None", regex=True)

                if any(file[col].str.contains("_")) and "Infos" not in col and "Parents" not in col:
                    file[[col, str(col + "_1")]] = file[col].str.split("_", expand=True)

        col_present = list(set(file.columns))
        dys_cols = [col for col in col_present if re.search(r'Dys[\d]?_', col)]
        for col in dys_cols:
            if "ID" in col or "NO" in col or "FCI" in col:
                if "_DG" in col:
                    if any(file[col].str.contains("/")):
                        file[[col.replace("_DG", "_D"),
                                col.replace("_DG", "_G")]] = file[col].str.split("/", expand=True)
                        errors_present = np.logical_and([not_null(x) for x in file[col.replace("_DG", "_G")]],
                                                        [is_null(x) for x in file[col.replace("_DG", "_D")]])
                        if any(errors_present):
                            file.loc[errors_present, col.replace("_DG", "_G")] = file.loc[
                                errors_present,col.replace("_DG", "_D")
                            ]
                            errors.update({
                                str(col + "_SepError"): error_register(
                                    file.loc[errors_present,["NomChien", col]]
                                )
                            })
                        del file[col]
                    # elif "FCI" in col:
                        # file[col.replace("_DG", "_G")] = file[col]
                        # file[col.replace("_DG", "_D")] = file[col]
                        # del file[col]

        col_present = list(set(file.columns))
        dys_cols = [col for col in col_present if re.search(r'Dys[\d]?_', col)]
        for col in dys_cols:
            file[col] = file[col].str.replace(">", "")
            file[col] = file[col].str.replace(" ", "")
            if "ID" in col or "NO" in col:
                if "ID" in col :
                    totype = "float64"
                else:
                    totype = "Int32"
                datas_conv, errors_present = convert_to_num(file[col],totype)
                if any(errors_present):
                    errors.update({str(col + "_ToNumError"):
                                    error_register(file.loc[errors_present, ["NomChien", col]])})
                file[col] = datas_conv
            elif "Operation" in col:
                file[col] = file[col].replace(r"SYMPH[^\s]*\b", "Sy", regex=True)
            elif "FCI" in col:
                file[col] = file[col].replace(r"(?<=[A-E])\sOU\s(?=[A-E])", "_", regex=True)
            elif "Lecteur" in col:
                file[col] = file[col].replace(".", "")
                file[col] = file[col].replace("(^DR )|(^D )", "", regex=True)
                file[col] = file[col].replace("(/ACGAO)|(, NON OFFICIEL)", "", regex=True)
                file[col] = file[col].replace(r"\(.*\)", "", regex=True)
                lecteur_replace = {"YVES LIGNEREUX": "LIGNEREUX",
                                    "DIDIER FAU": "FAU",
                                    "SEBASTIEN MIRKOVIC": "MIRKOVIC",
                                    "DIDIER FONTAINE": "FONTAINE"}
                file[col] = file[col].replace(lecteur_replace)
                file[col] = file[col].replace(r"\s", "", regex=True)

        if "NumCaniDNA" in col_present:
            file["NumCaniDNA"] = file["NumCaniDNA"].astype(str).str.lower()
            file["NumCaniDNA"] = file["NumCaniDNA"].str.replace(" ", "")
            file["NumCaniDNA"] = file["NumCaniDNA"].str.replace("-", "/")
            file["NumCaniDNA"] = file["NumCaniDNA"].str.replace("ou", "/")
            file["NumCaniDNA"] = file["NumCaniDNA"].str.replace("et", "/")
            file["NumCaniDNA"] = file["NumCaniDNA"].str.replace(r"^\?*$", "", regex=True)
            file["NumCaniDNA"] = file["NumCaniDNA"].str.replace("pasdesang", "None")
            file["NumCaniDNA"] = file["NumCaniDNA"].str.replace("congele", "None")
            datas_conv, num_cani_dna_errors = convert_to_num(file["NumCaniDNA"],"Int32")
            if any(num_cani_dna_errors):
                errors.update({"NumCaniDNA":
                                error_register(file.loc[num_cani_dna_errors,
                                                        ["NumCaniDNA"]])})
            file["NumCaniDNA"] = datas_conv

        if "AffixeChien" in col_present:
            file["AffixeChien"] = file["AffixeChien"].astype(str).str.replace("/", " ")
            file["AffixeChien"] = file["AffixeChien"].str.lower()
            file["AffixeChien"] = file["AffixeChien"].replace(r"^\s*", "", regex=True)
            file["AffixeChien"] = file["AffixeChien"].replace(r"\s*$", "", regex=True)
            file["AffixeChien"] = file["AffixeChien"].replace(r"^\/du cesecah$|^cesecah$", "du cesecah", regex=True)
            file["AffixeChien"] = file["AffixeChien"].replace(r"\/cesecah", "", regex=True)

        if 'Genotype' in col_present:
            genotype = {
                "0":"non","":"non",'noninforme':"non",
                "oui(2013)":"oui","oui(2014)11534":"oui"}
            file["Genotype"] = file["Genotype"].replace(r"\s", "", regex=True)
            file["Genotype"] = file["Genotype"].str.lower()
            file["Genotype"] = file["Genotype"].replace(genotype)
        if 'TypePuce' in col_present:
            file["TypePuce"] = file["TypePuce"].replace({"0":""})

        return file, errors
    except Exception as error:
        #logging.info(col)
        print_exception()
        raise RuntimeError("Error while normalizing") from error


def convert_to_num(datas, totype="Int32"):
    try:
        datas = datas.astype(str).str.replace(",", ".")
        errors = []
        all_datas = datas.str.split("/", expand=True)
        datas_conv = pd.DataFrame({k: pd.to_numeric(v, errors='coerce')
                                    for k, v in all_datas.items()})

        if totype == "Int32":
            datas_conv = datas_conv.map(np.floor).astype("Int64")

        errors.append(all_datas.map(not_null) & datas_conv.map(is_null))
        errors.append([any(row) for index, row in errors[0].iterrows()])

        all_datas_conv = pd.Series([get_not_null(x) for x in datas_conv.to_numpy()],dtype=object)
        all_datas_conv = pd.Series([np.NaN if is_null(x) else x[0] if len(x) == 1
                                    else x for x in all_datas_conv],dtype=object)
        all_datas_conv.index = datas_conv.index

        return all_datas_conv, errors[1]
    except Exception as error:
        logging.info(datas)
        logging.info(totype)
        print_exception()
        raise TypeError("Error while converting to numeric") from error


def check_columns(file, field_orga):
    """
    Verify if all columns present are present in the organisation.

    Will also check if dysplasia columns name format is correct.

    Parameters
    ----------
    file : TYPE
        DESCRIPTION.
    field_orga : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    try:
        logging.info("Checking Columns")
        file_field = set(file.columns)
        field_names = set(field_orga.loc[field_orga["Category"] != "Dysplasia", "Field"])
        dysplasia_field = set(field_orga.loc[field_orga["Category"] == "Dysplasia", "Field"])
        all_check = []
        for field in file_field:
            fields = field.split(".")
            field = fields[0]
            check = False
            check2 = False
            field_vars = field.split("_")

            if len(field_vars) != 1:  # Should be a dysplasia field
                try:
                    int(field_vars[1])
                    check2 = True

                except ValueError:
                    if field_vars[1] == "NA" or field_vars[1] == "PostOpe" or field_vars[1] == "Lecteur":
                        check2 = True
                    else:
                        logging.info("Second value not correct")
                        check2 = False

                if field_vars[0] in ["Dys", "Dys1", "Dys2", "Dys3"] and check2:
                    if len(field_vars) > 2:
                        if field_vars[2] in dysplasia_field:
                            if len(field_vars) == 4:
                                if field_vars[3] in ["DG", "D", "G"]:
                                    check = check2
                                else:
                                    logging.info("Last field not right")
                                    check = False
                            if len(field_vars) == 3:
                                check = check2
                        else:
                            logging.info("Third field not in authorized values")
                    else:
                        check = bool(field_vars[1] == "Lecteur")
                else:
                    logging.info("First field isn't a dysplasia field")

            else:  # Not a dysplasia field
                if field in field_names or field == "NA":
                    if len(fields) == 2:
                        try:
                            num = int(fields[1])
                            if num > 2:
                                check = bool(field == "NA")
                            else:
                                check = True
                        except ValueError:
                            logging.info("Field not a number")
                            check = False
                    elif len(fields) == 1:
                        check = True
                    else:
                        logging.info("Field is too much separable (_)")
                else:
                    logging.info("Field not separable and not present in possible fields")

            if check is False:
                logging.info(fields)
            all_check.append(check)
        if not all(all_check):
            input("Wait")
    except Exception as error:
        print_exception()
        raise RuntimeError("Error while checking columns") from error


def error_register(df_errors):
    """
    Generate a list with all the errors as independent document.

    Parameters
    ----------
    df_errors : DataFrame
        The DataFrame with all the errors by rows.

    Returns
    -------
    errors : list
        List of dictionnaries of each row of the DataFrame with the index added.

    """
    errors = []
    for index, record in zip(df_errors.to_dict("index"), df_errors.to_dict("records")):
        error = {}
        error.update(record)
        error.update({"Index": index})
        errors.append(error)
    return errors
