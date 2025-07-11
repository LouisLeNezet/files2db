# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 15:24:44 2021

@author: BUREAU
"""

import pandas as pd
import sys

sys.path.append(
    r"D:\Documents\IGDR-Dysplasie\Normalisation\file-concatenation-to-database\PythonScript"
)
from settings import set_value, init, PARAMS
from normdata2 import norm_data2, data_conv
from datatools import intersect, array_not_null, not_null

init()

set_value("TKINTER_SHOW", False)
set_value(
    "PATH_TO_ORGA",
    r"D:\Documents\IGDR-Dysplasie\Normalisation\file-concatenation-to-database\20-06-08_ContenusFichiersNormalise_LLN.xlsx",
)

file_toadd_path = r"D:\Documents\IGDR-Dysplasie\Normalisation\file-concatenation-to-database\ACGAO_Avt2020\ACGAO-Globaux\ACGAO_C-J_65_SgPdPoDcfCaniDNA.xlsx"
file = pd.read_excel(file_toadd_path, encoding="latin_1", skiprows=[0, 2])

field_orga = pd.read_excel(PARAMS["PATH_TO_ORGA"], sheet_name="Field")
values_corres = pd.read_excel(PARAMS["PATH_TO_ORGA"], sheet_name="Values")
formats_corres = pd.read_excel(PARAMS["PATH_TO_ORGA"], sheet_name="Formats")

db_orga = {
    "field_orga": field_orga,
    "values_corres": values_corres,
    "formats_corres": formats_corres,
}

file2 = norm_data2(file, db_orga)
