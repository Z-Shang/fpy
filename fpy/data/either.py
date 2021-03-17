from __future__ import annotations

from fpy.composable.function import func
from fpy.control.monad import _Monad
from fpy.control.natural_transform import NTrans, _NTrans
from abc import ABCMeta, abstractmethod, abstractclassmethod
import collections.abc as cabc
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, List, Tuple


T = TypeVar("T")
R = TypeVar("R")
L = TypeVar("L")
G = TypeVar("G")


class Either(_Monad, Generic[L, R]):
    @abstractmethod
    def __bool__(self):
        return NotImplemented

    def __bind__(self, b):
        raise NotImplementedError


@dataclass
class Left(Either[L, R]):
    v: L

    def __bool__(self):
        return False

    def __fmap__(self, f: Callable[[L], T]) -> Left[T]:
        return self

    def __bind__(self, _) -> Left[L, R]:
        return self

    def __ntrans__(self, t: _NTrans[Either, [L, R], G, T]) -> G[T]:
        return t(self.v)


@dataclass
class Right(Either[L, R]):
    v: R

    def __bool__(self):
        return True

    def __fmap__(self, f: Callable[[R], T]) -> Right[T]:
        return Right(f(self.v))

    def __bind__(self, b: Callable[[R], Either[T, G]]) -> Either[T, G]:
        return b(self.v)

    def __ntrans__(self, t: _NTrans[Either, [L, R], G, T]) -> G[T]:
        return t(self.v)


def isLeft(e: Either[L, R]) -> bool:
    return isinstance(e, Left)


def isRight(e: Either[L, R]) -> bool:
    return isinstance(e, Right)


def fromLeft(d: L, e: Either[L, R]) -> L:
    return d if not isLeft(e) else e.v


def fromRight(d: R, e: Either[L, R]) -> R:
    return d if not isRight(e) else e.v


@func
def either(fl: Callable[[L], T], fr: Callable[[R], T], e: Either[L, R]) -> T:
    if isLeft(e):
        return fl(fromLeft(None, e))
    return fr(fromRight(None, e))


def lefts(l: cabc.Sequence[Either[L, R]]) -> List[L]:
    return [fromLeft(None, v) for v in l if isLeft(v)]


def rights(l: cabc.Sequence[Either[L, R]]) -> List[R]:
    return [fromRight(None, v) for v in l if isRight(v)]


r2l: _NTrans[Right, T, Left, T] = NTrans(Left)
l2r: _NTrans[Left, T, Right, T] = NTrans(Right)


def partitionEithers(lst: cabc.Sequence[Either[L, R]]) -> Tuple[List[L], List[R]]:
    l = []
    r = []
    for e in lst:
        if isLeft(e):
            l.append(fromLeft(None, e))
        else:
            r.append(fromRight(None, e))
    return l, r
