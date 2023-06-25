from fpy.experimental.case import case

import unittest

class TestCase(unittest.TestCase):
    def testConstPat(self):
        @case
        def test(x):
            case(x)
            { 1: 1,
              2: 2 }

        self.assertEqual(1, test(1))
        self.assertEqual(2, test(2))
