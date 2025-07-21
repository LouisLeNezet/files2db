#!/usr/bin/env python3
"""
Created on 25/11/2022
@author: LouisLeNezet
Testing scripts for the different common functions.
"""

import os
import unittest
from unittest.mock import patch

import pandas as pd

from files2db.read_file.orga_read import (
    get_db_from_csv,
    get_db_from_excel,
    get_db_from_path,
    load_file_orga,
    validate_columns,
    validate_columns_orga,
    validate_files_presence,
)


class TestValidateFiles(unittest.TestCase):
    """Check that the validate_files_presence function works as expected."""

    def test_validate_files_presence_missing_files(self):
        """Test missing files detection."""
        with self.assertRaises(KeyError) as context:
            validate_files_presence({"file1", "file2"}, {"file1"}, "test.xlsx")
        self.assertIn("Missing files file2", str(context.exception))

    @patch("logging.warning")
    def test_validate_files_presence_extra_files(self, mock_log):
        """Test logging when extra files are present."""
        validate_files_presence({"file1"}, {"file1", "file2"}, "test.xlsx")
        mock_log.assert_called_once_with(
            "Extra files %s present in %s and not needed", {"file2"}, "test.xlsx"
        )

    def test_validate_files_presence_correct(self):
        """Test when all files are correctly present."""
        try:
            validate_files_presence({"file1", "file2"}, {"file1", "file2"}, "test.xlsx")
        except KeyError:
            self.fail("validate_files_presence raised KeyError unexpectedly!")


class TestingLoadFileOrga(unittest.TestCase):
    """Class for testing load_file_orga"""

    def test_load_file_orga(self):
        """Test load_file_orga"""
        db_orga = load_file_orga()
        self.assertEqual(
            list(db_orga.keys()),
            ["Files", "FieldRules", "ValuesMap"],
        )
        self.assertEqual(
            list(db_orga["Files"].keys()),
            ["columns_needed", "columns_sup", "integer", "list"],
        )
        self.assertEqual(
            db_orga["Files"]["columns_needed"],
            [
                "FilePath",
                "SheetName",
                "LineStart",
                "LineEnd",
                "Header",
                "ColStart",
                "ColEnd",
                "ToAdd",
                "AsCorrection",
                "Separator",
            ],
        )


class TestColumnValidation(unittest.TestCase):
    """Check that the validate_columns function works as expected."""

    def test_validate_columns_missing_columns(self):
        """Test missing columns error."""
        with self.assertRaises(KeyError) as context:
            validate_columns(
                pd.DataFrame(columns=["A"]),
                "test.xlsx",
                cols_need={"A", "B"},
                cols_sup=False,
            )
        self.assertIn("Missing columns {'B'} in", str(context.exception))

    @patch("logging.warning")
    def test_validate_columns_extra_columns(self, mock_log):
        """Test logging when extra columns exist."""
        validate_columns(
            pd.DataFrame(columns=["A", "B", "C"]),
            "test.xlsx",
            cols_need={"A", "B"},
            cols_sup=False,
        )
        mock_log.assert_called_once_with(
            "Extra columns %s in %s and won't be used", {"C"}, "test.xlsx"
        )

    def test_validate_columns_correct(self):
        """Test when all columns match expectations."""
        try:
            validate_columns(
                pd.DataFrame(columns=["A", "B", "C"]),
                "test.xlsx",
                cols_need={"A", "B"},
                cols_sup=True,
            )
        except KeyError:
            self.fail("validate_columns raised KeyError unexpectedly!")


class TestColumnValidationOrga(unittest.TestCase):
    """Check that the validate_columns_orga function works as expected."""

    def test_validate_columns_missing_columns(self):
        """Test missing columns error."""
        orga_dict = {
            "file1": {"columns_needed": ["A", "B"], "columns_sup": False},
            "file2": {"columns_needed": ["C", "D"], "columns_sup": True},
        }
        db_dict = {
            "file1": pd.DataFrame(columns=["A", "D"]),
            "file2": pd.DataFrame(columns=["C", "D", "E"]),
        }
        with self.assertRaises(KeyError) as context:
            validate_columns_orga(orga_dict, db_dict)
        self.assertIn("Missing columns {'B'} in", str(context.exception))

    @patch("logging.warning")
    def test_validate_columns_orga_extra_columns(self, mock_log):
        """Test logging when extra columns exist."""
        orga_dict = {
            "file1": {"columns_needed": ["A", "B"], "columns_sup": False},
            "file2": {"columns_needed": ["C", "D"], "columns_sup": False},
        }
        db_dict = {
            "file1": pd.DataFrame(columns=["A", "B"]),
            "file2": pd.DataFrame(columns=["C", "D", "E"]),
        }
        validate_columns_orga(orga_dict, db_dict)
        mock_log.assert_called_once_with("Extra columns %s in %s and won't be used", {"E"}, "file2")

    def test_validate_columns_orga_correct(self):
        """Test validate_columns_orga."""
        orga_dict = {
            "file1": {"columns_needed": ["A", "B"], "columns_sup": False},
            "file2": {"columns_needed": ["C", "D"], "columns_sup": True},
        }
        db_dict = {
            "file1": pd.DataFrame(columns=["A", "B"]),
            "file2": pd.DataFrame(columns=["C", "D", "E"]),
        }
        validate_columns_orga(orga_dict, db_dict)


class TestGetDBFromExcel(unittest.TestCase):
    """Check that the get_db_from_excel function works as expected."""

    def setUp(self):
        """Set up test data path"""
        self.test_data_path = os.path.join(os.path.dirname(__file__), "test_dataset")

    def test_get_db_from_excel_missing_file(self):
        """Test missing file error."""
        file_path = os.path.join(self.test_data_path, "missing.xlsx")
        with self.assertRaises(FileNotFoundError):
            get_db_from_excel(file_path, {})

    def test_get_db_from_excel_missing_sheet(self):
        """Test missing sheet error."""
        file_path = os.path.join(self.test_data_path, "RepTest_wrong.xlsx")
        with self.assertRaises(KeyError) as context:
            get_db_from_excel(file_path, load_file_orga())
        self.assertIn("'Missing files ValuesMap in", str(context.exception))


class TestGetDBFromPath(unittest.TestCase):
    """Check that the get_db_from_path function works as expected."""

    def setUp(self):
        """Set up test data path"""
        self.test_data_path = os.path.join(os.path.dirname(__file__), "test_dataset")

    @patch("logging.warning")
    def test_get_db_from_path_correct_xlsx(self, mock_log):
        """Test missing sheet error."""
        file_path = os.path.join(self.test_data_path, "RepTest_correct.xlsx")
        db_orga = get_db_from_path(file_path, load_file_orga())
        mock_log.assert_called_once_with(
            "Extra columns %s in %s and won't be used", {"OptColToNotUse"}, "FieldRules"
        )
        self.assertEqual(
            set(db_orga.keys()),
            set(["Files", "FieldRules", "ValuesMap"]),
        )
        self.assertEqual(db_orga["Files"].shape, (2, 22))

    def test_get_db_from_path_correct_csv(self):
        """Test missing sheet error."""
        file_path = os.path.join(self.test_data_path, "test1/orga.csv")
        db_orga = get_db_from_path(file_path, load_file_orga())

        self.assertEqual(
            set(db_orga.keys()),
            set(["Files", "FieldRules", "ValuesMap"]),
        )
        self.assertEqual(db_orga["Files"].shape, (4, 16))
        self.assertEqual(db_orga["FieldRules"]["DelMatch"][5], ["delmatchitis", "othermatch"])


class TestGetDBFromCSV(unittest.TestCase):
    """Check that the get_db_from_csv function works as expected."""

    def setUp(self):
        """Set up test data path"""
        self.test_data_path = os.path.join(os.path.dirname(__file__), "test_dataset")

    def test_get_db_from_csv_wrong_columns(self):
        """Test wrong columns error."""
        file_path = os.path.join(self.test_data_path, "wrong_orga.csv")
        with self.assertRaises(KeyError) as context:
            get_db_from_csv(file_path, {})
        self.assertIn("Columns in", str(context.exception))

    def test_get_db_from_csv_missing_files(self):
        """Test missing files error."""
        file_path = os.path.join(self.test_data_path, "missing.csv")
        with self.assertRaises(FileNotFoundError):
            get_db_from_csv(file_path, {})

    def test_get_db_from_csv_correct(self):
        """Test correct file."""
        file_path = os.path.join(self.test_data_path, "test1/orga.csv")
        db_orga = get_db_from_csv(file_path, load_file_orga())
        self.assertEqual(
            set(db_orga.keys()),
            set(["Files", "FieldRules", "ValuesMap"]),
        )
        self.assertEqual(db_orga["Files"].shape, (4, 16))


if __name__ == "__main__":
    unittest.main()
