#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 07/10/2021
@author: Louis Le Nézet
"""

import unittest
import pandas as pd
from pandas.testing import assert_series_equal, assert_frame_equal

from files2db.data_mg.string_management import data_replace, data_del, data_sep

class TestingClass(unittest.TestCase):
    """ Class for testing """
    def test_data_replace(self):
        """Test function date_convert"""
        test_values = pd.Series(["A", "a", "b", "E", "f", "Z"])

        equiv_data = {
            "A": ["a", "b", "c", "d"],
            "B": ["e", "f", "g", "h"],
        }

        test_result = pd.Series(["a", "a", "a", "b", "b", "z"])

        result = data_replace(test_values, equiv_data, to_lower=True)
        assert_series_equal(result, test_result)

class TestDataDel(unittest.TestCase):

    def test_del_match_only(self):
        s = pd.Series(["remove", "keep", "remove", "test", "test2"])
        expected = pd.Series([None, "keep", None, None, "test2"])
        result = data_del(s, del_match=["remove", "test"])
        assert_series_equal(result, expected)

    def test_strip_from_only(self):
        s = pd.Series(["abc=123", "xyz|78|9", "test:value", "this:test:item"])
        expected = pd.Series(["abc", "xyz", "test", "this"])
        result = data_del(s, strip_from=["=", "|", ":"])
        assert_series_equal(result, expected)

    def test_del_in_only(self):
        s = pd.Series(["a123b", "xyz456", "999test999"])
        expected = pd.Series(["ab", "xyz", "test"])
        result = data_del(s, del_in=["123", "456", "999"])
        assert_series_equal(result, expected)

    def test_all_parameters_combined(self):
        s = pd.Series(["REMOVE", "valueotherfoo", "trash:data", "skip"])
        expected = pd.Series(["", "value", "trash", "skip"])
        result = data_del(
            s,
            del_match=["REMOVE"],
            strip_from=["=", ":"],
            del_in=["other", "foo"],
            na_value=""
        )
        assert_series_equal(result, expected)

    def test_no_modification(self):
        s = pd.Series(["hello", "world"])
        expected = s.copy()
        result = data_del(s)
        assert_series_equal(result, expected)

    def test_non_string_input(self):
        s = pd.Series([123, 456, "789text"])
        expected = pd.Series(["12", "4", "text"])
        result = data_del(s, del_in=["789"], strip_from=["3", "5"])
        assert_series_equal(result, expected)

class TestDataSep(unittest.TestCase):

    def test_basic_separation(self):
        df = pd.DataFrame({
            "col1": ["a,b", "c,d", "e"]
        })

        expected = pd.DataFrame({
            "col1_0": ["a", "c", "e"],
            "col1_1": ["b", "d", None]
        })

        result = data_sep(df, sep=[","])
        assert_frame_equal(result, expected)

    def test_multiple_separators(self):
        df = pd.DataFrame({
            "col1": ["a|b,c", "d,e|f"]
        })

        expected = pd.DataFrame({
            "col1_0": ["a", "d"],
            "col1_1": ["b", "e"],
            "col1_2": ["c", "f"]
        })

        result = data_sep(df, sep=["|", ","])
        print(result)
        assert_frame_equal(result, expected)

    def test_no_separator_provided(self):
        df = pd.DataFrame({
            "col1": ["abc", "def"]
        })

        expected = df.copy()
        result = data_sep(df, sep=None)
        assert_frame_equal(result, expected)

    def test_empty_dataframe(self):
        df = pd.DataFrame(columns=["col1"])
        expected = pd.DataFrame(columns=["col1"])
        result = data_sep(df, sep=[","])
        assert_frame_equal(result, expected)

    def test_numeric_data(self):
        df = pd.DataFrame({
            "col1": [1, 2],
            "col2": ["a,b", "c,d"]
        })

        expected = pd.DataFrame({
            "col1_0": ["1", "2"],
            "col2_0": ["a", "c"],
            "col2_1": ["b", "d"]
        })

        result = data_sep(df, sep=[","])
        assert_frame_equal(result, expected)

if __name__ == '__main__':
    unittest.main()
