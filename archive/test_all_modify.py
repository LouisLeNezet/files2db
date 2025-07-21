
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 25/11/2022
@author: LouisLeNezet
Testing scripts for the different set operation.
"""

import unittest
import pandas as pd

from archive.null_values import all_modify, any_nested_list, simplify_array

class TestingClass(unittest.TestCase):
    """Class for testing"""
    def test_all_modify(self):
        """Test function all_modify"""
        test_values = [
            [1, 0, "a ", []],
            [{" bC", "NoNe"}],
            "",
            " ",
            "Na N",
            {"A": "N aN", "B": 1, "C": ["Test ", 12]},
            (1, 3, [0]),
            "JustString",
        ]
        test_result = [
            [1, 0, "a ", []],
            [{" bC", "NoNe"}],
            "",
            " ",
            "Na N",
            {"A": "N aN", "B": 1, "C": ["Test ", 12]},
            (1, 3, [0]),
            "JustString",
        ]
        test_result_m = [
            [1, None, "A", None],
            [{"BC", None}],
            None,
            None,
            None,
            {"A": None, "B": 1, "C": ["TEST", 12]},
            (1, 3, [None]),
            "JUSTSTRING",
        ]
        for value, result, result_m in zip(test_values, test_result, test_result_m):
            with self.subTest(line=value, alter=False):
                self.assertEqual(all_modify(value, alter=False), result)
            with self.subTest(line=value, alter=True):
                self.assertEqual(all_modify(value, alter=True), result_m)

    def test_all_modify_pd_series(self):
        """Test function all_modify with pandas Series"""
        test_values = [pd.Series({"A": 0, "B": None, "C": ["Nan ", 0], "D": "N A"})]
        test_result = [pd.Series({"A": 0, "B": None, "C": ["Nan ", 0], "D": "N A"})]
        test_result_m = [
            pd.Series({"A": None, "B": None, "C": [None, None], "D": None})
        ]
        for value, result, result_m in zip(test_values, test_result, test_result_m):
            with self.subTest(line=value, alter=False):
                self.assertTrue(all_modify(value, alter=False).equals(result))
            with self.subTest(line=value, alter=True):
                self.assertTrue(all_modify(value, alter=True).equals(result_m))

        for value in [["A", unittest.BaseTestSuite], unittest.BaseTestSuite]:
            with self.subTest(line=value, error="True"):
                error_msg = "Error while modifying all values from iterable"
                with self.assertRaisesRegex(Exception, error_msg):
                    all_modify(value)
    
    def test_any_nested_list(self):
        """Test function any_nested_list"""
        test_values = [
            [1, 0, "A", []],
            [{"B": "A"}],
            "Abcd",
            "aBCD",
            " ",
            [1, [[[3, "A"]]]],
            2
        ]
        test_result = [True, True, False, False, False, True, False]
        for value, result in zip(test_values, test_result):
            with self.subTest(line=value):
                self.assertEqual(any_nested_list(value, "A"), result)
    
    
    def test_simplify_array(self):
        """Test function simplify_array"""
        test_values = [[1, 0, "A", []], ["B", "B", None], "AbcdA", " ", [1, 1, 2], None]
        test_result = [[1, "A"], "B", "AbcdA", " ", [1, 2], None]
        for value, result in zip(test_values, test_result):
            if isinstance(result, list):
                self.assertEqual(set(simplify_array(value, alter=False)), set(result))
            else:
                self.assertEqual(simplify_array(value, alter=False), result)

        for value in [2]:
            with self.subTest(line=value, test="error"):
                error_msg = f"Error simplifying array {value}"
                with self.assertRaisesRegex(Exception, error_msg):
                    simplify_array(value, alter=False)