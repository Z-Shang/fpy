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

    def testLocal(self):
        @do(Just)
        def test():
            x = Just(1)
            y < -x
            return y

        res = test()
        self.assertTrue(isJust(res))
        self.assertEqual(fromJust(res), 1)

    def testLocalNested(self):
        @do(Just)
        def test():
            x = 1
            y < -Just(2)
            z < -Just(x + y)
            return z

        res = test()
        self.assertTrue(isJust(res))
        self.assertEqual(fromJust(res), 3)

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

    def testTuple(self):
        @do(Just)
        def test():
            (a, b) < -Just((1, 2))
            return a + b

        res = test()
        self.assertTrue(isJust(res))
        self.assertEqual(fromJust(res), 3)

    def testTupleNoParen(self):
        @do(Just)
        def test():
            a, b < -Just((1, 2))
            return a + b

        res = test()
        self.assertTrue(isJust(res))
        self.assertEqual(fromJust(res), 3)

    def testComplex(self):
        @do(Just)
        def test():
            (a, b) < -Just((1, 2))
            c < -Just(a + b)
            d < -Just(c * b)
            return d

        res = test()
        self.assertTrue(isJust(res))
        self.assertEqual(fromJust(res), 6)
