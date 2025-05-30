# -*- coding: utf-8 -*-
"""
Module to show all application in a GUI.

Created on Fri Mar 12 17:44:24 2021

@author: LouisLeNezet
"""

import tkinter as tk
from tkinter import filedialog, Tk, ttk
import settings
from mainscript import main_loop
from printconsole import print_d


class MainWindow(Tk):
    """Generate a GUI interface for the application."""

    def __init__(self):
        """
        Set the GUI interface with the basic organization.

        Returns
        -------
        None.

        """
        Tk.__init__(self)
        self.geometry('1200x600')
        self.title("Script to concatenate Data")
        self.create_menu()
        self.bind('<Alt-s>', self.start_script)
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=2)
        self.path_to_print = tk.StringVar()
        self.path_to_print.set(settings.PARAMS["PATH_TO_ORGA"])
        path_label = tk.Label(self, textvariable=self.path_to_print,
                              font=("Segoe UI", 10))
        path_label.grid(column=0, row=1, sticky="W")

        self.setup_progress_bar()

        self.log_box = tk.Text(self)
        self.log_box.grid(column=0, row=3, sticky='nsew', columnspan=2)
        self.log_box.tag_configure('text', foreground='black')
        self.log_box.tag_configure('center', foreground='black', justify="center")
        self.log_box.tag_configure('error', foreground='red')
        self.log_box.tag_configure('success', foreground='green')
        self.update_log_box("-------------Script Log-------------", "center")
        scroll_bar = tk.Scrollbar(self, command=self.log_box.yview)
        scroll_bar.grid(column=1, row=3, sticky="nse")
        self.log_box.configure(yscrollcommand=scroll_bar.set)

        input_frame = tk.Frame(self)
        input_frame.grid(column=0, row=4, columnspan=2)
        input_frame.focus_set()
        self.user_input = tk.Entry(input_frame)
        self.user_input.grid(column=0, row=0)
        self.user_input.bind("<Return>", self.confirm_answer)
        but_answer = tk.Button(input_frame, text="Ok")
        but_answer.bind("<Button-1>", self.confirm_answer)
        but_answer.grid(column=1, row=0)

        self.user_new_insert = None

    def select_file_orga(self, event=None):
        """
        Prompt a dialog to select the directory to use.

        Returns
        -------
        None.

        """
        initial_dir = settings.PARAMS["PATH_TO_ORGA"].rsplit("//", 1)[0]
        settings.set_value("PATH_TO_ORGA",
                           filedialog.askopenfilename(initialdir=initial_dir,
                                                      title="Select the organisation file",
                                                      filetypes=([('Excel files', "*.xlsx")])))
        self.update_log_box("Directory correctly changed")
        self.path_to_print.set(settings.PARAMS["PATH_TO_ORGA"])

    def start_script(self, event=None):
        """
        Start the main script when triggered.

        Returns
        -------
        None.

        """
        main_loop()

    def update_log_box(self, text, text_type="text"):
        """
        Update the log box with a new text at the end of the box.

        Parameters
        ----------
        text : String
            Text to print.
        text_type : String, optional
            Type of text to print ("text", "error", "warning", "success"). The default is "text".

        Returns
        -------
        None.

        """
        all_text_type = ["text", "error", "warning", "success", "center"]
        if text_type not in all_text_type:
            raise Exception(str("Text type invalid " + text_type))

        self.log_box.insert("end", text, text_type)
        if not text.endswith("\n"):
            self.log_box.insert("end", "\n")
        self.log_box.see("end")
        self.update()

    def ask_user(self, question):
        """
        Aks the user a question and wait for the confirmation to return an answer.

        Parameters
        ----------
        question : String
            Question to ask.

        Returns
        -------
        answer : String
            Answer obtained after confirmation.

        """
        self.update_log_box(question)
        self.user_input.focus()
        while self.user_new_insert is None:
            self.update()
        self.user_new_insert = None
        answer = self.user_input.get()
        self.user_input.delete(0, "end")
        return answer

    def confirm_answer(self, event=None):
        """
        When activated, modify self variable to confirm the answer.

        Parameters
        ----------
        event : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        self.user_new_insert = True

    def create_menu(self):
        """
        Create a menu a the top of the window.

        Returns
        -------
        None.

        """
        menubar = tk.Menu(self)

        param_menu = tk.Menu(menubar, tearoff=0)
        param_menu.add_command(label="Change directory", command=self.select_file_orga)
        param_menu.add_command(label="Change DB name", command=self.change_db_name)
        param_menu.add_command(label="Start script", command=self.start_script)
        menubar.add_cascade(label="Initialization", menu=param_menu)

        menubar.bind("Alt-s", self.start_script)

        self.config(menu=menubar)

    def change_db_name(self):
        """
        Change the database name based on the user input.

        Returns
        -------
        None.

        """
        self.user_input.insert(0, settings.PARAMS["DB_NAME"])
        settings.set_value("DB_NAME", self.ask_user("Enter name of the database and click Ok"))
        self.count_orga["DbName"]["Value"].set(settings.PARAMS["DB_NAME"])
        self.update_log_box(str(settings.PARAMS["DB_NAME"] + " will  be used as the database name"))

    def setup_progress_bar(self):
        """
        Generate all the progress bar necessary for the GUI.

        Returns
        -------
        None.

        """
        pb_frame = tk.Frame(self)
        pb_frame.grid(column=0, row=2, sticky="nsew")
        pb_frame.columnconfigure(0, weight=1)
        pb_frame.columnconfigure(1, weight=3)
        pb_frame.rowconfigure(0, weight=1)
        pb_frame.rowconfigure(1, weight=1)
        pb_frame.rowconfigure(2, weight=1)

        self.files_pb_label = tk.StringVar()
        self.files_pb_label.set("Files progression: ")
        pb_files_label = tk.Label(pb_frame, textvariable=self.files_pb_label,
                                  font=("Segoe UI", 10))
        pb_files_label.grid(column=0, row=0, sticky="we")

        self.pb_files = ttk.Progressbar(pb_frame, orient="horizontal", length=280, mode="determinate")
        self.pb_files.grid(column=1, row=0, sticky="we")

        self.file_screening = tk.StringVar()
        file_screening_label = tk.Label(pb_frame, textvariable=self.file_screening,
                                        font=("Segoe UI", 10))
        file_screening_label.grid(column=0, row=1, sticky="we", columnspan=2)

        self.datas_pb_label = tk.StringVar()
        self.datas_pb_label.set("Datas progression: ")
        pb_datas_label = tk.Label(pb_frame, textvariable=self.datas_pb_label,
                                  font=("Segoe UI", 10))
        pb_datas_label.grid(column=0, row=3, sticky="we")
        self.pb_datas = ttk.Progressbar(pb_frame, orient="horizontal", length=280, mode="determinate")
        self.pb_datas.grid(column=1, row=3, sticky="we")

        count_frame = tk.Frame()
        count_frame.grid(column=1, row=0, rowspan=3)
        self.setup_count(count_frame)

    def update_pb(self, value, max_value, pb, files_loc=None):
        if pb == "files":
            self.pb_files['value'] = value/max_value*100
            self.files_pb_label.set(str("Files progression: " + str(value) + "/" + str(max_value)))
            self.file_screening.set(files_loc)
        elif pb == "datas":
            self.datas_pb_label.set(str("Datas progression: " + str(value) + "/" + str(max_value)))
            self.pb_datas['value'] = value/max_value*100
        else:
            raise Exception("Wrong pb value given")

    def setup_count(self, frame):
        count_label = {}
        self.nb_count = []
        self.count_orga = {"DbName": {"Position": [0, 0],
                                      "Value": tk.StringVar(value=settings.PARAMS["DB_NAME"]),
                                      "Label": "DB name: "},
                           "Identity": {"Position": [1, 0], "Value": tk.IntVar(0),
                                        "Label": "Nb Dogs: "},
                           "DatasToCheck": {"Position": [0, 1], "Value": tk.IntVar(0),
                                            "Label": "Datas to Check: "},
                           "DatasNoID": {"Position": [1, 1], "Value": tk.IntVar(0),
                                    "Label": "Nb Missing Id: "},
                           "Errors": {"Position": [0, 2], "Value": tk.IntVar(0),
                                      "Label": "Nb Errors: "},
                           "Modifs": {"Position": [1, 2], "Value": tk.IntVar(0),
                                      "Label": "Nb Modifs: "},
                           "ToCheck": {"Position": [0, 3], "Value": tk.IntVar(0),
                                       "Label": "Lines to Check: ",
                                       "ValueMax": tk.IntVar(0)},
                           "ToAdd": {"Position": [1, 3], "Value": tk.IntVar(0),
                                     "Label": "Lines to Add: ",
                                     "ValueMax": tk.IntVar(0)}
                           }
        for value in self.count_orga.keys():
            count_label[value] = {}
            count_label[value]["Frame"] = tk.Frame(frame)
            count_label[value]["Frame"].grid(column=self.count_orga[value]["Position"][0],
                                             row=self.count_orga[value]["Position"][1])
            count_label[value]["Label"] = tk.Label(count_label[value]["Frame"],
                                                   text=self.count_orga[value]["Label"])
            count_label[value]["Label"].grid(column=0, row=0)
            count_label[value]["Value"] = tk.Label(count_label[value]["Frame"],
                                                   textvariable=self.count_orga[value]["Value"])
            count_label[value]["Value"].grid(column=1, row=0)
            if "ValueMax" in self.count_orga[value].keys():
                count_label[value]["Sep"] = tk.Label(count_label[value]["Frame"],
                                                     text="/")
                count_label[value]["Sep"].grid(column=2, row=0)
                count_label[value]["ValueMax"] = tk.Label(count_label[value]["Frame"],
                                                          textvariable=self.count_orga[value]["ValueMax"])
                count_label[value]["ValueMax"].grid(column=3, row=0)

    def update_count_label(self, results, task):
        for result in results:
            if result == "Updated":
                if task == "AddDatas":
                    self.count_orga["ToAdd"]["Value"].set(self.count_orga["ToAdd"]["Value"].get()+1)
                    self.count_orga["ToCheck"]["Value"].set(self.count_orga["ToCheck"]["Value"].get()+1)
            elif "Modif" in result:
                self.count_orga["Modifs"]["Value"].set(self.add_del_count(result, "Modifs"))
            elif "Error" in result:
                self.count_orga["Errors"]["Value"].set(self.add_del_count(result, "Errors"))
            elif "DatasToCheck" in result:
                self.count_orga["DatasToCheck"]["Value"].set(self.add_del_count(result, "DatasToCheck"))
            elif "DatasNoID" in result:
                self.count_orga["DatasNoID"]["Value"].set(self.add_del_count(result, "DatasNoID"))
            elif result == "Inserted":
                self.count_orga["Identity"]["Value"].set(self.count_orga["Identity"]["Value"].get()+1)
                if task == "AddDatas":
                    self.count_orga["ToAdd"]["Value"].set(self.count_orga["ToAdd"]["Value"].get()+1)
                    self.count_orga["ToCheck"]["Value"].set(self.count_orga["ToCheck"]["Value"].get()+1)
            elif "NotEnoughIDData" in result:
                if result != "NotEnoughIDData but PrepID":
                    self.count_orga["DatasNoID"]["Value"].set(self.add_del_count(result, "DatasNoID"))
            elif result != "CheckLater":
                print_d(result)
                raise Exception("Result obtained not in the tolerated possibilities")

    def add_del_count(self, result, value):
        if "del_" in result:
            return self.count_orga[value]["Value"].get()-1
        elif "new_" in result:
            return self.count_orga[value]["Value"].get()+1
        else:
            raise Exception(str("Error while changing the value of" + value))
            return "Error"
