from fpy.data.either import Either, Left, Right, isRight, fromRight
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
from typing import TypeVar, List, Tuple, Callable, Generic, Sequence, Union, Optional, Any
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

    fn: Union[Callable[[Sequence[S]], Either[Any, Tuple[T, Sequence[S]]]], Callable[[Sequence[S]], Optional[Tuple[T, Sequence[S]]]]] 

    def __underlying__(self):
        return self.fn

    def __call__(self, s: Sequence[S]):
        if not isinstance(s, cabc.Sequence):
            raise TypeError("Cannot parse none sequence")
        if not s:
            return Left(s)
        res = self.fn(s)
        if res is None:
            return Left(s)
        assert isinstance(res, (tuple, Either)), f"{res} type is {type(res)}"
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


def one(pred: Callable[[S], bool]) -> parser[S, S]:
    @parser
    def res(s: Sequence[S]):
        if pred(s[0]):
            return s[0], s[1:]
        return None

    return res


def neg(pred: Callable[[S], bool]) -> parser[S, S]:
    @parser
    def res(s: Sequence[S]):
        if not pred(s[0]):
            return s[0], s[1:]
        return None

    return res


def just_nothing(unit : T) -> parser[S, T]:
    @parser
    def __res(s: Sequence[S]):
        return (unit, s)
    return __res

def pmaybe(p: parser[S, T], unit: T):
    return p | just_nothing(unit)


def many1(p: parser[S, Sequence[T]]):
    """
    many1 must take a parser that results in a sequence of tokens
    """
    @parser
    def __many1(s: Sequence[S]) -> Either[Any, Tuple[Sequence[T], Sequence[S]]]:
        _res = []
        work_s = s
        while work_s:
            _part: Either[Any, Tuple[Sequence[T], Sequence[S]]] = p(work_s)
            if not isRight(_part):
                break
            part, work_s = fromRight(([], []), _part)
            _res += part
        if not _res:
            return Left("no res from many1")
        return Right((_res, work_s))

    return __many1


many = lambda p: pmaybe(many1(p), [])


def ptrans(p, trans):
    return parser(lambda s: p(s) | trans)


def peek(p):
    @parser
    def __peek(s):
        return p(s) | set1(s)

    return __peek


discard = set0([])
skip = flip(ptrans, discard)


def toSeq(p: parser[S, T]) -> parser[S, Sequence[T]]:
    return ptrans(p, trans0(lambda x: [x]))

def pseq(s: Sequence[S]) -> parser[S, Sequence[S]]:
    if not s:
        return just_nothing([])
    p = just_nothing([])
    for e in s:
        p = p + toSeq(one(__ == e))
    return p

def inv(p):
    @parser
    def __inv(s):
        _r = p(s)
        if _r:
            return None
        return [], s
    return __inv
