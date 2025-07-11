# -*- coding: utf-8 -*-
"""
Setting globals variables.

Created on Sat Mar 13 11:44:51 2021

@author: BUREAU
"""

import os

PARAMS = {}


def init():
    """
    Initialize the global variable used through the app.

    Returns
    -------
    None.

    """
    global PARAMS
    if not int(os.path.isfile(r"parameters.txt")):
        file_settings = open(r"parameters.txt", "w+", encoding="utf8")
        file_settings.close()
    with open(r"parameters.txt", "r", encoding="utf8") as file_settings:
        for line in file_settings:
            line_stripped = line.strip().split("=")
            if len(line_stripped) == 2:
                PARAMS[line_stripped[0]] = line_stripped[1]
            else:
                print("Error", line_stripped)
    all_parameters = [
        "GUI_MW",
        "ID_FIELDS",
        "ID_SUPL_FIELDS",
        "TKINTER_SHOW",
        "SHOW_QUERY",
        "DB_NAME",
        "PATH_TO_ORGA",
    ]
    all_defaults = (None, None, None, True, True, "Test", None)
    for param_name, default_value in zip(all_parameters, all_defaults):
        PARAMS[param_name] = get_value(param_name, default_value)


def set_value(name, value):
    """
    Set a value to a global dictionary and update the parameters.txt file.

    Parameters
    ----------
    name : Str
        Name of the variable.
    value : TYPE
        Value of the variable.

    Returns
    -------
    None.

    """
    global PARAMS
    with open(r"parameters.txt", "w", encoding="utf8") as file_settings:
        PARAMS[name] = value
        for name_items, value_items in PARAMS.items():
            file_settings.writelines(str(name_items + "=" + str(value_items) + "\n"))


def get_value(name, default):
    """
    Retrieve variable value.

    If variable present in global dictionary return value present.
    If not insert variable in the parameters.txt file and return default value.

    Parameters
    ----------
    name : Str
        Name of the variable.
    default : TYPE
        Default value of the variable.

    Returns
    -------
    TYPE
        Value of the variable in the global dictionary PARAMS.

    """
    global PARAMS
    if name in PARAMS:
        return PARAMS[name]
    set_value(name, default)
    return default
