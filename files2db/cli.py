#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 22/10/2021
@author: LouisLeNezet
Script to launch the application
"""

import os
import sys
import logging
import typer
from files2db.main import main

logging.basicConfig(level=logging.INFO)

# Remove '' and current working directory from the first entry
# of sys.path, if present to avoid using current directory
# in pip commands check, freeze, install, list and show,
# when invoked as python -m pip <command>
if sys.path[0] in ("", os.getcwd()):
    sys.path.pop(0)

# If we are running from a wheel, add the wheel to sys.path
# This allows the usage python common_tools-*.whl/ install common_tools-*.whl
if __package__ == "":
    # __file__ is common_tools-*.whl/__main__.py
    # first dirname call strips of '/__main__.py', second strips off '/pip'
    # Resulting path is the name of the wheel itself
    # Add that to sys.path so we can import pip
    path = os.path.dirname(os.path.dirname(__file__))
    logging.info(path)
    sys.path.insert(0, path)

if __name__ == "__main__":
    typer.run(main)
