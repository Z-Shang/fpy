from fpy.data.either import (
    Either,
    Left,
    Right,
    isLeft,
    isRight,
    fromLeft,
    fromRight,
    either,
    lefts,
    rights,
    partitionEithers,
    r2l,
    l2r,
)
from fpy.data.forgetful import forget, Under

import unittest


def even(n) -> Either[int, int]:
    if n % 2 == 0:
        return Right(n)
    return Left(n)


def add1(n):
    return n + 1


def sub1(n):
    return n - 1


class TestEither(unittest.TestCase):
    def testLeft(self):
        v = Left(3)
        self.assertTrue(isLeft(v))
        self.assertFalse(isRight(v))
        self.assertEqual(3, fromLeft(0, v))
        self.assertEqual(0, fromRight(0, v))
        self.assertEqual(4, either(add1, sub1, v))

    def testRight(self):
        v = Right(3)
        self.assertTrue(isRight(v))
        self.assertFalse(isLeft(v))
        self.assertEqual(3, fromRight(0, v))
        self.assertEqual(0, fromLeft(0, v))
        self.assertEqual(2, either(add1, sub1, v))

    def testEitherList(self):
        lst = [even(n) for n in range(8)]
        self.assertListEqual(lefts(lst), [1, 3, 5, 7])
        self.assertListEqual(rights(lst), [0, 2, 4, 6])
        ls, rs = partitionEithers(lst)
        self.assertListEqual(ls, [1, 3, 5, 7])
        self.assertListEqual(rs, [0, 2, 4, 6])

    def testNTransLeft(self):
        v = Left(3)
        vforgot = v & forget
        self.assertIsInstance(vforgot, Under)
        self.assertEqual(3, vforgot.under())
        vr = v & l2r
        self.assertTrue(isRight(vr))
        self.assertEqual(3, fromRight(0, vr))

    def testNTransRight(self):
        v = Right(3)
        vforgot = v & forget
        self.assertIsInstance(vforgot, Under)
        self.assertEqual(3, vforgot.under())
        vr = v & r2l
        self.assertTrue(isLeft(vr))
        self.assertEqual(3, fromLeft(0, vr))
