# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 13:41:26 2022

@author: BUREAU
"""

import pandas as pd
import sys

sys.path.append("..")

from normdata2 import norm_data2, format_float, nested_serie_test
from settings import set_value, init, PARAMS

init()
# rep = "/Users/louisln/Documents/Dysplasie/Concatenation/file-concatenation-to-database/Test/"
rep = r"D:/Documents/IGDR-Dysplasie/Normalisation/file-concatenation-to-database/Test/"

set_value("TKINTER_SHOW", False)
set_value("PATH_TO_ORGA", rf"{rep}RepTest.xlsx")

file_toadd_path = rf"{rep}TestNorm.xlsx"
columns = pd.read_excel(file_toadd_path, nrows=0).columns
file = pd.read_excel(file_toadd_path, converters={col: format_float for col in columns})

db_field = pd.read_excel(PARAMS["PATH_TO_ORGA"], sheet_name="Fields")
db_corres = pd.read_excel(PARAMS["PATH_TO_ORGA"], sheet_name="Corres")
db_type = pd.read_excel(PARAMS["PATH_TO_ORGA"], sheet_name="Types")

db_orga = {"Fields": db_field, "Corres": db_corres, "Types": db_type}

file_toadd, file_errors = norm_data2(file, db_orga)
