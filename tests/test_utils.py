#!/usr/bin/env python3
"""
Created on 07/10/2021
@author: Louis Le Nézet
"""

import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from files2db.data_mg.utils import _to_bool_float, _to_bool_int, _to_bool_str, update_only_missing


class TestingClass(unittest.TestCase):
    """Class for testing"""

    def test_update_only_missing(self):
        """Test function update_only_missing"""
        df_test = pd.DataFrame(
            {
                "A": [1, pd.NA, 3, pd.NA],
                "B": [pd.NA, 6, pd.NA, pd.NA],
            }
        )
        df_update = pd.DataFrame(
            {
                "A": [pd.NA, 20, pd.NA, 40],
                "B": [50, pd.NA, 70, 80],
            }
        )
        df_expected = pd.DataFrame(
            {
                "A": [1, 20, 3, 40],
                "B": [50, 6, 70, 80],
            },
            dtype="object",
        )
        df_result = update_only_missing(df_test, df_update)
        assert_frame_equal(df_result, df_expected)

    def test_to_bool_float(self):
        self.assertTrue(_to_bool_float(1.0))
        self.assertFalse(_to_bool_float(0.0))
        self.assertTrue(_to_bool_float(2.0, true_values=[2.0]))
        self.assertFalse(_to_bool_float(2.0, false_values=[2.0]))
        with self.assertRaisesRegex(ValueError, r"Float value must be in true_values"):
            _to_bool_float(2.0)

    def test_to_bool_int(self):
        self.assertTrue(_to_bool_int(1))
        self.assertFalse(_to_bool_int(0))
        self.assertTrue(_to_bool_int(2, true_values=[2]))
        self.assertFalse(_to_bool_int(2, false_values=[2]))
        with self.assertRaisesRegex(ValueError, r"Integer value must be in true_values"):
            _to_bool_int(2)

    def test_to_bool_str(self):
        for str_true in ["tRue", "1", "yeS"]:
            self.assertTrue(_to_bool_str(str_true))
        for str_false in ["False", "0", "nO"]:
            self.assertFalse(_to_bool_str(str_false))
        self.assertTrue(_to_bool_str("This Is True", true_values=["this is true"]))
        self.assertFalse(_to_bool_str("This Is False", false_values=["false", "this is false"]))
        with self.assertRaisesRegex(ValueError, "String value must be in true_values"):
            _to_bool_str("This is false")

    def test_update_only_missing_with_error(self):
        """Test function update_only_missing"""
        df_test = pd.DataFrame(
            {
                "A": [1, pd.NA, 3, 4],
                "B": [5, 6, pd.NA, pd.NA],
            }
        )
        df_update = pd.DataFrame(
            {
                "A": [pd.NA, 20, pd.NA, 40],
                "B": [50, pd.NA, 70, 80],
            }
        )

        error_msg = "Conflict detected in column 'A' at rows [3]."
        error_msg += " Attempt to overwrite non-null values."
        with self.assertRaises(ValueError) as context:
            update_only_missing(df_test, df_update)
        self.assertEqual(str(context.exception), error_msg)
