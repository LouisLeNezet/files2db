# -*- coding: utf-8 -*-
"""
Module for all prompt message.

Created on Tue Jan 19 13:00:12 2021

@author: LouisLeNezet
"""

import linecache
import sys
import settings


def print_d(*text_to_print, text_type="text", to_print=True):
    """
    Print text if SHOW_QUERY is true.

    Parameters
    ----------
    text_to_print : Multiple
        Text to send to prompt.
    *other_text : TYPE
        Other text to send to prompt.

    Returns
    -------
    None.

    """
    try:
        if to_print:
            text_to_print = " ".join([str(x) for x in text_to_print])
            if settings.PARAMS == {} or not settings.PARAMS["TKINTER_SHOW"]:
                if settings.PARAMS == {} or settings.PARAMS["SHOW_QUERY"]:
                    print(text_to_print)
            else:
                if settings.PARAMS["GUI_MW"] is None:
                    print("Error")
                else:
                    settings.PARAMS["GUI_MW"].update_log_box(
                        str(text_to_print), text_type
                    )
    except KeyError:
        print("KeyError", *text_to_print)
    except Exception as e:
        print(f"An error as occured during message printing {e} {type(e)}")
        raise Exception("Error print_d()")


def print_exception():
    """
    Print exception that happened.

    The filename, the line and the type of error is prompt.

    Returns
    -------
    None.

    """
    exc_type, exc_obj, latest_excpt = sys.exc_info()
    file = latest_excpt.tb_frame
    lineno = latest_excpt.tb_lineno
    filename = file.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, file.f_globals)
    print_d(
        f'EXCEPTION IN ({filename}, LINE {lineno} "{line.strip()}"): {exc_obj}, {exc_type}',
        text_type="error",
    )


def menu():
    """
    Show a menu for the user to choose what to do.

    Three option a possible:
        Check columns,
        Add data,
        Exit script

    Returns
    -------
    None.

    """
    answer = True
    while answer:
        print_d("""
              --------Menu--------

             1. Check Variable Names
             2. Prepare identity datas
             3. Add data from files
             4. Compare to database
             5. Check for Errors
             6. Add missing ID datas
             7. Exit
             """)
        question_prompt = "What would you like to do ? \n"
        if settings.PARAMS["TKINTER_SHOW"]:
            ans = settings.PARAMS["GUI_MW"].ask_user(question_prompt)
        else:
            ans = input(question_prompt)

        try:
            val_ans = int(ans)
            if val_ans > 0 < 8:
                result = {
                    1: "CheckCols",
                    2: "PrepId",
                    3: "AddDatas",
                    4: "CompareDB",
                    5: "CheckErrors",
                    6: "AddMissingID",
                    7: "Exit",
                }
                return result.get(val_ans, "Error")
            else:
                print_d("Invalid input, please enter number next to your choice")
        except ValueError:
            print_d("Invalid input, please enter number next to your choice")


def question_to_user(question, ans_v=1):
    """
    Prompt question and control the answer.

    Parameters
    ----------
    question : String
        Question to prompt to the user.
    ans_v : Int, optional
        Possibility to answer (1 = y/n, 2 = y/n/e) . The default is 1.
        If "q" is answered then sys.exit().

    Returns
    -------
    String or Boolean
        Return the answer obtained with True or False (+ "Error" if ans_v=2).

    """
    while True:
        if ans_v == 1:
            question_prompt = str(question + " y/n \n")
        elif ans_v == 2:
            question_prompt = str(question + " y/n/e \n")
        if settings.PARAMS["TKINTER_SHOW"]:
            answer = settings.PARAMS["GUI_MW"].ask_user(question_prompt)
        else:
            answer = input(question_prompt)
        if answer == "y":
            return True
        elif answer == "n":
            return False
        elif answer == "e" and ans_v == 2:
            return "Error"
        elif answer == "q":
            sys.exit()
        else:
            print_d("Please answer by 'y' (yes) or 'n' (no)!")
