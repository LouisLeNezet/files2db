#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 13:00:59 2021

@author: louisln
"""

import pandas as pd
import numpy as np
from datatools import not_null
from datareading import read_file
from normdata import norm_data
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


pathrep = "/Users/louisln/Documents/EnCours/Concatenate/20-06-08_ContenusFichiersNormalise_LLN.xlsx"
rep_file = pd.read_excel(pathrep, sheet_name="Rep")

rep_file = rep_file.loc[
    np.logical_and(rep_file["ToCheck"] == 1, rep_file["ToAdd"] == 1),
]

field_orga = pd.read_excel(pathrep, sheet_name="Field")
values_corres = pd.read_excel(pathrep, sheet_name="Values")
formats_corres = pd.read_excel(pathrep, sheet_name="Formats")
db_orga = {
    "field_orga": field_orga,
    "values_corres": values_corres,
    "formats_corres": formats_corres,
}
db_orga["field_orga"]
colID = list(
    db_orga["field_orga"]
    .loc[db_orga["field_orga"]["Category"] == "Identity", "Field"]
    .values
)
colIDSupl = list(
    db_orga["field_orga"]
    .loc[db_orga["field_orga"]["Category"] == "IdentitySupl", "Field"]
    .values
)
all_col = list(db_orga["field_orga"]["Field"].values)


allData = pd.DataFrame()

for index in rep_file.index:
    file_infos = rep_file.loc[index].copy()
    file_errors = {}
    file_to_skip = False
    file_name = file_infos["NomFichier"]
    file_loc = str(file_infos["Dossier"] + "\\" + file_name)
    file_infos.loc["FileLoc"] = file_loc

    file_path = file_infos["CheminAcces"]

    print(file_name)
    file_data, file_errors = read_file(file_path, "Prep", file_infos, db_orga)

    # colToUse = [col for col in file_data.columns if col in colID+colIDSupl]
    # file_data = file_data[colToUse]

    file_data, file_errors = norm_data(file_data, db_orga)

    # Lecteur
    if not_null(file_infos["Lecteur"]):
        file_data["Dys_Lecteur"] = file_infos["Lecteur"]

    file_data["File"] = file_loc
    allData = pd.concat([allData, file_data])

allData.to_csv(
    "/Users/louisln/Documents/EnCours/Concatenate/PythonScript/ScriptTest/AllID.csv",
    sep=";",
    index_label="Line",
)
