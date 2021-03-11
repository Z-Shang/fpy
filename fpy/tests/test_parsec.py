from fpy.parsec.parsec import (
    parser,
    one,
    neg,
    pmaybe,
    many,
    many1,
    ptrans,
    peek,
    skip,
    pseq,
)

import unittest

toks = [1, 2, 3]

even = lambda x: x % 2 == 0
odd = lambda x: x % 2 != 0


class TestParsec(unittest.TestCase):
    def testParseOne(self):
        p = one(odd)
        self.assertTrue(p(toks))
        p = one(even)
        self.assertFalse(p(toks))

    def testParseNeg(self):
        p = neg(odd)
        self.assertFalse(p(toks))
        p = neg(even)
        self.assertTrue(p(toks))

    def testParseCat(self):
        p1 = one(odd)
        p2 = one(even)
        p = p1 + p2
        self.assertTrue(p(toks))

    def testParseLR(self):
        p1 = one(odd)
        p2 = one(even)
        pl = p1 << p2
        pr = p1 >> p2

        self.assertTrue(pl(toks))
        self.assertTrue(pr(toks))
