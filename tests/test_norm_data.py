import unittest
import pandas as pd
from pandas.testing import assert_frame_equal

from files2db.data_mg.norm_data import initial_clean_na_values_utf8


class TestingInitCleanClass(unittest.TestCase):
    """Class for testing initial_clean_na_values_utf8 function"""

    def test_initial_clean_na_values_utf8(self):
        """Test the initial_clean_na_values_utf8 function."""
        # Create a sample DataFrame
        data = {
            "A": [1, None, 2, 4],
            "B": ["a", None, "c", "d"],
            "C": [None, None, None, None],
            "D": ["éclair", None, "résumé", None]
        }
        df = pd.DataFrame(data)

        # Expected DataFrame after cleaning
        expected_data = {
            "A": [1.0, 2.0, 4.0],
            "B": ["a", "c", "d"],
            "D": ["eclair", "resume", "na"]
        }
        expected_df = pd.DataFrame(expected_data)

        # Call the function to test
        cleaned_df = initial_clean_na_values_utf8(df, fillna_value="NA")

        # Check if the cleaned DataFrame matches the expected DataFrame
        assert_frame_equal(
            cleaned_df.reset_index(drop=True),
            expected_df.reset_index(drop=True),
        )
