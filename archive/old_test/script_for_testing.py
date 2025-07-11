#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script for testing."""


from src.read_file.check_file import read_orga, get_db_from_excel

dct = read_orga(
    "C:\\Users\\llenezet\\Documents\\EnCours\\Concatenate\\PythonScript\\src\\read_file\\file_orga.csv"
)

db = get_db_from_excel(
    "C:\\Users\\llenezet\\Documents\\EnCours\\Concatenate\\2022-11-16_ContenusFichiersNormalise.xlsx",
    dct,
)

a = set(["a", "b"])
b = set(["b", "b", "a"])

print(a.difference(b))
print(b.difference(a))

print(a == b)
