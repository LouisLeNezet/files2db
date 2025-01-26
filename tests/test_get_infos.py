#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 25/11/2022
@author: LouisLeNezet
Testing scripts for the different common functions.
"""
import unittest

from files2db.ui.get_infos import welcome, get_path_os, get_file_path, get_os

class TestingClass(unittest.TestCase):
    """ Class for testing """
    def test_welcome(self):
        """Test function welcome"""
        welcome()
        welcome(col_needed=["Test","It","Is"])

    def test_get_path_os(self):
        """Test function get_path_os"""
        test_values = ["/mnt/c/test","/test/it/is","C:/test/it/is"]
        test_result = ["Wsl","Relative","Windows"]
        for value, result in zip(test_values, test_result):
            with self.subTest(line=value):
                self.assertEqual(get_path_os(value),result)

    def test_get_file_path(self):
        """Test function get_file_path"""
        current_os = get_path_os(get_os()[1])
        test_values = [
            "/mnt/c/test","/test/it/is",
            "C:/test/it/is",r"C:\test\it\is",
            "../../test/it/is",r"..\..\test\it\is",
            "./test/it/is", r".\test\it\is"
        ]
        if current_os == "Windows":
            test_result = [
                "C:/test","/test/it/is","C:/test/it/is","C:/test/it/is",
                "../../test/it/is","../../test/it/is","./test/it/is","./test/it/is"
            ]
        elif current_os == "Wsl":
            test_result = [
                "/mnt/c/test","/test/it/is","/mnt/c/test/it/is","/mnt/c/test/it/is",
                "../../test/it/is","../../test/it/is","./test/it/is","./test/it/is"
            ]
        else:
            raise OSError(f"Operating system not supported for the moment:{current_os}")
        for value, result in zip(test_values, test_result):
            with self.subTest(line=value, os_test=current_os):
                self.assertEqual(get_file_path(value),result)
        with self.subTest(line="error"):
            with self.assertRaisesRegex(Exception,"should not match multiple or none os patterns"):
                get_file_path("ThisIsAwrongPath")

if __name__ == '__main__':
    unittest.main()
