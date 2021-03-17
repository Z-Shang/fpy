from fpy.data.maybe import (
    Maybe,
    Just,
    Nothing,
    isJust,
    isNothing,
    fromJust,
)
from fpy.experimental.do import do

import unittest


def foo(x, y):
    return Just(x + y)


class TestDo(unittest.TestCase):
    def testSimpleJust(self):
        @do(Just)
        def test():
            x < -Just(1)
            return x

        res = test()
        self.assertTrue(isJust(res))
        self.assertEqual(fromJust(res), 1)

    def testSimpleNothing(self):
        @do(Just)
        def test():
            x < -Just(1)
            Nothing()

        res = test()
        self.assertTrue(isNothing(res))

    def testNested(self):
        @do(Just)
        def test():
            x < -Just(1)
            y < -Just(2)
            z < -foo(x, y)
            return z + z

        res = test()
        self.assertTrue(isJust(res))
        self.assertEqual(fromJust(res), 6)
