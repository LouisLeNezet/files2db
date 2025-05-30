# -*- coding: utf-8 -*
"""Running module to use for starting app.

Created on Fri Jan 22 10:04:30 2021
@author: LouisLeNezet
"""
import os
import settings
from mainscript import main_loop
from printconsole import question_to_user, print_d
from tkinter_gui import MainWindow


class App():
    """Class for starting the app and select the directory."""

    def __init__(self):
        self.window = None
        settings.init()

    def setup(self):
        """
        Set the necessary parameters for the app.

        Returns
        -------
        None.

        """
        self.get_path_to_orga()

        if settings.PARAMS["TKINTER_SHOW"]:
            settings.PARAMS["GUI_MW"] = MainWindow()

    def start_script(self):
        """
        Start the main script when triggered.

        Returns
        -------
        None.

        """
        print_d("Test start")
        main_loop()

    def get_path_to_orga(self):
        """
        Ask the user for a change in directory.

        Returns
        -------
        Path: String
            Path to use for the app.

        """
        if settings.PARAMS["PATH_TO_ORGA"] is None:
            path = os.getcwd()
            if "\\PythonScript" in path:
                path = path.replace("\\PythonScript", "")

            path = str(path + "\\20-06-08_ContenusFichiersNormalise_LLN.xlsx")
            if int(os.path.isfile(path)):
                settings.set_value("PATH_TO_ORGA", path)
            else:
                path = None

            if not settings.PARAMS["TKINTER_SHOW"]:
                if path is None:
                    print("No organisation file known yet nor found")
                    change_path = True
                else:
                    print("Your current organisation file is the following: ")
                    print(path)
                    change_path = question_to_user("Do you want to change it")

                if change_path:
                    path = input("Please insert valid new path to file:")
                    while not int(os.path.isfile(path)):
                        print("Sorry, no file found at the path indicated.")
                        path = input("Please insert valid new path to file:")
                settings.set_value("PATH_TO_ORGA", path)

        return settings.PARAMS["PATH_TO_ORGA"]

def runApp():
    app = App()
    app.setup()
    if settings.PARAMS["TKINTER_SHOW"]:
        settings.PARAMS["GUI_MW"].mainloop()
    else:
        app.start_script()
    print("End of run module")

if __name__ == "__main__":
    runApp()
