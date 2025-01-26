#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 16/11/2022
@author: LouisLeNezet
Module for all functions for getting infos about the os and converting path.
"""
# ###Library needed####
import platform
import os
import re
import logging

def welcome(script_use=None, cwd=None, opsyst=None, col_needed=None):
    """
    Welcome the user and print the infos needed.

    Parameters
    ----------
    cwd_path : str
        Path of the working directory.

    Returns
    -------
    None.
    """
    logging.info("Hi, this script is used for %s", script_use)
    logging.info("If you have any questions or problems, contact Louis Le Nézet by mail")
    logging.info(" ")
    logging.info("Your current directory is the following: ")
    logging.info(cwd)
    logging.info("The operating system detected is %s", opsyst)
    if col_needed:
        logging.info("The columns should be named as follow")
        logging.info(col_needed)

def get_os():
    """
    Get the operating system.

    Raises
    ------
    Exception
        The operating system isn't supported.

    Returns
    -------
    operating_system : str
        Operating system detected (Mac, Windows, Linux).
    current_wd : str
        Current working directory.

    """
    operating_system = platform.uname()[0]
    if operating_system == "Darwin":
        operating_system = "Mac"
    elif not operating_system in ["Windows", "Linux"]:
        logging.info(
            "Please contact creator !!, operating system %s not supported.",
            operating_system
        )
        raise OSError(f"You are running on an unsupported system {operating_system}")
    return operating_system, os.getcwd()

os_pattern = {"Windows": r"^(C:|D:|E:|F:|S:)(\\|\/)",
    "Wsl":r"^\/mnt\/(c|d|e|f|s)(\\|\/)",
    "Relative":r"^(\/(?!mnt\/(c|d|e|f|s)(\\|\/)))|^((\.\.(\\|\/))+|(\.(\\|\/)))"}
os_prefix = {"Windows": "C:/","Wsl":"/mnt/c/","Relative":"/"}

os_pat_comp = {
    os_name:re.compile(os_pat, flags=re.IGNORECASE)
    for os_name, os_pat in os_pattern.items()
}

def get_path_os(path):
    """
    Get the os system based on the path provided

    Parameters
    ----------
    path : str
        Full path to test

    Returns
    -------
    operating_system : str
        Operating system detected (Windows, Wsl, Relative).

    Raises
    ------
    Exception
        Multiple match
    """
    os_match = [os_name for os_name, os_pat in os_pat_comp.items()
                if bool(os_pat.search(path))]
    if len(os_match) == 1:
        return os_match[0]
    else:
        raise OSError(f"Path {path} should not match multiple or none os patterns {os_match}")

def get_file_path(file_path):
    """
    Convert file path to match the os system running

    Parameters
    ----------
    file_path : str
        Full path to convert

    Returns
    -------
    file_path : str
        Full path converted to current os
    """
    _op_sys, cwd_path = get_os()
    cwd_os = get_path_os(cwd_path)
    file_os = get_path_os(file_path)
    if cwd_os != file_os and all([os_path in ["Windows","Wsl"] for os_path in [cwd_os, file_os]]):
        file_path = re.sub(os_pattern[file_os],os_prefix[cwd_os],file_path, count=1)
    return re.sub(r"\\","/",file_path)
