from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar, Generic, Callable

from fpy.control.monad import _Monad
from fpy.control.natural_transform import NTrans, _NTrans


T = TypeVar("T")
F = TypeVar("F")
G = TypeVar("G")
B = TypeVar("B")


@dataclass
class Under(_Monad, Generic[T]):
    v: T

    def under(self):
        return self.v

    def __fmap__(self, f: Callable[[T], B]) -> Under[B]:
        return Under(f(self.v))

    def __ntrans__(self, t: Callable[[T], G[B]]) -> G[B]:
        return t(self.val)

    def __bind__(self, b: Callable[[T], B]) -> Under[B]:
        return self.__fmap__(b)


forget: _NTrans[F, B, Under, T] = NTrans(Under)
