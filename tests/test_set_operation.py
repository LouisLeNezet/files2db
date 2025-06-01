#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 25/11/2022
@author: LouisLeNezet
Testing scripts for the different set operation.
"""
import unittest

from files2db.data_process.set_operation import union, convert_to_set, percent_error
from files2db.data_process.set_operation import difference, joint, disjoint, intersect, match

class TestingClass(unittest.TestCase):
    """ Class for testing """
    def test_convert_to_set(self):
        """Test function convert_to_set"""
        test_values = [{"A":"1","B":"2","C":"3","D":"4","E":"2"},(1,2,3,4,4),"AbCd",
                       ["ABC","NAN","Ab C"],"None", {"A":"1","B":"2"}.keys(),{"abc","NAN"}]
        test_result = [{'1', '4', '2', '3'},{1,2,3,4},{"AbCd"},
                       {"ABC","NAN","Ab C"},{'None'},{"A","B"},{"abc","NAN"}]
        test_result_m = [{'1', '4', '2', '3'},{1,2,3,4},{"ABCD"},
                         {"ABC"},set(),{"A","B"},{"ABC"}]
        test_result_l = [['1', '2', '3', '4'],[1,2,3,4],["ABCD"],
                         ["ABC"],[],["A","B"],["ABC"]]
        for value, result, result_m , result_l in zip(test_values, test_result,
                                                      test_result_m, test_result_l):
            with self.subTest(line=value, alter=False):
                self.assertEqual(convert_to_set(value, alter=False),result)
            with self.subTest(line=value, alter=True):
                self.assertEqual(convert_to_set(value, alter=True),result_m)
            with self.subTest(line=value, alter=True, to_list=True):
                self.assertEqual(set(convert_to_set(value, alter=True, to_list=True)),set(result_l))
        with self.subTest(error="True"):
            with self.assertRaisesRegex(Exception,"Error while converting"):
                convert_to_set(unittest.TestCase())

    def test_percent_error(self):
        """Test function percent_error"""
        test_values_a = ["AB C",1234567890]
        test_values_b = ["AbCd","123A567890"]
        test_result = [75,10]
        test_result_m = [25,10]
        for value_a, value_b, result, result_m in zip(test_values_a, test_values_b,
                                                      test_result, test_result_m):
            with self.subTest(str_a=value_a,str_b=value_b, alter=False):
                self.assertEqual(percent_error(value_a, value_b, alter=False),result)
            with self.subTest(str_a=value_a,str_b=value_b, alter=True):
                self.assertEqual(percent_error(value_a, value_b, alter=True),result_m)

        with self.subTest(error="True"):
            with self.assertRaisesRegex(Exception,
                                        "Error while calculating the % of difference between"):
                percent_error(tuple,"A")

    def test_difference(self):
        """Test function difference"""
        test_values_a = [["A","B","C","DE"],["A","B","C"]]
        test_values_b = [["A","B","D e"],["None","NAN"]]
        test_result = [["C","DE"],["A","B","C"]]
        test_result_m = [["C"],["A","B","C"]]
        for value_a, value_b, result, result_m in zip(test_values_a, test_values_b,
                                                      test_result, test_result_m):
            with self.subTest(str_a=value_a,str_b=value_b, alter=False):
                self.assertEqual(set(difference(value_a, value_b, alter=False)),set(result))
            with self.subTest(str_a=value_a,str_b=value_b, alter=True):
                self.assertEqual(set(difference(value_a, value_b, alter=True)),set(result_m))
        with self.subTest(error="True"):
            with self.assertRaisesRegex(Exception,"Error while getting the difference between"):
                difference(tuple,"A")

    def test_joint(self):
        """Test function joint"""
        test_values_a = [["A","B","C","DE"],["A","B","C"]]
        test_values_b = [["A","B","D e"],["None","NAN", "C "]]
        test_result = [True, False]
        test_result_m = [True, True]
        for value_a, value_b, result, result_m in zip(test_values_a, test_values_b,
                                                      test_result, test_result_m):
            with self.subTest(str_a=value_a,str_b=value_b, alter=False):
                self.assertEqual(joint(value_a, value_b, alter=False),result)
            with self.subTest(str_a=value_a,str_b=value_b, alter=True):
                self.assertEqual(joint(value_a, value_b, alter=True),result_m)
        with self.subTest(error="True"):
            with self.assertRaisesRegex(Exception,"Error while getting the joint between"):
                joint(tuple,"A")

    def test_disjoint(self):
        """Test function disjoint"""
        test_values_a = [["A","B","C","DE"],["A","B","C"]]
        test_values_b = [["A","B","D e"],["None","NAN", "C "]]
        test_result = [False, True]
        test_result_m = [False, False]
        for value_a, value_b, result, result_m in zip(test_values_a, test_values_b,
                                                      test_result, test_result_m):
            with self.subTest(str_a=value_a,str_b=value_b, alter=False):
                self.assertEqual(disjoint(value_a, value_b, alter=False),result)
            with self.subTest(str_a=value_a,str_b=value_b, alter=True):
                self.assertEqual(disjoint(value_a, value_b, alter=True),result_m)
        with self.subTest(error="True"):
            with self.assertRaisesRegex(Exception,"Error while getting the disjoint between"):
                disjoint(tuple,"A")

    def test_intersect(self):
        """Test function intersect"""
        test_values_a = [["A","B","C","DE"],["A","B","C"]]
        test_values_b = [["A","B","D e"],["None","NAN", "C "]]
        test_result = [["A","B"], []]
        test_result_m = [["A","B","DE"], ["C"]]
        for value_a, value_b, result, result_m in zip(test_values_a, test_values_b,
                                                      test_result, test_result_m):
            with self.subTest(str_a=value_a,str_b=value_b, alter=False):
                self.assertEqual(set(intersect(value_a, value_b, alter=False)),set(result))
            with self.subTest(str_a=value_a,str_b=value_b, alter=True):
                self.assertEqual(set(intersect(value_a, value_b, alter=True)),set(result_m))
        with self.subTest(error="True"):
            with self.assertRaisesRegex(Exception,"Error while getting the intersect between"):
                intersect(tuple,"A")

    def test_union(self):
        """Test function union"""
        test_values_a = [["A","B","C","DE"],["A","B","C"],["A"]]
        test_values_b = [["A","B","c","D e"],["None","NAN", "C "],["None","NAN"]]
        test_result = [["A","B","C","DE","c","D e"], ["A","B","C","None","NAN", 'C '],
                       ["A","None","NAN"]]
        test_result_m = [["A","B","C","DE"], ["A","B","C"],["A"]]
        for value_a, value_b, result, result_m in zip(test_values_a, test_values_b,
                                                      test_result, test_result_m):
            with self.subTest(str_a=value_a,str_b=value_b, alter=False):
                self.assertEqual(set(union(value_a, value_b, alter=False)),set(result))
            with self.subTest(str_a=value_a,str_b=value_b, alter=True):
                self.assertEqual(set(union(value_a, value_b, alter=True)),set(result_m))
        with self.subTest(error="True"):
            with self.assertRaisesRegex(Exception,"Error while getting the union between"):
                union(tuple,"A")

    def test_match(self):
        """Test function match"""
        test_values_a = [["A","B","C","DE"],["A","B","C"],["A"]]
        test_values_b = [["A","B","c","D e"],["None","NAN", "C "],["None","NAN"]]
        test_result = [[True,True,False,False], [False,False,False],[False]]
        test_result_m = [[True,True,True,True], [False,False,True],[False]]
        for value_a, value_b, result, result_m in zip(test_values_a, test_values_b,
                                                      test_result, test_result_m):
            with self.subTest(str_a=value_a,str_b=value_b, alter=False):
                self.assertEqual(match(value_a, value_b, alter=False),result)
            with self.subTest(str_a=value_a,str_b=value_b, alter=True):
                self.assertEqual(match(value_a, value_b, alter=True),result_m)
        with self.subTest(error="True"):
            with self.assertRaisesRegex(Exception,"Error while getting the match between"):
                match(tuple,"A")
