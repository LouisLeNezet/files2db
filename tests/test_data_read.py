#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 25/11/2022
@author: LouisLeNezet
Testing scripts for the different common functions.
"""
import os
import unittest
from read_file.data_read import read_file

class TestingClass(unittest.TestCase):
    """ Class for testing """
    def setUp(self):
        """Set up test data path"""
        self.test_data_path = os.path.join(os.path.dirname(__file__), "test_dataset")

    def test_read_file(self):
        """Test read_file"""
        file_path = os.path.join(self.test_data_path, "orga.csv")
        data = read_file(file_path)
        self.assertEqual(data.shape[0], 5)
        self.assertEqual(data.shape[1], 2)
        self.assertEqual(data.columns[0], "file")

        file_path = os.path.join(self.test_data_path, "FichierTestBaseDonnees.xlsx")
        data = read_file(
            file_path, sheet_name="Feuil1", header=3,
            line_start=6, line_end=21, col_start=2, col_end=6
        )
        self.assertEqual(data.shape[0], 16)
        self.assertEqual(data.shape[1], 5)
        self.assertEqual(data.columns[0], "NomChien")

        file_path = os.path.join(self.test_data_path, "FichierTestBaseDonnees.xlsx")
        data = read_file(
            file_path, sheet_name="Feuil1", header=3,
            line_start=6, line_end=6, col_start=4, col_end=4
        )
        self.assertEqual(data.shape[0], 1)
        self.assertEqual(data.shape[1], 1)
        self.assertEqual(data.columns[0], "Race")

if __name__ == '__main__':
    unittest.main()
