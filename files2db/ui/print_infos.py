#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 19/01/2022
@author: LouisLeNezet
Module for all prompt message and user input.
"""
import linecache
import sys
import os
import logging

def print_exception():
    """
    Print exception that happened.

    The filename, the line and the type of error is prompt.

    Returns
    -------
    None.

    """
    exc_type, exc_obj, latest_exception = sys.exc_info()
    if latest_exception:
        file = latest_exception.tb_frame
        lineno = latest_exception.tb_lineno
        filename = os.path.basename(file.f_code.co_filename)
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, file.f_globals)
        logging.exception(
            'EXCEPTION IN (%s, LINE %s "%s"): %s, %s',
            filename, lineno, line.strip(), exc_obj, exc_type
        )
    else:
        raise RuntimeError("Couldn't access the infos from the system")
