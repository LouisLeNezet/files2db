#!/usr/bin/env python3
"""
Created on 07/10/2021
@author: Louis Le Nézet
"""

import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal

from files2db.data_mg.data_convert import check_numeric, date_convert, num_convert


class TestingClass(unittest.TestCase):
    """Class for testing"""

    def test_date_convert(self):
        """Test function date_convert"""
        test_values = [
            "06.12.2022",
            "06/12/2022",
            "2022/12/06",
            "2022.12.06",
            "2022-12-0600:00:00",
            "00:00:00",
            "",
            pd.NA,
        ]
        test_result = [
            "06.12.2022",
            "06.12.2022",
            "06.12.2022",
            "06.12.2022",
            "06.12.2022",
            pd.NA,
            pd.NA,
            pd.NA,
        ]
        for value, result in zip(test_values, test_result, strict=False):
            with self.subTest(line=value):
                converted = date_convert(value)
                if pd.isna(result):
                    self.assertTrue(pd.isna(converted))
                else:
                    self.assertEqual(converted, result)

        test_values = ["06.12.22", "6.10.11", "WrongFormat"]
        error_msg = [
            "Format is not reliable please modify it to full year format",
            "Format is not reliable please modify it to full year format",
            "Format not recognised WrongFormat",
        ]
        for value, err in zip(test_values, error_msg, strict=False):
            with self.subTest(line=value):
                with self.assertRaisesRegex(Exception, err):
                    date_convert(value)

    def test_num_convert(self):
        """Test function num_convert"""
        test_values = pd.Series(
            {
                "A": 0,
                "B": None,
                "C": "five",
                "D": "N A",
                "E": "4.50001",
                "F": "4E-05",
                "G": np.nan,
                "H": 5.6498798,
            }
        )
        test_result_int = pd.Series([0, pd.NA, pd.NA, pd.NA, 5, 0, pd.NA, 6])
        test_result_float = pd.Series(
            [0.0, pd.NA, pd.NA, pd.NA, 4.50001, 0.00004, pd.NA, 5.6498798], dtype="object"
        )

        with self.subTest(line=test_values, to_type="int"):
            data = num_convert(test_values, "int")
            assert_series_equal(data, test_result_int)

        with self.subTest(line=test_values, to_type="float"):
            data = num_convert(test_values, "float")
            assert_series_equal(data, test_result_float)

        with self.subTest(line="Unittest", type="error"):
            with self.assertRaisesRegex(Exception, "data_se should be a Pandas Series"):
                num_convert(["A", "B"], to_type="int")

    def test_check_numeric(self):
        """Test function check_numeric"""
        test_values = [
            0,
            np.nan,
            1,
            5.41656541,
            "A",
            "1",
            "5.41656541",
            [1, 0],
            "N A",
            "4.50001",
            "4E-05",
            5.6498798,
        ]
        test_result = [
            True,
            False,
            True,
            True,
            False,
            True,
            True,
            False,
            False,
            True,
            True,
            True,
        ]

        for value, result in zip(test_values, test_result, strict=False):
            with self.subTest(line=value):
                self.assertEqual(check_numeric(value), result)


if __name__ == "__main__":
    unittest.main()
