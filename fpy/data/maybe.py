from __future__ import annotations

from fpy.control.monad import _Monad
from fpy.control.natural_transform import _NTrans
from abc import ABCMeta, abstractmethod, abstractclassmethod
import collections.abc as cabc
from typing import TypeVar, Generic, List, Callable
from dataclasses import dataclass

T = TypeVar("T")
S = TypeVar("S")
G = TypeVar("G")


class Maybe(_Monad[T], Generic[T]):
    @abstractmethod
    def __bool__(self):
        raise NotImplementedError

    def __bind__(self, b):
        raise NotImplementedError


@dataclass
class Just(Maybe[T], Generic[T]):
    v: T

    def __bool__(self):
        return True

    def __fmap__(self, f: Callable[[T], S]) -> Just[S]:
        return Just(f(self.v))

    def __ntrans__(self, t: _NTrans[Maybe, T, G, S]) -> G[S]:
        return t(self.v)

    def __bind__(self, b: Callable[[T], Maybe[S]]) -> Maybe[S]:
        return b(self.v)


class Nothing(Maybe[T], Generic[T]):
    def __bool__(self):
        return False

    def __bind__(self, _: any) -> Nothing[T]:
        return self

    def __ntrans__(self, t: _NTrans[Maybe, T, G, S]) -> G[S]:
        return t(None)


def isJust(m: Maybe[T]) -> bool:
    return isinstance(m, Just)


def isNothing(m: Maybe[T]) -> bool:
    return isinstance(m, Nothing)


def fromJust(m: Just[T]) -> T:
    assert isJust(m)
    return m.v


def fromMaybe(d: T, m: Maybe[T]) -> T:
    return d if not isJust(m) else fromJust(m)


def maybe(d: S, f: Callable[[T], S], m: Maybe[T]) -> S:
    return d if not isJust(m) else f(fromJust(m))


def mapMaybe(f: Callable[[T], Maybe[S]], l: cabc.Sequence[T]) -> List[S]:
    return [fromJust(v) for v in map(f, l) if isJust(v)]
