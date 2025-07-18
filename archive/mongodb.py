# -*- coding: utf-8 -*-

"""MongoDB module to create and use mongo database.

Created on Tue Jan 19 13:15:22 2021
@author: LouisLeNezet
"""

from pymongo import MongoClient
from pymongo import errors as pyMongoErrors
from bson.objectid import ObjectId
import numpy as np
import pandas as pd
import settings
from printconsole import print_exception, question_to_user, print_d
from datatools import difference, intersect, union
from datatools import size_diff, joint, not_null, bool_invert, is_null, get_not_null
from data_management import update_dic_dcf


class MongoClass:
    """Class to create and use a mongo database."""

    def __init__(self):
        self.client = None
        self.vars = {}
        self.my_db = None
        self.collection_present = None

    def init_vars(self):
        """Initialise the variable Fields, when Excel data has been updated."""
        self.vars["IdFields"] = settings.PARAMS["ID_FIELDS"]
        self.vars["IdSuplFields"] = settings.PARAMS["ID_SUPL_FIELDS"]
        settings.PARAMS["GUI_MW"].count_orga["Identity"]["Value"].set(
            self.count("Identity", {})
        )
        settings.PARAMS["GUI_MW"].count_orga["DatasToCheck"]["Value"].set(
            self.count("DatasToCheck", {})
        )
        settings.PARAMS["GUI_MW"].count_orga["DatasNoID"]["Value"].set(
            self.count("DatasNoID", {})
        )
        settings.PARAMS["GUI_MW"].count_orga["Errors"]["Value"].set(
            self.count("Errors", {})
        )
        settings.PARAMS["GUI_MW"].count_orga["Modifs"]["Value"].set(
            self.count("Modifs", {})
        )

    def connect_db(self):
        """Set MongoDB connection and help user to choose beetween using, or replace database.

        Parameters
        ----------
        db_name : String
            Name of the database to use.

        Raises
        ------
        Serveur
            Couldn't access to the server.
        User
            User choices couldn't permit use of database.
        """
        try:
            print_d("Connecting to MongoDB")
            self.client = MongoClient(
                "mongodb://localhost:27017/", serverSelectionTimeoutMS=5 * 1000
            )

            db_name = settings.PARAMS["DB_NAME"]
            self.vars["errors"] = []
            all_db = self.client.list_database_names()
            print_d(all_db)
            if db_name in all_db:
                use_old_db = question_to_user(
                    str(
                        "The database: "
                        + db_name
                        + " already exist do you want to use it ?"
                    )
                )
                if use_old_db:
                    self.use_db()
                    collection_present = self.my_db.list_collection_names()
                    print_d(
                        str(
                            "The following collection(s) already exist \n"
                            + str(collection_present)
                        )
                    )
                else:
                    delete_db = question_to_user("Do you want to replace it ?")
                    if delete_db:
                        print_d(
                            str(
                                "The database "
                                + db_name
                                + " will therefore be deleted and replaced by an empty one"
                            )
                        )
                        self.client.drop_database(db_name)
                        self.use_db()
                    else:
                        raise Exception(
                            "Exiting script due to presence of old database",
                            db_name,
                            "and no use or deletion of if",
                        )
            else:
                print_d(str("Your database: " + db_name + " is not present"))
                create = question_to_user("Do you want to create it ?")
                if create:
                    self.use_db()
                else:
                    raise Exception(
                        "Exiting script due to absence of database and no creation of it"
                    )
        except pyMongoErrors.ServerSelectionTimeoutError as err:
            print_d(str("Server not started: " + str(err)))
            print_d("Please activate the MongoDB server service before continuing")
            raise Exception("Server error, time out exception")
        except Exception:
            print_exception()
            raise Exception("Fatal error connect_db")

    def use_db(self):
        """Create or select database based on db_name registered.

        Returns
        -------
        None.

        """
        self.my_db = self.client[settings.PARAMS["DB_NAME"]]
        # myIDCol=self.myDB["Identity"]
        # myIDCol.create_index("Puce",unique=True,partialFilterExpression = {"Puce":None})
        # myIDCol.create_index("Tatouage",unique=True,partialFilterExpression = {"Tatouage":None})

    def count(self, collection, query):
        """
        Count the number of documents in a specific collection.

        Parameters
        ----------
        collection : String
            Name of the collection.
        query : Dict
            Query to filter the document.

        Returns
        -------
        Number of documents present in database.

        """
        return self.my_db[collection].count_documents(query)

    def find(self, collection, query, many="all"):
        """
        Find the documents in a specific collection.

        Parameters
        ----------
        collection : String
            Name of the collection.
        query : Dict
            Query to filter the document.
        many : String
            How many documents should be provided (one or all). Default is "all"

        Returns
        -------
        Documents present in database corresponding to the query.

        """
        if many == "all":
            return self.my_db[collection].find(query)
        elif many == "one":
            return self.my_db[collection].find_one(query)
        else:
            print_d("Error, argument 'many' given not recognize", many)
            raise Exception("Fatal error db.find")

    def delete(self, collection, query, many="one"):
        """
        Delete one document or many of them in a collection based on a query.

        Parameters
        ----------
        collection : String
            Name of the collection.
        query : Dict
            Query to filter the document.
        many : String
            Does only one document need to be deleted (Default: "one") or many of them.
            If only one to delete an error will be throwed if more than one document is found.

        Returns
        -------
        PyMongoDeleteOneResult
            Result of the documents deletion.

        """
        if many == "one":
            nb_doc_to_delete = self.count(collection, query)
            if nb_doc_to_delete == 1:
                return self.my_db[collection].delete_one(query)
            elif nb_doc_to_delete == 0:
                raise Exception("No document found to delete")
            else:
                raise Exception("Query corresponding to more than one document")
        elif many == "many":
            return self.my_db[collection].delete_many(query)
        else:
            raise Exception("Argument many not recognize")

    def get_dog_id(
        self,
        dog_to_add_infos,
        file_id_col,
        file_idsupl_col,
        nb_id_min,
        ask_user,
        task_to_do,
    ):
        """Search for the dog_id if present in the dataBase based on the data present in the file.

        Parameters
        ----------
        dog_to_add_infos : Serie
            All dog's infos inside the Excel.
        file_id_col : List
            Identity columns to used.
        file_idsupl_col : List
            Suplementary columns to used for further verification.
        nb_id_min : Int
            Number of identity variable to be present for checking the identity
        ask_user : Boolean
            Should a dialog be prompt to ask confirmation by the user.

        Returns
        -------
        errors_get : Array
            All errors obtained during processing.
        dog_id : ObjectId
            Identifier of the correct dog found.
        modifs_get : Array
            All modifications obtained during processing.

        """
        try:
            # Store query and informations available
            query_or = {"$or": []}
            query_and = {"$and": []}
            query_all_and = {"$and": []}

            errors_get = []
            modifs_get = []
            dog_id = None
            check_later = False

            for id_infos in union(file_id_col, file_idsupl_col):
                if not_null(dog_to_add_infos[id_infos]):
                    if isinstance(dog_to_add_infos[id_infos], list):
                        query_to_append = {"$or": []}
                        for value in dog_to_add_infos[id_infos]:
                            query_to_append["$or"].append({id_infos: value})
                    else:
                        query_to_append = {id_infos: dog_to_add_infos[id_infos]}
                    if id_infos in file_id_col:
                        query_and["$and"].append(query_to_append)
                        if id_infos != "DateNaissance":
                            query_or["$or"].append(query_to_append)
                    query_all_and["$and"].append(query_to_append)

            if (
                len(query_and["$and"]) > nb_id_min
            ):  # If not enough key to check try by query_or
                count_and = self.my_db["Identity"].count_documents(query_and)
                if count_and == 1:
                    # print_d("Exact match")
                    dog_db = self.my_db["Identity"].find_one(query_and)
                    dog_id = dog_db["_id"]

                elif count_and > 1:
                    errors_get.append("Error duplicate exact data present in DataBase")
                    dog_id = "Error_Check"
                    # input("Wait: Error duplicate exact data present in DataBase")
                    # raise Exception(str("Duplicate data found for " + str(query_and)))
                # else:
                # print_d("No dogs found with the $and query")
                # print_d(query_and)
            else:
                print_d(
                    "Not enough id fields to check by $and query", to_print=ask_user
                )

            if (
                len(query_or["$or"]) > nb_id_min - 1 and dog_id is None
            ):  # QueryAnd did not produce result
                count_or = self.my_db["Identity"].count_documents(query_or)
                print_d(
                    str(
                        str(count_or)
                        + " dogs have at least one corresponding data for their id fields"
                    ),
                    to_print=ask_user,
                )
                if count_or == 0:
                    dog_id = "NeedNew"
                else:
                    dogs_db_find = self.my_db["Identity"].find(query_or)
                    dogs_db_check = {}
                    for dog_db in dogs_db_find:
                        dog_db_check, modif_get, error_get = self.check_dogs(
                            dog_db,
                            dog_to_add_infos,
                            file_id_col,
                            file_idsupl_col,
                            ask_user,
                        )
                        dogs_db_check[dog_db["_id"]] = dog_db_check

                        if dog_db_check == "Error":
                            if error_get == {"Message": "Need to be check later"}:
                                check_later = True
                            else:
                                errors_get.append(error_get)
                            dog_id = "Error_Check"

                        if modif_get != {}:
                            modifs_get.append(modif_get)

                    dog_to_upd = sum(
                        1 for result in dogs_db_check.values() if result == "UpD"
                    )
                    dog_dif = sum(
                        1 for result in dogs_db_check.values() if result == "Dif"
                    )
                    dog_errors = sum(
                        1 for result in dogs_db_check.values() if result == "Error"
                    )

                    if (
                        dog_to_upd == 1 and dog_errors == 0
                    ):  # Only one dog correct to update
                        dog_id = list(dogs_db_check.keys())[
                            list(dogs_db_check.values()).index("UpD")
                        ]
                    elif (
                        dog_dif == count_or and dog_errors == 0
                    ):  # All dogs are different
                        dog_id = "NeedNew"
                    else:
                        if (
                            dog_to_upd > 1 and dog_errors == 0
                        ):  # Too much dog corresponding
                            errors_get.append(
                                "Error too much dog corresponding to request"
                            )
                        dog_id = "Error_NbSup"
                        # print_d("Dog won't be updated")

                    result = {
                        "NumUpD": dog_to_upd,
                        "NumDif:": dog_dif,
                        "NumTotal:": count_or,
                        "NumErrors:": dog_errors,
                    }
                    print_d(
                        str(
                            "\n Result: \n"
                            + str(dogs_db_check)
                            + "\n"
                            + str(errors_get)
                        ),
                        to_print=ask_user,
                    )
                    print_d(str(result), to_print=ask_user)

            if len(query_or["$or"]) <= nb_id_min - 1:
                if task_to_do == "AddMissingID":
                    count_all_and = self.my_db["Identity"].count_documents(
                        query_all_and
                    )
                    if count_all_and == 1:
                        # print_d("Exact match")
                        dog_db = self.my_db["Identity"].find_one(query_all_and)
                        dog_id = dog_db["_id"]
                    elif count_all_and == 0:
                        errors_get.append({"Message": "No corresponding data"})
                        dog_id = "Error_2"
                    elif count_all_and > 1:
                        errors_get.append(
                            {"Message": "Too much individuals correponding"}
                        )
                        dog_id = "Error_3"
                else:
                    errors_get.append({"Message": "Not enough data to check"})
                    dog_id = "Error_4"

            return errors_get, dog_id, modifs_get, check_later
        except Exception:
            print_exception()
            raise Exception("A fatal error has happened")

    def check_dogs(self, dog_db, dog_file_infos, dog_id_col, dog_id_supl_col, ask_user):
        """Compare dog's identity from file to dog from database and certified equality.

        Parameters
        ----------
        dog_db : Bson
            All dog's info from database found.
        dog_file_infos : Serie
            All dog's info from file.
        dog_id_col : Array
            Identity column to used.
        dog_id_supl_col : Array
            Suplementary identity column to used.
        ask_user : Boolean
            Should a dialog be prompt to ask confirmation by the user.

        Returns
        -------
        check_result : String
            Result UpD = dog to update, Dif = not the same dog, Error.
        modifs_check : TYPE
            All modifications that happened.
        errors_check : TYPE
            All errors that happened.

        """
        try:
            # Dataframe preparation to compare
            dog_db_id_keys = intersect(dog_db.keys(), self.vars["IdFields"])
            dog_db_id_supl_keys = intersect(dog_db.keys(), self.vars["IdSuplFields"])
            dog_db_all_id_keys = union(dog_db_id_keys, dog_db_id_supl_keys)

            dog_file_id_keys = list(dog_file_infos[dog_id_col].keys())
            dog_file_id_supl_keys = list(dog_file_infos[dog_id_supl_col].keys())
            dog_file_all_id_keys = union(dog_file_id_keys, dog_file_id_supl_keys)

            # allIdKeys=union(dog_file_id_keys,dog_db_id_keys)
            # allIdSuplKeys=union(dog_file_id_supl_keys,dog_db_id_supl_keys)

            common_id_keys = intersect(dog_file_id_keys, dog_db_id_keys)
            common_id_supl_keys = intersect(dog_file_id_supl_keys, dog_db_id_supl_keys)
            common_all_keys = union(common_id_keys, common_id_supl_keys)

            dog_file_s = pd.Series(dog_file_infos, name="DogFile")[dog_file_all_id_keys]
            dog_db_s = pd.Series(dog_db, name="DogDB")[dog_db_all_id_keys]
            df_c = pd.concat((dog_file_s, dog_db_s), axis=1, join="inner")

            df_c["SizeDiff"], df_c["Diff"], df_c["Equal"], df_c["Intersect"] = [
                None,
                None,
                None,
                None,
            ]
            df_c["SizeDiff"] = df_c["SizeDiff"].astype("object")
            df_c["Diff"] = df_c["Diff"].astype("object")

            for key in df_c.index.values:
                # Get value different to DB
                try:
                    df_c.at[key, "Equal"] = joint(
                        df_c.at[key, "DogFile"], df_c.at[key, "DogDB"], True
                    )
                    if (
                        len(
                            difference(
                                df_c.at[key, "DogFile"], df_c.at[key, "DogDB"], True
                            )
                        )
                        > 0
                    ):
                        df_c.at[key, "Intersect"] = intersect(
                            df_c.at[key, "DogFile"], df_c.at[key, "DogDB"], True
                        )
                        df_c.at[key, "Diff"] = difference(
                            df_c.at[key, "DogFile"], df_c.at[key, "DogDB"], True
                        )
                        df_c.at[key, "SizeDiff"] = size_diff(
                            df_c.at[key, "DogFile"], df_c.at[key, "DogDB"], True
                        )
                except Exception:
                    print_d(df_c)
                    print_d(
                        str(
                            "Joint: "
                            + str(
                                joint(
                                    df_c.at[key, "DogFile"], df_c.at[key, "DogDB"], True
                                )
                            )
                        )
                    )
                    print_d(
                        str(
                            "Intersect: "
                            + str(
                                intersect(
                                    df_c.at[key, "DogFile"], df_c.at[key, "DogDB"], True
                                )
                            )
                        )
                    )
                    print_d(
                        str(
                            "Difference: "
                            + str(
                                difference(
                                    df_c.at[key, "DogFile"], df_c.at[key, "DogDB"], True
                                )
                            )
                        )
                    )
                    print_d(str("Key error: " + key + " in " + str(common_all_keys)))
                    print_d(
                        str(
                            "Creation df_c failed: "
                            + str(df_c.at[key, "DogFile"])
                            + str(df_c.at[key, "DogDB"])
                        )
                    )
                    print_exception()
                    raise Exception("A fatal error as occured")

            check_result = []
            modif_check = {}
            error_check = {}

            if df_c["Equal"].all() and len(common_id_keys) > 1:  # All data are the same
                # print_d("It seems to be the same dog for")
                check_result.append("UpD")

            elif len(common_all_keys) > 1:  # Difference in values present
                print_d("--------------Need to check--------------", to_print=ask_user)
                df_c["OneInfLim"] = df_c["SizeDiff"].apply(
                    lambda row: False if row is None else min(list(row)) < 21
                )
                print_d(str(df_c), to_print=ask_user)

                dif = df_c.loc[bool_invert(df_c["OneInfLim"]),].index.tolist()
                similar = df_c.loc[df_c["OneInfLim"],].index.tolist()
                dif_id = intersect(dif, common_id_keys)
                similar_id = intersect(similar, common_id_keys)
                all_fields = union(dif, similar)
                print_d(str("Difference spotted for: " + str(dif)), to_print=ask_user)
                print_d(
                    str("Similarity present for: " + str(similar)), to_print=ask_user
                )
                if len(dif) > 0:
                    # Difference still present after threshold
                    if len(dif) == 1:
                        print_d(
                            str("Only the " + str(dif) + " is different"),
                            to_print=ask_user,
                        )
                        if len(common_id_keys) > 1:
                            if len(difference(common_id_keys, similar_id)) == 0:
                                print_d(
                                    "All id fields are true, should be the same dog",
                                    to_print=ask_user,
                                )
                                check_result.append("UpD")
                            else:
                                print_d(
                                    "Not all id fields are true, need to be checked",
                                    to_print=ask_user,
                                )
                        else:
                            print_d(
                                "Not enough id fields to conclude", to_print=ask_user
                            )
                        # input("Wait")

                    if len(check_result) == 0:
                        if (
                            all(
                                [x in dif_id for x in common_id_keys if x != "NomChien"]
                            )
                            and len(dif_id) > 1
                        ):
                            print_d(
                                str(
                                    "All ID fields different (Name not take into account) "
                                    + "it's seems to be different dog"
                                ),
                                to_print=ask_user,
                            )
                            check_result.append("Dif")

                        if (
                            not_null(similar_id)
                            and not_null(common_id_keys)
                            and all(
                                [
                                    x in similar_id
                                    for x in common_id_keys
                                    if x != "NomChien"
                                ]
                            )
                            and len(similar_id) > 1
                        ):
                            print_d(
                                str(
                                    "All ID fields are similar (Name not take into account) "
                                    + "it's seems to be the same dog"
                                ),
                                to_print=ask_user,
                            )
                            check_result.append("UpD")

                        # Only the lof number is similar and race are not equal
                        if (
                            similar_id == ["NumLof"]
                            and len(dif_id) > 1
                            and ("Race" in dif or "Race" not in all_fields)
                        ):
                            print_d(
                                "Only the lof number is similar and the race are different"
                            )
                            check_result.append("Dif")

                        if (
                            len(difference(common_id_keys, dif)) == 0
                            and len(dif_id) > 1
                        ):
                            print_d("Dif: Should be dif", to_print=ask_user)
                        else:
                            if len(difference(common_id_keys, dif)) > 0:
                                print_d("Dif: Not all ID field dif", to_print=ask_user)
                            if len(dif_id) == 0:
                                print_d("Dif: No Id field dif", to_print=ask_user)

                        if (
                            not_null(similar_id)
                            and len(difference(common_id_keys, similar)) == 0
                            and len(similar_id) > 1
                        ):
                            print_d("UpD: Should be UpD", to_print=ask_user)
                        else:
                            if len(difference(common_id_keys, similar)) > 0:
                                print_d(
                                    "UpD: Not all ID field similar", to_print=ask_user
                                )
                            if is_null(similar_id) or len(similar_id) == 0:
                                print_d("UpD: No Id field similar", to_print=ask_user)

                        if ask_user and len(check_result) == 0:
                            same_dog = question_to_user("Is it the same dog", 2)
                            if same_dog != "Error":
                                if same_dog:
                                    check_result.append("UpD")
                                    modif_check["Message"] = str(
                                        "Data "
                                        + ", ".join(dif)
                                        + " will be added to "
                                        + str(dog_db["NomChien"])
                                    )
                                else:
                                    modif_check["Message"] = str(
                                        "Datas are from a different dog "
                                        + str(dog_db["NomChien"])
                                        + " defined by User"
                                    )
                                    check_result.append("Dif")
                                modif_check["DogDB_ID"] = dog_db["_id"]
                            else:
                                check_result.append("Error")
                                error_check["Message"] = str(
                                    "Error raised by user comparing with "
                                    + str(dog_db["NomChien"])
                                )
                                error_check["DogDB_ID"] = dog_db["_id"]

                        if len(check_result) == 0 and not ask_user:
                            check_result.append("Error")
                            error_check["Message"] = "Need to be check later"

                else:
                    print_d(
                        "All data have at least similar data, seems to be the same dog",
                        to_print=ask_user,
                    )
                    check_result.append("UpD")

            elif len(common_all_keys) < 2:
                check_result.append("Error")
                error_check["Message"] = (
                    "Error, not enough common keys couldn't conclude"
                )

            else:
                print_d(str(common_all_keys))
                raise Exception("Shouldn't access to this line")

            if len(check_result) == 1:
                check_result = check_result[0]
            else:
                print_d(
                    str(
                        "Too many result for one comparison"
                        + str(check_result)
                        + str(len(check_result))
                    )
                )
                raise Exception("Error while checking identity")

            return check_result, modif_check, error_check

        except Exception:
            print_d("-------------Erreur-------------")
            print_d(str(dog_file_infos))
            print_d(str(dog_db))
            print_exception()
            raise Exception("A fatal error as occured")

    def update_dog(self, dog_id, new_values):
        """Update new values to an existing dog.

        Parameters
        ----------
        dog_id : ObjectId
            Identifier of the dog to update.
        new_values : Dict
            Values to update.

        Returns
        -------
        MongoDBUpdateResult
            Result of the update.

        """
        try:
            dog_db_data = self.my_db["Identity"].find_one({"_id": ObjectId(dog_id)})
            new_values_checked = {}
            for key, value in new_values.items():
                value_to_use = get_not_null(value, modify=False)
                if value_to_use is not None:  # Value not null
                    if key not in dog_db_data.keys():  # Info not present
                        new_values_checked[key] = value_to_use
                    else:  # Info present
                        if len(difference(value_to_use, dog_db_data[key])) != 0:
                            new_values_checked[key] = union(
                                difference(value_to_use, dog_db_data[key]),
                                dog_db_data[key],
                            )
                            # input(str(str(dog_db_data["NomChien"]) + " new values:" + str(new_values_checked)))

            if new_values_checked:
                return self.my_db["Identity"].update_one(
                    {"_id": ObjectId(dog_id)},
                    {"$set": new_values_checked},
                    upsert=False,
                )
            else:
                return None
        except Exception:
            print_exception()
            print_d(key, value)
            print_d(dog_db_data)
            input("Wait")
            return "Error"

    def update_doc(self, collection, doc_filter, new_values, upsert=False):
        """Update a document's values.

        Parameters
        ----------
        collection : String
            Name of the collection to update.
        doc_filter : Dict
            Filter to use for selecting the documents to update.
        new_values : Dict
            Values to update.
        upsert : Boolean, optional
            If no document found by doc_filter insert new one. The default is False.

        Returns
        -------
        MongoDBUpdateResult
            Result of the update.

        """
        for key, value in new_values.items():
            if isinstance(value, np.int64):
                value = int(value)
                new_values[key] = value
        return self.my_db[collection].update_one(
            doc_filter, {"$set": new_values}, upsert=upsert
        )

    def insert_newdog(self, dog_data):
        """Insert a new dog inside the database.

        Parameters
        ----------
        dog_data : Dict
            All values to insert.

        Returns
        -------
        MongoDBInsertResult
            Result of the insertion.

        """
        dog_data_check = {}
        try:
            for key, value in dog_data.items():
                if not_null(value):
                    dog_data_check[key] = value
            return self.my_db["Identity"].insert_one(dog_data_check)
        except Exception:
            print_exception()
            return "Error"

    def insert_dysplasia_data(self, dog_id, dog_data, file_id, lecteur_file=None):
        """
        Read all dysplasia data convert it to dictionnary normed for registering.

        Parameters
        ----------
        dog_id : ObjectID
            Dog identification number for MongoDB.
        dog_data : Dict
            Dog data dictionnary to parse.
        file_id : ObjectID
            File identification number for MongoDB.
        lecteur_file : TYPE, optional
            Default lecteur identification for dcf datas. The default is None.

        Raises
        ------
        Exception
            DESCRIPTION.

        Returns
        -------
        None.

        """
        try:
            lecteur_dog = None
            dog_all_data = self.my_db["Identity"].find_one({"_id": ObjectId(dog_id)})
            if "DCF" in dog_all_data.keys():
                all_infos_dict = dog_all_data["DCF"]
            else:
                all_infos_dict = {}
            for dcf_col_start in ["Dys_", "Dys1_", "Dys2_"]:
                dcf_cols = [col for col in dog_data.index if dcf_col_start in col]
                if str(dcf_col_start + "Lecteur") in dcf_cols:
                    lecteur_dog = dog_data[str(dcf_col_start + "Lecteur")]

                if is_null(lecteur_file) and is_null(lecteur_dog):
                    old_na = [
                        x
                        for month in all_infos_dict.keys()
                        for x in all_infos_dict[month].keys()
                        if "NA_" in x
                    ]
                    nb_na = 1
                    if len(old_na) > 0:
                        nb_na = max([int(na.split("_")[1]) for na in old_na]) + 1
                    lecteur_to_use = str("NA_" + str(nb_na))
                elif not_null(lecteur_dog):
                    lecteur_to_use = lecteur_dog
                else:
                    lecteur_to_use = lecteur_file
                for col in dcf_cols:
                    if not_null(dog_data[col]):
                        field_vars = col.split("_")
                        if len(field_vars) != 2:
                            month = field_vars[1]
                            info_type = field_vars[2]
                            lateralisation = None
                            if len(field_vars) == 4:
                                lateralisation = field_vars[3]
                            elif len(field_vars) == 5:
                                try:
                                    lateralisation = field_vars[3]
                                    rep = int(field_vars[4])
                                    if rep > 3:
                                        raise Exception(
                                            "Too much repetition found in the file"
                                        )
                                except ValueError:
                                    raise Exception(
                                        "Last field isn't a number of repetition"
                                    )
                            elif len(field_vars) != 3:
                                print_d(col)
                                raise Exception(
                                    "Columns does not conform to standardization"
                                )

                            all_infos_dict = update_dic_dcf(
                                all_infos_dict,
                                month,
                                info_type,
                                dog_data[col],
                                lateralisation,
                                lecteur_to_use,
                                file_id,
                            )
                        elif len(field_vars) == 2:
                            if field_vars[1] != "Lecteur":
                                print(field_vars)
                                raise Exception("Two fields present but not lecteur")
                        else:
                            print(field_vars)
                            raise Exception("More or less than 2-4 fields present")
            all_keys = [
                [month, lecteur]
                for month in all_infos_dict.keys()
                for lecteur in all_infos_dict[month].keys()
            ]
            for month, lecteur in all_keys:
                if "File" not in all_infos_dict[month][lecteur].keys():
                    all_infos_dict = update_dic_dcf(
                        all_infos_dict, month, "File", file_id, None, lecteur, file_id
                    )
            if len(all_infos_dict) != 0:
                self.my_db["Identity"].update_one(
                    {"_id": ObjectId(dog_id)}, {"$set": {"DCF": all_infos_dict}}
                )

        except Exception:
            print_exception()
            raise Exception("Error while inserting dysplasia datas")

    def new_error(self, file, line, dog_name, error_type):
        """Insert or update a new error inside the error collection.

        Parameters
        ----------
        file : String
            Name of the file where the error occurred.
        line : Int
            Line number where the error occured.
        dog_name : String
            Name of the dog whom the error occured.
        error_type : Array
            Detail of the error.

        Returns
        -------
        MongoDBResult
            Result of the insertion or the update.

        """
        error_db = self.my_db["Erreurs"].count_documents(
            {"Fichier": file, "Ligne": line, "NomChien": dog_name}
        )
        if error_db == 1:
            return self.my_db["Erreurs"].update_one(
                {"Fichier": file, "Ligne": line, "NomChien": dog_name},
                {"$push": {"Erreurs": error_type}},
            )
        elif error_db == 0:
            return self.my_db["Erreurs"].insert_one(
                {
                    "Fichier": file,
                    "Ligne": line,
                    "NomChien": dog_name,
                    "Erreurs": error_type,
                }
            )
        else:
            print_d("Error couldn't register the error")
            input("Wait")
            return "Error"

    def new_datas_to_register(self, datas, collection):
        """
        Register datas that throwed an error to be corrected later.

        Parameters
        ----------
        datas : Dict
            All data, with file an line localisation.

        Returns
        -------
        MongoInsertResult
            Result of the insertion of the data in the ErreursDatas collection.

        """
        try:
            datas_check = {}
            for key, value in datas.items():
                if not_null(value):
                    datas_check[key] = value
            present = self.my_db[collection].count_documents(datas)
            if present == 0:
                return self.my_db[collection].insert_one(datas)
            elif present == 1:
                print_d("Datas already present")
                return None
            else:
                raise Exception(
                    str(
                        "Datas to register in "
                        + collection
                        + "present in multiple documents"
                    )
                )
        except Exception:
            print_d(datas)
            print_exception()
            raise Exception("Error while registering datas to check")

    def new_modif(self, file, line, dog_id, dog_name, modif):
        """Insert or update a new modification inside the modif collection.

        Parameters
        ----------
        file : String
            Name of the file where the modif occurred.
        line : Int
            Line number where the modif occured.
        dog_name : String
            Name of the dog whom the modif occured.
        error_type : Array
            Detail of the modif.

        Returns
        -------
        MongoDBResult
            Result of the insertion or the update.

        """
        try:
            modif_db = self.my_db["Modifs"].count_documents(
                {"Dog_id": ObjectId(dog_id)}
            )
            if modif_db == 1:
                print("Dog id already present in the modif collection, will be updated")
                result_new_modif = self.my_db["Modifs"].update_one(
                    {"Dog_id": ObjectId(dog_id)},
                    {"$push": {"Modifs": {"File": file, "Line": line, "Modif": modif}}},
                )
            elif modif_db == 0:
                print(
                    "Dog id not already present in the modif collection, will be inserted"
                )
                result_new_modif = self.my_db["Modifs"].insert_one(
                    {
                        "Dog_id": ObjectId(dog_id),
                        "Dog_name": dog_name,
                        "Modifs": [{"File": file, "Line": line, "Modif": modif}],
                    }
                )
            else:
                print_d("Error couldn't register the modification")
                input("Wait")
                result_new_modif = "Error"
            return result_new_modif
        except Exception:
            print_d(str(str(dog_id) + " " + str(dog_name)))
            print_exception()
            raise Exception("Error while registering modification")

    def quit_db(self):
        """Close the database.

        Returns
        -------
        None.

        """
        if self.client is None:
            print_d("Database not connected yet")
        else:
            self.client.close()
