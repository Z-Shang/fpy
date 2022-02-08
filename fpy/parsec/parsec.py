from fpy.data.either import Either, Left, Right
from fpy.data.forgetful import forget
from fpy.data.function import const, flip
from fpy.utils.placeholder import __
from fpy.composable.transparent import Transparent
from fpy.composable.function import func
from fpy.composable.collections import (
    apply,
    transN,
    trans0,
    trans1,
    or_,
    and_,
    set0,
    set1,
    get0,
    get1,
)

import string
from typing import TypeVar, List, Tuple, Callable, Generic
from dataclasses import dataclass
import collections.abc as cabc

S = TypeVar("S")
T = TypeVar("T")


def isspace(c):
    return c in string.whitespace


def s2c(s: str) -> List[str]:
    return list(s)


def c2s(cs: List[str]) -> str:
    return "".join(cs)


@dataclass
class parser(Transparent, Generic[S, T]):
    """
    parser :: [S] -> Either [S] ([T] * [S])
    """

    fn: Callable[[List[S]], Either[List[S], Tuple[List[T], List[S]]]]

    def __underlying__(self):
        return self.fn

    def __call__(self, s: List[S]):
        if not isinstance(s, cabc.Sequence):
            raise TypeError("Cannot parse none sequence")
        if not s:
            return Left(s)
        res = self.fn(s)
        if res is None:
            return Left(s)
        assert isinstance(res, (tuple, Either)), f"{res}"
        return Right(res) if isinstance(res, tuple) else res

    def timeN(self, n):
        if n <= 0:
            return parser(const(None))

        p = self
        for n in range(n - 1):
            p = p + self

        return p

    def __mul__(self, n):
        return self.timeN(n)

    def __rmul__(self, n):
        return self.timeN(n)

    def concat(self, nxt):
        @parser
        def __concat(s):
            return self(s) >> apply(lambda a, rest: nxt(rest) | trans0(a + __))

        return __concat

    def __add__(self, nxt):
        return self.concat(nxt)

    def choice(self, other):
        @parser
        def __choice(s):
            return or_(self, other)(s) or None

        return __choice

    def __or__(self, other):
        return self.choice(other)

    def parseR(self, rightP):
        @parser
        def __parseR(s):
            return self(s) >> apply(lambda leftR, rest: rightP(rest))

        return __parseR

    def parseL(self, rightP):
        @parser
        def __parseL(s):
            return self(s) >> apply(lambda leftR, rest: rightP(rest) | set0(leftR))

        return __parseL

    def __rshift__(self, other):
        return self.parseR(other)

    def __lshift__(self, other):
        return self.parseL(other)


def one(pred):
    @parser
    def res(s):
        if pred(s[0]):
            return [s[0]], s[1:]
        return None

    return res


def neg(pred):
    @parser
    def res(s):
        if not pred(s[0]):
            return [s[0]], s[1:]
        return None

    return res


just_nothing = parser(lambda s: ([], s))
pmaybe = __ | just_nothing


def many1(p):
    @parser
    def __many1(s):
        _res = []
        while s:
            _part = p(s)
            if not _part:
                break
            part, s = (_part & forget).under()
            _res += part
        if not _res:
            return None
        return _res, s

    return __many1


many = lambda p: pmaybe(many1(p))


def ptrans(p, trans):
    return parser(lambda s: p(s) | trans)


def peek(p):
    @parser
    def __peek(s):
        return p(s) | set1(s)

    return __peek


discard = set0([])
skip = flip(ptrans, discard)


def pseq(s):
    if not s:
        return just_nothing
    p = just_nothing
    for e in s:
        p = p + one(__ == e)
    return p

def inv(p):
    @parser
    def __inv(s):
        _r = p(s)
        if _r:
            return None
        return [], s
    return __inv
