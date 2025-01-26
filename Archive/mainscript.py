# -*- coding: utf-8 -*-
"""
Main script for the app and iteration through all files.

Created on Mon Dec 07 09:30:41 2020

@author: LouisLeNezet
"""

import os
import platform
import re
import pandas as pd
import numpy as np
import settings
from printconsole import print_exception, menu, print_d
from datareading import read_file, get_columns
from datatools import intersect, joint, not_null
from normdata import check_columns
from mongodb import MongoClass
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')


def get_platform_infos():
    """
    Get the information of the running platform.

    Raises
    ------
    Platform not recognize
        The platform where the script is running isn't recognize.

    Returns
    -------
    None.

    """
    try:
        operating_system = platform.uname()[0]
        if operating_system == "Darwin":
            print("You are running on Mac")
        elif operating_system == "Windows":
            print("You are running on Windows")
        else:
            print("Please contact creator !!")
            raise Exception(f"You are running on an unsuported system {operating_system}")
    except Exception():
        print_exception()
        raise Exception("Error while checking platform informations")


def get_id_colums(field_orga):
    """
    Give the columns to use for the identity and suplementary identity infos.

    Parameters
    ----------
    field_orga : Dataframe
        Organisation of the datas.

    Returns
    -------
    None

    """
    settings.PARAMS["ID_FIELDS"] = list(field_orga.loc[field_orga["Category"] == "Identity", "Field"].values)
    settings.PARAMS["ID_SUPL_FIELDS"] = list(field_orga.loc[field_orga["Category"] == "IdentitySupl", "Field"].values)


def main_loop():
    """
    Loop to iterate through all documents.

    Parameters
    ----------
    path_to_use : String
        Path directory to use for the organisation file.

    Raises
    ------
    Exception
        DESCRIPTION.

    Returns
    -------
    None.

    """
    try:
        get_platform_infos()
        database = MongoClass()
        database.connect_db()

        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.width', 1000)
        pd.options.display.float_format = "{:.0f}".format

        task_to_do = 0
        while task_to_do != "Exit":
            task_to_do = menu()
            try:
                if int(os.path.isfile(settings.PARAMS["PATH_TO_ORGA"])) == 1 and task_to_do != "Exit":
                    print_d("The file used for the repertory of the database will be:\n",
                            settings.PARAMS["PATH_TO_ORGA"])
                    rep_file = pd.read_excel(settings.PARAMS["PATH_TO_ORGA"], sheet_name="Rep")
                    rep_file = rep_file.sort_values(by=["ToAdd"], ascending=False, ignore_index=True)
                    rep_file["DateReceptionFichier"] = rep_file["DateReceptionFichier"].astype(str)
                    tot_to_add = sum(rep_file.loc[rep_file["ToAdd"] == 1, "LineEnd"] -
                                     rep_file.loc[rep_file["ToAdd"] == 1, "LineStart"])
                    tot_to_check = sum(rep_file.loc[rep_file["ToCheck"] == 1, "LineEnd"] -
                                       rep_file.loc[rep_file["ToCheck"] == 1, "LineStart"])
                    settings.PARAMS["GUI_MW"].count_orga["ToAdd"]["ValueMax"].set(tot_to_add)
                    settings.PARAMS["GUI_MW"].count_orga["ToCheck"]["ValueMax"].set(tot_to_check)
                    field_orga = pd.read_excel(settings.PARAMS["PATH_TO_ORGA"], sheet_name="Field")
                    values_corres = pd.read_excel(settings.PARAMS["PATH_TO_ORGA"], sheet_name="Values")
                    formats_corres = pd.read_excel(settings.PARAMS["PATH_TO_ORGA"], sheet_name="Formats")
                    db_orga = {"field_orga": field_orga,
                               "values_corres": values_corres,
                               "formats_corres": formats_corres}
                    get_id_colums(db_orga["field_orga"])
                    print_d("Succeed to access repertory file")

                    database.init_vars()

                    if task_to_do == "PrepId":
                        nb_id_min = 2
                    else:
                        nb_id_min = 1

                    if task_to_do in ["AddDatas", "PrepId", "CompareDB", "CheckCols"]:
                        if task_to_do == "CompareDB":
                            rep_file = rep_file.loc[np.logical_and(rep_file["ToCheck"] == 1,
                                                                   rep_file["ToAdd"] == 0), ]
                        else:
                            rep_file = rep_file.loc[np.logical_and(rep_file["ToCheck"] == 1,
                                                                   rep_file["ToAdd"] == 1), ]
                        for index in rep_file.index:
                            file_to_skip, file_data, file_id, file_infos = file_to_use(rep_file.loc[index].copy(),
                                                                                       task_to_do,
                                                                                       database,
                                                                                       db_orga)
                            print(file_infos["FileLoc"])
                            settings.PARAMS["GUI_MW"].update_pb(index+1, max(rep_file.index)+1, "files",
                                                                file_infos["FileLoc"])
                            if file_to_skip:
                                continue

                            if task_to_do == "CheckCols":
                                check_columns(file_data, db_orga["field_orga"])
                                database.update_doc("Files", {"_id": file_id}, {"CheckColsDone": True})

                            elif task_to_do in ["AddDatas", "PrepId", "CompareDB"]:
                                print_d("Will iterate through file")
                                # Iterate through the lines to check for each dog
                                for index_dog, dog_file_data in file_data.iterrows():
                                    settings.PARAMS["GUI_MW"].update_pb(index_dog+1, max(file_data.index)+1,
                                                                        "datas")
                                    line = int(index_dog + file_infos.loc["LineStart"])
                                    result = dog_register(dog_file_data,
                                                          file_id, file_infos["FileLoc"],
                                                          line,
                                                          nb_id_min, False,
                                                          file_infos["ToAdd"] == 1,
                                                          database, task_to_do,
                                                          lecteur=file_infos["Lecteur"])
                                    settings.PARAMS["GUI_MW"].update_count_label(result, task_to_do)
                                if task_to_do == "PrepId":
                                    database.update_doc("Files", {"_id": file_id}, {"PrepIdDone": True})
                                elif task_to_do == "AddDatas":
                                    database.update_doc("Files", {"_id": file_id}, {"AddDatasDone": True})
                                elif task_to_do == "CompareDB":
                                    database.update_doc("Files", {"_id": file_id}, {"CompareDBDone": True})
                                else:
                                    raise Exception("Fatal Error, shouldn't access here")
                    elif task_to_do == "AddMissingID":
                        iterate_data(database, "DatasNoID", 1, False, task_to_do)
                    elif task_to_do == "CheckErrors":
                        iterate_data(database, "DatasToCheck", 1, False, task_to_do)
                        iterate_data(database, "DatasToCheck", 1, True, task_to_do)
                    else:
                        raise Exception("Task_to_do not recognize")

                elif task_to_do == "Exit":
                    print_d("End of the script")
                else:
                    print_d(str("Couldn't access organisation file:\n" + settings.PARAMS["PATH_TO_ORGA"] +
                                "\nPlease make sure the file is present"))

            except Exception:
                print_exception()
                raise Exception("Error while main loop")

    except Exception:
        print_exception()
        print_d("End")

    finally:
        database.quit_db()


def dog_register(dog_file_data,
                 file_id, file_loc, line,
                 nb_id_min, ask_user,
                 new_dog_toadd,
                 database, task_to_do,
                 lecteur):
    """
    Control for the result of the dog comparison to the database.

    Update or insert the dog inside the database with its infos.
    Register errors and modifications done to the datas.

    Parameters
    ----------
    dog_file_data : Series
        All file's data about the dog.
    file_id : ObjectID
        Identification number of the file inside the database.
    file_loc : String
        Localisation of the file.
    line : Int
        Dog's line inside the file.
    nb_id_min : Int
        Minimal number of identity columns required to asser identity.
    ask_user : Boolean
        Should the user be asked to correct the errors.
    new_dog_toadd : Boolean
        Should the new dog found be add to the database.
    database : MongoClass
        Object to interact with the databse.
    task_to_do : String
        Type of task to do (CheckCols, PrepId, AddDatas).

    Returns
    -------
    result : String
        Result of the comparison to the database (Error, Insertion, Update).

    """
    try:
        if("NomChien" not in dog_file_data.keys()):
            print("Error dog data doesn't have a name")
            return ["CheckLater"]

        dog_file_name = dog_file_data["NomChien"]
        dog_file_data = dog_file_data.dropna()
        dog_file_id_col = list(set(settings.PARAMS["ID_FIELDS"]).intersection(
            set(dog_file_data.index)))
        dog_file_id_supl_col = list(set(settings.PARAMS["ID_SUPL_FIELDS"]).intersection(
            set(dog_file_data.index)))

        errors, dog_id, modifs_id, check_later = database.get_dog_id(dog_file_data,
                                                                     dog_file_id_col,
                                                                     dog_file_id_supl_col,
                                                                     nb_id_min, ask_user,
                                                                     task_to_do)
        data_to_add_id = dog_file_data[dog_file_id_col +
                                       dog_file_id_supl_col].to_dict()
        data_to_add_id["File"] = file_id
        result = []

        if len(errors) == 0 and dog_id is not None:
            if check_later and task_to_do != "CheckErrors": # DatasToCheck
                datas_to_check = dog_file_data.to_dict()
                datas_to_check["File"] = file_id
                datas_to_check["Line"] = line
                datas_to_check["FileLoc"] = file_loc
                database.new_datas_to_register(datas_to_check, "DatasToCheck")
                result.append("new_DatasToCheck")
            elif check_later and task_to_do == "CheckErrors":
                result.append("CheckLater")
            else:
                if dog_id == "NeedNew" and new_dog_toadd: # Need to create new dog
                    dog_insert = database.insert_newdog(data_to_add_id)
                    if dog_insert.acknowledged:
                        dog_id = dog_insert.inserted_id
                        #print_d(str("New dog inserted: " + str(dog_id)))
                        result.append("Inserted")
                    else:
                        #print_d(str("Error" + str(dog_insert)))
                        raise Exception("Insertion not acknowledged")

                elif isinstance(dog_id, bson.objectid.ObjectId): # Dog to update
                    #print_d(str("Update: " + str(dog_id)))
                    database.update_dog(dog_id, data_to_add_id)
                    result.append("Updated")
                elif dog_id != "NeedNew": # Wrong id given
                    print_d(str("Error, dog id given not in the right format " +
                                str(dog_id) + " " + str(type(dog_id))))
                    raise Exception("Error dog_id not correct")

                if modifs_id != []:
                    database.new_modif(file_loc, line, dog_id,
                                       dog_file_name, modifs_id)
                    result.append("new_Modif")
                if task_to_do == "AddDatas" and new_dog_toadd: # Add 
                    database.insert_dysplasia_data(dog_id, dog_file_data, file_id, lecteur)

        elif dog_id is None:  # dog_id is None,script didn't generate a dog_id
            print_d(str("Error, dog_id get is None" + str(dog_id) + " " + type(dog_id)))
            raise Exception("Dog id is none, shouldn't be possible")
        else:
            if (len(errors) > 1 or errors != [{'Message': "Not enough data to check"}]):
                database.new_error(file_loc, line, dog_file_name, errors)
                #print_d(str("An error as occured for line " + str(line) + str(errors)))
                result.append("new_Error")
            elif errors == [{'Message': "Not enough data to check"}]:
                if task_to_do == "PrepId":
                    #print_d("Not enough data to check")
                    result.append("NotEnoughIDData but PrepID")
                elif task_to_do in ["AddDatas", "CompareDB"]:
                    datas_no_id = dog_file_data.to_dict()
                    datas_no_id["File"] = file_id
                    datas_no_id["Line"] = line
                    datas_no_id["FileLoc"] = file_loc
                    database.new_datas_to_register(datas_no_id, "DatasNoID")
                    result.append("new_NotEnoughIDData")
                elif task_to_do in ["CheckErrors", "AddMissingID"]:
                    result.append("CheckLater")
                else:
                    print_d("Shouldn't access here: Task to do not recognize")
                    print_d(errors)
                    raise Exception()
            else:
                print_d("Shouldn't access here")
                print_d(errors)
                raise Exception()
        return result
    except Exception:
        print_exception()
        raise Exception("Fatal Error dog registering")


def file_to_use(file_infos, task_to_do, database, db_orga):
    """
    Control the file usage inside the database and read it.

    If the file already has be used for the task to do, then the file will be skipped.
    The file is added in the database if it isn't already present.

    Parameters
    ----------
    file_infos : Series
        All infos about the file to add.
    task_to_do : String
        Type of task to do (CheckCols, PrepId, AddDatas).
    database : MongoClass
        Object to use to interact with the mongo database.

    Raises
    ------
    File not inserted
        The file's infos couldn't be inserted inside the database.

    Returns
    -------
    file_to_skip : Boolean
        Is the current file to skip.
    file_data : Dataframe
        All datas present in the file to use.
    file_id : ObjectID
        Identification number to the file in the file collection of the database.
    file_infos : Series
        All informations about the file to use.

    """
    try:
        file_errors = {}
        file_to_skip = False
        file_name = file_infos["NomFichier"]
        file_loc = str(file_infos["Dossier"] + "\\" + file_name)
        file_infos.loc["FileLoc"] = file_loc
        file_path = file_infos["CheminAcces"]
        db_file_count = database.count("Files",
                                       {"NomFichier": file_name})
        if db_file_count == 1:
            db_file = database.find("Files",
                                    {"NomFichier": file_name},
                                    "one")
            file_id = db_file["_id"]
            if db_file["CheckColsDone"] is True and task_to_do == "CheckCols":
                print_d(str(file_loc + " File columns already checked"))
                file_to_skip = True
            elif db_file["PrepIdDone"] is True and task_to_do == "PrepId":
                print_d(str(file_loc + " File id already added to database"))
                file_to_skip = True
            elif db_file["AddDatasDone"] is True and task_to_do == "AddDatas":
                print_d(str(file_loc + " File datas already added to database"))
                file_to_skip = True
            elif db_file["CompareDBDone"] is True and task_to_do == "CompareDB":
                print_d(str(file_loc + " datas already compare to database"))
                file_to_skip = True
            else:
                print_d(str(file_loc + " Hasn't be used for this operation yet"))

        elif db_file_count == 0 and file_infos["ToCheck"] == 1:
            print_d(str(file_loc + " File not used yet"))
            file_infos_todb = {}
            for key in file_infos.index:
                if not_null(file_infos[key]):
                    file_infos_todb.update({key: file_infos[key]})
            file_infos_todb.update({"CheckColsDone": False,
                                    "PrepIdDone": False,
                                    "AddDatasDone": False,
                                    "CompareDBDone": False})
            file_insert = database.update_doc("Files",
                                              {"NomFichier": file_name},
                                              file_infos_todb, upsert=True)
            if file_insert.acknowledged:
                file_id = file_insert.upserted_id
            else:
                raise Exception("File not inserted")
        else:
            if db_file_count > 1:
                raise Exception("Error multiple same file")
            elif file_infos["ToCheck"] == 0:
                print_d(str(file_loc + " File not to use"))
                file_to_skip = True
            else:
                raise Exception("Fatal error, shouldn't access here")

        if file_to_skip is False:
            file_data, file_errors = read_file(file_path, task_to_do, file_infos, db_orga)
            if file_errors != {}:
                if database.count("FilesNormErrors", {"_id": ObjectId(file_id)}) == 0:
                    file_errors["File"] = file_id
                    file_errors["FileLoc"] = file_loc
                    database.new_datas_to_register(file_errors, "FilesNormErrors")

        else:
            file_data = None
            file_id = None
        return file_to_skip, file_data, file_id, file_infos
    except Exception:
        print_exception()
        raise Exception


def iterate_data(database, data_name, nb_min_id, ask_user, task_to_do):
    """
    Iterate through MongoDB collection and check for dog correspondancies.

    Parameters
    ----------
    database : MongoClass
        MongoClass to use as a database.
    data_name : Str
        Collection name to iterate through.
    nb_min_id : int
        Minimal number of identity value to be present for identification.
    ask_user : Boolean
        Does the user need to be asked an error occured.
    task_to_do : Str
        Name of the task to do.

    Raises
    ------
    Exception
        Access error.

    Returns
    -------
    None.

    """
    try:
        print_d(str("----------------Now iterating through " + data_name + "----------------"))
        nb_docs = database.count(data_name, {})
        print_d(str(str(nb_docs) + " " + data_name + " documents found"))
        docs_cursor = database.find(data_name, {}, "all")
        index_doc = 1
        settings.PARAMS["GUI_MW"].update_pb(1, 1, "files",
                                            data_name)
        for doc in docs_cursor:
            settings.PARAMS["GUI_MW"].update_pb(index_doc, nb_docs, "datas")
            print_d(str(data_name) + " " + str(index_doc) + "/" + str(nb_docs))
            file_id = doc["File"]
            file_loc = doc["FileLoc"]
            line = doc["Line"]
            doc_data = pd.Series({key: doc[key] for key in doc.keys()
                                  if key not in {"File", "Line", "_id", "FileLoc"}})
            file_infos = database.find("Files", {"_id": ObjectId(file_id)}, "one")
            if "Lecteur" in file_infos.keys():
                lecteur = file_infos["Lecteur"]
            else:
                lecteur = None
            result = dog_register(doc_data,
                                  file_id, file_loc, line,
                                  nb_min_id, ask_user,
                                  True,
                                  database, task_to_do=task_to_do,
                                  lecteur=lecteur)
            if result == ["new_Error"]:
                print("Error still present")
            elif result == ["CheckLater"]:
                print("Need to be checked by user")
            elif joint(result, ["Inserted", "Updated","new_DatasToCheck"]):
                print_d(str("A new dog has been " + intersect(result, ["Inserted", "Updated","new_DatasToCheck"])[0].lower()))
                database.delete(data_name, {"_id": doc["_id"]}, many="one")
                result.append(str("del_" + data_name))
            elif result != [str("new_" + data_name)]:
                print_d(str(data_name))
                print_d(str("Result of error checking" + str(result)))
                raise Exception("Error while error checking, shouldn't access here")

            if result != str("new_" + data_name):
                settings.PARAMS["GUI_MW"].update_count_label(result, task_to_do)
            index_doc = index_doc + 1
    except Exception:
        print_exception()
        raise Exception("Error while error checking")
