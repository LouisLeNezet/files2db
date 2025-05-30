# -*- coding: utf-8 -*
"""Data management module to use for starting app.

Created on Fri Mar 05 12:45:29 2021
@author: LouisLeNezet
"""
from printconsole import print_exception
from datatools import disjoint, union

def update_dic_dcf(dic, month, type_infos, value, lateralisation, lecturer, file_id):
    """
    Update dysplasia infos present in dictionnary.

    Parameters
    ----------
    dic : Dict
        Dictionnary with dysplasia infos.
    month : Int
        Dog's age in month for the intervention.
    type_infos : String
        Type of infos to insert.
    value : TYPE
        Value of the info to insert.
    lateralisation : String
        Dog's side of the info ("D","G","DG").

    Returns
    -------
    Dict.
        Dictionnary update with the new informations.
    """
    try:
        if month in dic.keys():
            if lecturer in dic[month].keys():
                if type_infos in dic[month][lecturer].keys():
                    if lateralisation is not None:
                        if isinstance(dic[month][lecturer][type_infos], dict):
                            if lateralisation in dic[month][lecturer][type_infos].keys():
                                if value != dic[month][lecturer][type_infos][lateralisation]:
                                    dic[month][lecturer][type_infos][lateralisation] = union(dic[month][lecturer][type_infos][lateralisation], value)
                            else:
                                dic[month][lecturer][type_infos].update(set_value(value, lateralisation))
                        else:
                            dic[month][lecturer][type_infos] = [dic[month][lecturer][type_infos], {lateralisation: value}]
                    else:
                        dic[month][lecturer][type_infos] = union(dic[month][lecturer][type_infos], value)

                else:
                    dic[month][lecturer].update({type_infos: set_value(value, lateralisation)})
            else:
                dic[month][lecturer] = {type_infos: set_value(value, lateralisation)}
        else:
            dic[month] = {lecturer: {type_infos: set_value(value, lateralisation)}}
        if lecturer not in dic[month][lecturer].keys():
            dic[month][lecturer].update({"Lecteur": lecturer})
        if "File" not in dic[month][lecturer].keys():
            dic[month][lecturer].update({"File": file_id})
        else:
            if disjoint(file_id, dic[month][lecturer]["File"]):
                dic[month][lecturer]["File"] = union(dic[month][lecturer]["File"], file_id)
        return dic
    except Exception:
        print_exception()
        print(dic, month, type_infos, value, lateralisation, lecturer, file_id)
        raise Exception("Error while updating dcf dictionnary")


def set_value(value, lateralisation):
    """
    Return a dictionnary for the lateralisation with the value or just the value.

    Parameters
    ----------
    value : TYPE
        Value of the variable.
    lateralisation : Str
        Lateralisation of the variable, if None return only the value.

    Returns
    -------
    TYPE
        Dictionnary or only the value.

    """
    if lateralisation is None:
        return value
    else:
        return {lateralisation: value}
