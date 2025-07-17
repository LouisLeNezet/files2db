#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 07/10/2021
@author: Louis Le Nézet
"""

import unittest
import pandas as pd
from pandas.testing import assert_series_equal, assert_frame_equal

from files2db.data_mg.string_management import (
    data_replace,
    data_clean,
    data_sep,
    data_sep_pattern,
)


class TestingDataReplace(unittest.TestCase):
    """Class for testing"""

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


class TestDataClean(unittest.TestCase):
    def test_del_match_only(self):
        s = pd.Series(["remove", "keep", "remove", "test", "test2"])
        expected = pd.Series([None, "keep", None, None, "test2"])
        result = data_clean(s, del_match=["remove", "test"])
        assert_series_equal(result, expected)

    def test_strip_from_only(self):
        s = pd.Series(["abc=123", "xyz|78|9", "test:value", "this:test:item"])
        expected = pd.Series(["abc", "xyz", "test", "this"])
        result = data_clean(s, strip_from=["=", "|", ":"])
        assert_series_equal(result, expected)

    def test_del_in_only(self):
        s = pd.Series(["a123b", "xyz456", "999test999"])
        expected = pd.Series(["ab", "xyz", "test"])
        result = data_clean(s, del_in=["123", "456", "999"])
        assert_series_equal(result, expected)

    def test_delin_delstart_delend(self):
        s = pd.Series(["a123a", "xyz456y", "999test999"])
        expected = pd.Series(["123a", "z456", "999test99"])
        result = data_clean(s, del_in="y", del_start=["a", "x"], del_end="9")
        assert_series_equal(result, expected)

    def test_all_parameters_combined(self):
        s = pd.Series(["REMOVE", "valueotherfoo", "trash:data", "skip"])
        expected = pd.Series(["", "value", "trash", "skip"])
        result = data_clean(
            s,
            del_match=["REMOVE"],
            strip_from=["=", ":"],
            del_in=["other", "foo"],
            fillna_value="",
        )
        assert_series_equal(result, expected)

    def test_no_modification(self):
        s = pd.Series(["hello", "world"])
        expected = s.copy()
        result = data_clean(s)
        assert_series_equal(result, expected)

    def test_non_string_input(self):
        s = pd.Series([123, 456, "789text"])
        with self.assertRaises(TypeError):
            data_clean(s, del_in=["789"], strip_from=["3", "5"])


class TestDataSep(unittest.TestCase):
    def test_basic_separation(self):
        s = pd.Series(["a,b", "c,d", "e"], name="col1")

        expected = pd.DataFrame({"col1_0": ["a", "c", "e"], "col1_1": ["b", "d", None]})

        result = data_sep(s, sep=[","])
        assert_frame_equal(result, expected)

    def test_multiple_separators(self):
        s = pd.Series(["a|b,c", "d,e|f"], name="col1")

        expected = pd.DataFrame(
            {"col1_0": ["a", "d"], "col1_1": ["b", "e"], "col1_2": ["c", "f"]}
        )

        result = data_sep(s, sep=["|", ","])
        assert_frame_equal(result, expected)

    def test_multiple_separators_and_navalue(self):
        s = pd.Series(["a|b,c", "d,e"], name="col1")

        expected = pd.DataFrame(
            {"col1_0": ["a", "d"], "col1_1": ["b", "e"], "col1_2": ["c", pd.NA]}
        )

        result = data_sep(s, sep=["|", ","], fillna_value=pd.NA)
        assert_frame_equal(result, expected)

    def test_no_separator_provided(self):
        s = pd.Series(["abc", "def"], name="col1")

        expected = pd.DataFrame({"col1": ["abc", "def"]})
        result = data_sep(s, sep=None)
        assert_frame_equal(result, expected)

    def test_empty_dataframe(self):
        s = pd.Series(name="col1")
        expected = pd.DataFrame(columns=["col1"])
        result = data_sep(s, sep=[","])
        assert_frame_equal(result, expected)

    def test_numeric_data(self):
        s = pd.Series([1, 2], name="col1")
        with self.assertRaises(TypeError):
            data_sep(s, sep=[","])


class TestDataSepPattern(unittest.TestCase):
    def test_basic_separation_num_alpha(self):
        s = pd.Series(["123-abc", "456-def", "789-ghi"])
        pattern = r"(?P<num>\d+)-(?P<word>[a-zA-Z]+)"
        df = data_sep_pattern(s, pattern)

        expected = pd.DataFrame(
            {"num": ["123", "456", "789"], "word": ["abc", "def", "ghi"]}
        )
        assert_frame_equal(df, expected)

    def test_basic_separation_multiple_alpha(self):
        s = pd.Series(["A/E", "aA", "D"])
        pattern = r"((?P<G>[A-E])(\/*)(?P<D>[A-E]))|(?P<DG>[A-E])"
        df = data_sep_pattern(s, pattern)

        expected = pd.DataFrame(
            {"G": ["A", "a", None], "D": ["E", "A", None], "DG": [None, None, "D"]}
        )
        assert_frame_equal(df, expected)

    def test_basic_separation_multiple_alpha_num(self):
        s = pd.Series(["250268720147419", "985154000245240 2DVT608", "2DVT608"])
        pattern = r"(?P<Puce>[0-9]{12,19})*(\s)*(?P<Tatouage>[A-Z0-9]+[A-Z][A-Z0-9]*)*"
        df = data_sep_pattern(s, pattern)

        expected = pd.DataFrame(
            {
                "Puce": ["250268720147419", "985154000245240", None],
                "Tatouage": [None, "2DVT608", "2DVT608"],
            }
        )
        assert_frame_equal(df, expected)
    
    def test_basic_separation_multiple_alpha_num_noorder(self):
        s = pd.Series([pd.NA, "SomethingElse", "250268720147419", "985154000245240 2DVT608", "2DVT608", "2DVT608 250268720147419"])
        pattern = r"(?P<Puce>\d{12,19})|(?P<Tatouage>[0-9]+[A-Z][A-Z0-9]*)"
        df = data_sep_pattern(s, pattern)

        expected = pd.DataFrame(
            {
                "Puce": [pd.NA, pd.NA, "250268720147419", "985154000245240", pd.NA, "250268720147419"],
                "Tatouage": [pd.NA, pd.NA, pd.NA, "2DVT608", "2DVT608", "2DVT608"],
            }
        )
        assert_frame_equal(df, expected)

    def test_no_named_groups(self):
        s = pd.Series(["abc", "def"])
        pattern = r"\d+"
        with self.assertRaises(ValueError):
            data_sep_pattern(s, pattern)

    def test_keep_link_to_column(self):
        s = pd.Series(["abc", "def"], name="test_col")
        pattern = r"(?P<letter>[a-z]+)"
        df = data_sep_pattern(s, pattern, keep_link=True)
        expected = pd.DataFrame({"test_col_letter": ["abc", "def"]})
        assert_frame_equal(df, expected)


if __name__ == "__main__":
    unittest.main()
