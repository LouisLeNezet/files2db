#!/usr/bin/env python3
"""
Created on 25/11/2022
@author: LouisLeNezet
Testing scripts for the different common functions.
"""

import logging
import os
import unittest

import pandas as pd

from files2db.data_mg.data_iterate import iterate_file


class TestValidateFiles(unittest.TestCase):
    """Check that the validate_files_presence function works as expected."""

    def setUp(self):
        """Set up test data path"""
        logging.getLogger().setLevel(logging.CRITICAL)

    def test_iterate_with_file_csv(self):
        """Use a CSV file to test the iterate_file function."""
        test_file_path = os.path.join(os.path.dirname(__file__), "test_dataset", "test1/files.csv")
        file_df = pd.read_csv(test_file_path, sep=";", encoding="utf8")
        iterated_data = iterate_file(file_df)

        self.assertIsInstance(iterated_data, pd.DataFrame)
        self.assertFalse(iterated_data.empty, "The resulting DataFrame should not be empty.")
        columns_expected = [
            "EmplacementOrigine",
            "ColA",
            "ColB",
            "ColC",
            "ColD",
            "Author",
            "DateFileCreation",
            "FileName",
        ]
        for col in columns_expected:
            self.assertIn(
                col,
                iterated_data.columns,
                f"Column {col} should be present in the DataFrame.",
            )

        # Check that no Out value is present
        self.assertFalse(
            (iterated_data == "Out").any().any(),
            "The DataFrame should not contain 'Out' values.",
        )

        # Check that the dimensions of the DataFrame are as expected
        self.assertEqual(iterated_data.shape[0], 10, "The DataFrame should have 10 rows.")
        self.assertEqual(iterated_data.shape[1], 11, "The DataFrame should have 11 columns.")

    def test_iterate_empty_dataframe(self):
        """Test the iterate_file function with an empty DataFrame."""
        empty_df = pd.DataFrame()
        with self.assertRaises(ValueError):
            iterate_file(empty_df)

    def test_iterate_with_invalid_file(self):
        """Test the iterate_file function with an invalid file."""
        invalid_file_df = pd.DataFrame(
            {
                "FileName": ["invalid_file.csv"],
                "FilePath": ["C:/invalid_file.csv"],
                "Header": [1],
                "LineStart": [1],
                "LineEnd": [10],
                "ColStart": ["A"],
                "ColEnd": ["D"],
                "SheetName": [None],
                "Encoding": ["utf8"],
                "Sep": [";"],
            }
        )

        with self.assertRaises(FileNotFoundError):
            iterate_file(invalid_file_df)
