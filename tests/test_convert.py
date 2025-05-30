#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 07/10/2021
@author: Louis Le Nézet
"""

import unittest
import pandas as pd
import numpy as np

from data_mg.convert import date_convert, num_convert, check_numeric

class TestingClass(unittest.TestCase):
    """ Class for testing """
    def test_date_convert(self):
        """Test function date_convert"""
        test_values = ["06.12.2022","06/12/2022","2022/12/06",
                       "2022.12.06","2022-12-0600:00:00","00:00:00",0]
        test_result = ["06.12.2022","06.12.2022","06.12.2022",
                       "06.12.2022","06.12.2022",None,None]
        for value, result in zip(test_values, test_result):
            with self.subTest(line=value):
                self.assertEqual(date_convert(value),result)

        test_values = ["06.12.22","6.10.11","WrongFormat"]
        for value in test_values:
            with self.subTest(line=value):
                with self.assertRaisesRegex(Exception,"Error while converting date"):
                    date_convert(value)

    def test_num_convert(self):
        """Test function num_convert"""
        test_values = [pd.Series({"A":0,"B":None,"C":[1,0],"D":"N A","E":"4.50001",
                                  "F":'4E-05', "G": np.nan, "H":5.6498798 })]
        test_result_int = [pd.Series([0,np.nan,np.nan,np.nan,5,0,np.nan,6])]
        test_result_float = [pd.Series([0,np.nan,np.nan,np.nan,4.50001,0.00004,np.nan,5.6498798])]
        error_num = 'Cannot be converted to Numeric'
        err_to_get = [None, error_num, error_num, error_num, None, None, error_num, None]
        for value, result_int,result_float in zip(test_values, test_result_int, test_result_float):
            with self.subTest(line=value, to_type="int"):
                data, error = num_convert(value, "int")
                self.assertTrue(data.equals(result_int))
                self.assertEqual(error, err_to_get)
            with self.subTest(line=value, to_type="float"):
                data, error = num_convert(value, "float")
                self.assertTrue(data.equals(result_float))
                self.assertEqual(error, err_to_get)

        test_values = [unittest.TestCase]
        for value in test_values:
            with self.subTest(line=value, type="error"):
                with self.assertRaisesRegex(Exception,"Error while converting to numeric"):
                    num_convert(value, to_type="int")

    def test_check_numeric(self):
        """Test function check_numeric"""
        test_values = [0, np.nan, 1, 5.41656541, "A", "1", "5.41656541", [1,0],
                       "N A","4.50001", '4E-05', 5.6498798 ]
        test_result = [True, False, True, True, False, True, True, False,
                       False, True, True, True]

        for value, result in zip(test_values, test_result):
            with self.subTest(line=value):
                self.assertEqual(check_numeric(value),result)

if __name__ == '__main__':
    unittest.main()
