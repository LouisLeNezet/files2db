#!/usr/bin/env python3
"""
Created on 25/11/2022
@author: LouisLeNezet
Testing scripts for the different common functions.
"""

import logging
import unittest

from files2db.ui.get_infos import get_file_path, get_path_os, welcome


class TestingClass(unittest.TestCase):
    """Class for testing"""

    def setUp(self):
        """Set up test"""
        logging.getLogger().setLevel(logging.CRITICAL)

    def test_welcome(self):
        """Test function welcome"""
        welcome()
        welcome(col_needed=["Test", "It", "Is"])

    def test_get_path_os(self):
        """Test function get_path_os"""
        test_values = ["/mnt/c/test", "/test/it/is", "C:/test/it/is"]
        test_result = ["Wsl", "Relative", "Windows"]
        for value, result in zip(test_values, test_result, strict=False):
            with self.subTest(line=value):
                self.assertEqual(get_path_os(value), result)

    def test_get_file_path(self):
        """Test function get_file_path"""
        test_values = [
            "/mnt/c/test",
            "/test/it/is",
            "C:/test/it/is",
            r"C:\test\it\is",
            "../../test/it/is",
            r"..\..\test\it\is",
            "./test/it/is",
            r".\test\it\is",
        ]

        results_by_os = {
            "Windows": [
                "C:/test",
                "/test/it/is",
                "C:/test/it/is",
                "C:/test/it/is",
                "../../test/it/is",
                "../../test/it/is",
                "./test/it/is",
                "./test/it/is",
            ],
            "Wsl": [
                "/mnt/c/test",
                "/test/it/is",
                "/mnt/c/test/it/is",
                "/mnt/c/test/it/is",
                "../../test/it/is",
                "../../test/it/is",
                "./test/it/is",
                "./test/it/is",
            ],
            "Linux": [
                "/mnt/c/test",
                "/test/it/is",
                "C:/test/it/is",
                "C:/test/it/is",
                "../../test/it/is",
                "../../test/it/is",
                "./test/it/is",
                "./test/it/is",
            ],
        }

        for dest_os, expected_results in results_by_os.items():
            for value, result in zip(test_values, expected_results, strict=False):
                with self.subTest(line=value, os_test=dest_os):
                    self.assertEqual(get_file_path(value, cwd_os=dest_os), result)

        with self.subTest(line="error"):
            with self.assertRaisesRegex(Exception, "should not match multiple or none os patterns"):
                get_file_path("ThisIsAwrongPath")


if __name__ == "__main__":
    unittest.main()
