from fpy.composable.function import func, SignatureMismatchError, NotEnoughArgsError
from fpy.composable.collections import (
    Seq,
    Map,
    transN,
    setN,
    getN,
    of_,
    is_,
    and_,
    or_,
    to,
    apply,
    mapN,
    fwd_,
)
from fpy.data.forgetful import Under

import unittest


def add1(x):
    return x + 1


def mul2(x):
    return x * 2


def pos(x):
    return x > 0


def odd(x):
    return x % 2 != 0


def add(a, b):
    return a + b


class TestCompsable(unittest.TestCase):
    def testFunc(self):
        f1 = func(add1)
        f2 = func(mul2)
        self.assertEqual(4, (f1 ^ f2)(1))
        self.assertEqual(3, (f2 ^ f1)(1))
        self.assertEqual(fwd_(1) | f1 ^ f2, Under(4))
        self.assertEqual(fwd_(1) | f2 ^ f1, Under(3))

    def testSeq(self):
        lst = [1, 2, 3, 4, 5]
        fn = Seq(lst)
        self.assertEqual(1, fn(0))
        self.assertEqual(2, fn(1))
        self.assertEqual(3, fn(2))
        self.assertEqual(4, fn(3))
        self.assertEqual(5, fn(4))
        self.assertEqual(Under(1), fwd_(0) | fn)
        self.assertEqual(Under(2), fwd_(1) | fn)
        self.assertEqual(Under(3), fwd_(2) | fn)
        self.assertEqual(Under(4), fwd_(3) | fn)
        self.assertEqual(Under(5), fwd_(4) | fn)

    def testMap(self):
        mp = {"a": 1, "b": 2, "c": 3}
        fn = Map(mp)
        self.assertEqual(1, fn("a"))
        self.assertEqual(2, fn("b"))
        self.assertEqual(3, fn("c"))
        self.assertEqual(Under(1), fwd_("a") | fn)
        self.assertEqual(Under(2), fwd_("b") | fn)
        self.assertEqual(Under(3), fwd_("c") | fn)

    def testItN(self):
        lst = [1, 2, 3]
        self.assertListEqual([2, 2, 3], transN(0, add1, lst))
        self.assertListEqual([2, 2, 3], setN(0, 2, lst))
        self.assertEqual(2, getN(1, lst))

    def testOf(self):
        self.assertTrue(of_(1, 2, 3, 4)(2))
        self.assertFalse(of_(1, 2, 3, 4)(5))

    def testIs(self):
        self.assertTrue(is_(int)(1))
        self.assertFalse(is_(str)(1))

    def testAnd(self):
        self.assertTrue(and_(odd, pos)(1))
        self.assertFalse(and_(odd, pos)(2))

    def testOr(self):
        self.assertTrue(or_(odd, pos)(1))
        self.assertTrue(or_(odd, pos)(2))

    def testTo(self):
        fn = to(int)
        self.assertEqual(1, fn("1"))

    def testApply(self):
        fn = apply(add1)
        self.assertEqual(2, fn((1,)))

    def testMapN(self):
        f1 = mapN(1, add1)
        self.assertListEqual([2, 3, 4], f1([1, 2, 3]))
        f2 = mapN(1)(add1)
        self.assertListEqual([2, 3, 4], f2([1, 2, 3]))
