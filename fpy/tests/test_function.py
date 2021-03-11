from fpy.data.function import id_, const, flip, fix, on

import unittest


def catInt(a: str, b: int) -> str:
    return a + str(b)


def add(a: int, b: int) -> int:
    return a + b


class TestFunction(unittest.TestCase):
    def testId(self):
        v = id_(1)
        self.assertEqual(1, v)

    def testConst(self):
        f = const(1)
        self.assertEqual(1, f(123))

    def testFlip(self):
        a = 123
        b = "hello"
        f = flip(catInt)
        self.assertEqual("hello123", f(a, b))

    def testOn(self):
        a = "1"
        b = "2"
        f = on(add, int)
        self.assertEqual(3, f(a, b))

    def testFix(self):
        _fib = lambda r, n: 1 if n <= 1 else n * r(n - 1)
        fib = fix(_fib)
        self.assertEqual(120, fib(5))
