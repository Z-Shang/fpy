from fpy.data.maybe import (
    Maybe,
    Just,
    Nothing,
    isJust,
    isNothing,
    fromJust,
    fromMaybe,
    maybe,
    mapMaybe,
)
from fpy.data.forgetful import forget, Under

import unittest


def add1(x):
    return x + 1


def even(n: int) -> Maybe[int]:
    if n % 2 == 0:
        return Just(n)
    return Nothing()


class TestMaybe(unittest.TestCase):
    def testJust(self):
        v = Just(3)
        self.assertTrue(isJust(v))
        self.assertFalse(isNothing(v))
        self.assertEqual(3, fromJust(v))
        self.assertEqual(3, fromMaybe(0, v))
        self.assertEqual(4, maybe(0, add1, v))

    def testNothing(self):
        v = Nothing()
        self.assertFalse(isJust(v))
        self.assertTrue(isNothing(v))
        with self.assertRaises(AssertionError):
            fromJust(v)
        self.assertEqual(3, fromMaybe(3, v))
        self.assertEqual(0, maybe(0, add1, v))

    def testList(self):
        lst = [1, 2, 3, 4, 5, 6, 7, 8]
        res = mapMaybe(even, lst)
        self.assertListEqual(res, [2, 4, 6, 8])

    def testBindJust(self):
        v = Just(4)
        vb = v >> even
        self.assertTrue(isJust(vb))
        self.assertEqual(4, fromJust(vb))

    def testBindJust1(self):
        v = Just(3)
        vb = v >> even
        self.assertTrue(isNothing(vb))

    def testBindNothing(self):
        n = Nothing()
        nb = n >> even
        self.assertTrue(isNothing(nb))
        self.assertIs(n, nb)

    def testNTransJust(self):
        v = Just(4)
        vforgot = v & forget
        self.assertIsInstance(vforgot, Under)
        self.assertEqual(vforgot.under(), 4)

    def testNTransNothing(self):
        v = Nothing()
        vforgot = v & forget
        self.assertIsInstance(vforgot, Under)
        self.assertIsNone(vforgot.under())
