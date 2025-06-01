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

from files2db.data_process.null_values import not_null, is_null, array_not_null, bool_invert
from files2db.data_process.null_values import any_nested_list, get_not_null
from files2db.data_process.null_values import simplify_array, modify, all_modify


class TestingClass(unittest.TestCase):
    """ Class for testing """
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
            error_msg = "Error while modifying"
            with self.assertRaisesRegex(Exception, error_msg):
                modify(unittest.TestCase)

    def test_all_modify(self):
        """Test function all_modify"""
        test_values = [[1, 0, "a ", []], [{" bC", "NoNe"}], "", " ", "Na N", {
            "A": "N aN", "B": 1, "C": ["Test ", 12]}, (1, 3, [0]), "JustString"]
        test_result = [[1, 0, "a ", []], [{" bC", "NoNe"}], "", " ", "Na N", {
            "A": "N aN", "B": 1, "C": ["Test ", 12]}, (1, 3, [0]), "JustString"]
        test_result_m = [[1, None, "A", None], [{"BC", None}], None, None, None, {
            "A": None, "B": 1, "C": ["TEST", 12]}, (1, 3, [None]), "JUSTSTRING"]
        for value, result, result_m in zip(test_values, test_result, test_result_m):
            with self.subTest(line=value, alter=False):
                self.assertEqual(all_modify(value, alter=False), result)
            with self.subTest(line=value, alter=True):
                self.assertEqual(all_modify(value, alter=True), result_m)

        test_values = [
            pd.Series({"A": 0, "B": None, "C": ["Nan ", 0], "D":"N A"})]
        test_result = [
            pd.Series({"A": 0, "B": None, "C": ["Nan ", 0], "D":"N A"})]
        test_result_m = [
            pd.Series({"A": None, "B": None, "C": [None, None], "D":None})]
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

    def test_not_null(self):
        """Test function not_null"""
        values_null = ["NAN", "nan", "Nan", "None", "none", 0, float("NAN"), " ", "",
                       math.nan, pd.NaT, np.nan, [], {}, {}.keys(), pd.Timestamp(0)]
        for value in values_null:
            with self.subTest(line=value):
                self.assertFalse(not_null(value))
                self.assertTrue(is_null(value))

        values_not_null = ["NANA", "0", "12/02/90", [0],
                           {"A"}, {""}, {"A": 1}.keys(), pd.Timestamp(2022)]
        for value in values_not_null:
            with self.subTest(line=value):
                self.assertTrue(not_null(value))
                self.assertFalse(is_null(value))

        with self.subTest(line="error"):
            error_msg = "Error, while checking for null values"
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
        test_values = [[["A", "NAN", [0]], {"A": (1, 0)}],
                       ["A", "0", [0, pd.NaT]],
                       [1, "None", np.nan],
                       {pd.NaT, "Bernard"},
                       '0', {"A": (1, 0), "B": "NA", "C": 0}]
        test_result = [[True, True], [True, True, True], [
            True, False, False], [False, True], True, [True, False, False]]
        for value, result in zip(test_values, test_result):
            with self.subTest(line=value, test="Null array"):
                self.assertEqual(array_not_null(
                    value, recursive=False), result)

        with self.subTest(line="error"):
            error_msg = "Error while checking null values in array"
            with self.assertRaisesRegex(Exception, error_msg):
                array_not_null(unittest.TestCase)

    def test_array_not_null_recursive(self):
        """Test function array_not_null with recursive argument set to True."""
        test_values = [[["A", "NAN", [0]], {"A": (1, 0)}], [
            "A", "0", [0, pd.NaT]]]
        test_result = [[[True, False, [False]], [[True, False]]], [
            True, True, [False, False]]]
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
                error_msg = "Error, while inverting boolean values"
                with self.assertRaisesRegex(Exception, error_msg):
                    bool_invert(value)

    def test_get_not_null(self):
        """Test function get_not_null"""
        test_values = [[1, 0, "A", []], [{}], "", " ",
                       {"A": "B", "B": [0, 1, {"C": 2, "D": [0]}], "D":pd.NaT, "E":{
                           "F": []}, "G":np.array([1, 2, 0])},
                       (0, 2, "NAn", ["A", 0]), {4, np.nan, ("A", 1)}]
        test_result = [[1, "A"], [], None, " ", {"A": "B", "B": [
            1, {"C": 2}], "G": [1, 2]}, (2, "NAn", ["A"]), {4, ("A", 1)}]
        test_result_m = [[1, "A"], [], None, None, {"A": "B", "B": [
            1, {"C": 2}], "G": [1, 2]}, (2, ["A"]), {4, ("A", 1)}]
        for value, result, result_m in zip(test_values, test_result, test_result_m):
            with self.subTest(line=value, alter=False):
                self.assertEqual(get_not_null(value, alter=False), result)
            with self.subTest(line=value, alter=True):
                self.assertEqual(get_not_null(value, alter=True), result_m)

        test_values = [pd.Series({"A": 0, "B": None, "C": [1, 0], "D":"N A"})]
        test_result = [pd.Series({"C": [1], "D":"N A"})]
        test_result_m = [pd.Series({"C": [1]})]
        for value, result, result_m in zip(test_values, test_result, test_result_m):
            with self.subTest(line=value, alter=False):
                self.assertTrue(get_not_null(
                    value, alter=False).equals(result))
            with self.subTest(line=value, alter=True):
                self.assertTrue(get_not_null(
                    value, alter=True).equals(result_m))

        for value in [["A", unittest.BaseTestSuite], unittest.BaseTestSuite]:
            with self.subTest(line=value, error="True"):
                error_msg = "Error while filtering null value from iterable"
                with self.assertRaisesRegex(Exception, error_msg):
                    get_not_null(value)

    def test_any_nested_list(self):
        """Test function any_nested_list"""
        test_values = [[1, 0, "A", []], [
            {"B": "A"}], "Abcd", "aBCD", " ", [1, [[[3, "A"]]]]]
        test_result = [True, False, True, False, False, True]
        for value, result in zip(test_values, test_result):
            with self.subTest(line=value):
                self.assertEqual(any_nested_list(value, "A"), result)

        for value in [2]:
            with self.subTest(line=value, test="error"):
                error_msg = f"Error while testing for presence of A in {value}"
                with self.assertRaisesRegex(Exception, error_msg):
                    any_nested_list(value, "A")

    def test_simplify_array(self):
        """Test function simplify_array"""
        test_values = [[1, 0, "A", []], ["B", "B", None],
                        "AbcdA", " ", [1, 1, 2], None]
        test_result = [[1, "A"], "B", "AbcdA", ' ', [1, 2], None]
        for value, result in zip(test_values, test_result):
            self.assertEqual(simplify_array(value, alter=False),result)
            print(simplify_array(value, alter=False))

        for value in [2]:
            with self.subTest(line=value, test="error"):
                error_msg = f"Error simplifying array {value}"
                with self.assertRaisesRegex(Exception, error_msg):
                    simplify_array(value, alter=False)


if __name__ == '__main__':
    unittest.main()
