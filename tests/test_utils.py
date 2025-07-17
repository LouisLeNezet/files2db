#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 07/10/2021
@author: Louis Le Nézet
"""

import unittest
import pandas as pd
import numpy as np

from files2db.data_mg.utils import update_only_missing
from pandas.testing import assert_frame_equal


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
            dtype = "object",
        )
        df_result = update_only_missing(df_test, df_update)
        assert_frame_equal(df_result, df_expected)
    
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
        
        error_msg = "Conflict detected in column 'A' at rows [3]. Attempt to overwrite non-null values."
        with self.assertRaises(ValueError) as context:
            update_only_missing(df_test, df_update)
        self.assertEqual(str(context.exception), error_msg)
