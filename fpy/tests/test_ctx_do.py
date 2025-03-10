from fpy.data.maybe import (
    Maybe,
    Just,
    Nothing,
    isJust,
    isNothing,
    fromJust,
)
from fpy.control.monad import do

import unittest


def foo(x, y):
    return Just(x + y)


class TestDo(unittest.TestCase):
    def testSimpleJust(self):
        @do
        def test():
            with Just(1) as x:
                return Just(x)

        res = test()
        self.assertTrue(isJust(res))
        self.assertEqual(fromJust(res), 1)

    def testSimpleNothing(self):
        @do
        def test():
            with Just(1) as x:
                return Nothing()

        res = test()
        self.assertTrue(isNothing(res))

    def testLocal(self):
        @do
        def test():
            x = Just(1)
            with x as y:
                return Just(y)

        res = test()
        self.assertTrue(isJust(res))
        self.assertEqual(fromJust(res), 1)

    def testLocalNested(self):
        @do
        def test():
            x = 1
            with Just(2) as y:
                with Just(x + y) as z:
                    return Just(z)

        res = test()
        self.assertTrue(isJust(res))
        self.assertEqual(fromJust(res), 3)

    def testNested(self):
        @do
        def test():
            with Just(1) as  x, Just(2) as y, foo(x, y) as z:
                return Just(z + z)

        res = test()
        self.assertTrue(isJust(res))
        self.assertEqual(fromJust(res), 6)

    def testTuple(self):
        @do
        def test():
            with Just((1, 2)) as (a, b):
                return Just(a + b)

        res = test()
        self.assertTrue(isJust(res))
        self.assertEqual(fromJust(res), 3)

    def testComplex(self):
        @do
        def test():
            with Just((1, 2)) as (a, b), Just(a + b) as c, Just(c * b) as d:
                return Just(d)

        res = test()
        self.assertTrue(isJust(res))
        self.assertEqual(fromJust(res), 6)
