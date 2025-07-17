import unittest
import pandas as pd
import os
from pandas.testing import assert_frame_equal

from files2db.main import main

import logging

logging.basicConfig(level=logging.DEBUG)


class TestMainFunction(unittest.TestCase):
    def setUp(self):
        """Set up test data path"""
        self.test_data_path = os.path.join(os.path.dirname(__file__), "test_dataset")

    def test_main_function_no_normalisation(self):
        """Test the main function with a sample path and options."""
        # Define a sample path and options
        db_path = os.path.join(self.test_data_path, "orga.csv")
        normalize = False
        output_folder = "./DataGenerated"
        output_files_prefix = "AllID"

        # Call the main function
        df_raw, df_norm, df_error = main(
            path=db_path,
            normalize=normalize,
            output_folder=output_folder,
            output_files_prefix=output_files_prefix,
        )

        # Check if the output DataFrames are not None
        self.assertIsNotNone(df_raw, "Raw DataFrame should not be None")
        self.assertIsNone(df_norm, "Normalized DataFrame should be None")
        self.assertIsNone(df_error, "Error DataFrame should be None")
        
        # Check dimensions of the raw DataFrame
        self.assertEqual(df_raw.shape, (7, 10), "Raw DataFrame should have 7 rows and 10 columns")
    
    def test_main_function_with_normalisation(self):
        """Test the main function with a sample path and options."""
        # Define a sample path and options
        db_path = os.path.join(self.test_data_path, "orga.csv")
        normalize = True
        output_folder = "./DataGenerated"
        output_files_prefix = "AllID"

        # Call the main function
        df_raw, df_norm, df_error = main(
            path=db_path,
            normalize=normalize,
            output_folder=output_folder,
            output_files_prefix=output_files_prefix,
        )

        # Check if the output DataFrames are not None
        self.assertIsNotNone(df_raw, "Raw DataFrame should not be None")
        self.assertIsNotNone(df_norm, "Normalized DataFrame should not be None")
        self.assertIsNotNone(df_error, "Error DataFrame should not be None")

        # Check dimensions of the raw DataFrame
        self.assertEqual(df_raw.shape, (7, 10), "Raw DataFrame should have 6 rows and 10 columns")
        self.assertEqual(df_norm.shape, (7, 11), "Normalized DataFrame should have 6 rows and 7 columns")
        self.assertEqual(df_error.shape, (7, 7), "Error DataFrame should have 6 rows and 1 column")

if __name__ == "__main__":
    unittest.main()
