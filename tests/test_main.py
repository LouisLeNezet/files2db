import logging
import os
import shutil
import unittest

from pandas._testing import assert_frame_equal

from files2db.data_mg.utils import df_to_str_keep_na
from files2db.main import main
from files2db.read_file.data_read import read_file

logging.basicConfig(level=logging.DEBUG)


class TestMainFunction(unittest.TestCase):
    def setUp(self):
        """Set up test data path"""
        self.test_data_path = os.path.join(os.path.dirname(__file__), "test_dataset")
        logging.getLogger().setLevel(logging.CRITICAL)

    def test_main_function_no_normalisation(self):
        """Test the main function with a sample path and no normalisation."""
        # Define a sample path and options
        db_path = os.path.join(self.test_data_path, "test1/orga.csv")
        normalize = False
        output_folder = "./DataGenerated"
        output_files_prefix = "AllID"

        # Call the main function
        df_raw, df_norm = main(
            path=db_path,
            normalize=normalize,
            output_folder=output_folder,
            output_files_prefix=output_files_prefix,
        )

        # Check if the output DataFrames are not None
        self.assertIsNotNone(df_raw, "Raw DataFrame should not be None")
        self.assertIsNone(df_norm, "Normalized DataFrame should be None")

        # Check dimensions of the raw DataFrame
        self.assertEqual(df_raw.shape, (10, 11))

    def test_main_function_with_normalisation(self):
        """Test the main function with a sample path and normalisation."""
        # Define a sample path and options
        db_path = os.path.join(self.test_data_path, "test1/orga.csv")
        normalize = True
        output_folder = os.path.join(self.test_data_path, "DataGenerated")
        output_files_prefix = "AllID"

        # Call the main function
        df_raw, df_norm = main(
            path=db_path,
            normalize=normalize,
            output_folder=output_folder,
            output_files_prefix=output_files_prefix,
        )

        # Check if the output DataFrames are not None
        self.assertIsNotNone(df_raw, "Raw DataFrame should not be None")
        self.assertIsNotNone(df_norm, "Normalized DataFrame should not be None")

        # Check dimensions of the raw DataFrame
        self.assertEqual(df_raw.shape, (10, 11))

        db_expected_path = os.path.join(self.test_data_path, "test1/expected.csv")
        db_expected = read_file(db_expected_path, sep=";", col_start=2)
        db_expected.reset_index(drop=True, inplace=True)

        df_norm.columns.name = None
        db_expected.columns.name = None

        df_norm = df_to_str_keep_na(df_norm)
        db_expected = df_to_str_keep_na(db_expected)

        assert_frame_equal(df_norm, db_expected, check_dtype=False)
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)


if __name__ == "__main__":
    unittest.main()
