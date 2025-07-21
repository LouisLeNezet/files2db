#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 18/11/2022
@author: LouisLeNezet
Testing scripts for the null_values functions.
"""

import unittest
import math
import pandas as pd
import numpy as np

from files2db.data_process.null_values import (
    not_null,
    is_null,
    array_not_null,
    bool_invert,
)
from files2db.data_process.null_values import get_not_null, modify


class TestingClass(unittest.TestCase):
    """Class for testing"""

    def test_modify(self):
        """Test function modify"""
        test_values = ["A bc ", "None", "Na N"]
        test_result = ["A bc ", "None", "Na N"]
        test_result_m = ["ABC", None, None]
        for value, result, result_m in zip(test_values, test_result, test_result_m):
            with self.subTest(str=value, alter=False):
                self.assertEqual(modify(value, alter=False), result)
            with self.subTest(str=value, alter=True):
                self.assertEqual(modify(value, alter=True), result_m)

        with self.subTest(line="error"):
            error_msg = "Value passed not recognized"
            with self.assertRaisesRegex(Exception, error_msg):
                modify(unittest.TestCase)

    def test_not_null(self):
        """Test function not_null"""
        values_null = [
            "NAN",
            "nan",
            "Nan",
            "None",
            "none",
            0,
            float("NAN"),
            " ",
            "",
            math.nan,
            pd.NaT,
            np.nan,
            [],
            {},
            {}.keys(),
            pd.Timestamp(0),
        ]
        for value in values_null:
            with self.subTest(line=value):
                self.assertFalse(not_null(value))
                self.assertTrue(is_null(value))

        values_not_null = [
            "NANA",
            "0",
            "12/02/90",
            [0],
            {"A"},
            {""},
            {"A": 1}.keys(),
            pd.Timestamp(2022),
        ]
        for value in values_not_null:
            with self.subTest(line=value):
                self.assertTrue(not_null(value))
                self.assertFalse(is_null(value))

        with self.subTest(line="error"):
            error_msg = "Value passed not recognized"
            with self.assertRaisesRegex(Exception, error_msg):
                not_null(unittest.TestCase)

    def test_not_null_size(self):
        """Test function not_null with str_size to True"""
        test_values = ["NAN", ""]
        test_result = [True, False]
        for value, result in zip(test_values, test_result):
            with self.subTest(line=value):
                self.assertEqual(not_null(value, str_size=True), result)

    def test_array_not_null(self):
        """Test function array_not_null with recursive argument set to False."""
        test_values = [
            [["A", "NAN", [0]], {"A": (1, 0)}],
            ["A", "0", [0, pd.NaT]],
            [1, "None", np.nan],
            {pd.NaT, "Bernard"},
            "0",
            {"A": (1, 0), "B": "NA", "C": 0},
        ]
        test_result = [
            [True, True],
            [True, True, True],
            [True, False, False],
            [False, True],
            True,
            [True, False, False],
        ]
        for value, result in zip(test_values, test_result):
            with self.subTest(line=value, test="Null array"):
                self.assertEqual(array_not_null(value, recursive=False), result)

        with self.subTest(line="error"):
            error_msg = "Value passed not recognized"
            with self.assertRaisesRegex(Exception, error_msg):
                array_not_null(unittest.TestCase)

    def test_array_not_null_recursive(self):
        """Test function array_not_null with recursive argument set to True."""
        test_values = [[["A", "NAN", [0]], {"A": (1, 0)}], ["A", "0", [0, pd.NaT]]]
        test_result = [
            [[True, False, [False]], [[True, False]]],
            [True, True, [False, False]],
        ]
        for value, result in zip(test_values, test_result):
            with self.subTest(line=test_values, recursive=True):
                self.assertEqual(array_not_null(value, recursive=True), result)

    def test_bool_invert(self):
        """Test function bool_invert"""
        test_values = [[False, True, True], True, [False, "", True]]
        test_result = [[True, False, False], False, [True, False, False]]
        for value, result in zip(test_values, test_result):
            with self.subTest(line=value):
                self.assertEqual(bool_invert(value), result)

        for value in ["A", unittest.TestCase]:
            with self.subTest(line=value):
                error_msg = "Not a boolean"
                with self.assertRaisesRegex(Exception, error_msg):
                    bool_invert(value)

    def test_get_not_null_simple(self):
        """Test function get_not_null with simple values"""
        test_values = [1, 0, "A", [], {}, None, pd.NaT, pd.Timestamp(2022)]
        test_result = [1, None, "A", None, None, None, None, pd.Timestamp(2022)]
        for value, result in zip(test_values, test_result):
            with self.subTest(line=value):
                self.assertEqual(get_not_null(value), result)


        error_msg = "Value passed not recognized"
        with self.assertRaisesRegex(Exception, error_msg):
            result = get_not_null(unittest.TestCase)
    
    def test_get_not_null_iterable(self):
        """Test function get_not_null with simple values"""
        test_values = {'C': 2, 'D': [0]}
        test_result = {'C': 2 }
        self.assertEqual(get_not_null(test_values), test_result)

    def test_get_not_null(self):
        """Test function get_not_null"""
        test_values = [
            [1, 0, "A", []],
            [{}],
            "",
            " ",
            {
                "A": "B",
                "B": [0, 1, {"C": 2, "D": [0]}],
                "D": pd.NaT,
                "E": {"F": []},
                "G": np.array([1, 2, 0]),
            },
            (0, 2, "NAn", ["A", 0]),
            {4, np.nan, ("A", 1)},
        ]
        test_result = [
            [1, "A"],
            [],
            None,
            " ",
            {"A": "B", "B": [1, {"C": 2}], "G": [1, 2]},
            (2, "NAn", ["A"]),
            {4, ("A", 1)},
        ]
        test_result_m = [
            [1, "A"],
            [],
            None,
            None,
            {"A": "B", "B": [1, {"C": 2}], "G": [1, 2]},
            (2, ["A"]),
            {4, ("A", 1)},
        ]
        for value, result, result_m in zip(test_values, test_result, test_result_m):
            with self.subTest(line=value, alter=False):
                self.assertEqual(get_not_null(value, alter=False), result)
            with self.subTest(line=value, alter=True):
                self.assertEqual(get_not_null(value, alter=True), result_m)

        test_values = [pd.Series({"A": 0, "B": None, "C": [1, 0], "D": "N A"})]
        test_result = [pd.Series({"C": [1], "D": "N A"})]
        test_result_m = [pd.Series({"C": [1]})]
        for value, result, result_m in zip(test_values, test_result, test_result_m):
            with self.subTest(line=value, alter=False):
                self.assertTrue(get_not_null(value, alter=False).equals(result))
            with self.subTest(line=value, alter=True):
                self.assertTrue(get_not_null(value, alter=True).equals(result_m))

        for value in [["A", unittest.BaseTestSuite], unittest.BaseTestSuite]:
            with self.subTest(line=value, error="True"):
                error_msg = "Value passed not recognized"
                with self.assertRaisesRegex(Exception, error_msg):
                    get_not_null(value)


if __name__ == "__main__":
    unittest.main()
