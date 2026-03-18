import logging
import os
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from files2db.data_mg.data_norm import initial_clean_na_values_utf8, norm_data
from files2db.data_mg.utils import df_to_str_keep_na
from files2db.read_file.data_read import read_file
from files2db.read_file.orga_read import get_db_from_path, load_file_orga


class TestingInitCleanClass(unittest.TestCase):
    """Class for testing initial_clean_na_values_utf8 function"""

    def setUp(self):
        """Set up test"""
        logging.getLogger().setLevel(logging.CRITICAL)

    def test_initial_clean_na_values_utf8(self):
        """Test the initial_clean_na_values_utf8 function."""
        # Create a sample DataFrame
        data = {
            "A": [1, None, 2, 4],
            "B": ["a", None, "c", "d"],
            "C": [None, None, None, None],
            "D": ["éclàir", None, "Résumé", None],
        }
        df = pd.DataFrame(data)

        # Expected DataFrame after cleaning
        expected_data = {
            "A": [1.0, 2.0, 4.0],
            "B": ["a", "c", "d"],
            "D": ["eclair", "Resume", pd.NA],
        }
        expected_df = pd.DataFrame(expected_data)

        # Call the function to test
        cleaned_df = initial_clean_na_values_utf8(df)

        # Check if the cleaned DataFrame matches the expected DataFrame
        assert_frame_equal(
            cleaned_df.reset_index(drop=True),
            expected_df.reset_index(drop=True),
        )


class TestingNormData(unittest.TestCase):
    """Class for testing normdata function"""

    def setUp(self):
        """Set up test data path"""
        self.test_data_path = os.path.join(os.path.dirname(__file__), "test_dataset/test2/")
        logging.getLogger().setLevel(logging.CRITICAL)

    def test_normdata_complex(self):
        """Test the normalisation process."""
        db_path = os.path.join(self.test_data_path, "orga.csv")
        db_files = get_db_from_path(db_path, load_file_orga())

        file_path = os.path.join(self.test_data_path, "file_complex.csv")
        df_file = read_file(file_path, sep=";")
        df_file.reset_index(drop=True, inplace=True)

        df_expected_path = os.path.join(self.test_data_path, "expected.csv")
        df_expected = read_file(df_expected_path, sep=";", col_start=2)
        df_expected.reset_index(drop=True, inplace=True)

        result = norm_data(
            data_df=df_file,
            db_field_rules=db_files["FieldRules"],
            db_values_map=db_files["ValuesMap"],
            na_values=["", None, "NaN", "nan", "<na>", "None", {}],
            fillna_value="NA",
        )

        save_path = os.path.join(self.test_data_path, "result.csv")
        result.to_csv(save_path, sep=";")

        df_norm = df_to_str_keep_na(result).reset_index(drop=True)
        df_expected = df_to_str_keep_na(df_expected).reset_index(drop=True)

        print(df_norm)

        # Check if the cleaned DataFrame matches the expected DataFrame
        assert_frame_equal(
            df_norm,
            df_expected,
        )
