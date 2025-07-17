#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 07/10/2021
@author: Louis Le Nézet
"""

import unittest
import pandas as pd
from pandas.testing import assert_series_equal, assert_frame_equal

from files2db.data_mg.data_validate import data_validate


class TestingClass(unittest.TestCase):
    """Class for testing"""

    def test_data_validate_LETTERS(self):
        """Test function data_validate"""
        test_values = pd.Series(["A", "A", "1", "E", "f", "Z"])
        test_result = pd.Series([
            pd.NA,
            pd.NA,
            {"Which": "1", "Error": ['not LETTERS']},
            pd.NA,
            {"Which": "f", "Error": ['not LETTERS']},
            pd.NA
        ])

        errors = data_validate(test_values, contains="LETTERS", min_value=None, max_value=None)
        assert_series_equal(errors, test_result)
    
    def test_data_validate_letters(self):
        """Test function data_validate"""
        test_values = pd.Series(["A", "A", "1", "E", "f", "Z"])
        test_result = pd.Series([
            {"Which": "A", "Error": ['not letters']},
            {"Which": "A", "Error": ['not letters']},
            {"Which": "1", "Error": ['not letters']},
            {"Which": "E", "Error": ['not letters']},
            pd.NA,
            {"Which": "Z", "Error": ['not letters']}
        ])

        errors = data_validate(test_values, contains="letters", min_value=None, max_value=None)
        assert_series_equal(errors, test_result)

    def test_data_validate_Alphanum(self):
        """Test function data_validate"""
        test_values = pd.Series(["A", "A", "1", "E", "f", "Z"])
        test_result = pd.Series([
            pd.NA, pd.NA, pd.NA,
            pd.NA, pd.NA, pd.NA
        ])

        errors = data_validate(test_values, contains="Alphanum", min_value=None, max_value=None)
        assert_series_equal(errors, test_result)
    

    def test_data_validate_date(self):
        """Test function data_validate"""
        test_values = pd.Series(["12.10.2024", "12.10.24", "12-10-2024", "SomethingElse"])
        test_result = pd.Series([
            pd.NA,
            {"Which": "12.10.24", "Error": ['not date']},
            {"Which": "12-10-2024", "Error": ['not date']},
            {"Which": "SomethingElse", "Error": ['not date']}
        ])

        errors = data_validate(test_values, contains="date", min_value=None, max_value=None)
        assert_series_equal(errors, test_result)
    

    def test_data_validate_int(self):
        """Test function data_validate"""
        test_values = pd.Series([1, 2.0, "3", 4, "five", None])
        test_result = pd.Series([
            pd.NA,
            {"Which": 2.0, "Error": ['not int']},
            {"Which": "3", "Error": ['not int']},
            pd.NA,
            {"Which": "five", "Error": ['not int']},
            pd.NA
        ])

        errors = data_validate(test_values, contains="int", min_value=None, max_value=None)
        assert_series_equal(errors, test_result)
    
    def test_data_validate_float(self):
        """Test function data_validate"""
        test_values = pd.Series([1, 2.0, "3.0", 4, "five", None])
        test_result = pd.Series([
            {'Which': 1, 'Error': ['not float']},
            pd.NA,
            {"Which": "3.0", "Error": ['not float']},
            {'Which': 4, 'Error': ['not float']},
            {"Which": "five", "Error": ['not float']},
            pd.NA
        ])

        errors = data_validate(test_values, contains="float", min_value=None, max_value=None)
        assert_series_equal(errors, test_result)
    
    def test_data_validate_none(self):
        """Test function data_validate"""
        test_values = pd.Series([1, 2.0, "3.0", 4, "five", None])
        test_result = pd.Series([
            pd.NA, pd.NA, pd.NA,
            pd.NA, pd.NA, pd.NA
        ])

        errors = data_validate(test_values, contains=None, min_value=None, max_value=None)
        assert_series_equal(errors, test_result)
    

    def test_data_validate_list(self):
        """Test function data_validate"""
        test_values = pd.Series([1, 2.0, "3.0", 4, "five", None])
        test_result = pd.Series([
            {'Which': 1, 'Error': ['not 3.0,five']},
            {"Which": 2, "Error": ['not 3.0,five']},
            pd.NA,
            {'Which': 4, 'Error': ['not 3.0,five']},
            pd.NA,
            pd.NA
        ])

        errors = data_validate(test_values, contains="3.0,five", min_value=None, max_value=None)
        assert_series_equal(errors, test_result)
    
    def test_data_validate_min_max_int(self):
        """Test function data_validate"""
        test_values = pd.Series([1, 2, 4, 5, 6, "A"])
        test_result = pd.Series([
            {'Which': 1, 'Error': ['InfToMin']},
            pd.NA,
            pd.NA,
            pd.NA,
            {'Which': 6, 'Error': ['SupToMax']},
            {'Which': 'A', 'Error': ['not int']}
        ])

        errors = data_validate(test_values, contains="int", min_value=2, max_value=5)
        assert_series_equal(errors, test_result)