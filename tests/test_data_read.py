#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 25/11/2022
@author: LouisLeNezet
Testing scripts for the different common functions.
"""
import os
import unittest
import pandas as pd
from files2db.read_file.data_read import read_file, columns_to_int, lines_to_int

class TestingClass(unittest.TestCase):
    """ Class for testing """
    def setUp(self):
        """Set up test data path"""
        self.test_data_path = os.path.join(os.path.dirname(__file__), "test_dataset")

    def test_columns_to_int(self):
        """Test columns_to_int"""
        # Test with a list of strings
        result = columns_to_int(1, 5, [3, 4])
        self.assertEqual(result, (1, 5))

        # Test with a list of mixed types
        result = columns_to_int("3", "5", [2, 5])
        self.assertEqual(result, (3, 5))
        
        # Test with letters in the list
        result = columns_to_int("A", "AAA", [2, 800])
        self.assertEqual(result, (1, 703))
        
        # Test with a mix string
        result = columns_to_int("A", "3", [2, 5])
        self.assertEqual(result, (1, 3))
        
        # Test raising ValueError for invalid range
        with self.assertRaises(ValueError):
            columns_to_int(5, 1, [2, 5])
        # Test raising ValueError for out of range
        with self.assertRaises(ValueError):
            columns_to_int(1, 10, [2, 5])
        
    def test_lines_to_int(self):
        """Test lines_to_int"""
        # Test with valid inputs
        result = lines_to_int(2, 5, 1, [10, 5])
        self.assertEqual(result, (2, 5, 1))

        # Test with header and line_start
        result = lines_to_int(3, None, 1, [10, 5])
        self.assertEqual(result, (3, 11, 1))

        # Test with line_start and line_end
        result = lines_to_int(None, None, 2, [10, 5])
        self.assertEqual(result, (3, 11, 2))
        
        # Test with header and line_end
        result = lines_to_int(2, 6, None, [10, 5])
        self.assertEqual(result, (2, 6, 1))

        # Test raising ValueError for invalid range
        with self.assertRaises(ValueError):
            lines_to_int(5, 2, 1, [10, 5])
        
        # Test raising ValueError for out of range
        with self.assertRaises(ValueError):
            lines_to_int(0, 12, 1, [10, 5])
        # Test raising ValueError for header >= line_start
        with self.assertRaises(ValueError):
            lines_to_int(2, 5, 2, [10, 5])
        # Test raising ValueError for line_start > line_end
        with self.assertRaises(ValueError):
            lines_to_int(5, 3, 1, [10, 5])
            
    def test_read_file_simple(self):
        """Test read_file with simple CSV file"""
        file_path = os.path.join(self.test_data_path, "files/fileA.xlsx")
        data = read_file(file_path, sheet_name="Feuil1", header=3, line_start=5, line_end=6, col_start="C", col_end="E")
        self.assertEqual(data.shape[0], 2)
        self.assertEqual(data.shape[1], 3)
        self.assertEqual(data.columns[0], "ColA")
        self.assertEqual(data["ColA"].tolist(), ["1", "3"])

    def test_read_file(self):
        """Test read_file"""
        file_path = os.path.join(self.test_data_path, "orga.csv")
        data = read_file(file_path, sep=",")
        self.assertEqual(data.shape[0], 5)
        self.assertEqual(data.shape[1], 3)
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
