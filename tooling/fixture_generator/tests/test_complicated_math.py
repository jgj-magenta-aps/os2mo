# -- coding: utf-8 --

import unittest
from complicated_math import expert_calc

class MathStuff(unittest.TestCase):

    def setUp(self):
        self.result = expert_calc(5, 5)

    def test_some_math(self):

        self.assertEqual(self.result, 10)

    def test_some_more_math(self):

        self.assertEqual(self.result, 11)
