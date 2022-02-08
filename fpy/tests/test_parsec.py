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
    inv,
)
from fpy.data.either import fromRight

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

    def testParseChoice(self):
        p1 = one(odd)
        p2 = one(even)
        p = p1 | p2
        self.assertTrue((p + p)(toks))

    def testMany(self):
        p1 = one(odd)
        p2 = one(even)
        p = many1(p1)
        self.assertTrue(p(toks))
        p = many(p2)
        self.assertTrue(p(toks))

    def testSkip(self):
        p1 = one(odd)
        p2 = one(even)
        p = skip(p1) + p2
        self.assertTrue(p(toks))

    def testPSeq(self):
        seq = [1, 2, 3]
        p = pseq(seq)
        self.assertTrue(p(toks))
        self.assertFalse(pseq([2, 3, 4])(toks))

    def testPeek(self):
        p1 = one(odd)
        p = peek(p1)
        res = p(toks)
        self.assertTrue(res)
        head, rest = fromRight(None, res)
        self.assertEqual(head, [1])
        self.assertIs(toks, rest)

    def testTimeN(self):
        p1 = one(odd)
        p2 = one(even)
        p = p1 | p2
        self.assertTrue((p * 2)(toks))

    def testInv(self):
        p1 = pseq("abc")
        p2 = inv(p1)
        p3 = pseq("cba")
        self.assertFalse(p2("abc"))
        self.assertTrue((p2 >> p3)("cba"))
